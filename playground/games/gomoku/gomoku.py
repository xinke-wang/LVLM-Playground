import random
import re
from copy import deepcopy

from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QLabel, QMainWindow

from playground.games import BaseGame, BaseGameLogic
from playground.games.gomoku.AI import AI
from playground.games.gomoku.gomoku_ui import Ui_MainWindow
from playground.registry import GAME_REGISTRY
from playground.state_code import GameStatus


class GomokuLogic(BaseGameLogic):
    """Pure logic for Gomoku game."""

    def __init__(self, game_cfg):
        self.game_cfg = game_cfg
        self.size = game_cfg.chessboard_size
        self.board = [[[40 + j * 64, 40 + i * 64, 0] for j in range(self.size)]
                      for i in range(self.size)]
        self.status = GameStatus.IN_PROGRESS

    def make_move(self, row, col, player):
        """Make a move on the board and check game status."""
        if not (0 <= row < self.size and 0 <= col < self.size) or self.board[
                row][col][2] != 0 or self.status != GameStatus.IN_PROGRESS:
            return False
        self.board[row][col][2] = player
        self._judge(row, col)
        return True

    def _judge(self, row, col):
        """Check if the move leads to a win or tie."""
        directions = [(-1, 0), (1, 0), (-1, 1), (1, -1), (0, 1), (0, -1),
                      (1, 1), (-1, -1)]
        player = self.board[row][col][2]
        for dx, dy in directions:
            count = 1
            for step in range(1, 5):
                x, y = row + step * dx, col + step * dy
                if not (0 <= x < self.size and
                        0 <= y < self.size) or self.board[x][y][2] != player:
                    break
                count += 1
            for step in range(1, 5):
                x, y = row - step * dx, col - step * dy
                if not (0 <= x < self.size and
                        0 <= y < self.size) or self.board[x][y][2] != player:
                    break
                count += 1
            if count >= 5:
                self.status = GameStatus.WIN if player == 1 else GameStatus.LOSE  # noqa
                return
        if all(self.board[i][j][2] != 0 for i in range(self.size)
               for j in range(self.size)):
            self.status = GameStatus.TIE

    def input_move(self, move):
        """Process player move from input string (e.g., 'H11')."""
        if self.status != GameStatus.IN_PROGRESS:
            return self.status
        row_dict = {chr(65 + i): i for i in range(15)}  # A=0, B=1, ..., O=14
        move = re.sub(r'\s+', '', move).upper()
        match = re.match(r'([A-O])([0-9]{1,2})|([0-9]{1,2})([A-O])', move)
        if not match:
            return GameStatus.INVALID_MOVE
        if match.group(1) and match.group(2):
            row, col = row_dict[match.group(1)], int(match.group(2))
        else:
            col, row = int(match.group(3)), row_dict[match.group(4)]
        if not (0 <= row < self.size
                and 0 <= col < self.size) or self.board[row][col][2] != 0:
            return GameStatus.INVALID_MOVE
        self.make_move(row, col, 1)  # Player is black (1)
        return self.status

    def get_game_status(self):
        return self.status

    def reset_board(self):
        """Reset the game board."""
        self.board = [[[40 + j * 64, 40 + i * 64, 0] for j in range(self.size)]
                      for i in range(self.size)]
        self.status = GameStatus.IN_PROGRESS

    def get_random_state(self):
        """Generate a random game state."""
        self.reset_board()
        total_cells = self.size * self.size
        total_stones = random.randint(total_cells * 30 // 100,
                                      total_cells * 70 // 100)
        black_stones = random.randint(total_stones * 30 // 100,
                                      total_stones * 70 // 100)
        white_stones = total_stones - black_stones
        pieces = [1] * black_stones + [2] * white_stones + [0] * (total_cells -
                                                                  total_stones)
        random.shuffle(pieces)
        for i in range(self.size):
            for j in range(self.size):
                self.board[i][j][2] = pieces[i * self.size + j]
        return [[self.board[i][j][2] for j in range(self.size)]
                for i in range(self.size)]

    def get_rule_state(self):
        """Generate a rule state with valid movements."""
        game_state = self.get_random_state()
        directions = [(-1, 0), (1, 0), (-1, 1), (1, -1), (0, 1), (0, -1),
                      (1, 1), (-1, -1)]

        def count_consecutive(x, y, dx, dy):
            count = 1
            stone = self.board[x][y][2]
            for step in range(1, 5):
                nx, ny = x + step * dx, y + step * dy
                if not (0 <= nx < self.size and
                        0 <= ny < self.size) or self.board[nx][ny][2] != stone:
                    break
                count += 1
            return count

        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j][2] != 0:
                    for dx, dy in directions:
                        count = count_consecutive(i, j, dx, dy)
                        if count >= 5:
                            rand_idx = random.randint(0, count - 1)
                            x, y = i + rand_idx * dx, j + rand_idx * dy
                            self.board[x][y][2] = 0
                            game_state[x][y] = 0

        valid_movement = []
        letters = 'ABCDEFGHIJKLMNO'
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col][2] == 0:
                    valid_movement.append(f'{letters[row]}{col + 1}')
        return game_state, valid_movement

    def calculate_score(self):
        """Calculate score based on player's steps and game outcome."""
        player_steps = sum(1 for i in range(self.size)
                           for j in range(self.size)
                           if self.board[i][j][2] == 1)
        base_score = player_steps * 10
        bonus_score = 0
        if self.status == GameStatus.WIN:
            bonus_score = 1000
        elif self.status == GameStatus.TIE:
            bonus_score = 500
        return base_score + bonus_score

    def parse_e2e(self, lmm_output):
        """Parse e2e output to a move."""
        match = re.search(
            r'Movement:\s*([A-Oa-o](?:[1-9]|1[0-5])|(?:[1-9]|1[0-5])[A-Oa-o])',
            lmm_output, re.IGNORECASE)
        if match:
            move = match.group(1).upper()
            if move[0].isdigit():
                move = move[1:] + move[0]  # Convert "8H" to "H8"
            return move
        return GameStatus.INVALID_MOVE


