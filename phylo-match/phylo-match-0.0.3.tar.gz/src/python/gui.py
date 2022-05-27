import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, \
    QHBoxLayout, QGridLayout, QLabel, QLineEdit
from src.python.definitions import *
from src.python.match import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


class LoadingWindow(QMainWindow):
    def __init__(self, parent=None):
        super(LoadingWindow, self).__init__(parent)
        self.setWindowTitle("Loading, please wait...")


class MainMenu(QMainWindow):
    # TODO: allow for setting of DB_PATH, TREE_PATH, and before run
    def __init__(self, parent=None):
        super(MainMenu, self).__init__(parent)

        # Create main_layout
        self.main_widget = QWidget()
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QGridLayout(self.main_widget)

        # Set stylesheets
        self.file_selection_stylesheet = "padding: 5px; border-radius: 0px; background-color: white; color: black; border: black 1px;"

        # Add db selection layout
        self.db_selection_layout = QGridLayout()
        self.main_layout.addLayout(self.db_selection_layout, 0, 0)

        # Add nexus selection layout
        self.nexus_selection_layout = QGridLayout()
        self.main_layout.addLayout(self.nexus_selection_layout, 0, 1)

        # Add file run button layout
        self.run_button_layout = QGridLayout()
        self.main_layout.addLayout(self.run_button_layout, 1, 1)

        # Add db selection button
        self.db_label = QLabel("Database File Selection")
        self.db_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.db_label.setFixedHeight(self.db_label.font().pointSize()*2)

        self.db_path = DB_PATH
        self.db_path_label = QLabel()
        self.db_path_label.setStyleSheet(self.file_selection_stylesheet)
        self.db_path_label.setFixedHeight(self.db_path_label.font().pointSize()*2)

        self.db_file_selection = QPushButton("Change")
        self.db_file_selection.clicked.connect(self.select_db_file)

        self.db_selection_layout.addWidget(self.db_label, 0, 0, 1, 2)
        self.db_selection_layout.addWidget(self.db_path_label, 2, 0, 1, 2)
        self.db_selection_layout.addWidget(self.db_file_selection, 4, 0, 1, 1)

        # Add nexus selection button
        self.nexus_label = QLabel("Nexus File Selection")
        self.nexus_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.nexus_label.setFixedHeight(self.nexus_label.font().pointSize()*2)

        self.nexus_file_selection = QPushButton("Change")
        self.nexus_file_selection.clicked.connect(self.select_nexus_file)

        self.nexus_path = TREE_PATH
        self.nexus_path_label = QLabel()
        self.nexus_path_label.setStyleSheet(self.file_selection_stylesheet)
        self.nexus_path_label.setFixedHeight(self.nexus_path_label.font().pointSize()*2)

        self.nexus_selection_layout.addWidget(self.nexus_label, 0, 0, 1, 2)
        self.nexus_selection_layout.addWidget(self.nexus_path_label, 2, 0, 1, 2)
        self.nexus_selection_layout.addWidget(self.nexus_file_selection, 4, 0, 1, 1)

        # Add run button
        self.run_button_spacer = QLabel()
        self.run_button = QPushButton("Run")
        self.run_button.setEnabled(False)
        self.run_button.clicked.connect(self.start_match)
        self.run_button_layout.addWidget(self.run_button_spacer)
        self.run_button_layout.addWidget(self.run_button)
        self.nexus_file_selected = False
        self.db_file_selected = False

        self.loading_window = LoadingWindow(self)
        self.dialogs = list()

    def select_nexus_file(self):
        self.nexus_path = QFileDialog.getOpenFileName(self, 'Open file',
                                            f'{TREE_PATH}', "Tree files (*.nex *.csv)")[0]
        self.nexus_path_label.setText(os.path.basename(self.nexus_path))

        self.nexus_file_selected = True
        if self.nexus_file_selected and self.db_file_selected:
            self.run_button.setEnabled(True)

    def select_db_file(self):
        self.db_path = QFileDialog.getOpenFileName(self, 'Open file',
                                                      f'{DB_PATH}', "Tree files (*.nex *.csv)")[0]
        self.db_path_label.setText(os.path.basename(self.db_path))

        self.db_file_selected = True
        if self.nexus_file_selected and self.db_file_selected:
            self.run_button.setEnabled(True)

    def start_match(self):
        # Might include other functionality, such as loading bar
        self.run_match()

    def run_match(self):
        compare_window = Compare(self)
        self.dialogs.append(compare_window)

        dbs, tree = read_files(self.db_path, self.nexus_path)
        taxa_list = match(dbs, tree, "_", 4)

        # Cached_info may be cached remotely or locally in future versions
        # cached_info = read_wiki_file(INFO_PATH, INFO_FNAME)
        cached_info = []

        missing_info = validate_info(cached_info, taxa_list)
        # This serves to call the information to cache at the beginning of a run, so a user can wait all at once at the beginning instead of iteratively
        wiki_info = get_wiki_info(missing_info)

        # No file caching
        # if wiki_info:
        #     write_wiki_file(wiki_info, INFO_PATH, INFO_FNAME)

        compare_window.__init__(self)

        compare_window.setParent(self)
        compare_window.set_db_path(self.db_path)
        compare_window.compare_mismatch(iter(taxa_list), compare_window)
        self.hide()


