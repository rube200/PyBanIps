from os import path

from paramiko.client import MissingHostKeyPolicy, SSHClient, RejectPolicy, AutoAddPolicy
from paramiko.pkey import PKey

from ui.dialog.ssh_host_confirm import SSHHostConfirm


class SSHHostKeyPolicy(MissingHostKeyPolicy):
    def __init__(self):
        self.dialog = SSHHostConfirm()
        self.accept_policy = AutoAddPolicy()
        self.reject_policy = RejectPolicy()

    def missing_host_key(self, client: SSHClient, hostname: str, key: PKey) -> None:
        # noinspection PyUnresolvedReferences
        host_info = f'{key.get_name()} {key.fingerprint}'

        self.dialog.set_hostname(hostname)
        self.dialog.set_host_info(host_info)

        result = self.dialog.exec()
        if not result:
            self.reject_policy.missing_host_key(client, hostname, key)
            return

        self.accept_policy.missing_host_key(client, hostname, key)
        # noinspection PyProtectedMember, PyUnresolvedReferences
        if client._host_keys_filename is None:
            hosts_path = path.expanduser('~/.ssh/known_hosts')
            client.get_host_keys().save(hosts_path)
