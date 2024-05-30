from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

from ui.items.label_12 import Label12


class Notifier(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Info')

        self.container_layout = QVBoxLayout(self)

        self.header_label = Label12('Header placeholder', self, self.container_layout)
        self.message_label = Label12('Message placeholder', self, self.container_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, self)
        self.container_layout.addWidget(self.button_box)

        # noinspection PyUnresolvedReferences
        self.button_box.accepted.connect(self.accept)
        self.button_box.setCenterButtons(True)

    def display_message(self, msg: object, header: str, title: str = 'Info') -> None:
        print(f'[{title}] {header} {msg}')

        if title and title is not self.windowTitle():
            self.setWindowTitle(title)

        if header:
            self.header_label.setText(header)
        else:
            self.header_label.setText(title)

        if msg:
            self.message_label.setText(msg if isinstance(msg, str) else str(msg))
        else:
            self.message_label.setText('-')
        self.exec()
