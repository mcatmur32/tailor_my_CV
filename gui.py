from PyQt5.QtWidgets import QApplication, QStackedWidget
from app_pages.WelcomePage import WelcomePage
from app_pages.NewApplicationPage import NewApplicationPage
from app_pages.ManageApplicationsPage import ManageApplicationsPage

import sys



app = QApplication(sys.argv)

stack = QStackedWidget()
welcome_page = WelcomePage()
new_application_page = NewApplicationPage()
manage_applications_page = ManageApplicationsPage()

stack.addWidget(welcome_page)  # index 0
stack.addWidget(new_application_page)  # index 1
stack.addWidget(manage_applications_page) # index 2

# Connect buttons
welcome_page.button_new_application.clicked.connect(lambda: stack.setCurrentIndex(1))
welcome_page.button_manage_applications.clicked.connect(lambda: stack.setCurrentIndex(2))

stack.setWindowTitle("Stacked Page App")
stack.setGeometry(100, 100, 300, 200)
stack.show()

sys.exit(app.exec_())
