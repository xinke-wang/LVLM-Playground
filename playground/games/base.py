from playground.state_code import GameStatus


class BaseGame:
    AI_component = False

    def __init__(self, game_cfg) -> None:
        self.status = GameStatus.IN_PROGRESS
        self.game_cfg = game_cfg

    def get_screenshot(self):
        raise NotImplementedError

    def input_move(self, move):
        raise NotImplementedError

    def get_game_status(self):
        raise NotImplementedError

    def get_random_state(self):
        raise NotImplementedError

    def get_rule_state(self):
        raise NotImplementedError

    def calculate_score(self):
        """Calculate score based on current game state."""
        raise NotImplementedError


class BaseGameLogic:

    def parse_e2e(self, lmm_output):
        """Parse e2e output to a move."""
        raise NotImplementedError('Subclasses must implement parse_e2e')
