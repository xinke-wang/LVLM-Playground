class Minimax:

    def __init__(self, bot, opponent):
        self.bot = bot
        self.opponent = opponent

    @staticmethod
    def generate_plugin(lst, cols):
        return [lst[i:i + cols] for i in range(0, len(lst), cols)]

    @staticmethod
    def generate_1d(row, col):
        return row * 3 + col

    def generate_2d(self, board):
        return self.generate_plugin([
            '_' if cell not in [self.bot, self.opponent] else cell
            for cell in board
        ], 3)

    @staticmethod
    def is_moves_left(board):
        return any(cell == '_' for row in board for cell in row)

    def reset(self, bot, opponent):
        self.bot = bot
        self.opponent = opponent

    def evaluate(self, board):
        for row in board:
            if row[0] == row[1] == row[2]:
                if row[0] == self.bot:
                    return 10
                elif row[0] == self.opponent:
                    return -10

        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col]:
                if board[0][col] == self.bot:
                    return 10
                elif board[0][col] == self.opponent:
                    return -10

        if board[0][0] == board[1][1] == board[2][2]:
            if board[0][0] == self.bot:
                return 10
            elif board[0][0] == self.opponent:
                return -10

        if board[0][2] == board[1][1] == board[2][0]:
            if board[0][2] == self.bot:
                return 10
            elif board[0][2] == self.opponent:
                return -10

        return 0

    def minimax(self, board, depth, is_max):
        score = self.evaluate(board)

        if score == 10 or score == -10:
            return score

        if not self.is_moves_left(board):
            return 0

        if is_max:
            best = -1000
            for i in range(3):
                for j in range(3):
                    if board[i][j] == '_':
                        board[i][j] = self.bot
                        best = max(best,
                                   self.minimax(board, depth + 1, not is_max))
                        board[i][j] = '_'
            return best
        else:
            best = 1000
            for i in range(3):
                for j in range(3):
                    if board[i][j] == '_':
                        board[i][j] = self.opponent
                        best = min(best,
                                   self.minimax(board, depth + 1, not is_max))
                        board[i][j] = '_'
            return best

    def find_best_move(self, board):
        best_val = -1000
        best_move = (-1, -1)
        for i in range(3):
            for j in range(3):
                if board[i][j] == '_':
                    board[i][j] = self.bot
                    move_val = self.minimax(board, 1, False)
                    board[i][j] = '_'
                    if move_val > best_val:
                        best_move = (i, j)
                        best_val = move_val
        return self.generate_1d(best_move[0], best_move[1])
