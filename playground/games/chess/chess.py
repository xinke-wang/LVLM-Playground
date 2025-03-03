import random
import re

import chess
import chess.engine
from PyQt5.QtWidgets import QMainWindow

from playground.games import BaseGame, BaseGameLogic
from playground.games.chess.chess_ui import ChessUI
from playground.registry import GAME_REGISTRY
from playground.state_code import GameStatus


class ChessLogic(BaseGameLogic):
    """Pure logic for Chess game."""

    def __init__(self, game_cfg):
        self.game_cfg = game_cfg
        self.user_is_white = game_cfg.user_is_white
        self.board = chess.Board()
        self.status = GameStatus.IN_PROGRESS
        self.turn = 'white' if self.user_is_white else 'black'
        self.moves_history = []

    def make_move(self, move, is_ai=False):
        """Make a move on the board."""
        expected_turn = 'white' if self.user_is_white else 'black'
        if is_ai:
            expected_turn = 'black' if self.user_is_white else 'white'
        if self.turn != expected_turn:
            return False
        try:
            if len(move) > 2 and move[0] in 'NBRQK':
                adjusted_move = move[0] + move[1:].lower()
            else:
                adjusted_move = move.lower()
            chess_move = self.board.parse_san(adjusted_move)
            if chess_move not in self.board.legal_moves:
                return False
            self.board.push(chess_move)
            self.moves_history.append(chess_move)
            self.turn = 'black' if self.turn == 'white' else 'white'
            self._update_game_status()
            return True
        except ValueError:
            return False

    def _update_game_status(self):
        """Update game status based on current board state."""
        if self.board.is_checkmate():
            self.status = GameStatus.LOSE if self.turn == (
                'white' if self.user_is_white else 'black') else GameStatus.WIN
        elif (self.board.is_insufficient_material()
              or self.board.is_stalemate() or self.board.is_repetition(count=3)
              or self.board.halfmove_clock >= 100):
            self.status = GameStatus.TIE
        else:
            self.status = GameStatus.IN_PROGRESS

    def input_move(self, move):
        """Process player move in SAN format (e.g., 'e4')."""
        if self.status != GameStatus.IN_PROGRESS:
            return self.status
        if self.make_move(move, is_ai=False):
            return self.status
        return GameStatus.INVALID_MOVE

    def get_game_status(self):
        return self.status

    def reset_board(self):
        """Reset the board to initial state."""
        self.board = chess.Board()
        self.status = GameStatus.IN_PROGRESS
        self.turn = 'white' if self.user_is_white else 'black'
        self.moves_history = []

    def get_random_state(self):
        """Generate a random game state."""
        self.reset_board()
        num_moves = random.randint(5, 55)
        for _ in range(num_moves):
            legal_moves = list(self.board.legal_moves)
            if not legal_moves:
                break
            move = random.choice(legal_moves)
            self.board.push(move)
            self.moves_history.append(move)

        piece_to_numeric = {
            chess.PAWN: 1,
            chess.KNIGHT: 2,
            chess.BISHOP: 3,
            chess.ROOK: 4,
            chess.QUEEN: 5,
            chess.KING: 6,
            None: 0
        }
        board_matrix = [[0 for _ in range(8)] for _ in range(8)]
        for i in range(64):
            piece = self.board.piece_at(i)
            if piece:
                value = piece_to_numeric[piece.piece_type]
                if piece.color == chess.BLACK:
                    value = -value
                board_matrix[7 - (i // 8)][i % 8] = value

        self._update_game_status()
        return board_matrix

    def get_rule_state(self):
        """Generate a rule state with valid movements."""
        self.reset_board()
        num_moves = random.randint(5, 55)
        for _ in range(num_moves):
            legal_moves = list(self.board.legal_moves)
            if not legal_moves:
                break
            move = random.choice(legal_moves)
            self.board.push(move)
            self.moves_history.append(move)

        while self.board.turn != (chess.WHITE
                                  if self.user_is_white else chess.BLACK):
            legal_moves = list(self.board.legal_moves)
            if not legal_moves:
                break
            move = random.choice(legal_moves)
            self.board.push(move)
            self.moves_history.append(move)

        fen = self.board.fen()
        valid_movements = [self.board.san(m) for m in self.board.legal_moves]
        self._update_game_status()
        return fen, valid_movements

    def calculate_score(self):
        """Calculate score based on steps and captured enemy pieces."""
        white_steps = len(
            [m for i, m in enumerate(self.moves_history) if i % 2 == 0])
        step_score = white_steps * 10

        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }

        initial_black_piece_value = (8 * piece_values[chess.PAWN] +
                                     2 * piece_values[chess.KNIGHT] +
                                     2 * piece_values[chess.BISHOP] +
                                     2 * piece_values[chess.ROOK] +
                                     1 * piece_values[chess.QUEEN])

        black_piece_value = 0
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece and piece.color == chess.BLACK:
                black_piece_value += piece_values.get(piece.piece_type, 0)

        captured_black_value = initial_black_piece_value - black_piece_value
        piece_bonus = captured_black_value * 5

        outcome_bonus = 0
        if self.status == GameStatus.WIN:
            outcome_bonus = 1000
        elif self.status == GameStatus.TIE:
            outcome_bonus = 500

        total_score = step_score + piece_bonus + outcome_bonus
        return total_score

    def parse_e2e(self, lmm_output):
        """Parse e2e output to a move in SAN format."""
        match = re.search(
            r'Movement:\s*([a-hA-H][1-8][a-hA-H][1-8]|[a-hA-H][1-8]|O-O|O-O-O|(?:N|B|R|Q|K)?[a-hA-H]?[1-8]?x?[a-hA-H][1-8](?:=[QRNB])?|(?:N|B|R|Q|K)[a-hA-H][1-8])',  # noqa
            lmm_output,
            re.IGNORECASE)
        if match:
            return match.group(1)
        return GameStatus.INVALID_MOVE


class ChessRenderer(QMainWindow):
    """Renderer for Chess UI."""

    def __init__(self, logic):
        super().__init__()
        self.logic = logic
        self.ui = ChessUI(self, user_is_white=self.logic.user_is_white)
        self.setCentralWidget(self.ui)
        self.ui.position = self.logic.board
        self.ui.reset_board()

    def get_screenshot(self):
        """Generate screenshot of the current board."""
        self.ui.position = self.logic.board
        self.ui.refresh_from_state()
        screenshot = self.ui.grab()
        return screenshot


@GAME_REGISTRY.register('chess')
class Chess(BaseGame):
    AI_component = True

    def __init__(self, game_cfg):
        super().__init__(game_cfg)
        self.logic = ChessLogic(game_cfg)
        self.renderer = None
        self.engine = chess.engine.SimpleEngine.popen_uci(
            '/usr/games/stockfish')

    def __del__(self):
        """Cleanup engine resources."""
        if hasattr(self, 'engine'):
            self.engine.quit()

    def get_screenshot(self):
        if self.renderer is None:
            self.renderer = ChessRenderer(self.logic)
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
        """Calculate and apply AI move using Stockfish."""
        if not self.AI_component or self.logic.status != GameStatus.IN_PROGRESS:  # noqa
            return None

        result = self.engine.play(self.logic.board,
                                  chess.engine.Limit(time=1.0))
        chess_move = result.move
        if chess_move in self.logic.board.legal_moves:
            san_move = self.logic.board.san(chess_move)
            if self.logic.make_move(san_move, is_ai=True):
                return san_move
        return None

    def calculate_score(self):
        return self.logic.calculate_score()

    def parse_e2e(self, lmm_output):
        return self.logic.parse_e2e(lmm_output)
