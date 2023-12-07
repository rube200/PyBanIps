from typing import Callable

from PyQt6.QtWidgets import QLayout
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtWidgets import QWidget

from utils.thread_worker import ThreadWorker


class PushButton12(QPushButton):
    def __init__(self, text: str, parent: QWidget, layout: QLayout, press_callback: Callable[[], None],
                 disable_ui: bool = True):
        super().__init__(text, parent)

        # noinspection PyUnresolvedReferences
        self.clicked.connect(self.__button_pressed)
        self.__disable_ui = disable_ui

        font = self.font()
        font.setPointSize(12)
        self.setFont(font)

        size_policy = self.sizePolicy()
        size_policy.setVerticalPolicy(QSizePolicy.Policy.Preferred)
        self.setSizePolicy(size_policy)

        self.__worker = ThreadWorker(parent, press_callback, self.__work_finished if self.__disable_ui else None)

        layout.addWidget(self)

    def __button_pressed(self) -> None:
        if self.__disable_ui:
            self.parent().setEnabled(False)
        self.__worker.start()

    def __work_finished(self) -> None:
        self.parent().setEnabled(True)
