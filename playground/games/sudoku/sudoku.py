import copy
import re
import time

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QMainWindow

from playground.games import BaseGame, BaseGameLogic
from playground.games.sudoku import sudoku_generator
from playground.games.sudoku.sudoku_ui import SudokuUI
from playground.registry import GAME_REGISTRY
from playground.state_code import GameStatus


class SudokuLogic(BaseGameLogic):
    """Pure logic for Sudoku game."""

    def __init__(self, game_cfg):
        self.game_cfg = game_cfg
        self.b_size = 9
        self.solution = [[0 for _ in range(self.b_size)]
                         for _ in range(self.b_size)]
        self.puzzle = []
        self.assigned = [[False for _ in range(self.b_size)]
                         for _ in range(self.b_size)]
        self.status = GameStatus.IN_PROGRESS
        self.moves_history = []
        self.timer_start = int(time.time())
        self.pause_time = 0
        self.start_game()

    def start_game(self):
        """Initialize the Sudoku puzzle."""
        self.status = GameStatus.IN_PROGRESS
        solution = [[0 for _ in range(self.b_size)]
                    for _ in range(self.b_size)]
        sudoku_generator.fillGrid(solution)
        self.solution = copy.deepcopy(solution)
        self.puzzle = sudoku_generator.generate_puzzle(solution, 5)
        self.assigned = [[self.puzzle[y][x] != 0 for x in range(self.b_size)]
                         for y in range(self.b_size)]
        self.moves_history = []

    def input_move(self, move):
        """Process move in format 'A1 5' (row A, col 1, number 5)."""
        if self.status != GameStatus.IN_PROGRESS:
            return self.status

        match = re.match(r'([A-Ia-i])([1-9])\s([1-9])', move)
        if not match:
            return GameStatus.INVALID_MOVE

        row = ord(match.group(1).upper()) - ord('A')
        col = int(match.group(2)) - 1
        number = int(match.group(3))

        if not (0 <= row < self.b_size and 0 <= col < self.b_size):
            return GameStatus.INVALID_MOVE

        if self.assigned[row][col]:
            return GameStatus.INVALID_MOVE

        if self.puzzle[row][col] != 0:
            return GameStatus.INVALID_MOVE

        if not self._is_valid_move(row, col, number):
            return GameStatus.INVALID_MOVE

        self.moves_history.append(move)
        self.puzzle[row][col] = number
        self._check_win()
        return self.status

    def _is_valid_move(self, row, col, number):
        """Check if placing number at (row, col) is valid."""
        if number in self.puzzle[row]:
            return False
        if number in [self.puzzle[r][col] for r in range(self.b_size)]:
            return False
        start_row, start_col = (row // 3) * 3, (col // 3) * 3
        for y in range(start_row, start_row + 3):
            for x in range(start_col, start_col + 3):
                if self.puzzle[y][x] == number:
                    return False
        return True

    def _check_win(self):
        """Check if the puzzle is solved correctly."""
        for y in range(self.b_size):
            for x in range(self.b_size):
                if self.puzzle[y][
                        x] == 0 or self.puzzle[y][x] != self.solution[y][x]:
                    return
        self.status = GameStatus.WIN

    def get_game_status(self):
        return self.status

    def get_random_state(self):
        return copy.deepcopy(self.puzzle)

    def get_rule_state(self):
        valid_movements = []
        for y in range(self.b_size):
            for x in range(self.b_size):
                if self.puzzle[y][x] == 0:
                    candidates = set(range(1, 10))
                    for col in range(self.b_size):
                        if self.puzzle[y][col] != 0:
                            candidates.discard(self.puzzle[y][col])
                    for row in range(self.b_size):
                        if self.puzzle[row][x] != 0:
                            candidates.discard(self.puzzle[row][x])
                    start_row, start_col = (y // 3) * 3, (x // 3) * 3
                    for row in range(start_row, start_row + 3):
                        for col in range(start_col, start_col + 3):
                            if self.puzzle[row][col] != 0:
                                candidates.discard(self.puzzle[row][col])
                    for num in sorted(candidates):
                        valid_movements.append(
                            f"{chr(y + ord('A'))}{x + 1} {num}")
        return self.puzzle, valid_movements

    def calculate_score(self):
        """Calculate score based on filled numbers"""
        base_score = sum(
            1 for y in range(self.b_size) for x in range(self.b_size)
            if self.puzzle[y][x] != 0 and not self.assigned[y][x]) * 2

        correct_count = sum(
            1 for y in range(self.b_size) for x in range(self.b_size)
            if self.puzzle[y][x] != 0 and not self.assigned[y][x]
            and self.puzzle[y][x] == self.solution[y][x])
        correct_score = correct_count * 10

        outcome_bonus = 1000 if self.status == GameStatus.WIN else 0

        total_score = base_score + correct_score + outcome_bonus
        return total_score

    def parse_e2e(self, lmm_output):
        """Parse e2e output to a move."""
        match = re.search(r'Movement:\s*([A-Ia-i][1-9]\s[1-9])', lmm_output,
                          re.IGNORECASE)
        if match:
            move = match.group(1).upper()
            return move
        return GameStatus.INVALID_MOVE


class SudokuRenderer(QMainWindow):
    """Renderer for Sudoku UI."""

    def __init__(self, logic):
        super().__init__()
        self.logic = logic
        self.ui = SudokuUI(self)
        self.setCentralWidget(self.ui.centralwidget)
        self._update_ui_from_logic()
        self.adjust_window_size()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.show()

    def adjust_window_size(self):
        self.setFixedSize(550, 700)

    def _update_ui_from_logic(self):
        """Sync UI with logic state."""
        for y in range(self.logic.b_size):
            for x in range(self.logic.b_size):
                btn = self.ui.puzzle_buttons[y][x]
                if self.logic.puzzle[y][x] != 0:
                    btn.setText(str(self.logic.puzzle[y][x]))
                    if self.logic.assigned[y][x]:
                        btn.setStyleSheet(
                            'color: black; background-color: white; font-family: sans-serif; font-size: 25px; border: 1px solid black;'  # noqa
                        )
                    else:
                        btn.setStyleSheet(
                            'color: blue; background-color: white; font-family: sans-serif; font-size: 25px; border: 1px solid black;'  # noqa
                        )
                    btn.setDisabled(True)
                else:
                    btn.setText('')
                    btn.setStyleSheet(
                        'color: black; background-color: white; font-family: sans-serif; font-size: 25px; border: 1px solid black;'  # noqa
                    )
                    btn.setEnabled(True)

    def update_time(self):
        """Update the timer display."""
        elapsed_time = int(time.time() - self.logic.timer_start -
                           self.logic.pause_time)
        self.ui.show_time.setText(self.time_int_to_string(elapsed_time))

    def time_int_to_string(self, i):
        return time.strftime('%H:%M:%S', time.gmtime(i))

    def get_screenshot(self):
        """Generate screenshot of the entire window."""
        self._update_ui_from_logic()
        screenshot = QPixmap(self.width(), self.height())
        painter = QPainter(screenshot)
        painter.setRenderHint(QPainter.Antialiasing)
        self.render(painter)
        painter.end()
        return screenshot


@GAME_REGISTRY.register('sudoku')
class Sudoku(BaseGame):
    AI_component = False

    def __init__(self, game_cfg):
        super().__init__(game_cfg)
        self.logic = SudokuLogic(game_cfg)
        self.renderer = None

    def get_screenshot(self):
        if self.renderer is None:
            self.renderer = SudokuRenderer(self.logic)
        return self.renderer.get_screenshot()

    def input_move(self, move):
        return self.logic.input_move(move)

    def get_game_status(self):
        return self.logic.get_game_status()

    def get_random_state(self):
        return self.logic.get_random_state()

    def get_rule_state(self):
        return self.logic.get_rule_state()

    def ai_move(self):
        return None

    def calculate_score(self):
        return self.logic.calculate_score()

    def parse_e2e(self, lmm_output):
        return self.logic.parse_e2e(lmm_output)
