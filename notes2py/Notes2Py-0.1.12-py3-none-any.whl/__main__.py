import os
import sys
from pathlib import Path

from PyQt6 import QtWidgets
from tinydb import TinyDB

from notes2py.ui.main import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, session: TinyDB, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.session = session
        self.setupUi(self)
        self.save_note.clicked.connect(self.save_note_handler)
        self.add_note.clicked.connect(self.add_new_note)
        self.delete_note.clicked.connect(self.delete_note_handler)
        self.notes_list.itemSelectionChanged.connect(self.show_note_handler)

    def add_new_note(self):
        self.notes_list.addItem("Новая заметка")
        self.session.insert(
            {"name": "Новая заметка", "text": "Текст заметки"}
        )
        self.notes_list.setCurrentRow(self.notes_list.count() - 1)

    def save_note_handler(self):
        self.session.update(
            {
                "text": self.textEdit.toPlainText(),
                "name": self.name_field.text(),
            },
            doc_ids=[self.notes_list.currentRow() + 1],
        )
        self.notes_list.clear()
        self.notes_list.addItems([item['name'] for item in db_session.all()])

    def delete_note_handler(self):
        self.session.remove(doc_ids=[self.notes_list.currentIndex().row()])
        self.notes_list.takeItem(self.notes_list.currentIndex().row())

    def show_note_handler(self):
        self.textEdit.setText(self.session.get(doc_id=self.notes_list.currentRow() + 1)["text"])
        self.name_field.setText(self.session.get(doc_id=self.notes_list.currentRow() + 1)["name"])


if __name__ == "__main__":
    db_session = TinyDB(os.path.join(Path(__file__).parent.parent, "database.json"))
    db_session.default_table_name = "notes"
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(db_session)
    window.notes_list.addItems([item['name'] for item in db_session.all()])
    window.show()
    app.exec()
