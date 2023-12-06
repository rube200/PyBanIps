from PyQt6.QtCore import pyqtSlot as Slot
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QListWidget
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from controllers.main_controller import MainController
from models.address_network_base import AddressNetworkBase
from ui.items.label_12 import Label12
from ui.items.line_edit_12 import LineEdit12
from ui.items.push_button_12 import PushButton12
from ui.list.address_network_item import AddressNetworkItem
from ui.list.address_network_list import AddressNetworkList
from validator.address_validator import AddressValidator


class MainWidget(QWidget):
    def __init__(self, parent: QWidget, main_controller: MainController):
        super().__init__(parent)
        self.__main_controller = main_controller
        self.settings = main_controller.get_settings

        self.__main_controller.set_add_address_ui_callback(self.add_address)
        self.__main_controller.set_add_network_ui_callback(self.add_network)
        self.__main_controller.set_remove_address_ui_callback(self.remove_address)
        self.__main_controller.set_set_addresses_ui_callback(self.refresh_addresses)
        self.__main_controller.set_set_networks_ui_callback(self.refresh_networks)
        self.__main_controller.set_update_address_ui_callback(self.update_address)

        self.container_layout = QHBoxLayout(self)

        # Create layouts
        self.analyse_addresses_input_labels_layout = QHBoxLayout(self)
        self.analyse_addresses_input_group_layout = QVBoxLayout(self)
        self.analyse_addresses_header = QHBoxLayout(self)
        self.analyse_addresses_layout = QVBoxLayout(self)

        self.banned_networks_header = QHBoxLayout(self)
        self.banned_networks_layout = QVBoxLayout(self)

        # Adding layouts together
        self.container_layout.addLayout(self.analyse_addresses_layout)
        self.analyse_addresses_layout.addLayout(self.analyse_addresses_header)
        self.analyse_addresses_header.addLayout(self.analyse_addresses_input_group_layout)
        self.analyse_addresses_input_group_layout.addLayout(self.analyse_addresses_input_labels_layout)

        self.container_layout.addLayout(self.banned_networks_layout)
        self.banned_networks_layout.addLayout(self.banned_networks_header)

        # Create input labels
        self.address_input_label = Label12('Target Address:', self, self.analyse_addresses_input_labels_layout)
        self.address_input_info_label = Label12('', self, self.analyse_addresses_input_labels_layout, QColor('#FF0000'))

        # Create save button
        self.address_input_button = PushButton12('Save', self, self.analyse_addresses_header)
        # noinspection PyUnresolvedReferences
        self.address_input_button.clicked.connect(self.__verify_and_save_input)

        # Create input form
        self.address_input_field = LineEdit12('IPV4 or IPV6', self, self.analyse_addresses_input_group_layout)
        self.address_input_field.setValidator(AddressValidator(self.address_input_field, self._set_input_info_text))
        # noinspection PyUnresolvedReferences
        self.address_input_field.returnPressed.connect(self.__save_input)
        # noinspection PyUnresolvedReferences
        self.address_input_field.textChanged.connect(self.__change_input_box_color)

        # Create analyse addresses list
        self.analyse_addresses_list = AddressNetworkList(self, self.analyse_addresses_layout)

        # Create banned networks label
        self.banned_networks_label = Label12('Banned Networks:', self)
        self.banned_networks_header.addWidget(self.banned_networks_label, 2)

        # Create save button
        self.load_logs_button = PushButton12('Load logs', self, self.banned_networks_header)
        # noinspection PyUnresolvedReferences
        self.load_logs_button.clicked.connect(self.__load_logs)

        # Create save button
        self.write_logs_button = PushButton12('Write bans', self, self.banned_networks_header)
        # noinspection PyUnresolvedReferences
        self.write_logs_button.clicked.connect(self.__write_bans)

        # Create banned networks list
        self.banned_networks_list = AddressNetworkList(self, self.banned_networks_layout)

    @Slot()
    def __verify_and_save_input(self) -> None:
        if self.address_input_field.hasAcceptableInput():
            self.__save_input()
        else:
            self._set_input_info_text('Invalid input!')

    @Slot()
    def __save_input(self) -> None:
        text = self.address_input_field.text()
        result = self.__main_controller.add_address_db(text)
        if result:
            self._set_input_info_text(result)

    @Slot(str)
    def __change_input_box_color(self, text: str) -> None:
        validator = self.address_input_field.validator()

        method = getattr(validator, 'get_color', None)
        if not callable(method):
            return

        # noinspection PyUnresolvedReferences
        color = validator.get_color(text)

        palette = self.address_input_field.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(color))

        self.address_input_field.setPalette(palette)

    @Slot()
    def __load_logs(self) -> None:
        self.__main_controller.load_logs_ssh()

    @Slot()
    def __write_bans(self) -> None:
        pass  # todo finish

    @staticmethod
    def _add_to_list(address: AddressNetworkBase, target_list: QListWidget) -> AddressNetworkItem:
        list_item = AddressNetworkItem(target_list, address)
        target_list.addItem(list_item)
        return list_item

    def _add_address_list(self, address: AddressNetworkBase) -> None:
        self._add_to_list(address, self.analyse_addresses_list)

    def _add_network_list(self, network: AddressNetworkBase) -> None:
        self._add_to_list(network, self.banned_networks_list)

    def _clear_input(self) -> None:
        if self.address_input_field.text():
            self.address_input_field.clear()

    def _index_of_address(self, address: AddressNetworkBase) -> int:
        address_list = self.analyse_addresses_list

        for i in range(len(address_list)):
            item = address_list.item(i)
            if item == address:
                return i

        return -1

    def _edit_address(self, address: AddressNetworkBase) -> None:
        address_index = self._index_of_address(address)
        if address_index != -1:
            self.analyse_addresses_list.item(address_index).setText(str(address))

    def _remove_address(self, address: AddressNetworkBase) -> None:
        address_index = self._index_of_address(address)
        if address_index != -1:
            self.analyse_addresses_list.takeItem(address_index)

    def _set_input_info_text(self, text: str) -> None:
        self.address_input_info_label.setText(text)

    def add_address(self, address: AddressNetworkBase) -> None:
        self._clear_input()
        self._add_address_list(address)

    def add_network(self, network: AddressNetworkBase) -> None:
        self._clear_input()
        self._add_network_list(network)

    def refresh_addresses(self, addresses: list[AddressNetworkBase]) -> None:
        self.analyse_addresses_list.clear()
        for address in addresses:
            self._add_address_list(address)

    def refresh_networks(self, networks: list[AddressNetworkBase]) -> None:
        self.banned_networks_list.clear()
        for network in networks:
            self._add_network_list(network)

    def remove_address(self, address: AddressNetworkBase) -> None:
        self._remove_address(address)

    def update_address(self, address: AddressNetworkBase) -> None:
        self._clear_input()
        self._edit_address(address)
