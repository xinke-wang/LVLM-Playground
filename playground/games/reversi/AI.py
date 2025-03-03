import copy


class ReversiAI:

    def valid_move(self, board, x, y, player):
        if board[y][x] != 0:
            return False
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8 and board[ny][
                        nx] == self.opponent(player):
                    while 0 <= nx < 8 and 0 <= ny < 8:
                        if board[ny][nx] == player:
                            return True
                        if board[ny][nx] == 0:
                            break
                        nx += dx
                        ny += dy
        return False

    def make_move(self, board, x, y, player):
        board[y][x] = player
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8 and board[ny][
                        nx] == self.opponent(player):
                    nx += dx
                    ny += dy
                    while 0 <= nx < 8 and 0 <= ny < 8:
                        if board[ny][nx] == player:
                            while True:
                                nx -= dx
                                ny -= dy
                                if nx == x and ny == y:
                                    break
                                board[ny][nx] = player
                            break
                        if board[ny][nx] == 0:
                            break
                        nx += dx
                        ny += dy

    def opponent(self, player):
        return 1 if player == 2 else 2

    def score(self, board):
        w, b = 0, 0
        for row in board:
            for cell in row:
                if cell == 2:
                    w += 1
                elif cell == 1:
                    b += 1
        return w, b

    def best_move(self, board, depth, player):
        moves = [(x, y) for x in range(8) for y in range(8)
                 if self.valid_move(board, x, y, player)]
        if not moves:
            return None

        best = None
        if player == 2:
            max_val = -float('inf')
            for x, y in moves:
                new_board = copy.deepcopy(board)
                self.make_move(new_board, x, y, player)
                val = self.alpha_beta(new_board, depth - 1, -float('inf'),
                                      float('inf'), self.opponent(player))
                if val > max_val:
                    max_val = val
                    best = (x, y)
        else:
            min_val = float('inf')
            for x, y in moves:
                new_board = copy.deepcopy(board)
                self.make_move(new_board, x, y, player)
                val = self.alpha_beta(new_board, depth - 1, -float('inf'),
                                      float('inf'), self.opponent(player))
                if val < min_val:
                    min_val = val
                    best = (x, y)
        return best

    def alpha_beta(self, board, depth, alpha, beta, player):
        if depth == 0:
            w, b = self.score(board)
            return w - b if player == 2 else b - w

        moves = [(x, y) for x in range(8) for y in range(8)
                 if self.valid_move(board, x, y, player)]
        if not moves:
            return self.alpha_beta(board, depth - 1, alpha, beta,
                                   self.opponent(player))

        if player == 2:
            max_val = -float('inf')
            for x, y in moves:
                new_board = copy.deepcopy(board)
                self.make_move(new_board, x, y, player)
                val = self.alpha_beta(new_board, depth - 1, alpha, beta,
                                      self.opponent(player))
                max_val = max(max_val, val)
                alpha = max(alpha, val)
                if beta <= alpha:
                    break
            return max_val
        else:
            min_val = float('inf')
            for x, y in moves:
                new_board = copy.deepcopy(board)
                self.make_move(new_board, x, y, player)
                val = self.alpha_beta(new_board, depth - 1, alpha, beta,
                                      self.opponent(player))
                min_val = min(min_val, val)
                beta = min(beta, val)
                if beta <= alpha:
                    break
            return min_val
