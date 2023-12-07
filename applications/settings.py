from re import Pattern
from re import compile

from PyQt6.QtCore import QSettings

from models.auth_methods import AuthMethods

DEFAULT_DB_SQL_STRING = 'sqlite:///ban_ips.db'
DEFAULT_DB_MAX_DETECTS_TO_BAN = 5
DEFAULT_DB_MAX_ADDRESS_TO_CLUSTER = 32

DEFAULT_SSH_HOST = 'localhost'
DEFAULT_SSH_PORT = 22
DEFAULT_SSH_AUTH_METHOD = AuthMethods.LOGIN.value
DEFAULT_SSH_USERNAME = 'username'
DEFAULT_SSH_PASSWORD = 'password'
DEFAULT_SSH_KEY_FILE = 'id_rsa'
DEFAULT_SSH_PASSPHRASE = 'passphrase'
DEFAULT_SSH_DATA_RETRIEVER_COMMAND = 'journalctl -g ddos -o short-iso -S \'{date:%Y-%m-%d %H:%M:%S}\''
DEFAULT_SSH_DATA_REGEX = (r'(?P<date>[0-9-]{10}T[0-9:]{8}\+[0-9]{4}).+SRC=(?P<src>[0-9.]{5,15}|[0-9a-fA-F:]{39}) '
                          r'DST=(?P<dst>[0-9.]{7,15}|[0-9a-fA-F:]{39})')
DEFAULT_SSH_DATA_DATE_FORMAT = ''


class Settings(QSettings):
    def __init__(self):
        super().__init__('config.ini', QSettings.Format.IniFormat)

        self.__check_or_generate_config()

        self.beginGroup('DataBase')
        self.db_connection: str = self.value('connection', DEFAULT_DB_SQL_STRING, str)
        self.max_detects: int = self.value('max_detects', DEFAULT_DB_MAX_DETECTS_TO_BAN, int)
        self.max_addresses: int = self.value('max_addresses', DEFAULT_DB_MAX_ADDRESS_TO_CLUSTER, int)
        self.endGroup()

        self.beginGroup('Ssh')
        self.hostname: str = self.value('hostname', DEFAULT_SSH_HOST, str)
        self.port: int = self.value('port', DEFAULT_SSH_PORT, int)
        self.auth_method: AuthMethods = AuthMethods[self.value('auth_method', DEFAULT_SSH_AUTH_METHOD, str).upper()]
        self.username: str = self.value('username', DEFAULT_SSH_USERNAME, str)
        self.password: str = self.value('password', DEFAULT_SSH_PASSWORD, str)
        self.key_file: str = self.value('key_file', DEFAULT_SSH_KEY_FILE, str)
        self.passphrase: str = self.value('passphrase', DEFAULT_SSH_PASSPHRASE, str)
        self.data_retriever_command: str = self.value('data_retriever_command', DEFAULT_SSH_DATA_RETRIEVER_COMMAND, str)
        self.data_regex: Pattern = compile(self.value('data_regex', DEFAULT_SSH_DATA_REGEX, str))
        self.data_date_format: str = self.value('data_date_format', DEFAULT_SSH_DATA_DATE_FORMAT, str)
        self.endGroup()

    def __check_or_generate_config(self) -> None:
        self.beginGroup('DataBase')
        if not self.contains('connection'):
            self.setValue('connection', DEFAULT_DB_SQL_STRING)
        if not self.contains('max_detects'):
            self.setValue('max_detects', DEFAULT_DB_MAX_DETECTS_TO_BAN)
        if not self.contains('max_addresses'):
            self.setValue('max_addresses', DEFAULT_DB_MAX_ADDRESS_TO_CLUSTER)
        self.endGroup()

        self.beginGroup('Ssh')
        if not self.contains('hostname'):
            self.setValue('hostname', DEFAULT_SSH_HOST)
        if not self.contains('port'):
            self.setValue('port', DEFAULT_SSH_PORT)
        if not self.contains('auth_method'):
            self.setValue('auth_method', DEFAULT_SSH_AUTH_METHOD)
        if not self.contains('username'):
            self.setValue('username', DEFAULT_SSH_USERNAME)
        if not self.contains('password'):
            self.setValue('password', DEFAULT_SSH_PASSWORD)
        if not self.contains('key_file'):
            self.setValue('key_file', DEFAULT_SSH_KEY_FILE)
        if not self.contains('passphrase'):
            self.setValue('passphrase', DEFAULT_SSH_PASSPHRASE)
        if not self.contains('data_retriever_command'):
            self.setValue('data_retriever_command', DEFAULT_SSH_DATA_RETRIEVER_COMMAND)
        if not self.contains('data_regex'):
            self.setValue('data_regex', DEFAULT_SSH_DATA_REGEX)
        if not self.contains('data_date_format'):
            self.setValue('data_date_format', DEFAULT_SSH_DATA_DATE_FORMAT)
        self.endGroup()
