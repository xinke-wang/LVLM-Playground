import copy
import random
import re

from PyQt5.QtGui import QColor, QPainter, QPixmap
from PyQt5.QtWidgets import QMainWindow

from playground.games import BaseGame, BaseGameLogic
from playground.games.reversi.AI import ReversiAI
from playground.games.reversi.reversi_ui import Ui_MainWindow
from playground.registry import GAME_REGISTRY
from playground.state_code import GameStatus


class ReversiLogic(BaseGameLogic):
    """Pure logic for Reversi game."""

    def __init__(self, game_cfg):
        self.game_cfg = game_cfg
        self.board = [[0 for _ in range(8)] for _ in range(8)]
        self.board[3][3], self.board[3][4], self.board[4][3], self.board[4][
            4] = 2, 1, 1, 2
        self.current_player = 1
        self.last_move = None
        self.player_steps = 0
        self.status = GameStatus.IN_PROGRESS
        self.no_move_count = 0
        self.ai = ReversiAI()

    def make_move(self, x, y):
        """Make a move on the board and flip pieces."""
        if not self.valid_move(x, y):
            return False
        self.ai.make_move(self.board, x, y, self.current_player)
        self.last_move = (x, y)
        if self.current_player == 1:
            self.player_steps += 1
        self._check_game_over()
        return True

    def valid_move(self, x, y):
        """Check if a move is valid for the current player."""
        return self.ai.valid_move(self.board, x, y, self.current_player)

    def switch_player(self):
        """Switch the current player."""
        self.current_player = self.ai.opponent(self.current_player)

    def _check_game_over(self):
        """Check if the game is over (no valid moves for both players)."""
        if not any(self.valid_move(x, y) for x in range(8) for y in range(8)):
            self.no_move_count += 1
            self.switch_player()
        else:
            self.no_move_count = 0

        if self.no_move_count >= 2:
            white_score, black_score = self.ai.score(self.board)
            if white_score > black_score:
                self.status = GameStatus.LOSE
            elif black_score > white_score:
                self.status = GameStatus.WIN
            else:
                self.status = GameStatus.TIE

    def input_move(self, move):
        """Process player move from input string (e.g., 'D4')."""
        if self.status != GameStatus.IN_PROGRESS:
            return self.status
        col_map = {
            '1': 0,
            '2': 1,
            '3': 2,
            '4': 3,
            '5': 4,
            '6': 5,
            '7': 6,
            '8': 7
        }
        row_map = {
            'A': 0,
            'B': 1,
            'C': 2,
            'D': 3,
            'E': 4,
            'F': 5,
            'G': 6,
            'H': 7
        }
        move = re.sub(r'\s+', '', move).upper()
        match = re.match(r'([A-H])([1-8])|([1-8])([A-H])', move)
        if not match:
            return GameStatus.INVALID_MOVE
        if match.group(1) and match.group(2):
            row, col = row_map[match.group(1)], col_map[match.group(2)]
        else:
            col, row = col_map[match.group(3)], row_map[match.group(4)]
        if not (0 <= row < 8 and 0 <= col < 8) or not self.valid_move(
                col, row):
            return GameStatus.INVALID_MOVE
        self.make_move(col, row)
        self.switch_player()
        return self.status

    def get_game_status(self):
        return self.status

    def reset_board(self):
        """Reset the game board."""
        self.board = [[0 for _ in range(8)] for _ in range(8)]
        self.board[3][3], self.board[3][4], self.board[4][3], self.board[4][
            4] = 2, 1, 1, 2
        self.current_player = 1
        self.last_move = None
        self.player_steps = 0
        self.status = GameStatus.IN_PROGRESS
        self.no_move_count = 0

    def get_random_state(self):
        """Generate a random game state."""
        self.reset_board()
        total_cells = 8 * 8
        stone_ranges = {
            'sparse': (10, 25),
            'mild': (26, 40),
            'dense': (41, 56)
        }
        range_choice = random.choice(list(stone_ranges.keys()))
        min_stones, max_stones = stone_ranges[range_choice]
        min_stones = max(0, min(min_stones, total_cells))
        max_stones = max(0, min(max_stones, total_cells))

        total_stones = random.randint(min_stones, max_stones)
        black_stones = random.randint(total_stones * 30 // 100,
                                      total_stones * 70 // 100)
        white_stones = total_stones - black_stones
        empty_cells = total_cells - total_stones

        pieces = [1] * black_stones + [2] * white_stones + [0] * empty_cells
        random.shuffle(pieces)

        for i in range(8):
            for j in range(8):
                self.board[i][j] = pieces[i * 8 + j]

        self._check_game_over()
        if self.status != GameStatus.IN_PROGRESS:
            return self.get_random_state()
        return self.board

    def get_rule_state(self):
        """Generate a rule state with valid movements."""
        valid_state_found = False
        valid_moves = []

        row_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        col_labels = ['1', '2', '3', '4', '5', '6', '7', '8']

        while not valid_state_found:
            board_state = self.get_random_state()
            valid_moves = []

            for x in range(8):
                for y in range(8):
                    if self.ai.valid_move(board_state, x, y, 1):
                        move_str = f'{row_labels[y]}{col_labels[x]}'
                        valid_moves.append(move_str)

            if valid_moves:
                valid_state_found = True
        return board_state, valid_moves

    def calculate_score(self):
        """Calculate score based on player's steps and remaining pieces."""
        step_score = self.player_steps * 10
        black_count = sum(1 for i in range(8) for j in range(8)
                          if self.board[i][j] == 1)
        piece_bonus = black_count * 20
        outcome_bonus = 0
        if self.status == GameStatus.WIN:
            outcome_bonus = 1000
        elif self.status == GameStatus.TIE:
            outcome_bonus = 500
        total_score = step_score + piece_bonus + outcome_bonus
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


class ReversiRenderer(QMainWindow):

    def __init__(self, logic):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.logic = logic

    def get_screenshot(self):
        board_width = 500
        board_height = 600
        screenshot = QPixmap(board_width, board_height)
        screenshot.fill(QColor(255, 255, 255))
        painter = QPainter(screenshot)
        self.render(painter)
        self.ui.draw_board(painter, self.logic.board)
        self.ui.draw_labels(painter)
        painter.end()
        return screenshot


@GAME_REGISTRY.register('reversi')
class Reversi(BaseGame):
    AI_component = True

    def __init__(self, game_cfg):
        super().__init__(game_cfg)
        self.logic = ReversiLogic(game_cfg)
        self.renderer = None

    def get_screenshot(self):
        if self.renderer is None:
            self.renderer = ReversiRenderer(self.logic)
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
        if not self.AI_component or self.logic.status != GameStatus.IN_PROGRESS:  # noqa
            return None

        best_move = self.logic.ai.best_move(copy.deepcopy(self.logic.board), 3,
                                            self.logic.current_player)
        if best_move:
            x, y = best_move
            if self.logic.make_move(x, y):
                self.logic.switch_player()
                row_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
                col_labels = ['1', '2', '3', '4', '5', '6', '7', '8']
                return f'{row_labels[y]}{col_labels[x]}'
        return None

    def calculate_score(self):
        return self.logic.calculate_score()

    def parse_e2e(self, lmm_output):
        return self.logic.parse_e2e(lmm_output)
