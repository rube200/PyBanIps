from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

from ui.items.label_12 import Label12


class SSHHostConfirm(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Confirm ssh host!')

        self.container_layout = QVBoxLayout(self)

        self.message_label = Label12('Unknown host fingerprint:', self, self.container_layout)
        self.hostname_label = Label12('', self, self.container_layout)
        self.host_info_label = Label12('', self, self.container_layout)

        self.response_label = Label12('Do you want to continue?', self, self.container_layout)

        bts = QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(bts, self)
        self.container_layout.addWidget(self.button_box)

        # noinspection PyUnresolvedReferences
        self.button_box.accepted.connect(self.accept)
        # noinspection PyUnresolvedReferences
        self.button_box.rejected.connect(self.reject)
        self.button_box.setCenterButtons(True)

    def set_hostname(self, hostname: str) -> None:
        self.hostname_label.setText(f'Hostname: {hostname}')

    def set_host_info(self, host_info: str) -> None:
        self.host_info_label.setText(f'Fingerprint: {host_info}')
