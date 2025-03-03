from playground.games import SudokuQuestionAnswering

_base_ = ['configs/base.py']

game_name = 'sudoku'
game_description = dict(
    e2e=(
        'Sudoku is a logic-based puzzle played on a 9x9 grid, subdivided into '
        'nine 3x3 subgrids. The goal is to fill the grid so that each row, '
        'column, and 3x3 subgrid contains all digits from 1 to 9 without '
        'repetition. The grid starts with some cells filled with numbers '
        '(clues), and you must fill in the remaining empty cells one at a '
        'time. Rows are labeled A to I (top to bottom), and columns are '
        'numbered 1 to 9 (left to right). Each move involves placing a digit '
        '(1-9) in an empty cell, ensuring no repetition in its row, column, '
        'or 3x3 subgrid. Based on the current board state screenshot, observe '
        'the situation, formulate a strategy, and output a single valid move '
        'to place a digit.\nPlease strictly follow the format:\n'
        'Observation: <observation>\n'
        'Strategy: <strategy>\n'
        'Movement: <row><column> <digit>\n'
        'where <row> is A to I, <column> is 1 to 9, and <digit> is 1 to 9. '
        'For example, "A1 5" places 5 in the top-left cell.'
    ),
    perceive=(
        'Sudoku is a logic-based puzzle played on a 9x9 grid, where the grid '
        'is subdivided into nine 3x3 subgrids. The goal is to fill the grid '
        'so that each row, each column, and each 3x3 subgrid contains all '
        'digits from 1 to 9 without repetition. Given a screenshot of the '
        'Sudoku grid, please represent the current state of the puzzle using '
        'a 9x9 matrix. In this matrix, an empty cell should be represented by '
        '0, and filled cells should contain their respective numbers (1-9). '
        'Please strictly follow the format:\n'
        'Game State: <boardmatrix>\n'
        'where <boardmatrix> is a 9x9 matrix. For example,\n'
        'Game State: [[5, 3, 0, 0, 7, 0, 0, 0, 0], '
        '[6, 0, 0, 1, 9, 5, 0, 0, 0], [0, 9, 8, 0, 0, 0, 0, 6, 0], '
        '[8, 0, 0, 0, 6, 0, 0, 0, 3], [4, 0, 0, 8, 0, 3, 0, 0, 1], '
        '[7, 0, 0, 0, 2, 0, 0, 0, 6], [0, 6, 0, 0, 0, 0, 2, 8, 0], '
        '[0, 0, 0, 4, 1, 9, 0, 0, 5], [0, 0, 0, 0, 8, 0, 0, 7, 9]]\n'
        'represents a partially filled Sudoku grid with some cells empty '
        '(represented by 0).'
    ),
    qa=(
        'Sudoku is played on a 9x9 grid, where each row, column, and 3x3 '
        'subgrid must contain the numbers 1 to 9 exactly once. Please answer '
        'the following question based on the provided screenshot of the '
        'current game state:\n'
        '{question}\n'
        'Answer: <answer>\n'
        'where <answer> should be one of A, B, C, or D.'
    ),
    rule=(
        'Sudoku is played on a 9x9 grid, where each row, column, and 3x3 '
        'subgrid must contain the numbers 1 to 9 exactly once. The grid '
        'starts with the top-left corner as A1, where rows are labeled from '
        'A to I and columns are numbered from 1 to 9. A valid move involves '
        'placing a digit from 1 to 9 in an empty cell, ensuring that the '
        'number does not already appear in the same row, column, or 3x3 '
        'subgrid. Based on the current state of the Sudoku grid, please find '
        'a valid empty cell where you can place a digit and make a valid '
        'move.\nPlease strictly follow the format:\n'
        'Movement: <row><column> <digit>\n'
        'where <row> is A to I (representing rows), <column> is 1 to 9 '
        '(representing columns), and <digit> is a number between 1 to 9. For '
        'example, A1 5 means placing the digit 5 in the top-left corner of '
        'the grid.'
    )
)

player_first = True
qa = SudokuQuestionAnswering
