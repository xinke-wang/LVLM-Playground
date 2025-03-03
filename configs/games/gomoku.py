from playground.games import GomokuQuestionAnswering

_base_ = ['configs/base.py']

game_name = 'gomoku'
game_description = dict(
    e2e=(
        'Gomoku is played on a 15x15 grid, where players take turns placing '
        'black or white stones on the intersections. The goal is to be the '
        'first to form an unbroken line of five stones horizontally, '
        'vertically, or diagonally. The game starts with an empty board, and '
        'the black player (you) goes first, followed by the white player '
        '(AI). The grid is labeled with columns A to O (left to right) and '
        'rows 1 to 15 (top to bottom). You are playing as black, aiming to '
        'win by placing stones strategically. Each intersection can only be '
        'occupied by one stone, so do not choose a spot that is already '
        'taken. Based on the board state screenshots, please first observe '
        'the current situation, then carefully think and explain your '
        'strategy briefly, and finally output your movement for this status. '
        'Please strictly follow the following format:\n'
        'Observation: <observation>\n'
        'Strategy: <strategy>\n'
        'Movement: <position>\n'
        'where the observation should briefly summarize the current '
        'situation, the strategy is a brief explanation of how you plan to '
        'win the game, and the position can be any combination of columns A '
        'to O and rows 1 to 15, for example, A1, H8, or O15.'
    ),
    perceive=(
        'Gomoku is a game played on a 15x15 grid where players take turns '
        'placing black or white stones on the intersections. Given a '
        'screenshot of the Gomoku board, please determine the current game '
        'state using a 15x15 matrix. In this matrix, an empty intersection '
        'should be represented by 0, a black stone by 1, and a white stone by '
        '2. Please strictly follow the format:\n'
        'Game State: <boardmatrix>\n'
        'where <boardmatrix> is a 15x15 matrix. For example,\n'
        'Game State: [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], '
        '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], '
        '[0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0], '
        '[0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0], '
        '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], '
        '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], '
        '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], '
        '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], '
        '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], '
        '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], '
        '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], '
        '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], '
        '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], '
        '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], '
        '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]\n'
        'represents a partially filled Gomoku board.'
    ),
    qa=(
        'Gomoku is played on a 15x15 grid, where black and white stones are '
        'placed in turns. The goal is to place five consecutive stones in a '
        'horizontal, vertical, or diagonal line. Please answer the following '
        'question based on the provided screenshot of the current game '
        'state:\n'
        '{question}\n'
        'Answer: <answer>\n'
        'where <answer> should be one of A, B, C, or D.'
    ),
    rule=(
        'Gomoku is played on a 15x15 grid, where black and white stones are '
        'placed on the intersections of the grid. The objective is to place '
        'five consecutive stones in a horizontal, vertical, or diagonal line. '
        'The game starts with an empty board. The grid is labeled with '
        'columns A to O (left to right) and rows 1 to 15 (top to bottom). '
        'Each intersection can only be occupied by one stone, either black or '
        'white. Based on the board state, please find an empty intersection '
        'where you can place your next stone.\n'
        'Please strictly follow the following format:\n'
        'Movement: <position>\n'
        'where the position can be any combination of columns A to O and rows '
        '1 to 15, for example, A1, H8, or O15.'
    )
)

chessboard_size = 15
player_first = True
qa = GomokuQuestionAnswering
