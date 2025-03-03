from PyQt5.QtGui import QColor, QImage

from playground.state_code import GameStatus

IMG_BOMB = QImage('playground/games/minesweeper/images/bomb.png')
IMG_FLAG = QImage('playground/games/minesweeper/images/flag.png')
IMG_START = QImage('playground/games/minesweeper/images/rocket.png')
IMG_CLOCK = QImage('playground/games/minesweeper/images/clock-select.png')

STATUS_ICONS = {
    GameStatus.INVALID_MOVE: 'playground/games/minesweeper/images/plus.png',
    GameStatus.ERROR: 'playground/games/minesweeper/images/plus.png',
    GameStatus.IN_PROGRESS: 'playground/games/minesweeper/images/smiley.png',
    GameStatus.LOSE: 'playground/games/minesweeper/images/cross.png',
    GameStatus.WIN: 'playground/games/minesweeper/images/smiley-lol.png',
}

NUM_COLORS = {
    1: QColor('#f44336'),
    2: QColor('#9C27B0'),
    3: QColor('#3F51B5'),
    4: QColor('#03A9F4'),
    5: QColor('#00BCD4'),
    6: QColor('#4CAF50'),
    7: QColor('#E91E63'),
    8: QColor('#FF9800')
}

LEVELS = {'easy': (8, 10), 'middle': (12, 30), 'hard': (16, 40)}