# dialog.close()

#
# start_time = time.time()
# taxa_list = db_match(DB_PATH, TREE_PATH, "_", 4)
#
# compare = Compare(self)
# compare.compare_mismatch(self, iter(taxa_list))


class Compare(QMainWindow):
    def __init__(self, parent=None):
        super(Compare, self).__init__(parent)
        self.setWindowTitle("compare")

        self.db_path = ""

        # Create main_layout
        self.main_widget = QWidget()
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QGridLayout(self.main_widget)

        # Create sub-layouts for main_layout and order them
        self.info_layout_style = QWidget()
        self.info_layout_style.setStyleSheet("border-width: 1px; border-style: solid; border-color: black white black black;")
        self.main_layout.addWidget(self.info_layout_style, 0, 0, 3, 1)

        self.info_layout = QVBoxLayout()
        self.main_layout.addLayout(self.info_layout, 0, 0,)

        self.taxa_layout = QVBoxLayout()
        self.taxa_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addLayout(self.taxa_layout, 1, 0)

        self.count_layout = QHBoxLayout()
        self.main_layout.addLayout(self.count_layout, 0, 1)

        self.suggestions_layout = QHBoxLayout()
        self.main_layout.addLayout(self.suggestions_layout, 1, 1)

        self.manual_entry_layout = QVBoxLayout()
        self.main_layout.addLayout(self.manual_entry_layout, 2, 1, 1, 2)

        # Add contents to info_layout
        self.taxa_label = QLabel("animals_animals")
        self.taxa_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.taxa_label.setStyleSheet("padding: 30px; border-radius: 0px; background-color: lightgray; color: black;")
        self.info_layout.addWidget(self.taxa_label, 1)

        # Add contents to taxa_layout
        self.removed_suggestions_label = QLabel()
        self.removed_suggestions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.removed_suggestions_label.setContentsMargins(5, 5, 5, 5)
        self.removed_suggestions_count = QLabel()
        self.removed_suggestions_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.taxa_layout.addWidget(self.removed_suggestions_count, 1)

        # Add contents to count_layout
        self.options_count_label = QHBoxLayout()
        self.options_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.similar_entries_count = QPushButton()
        self.options_count_label.addWidget(self.similar_entries_count)
        self.same_species_count = QPushButton()
        self.options_count_label.addWidget(self.same_species_count)
        self.same_genus_count = QPushButton()
        self.options_count_label.addWidget(self.same_genus_count)
        self.count_layout.addLayout(self.options_count_label, 1)

        # Create label for main taxa info, to be attached as needed
        self.taxa_info = QLabel("So many options!")
        self.taxa_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add contents to manual_entry_layout
        self.entry_label = QLabel("Manual Entry:")
        self.manual_entry_layout.addWidget(self.entry_label)
        self.line_edit = QLineEdit()
        self.manual_entry_layout.addWidget(self.line_edit)
        self.manual_btn = QPushButton("Enter", self)
        self.manual_btn.setMaximumWidth(150)
        self.manual_entry_layout.addWidget(self.manual_btn)
        self.leave_btn = QPushButton("Leave as is", self)
        self.leave_btn.setMaximumWidth(150)
        self.manual_entry_layout.addWidget(self.leave_btn)
        self.manual_entry_layout.setContentsMargins(10, 10, 10, 10)

        # Init global variables
        self.removed_suggestions = []
        self.taxa_list = []

    def set_db_path(self, db_path):
        self.db_path = db_path

    def compare_mismatch(self, taxa_iter, compare_window):

        next_taxa = next(taxa_iter, None)
        if next_taxa:
            # Type Str indicates to move on
            if type(next_taxa) == str:
                self.taxa_list.append(next_taxa)
                self.compare_mismatch(taxa_iter, compare_window)
            else:
                db_taxa = next_taxa[0]

                i = 1

                next_taxa = self.remove_chosen_entries(next_taxa)

                self.show_suggestions(next_taxa, taxa_iter, i)

                self.taxa_label.setText(db_taxa)
                compare_window.setGeometry(100, 100, 600, 400)
                compare_window.show()
        else:
            # End of file, record results
            write_file(self.taxa_list, self.db_path)
            # Open main menu
            self.parent().show()
            self.close()

    def make_confirm_function(self, suggestion, taxa_iter, compare_window):
        def confirm_suggestion():
            self.taxa_list.append(suggestion)

            self.line_edit.clear()
            self.removed_suggestions.clear()

            self.compare_mismatch(taxa_iter, compare_window)

        return confirm_suggestion

    def remove_chosen_entries(self, taxa):

        taxa_name = taxa[0]

        for taxa_suggestions in taxa:
            if type(taxa_suggestions) != str:
                for suggestion in taxa_suggestions:
                    # Remove suggestions that have already been chosen
                    # TODO: do this for entire suggestions list at beginning of new taxa to avoid changing once clicking
                    if suggestion in self.taxa_list:
                        self.removed_suggestions.append(suggestion)
                        taxa_suggestions.remove(suggestion)
                        continue
        return taxa

    def confirm_text(self, suggestion, taxa_iter, compare_window):
        # TODO: close window more intelligently
        self.taxa_list.append(suggestion)

        self.line_edit.clear()
        self.removed_suggestions.clear()

        self.compare_mismatch(taxa_iter, compare_window)

    def create_wiki_label(self, taxa):
        # Create text box from wiki
        label = QLabel()
        label.setScaledContents(True)
        try:
            label.setText(get_wiki_section(taxa))
        except:
            label.setText("No information found")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.show()

        # Create scroll area for text box
        scroll = QScrollArea()
        scroll.setWidget(label)
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setFixedHeight(200)
        scroll.setMaximumWidth(200)

        return scroll

    def create_wiki_layout(self, taxa, taxa_iter):
        # TODO: reimplement count_layout?

        # url_image = get_wiki_image(taxa)
        # Get wiki information, and image if it's available
        # try:
        #     if url_image != 0:
        #         image = QImage()
        #         image.loadFromData(requests.get(url_image).content)
        #
        #         label.setPixmap(QPixmap(image))
        # except:
        #     label.setText("Cannot find " + taxa)

        # Create base main_layout for taxa selection
        taxa_layout = QVBoxLayout()
        taxa_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create taxa selection button
        btn = QPushButton(taxa, self)
        btn.setStyleSheet("padding: 20px; border-radius: 15px; background-color: gray;")
        # btn.adjustSize()
        f = self.make_confirm_function(taxa, taxa_iter, self)
        btn.clicked.connect(f)
        taxa_layout.addWidget(btn)

        scroll = self.create_wiki_label(taxa)
        taxa_layout.addWidget(scroll)
        taxa_layout.setContentsMargins(10, 5, 10, 5)

        return taxa_layout

    def show_suggestions(self, next_taxa, taxa_iter, i):

        # Clear old buttons + count_layout
        for j in reversed(range(self.suggestions_layout.count())):
            layout = self.suggestions_layout.itemAt(j).layout()
            self.suggestions_layout.removeItem(layout)
            for k in reversed(range(layout.count())):
                layout.itemAt(k).widget().setParent(None)


        self.removed_suggestions_label.setParent(None)
        self.removed_suggestions_count.setText(f"Removed Suggestions: {len(self.removed_suggestions)}")
        if self.removed_suggestions:
            self.removed_suggestions_label.setText(", ".join(self.removed_suggestions))
            self.taxa_layout.addWidget(self.removed_suggestions_label, 1)

        num_suggestions = [len(next_taxa[1]), len(next_taxa[2]), len(next_taxa[3])]

        if i <= 3:
            category_suggestions = next_taxa[i]
            while not category_suggestions:
                i += 1
                if i > 3:
                    break
                category_suggestions = next_taxa[i]

            if i <= 3:
                # reset and load taxa, if possible
                self.taxa_info.setParent(None)
                self.taxa_info = self.create_wiki_label(next_taxa[0])
                h_layout = QHBoxLayout()
                h_layout.addWidget(self.taxa_info)
                self.taxa_layout.insertLayout(0, h_layout)

                for suggestion in category_suggestions:

                    # Add info and image widget to page
                    suggestion_layout = self.create_wiki_layout(suggestion, taxa_iter)
                    self.suggestions_layout.addLayout(suggestion_layout)

                # Check that all category_suggestions were not removed by being previously picked, continue if they were
                if not category_suggestions:
                    i += 1
                    self.show_suggestions(next_taxa, taxa_iter, i)

            # TODO: get this logic outside of the category_suggestions, so it's not doing it every time
            # Set button text
            self.similar_entries_count.setText(f"Similar Entries: {num_suggestions[0]}")
            self.same_species_count.setText(f"Same Species: {num_suggestions[1]}")
            self.same_genus_count.setText(f"Same Genus: {num_suggestions[2]}")

            # Unlink buttons, if needed
            try:
                self.similar_entries_count.clicked.disconnect()
            except Exception:
                pass
            try:
                self.same_species_count.clicked.disconnect()
            except Exception:
                pass
            try:
                self.same_genus_count.clicked.disconnect()
            except Exception:
                pass

            # Link buttons, if category_suggestions exist for those categories
            if num_suggestions[0] > 0: self.similar_entries_count.clicked.connect(
                lambda: self.show_suggestions(next_taxa, taxa_iter, 1))
            if num_suggestions[1] > 0: self.same_species_count.clicked.connect(
                lambda: self.show_suggestions(next_taxa, taxa_iter, 2))
            if num_suggestions[2] > 0: self.same_genus_count.clicked.connect(
                lambda: self.show_suggestions(next_taxa, taxa_iter, 3))

        if i == 1:
            self.setWindowTitle("Similar Entries")
        elif i == 2:
            self.setWindowTitle("Same Species")
        elif i == 3:
            self.setWindowTitle("Same Genus")
        else:
            self.setWindowTitle("No Suggestions")

        # Disconnect if already connected
        try:
            self.manual_btn.clicked.disconnect()
        except Exception:
            pass
        try:
            self.leave_btn.clicked.disconnect()
        except Exception:
            pass

        # Chooses the text entry box
        self.manual_btn.setEnabled(False)
        self.line_edit.textChanged.connect(self.disableManualButton)
        self.manual_btn.clicked.connect(lambda: self.confirm_text(self.line_edit.text(), taxa_iter, self))
        # Chooses the text entry box
        self.leave_btn.clicked.connect(lambda: self.confirm_text("", taxa_iter, self))

    def disableManualButton(self):
        if len(self.line_edit.text()) > 0:
            self.manual_btn.setEnabled(True)
        else:
            self.manual_btn.setEnabled(False)

def main():
    app = QApplication(sys.argv)
    main = MainMenu()
    main.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
