import os
import sys
from pathlib import Path

from PyQt6 import QtWidgets
from tinydb import TinyDB, Query, where

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
            {
                "id": self.notes_list.count() - 1,
                "name": "Новая заметка",
                "text": "Текст заметки",
            }
        )
        self.notes_list.setCurrentRow(self.notes_list.count() - 1)

    def save_note_handler(self):
        if self.notes_list.currentRow() != -1:
            self.session.update(
                {
                    "text": self.textEdit.toPlainText(),
                    "name": self.name_field.text(),
                },
                cond=where("id") == self.notes_list.currentRow(),
            )
            self.notes_list.clear()
            self.notes_list.addItems([item["name"] for item in self.session.all()])

    def delete_note_handler(self):
        Note = Query()
        self.notes_list.takeItem(self.notes_list.currentIndex().row())
        self.session.remove(Note.id == int(self.notes_list.currentRow()))
        items = [
            {"id": index, "name": item["name"], "text": item["text"]}
            for index, item in enumerate(self.session.all())
        ]
        self.session.truncate()
        self.session.insert_multiple(items)

    def show_note_handler(self):
        Note = Query()
        if self.notes_list.count() == 1:
            self.save_note.setVisible(False)
            self.delete_note.setVisible(False)
            self.name_field.setVisible(False)
            self.name_label.setVisible(False)
            self.textEdit.setVisible(False)
            return
        else:
            self.save_note.setVisible(True)
            self.delete_note.setVisible(True)
            self.name_field.setVisible(True)
            self.name_label.setVisible(True)
            self.textEdit.setVisible(True)
        print(self.notes_list.currentRow())
        current_id = int(
            self.session.search(Note.id == int(self.notes_list.currentRow()))[0]["id"]
        )
        note = self.session.search(Note.id == current_id)[0]
        self.textEdit.setText(note["text"])
        self.name_field.setText(note["name"])


def main():
    db_session = TinyDB(os.path.join(Path(__file__).parent.parent, "database.json"))
    db_session.default_table_name = "notes"
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(db_session)
    window.notes_list.addItems([item["name"] for item in db_session.all()])
    window.save_note.setVisible(False)
    window.delete_note.setVisible(False)
    window.name_field.setVisible(False)
    window.name_label.setVisible(False)
    window.textEdit.setVisible(False)
    window.show()
    app.exec()
    db_session.close()


if __name__ == "__main__":
    main()
