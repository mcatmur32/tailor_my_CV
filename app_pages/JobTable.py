import os
import sqlite3
from datetime import date

from database.Database import Database

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (
    QApplication, QComboBox, QHeaderView, QLabel, QMainWindow, QMessageBox,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
)

STATUSES = [
    "Draft", "Submitted", "Online Assessment", "Interview",
    "Offer", "Accepted", "Rejected"
]

# -----------------------------------
# Table widget that drives the UI
# -----------------------------------
class JobTable(QTableWidget):
    """
    Columns:
      0: Company (text)
      1: Role (text)
      2: Deadline (text YYYY-MM-DD)
      3: Status (QComboBox)
      4: CV File (QPushButton)
      5: Delete (QPushButton)
    """
    HEADERS = ["Company", "Role", "Deadline", "Status", "CV File", "Delete"]
    

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db

        self.setColumnCount(len(self.HEADERS))
        self.setHorizontalHeaderLabels(self.HEADERS)
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QTableWidget.NoEditTriggers)  # we edit via widgets, not raw cells
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)

        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        # Give the button columns a reasonable fixed width
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Open
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Delete

        self.load_data()

    # --- UI population ---
    def load_data(self):
        rows = self.db.fetch_all()
        self.setRowCount(0)
        self.setRowCount(len(rows))

        for r, rec in enumerate(rows):
            app_id = int(rec["id"])
            company = rec["company"]
            role = rec["role"]
            deadline = rec["deadline"]
            status = rec["status"]
            CV_file_path = rec["CV_file_path"] or ""

            # Plain text cells
            self.setItem(r, 0, QTableWidgetItem(company))
            self.setItem(r, 1, QTableWidgetItem(role))
            self.setItem(r, 2, QTableWidgetItem(deadline))

            # Status dropdown (writes back to DB)
            combo = QComboBox()
            combo.addItems(STATUSES)
            if status not in STATUSES:
                combo.addItem(status)  # tolerate unexpected status values
            combo.setCurrentText(status)
            # Store id on the widget; use signal that gives us the new text directly
            combo.setProperty("app_id", app_id)
            combo.currentTextChanged.connect(
                lambda text, cb=combo: self.on_status_changed(cb.property("app_id"), text)
            )
            self.setCellWidget(r, 3, combo)

            # File (just display basename)
            # basename = os.path.basename(CV_file_path) if CV_file_path else ""
            # file_item = QTableWidgetItem(basename)
            # file_item.setToolTip(CV_file_path)  # hover to see full path
            # self.setItem(r, 4, file_item)

            # Open button
            open_btn = QPushButton("Open CV")
            open_btn.setProperty("app_id", app_id)
            open_btn.clicked.connect(
                lambda _, b=open_btn: self.on_open_clicked(b.property("app_id"))
            )
            self.setCellWidget(r, 4, open_btn)

            # Delete button
            del_btn = QPushButton("Delete")
            del_btn.setProperty("app_id", app_id)
            del_btn.clicked.connect(
                lambda _, b=del_btn: self.on_delete_clicked(b.property("app_id"))
            )
            self.setCellWidget(r, 5, del_btn)

        # Cosmetic: align text columns a bit nicer
        for c in (0, 1, 2, 4):
            for r in range(self.rowCount()):
                item = self.item(r, c)
                if item:
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)

    # --- Button/combobox handlers ---
    def on_status_changed(self, app_id: int, new_status: str):
        self.db.update_status(app_id, new_status)
        # You could show a non-blocking toast/snackbar in a fancier UI.
        # Here we keep it quiet to avoid spamming dialogs.

    def on_open_clicked(self, app_id: int):
        path = self.db.get_file_path(app_id) or ""
        if not path or not os.path.exists(path):
            QMessageBox.warning(self, "File not found",
                                "No file found for this entry.\n\nPath:\n" + (path or "<empty>"))
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def on_delete_clicked(self, app_id: int):
        reply = QMessageBox.question(
            self, "Confirm delete",
            "Delete this application entry?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.delete(app_id)
            self.load_data()  # refresh UI