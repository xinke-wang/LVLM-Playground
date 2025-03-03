from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QPen

WHITE = Qt.white
BLACK = Qt.black
GREEN = QColor(0, 128, 0)
CELL_SIZE = 400 // 8


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName('MainWindow')
        MainWindow.resize(500, 600)
        MainWindow.setMinimumSize(QtCore.QSize(500, 600))
        MainWindow.setMaximumSize(QtCore.QSize(500, 600))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName('centralwidget')

        font = QtGui.QFont()
        font.setPointSize(12)

        self.player_label = QtWidgets.QLabel(self.centralwidget)
        self.player_label.setGeometry(QtCore.QRect(100, 450, 300, 50))
        self.player_label.setFont(font)
        self.player_label.setAlignment(QtCore.Qt.AlignCenter)

        self.restart_button = QtWidgets.QPushButton(self.centralwidget)
        self.restart_button.setGeometry(QtCore.QRect(200, 500, 100, 40))
        self.restart_button.setText('Restart')
        self.restart_button.setFont(font)

        MainWindow.setCentralWidget(self.centralwidget)

    def draw_board(self, qp, board):
        for y in range(8):
            for x in range(8):
                qp.setBrush(QBrush(GREEN))
                qp.drawRect(x * CELL_SIZE + 60, y * CELL_SIZE + 40, CELL_SIZE,
                            CELL_SIZE)
                qp.setPen(QPen(BLACK))
                qp.drawRect(x * CELL_SIZE + 60, y * CELL_SIZE + 40, CELL_SIZE,
                            CELL_SIZE)
                if board[y][x] == 2:
                    qp.setBrush(QBrush(WHITE))
                    qp.drawEllipse(
                        QRect(int(x * CELL_SIZE + CELL_SIZE / 6 + 60),
                              int(y * CELL_SIZE + CELL_SIZE / 6 + 40),
                              CELL_SIZE * 2 // 3, CELL_SIZE * 2 // 3))
                elif board[y][x] == 1:
                    qp.setBrush(QBrush(BLACK))
                    qp.drawEllipse(
                        QRect(int(x * CELL_SIZE + CELL_SIZE / 6 + 60),
                              int(y * CELL_SIZE + CELL_SIZE / 6 + 40),
                              CELL_SIZE * 2 // 3, CELL_SIZE * 2 // 3))

    def draw_labels(self, qp):
        qp.setPen(Qt.black)
        label_font = QFont('Arial', 14, QFont.Bold)
        qp.setFont(label_font)

        for col in range(8):
            label = str(col + 1)
            qp.drawText(col * CELL_SIZE + 60 + CELL_SIZE // 2 - 5, 35, label)

        for row in range(8):
            label = chr(ord('A') + row)
            qp.drawText(35, row * CELL_SIZE + 40 + CELL_SIZE // 2 + 5, label)
