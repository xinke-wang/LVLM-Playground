import random
import re
import time

from PyQt5.QtGui import QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import QMainWindow

from playground.games import BaseGame, BaseGameLogic
from playground.games.minesweeper.game_cfg import LEVELS, STATUS_ICONS
from playground.games.minesweeper.minesweeper_ui import MinesweeperUI
from playground.registry import GAME_REGISTRY
from playground.state_code import GameStatus


class MinesweeperLogic(BaseGameLogic):
    """Pure logic for Minesweeper game."""

    def __init__(self, game_cfg):
        self.game_cfg = game_cfg
        self.level = game_cfg.level
        self.b_size, self.n_mines = LEVELS[self.level]
        self.board = None
        self.status = GameStatus.IN_PROGRESS
        self.moves_history = []
        self.timer_start = 0
        self.reset_board()

    def reset_board(self):
        """Reset the game board to initial state without revealing."""
        self.board = [[-1 for _ in range(self.b_size)]
                      for _ in range(self.b_size)]
        self.status = GameStatus.IN_PROGRESS
        self.moves_history = []
        self.timer_start = int(time.time())

        mine_positions = set()
        while len(mine_positions) < self.n_mines:
            x, y = random.randint(0, self.b_size - 1), random.randint(
                0, self.b_size - 1)
            if (x, y) not in mine_positions:
                mine_positions.add((x, y))
                self.board[y][x] = 9

        for y in range(self.b_size):
            for x in range(self.b_size):
                if self.board[y][x] != 9:
                    self.board[y][x] = -1

    def _get_adjacency_n(self, x, y, mine_positions):
        """Calculate number of adjacent mines."""
        count = 0
        for xi in range(max(0, x - 1), min(self.b_size, x + 2)):
            for yi in range(max(0, y - 1), min(self.b_size, y + 2)):
                if (xi, yi) in mine_positions:
                    count += 1
        return count

    def _expand_reveal(self, x, y):
        """Reveal surrounding cells if no adjacent mines."""
        if not (0 <= x < self.b_size
                and 0 <= y < self.b_size) or self.board[y][x] >= 0:
            return
        mine_positions = {(xi, yi)
                          for yi in range(self.b_size)
                          for xi in range(self.b_size)
                          if self.board[yi][xi] in [9, 10]}
        self.board[y][x] = self._get_adjacency_n(x, y, mine_positions)
        if self.board[y][x] == 0:
            for xi in range(max(0, x - 1), min(self.b_size, x + 2)):
                for yi in range(max(0, y - 1), min(self.b_size, y + 2)):
                    self._expand_reveal(xi, yi)

    def input_move(self, move):
        """Process move in format 'A1'."""
        if self.status != GameStatus.IN_PROGRESS:
            return self.status
        pattern = re.compile(r'([a-zA-Z])([0-9]+)|([0-9]+)([a-zA-Z])')
        match = pattern.match(move)
        if not match:
            return GameStatus.INVALID_MOVE

        row, col = (match.group(1),
                    match.group(2)) if match.group(1) else (match.group(4),
                                                            match.group(3))
        row = row.lower()
        if row.isalpha():
            y = ord(row) - ord('a')
            x = int(col) - 1
        else:
            y = int(row) - 1
            x = ord(col.lower()) - ord('a')

        if not (0 <= x < self.b_size and 0 <= y < self.b_size):
            return GameStatus.INVALID_MOVE

        if 0 <= self.board[y][x] <= 8:
            return GameStatus.INVALID_MOVE

        self.moves_history.append(move)
        if self.board[y][x] == 9:
            self.board[y][x] = 10
            self.status = GameStatus.LOSE
            return self.status

        self._expand_reveal(x, y)
        self._check_win()
        return self.status

    def _check_win(self):
        """Check if only mines (10) remain unrevealed."""
        unrevealed_count = sum(row.count(-1) for row in self.board)
        if unrevealed_count == self.n_mines:
            self.status = GameStatus.WIN

    def get_game_status(self):
        return self.status

    def get_random_state(self):
        """Generate a random game state with ~50% cells revealed."""
        self.reset_board()
        game_state = [[-1 for _ in range(self.b_size)]
                      for _ in range(self.b_size)]
        total_cells = self.b_size * self.b_size
        cells_to_reveal = total_cells // 2 + 1
        positions = [(x, y) for x in range(self.b_size)
                     for y in range(self.b_size)]
        revealed_positions = random.sample(positions, cells_to_reveal)

        mine_positions = {(x, y)
                          for y in range(self.b_size)
                          for x in range(self.b_size) if self.board[y][x] == 9}
        for y in range(self.b_size):
            for x in range(self.b_size):
                if (x, y) in revealed_positions:
                    if self.board[y][x] == 9:
                        game_state[y][x] = 9
                    else:
                        game_state[y][x] = self._get_adjacency_n(
                            x, y, mine_positions)
                else:
                    game_state[y][x] = -1
        return game_state

    def get_rule_state(self):
        """Generate a rule state with valid movements."""
        game_state = self.get_random_state()
        valid_movements = []
        for y in range(self.b_size):
            for x in range(self.b_size):
                if game_state[y][x] == -1:
                    pos_str = f"{chr(y + ord('A'))}{x + 1}"
                    valid_movements.append(pos_str)
        return game_state, valid_movements

    def calculate_score(self):
        """Calculate score based on steps, revealed cells, and game outcome."""
        step_score = len(self.moves_history) * 10
        reveal_bonus = sum(1 for y in range(self.b_size)
                           for x in range(self.b_size)
                           if 0 <= self.board[y][x] <= 8) * 2
        outcome_bonus = 1000 if self.status == GameStatus.WIN else 0
        total_score = step_score + reveal_bonus + outcome_bonus
        return total_score

    def parse_e2e(self, lmm_output):
        """Parse e2e output to a move."""
        match = re.search(r'Movement:\s*([A-Ha-h][1-8]|[1-8][A-Ha-h])',
                          lmm_output, re.IGNORECASE)
        if match:
            move = match.group(1).upper()
            if move[0].isdigit():
                move = move[1] + move[0]
            return move
        return GameStatus.INVALID_MOVE


