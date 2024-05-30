import os

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QListWidget, QWidget, QLayout, QMenu, QAbstractItemView, QApplication

from ui.list.address_network_item import AddressNetworkItem
from utils.ip_network_utils import IPvNetwork


class AddressNetworkList(QListWidget):
    def __init__(self, parent: QWidget, layout: QLayout):
        super().__init__(parent)

        self.__context_menu = QMenu(self)

        copy_action = QAction('&Copy', self)
        # noinspection PyUnresolvedReferences
        copy_action.triggered.connect(self.copy_selected)

        delete_action = QAction('&Delete', self)
        # noinspection PyUnresolvedReferences
        delete_action.triggered.connect(self.delete_selected)

        self.__context_menu.addAction(copy_action)
        self.__context_menu.addAction(delete_action)

        font = self.font()
        font.setPointSize(12)
        self.setFont(font)

        # noinspection PyUnresolvedReferences
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSortingEnabled(True)

        layout.addWidget(self)

    def show_context_menu(self, event: QPoint):
        index = self.indexAt(event)
        if not index.isValid():
            return

        global_pos = self.mapToGlobal(event)
        self.__context_menu.popup(global_pos)

    def copy_selected(self):
        items_text = []
        for item in self.selectedItems():
            if not isinstance(item, AddressNetworkItem):
                continue

            ip = item.ip
            # noinspection PyUnresolvedReferences
            items_text.append(str(ip.network_address if isinstance(ip, IPvNetwork) else ip))

        QApplication.clipboard().setText(os.linesep.join(items_text))

    def delete_selected(self):
        pass
        # for item in self.selectedItems():
        # row = self.row(item)
        # print(row)
        # self.takeItem(row)
