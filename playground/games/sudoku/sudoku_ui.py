import string

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class SudokuUI:

    def __init__(self, parent):
        self.centralwidget = QWidget(parent)
        self.centralwidget.setObjectName('centralwidget')

        layout = QVBoxLayout(self.centralwidget)
        layout.setSpacing(0)
        self.secondPageWidget = QWidget(self.centralwidget)
        layout.addWidget(self.secondPageWidget)

        self.centralwidget.setStyleSheet('background-color: white')
        self.secondPageWidget.setStyleSheet(
            'margin: 0; padding: 0px; background-color: white;')

        self.setup_second_page()

    def setup_second_page(self):
        self.setup_borders()
        self.setup_grid_buttons()
        self.setup_row_labels()
        self.setup_col_labels()

    def setup_borders(self):
        self.border_lines = [QWidget(self.secondPageWidget) for _ in range(4)]
        self.border_lines[0].setGeometry(50, 100, 424, 3)
        self.border_lines[1].setGeometry(50, 100, 3, 424)
        self.border_lines[2].setGeometry(470, 100, 3, 424)
        self.border_lines[3].setGeometry(50, 520, 424, 3)
        for line in self.border_lines:
            line.setStyleSheet('background-color: black')

        self.main_vertical_lines = [
            QWidget(self.secondPageWidget) for _ in range(2)
        ]
        self.main_vertical_lines[0].setGeometry(190, 100, 3, 422)
        self.main_vertical_lines[1].setGeometry(330, 100, 3, 422)
        for line in self.main_vertical_lines:
            line.setStyleSheet('background-color: black')

        self.main_horizontal_lines = [
            QWidget(self.secondPageWidget) for _ in range(2)
        ]
        self.main_horizontal_lines[0].setGeometry(50, 240, 422, 3)
        self.main_horizontal_lines[1].setGeometry(50, 380, 422, 3)
        for line in self.main_horizontal_lines:
            line.setStyleSheet('background-color: black')

        self.internal_vertical_lines = [
            QWidget(self.secondPageWidget) for _ in range(6)
        ]
        row_gap = 98
        for i, line in enumerate(self.internal_vertical_lines):
            if i > 0 and i % 2 == 0:
                row_gap += 48
            line.setGeometry(row_gap, 100, 1, 422)
            line.setStyleSheet('background-color: black')
            row_gap += 46

        self.internal_horizontal_lines = [
            QWidget(self.secondPageWidget) for _ in range(6)
        ]
        col_gap = 148
        for i, line in enumerate(self.internal_horizontal_lines):
            if i > 0 and i % 2 == 0:
                col_gap += 48
            line.setGeometry(50, col_gap, 422, 1)
            line.setStyleSheet('background-color: black')
            col_gap += 46

    def setup_grid_buttons(self):
        self.puzzle_buttons = [[
            QPushButton('', self.secondPageWidget) for _ in range(9)
        ] for _ in range(9)]
        gap_col = 0
        for j in range(9):
            gap_row = 0
            if j % 3 == 0:
                gap_col += 2
            for i in range(9):
                if i % 3 == 0:
                    gap_row += 2
                btn = self.puzzle_buttons[j][i]
                btn.setGeometry(51 + i * 45 + gap_row, 101 + j * 45 + gap_col,
                                45, 45)
                btn.setStyleSheet(
                    'background-color: white; font-family: sans-serif; font-size: 25px; border: 1px solid black;'  # noqa
                )
                gap_row += 1
            gap_col += 1

    def setup_row_labels(self):
        """Setup row labels A-I on the left side of the grid."""
        self.row_labels = []
        for i in range(9):
            label = QLabel(string.ascii_uppercase[i], self.secondPageWidget)
            label.setGeometry(30, 101 + i * 45 + (45 - 25) // 2, 20, 25)
            label.setStyleSheet(
                'color: black; background-color: white; font-family: sans-serif; font-size: 20px;'  # noqa
            )
            label.setAlignment(Qt.AlignCenter)
            self.row_labels.append(label)

    def setup_col_labels(self):
        """Setup column labels 1-9 on the top of the grid."""
        self.col_labels = []
        for i in range(9):
            label = QLabel(str(i + 1), self.secondPageWidget)
            label.setGeometry(51 + i * 45 + (45 - 25) // 2, 75, 25, 20)
            label.setStyleSheet(
                'color: black; background-color: white; font-family: sans-serif; font-size: 20px;'  # noqa
            )
            label.setAlignment(Qt.AlignCenter)
            self.col_labels.append(label)
