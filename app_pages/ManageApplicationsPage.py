from PyQt5.QtWidgets import QWidget, QTableView, QVBoxLayout, QComboBox, QStyledItemDelegate, QStyleOptionButton, QStyle, QApplication
from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter
import os

class ManageApplicationsPage(QWidget):
    def __init__(self, db):
        super().__init__()
        
        layout = QVBoxLayout()

        # Table view
        self.table_view = QTableView()
        self.model = QSqlTableModel(db=db)
        self.model.setTable("job_applications")
        self.model.select()
        self.table_view.setModel(self.model)

        # Only prevent editing for non-status columns
        self.table_view.setEditTriggers(QTableView.DoubleClicked)  

        # Delegates
        self.table_view.setItemDelegateForColumn(3, CVButtonDelegate(self.table_view))

        # Optional: resize columns
        self.table_view.resizeColumnsToContents()

        # Handle clicks for button
        self.table_view.clicked.connect(self.handle_click)

        layout.addWidget(self.table_view)
        self.setLayout(layout)

    def handle_click(self, index):
        if index.column() == 3:  # CV_path column
            file_path = index.data()
            if file_path and os.path.exists(file_path):
                os.startfile(file_path)  # Windows
            else:
                print("File not found:", file_path)


# Button-like delegate for CV column
class CVButtonDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        button_option = QStyleOptionButton()
        button_option.rect = option.rect
        button_option.text = "Open CV"
        if option.state & QStyle.State_Selected:
            button_option.state = QStyle.State_Enabled | QStyle.State_Selected
        else:
            button_option.state = QStyle.State_Enabled

        QApplication.style().drawControl(QStyle.CE_PushButton, button_option, painter)

    def createEditor(self, parent, option, index):
        return None  # No editor, click handled externally