class GomokuRenderer(QMainWindow):
    """Renderer for Gomoku UI."""

    def __init__(self, logic):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.logic = logic
        self.black = QPixmap(
            'playground/games/gomoku/designer/image/black.png')
        self.white = QPixmap(
            'playground/games/gomoku/designer/image/white.png')
        self.pieces = [
            QLabel(self) for _ in range(self.logic.size * self.logic.size)
        ]
        for piece in self.pieces:
            piece.setVisible(True)
            piece.setScaledContents(True)
        self._update_ui()

    def _update_ui(self):
        """Update UI based on current game state."""
        step = 0
        for i in range(self.logic.size):
            for j in range(self.logic.size):
                state = self.logic.board[i][j][2]
                if state == 1:
                    self.pieces[step].setPixmap(self.black)
                    self.pieces[step].setGeometry(
                        self.logic.board[i][j][0] - 16,
                        self.logic.board[i][j][1] - 16, 64, 64)
                    step += 1
                elif state == 2:
                    self.pieces[step].setPixmap(self.white)
                    self.pieces[step].setGeometry(
                        self.logic.board[i][j][0] - 16,
                        self.logic.board[i][j][1] - 16, 64, 64)
                    step += 1

    def get_screenshot(self):
        """Generate screenshot of the current board."""
        board_width = 1000
        board_height = 1000
        screenshot = QPixmap(board_width, board_height)
        painter = QPainter(screenshot)
        self.render(painter)
        painter.end()
        return screenshot


@GAME_REGISTRY.register('gomoku')
class Gomoku(BaseGame):
    AI_component = True

    def __init__(self, game_cfg):
        super().__init__(game_cfg)
        self.logic = GomokuLogic(game_cfg)
        self.renderer = None

    def get_screenshot(self):
        if self.renderer is None:
            self.renderer = GomokuRenderer(self.logic)
        self.renderer._update_ui()
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
        """Calculate and apply AI move synchronously."""
        if not self.AI_component or self.logic.status != GameStatus.IN_PROGRESS:  # noqa
            return None

        board_copy = deepcopy(self.logic.board)
        ai = AI(board_copy)
        values = -100000000
        best_move = [-1, -1, 2]  # [row, col, player]

        for i in range(self.logic.size):
            for j in range(self.logic.size):
                if board_copy[i][j][2] == 0:
                    if ai.judge_empty(i, j):
                        continue
                    board_copy[i][j][2] = 2
                    evaluate = ai.ai(1, 1, values)
                    if evaluate >= values:
                        values = evaluate
                        best_move = [i, j, 2]
                    board_copy[i][j][2] = 0

        if best_move[0] != -1 and best_move[1] != -1:
            row, col, player = best_move
            if self.logic.make_move(row, col, player):
                letters = 'ABCDEFGHIJKLMNO'
                return f'{letters[row]}{col + 1}'
        return None

    def calculate_score(self):
        return self.logic.calculate_score()

    def parse_e2e(self, lmm_output):
        return self.logic.parse_e2e(lmm_output)