class MinesweeperRenderer(QMainWindow):
    """Renderer for Minesweeper UI."""

    def __init__(self, logic):
        super().__init__()
        self.logic = logic
        self.ui = MinesweeperUI(self, self.logic.b_size)
        self.setCentralWidget(self.ui.centralwidget)
        self._update_ui_from_logic()
        self.adjust_window_size()
        self.show()

    def adjust_window_size(self):
        window_width = 50 + self.logic.b_size * 20
        window_height = 100 + self.logic.b_size * 20
        self.setFixedSize(window_width, window_height)

    def _update_ui_from_logic(self):
        """Sync UI with logic state."""
        self.ui.minesLabel.setText(f'{self.logic.n_mines:03d}')
        elapsed = int(
            time.time()
        ) - self.logic.timer_start if self.logic.status == GameStatus.IN_PROGRESS else 0  # noqa
        self.ui.clockLabel.setText(f'{elapsed:03d}')
        self.ui.statusButton.setIcon(QIcon(STATUS_ICONS[self.logic.status]))
        for y in range(self.logic.b_size):
            for x in range(self.logic.b_size):
                widget = self.ui.gameGrid.itemAtPosition(y + 1, x + 1).widget()
                widget.is_mine = (self.logic.board[y][x] in [9, 10])
                widget.is_revealed = (self.logic.board[y][x] >= 0
                                      and self.logic.board[y][x] != 9
                                      ) or self.logic.board[y][x] == 10
                widget.adjacent_n = self.logic.board[y][
                    x] if widget.is_revealed and not widget.is_mine else 0
                widget.update()

    def get_screenshot(self):
        """Generate screenshot of the entire window."""
        self._update_ui_from_logic()
        window_width = self.width()
        window_height = self.height()
        screenshot = QPixmap(window_width, window_height)
        painter = QPainter(screenshot)
        painter.setRenderHint(QPainter.Antialiasing)
        self.render(painter)
        painter.end()
        return screenshot


@GAME_REGISTRY.register('minesweeper')
class MineSweeper(BaseGame):
    AI_component = False

    def __init__(self, game_cfg):
        super().__init__(game_cfg)
        self.logic = MinesweeperLogic(game_cfg)
        self.renderer = None

    def get_screenshot(self):
        if self.renderer is None:
            self.renderer = MinesweeperRenderer(self.logic)
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
