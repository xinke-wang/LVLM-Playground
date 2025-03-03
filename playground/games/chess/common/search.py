import copy
import math
import time

from playground.games.chess.common.consts import (ALL, CAPTURES, CASTLING, DRAW,
                                              EVASIONS, EXACT, INFINITY, KING,
                                              LOWER, MATE, MATERIAL, MIDGAME,
                                              PAWN, PROMOTION, QUIETS, UPPER,
                                              TTEntry)
from playground.games.chess.common.evaluate import Evaluate


class SearchStoppedException(Exception):
    pass


class Search:

    def __init__(self, position):
        self.position = position

        # Initialise transposition table
        self.TT_SIZE = 2**16
        self.tt = [None] * self.TT_SIZE

        # Used for move ordering with the killer heuristic
        # Indexed by ply and colour
        self.killers = [[None for _ in range(2)] for _ in range(50)]

        # Used for move ordering with the history heuristic
        # Indexed by colour, start square, and end square
        self.history = [[[0 for _ in range(64)] for _ in range(64)]
                        for _ in range(2)]

        # Keeps track of node count during the search
        self.node_count = 0

        # Keeps track of time during the search
        self.start_time = None
        self.time_limit = None

        self.eval = Evaluate()

    def search_moves(self, gen_type, hash_move=None, killers=None):
        # Search hash move first
        if hash_move and self.position.is_pseudo_legal(
                hash_move) and self.position.is_legal(hash_move):
            yield hash_move

        # Use specialised check evasion generator
        if gen_type == EVASIONS:
            evasions = self.position.get_check_evasions(self.position.colour)
            for move in evasions:
                yield move

        # Search captures before quiet moves
        if gen_type == CAPTURES or gen_type == ALL:
            captures = self.position.get_pseudo_legal_moves(CAPTURES)

            # Order captures by MVV/LVA
            captures = sorted(
                captures,
                key=lambda x:
                (-(MATERIAL[((x >> 12) & 0x3) + 2][MIDGAME] + MATERIAL[
                    self.position.squares[x & 0x3F] & 7][MIDGAME]) if x &
                 (0x3 << 14) == PROMOTION else -MATERIAL[self.position.squares[
                     x & 0x3F] & 7][MIDGAME], MATERIAL[self.position.squares[
                         (x >> 6) & 0x3F] & 7][MIDGAME]))
            # Return legal captures
            for move in captures:
                if self.position.is_legal(move):
                    yield move

        # Search killer moves next
        if killers:
            killer1 = killers[0]
            if killer1:
                if killer1 != hash_move and self.position.is_pseudo_legal(
                        killer1) and self.position.is_legal(killer1):
                    yield killer1

                killer2 = killers[1]
                if killer2:
                    if killer2 != hash_move and self.position.is_pseudo_legal(
                            killer2) and self.position.is_legal(killer2):
                        yield killer2

        # Search quiet moves last
        if gen_type == QUIETS or gen_type == ALL:
            quiets = self.position.get_pseudo_legal_moves(QUIETS)

            # Order quiet moves by history heuristic
            quiets = sorted(quiets,
                            key=lambda x: -self.history[self.position.colour][
                                (x >> 6) & 0x3F][x & 0x3F])

            # Return legal quiet moves
            for move in quiets:
                if self.position.is_legal(move):
                    yield move

    def tt_store(self, index, zobrist, move, depth, score, type_):
        self.tt[index] = TTEntry(zobrist, move, depth, score, type_)

    # Main search algorithm (Principal Variation Search)
    def pvs(self, alpha, beta, depth, ply=0):
        self.node_count += 1

        is_pv_node = True if alpha != beta - 1 else False

        # Clear killer moves for child nodes as a new sibling node is entered
        self.killers[ply + 1][0] = None
        self.killers[ply + 1][1] = None

        # Check for threefold repetition
        rep_count = 0
        for zobrist in self.position.repetition_stack[
                -self.position.halfmove_clock - 1:]:
            if zobrist == self.position.zobrist:
                rep_count += 1
        if rep_count >= 2:
            return DRAW

        # Check for fifty-move rule
        if self.position.halfmove_clock >= 100:
            return DRAW

        hash_move = None

        tt_index = self.position.zobrist & 0xFFFF
        tt_entry = self.tt[tt_index]

        if tt_entry and tt_entry.zobrist == self.position.zobrist:
            hash_move = tt_entry.move
            if tt_entry.depth >= depth:
                entry_type = tt_entry.type
                entry_score = tt_entry.score
                if entry_type == LOWER and entry_score >= beta:
                    return entry_score
                if entry_type == UPPER and entry_score <= alpha:
                    return entry_score
                if entry_type == EXACT:
                    return entry_score

        if depth <= 0:
            return self.quiescence(alpha, beta, depth, ply)

        # Check if the time limit is exceeded every 1024 nodes
        if self.node_count & 1024:
            if time.time() - self.start_time > self.time_limit:
                raise SearchStoppedException

        if (self.position.player_occ[self.position.colour]
                & ~self.position.piece_bb[(self.position.colour << 3) | KING]
                & ~self.position.piece_bb[(self.position.colour << 3) | PAWN]):
            is_endgame = False
        else:
            is_endgame = True

        in_check = True if self.position.is_in_check() else False

        # Null move pruning
        if not in_check and not is_endgame and not is_pv_node \
            and self.position.undo_info[
                -1]['move']:
            depth_reduction = 2
            self.position.make_null_move()
            null_score = -self.pvs(-beta, -beta + 1,
                                   depth - depth_reduction - 1, ply + 1)
            self.position.undo_null_move()

            if null_score >= beta:
                return null_score
            if null_score <= -MATE:  # Mate threat extension
                depth += 1

        best_score = -INFINITY
        old_alpha = alpha
        move_count = 0

        if in_check:
            moves = self.search_moves(EVASIONS, hash_move)
        else:
            moves = self.search_moves(ALL, hash_move, self.killers[ply][:])

        for move in moves:
            move_count += 1

            is_capture = True if (
                1 << (move & 0x3F)) & self.position.occupancy else False

            self.position.make_move(move)

            if move_count == 1:
                # Search first move (PV-move) with full window
                score = -self.pvs(-beta, -alpha, depth - 1, ply + 1)
            else:
                # Late move reductions
                if (move_count > 3 and not in_check and not is_capture
                        and not is_endgame
                        and not self.position.gives_check(move)
                        and move & (0x3 << 14) != PROMOTION
                        and move & (0x3 << 14) != CASTLING):
                    depth_reduction = 1
                    score = -self.pvs(-alpha - 1, -alpha,
                                      depth - depth_reduction - 1, ply + 1)
                else:
                    score = alpha + 1

                if score > alpha:
                    # Search non-PV moves with null window
                    score = -self.pvs(-alpha - 1, -alpha, depth - 1, ply + 1)
                    if alpha < score < beta:
                        # Re-search with full window if better move found
                        score = -self.pvs(-beta, -alpha, depth - 1, ply + 1)

            self.position.undo_move()

            if score > best_score:
                if score > alpha:
                    if score >= beta:
                        if not is_capture and move & (0x3 << 14) != PROMOTION:
                            # Store killer move
                            if move != self.killers[ply][0]:
                                self.killers[ply][1] = self.killers[ply][0]
                                self.killers[ply][0] = move
                            # Increase score of move in history table
                            self.history[self.position.colour][
                                (move >> 6) & 0x3F][move
                                                    & 0x3F] += depth * depth
                        self.tt_store(tt_index, self.position.zobrist, move,
                                      depth, score, LOWER)
                        return score
                    alpha = score
                    best_move = move
                best_score = score

        if move_count == 0:
            if in_check:
                return -MATE - depth  # Checkmate
            else:
                return DRAW  # Stalemate

        if best_score <= old_alpha:
            self.tt_store(tt_index, self.position.zobrist, None, depth,
                          best_score, UPPER)
        else:
            self.tt_store(tt_index, self.position.zobrist, best_move, depth,
                          best_score, EXACT)

        return best_score

    def quiescence(self, alpha, beta, depth, ply):
        self.node_count += 1

        # Fifty-move rule
        if self.position.halfmove_clock >= 100:
            return DRAW

        if self.position.is_in_check():
            moves = self.search_moves(EVASIONS)
            best_score = -INFINITY
            in_check = True
        else:
            moves = self.search_moves(CAPTURES)
            in_check = False

            # Static evaluation
            static_eval = self.eval.evaluate(self.position)
            if static_eval > alpha:
                if static_eval >= beta:
                    return static_eval
                alpha = static_eval
            best_score = static_eval

        move_count = 0

        for move in moves:
            move_count += 1

            # SEE pruning when not in check
            if not in_check and self.position.see(
                (move >> 6) & 0x3F, move & 0x3F) < 0:  # noqa
                continue

            self.position.make_move(move)
            if move_count == 1:
                score = -self.quiescence(-beta, -alpha, depth - 1, ply + 1)
            else:
                score = -self.quiescence(-alpha - 1, -alpha, depth - 1,
                                         ply + 1)
                if alpha < score < beta:
                    score = -self.quiescence(-beta, -alpha, depth - 1, ply + 1)
            self.position.undo_move()

            if score > best_score:
                if score > alpha:
                    if score >= beta:
                        return score
                    alpha = score
                best_score = score

        if in_check and move_count == 0:
            return -MATE - depth  # Checkmate

        return best_score

    # Wrap search algorithm in iterative deepening structure
    def iter_search(self, max_depth=math.inf, time_limit=math.inf):
        self.node_count = 0
        self.start_time = time.time()
        self.time_limit = time_limit
        depth = 0

        # Clear killer moves
        for ply in self.killers:
            ply[0] = None
            ply[1] = None

        while depth < max_depth and time.time(
        ) - self.start_time < self.time_limit:
            depth += 1

            current_pos = copy.deepcopy(self.position)
            try:
                self.pvs(-INFINITY, INFINITY, depth)
            except SearchStoppedException:  # Time expired
                self.position = current_pos
                break

            # Retrieve best move from transposition table
            tt_entry = self.tt[self.position.zobrist & 0xFFFF]
            if tt_entry:
                if tt_entry.zobrist == self.position.zobrist:
                    tt_move = tt_entry.move
                    tt_depth = tt_entry.depth
                    tt_score = tt_entry.score
                else:
                    raise Exception(
                        'Transposition table entry does not match current')
            else:
                raise Exception(
                    'No transposition table entry for current position')

        print('{} found move {} with depth {}, score of {}'.format(
            'Black' if self.position.colour else 'White',
            self.position.move_to_san(tt_move), tt_depth, tt_score))
        print('Searched {} nodes'.format(self.node_count))
        print('Time taken: {:0.2f}s'.format(time.time() - self.start_time))
        print()

        return tt_move

    # Perft function used for debugging
    def perft(self, depth):
        node_count = 0

        if depth == 0:
            return 1

        if self.position.is_in_check():
            in_check = True
            moves = self.position.get_check_evasions(self.position.colour)
        else:
            in_check = False
            moves = self.position.get_pseudo_legal_moves()

        for move in moves:
            if not in_check:
                if not self.position.is_legal(move):
                    continue

            self.position.make_move(move)
            child_nodes = self.perft(depth - 1)
            node_count += child_nodes
            self.position.undo_move()

        return node_count
