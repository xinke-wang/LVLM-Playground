from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName('MainWindow')
        MainWindow.resize(500, 600)
        MainWindow.setMinimumSize(QtCore.QSize(500, 600))
        MainWindow.setMaximumSize(QtCore.QSize(500, 600))
        MainWindow.setStyleSheet('')
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName('centralwidget')

        font = QtGui.QFont()
        font.setPointSize(1)

        self.buttons = []
        positions = [(i, j) for i in range(3) for j in range(3)]
        for idx, pos in enumerate(positions):
            button = QtWidgets.QPushButton(self.centralwidget)
            button.setGeometry(
                QtCore.QRect(50 + pos[1] * 140, 100 + pos[0] * 140, 140, 140))
            button.setFont(font)
            button.setText(str(idx + 1))
            button.setObjectName(f'button_{idx + 1}')
            self.buttons.append(button)

        self.row_labels = []
        rows = ['A', 'B', 'C']
        for i, row in enumerate(rows):
            label = QtWidgets.QLabel(self.centralwidget)
            label.setGeometry(QtCore.QRect(30, 170 + i * 140, 20, 20))
            label.setText(row)
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setFont(QtGui.QFont('Arial', 16, QtGui.QFont.Bold))
            self.row_labels.append(label)

        self.column_labels = []
        columns = ['1', '2', '3']
        for i, column in enumerate(columns):
            label = QtWidgets.QLabel(self.centralwidget)
            label.setGeometry(QtCore.QRect(105 + i * 140, 70, 20, 20))
            label.setText(column)
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setFont(QtGui.QFont('Arial', 16, QtGui.QFont.Bold))
            self.column_labels.append(label)

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(50, 10, 351, 71))
        font = QtGui.QFont()
        font.setFamily('URW Gothic')
        font.setPointSize(20)
        self.label.setFont(font)

        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(50, 30, 351, 51))
        font2 = QtGui.QFont()
        font2.setFamily('URW Gothic')
        font2.setPointSize(20)
        font2.setWeight(50)
        self.label_2.setFont(font2)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate('MainWindow', 'Tic Tac Toe'))
