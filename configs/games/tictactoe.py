from playground.games import TicTacToeQuestionAnswering

_base_ = ['configs/base.py']

game_name = 'tictactoe'
game_description = dict(
    e2e=('Tic Tac Toe is played on a 3x3 grid. Players take turns placing X '
         'or O in the cells. The goal is to be the first to form an unbroken '
         'line of three marks horizontally, vertically, or diagonally. The '
         'game starts with an empty board, and the O player goes first. The '
         'grid is labeled with rows A to C and columns 1 to 3. You are '
         'playing as O, aiming to win by placing marks strategically. Each '
         'position can only be occupied by one mark, so do not choose a spot '
         'that is already taken. Based on the board state screenshots, please '
         'first observe the current situation, then carefully think and '
         'explain your strategy briefly, and finally output your movement for '
         'this status. Please strictly follow the following format:\n'
         'Observation: <observation>\n'
         'Strategy: <strategy>\n'
         'Movement: <position>\n'
         'where the observation should briefly summarize the current '
         'situation, the strategy is a brief explanation of how you plan to '
         'win the game, and the position can be any combination of rows A to '
         'C and columns 1 to 3, for example, A1, 2B, or c3.'),
    perceive=(
        'Tic Tac Toe is a game played on a 3x3 grid where players take turns '
        'placing X or O in the cells. Given a screenshot of the game board, '
        'please determine the current game state using a 3x3 matrix. In this '
        'matrix, an empty cell should be represented by -1, X should be '
        'represented by 1, and O should be represented by 0. Please strictly '
        'follow the format:\n'
        'Game State: <boardmatrix>\n'
        'where <boardmatrix> is a 3x3 matrix. For example,\n'
        'Game State: [[-1, -1, -1], [-1, -1, -1], [-1, -1, -1]]\n'
        'represents an empty board.'),
    rule=(
        'Tic Tac Toe is played on a 3x3 grid. Players take turns placing X or '
        'O in the cells. The game starts with an empty board. The grid is '
        'labeled with rows A to C and columns 1 to 3. Each position can only '
        'be occupied by one mark. Based on the board state, '
        'please find an empty cell where you can place your next stone.\n'
        'Please strictly follow the following format:\n'
        'Movement: <position>\n'
        'where the position can be any combination of rows A to C and columns '
        '1 to 3, for example, A1, B2, or C3.'
    ),
    qa=(
        'Tic Tac Toe is a game played on a 3x3 grid where two players take '
        'turns placing X or O in the cells. The goal is to form a horizontal, '
        'vertical, or diagonal line with three of your own marks. The grid is '
        'labeled with rows A to C and columns 1 to 3. Please answer the '
        'following question based on the provided screenshot of the current '
        'game state:\n'
        '{question}\n'
        'Answer: <answer>\n'
        'where <answer> should be one of A, B, C, or D.'
    )
)

player_first = True
qa = TicTacToeQuestionAnswering
