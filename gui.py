from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtSql import QSqlDatabase

from app_pages.WelcomePage import WelcomePage
from app_pages.NewApplicationPage import NewApplicationPage
from app_pages.ManageApplicationsPage import ManageApplicationsPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Page App")

        # Setup database
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("database/my_database.db")
        if not self.db.open():
            print("Failed to connect to database")

        # Setup stacked widget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create pages
        self.welcome_page = WelcomePage()
        self.new_application_page = NewApplicationPage()
        self.manage_applications_page = ManageApplicationsPage(self.db)

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.welcome_page)
        self.stacked_widget.addWidget(self.new_application_page)
        self.stacked_widget.addWidget(self.manage_applications_page)

        # Connect buttons
        self.welcome_page.button_new_application.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.welcome_page.button_manage_applications.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))

app = QApplication([])
window = MainWindow()
window.show()
app.exec_()

