from datetime import UTC
from datetime import datetime
from os import path
from re import Match

from paramiko.client import SSHClient
from paramiko.ssh_exception import AuthenticationException

from controllers.main_controller import MainController
from models.auth_methods import AuthMethods
from policies.ssh_host_key_policy import SSHHostKeyPolicy
from utils.ip_address_utils import IPvAddress
from utils.ip_address_utils import ip_address
from utils.safe_formatter_dict import SafeFormatterDict


class SSHController:
    def __init__(self, main_controller: MainController):
        self.__main_controller = main_controller
        self.settings = main_controller.get_settings

        self.__main_controller.load_logs_ssh.connect(self.load_logs)
        self.__main_controller.write_bans_ssh.connect(self.write_bans)

        self._ssh_client = SSHClient()
        self._ssh_client.load_system_host_keys()
        self._ssh_client.set_missing_host_key_policy(SSHHostKeyPolicy())

    def _connect(self) -> None:
        # noinspection PyArgumentList
        settings = self.settings()

        match settings.auth_method:
            case AuthMethods.LOGIN:
                self._ssh_client.connect(settings.hostname, settings.port, settings.username, settings.password)

            case AuthMethods.KEY_FILE:
                key_path = path.expanduser(settings.key_file)
                self._ssh_client.connect(settings.hostname, settings.port, settings.username, key_filename=key_path,
                                         passphrase=settings.passphrase)

            case _:
                raise AuthenticationException(f'Invalid auth method {settings.auth_method}')

    def _retrieve_ssh_data(self, date: datetime = None) -> (None | list[str], None | datetime):
        try:
            self._connect()
            if not date:
                date = datetime(1970, 1, 1, 1)

            # noinspection PyArgumentList
            settings = self.settings()
            data_retriever_cmd = settings.data_retriever_command.format_map(SafeFormatterDict(date=date))
            _, stdout, stderr = self._ssh_client.exec_command(data_retriever_cmd)
            retrieve_date = datetime.now(UTC)

            output_data = stdout.read()
            error = stderr.read()
            if error:
                print(error)  # todo finish
                return None

            return output_data.decode('utf-8').split('\n'), retrieve_date

        except Exception as ex:
            print(ex)  # todo finish
            return None

        finally:
            self._ssh_client.close()

    def __get_regex_date(self, match: Match, default: datetime = datetime.now(UTC)) -> None | datetime:
        if 'date' not in match.groupdict():
            return default

        date_raw = match.group('date')
        if not date_raw:
            return None

        try:
            # noinspection PyArgumentList
            settings = self.settings()
            if settings.data_date_format:
                return datetime.strptime(date_raw, settings.data_date_format)
            else:
                return datetime.fromisoformat(date_raw)

        except ValueError:
            return None

    @staticmethod
    def __get_address_by_key(match: Match, key: str) -> IPvAddress:
        if key not in match.groupdict():
            return None

        address_raw = match.group(key)
        if not address_raw:
            return None

        address = ip_address(address_raw)
        return address if not address.is_private else None

    def __get_address(self, match: Match) -> IPvAddress:
        address = self.__get_address_by_key(match, 'src')
        if address:
            return address

        return self.__get_address_by_key(match, 'dst')

    def _process_ssh_data(self, logs_data: list[str], retrieve_date: datetime, last_logs_date: datetime) -> (
            list[IPvAddress], datetime):
        failed_matches: list[str] = []
        failed_parse_address: list[str] = []
        failed_parse_date: list[str] = []

        addresses_to_report: list[IPvAddress] = []
        most_recent_log_date = None

        # noinspection PyArgumentList
        regex = self.settings().data_regex

        for log in logs_data:
            if not log:
                continue

            log_match = regex.match(log)
            if not log_match:
                if not log.startswith('-- Boot ') or not log.endswith(' --'):
                    failed_matches.append(log)
                continue

            log_date = self.__get_regex_date(log_match, retrieve_date)
            if not log_date:
                failed_parse_date.append(log)
            elif last_logs_date and last_logs_date >= log_date:
                continue

            log_address = self.__get_address(log_match)
            if not log_address:
                failed_parse_address.append(log)
                continue

            if not most_recent_log_date or log_date > most_recent_log_date:
                most_recent_log_date = log_date

            addresses_to_report.append(log_address)

        # todo finish
        print(failed_matches)
        print(failed_parse_address)
        print(failed_parse_date)

        return addresses_to_report, most_recent_log_date

    def load_logs(self) -> None:
        last_logs_date = self.__main_controller.get_last_load_date()
        ssh_data = self._retrieve_ssh_data(last_logs_date)
        if not ssh_data:
            return

        logs_data, retrieve_date = ssh_data
        result_addresses, most_recent_log_date = self._process_ssh_data(logs_data, retrieve_date, last_logs_date)
        print(f"Found {len(result_addresses)} addresses")
        # todo show msg
        if not result_addresses:
            return

        self.__main_controller.bulk_add_addresses_db.emit(result_addresses, most_recent_log_date)

    def write_bans(self) -> None:
        networks = self.__main_controller.get_networks_db()
        if networks is None:
            networks = []

        try:
            self._connect()

            sftp = self._ssh_client.open_sftp()
            settings = self.settings()
            network_format = settings.format

            with sftp.open(settings.file_v4, 'w') as ipv4_file, sftp.open(settings.file_v6, 'w') as ipv6_file:
                for network in networks:
                    network_ip = network.ip

                    network_bytes = network_format.format(network=network_ip, address=network_ip.network_address,
                                                          mask=network_ip.prefixlen).encode('utf-8')
                    if network.ip.version == 6:
                        ipv6_file.write(network_bytes)
                    else:
                        ipv4_file.write(network_bytes)

            if settings.refresh_firewall:
                _, _, stderr = self._ssh_client.exec_command(settings.refresh_firewall_cmd)
                error = stderr.read()
                if error:
                    print(error)  # todo finish
                    return None

            # todo show msg

        finally:
            self._ssh_client.close()
