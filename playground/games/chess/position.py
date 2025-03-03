from collections import deque

from gmpy2 import bit_scan1, popcount

from playground.games.chess.common.attack_tables import (batk_table, bishop_masks,
                                                     pawn_attacks,
                                                     pseudo_attacks,
                                                     ratk_table, rook_masks)
from playground.games.chess.common.common import (
    bb_between, flip_vertical, gen_bitboard_indices, index_to_san, pawn_push,
    pawn_shift, piece_int_to_string, piece_string_to_int, san_to_index)
from playground.games.chess.common.consts import (
    ALL, ALL_PIECES, B_BISHOP, B_KING, B_KINGSIDE, B_KNIGHT, B_PAWN, B_QUEEN,
    B_QUEENSIDE, B_ROOK, BISHOP, BLACK, CAPTURES, CASTLING, COLOURS,
    EN_PASSANT, ENDGAME, KING, KINGSIDE, KNIGHT, MATERIAL, MIDGAME,
    NO_CASTLING, NO_PIECE, NORMAL, NORTH, PAWN, PIECE_TYPES, PIECES, PROMOTION,
    QUEEN, QUEENSIDE, RANK_1, RANK_2_BB, RANK_4_BB, RANK_5_BB, RANK_7_BB,
    RANK_8, ROOK, W_BISHOP, W_KING, W_KINGSIDE, W_KNIGHT, W_PAWN, W_QUEEN,
    W_QUEENSIDE, W_ROOK, WHITE, ZOBRIST_BOARD, ZOBRIST_CASTLING,
    ZOBRIST_COLOUR, ZOBRIST_ENPASSANT)
from playground.games.chess.common.eval_tables import psq_table
from playground.games.chess.common.movegen import (
    generate_promotions, get_bishop_moves, get_king_moves, get_knight_moves,
    get_pawn_moves, get_queen_moves, get_rook_moves)


