from gmpy2 import bit_scan1, popcount

from playground.games.chess.common.attack_tables import (batk_table, bishop_masks,
                                                     pseudo_attacks,
                                                     ratk_table, rook_masks)
from playground.games.chess.common.common import (adjacent_files, distance_ring,
                                              forward_fill, forward_ranks,
                                              gen_bitboard_indices, pawn_shift,
                                              rank_of)
from playground.games.chess.common.consts import (
    _64BITS, A_FILE, A_FILE_BB, B_BISHOP, B_FILE, B_KNIGHT, B_QUEEN, B_ROOK,
    BACKWARD, BISHOP, BLACK, COLOURS, DOUBLED, ENDGAME, G_FILE, H_FILE,
    H_FILE_BB, ISOLATED, KING, KINGSIDE, KNIGHT, MATERIAL, MIDGAME, NORTH,
    NORTHEAST, NORTHWEST, PAWN, PIECE_TYPES, QUEEN, QUEENSIDE, RANK_1,
    RANK_1_BB, RANK_2_BB, RANK_3, RANK_7_BB, RANK_8_BB, ROOK, W_BISHOP,
    W_KNIGHT, W_QUEEN, W_ROOK, WHITE, MaterialEntry, PawnEntry)
from playground.games.chess.common.eval_tables import (connected_bonus,
                                                   enemy_imbalance, mobility,
                                                   player_imbalance,
                                                   shelter_strength,
                                                   unblocked_storm)


