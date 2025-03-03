from playground.games import MinesweeperQuestionAnswering

_base_ = ['configs/base.py']

game_name = 'minesweeper'
game_description = dict(
    e2e=(
        'Minesweeper is a logic-based puzzle game played on an 8x8 grid with '
        'exactly 10 mines. Each cell can either contain a mine, be '
        'unrevealed, or show the number of adjacent mines (from 0 to 8). The '
        'goal is to reveal all cells that do not contain mines without '
        'triggering any mines. You win when only the 10 mine cells remain '
        'unrevealed. The grid is labeled with rows A to H (top to bottom) '
        'and columns 1 to 8 (left to right). You can only reveal cells (e.g., '
        '"A1"), and flagging is not allowed. Based on the current board state '
        'screenshot, please observe the situation, formulate a strategy, and '
        'output a move to reveal a cell. Please strictly follow the format:\n'
        'Observation: <observation>\n'
        'Strategy: <strategy>\n'
        'Movement: <position>\n'
        'where <observation> summarizes the current board state, '
        '<strategy> explains your reasoning, and <position> is a move in the '
        'format "A1".'
    ),
    perceive=(
        'Minesweeper is a logic-based puzzle game played on an 8x8 grid with '
        'exactly 10 mines. Each cell can either contain a mine (represented '
        'by 9), or it can be empty. Unrevealed cells should be represented by '
        '-1. Cells that are revealed and contain no adjacent mines are '
        'represented by 0, while cells that are revealed and show a number '
        'from 1 to 8 indicate how many adjacent mines surround the cell. '
        'Mines are represented by the number 9.\nPlease strictly follow the '
        'format:\n'
        'Game State: <boardmatrix>\n'
        'where <boardmatrix> is an 8x8 matrix representing the game grid, '
        'with unrevealed cells as -1, mines as 9, and numbers from 0 to 8 '
        'indicating the number of adjacent mines. For example,\n'
        'Game State: [[-1, 1, 1, 2, -1, -1, -1, 1], '
        '[1, 2, 3, 2, -1, 1, 1, 2], '
        '[2, 3, 4, 3, 1, 1, 1, 2], '
        '[1, 2, 2, 2, 2, 2, 2, 1], '
        '[1, 2, 2, 2, 2, 9, 1, 0], '
        '[-1, 1, 2, 3, 2, 1, 0, -1], '
        '[-1, -1, 1, 2, 3, 1, -1, -1], '
        '[1, 2, 9, 1, 1, -1, -1, -1]]\n'
        'This example represents a grid where some cells have been uncovered, '
        'showing numbers indicating adjacent mines, unrevealed cells are '
        'represented by -1, and mines are represented by the number 9.'
    ),
    qa=(
        'Minesweeper is played on an 8x8 grid with exactly 10 mines. Each '
        'cell can either contain a mine, be unrevealed, or show the number of '
        'adjacent mines (from 0 to 8). The grid is labeled with rows A to H '
        '(top to bottom) and columns 1 to 8 (left to right). Please answer '
        'the following question based on the provided screenshot of the '
        'current game state:\n'
        '{question}\n'
        'Answer: <answer>\n'
        'where <answer> should be one of A, B, C, or D.'
    ),
    rule=(
        'Minesweeper is played on an 8x8 grid with exactly 10 mines. Each '
        'cell can either contain a mine, be unrevealed, or show the number of '
        'adjacent mines (from 0 to 8). The goal is to reveal all cells that '
        'do not contain mines, without triggering any mines. You win when '
        'only the 10 mine cells remain unrevealed. The grid is labeled with '
        'rows A to H (top to bottom) and columns 1 to 8 (left to right). Each '
        'cell can only be revealed once, and flagging is not allowed. Based '
        'on the current board state image, please find a cell to reveal '
        'next.\nPlease strictly follow the following format:\n'
        'Movement: <position>\n'
        'where the position can be any combination of rows A to H and columns '
        '1 to 8, for example, A1, B5, or H8.'
    )
)

level = 'easy'
qa = MinesweeperQuestionAnswering
