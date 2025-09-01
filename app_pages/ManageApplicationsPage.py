import os
from database.Database import Database

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (
    QComboBox, QHeaderView, QLabel, QMessageBox,
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
    HEADERS = ["Company", "Job Title", "Deadline", "Status", "CV Word Doc", "CL Word Doc", "Delete Application"]
    

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
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Open CV
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Open CL
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
            #CV_file_path = rec["CV_file_path"]

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
            #file_item = QTableWidgetItem(CV_file_path)
            #file_item.setToolTip(CV_file_path)  # hover to see full path
            #self.setItem(r, 4, file_item)

            # Open CV button
            open_CV_btn = QPushButton("Open CV")
            open_CV_btn.setProperty("app_id", app_id)
            open_CV_btn.clicked.connect(
                lambda _, b=open_CV_btn: self.on_open_CV_clicked(b.property("app_id"))
            )
            self.setCellWidget(r, 4, open_CV_btn)

            # Open CL button
            open_CL_btn = QPushButton("Open Cover Letter")
            open_CL_btn.setProperty("app_id", app_id)
            open_CL_btn.clicked.connect(
                lambda _, b=open_CL_btn: self.on_open_CL_clicked(b.property("app_id"))
            )
            self.setCellWidget(r, 5, open_CL_btn)

            # Delete button
            del_btn = QPushButton("Delete")
            del_btn.setProperty("app_id", app_id)
            del_btn.clicked.connect(
                lambda _, b=del_btn: self.on_delete_clicked(b.property("app_id"))
            )
            self.setCellWidget(r, 6, del_btn)

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

    def on_open_CV_clicked(self, app_id: int):
        path = self.db.get_CV_file_path(app_id)
        if not path or not os.path.exists(path):
            QMessageBox.warning(self, "File not found",
                                "No file found for this entry.\n\nPath:\n" + (path or "<empty>"))
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def on_open_CL_clicked(self, app_id: int):
        path = self.db.get_CL_file_path(app_id)
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

class ManageApplicationsPage(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db

        self.table = JobTable(db)
        info = QLabel("Tip: change Status via the dropdown; use Open/Delete per row.")
        info.setStyleSheet("color: gray;")

        layout = QVBoxLayout()
        layout.addWidget(info)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_data(self):
        self.table.load_data()
