import sqlite3
import sys
from dataclasses import dataclass
from typing import List

import PyQt5.uic as uic
from PyQt5.QtWidgets import (QApplication,
                             QWidget,
                             QFileDialog,
                             QMessageBox, QTableWidgetItem)


@dataclass
class Coffee:
    name: str
    roasting_level: str
    state: str
    taste_description: str
    cost: int
    volume: int

    def __iter__(self):
        yield from [self.name, self.roasting_level, self.state, self.taste_description, self.cost, self.volume]


getting_all_records_request = """
SELECT coffee.name, roasting_levels.name, states.name, taste_description, cost, volume FROM coffee
INNER JOIN roasting_levels ON roasting_level = roasting_levels.id
INNER JOIN states ON state = states.id;
"""


def get_all_records(connection: sqlite3.Connection) -> List[Coffee]:
    cursor = connection.cursor()
    data = map(lambda args: Coffee(*args), cursor.execute(getting_all_records_request).fetchall())
    return list(data)


class MainWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._data: List[Coffee] = []
        self._connection: sqlite3.Connection = None
        self._configure_ui()

    def _configure_ui(self) -> None:
        uic.loadUi('main.ui', self)
        self.load_button.clicked.connect(self._rise_db_dialog)

    def _load_db(self) -> None:
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Название',
                                              'Степень обжарки',
                                              'Состояние',
                                              'Описание',
                                              'Цена (руб)',
                                              'Объем (куб. см)'])
        records = get_all_records(self._connection)
        self.table.setRowCount(len(records))
        for row, record in enumerate(records):
            for column, elem in enumerate(record):
                self.table.setItem(row, column, QTableWidgetItem(str(elem)))
        self.table.resizeColumnsToContents()

    def _rise_db_dialog(self):
        filepath = QFileDialog.getOpenFileName()[0]
        try:
            self._connection = sqlite3.connect(filepath)
            self._load_db()
        except FileNotFoundError:
            QMessageBox.information(self, 'Ошибка!', 'Файл не найден :(')
        except sqlite3.Error:
            QMessageBox.information(self, 'Ошибка!', 'Ошибка при чтении файла :(')


def main():
    app = QApplication(sys.argv)
    main_widget = MainWidget()
    main_widget.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
