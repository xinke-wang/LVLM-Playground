import os

from PyQt5.QtCore import (QEventLoop, QPropertyAnimation, Qt, QThread,
                          pyqtSignal)
from PyQt5.QtGui import QFont, QPixmap, QResizeEvent
from PyQt5.QtWidgets import QGridLayout, QLabel, QSizePolicy, QWidget

import playground.games.chess.common.common as common
from playground.games.chess.common.consts import PIECE_CONVERSION, PIECE_MAP
from playground.games.chess.position import Position

SQR_SIZE = 100


class ChessUI(QWidget):

    def __init__(self, parent=None, user_is_white=True):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)
        self.setFixedSize(800, 800)
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        self.sqr_size = SQR_SIZE
        self.user_is_white = user_is_white
        self.position = Position(common.starting_fen)
        self.search_thread = SearchThread(self)
        self.pieces = {}
        self.selected_piece = None
        self.selected_square = None
        self.draw_board_with_labels()
        self.reset_board()

    def resizeEvent(self, event: QResizeEvent):
        side = min(self.width(), self.height())
        self.setFixedSize(side, side)
        super().resizeEvent(event)

    def draw_board_with_labels(self):
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)

        for row in range(8):  # 0..7
            for col in range(8):  # 0..7
                square = QWidget(self)
                square.setSizePolicy(QSizePolicy.Expanding,
                                     QSizePolicy.Expanding)
                if (row + col) % 2 == 0:
                    square.setStyleSheet('background-color: #F0D9B5;')  # 浅
                else:
                    square.setStyleSheet('background-color: #B58863;')  # 深

                self.layout.addWidget(square, row + 1, col + 1)

        for i in range(10):
            self.layout.setRowStretch(i, 1)
            self.layout.setColumnStretch(i, 1)

        file_labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        for col in range(8):
            lbl = QLabel(file_labels[col], self)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFont(font)
            self.layout.addWidget(lbl, 0, col + 1)  # top row=0, col+1

        for col in range(8):
            lbl = QLabel(file_labels[col], self)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFont(font)
            self.layout.addWidget(lbl, 9, col + 1)

        rank_labels = ['8', '7', '6', '5', '4', '3', '2', '1']
        for row in range(8):
            lbl = QLabel(rank_labels[row], self)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFont(font)
            self.layout.addWidget(lbl, row + 1, 0)

        for row in range(8):
            lbl = QLabel(rank_labels[row], self)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFont(font)
            self.layout.addWidget(lbl, row + 1, 9)

    def place_piece(self, sqr_name, piece):
        if isinstance(piece, str):
            piece_symbol = piece
        else:
            piece_symbol = PIECE_CONVERSION.get(piece)

        if not piece_symbol:
            print(f'Unknown piece: {piece}')
            return

        piece_image = PIECE_MAP.get(piece_symbol)
        if not piece_image:
            print(f'Unknown piece: {piece_symbol}')
            return

        piece_label = PieceLabel(self, piece_image)
        pixmap_path = f'./playground/games/chess/assets/pieces/{piece_image}.png'  # noqa
        if not os.path.exists(pixmap_path):
            print(f'Image not found: {pixmap_path}')
        else:
            piece_label.setPixmap(QPixmap(pixmap_path))

        col, row = common.square_to_coords[sqr_name]
        self.layout.addWidget(piece_label, row + 1, col + 1)
        self.pieces[sqr_name] = piece_label

    def move_piece(self, src_sqr, dst_sqr):
        piece = self.pieces.get(src_sqr)
        if piece:
            dst_col, dst_row = common.square_to_coords[dst_sqr]
            dst_square = self.layout.itemAtPosition(dst_row + 1,
                                                    dst_col + 1).widget()

            animation = QPropertyAnimation(piece, b'pos')
            animation.setEndValue(dst_square.pos())
            animation.setDuration(500)
            animation.start()

            loop = QEventLoop()
            animation.finished.connect(loop.quit)
            loop.exec_()

            self.pieces[dst_sqr] = self.pieces.pop(src_sqr)
            piece.setParent(None)
            self.layout.removeWidget(piece)

    def reset_board(self):
        initial_positions = {
            'a8': 'r',
            'b8': 'n',
            'c8': 'b',
            'd8': 'q',
            'e8': 'k',
            'f8': 'b',
            'g8': 'n',
            'h8': 'r',
            'a7': 'p',
            'b7': 'p',
            'c7': 'p',
            'd7': 'p',
            'e7': 'p',
            'f7': 'p',
            'g7': 'p',
            'h7': 'p',
            'a1': 'R',
            'b1': 'N',
            'c1': 'B',
            'd1': 'Q',
            'e1': 'K',
            'f1': 'B',
            'g1': 'N',
            'h1': 'R',
            'a2': 'P',
            'b2': 'P',
            'c2': 'P',
            'd2': 'P',
            'e2': 'P',
            'f2': 'P',
            'g2': 'P',
            'h2': 'P'
        }

        self.clear()
        for sqr, piece in initial_positions.items():
            self.place_piece(sqr, piece)

    def refresh_from_state(self):
        self.clear()
        for sqr_index in range(64):
            piece = self.position.piece_at(sqr_index)
            sqr_name = common.squares_san[sqr_index]
            if piece:
                self.place_piece(sqr_name, piece.symbol())

    def clear(self):
        all_pieces = self.findChildren(QLabel)
        for piece in all_pieces:
            if isinstance(piece, PieceLabel):
                piece.setParent(None)


class PieceLabel(QLabel):

    def __init__(self, parent, piece):
        super().__init__(parent)
        self.piece = piece
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(1, 1)
        self.setScaledContents(True)
        self.setMouseTracking(True)
        self.show()


class SearchThread(QThread):
    move_signal = pyqtSignal(int)

    def __init__(self, board):
        super().__init__()
        self.board = board

    def run(self):
        move = self.board.search.iter_search(time_limit=1)
        self.board.parent().computer_move(move)