class Evaluate:

    def __init__(self):
        # Initialise pawn hash table
        self.PAWN_TABLE_SIZE = 2**16
        self.pawn_table = [None] * self.PAWN_TABLE_SIZE

        # Initialise material hash table
        self.MATERIAL_TABLE_SIZE = 2**16
        self.material_table = [None] * self.MATERIAL_TABLE_SIZE

        self.prev_king_square = [None for _ in range(2)]
        self.prev_castling_rights = [None for _ in range(2)]

        self.king_safety = [None for _ in range(2)]

    def imbalance(self, position, colour):
        imbalance_score = 0

        player_bishop_pair = True if popcount(
            position.piece_bb[(colour << 3) | BISHOP]) > 1 else False
        if player_bishop_pair:
            enemy_bishop_pair = True if popcount(position.piece_bb[(
                (colour ^ 1) << 3) | BISHOP]) > 1 else False
            temp = (player_imbalance[0][0] * player_bishop_pair +
                    enemy_imbalance[0][0] * enemy_bishop_pair)
            imbalance_score += player_bishop_pair * temp

        for piece_type_one in PIECE_TYPES[:QUEEN]:
            ours = position.piece_bb[(colour << 3) | piece_type_one]
            if not popcount(ours):
                continue
            temp = 0
            for piece_type_two in PIECE_TYPES[:piece_type_one]:
                player_pieces = position.piece_bb[(colour << 3)
                                                  | piece_type_two]
                enemy_pieces = position.piece_bb[((colour ^ 1) << 3)
                                                 | piece_type_two]
                temp += (player_imbalance[piece_type_one][piece_type_two] *
                         popcount(player_pieces) +
                         enemy_imbalance[piece_type_one][piece_type_two] *
                         popcount(enemy_pieces))
            imbalance_score += popcount(ours) * temp

        return imbalance_score

    def evaluate_material(self, position):
        score_mg = 0
        score_eg = 0

        material_table_index = position.material_key & 0xFFFF
        material_entry = self.material_table[material_table_index]
        if material_entry and material_entry.key == position.material_key:
            score_mg += material_entry.imbalance
            score_eg += material_entry.imbalance

            score_mg += material_entry.material_score[MIDGAME]
            score_eg += material_entry.material_score[ENDGAME]
        else:
            imbalance_score = (self.imbalance(position, WHITE) -
                               self.imbalance(position, BLACK)) // 16
            score_mg += imbalance_score
            score_eg += imbalance_score

            material_score = [0, 0]
            for sq in gen_bitboard_indices(position.occupancy):
                piece = position.squares[sq]
                if piece >> 3 == WHITE:
                    material_score[MIDGAME] += MATERIAL[piece & 7][MIDGAME]
                    material_score[ENDGAME] += MATERIAL[piece & 7][ENDGAME]
                else:
                    material_score[MIDGAME] -= MATERIAL[piece & 7][MIDGAME]
                    material_score[ENDGAME] -= MATERIAL[piece & 7][ENDGAME]
            score_mg += material_score[MIDGAME]
            score_eg += material_score[ENDGAME]

            self.material_table[material_table_index] = MaterialEntry(
                position.material_key, material_score, imbalance_score)

        return score_mg, score_eg

    def get_mobility_area(self, position, colour):
        area = _64BITS
        player_pawns = position.piece_bb[(colour << 3) | PAWN]
        enemy_pawns = position.piece_bb[((colour ^ 1) << 3) | PAWN]

        area &= ~(pawn_shift[colour ^ 1](enemy_pawns, NORTHEAST)
                  | pawn_shift[colour ^ 1](enemy_pawns, NORTHWEST))
        area &= ~(player_pawns & (pawn_shift[colour ^ 1](enemy_pawns, NORTH)
                                  | RANK_1_BB << (1 ^ (colour * 7))
                                  | RANK_1_BB << (2 ^ (colour * 7))))
        area &= ~position.piece_bb[(colour << 3) | KING]
        area &= ~position.piece_bb[(colour << 3) | QUEEN]

        return area

    def evaluate_mobility(self, position, mobility_bb):
        mobility_area = [0, 0]
        mobility_score_mg = [0, 0]
        mobility_score_eg = [0, 0]

        mobility_area[WHITE] = self.get_mobility_area(position, WHITE)
        mobility_area[BLACK] = self.get_mobility_area(position, BLACK)

        for sq in gen_bitboard_indices(mobility_bb):
            piece = position.squares[sq]
            piece_type = piece & 7
            piece_colour = piece >> 3

            if piece_type == KNIGHT:
                moves = pseudo_attacks[KNIGHT][sq]
            elif piece_type == BISHOP:
                moves = batk_table[sq][(position.occupancy ^ position.piece_bb[
                    (piece_colour << 3) | QUEEN]) & bishop_masks[sq]]
            elif piece_type == ROOK:
                moves = ratk_table[sq][(position.occupancy ^ position.piece_bb[
                    (piece_colour << 3) | ROOK] ^ position.piece_bb[
                        (piece_colour << 3) | QUEEN]) & rook_masks[sq]]
            elif piece_type == QUEEN:
                moves = ratk_table[sq][position.occupancy
                                       & rook_masks[sq]] | batk_table[sq][
                                           position.occupancy
                                           & bishop_masks[sq]]

            moves &= mobility_area[piece_colour]

            move_count = popcount(moves)
            mobility_score_mg[piece_colour] += mobility[piece_type][
                move_count][MIDGAME]
            mobility_score_eg[piece_colour] += mobility[piece_type][
                move_count][ENDGAME]

        score_mg = mobility_score_mg[WHITE] - mobility_score_mg[BLACK]
        score_eg = mobility_score_eg[WHITE] - mobility_score_eg[BLACK]

        return score_mg, score_eg

    def evaluate_pawns(self, position):
        pawn_table_index = position.pawn_key & 0xFFFF
        pawn_entry = self.pawn_table[pawn_table_index]
        if pawn_entry and pawn_entry.key == position.pawn_key:
            return pawn_entry.score_mg, pawn_entry.score_eg

        # king_sqr = None

        score_mg = [0, 0]
        score_eg = [0, 0]

        for colour in COLOURS:
            player_pawns = position.piece_bb[(colour << 3) | PAWN]
            enemy_pawns = position.piece_bb[((colour ^ 1) << 3) | PAWN]
            enemy_pawn_attacks = (
                pawn_shift[colour ^ 1](enemy_pawns, NORTHEAST)
                | pawn_shift[colour ^ 1](enemy_pawns, NORTHWEST))

            for sq in gen_bitboard_indices(player_pawns):
                pawn_bb = 1 << sq
                adjacent_squares = adjacent_files[sq] & rank_of[sq]
                adjacent_pawns = adjacent_files[sq] & player_pawns
                aligned = True if adjacent_squares & player_pawns else False
                defenders = adjacent_pawns & pawn_shift[colour ^ 1](
                    rank_of[sq], NORTH)
                opposed = True if forward_fill[colour](
                    pawn_bb) & enemy_pawns else False

                # Doubled pawn
                if (player_pawns & pawn_shift[colour ^ 1](
                        pawn_bb, NORTH)) and not defenders:
                    score_mg[colour] -= DOUBLED[MIDGAME]
                    score_eg[colour] -= DOUBLED[ENDGAME]

                # Connected pawn
                if aligned or defenders:
                    score_mg[colour] += connected_bonus[opposed][aligned][
                        popcount(defenders)][(sq >> 3) ^ (colour * 7)][MIDGAME]
                    score_eg[colour] += connected_bonus[opposed][aligned][
                        popcount(defenders)][(sq >> 3) ^ (colour * 7)][ENDGAME]

                # Isolated pawn
                elif not adjacent_pawns:
                    score_mg[colour] -= ISOLATED[MIDGAME]
                    score_eg[colour] -= ISOLATED[ENDGAME]

                # Backward pawn
                elif (pawn_shift[colour](pawn_bb, NORTH) &
                      (enemy_pawns | enemy_pawn_attacks)
                      and not forward_fill[colour ^ 1](adjacent_squares)
                      & player_pawns):
                    score_mg[colour] -= BACKWARD[MIDGAME]
                    score_eg[colour] -= BACKWARD[ENDGAME]

        score_mg = score_mg[WHITE] - score_mg[BLACK]
        score_eg = score_eg[WHITE] - score_eg[BLACK]

        self.pawn_table[pawn_table_index] = PawnEntry(position.pawn_key,
                                                      score_mg, score_eg)

        return score_mg, score_eg

    def evaluate_king_shelter(self, position, colour, king_sqr):
        # Gets the bitboard of the back two ranks for the given colour
        shelter_ranks = RANK_1_BB | RANK_2_BB if colour == WHITE \
            else RANK_7_BB | RANK_8_BB

        ranks_in_front = ~forward_ranks[colour ^ 1][king_sqr]
        player_pawns = position.piece_bb[(colour << 3) | PAWN] & ranks_in_front
        enemy_pawns = position.piece_bb[(
            (colour ^ 1) << 3) | PAWN] & ranks_in_front

        # Give a bonus for enemy edge pawns in front of our king
        if pawn_shift[colour ^ 1](enemy_pawns, NORTH) & (
                A_FILE_BB | H_FILE_BB) & shelter_ranks & (1 << king_sqr):
            safety_score = 374
        else:
            safety_score = 5

        # Get the centre file of the king shelter
        king_file = king_sqr & 7
        if king_file == A_FILE:
            centre = B_FILE
        elif king_file == H_FILE:
            centre = G_FILE
        else:
            centre = king_file

        # Iterate through the centre file and the two adjacent files
        for file_num in range(centre - 1, centre + 2):
            file_bb = A_FILE_BB << file_num

            pawns_on_file = player_pawns & file_bb
            if pawns_on_file:
                if colour == WHITE:
                    backmost_sq = bit_scan1(
                        pawns_on_file)  # Least significant bit
                else:
                    backmost_sq = pawns_on_file.bit_length(
                    ) - 1  # Most significant bit
                player_rank = (backmost_sq >> 3) ^ (colour * 7)
            else:
                player_rank = RANK_1

            pawns_on_file = enemy_pawns & file_bb
            if pawns_on_file:
                if colour == WHITE:
                    frontmost_sq = pawns_on_file.bit_length(
                    ) - 1  # Most significant bit
                else:
                    frontmost_sq = bit_scan1(
                        pawns_on_file)  # Least significant bit
                enemy_rank = (frontmost_sq >> 3) ^ (colour * 7)
            else:
                enemy_rank = RANK_1

            opposite_file = file_num ^ H_FILE
            min_file = opposite_file if opposite_file < file_num else file_num
            safety_score += shelter_strength[min_file][player_rank]
            if player_rank and player_rank == enemy_rank - 1:
                if enemy_rank == RANK_3:
                    safety_score -= 66
            else:
                safety_score -= unblocked_storm[min_file][enemy_rank]

        return safety_score

    def get_king_safety(self, position, colour):
        king_sqr = bit_scan1(position.piece_bb[(colour << 3) | KING])
        if self.prev_king_square[colour] == king_sqr:
            if self.prev_castling_rights[
                    colour] == position.castling_rights & (0x3 <<
                                                           (colour * 2)):
                return self.king_safety[colour]

        player_pawns = position.piece_bb[(colour << 3) | PAWN]

        king_pawn_distance = 0
        if player_pawns:
            king_pawn_distance += 1
            while not distance_ring[king_sqr][
                    king_pawn_distance] & player_pawns:
                king_pawn_distance += 1

        # Evaluate the shelter for the king square
        score = self.evaluate_king_shelter(position, colour, king_sqr)

        if position.castling_rights & (KINGSIDE << colour):
            castled_score = self.evaluate_king_shelter(position, colour,
                                                       6 ^ (colour * 56))
            if castled_score > score:
                score = castled_score

        if position.castling_rights & (QUEENSIDE << colour):
            castled_score = self.evaluate_king_shelter(position, colour,
                                                       2 ^ (colour * 56))
            if castled_score > score:
                score = castled_score

        # Save the king safety information for the current position
        self.prev_king_square[colour] = king_sqr
        self.prev_castling_rights[colour] = position.castling_rights & (
            0x3 << (colour * 2))
        self.king_safety[colour] = (score, -16 * king_pawn_distance)

        return score, -16 * king_pawn_distance

    def evaluate(self, position):
        knights = position.piece_bb[W_KNIGHT] | position.piece_bb[B_KNIGHT]
        bishops = position.piece_bb[W_BISHOP] | position.piece_bb[B_BISHOP]
        rooks = position.piece_bb[W_ROOK] | position.piece_bb[B_ROOK]
        queens = position.piece_bb[W_QUEEN] | position.piece_bb[B_QUEEN]

        phase = 24 - (popcount(knights | bishops) + (popcount(rooks) * 2) +
                      (popcount(queens) * 4))
        phase = ((phase * 256) + 12) // 24

        score_mg = 0
        score_eg = 0

        # Piece-square tables
        score_mg += position.psq_score_mg[WHITE] - position.psq_score_mg[BLACK]
        score_eg += position.psq_score_eg[WHITE] - position.psq_score_eg[BLACK]

        # Evaluate material
        material_score_mg, material_score_eg = self.evaluate_material(position)
        score_mg += material_score_mg
        score_eg += material_score_eg

        # Evaluate pawns
        pawn_score_mg, pawn_score_eg = self.evaluate_pawns(position)
        score_mg += pawn_score_mg
        score_eg += pawn_score_eg

        # Mobility
        mobility_bb = knights | bishops | rooks | queens
        mobility_score_mg, mobility_score_eg = self.evaluate_mobility(
            position, mobility_bb)
        score_mg += mobility_score_mg
        score_eg += mobility_score_eg

        # King safety
        w_king_score_mg, w_king_score_eg = self.get_king_safety(
            position, WHITE)
        b_king_score_mg, b_king_score_eg = self.get_king_safety(
            position, BLACK)
        score_mg += w_king_score_mg - b_king_score_mg
        score_eg += w_king_score_eg - b_king_score_eg

        # Interpolate between midgame and endgame score based on phase
        score = ((score_mg * (256 - phase)) + (score_eg * phase)) // 256

        return score + 28 if position.colour == WHITE else -score + 28
