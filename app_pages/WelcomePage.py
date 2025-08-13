from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel

class WelcomePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Welcome Back, Max"))
        self.button_new_application = QPushButton("New Application")
        self.button_manage_applications = QPushButton("Manage Applications")
        layout.addWidget(self.button_new_application)
        layout.addWidget(self.button_manage_applications)
        self.setLayout(layout)