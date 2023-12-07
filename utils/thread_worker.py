from typing import Callable

from PyQt6.QtCore import QObject, QThread


class ThreadWorker(QThread):
    def __init__(self, parent: QObject, run_method: Callable[[], None], finish_callback: Callable[[], None] = None):
        super().__init__(parent)
        self.__run_method = run_method

        if finish_callback:
            self.finished.connect(finish_callback)

    def run(self):
        self.__run_method()
