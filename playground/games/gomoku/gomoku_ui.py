from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName('MainWindow')
        MainWindow.resize(1000, 1000)
        MainWindow.setMinimumSize(QtCore.QSize(1000, 1000))
        MainWindow.setMaximumSize(QtCore.QSize(1000, 1000))
        MainWindow.setStyleSheet('')
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName('centralwidget')
        self.chessboard = QtWidgets.QWidget(self.centralwidget)
        self.chessboard.setGeometry(QtCore.QRect(0, 0, 1000, 1000))
        self.chessboard.setStyleSheet(
            'border-image: url(:/bg/image/chessboard.png);')
        self.chessboard.setObjectName('chessboard')
        self.result_label = QtWidgets.QLabel(self.centralwidget)
        self.result_label.setGeometry(QtCore.QRect(240, 239, 521, 191))
        font = QtGui.QFont()
        font.setPointSize(90)
        self.result_label.setFont(font)
        self.result_label.setText('')
        self.result_label.setObjectName('result_label')
        self.chessboard.raise_()
        self.result_label.raise_()
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate('MainWindow', 'MainWindow'))


import playground.games.gomoku.gomoku_qrc_rc  # noqa