class Position:

    def __init__(self, fen):
        [
            fen_board, fen_colour, fen_castling_rights, fen_ep_target,
            fen_halfmove_clock, fen_fullmove_number
        ] = fen.split(' ')

        # Set colour of current player
        self.colour = WHITE if fen_colour == 'w' else BLACK

        # Set castling rights of current position
        self.castling_rights = NO_CASTLING
        if 'K' in fen_castling_rights:
            self.castling_rights += W_KINGSIDE
        if 'Q' in fen_castling_rights:
            self.castling_rights += W_QUEENSIDE
        if 'k' in fen_castling_rights:
            self.castling_rights += B_KINGSIDE
        if 'q' in fen_castling_rights:
            self.castling_rights += B_QUEENSIDE

        # Set en passant target of current position
        if fen_ep_target == '-':
            self.ep_square = None
        else:
            self.ep_square = san_to_index[fen_ep_target]

        # Set halfmove clock and fullmove number of current position
        self.halfmove_clock = int(fen_halfmove_clock)
        self.fullmove_number = int(fen_fullmove_number)

        self.squares = None

        # Initialise bitboards for piece, colour, and overall occupancy
        self.occupancy = 0
        self.player_occ = [0 for _ in range(2)]
        self.piece_bb = [None for _ in range(15)]
        for piece in PIECES:
            self.piece_bb[piece] = 0

        self.zobrist = None
        self.pawn_key = None
        self.material_key = None

        self.init_bitboards_from_fen(fen_board)
        self.init_squares_from_fen(fen_board)
        self.init_zobrist()

        # Initialise stacks for undoing moves and detecting repetitions
        self.undo_info = deque()
        self.repetition_stack = []

        self.is_endgame = False
        self.psq_score_mg = [0, 0]
        self.psq_score_eg = [0, 0]

        self.init_psq_score()

        self.get_moves_for_piece = [None for _ in range(7)]
        self.get_moves_for_piece[PAWN] = get_pawn_moves
        self.get_moves_for_piece[KNIGHT] = get_knight_moves
        self.get_moves_for_piece[BISHOP] = get_bishop_moves
        self.get_moves_for_piece[ROOK] = get_rook_moves
        self.get_moves_for_piece[QUEEN] = get_queen_moves
        self.get_moves_for_piece[KING] = get_king_moves

    # Parse 'FEN' string to initialise bitboard values
    def init_bitboards_from_fen(self, board_fen):
        index = 0

        for char in board_fen:
            if char in 'KQRBNPkqrbnp':
                mask = 1 << index
                if char == 'K':
                    self.piece_bb[W_KING] |= mask
                elif char == 'Q':
                    self.piece_bb[W_QUEEN] |= mask
                elif char == 'R':
                    self.piece_bb[W_ROOK] |= mask
                elif char == 'B':
                    self.piece_bb[W_BISHOP] |= mask
                elif char == 'N':
                    self.piece_bb[W_KNIGHT] |= mask
                elif char == 'P':
                    self.piece_bb[W_PAWN] |= mask
                elif char == 'k':
                    self.piece_bb[B_KING] |= mask
                elif char == 'q':
                    self.piece_bb[B_QUEEN] |= mask
                elif char == 'r':
                    self.piece_bb[B_ROOK] |= mask
                elif char == 'b':
                    self.piece_bb[B_BISHOP] |= mask
                elif char == 'n':
                    self.piece_bb[B_KNIGHT] |= mask
                elif char == 'p':
                    self.piece_bb[B_PAWN] |= mask
                index += 1
            elif char in '12345678':
                index += int(char)
            elif char == '/':
                pass
            else:
                raise Exception('Unknown character in FEN: {}'.format(char))

        for piece in PIECES:
            self.piece_bb[piece] = flip_vertical(self.piece_bb[piece])

        for colour in COLOURS:
            for piece_type in PIECE_TYPES:
                self.player_occ[colour] |= self.piece_bb[(colour << 3)
                                                         | piece_type]

        self.occupancy = self.player_occ[WHITE] | self.player_occ[BLACK]

    # Parse 'FEN' string to initialise list values
    def init_squares_from_fen(self, board_fen):
        self.squares = [None] * 64

        index = 0
        for char in board_fen:
            if char in 'KQRBNPkqrbnp':
                self.squares[index ^ 56] = piece_string_to_int[char]
                index += 1
            elif char in '12345678':
                for _ in range(int(char)):
                    self.squares[index ^ 56] = NO_PIECE
                    index += 1
            elif char == '/':
                pass
            else:
                raise Exception('Unknown character in FEN: {}'.format(char))

    def init_zobrist(self):
        self.zobrist = 0
        self.pawn_key = 0
        self.material_key = 0

        for sq in range(64):
            piece = self.squares[sq]
            if piece:
                self.zobrist ^= ZOBRIST_BOARD[piece][sq]
                if piece & 7 == PAWN:
                    self.pawn_key ^= ZOBRIST_BOARD[piece][sq]

        for piece in PIECES:
            for count in range(popcount(self.piece_bb[piece])):
                self.material_key ^= ZOBRIST_BOARD[piece][count]

        if self.castling_rights & W_KINGSIDE:
            self.zobrist ^= ZOBRIST_CASTLING[W_KINGSIDE]
        if self.castling_rights & W_QUEENSIDE:
            self.zobrist ^= ZOBRIST_CASTLING[W_QUEENSIDE]
        if self.castling_rights & B_KINGSIDE:
            self.zobrist ^= ZOBRIST_CASTLING[B_KINGSIDE]
        if self.castling_rights & B_QUEENSIDE:
            self.zobrist ^= ZOBRIST_CASTLING[B_QUEENSIDE]

    def init_psq_score(self):
        for sq in range(64):
            piece = self.squares[sq]
            if piece:
                colour = piece >> 3
                self.psq_score_mg[colour] += psq_table[piece][sq][MIDGAME]
                self.psq_score_eg[colour] += psq_table[piece][sq][ENDGAME]

    def update_bitboards(self, src_piece, dst_piece, src_index, dst_index,
                         captured):
        src_bb = 1 << src_index
        dst_bb = 1 << dst_index
        move_bb = src_bb | dst_bb

        self.piece_bb[src_piece] ^= src_bb
        self.piece_bb[dst_piece] ^= dst_bb

        self.player_occ[self.colour] ^= move_bb

        if captured:
            self.piece_bb[captured] ^= dst_bb
            self.player_occ[self.colour ^ 1] ^= dst_bb
            self.occupancy ^= src_bb
        else:
            self.occupancy ^= move_bb

    def make_move(self, move):
        src_index = (move >> 6) & 0x3F
        dst_index = move & 0x3F
        move_type = move & (0x3 << 14)

        src_piece = self.squares[src_index]
        captured = self.squares[dst_index]

        self.undo_info.append({
            'move': move,
            'captured': captured,
            'zobrist': self.zobrist,
            'pawn key': self.pawn_key,
            'material key': self.material_key,
            'en passant': self.ep_square,
            'castling': self.castling_rights,
            'halfmove clock': self.halfmove_clock
        })

        self.halfmove_clock += 1

        if move_type == PROMOTION:
            dst_piece_type = ((move >> 12) & 0x3) + 2
            dst_piece = (self.colour << 3) | dst_piece_type
            self.material_key ^= ZOBRIST_BOARD[src_piece][
                popcount(self.piece_bb[src_piece]) - 1]
            self.material_key ^= ZOBRIST_BOARD[dst_piece][popcount(
                self.piece_bb[dst_piece])]
        else:
            dst_piece = src_piece

        old_castle_rights = self.castling_rights

        # Remove castling rights if king has moved
        if src_piece & 7 == KING:
            self.castling_rights &= ~((KINGSIDE + QUEENSIDE) << self.colour)

        # Remove castling rights if rook has moved or been captured
        if src_index == 0 or dst_index == 0:
            self.castling_rights &= ~W_QUEENSIDE
        if src_index == 7 or dst_index == 7:
            self.castling_rights &= ~W_KINGSIDE
        if src_index == 56 or dst_index == 56:
            self.castling_rights &= ~B_QUEENSIDE
        if src_index == 63 or dst_index == 63:
            self.castling_rights &= ~B_KINGSIDE

        changed_rights = old_castle_rights ^ self.castling_rights
        if changed_rights:
            self.zobrist ^= ZOBRIST_CASTLING[changed_rights]

        # Reset en passant square and zobrist
        if self.ep_square:
            self.zobrist ^= ZOBRIST_ENPASSANT[self.ep_square & 7]
            self.ep_square = None

        # Update zobrist
        self.zobrist ^= ZOBRIST_BOARD[src_piece][
            src_index]  # Remove piece from start square
        if captured:
            self.zobrist ^= ZOBRIST_BOARD[captured][
                dst_index]  # Remove captured piece
            self.material_key ^= ZOBRIST_BOARD[captured][
                popcount(self.piece_bb[captured]) - 1]
            self.psq_score_mg[self.colour
                              ^ 1] -= psq_table[captured][dst_index][MIDGAME]
            self.psq_score_eg[self.colour
                              ^ 1] -= psq_table[captured][dst_index][ENDGAME]
            self.halfmove_clock = 0  # Reset halfmove clock on captures
        self.zobrist ^= ZOBRIST_BOARD[dst_piece][
            dst_index]  # Add piece to target square
        self.zobrist ^= ZOBRIST_COLOUR  # Toggle colour

        # Update pawn key
        if src_piece & 7 == PAWN:
            # If making a double push, update en passant square and zobrist
            if src_index ^ dst_index == 16:
                self.ep_square = dst_index - pawn_push[self.colour]
                self.zobrist ^= ZOBRIST_ENPASSANT[self.ep_square & 7]

            # Make changes that are specific for en passant moves
            if move_type == EN_PASSANT:
                ep_capture_index = dst_index - pawn_push[self.colour]
                ep_capture_bb = 1 << ep_capture_index
                ep_captured_piece = ((self.colour ^ 1) << 3) | PAWN

                self.squares[ep_capture_index] = NO_PIECE

                # Update bitboards for the en passant captured piece
                self.piece_bb[ep_captured_piece] ^= ep_capture_bb
                self.player_occ[self.colour ^ 1] ^= ep_capture_bb
                self.occupancy ^= ep_capture_bb

                # Update zobrist for en passant captured piece
                self.zobrist ^= ZOBRIST_BOARD[ep_captured_piece][
                    ep_capture_index]
                self.material_key ^= ZOBRIST_BOARD[ep_captured_piece][
                    popcount(self.piece_bb[ep_captured_piece]) - 1]

                self.psq_score_mg[self.colour ^ 1] -= psq_table[
                    ep_captured_piece][ep_capture_index][MIDGAME]
                self.psq_score_eg[self.colour ^ 1] -= psq_table[
                    ep_captured_piece][ep_capture_index][ENDGAME]

            self.pawn_key ^= ZOBRIST_BOARD[src_piece][src_index]

            if move_type != PROMOTION:
                self.pawn_key ^= ZOBRIST_BOARD[dst_piece][dst_index]

            self.halfmove_clock = 0  # Reset halfmove clock on pawn moves

        if captured & 7 == PAWN:
            self.pawn_key ^= ZOBRIST_BOARD[captured][dst_index]

        # Update square-centric representation
        self.squares[src_index] = NO_PIECE
        self.squares[dst_index] = dst_piece

        # Update piece-square score
        self.psq_score_mg[
            self.colour] -= psq_table[src_piece][src_index][MIDGAME]
        self.psq_score_mg[
            self.colour] += psq_table[dst_piece][dst_index][MIDGAME]
        self.psq_score_eg[
            self.colour] -= psq_table[src_piece][src_index][ENDGAME]
        self.psq_score_eg[
            self.colour] += psq_table[dst_piece][dst_index][ENDGAME]

        # Update bitboards
        self.update_bitboards(src_piece, dst_piece, src_index, dst_index,
                              captured)

        # If castling, move rook
        if move_type == CASTLING:
            if dst_index > src_index:  # Kingside
                rook_src = (7 ^ (self.colour * 56))
                rook_dst = dst_index - 1
            else:  # Queenside
                rook_src = (0 ^ (self.colour * 56))
                rook_dst = dst_index + 1

            player_rook = (self.colour << 3) | ROOK
            self.squares[rook_src] = NO_PIECE
            self.squares[rook_dst] = player_rook
            self.update_bitboards(player_rook, player_rook, rook_src, rook_dst,
                                  None)

            self.zobrist ^= ZOBRIST_BOARD[player_rook][rook_src]
            self.zobrist ^= ZOBRIST_BOARD[player_rook][rook_dst]

            self.psq_score_mg[self.colour] -= psq_table[(
                self.colour << 3) | ROOK][rook_src][MIDGAME]
            self.psq_score_mg[self.colour] += psq_table[(
                self.colour << 3) | ROOK][rook_dst][MIDGAME]
            self.psq_score_eg[self.colour] -= psq_table[(
                self.colour << 3) | ROOK][rook_src][ENDGAME]
            self.psq_score_eg[self.colour] += psq_table[(
                self.colour << 3) | ROOK][rook_dst][ENDGAME]

        # Toggle colour
        self.colour ^= 1

        self.repetition_stack.append(self.zobrist)

    def undo_move(self):
        # Toggle colour
        self.colour ^= 1

        prev_state_info = self.undo_info.pop()

        move = prev_state_info['move']
        captured = prev_state_info['captured']
        self.zobrist = prev_state_info['zobrist']
        self.pawn_key = prev_state_info['pawn key']
        self.material_key = prev_state_info['material key']
        self.ep_square = prev_state_info['en passant']
        self.castling_rights = prev_state_info['castling']
        self.halfmove_clock = prev_state_info['halfmove clock']

        src_index = (move >> 6) & 0x3F
        dst_index = move & 0x3F
        move_type = move & (0x3 << 14)

        dst_piece = self.squares[dst_index]

        if move_type == PROMOTION:
            src_piece = (self.colour << 3) | PAWN
        else:
            src_piece = dst_piece

        self.squares[src_index] = src_piece
        self.squares[dst_index] = captured

        self.psq_score_mg[
            self.colour] -= psq_table[dst_piece][dst_index][MIDGAME]
        self.psq_score_mg[
            self.colour] += psq_table[src_piece][src_index][MIDGAME]
        self.psq_score_eg[
            self.colour] -= psq_table[dst_piece][dst_index][ENDGAME]
        self.psq_score_eg[
            self.colour] += psq_table[src_piece][src_index][ENDGAME]
        if captured:
            self.psq_score_mg[self.colour
                              ^ 1] += psq_table[captured][dst_index][MIDGAME]
            self.psq_score_eg[self.colour
                              ^ 1] += psq_table[captured][dst_index][ENDGAME]

        self.update_bitboards(src_piece, dst_piece, src_index, dst_index,
                              captured)

        # If castling, move rook
        if move_type == CASTLING:
            if dst_index > src_index:  # Kingside
                rook_src = (7 ^ (self.colour * 56))
                rook_dst = dst_index - 1
            else:  # Queenside
                rook_src = (0 ^ (self.colour * 56))
                rook_dst = dst_index + 1

            player_rook = (self.colour << 3) | ROOK
            self.squares[rook_src] = player_rook
            self.squares[rook_dst] = NO_PIECE
            self.update_bitboards(player_rook, player_rook, rook_src, rook_dst,
                                  None)

            self.psq_score_mg[self.colour] -= psq_table[(
                self.colour << 3) | ROOK][rook_dst][MIDGAME]
            self.psq_score_mg[self.colour] += psq_table[(
                self.colour << 3) | ROOK][rook_src][MIDGAME]
            self.psq_score_eg[self.colour] -= psq_table[(
                self.colour << 3) | ROOK][rook_dst][ENDGAME]
            self.psq_score_eg[self.colour] += psq_table[(
                self.colour << 3) | ROOK][rook_src][ENDGAME]
        elif move_type == EN_PASSANT:
            ep_capture_index = dst_index - pawn_push[self.colour]
            ep_capture_bb = 1 << ep_capture_index
            ep_captured_piece = ((self.colour ^ 1) << 3) | PAWN

            # Add en passant captured piece to the square-centric board
            self.squares[ep_capture_index] = ep_captured_piece

            # Update bitboards for the en passant captured piece
            self.piece_bb[ep_captured_piece] ^= ep_capture_bb
            self.player_occ[self.colour ^ 1] ^= ep_capture_bb
            self.occupancy ^= ep_capture_bb

            self.psq_score_mg[
                self.colour
                ^ 1] += psq_table[ep_captured_piece][ep_capture_index][MIDGAME]
            self.psq_score_eg[
                self.colour
                ^ 1] += psq_table[ep_captured_piece][ep_capture_index][ENDGAME]

        self.repetition_stack.pop()

    def make_null_move(self):
        self.undo_info.append({
            'move': 0,
            'captured': 0,
            'zobrist': self.zobrist,
            'en passant': self.ep_square,
            'castling': self.castling_rights,
            'halfmove clock': self.halfmove_clock
        })

        # Reset en passant square and zobrist
        if self.ep_square:
            self.zobrist ^= ZOBRIST_ENPASSANT[self.ep_square & 7]
            self.ep_square = None

        self.zobrist ^= ZOBRIST_COLOUR

        self.halfmove_clock = 0

        # Toggle colour
        self.colour ^= 1

        self.repetition_stack.append(self.zobrist)

    def undo_null_move(self):
        # Toggle colour
        self.colour ^= 1

        prev_state_info = self.undo_info.pop()

        # Restore the attributes that may have been changed by a null move
        self.zobrist = prev_state_info['zobrist']
        self.ep_square = prev_state_info['en passant']
        self.halfmove_clock = prev_state_info['halfmove clock']

        self.repetition_stack.pop()

    def generate_castling(self, colour, move_list):
        if colour == WHITE:
            if self.castling_rights & W_KINGSIDE:
                if not self.occupancy & 0x60:
                    if not self.is_square_attacked(
                            4) and not self.is_square_attacked(
                                5) and not self.is_square_attacked(6):
                        move_list.append(CASTLING + (4 << 6) + 6)
            if self.castling_rights & W_QUEENSIDE:
                if not self.occupancy & 0xe:
                    if not self.is_square_attacked(
                            2) and not self.is_square_attacked(
                                3) and not self.is_square_attacked(4):
                        move_list.append(CASTLING + (4 << 6) + 2)
        else:
            if self.castling_rights & B_KINGSIDE:
                if not self.occupancy & 0x6000000000000000:
                    if not self.is_square_attacked(
                            60) and not self.is_square_attacked(
                                61) and not self.is_square_attacked(62):
                        move_list.append(CASTLING + (60 << 6) + 62)
            if self.castling_rights & B_QUEENSIDE:
                if not self.occupancy & 0xe00000000000000:
                    if not self.is_square_attacked(
                            58) and not self.is_square_attacked(
                                59) and not self.is_square_attacked(60):
                        move_list.append(CASTLING + (60 << 6) + 58)

    def get_check_evasions(self, colour):
        move_list = deque()

        occ = self.occupancy
        king_sqr = bit_scan1(self.piece_bb[((colour << 3) | KING)])

        # Try moving king
        moves = pseudo_attacks[KING][king_sqr] & ~self.player_occ[colour]
        for sq in gen_bitboard_indices(moves):
            if not self.is_square_attacked(sq, occ ^ (1 << king_sqr)):
                move_list.append((king_sqr << 6) + sq)

        attackers = self.attacks_to(king_sqr, colour ^ 1, occ)

        # If in double check, only evasions are through king moves
        if attackers & (attackers - 1):
            return move_list

        enemy_colour = colour ^ 1
        enemy_rooks = self.piece_bb[((enemy_colour << 3) | ROOK)]
        enemy_bishops = self.piece_bb[((enemy_colour << 3) | BISHOP)]
        enemy_queens = self.piece_bb[((enemy_colour << 3) | QUEEN)]

        sliders = ((pseudo_attacks[ROOK][king_sqr] &
                    (enemy_rooks | enemy_queens))
                   | (pseudo_attacks[BISHOP][king_sqr] &
                      (enemy_bishops | enemy_queens)))

        pinned = 0
        while sliders:
            slider_sqr = bit_scan1(sliders)
            sqrs_between = bb_between[king_sqr][slider_sqr]
            blockers = sqrs_between & occ
            if not blockers & (blockers - 1):
                pinned |= blockers
            sliders &= sliders - 1

        attacker_sqr = bit_scan1(attackers)
        attacker_piece = self.squares[attacker_sqr] & 7
        colour_mask = colour << 3

        pawns = self.piece_bb[colour_mask | PAWN]
        knights = self.piece_bb[colour_mask | KNIGHT]
        bishops = self.piece_bb[colour_mask | BISHOP]
        rooks = self.piece_bb[colour_mask | ROOK]
        queens = self.piece_bb[colour_mask | QUEEN]

        # Try capturing attacker piece
        defenders = pawn_attacks[colour ^ 1][attacker_sqr] & pawns
        defenders |= pseudo_attacks[KNIGHT][attacker_sqr] & knights
        defenders |= ratk_table[attacker_sqr][
            occ & rook_masks[attacker_sqr]] & (rooks | queens)
        defenders |= batk_table[attacker_sqr][
            occ & bishop_masks[attacker_sqr]] & (bishops | queens)
        defenders &= ~pinned

        for defender_sq in gen_bitboard_indices(defenders):
            if self.squares[defender_sq] & 7 == PAWN and attacker_sqr >> 3 == (
                    RANK_8 if colour == WHITE else RANK_1):
                generate_promotions(defender_sq, attacker_sqr, move_list)
            else:
                move_list.append((defender_sq << 6) + attacker_sqr)

        # Try blocking attack by slider piece
        if attacker_piece == BISHOP or attacker_piece == ROOK or attacker_piece == QUEEN:  # noqa
            sqrs_between = bb_between[king_sqr][attacker_sqr]

            for sq in gen_bitboard_indices(sqrs_between):
                one_step = pawn_shift[colour ^ 1](1 << sq, NORTH)
                blockers = one_step & pawns
                blockers |= ((RANK_2_BB if colour == WHITE else RANK_7_BB)
                             & pawn_shift[colour ^ 1](one_step & ~occ, NORTH)
                             & pawns)
                blockers |= pseudo_attacks[KNIGHT][sq] & knights
                blockers |= ratk_table[sq][occ & rook_masks[sq]] & (rooks
                                                                    | queens)
                blockers |= batk_table[sq][occ & bishop_masks[sq]] & (bishops
                                                                      | queens)
                blockers &= ~pinned

                for blocker_sq in gen_bitboard_indices(blockers):
                    if self.squares[
                            blocker_sq] & 7 == PAWN and attacker_sqr >> 3 == (
                                RANK_8 if colour == WHITE else RANK_1):
                        generate_promotions(blocker_sq, sq, move_list)
                    else:
                        move_list.append((blocker_sq << 6) + sq)

        if self.ep_square:
            ep_attackers = pawn_attacks[colour ^ 1][self.ep_square] & pawns
            if ep_attackers:
                for sq in gen_bitboard_indices(ep_attackers):
                    ep_move = EN_PASSANT + (sq << 6) + self.ep_square
                    self.make_move(ep_move)
                    in_check = self.is_in_check(colour)
                    self.undo_move()
                    if not in_check:
                        move_list.append(ep_move)

        return move_list

    def get_pseudo_legal_moves(self, gen_type=ALL):
        move_list = deque()

        player_pawns = self.piece_bb[(self.colour << 3) | PAWN]

        self.get_moves_for_piece[PAWN](player_pawns, self.colour, gen_type,
                                       self.occupancy, self.player_occ,
                                       move_list)

        occ_without_pawns = self.player_occ[self.colour] & ~player_pawns

        for sq in gen_bitboard_indices(occ_without_pawns):
            piece = self.squares[sq]
            piece_type = piece & 7

            self.get_moves_for_piece[piece_type](sq, self.colour, gen_type,
                                                 self.occupancy,
                                                 self.player_occ, move_list)

        if self.ep_square:
            ep_attackers = pawn_attacks[self.colour
                                        ^ 1][self.ep_square] & player_pawns
            if ep_attackers:
                for sq in gen_bitboard_indices(ep_attackers):
                    move_list.append(EN_PASSANT + (sq << 6) + self.ep_square)

        if gen_type != CAPTURES:
            self.generate_castling(self.colour, move_list)

        return move_list

    def is_pseudo_legal(self, move):
        move_type = move & (0x3 << 14)
        if move_type != NORMAL:
            return move in self.get_pseudo_legal_moves()

        colour = self.colour

        src_index = (move >> 6) & 0x3F
        dst_index = move & 0x3F
        src_bb = 1 << src_index
        dst_bb = 1 << dst_index

        player_occ = self.player_occ[colour]
        enemy_occ = self.player_occ[colour ^ 1]
        if not src_bb & player_occ:
            return False
        if dst_bb & player_occ:
            return False

        occ = self.occupancy
        piece_type = self.squares[src_index] & 7
        if piece_type == PAWN:
            if dst_bb & pawn_attacks[colour][src_index] & enemy_occ:  # Attack
                return True
            elif dst_bb & pawn_shift[colour](src_bb,
                                             NORTH) & ~occ:  # Single push
                return True
            elif ((dst_bb & (RANK_4_BB if colour == WHITE else RANK_5_BB)
                   & pawn_shift[colour](src_bb, NORTH + NORTH) & ~occ) and
                  (pawn_shift[colour](src_bb, NORTH) & ~occ)):  # Double push
                return True
        elif piece_type == BISHOP:
            if dst_bb & batk_table[src_index][occ & bishop_masks[src_index]]:
                return True
        elif piece_type == ROOK:
            if dst_bb & ratk_table[src_index][occ & rook_masks[src_index]]:
                return True
        elif piece_type == QUEEN:
            if dst_bb & (batk_table[src_index][occ & bishop_masks[src_index]]
                         | ratk_table[src_index][occ & rook_masks[src_index]]):
                return True
        elif dst_bb & pseudo_attacks[piece_type][src_index]:
            return True

        return False

    # Tests the legality of a move, assuming it is pseudo-legal
    def is_legal(self, move):
        colour = self.colour
        enemy_colour = colour ^ 1
        src_index = (move >> 6) & 0x3F
        dst_index = move & 0x3F
        src_bb = 1 << src_index
        dst_bb = 1 << dst_index
        move_type = move & (0x3 << 14)
        king_sqr = bit_scan1(self.piece_bb[((colour << 3) | KING)])
        occ = self.occupancy
        enemy_rooks = self.piece_bb[((enemy_colour << 3) | ROOK)]
        enemy_bishops = self.piece_bb[((enemy_colour << 3) | BISHOP)]
        enemy_queens = self.piece_bb[((enemy_colour << 3) | QUEEN)]

        if self.is_square_attacked(king_sqr):
            return True if move in self.get_check_evasions(colour) else False

        if move_type == EN_PASSANT:
            self.make_move(move)
            in_check = self.is_in_check(colour)
            self.undo_move()
            return False if in_check else True

        if src_index == king_sqr:
            # Castling legality is checked during move generation
            if move_type == CASTLING:
                return True
            if self.is_square_attacked(dst_index, occ ^ (1 << king_sqr)):
                return False
            else:
                return True

        sliders = ((pseudo_attacks[ROOK][king_sqr] &
                    (enemy_rooks | enemy_queens))
                   | (pseudo_attacks[BISHOP][king_sqr] &
                      (enemy_bishops | enemy_queens)))

        while sliders:
            slider_sqr = bit_scan1(sliders)
            sqrs_between = bb_between[king_sqr][slider_sqr]
            blockers = sqrs_between & occ
            if src_bb & sqrs_between:  # If moving blocker piece
                if not blockers ^ src_bb:  # If no other blockers
                    if not dst_bb & (sqrs_between | (1 << slider_sqr)):
                        return False
            sliders &= sliders - 1

        return True

    def is_insufficient_material(self):
        if popcount(self.occupancy) == 2:
            return True
        elif popcount(self.occupancy) == 3:
            if (self.piece_bb[W_KNIGHT] or self.piece_bb[B_KNIGHT]
                    or self.piece_bb[W_BISHOP] or self.piece_bb[B_BISHOP]):
                return True
        return False

    def is_threefold_repetition(self):
        rep_count = 0
        for zobrist in self.repetition_stack[-self.halfmove_clock - 1:]:
            if zobrist == self.zobrist:
                rep_count += 1
                if rep_count >= 3:
                    return True
        return False

    def is_game_over(self):
        # Insufficient material
        if self.is_insufficient_material():
            return True

        # Threefold repetition
        if self.is_threefold_repetition():
            return True

        # Fifty-move rule
        if self.halfmove_clock >= 100:
            return True

        # Checkmate/Stalemate
        has_move = False
        for move in self.get_pseudo_legal_moves():
            if self.is_legal(move):
                has_move = True
                break
        if not has_move:
            return True

        return False

    def is_square_attacked(self, sq, occ=None, colour=None):
        if occ is None:
            occ = self.occupancy
        if colour is None:
            colour = self.colour ^ 1

        colour_mask = colour << 3

        pawns = self.piece_bb[colour_mask | PAWN]
        if pawn_attacks[colour ^ 1][sq] & pawns:
            return True

        knights = self.piece_bb[colour_mask | KNIGHT]
        if pseudo_attacks[KNIGHT][sq] & knights:
            return True

        queens = self.piece_bb[colour_mask | QUEEN]

        bishops = self.piece_bb[colour_mask | BISHOP]
        if batk_table[sq][occ & bishop_masks[sq]] & (bishops | queens):
            return True

        rooks = self.piece_bb[colour_mask | ROOK]
        if ratk_table[sq][occ & rook_masks[sq]] & (rooks | queens):
            return True

        kings = self.piece_bb[colour_mask | KING]
        if pseudo_attacks[KING][sq] & kings:
            return True

        return False

    def attacks_from(self, sq, piece_type, colour, occ):
        if piece_type == PAWN:
            return pawn_attacks[colour][sq]
        if piece_type == BISHOP:
            return batk_table[sq][occ & bishop_masks[sq]]
        elif piece_type == ROOK:
            return ratk_table[sq][occ & rook_masks[sq]]
        elif piece_type == QUEEN:
            return batk_table[sq][occ & bishop_masks[sq]] | ratk_table[sq][
                occ & rook_masks[sq]]
        else:
            return pseudo_attacks[piece_type][sq]

    def attacks_to(self, sq, colour, occ=None):
        if occ is None:
            occ = self.occupancy

        colour_mask = colour << 3

        pawns = self.piece_bb[colour_mask | PAWN]
        knights = self.piece_bb[colour_mask | KNIGHT]
        bishops = self.piece_bb[colour_mask | BISHOP]
        rooks = self.piece_bb[colour_mask | ROOK]
        queens = self.piece_bb[colour_mask | QUEEN]
        kings = self.piece_bb[colour_mask | KING]

        attacked_by = 0
        attacked_by |= pawn_attacks[colour ^ 1][sq] & pawns
        attacked_by |= pseudo_attacks[KNIGHT][sq] & knights
        attacked_by |= pseudo_attacks[KING][sq] & kings
        attacked_by |= ratk_table[sq][occ & rook_masks[sq]] & (rooks | queens)
        attacked_by |= batk_table[sq][occ & bishop_masks[sq]] & (bishops
                                                                 | queens)

        return attacked_by

    def attacks_by(self, piece_type, colour):
        if piece_type == ALL_PIECES:
            piece_bb = self.player_occ[colour]
        else:
            piece_bb = self.piece_bb[(colour << 3) | piece_type]

        attacked = 0
        for sq in gen_bitboard_indices(piece_bb):
            attacked |= self.attacks_from(sq, piece_type, colour,
                                          self.occupancy)

        return attacked

    def get_least_valuable_piece(self, bb, colour):
        colour_mask = colour << 3

        pawns = bb & self.piece_bb[colour_mask | PAWN]
        if pawns:
            return pawns & -pawns  # LSB

        knights = bb & self.piece_bb[colour_mask | KNIGHT]
        if knights:
            return knights & -knights  # LSB

        bishops = bb & self.piece_bb[colour_mask | BISHOP]
        if bishops:
            return bishops & -bishops  # LSB

        rooks = bb & self.piece_bb[colour_mask | ROOK]
        if rooks:
            return rooks & -rooks  # LSB

        queens = bb & self.piece_bb[colour_mask | QUEEN]
        if queens:
            return queens & -queens  # LSB

        kings = bb & self.piece_bb[colour_mask | KING]
        if kings:
            return kings & -kings  # LSB

        return 0  # No pieces of given colour

    def see(self, from_sq, target_sq):
        gain = [None] * 32
        depth = 0
        gain[depth] = MATERIAL[self.squares[target_sq] & 7][MIDGAME]
        occ = self.occupancy
        colour = self.colour
        attackers = self.attacks_to(target_sq, colour ^ 1, occ)
        attackers |= self.attacks_to(target_sq, colour, occ)
        from_bb = 1 << from_sq
        slider_blockers = occ ^ (
            self.piece_bb[W_KNIGHT] | self.piece_bb[B_KNIGHT]
            | self.piece_bb[W_KING] | self.piece_bb[B_KING])

        piece = self.squares[from_sq]

        while from_bb:
            depth += 1
            colour ^= 1
            gain[depth] = MATERIAL[piece & 7][MIDGAME] - gain[depth - 1]
            if max(-gain[depth - 1], gain[depth]) < 0:
                break
            attackers ^= from_bb
            occ ^= from_bb
            if from_bb & slider_blockers:
                attackers |= ratk_table[target_sq][
                    occ
                    & rook_masks[target_sq]] & (self.piece_bb[W_ROOK]
                                                | self.piece_bb[B_ROOK]
                                                | self.piece_bb[W_QUEEN]
                                                | self.piece_bb[B_QUEEN]) & occ
                attackers |= batk_table[target_sq][
                    occ & bishop_masks[target_sq]] & (
                        self.piece_bb[W_BISHOP]
                        | self.piece_bb[B_BISHOP]
                        | self.piece_bb[W_QUEEN]
                        | self.piece_bb[B_QUEEN]) & occ
            from_bb = self.get_least_valuable_piece(attackers, colour)
            if from_bb:
                piece = self.squares[bit_scan1(from_bb)]

        depth -= 1
        while depth:
            gain[depth - 1] = -max(-gain[depth - 1], gain[depth])
            depth -= 1

        return gain[0]

    def gives_check(self, move):
        src_index = (move >> 6) & 0x3F
        dst_index = move & 0x3F
        piece = self.squares[src_index]
        piece_type = piece & 7
        piece_colour = piece >> 3

        attacks = self.attacks_from(dst_index, piece_type, piece_colour,
                                    self.occupancy)

        return attacks & self.piece_bb[((self.colour ^ 1) << 3) | KING]

    def is_in_check(self, colour=None):
        if colour is None:
            colour = self.colour
        king_index = bit_scan1(self.piece_bb[((colour << 3) | KING)])

        if self.is_square_attacked(king_index, colour=colour ^ 1):
            return True

        return False

    def is_checkmate(self):
        if self.is_in_check():
            for move in self.get_pseudo_legal_moves():
                if self.is_legal(move):
                    return False
            return True
        return False

    def move_to_san(self, move):
        src_index = (move >> 6) & 0x3F
        dst_index = move & 0x3F

        move_type = move & (0x3 << 14)
        piece_type = self.squares[src_index] & 7

        is_capture = True if self.squares[
            dst_index] or move_type == EN_PASSANT else False
        is_promotion = True if move_type == PROMOTION else False
        is_castle = True if move_type == CASTLING else False

        if is_castle:
            if dst_index > src_index:  # Kingside
                return '0-0'
            else:  # Queenside
                return '0-0-0'

        san = ''
        if piece_type == PAWN:
            if is_capture:
                san += chr(97 + (src_index & 7))
        else:
            san += piece_int_to_string[piece_type]
        if is_capture:
            san += 'x'
        san += index_to_san[dst_index]

        if is_promotion:
            san += '='
            san += piece_int_to_string[piece_type]

        if self.gives_check(move):
            self.make_move(move)
            if self.is_checkmate():
                san += '#'
            else:
                san += '+'
            self.undo_move()
        return san

    def get_fen(self):
        board = [None for _ in range(64)]

        for sq in range(32):
            current_piece = self.squares[sq]
            flipped_piece = self.squares[sq ^ 56]
            board[sq] = flipped_piece
            board[sq ^ 56] = current_piece

        fen = ''
        empty = 0

        for sq in range(64):
            piece = board[sq]
            if piece:
                if empty > 0:
                    fen += str(empty)
                    empty = 0
                fen += piece_int_to_string[piece]
            else:
                empty += 1

            if (sq + 1) % 8 == 0:
                if empty > 0:
                    fen += str(empty)
                    empty = 0
                if sq != 63:
                    fen += '/'

        fen += ' '

        if self.colour == WHITE:
            fen += 'w'
        else:
            fen += 'b'

        fen += ' '

        if self.castling_rights:
            if self.castling_rights & W_KINGSIDE:
                fen += 'W'
            if self.castling_rights & W_QUEENSIDE:
                fen += 'Q'
            if self.castling_rights & B_KINGSIDE:
                fen += 'k'
            if self.castling_rights & B_QUEENSIDE:
                fen += 'q'
        else:
            fen += '-'

        fen += ' '
        fen += str(self.ep_square) if self.ep_square else '-'
        fen += ' '
        fen += str(self.halfmove_clock)
        fen += ' '
        fen += str(self.fullmove_number)

        return fen
