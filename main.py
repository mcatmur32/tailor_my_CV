from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget

from database.Database import Database

from app_pages.NewApplicationPage import NewApplicationPage
from app_pages.ManageApplicationsPage import ManageApplicationsPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tailor my CV App")

        # Setup database
        self.db = Database("database/applications_database.db")

        # Setup Tabbed widgets
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create pages
        self.new_application_page = NewApplicationPage(self.db, self.tabs)
        self.manage_applications_page = ManageApplicationsPage(self.db)

        # Add pages to tab widget
        self.tabs.addTab(self.new_application_page, "New Application")
        self.tabs.addTab(self.manage_applications_page, "Manage Applications")

        self.tabs.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        # Find which widget the tab index belongs to
        current_widget = self.tabs.widget(index)

        # If it's the ManageApplications page, refresh the table
        if isinstance(current_widget, ManageApplicationsPage):
            current_widget.load_data()  # Make sure this method re-queries DB

if __name__ == "__main__":
    import sys, traceback
    try:
        app = QApplication(sys.argv)

        with open("app_pages/style.qss", "r") as f:
            app.setStyleSheet(f.read())

        window = MainWindow()
        window.showMaximized()
        sys.exit(app.exec_())
    except Exception:
        traceback.print_exc()

