import string

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QBrush, QIcon, QPainter, QPalette, QPen, QPixmap
from PyQt5.QtWidgets import (QGridLayout, QHBoxLayout, QLabel, QPushButton,
                             QWidget)

from playground.games.minesweeper.game_cfg import (IMG_BOMB, IMG_CLOCK,
                                                   NUM_COLORS, STATUS_ICONS)
from playground.state_code import GameStatus


class MinesweeperUI:

    def __init__(self, parent, b_size):
        self.centralwidget = QWidget(parent)
        self.centralwidget.setObjectName('centralwidget')
        self.b_size = b_size

        self.gridLayout = QGridLayout(self.centralwidget)
        self.headerLayout = QHBoxLayout()
        self.minesLabel = QLabel(self.centralwidget)
        self.clockLabel = QLabel(self.centralwidget)
        self.statusButton = QPushButton(self.centralwidget)

        bomb_icon = QLabel(self.centralwidget)
        bomb_icon.setPixmap(QPixmap.fromImage(IMG_BOMB))
        bomb_icon.setFixedSize(QSize(32, 32))
        bomb_icon.setScaledContents(True)

        clock_icon = QLabel(self.centralwidget)
        clock_icon.setPixmap(QPixmap.fromImage(IMG_CLOCK))
        clock_icon.setFixedSize(QSize(32, 32))
        clock_icon.setScaledContents(True)

        self.headerLayout.addWidget(bomb_icon)
        self.headerLayout.addWidget(self.minesLabel)
        self.headerLayout.addWidget(self.statusButton)
        self.headerLayout.addWidget(self.clockLabel)
        self.headerLayout.addWidget(clock_icon)

        self.gridLayout.addLayout(self.headerLayout, 0, 0, 1, 1)
        self.gameGrid = QGridLayout()
        self.gridLayout.addLayout(self.gameGrid, 1, 0, 1, 1)

        self.statusButton.setIcon(QIcon(STATUS_ICONS[GameStatus.IN_PROGRESS]))
        self.statusButton.setIconSize(QSize(32, 32))
        self.statusButton.setFlat(True)

        for x in range(1, self.b_size + 1):
            label = QLabel(str(x))
            label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.gameGrid.addWidget(label, 0, x)
        for y in range(1, self.b_size + 1):
            label = QLabel(string.ascii_lowercase[y - 1])
            label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.gameGrid.addWidget(label, y, 0)
        for x in range(1, self.b_size + 1):
            for y in range(1, self.b_size + 1):
                self.gameGrid.addWidget(Pos(x - 1, y - 1), y, x)


class Pos(QWidget):

    def __init__(self, x, y):
        super().__init__()
        self.setFixedSize(QSize(20, 20))
        self.x = x
        self.y = y
        self.is_mine = False
        self.adjacent_n = 0
        self.is_revealed = False

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = event.rect()
        if self.is_revealed:
            color = self.palette().color(QPalette.Background)
            outer, inner = color, color
        else:
            outer, inner = Qt.gray, Qt.lightGray
        p.fillRect(r, QBrush(inner))
        pen = QPen(outer)
        pen.setWidth(1)
        p.setPen(pen)
        p.drawRect(r)
        if self.is_revealed:
            if self.is_mine:
                p.drawPixmap(r, QPixmap(IMG_BOMB))
            elif self.adjacent_n > 0:
                pen = QPen(NUM_COLORS[self.adjacent_n])
                p.setPen(pen)
                f = p.font()
                f.setBold(True)
                p.setFont(f)
                p.drawText(r, Qt.AlignHCenter | Qt.AlignVCenter,
                           str(self.adjacent_n))
