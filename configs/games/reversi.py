from playground.games import ReversiQuestionAnswering

_base_ = ['configs/base.py']

game_name = 'reversi'
game_description = dict(
    e2e=(
        'Reversi (also known as Othello) is a strategy board game played on '
        'an 8x8 grid. Players take turns placing black and white pieces on '
        'the board. The goal is to have more pieces of your color on the '
        'board than your opponent by the end of the game. A valid move must '
        'sandwich one or more of the opponent\'s pieces between the newly '
        'placed piece and another of your pieces in a horizontal, vertical, '
        'or diagonal line, flipping the sandwiched pieces to your color. The '
        'game starts with four pieces in the center: two black (at D4 and E5) '
        'and two white (at D5 and E4). The black player (you) goes first, '
        'followed by the white player (AI). The grid is labeled with rows A '
        'to H (top to bottom) and columns 1 to 8 (left to right). You are '
        'playing as black, aiming to maximize your pieces by placing them '
        'strategically. Based on the board state screenshots, please first '
        'observe the current situation, then carefully think and explain your '
        'strategy briefly, and finally output your movement for this status. '
        'Please strictly follow the following format:\n'
        'Observation: <observation>\n'
        'Strategy: <strategy>\n'
        'Movement: <position>\n'
        'where the observation should briefly summarize the current '
        'situation, the strategy is a brief explanation of how you plan to '
        'maximize your pieces, and the position can be any combination of '
        'rows A to H and columns 1 to 8, for example, A1, D4, or H8.'
    ),
    perceive=(
        'Reversi (also known as Othello) is a strategy board game played on '
        'an 8x8 grid, where two players take turns placing black and white '
        'pieces on the board. The goal is to have more pieces of your color '
        'on the board than your opponent by the end of the game. A piece is '
        'placed on an empty square and must sandwich one or more of the '
        'opponent\'s pieces between the newly placed piece and another of the '
        'player\'s pieces in a horizontal, vertical, or diagonal line. The '
        'opponent\'s pieces in between are then flipped to the player\'s '
        'color. Given a screenshot of the Reversi board, please represent the '
        'current state of the game using an 8x8 matrix. In this matrix, empty '
        'cells should be represented by 0, black pieces by 1, and white '
        'pieces by 2. Please strictly follow the format:\n'
        'Game State: <boardmatrix>\n'
        'where <boardmatrix> is an 8x8 matrix. For example,\n'
        'Game State: [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], '
        '[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 2, 1, 0, 0, 0], '
        '[0, 0, 0, 1, 2, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], '
        '[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]]\n'
        'represents a Reversi board with the initial four pieces placed.'
    ),
    qa=(
        'Reversi (also known as Othello) is played on an 8x8 grid where two '
        'players take turns placing black and white pieces on the board. '
        'Please answer the following question based on the provided '
        'screenshot of the current game state:\n'
        '{question}\n'
        'Answer: <answer>\n'
        'where <answer> should be one of A, B, C, or D.'
    ),
    rule=(
        'Reversi (also known as Othello) is played on an 8x8 grid. Players '
        'take turns placing black and white pieces on the board. The grid '
        'starts with two black pieces and two white pieces in the center '
        '(D4, D5, E4, E5). A valid move consists of placing a piece in such a '
        'way that it sandwiches one or more of the opponent\'s pieces between '
        'the newly placed piece and another of the player\'s pieces in a '
        'horizontal, vertical, or diagonal line. After placing the piece, all '
        'of the opponent\'s pieces in between are flipped to the player\'s '
        'color. The black player (you) goes first, followed by the white '
        'player (AI). The grid is labeled with rows A to H and columns 1 to '
        '8. Based on the current game state, please find a valid position '
        'where you can place your next black piece and flip at least one of '
        'the opponent\'s white pieces.\n'
        'Please strictly follow the format:\n'
        'Movement: <position>\n'
        'where the position can be any combination of rows A to H and columns '
        '1 to 8, for example, A1, D4, or H8.'
    )
)

player_first = True
qa = ReversiQuestionAnswering
