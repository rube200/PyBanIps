from controllers.main_controller import MainController
from datetime import datetime
from models.auth_methods import AuthMethods
from os import path
from paramiko.client import SSHClient
from paramiko.ssh_exception import AuthenticationException
from policies.ssh_host_key_policy import SSHHostKeyPolicy
from utils.safe_formatter_dict import SafeFormatterDict


class SSHController:
    def __init__(self, main_controller: MainController):
        self.__main_controller = main_controller
        self.settings = main_controller.get_settings

        self.__main_controller.set_load_logs_ssh_callback(self.load_logs)

        self._ssh_client = SSHClient()
        self._ssh_client.load_system_host_keys()
        self._ssh_client.set_missing_host_key_policy(SSHHostKeyPolicy())

    def _connect(self) -> None:
        settings = self.settings()

        match settings.auth_method:
            case AuthMethods.LOGIN:
                self._ssh_client.connect(settings.hostname, settings.port, settings.username, settings.password)

            case AuthMethods.KEY_FILE:
                key_path = path.expanduser(settings.key_file)
                print(key_path)
                self._ssh_client.connect(settings.hostname, settings.port, settings.username, key_filename=key_path,
                                         passphrase=settings.passphrase)

            case _:
                raise AuthenticationException(f'Invalid auth method {settings.auth_method}')

    def _retrieve_ssh_data(self, date: datetime = None) -> None | list[str]:
        settings = self.settings()

        try:
            self._connect()

            if not date:
                date = datetime.min

            data_retriever_cmd = settings.data_retriever_command.format_map(SafeFormatterDict(date=date))
            print(data_retriever_cmd)
            _, stdout, stderr = self._ssh_client.exec_command(data_retriever_cmd)

            output_data = stdout.read()
            error = stderr.read()
            if error:
                print(error)  # todo finish
                return None

            return output_data.decode('utf-8').split('\n')

        except Exception as ex:
            print(ex)  # todo finish
            return None

        finally:
            self._ssh_client.close()

    def load_logs(self) -> None:
        last_logs_date = self.__main_controller.get_last_load_date()

        log_data = self._retrieve_ssh_data(last_logs_date)
        if not log_data:
            return
