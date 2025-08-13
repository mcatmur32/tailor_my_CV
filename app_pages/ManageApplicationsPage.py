from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel

class ManageApplicationsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("This is Page 1"))
        self.button = QPushButton("Go to Page 2")
        layout.addWidget(self.button)
        self.setLayout(layout)