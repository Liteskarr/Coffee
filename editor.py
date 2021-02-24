import sqlite3
import sys

import PyQt5.uic as uic
from PyQt5.QtWidgets import (QApplication,
                             QWidget,
                             QFileDialog,
                             QMessageBox,
                             QTableWidgetItem, QTableWidget)


deleting_coffee_request = """
DELETE FROM coffee;
"""

deleting_roasting_request = """
DELETE FROM roasting_levels;
"""

deleting_state_request = """
DELETE FROM states;
"""

inserting_coffee_request = """
INSERT INTO coffee
VALUES(?, ?, ?, ?, ?, ?, ?);
"""

inserting_roasting_request = """
INSERT INTO roasting_levels VALUES(?, ?);
"""

inserting_state_request = """
INSERT INTO states VALUES(?, ?);
"""

getting_coffee_request = """
SELECT name, roasting_level, state, taste_description, cost, volume FROM coffee;
"""

getting_roasting_request = """
SELECT name FROM roasting_levels;
"""

getting_state_request = """
SELECT name FROM states;
"""


def get_table_data(table: QTableWidget) -> list:
    result = []
    for row in range(table.rowCount()):
        data = []
        for column in range(table.columnCount()):
            data.append(table.item(row, column).text())
        result.append(data)
    return result


class EditorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._current_row = None
        self._configure_ui()

    def _configure_ui(self):
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.load_button.clicked.connect(self._rise_db_dialog)
        self.add_button.clicked.connect(self._add_row)
        self.save_button.clicked.connect(self._save_db)
        self.delete_button.clicked.connect(self._delete_row)
        self.coffee_table.cellClicked.connect(self._handle_cell_click)
        self.roasting_table.cellClicked.connect(self._handle_cell_click)
        self.state_table.cellClicked.connect(self._handle_cell_click)

    def _rise_db_dialog(self):
        filepath = QFileDialog.getOpenFileName()[0]
        try:
            self._connection = sqlite3.connect(filepath)
            self._load_db()
        except FileNotFoundError:
            QMessageBox.information(self, 'Ошибка!', 'Файл не найден :(')
        except sqlite3.Error:
            QMessageBox.information(self, 'Ошибка!', 'Ошибка при чтении файла :(')

    def _get_current_table(self) -> QTableWidget:
        if self.tabs.currentIndex() == 0:
            return self.coffee_table
        elif self.tabs.currentIndex() == 1:
            return self.roasting_table
        elif self.tabs.currentIndex() == 2:
            return self.state_table

    def _handle_cell_click(self, row: int, column: int):
        self._current_row = row

    def _add_row(self):
        table = self._get_current_table()
        table.setRowCount(table.rowCount() + 1)

    def _delete_row(self):
        if self._current_row is not None:
            table = self._get_current_table()
            table.removeRow(self._current_row)
        self._current_row = None

    def _load_db(self):
        cursor = self._connection.cursor()
        self.coffee_table.setColumnCount(6)
        self.coffee_table.setHorizontalHeaderLabels(['Название',
                                                     'Степень обжарки',
                                                     'Состояние',
                                                     'Описание',
                                                     'Цена (руб)',
                                                     'Объем (куб. см)'])
        for row, line in enumerate(cursor.execute(getting_coffee_request).fetchall()):
            self.coffee_table.setRowCount(row + 1)
            for column, item in enumerate(line):
                self.coffee_table.setItem(row, column, QTableWidgetItem(str(item)))

        self.roasting_table.setColumnCount(1)
        self.roasting_table.setHorizontalHeaderLabels(['Название'])
        for row, line in enumerate(cursor.execute(getting_roasting_request).fetchall()):
            self.roasting_table.setRowCount(row + 1)
            for column, item in enumerate(line):
                self.roasting_table.setItem(row, column, QTableWidgetItem(str(item)))

        self.state_table.setColumnCount(1)
        self.state_table.setHorizontalHeaderLabels(['Название'])
        for row, line in enumerate(cursor.execute(getting_state_request).fetchall()):
            self.state_table.setRowCount(row + 1)
            for column, item in enumerate(line):
                self.state_table.setItem(row, column, QTableWidgetItem(str(item)))

    def _save_db(self):
        cursor = self._connection.cursor()
        cursor.execute(deleting_coffee_request)
        cursor.execute(deleting_roasting_request)
        cursor.execute(deleting_state_request)
        coffee_data = map(lambda x: [x[0]] + x[1], enumerate(get_table_data(self.coffee_table)))
        for data in coffee_data:
            cursor.execute(inserting_coffee_request, data)
        roasting_data = map(lambda x: [x[0]] + x[1], enumerate(get_table_data(self.roasting_table)))
        for data in roasting_data:
            cursor.execute(inserting_roasting_request, data)
        state_data = map(lambda x: [x[0]] + x[1], enumerate(get_table_data(self.state_table)))
        for data in state_data:
            cursor.execute(inserting_state_request, data)
        self._connection.commit()


def enable_threads_exceptions() -> None:
    excepthook = sys.excepthook

    def exception_hook(exctype, value, traceback):
        excepthook(exctype, value, traceback)
        sys.exit(1)

    sys.excepthook = exception_hook


def main():
    app = QApplication(sys.argv)
    editor = EditorWidget()
    editor.show()
    app.exec()


if __name__ == '__main__':
    enable_threads_exceptions()
    main()
