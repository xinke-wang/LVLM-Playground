from gmpy2 import bit_scan1

from playground.games.chess.common.attack_tables import (batk_table, bishop_masks,
                                                     pseudo_attacks,
                                                     ratk_table, rook_masks)
from playground.games.chess.common.common import pawn_shift
from playground.games.chess.common.consts import (
    A_FILE_BB, ALL, BISHOP_PROMOTION, CAPTURES, H_FILE_BB, KING, KNIGHT,
    KNIGHT_PROMOTION, NORTH, NORTHEAST, NORTHWEST, PROMOTION, QUEEN_PROMOTION,
    QUIETS, RANK_2_BB, RANK_3_BB, RANK_6_BB, RANK_7_BB, ROOK_PROMOTION, WHITE)


def get_king_moves(sq, colour, move_type, occ, player_occ, move_list):
    moves = pseudo_attacks[KING][sq]

    if move_type == QUIETS:
        moves &= ~occ
    elif move_type == CAPTURES:
        moves &= player_occ[colour ^ 1]
    elif move_type == ALL:
        moves &= ~player_occ[colour]

    while moves:
        index = bit_scan1(moves)
        moves &= moves - 1
        move_list.append((sq << 6) + index)


def get_knight_moves(sq, colour, move_type, occ, player_occ, move_list):
    moves = pseudo_attacks[KNIGHT][sq]

    if move_type == QUIETS:
        moves &= ~occ
    elif move_type == CAPTURES:
        moves &= player_occ[colour ^ 1]
    elif move_type == ALL:
        moves &= ~player_occ[colour]

    while moves:
        index = bit_scan1(moves)
        moves &= moves - 1
        move_list.append((sq << 6) + index)


def get_pawn_moves(bitboard, colour, move_type, occ, player_occ, move_list):
    empty = ~occ
    enemy_occ = player_occ[colour ^ 1]

    if colour == WHITE:
        third_rank = RANK_3_BB
        seventh_rank = RANK_7_BB
        one_step_shift = NORTH
        two_step_shift = one_step_shift + NORTH
        left_atk_shift = 7
        right_atk_shift = 9
        left_file = A_FILE_BB
        right_file = H_FILE_BB
    else:
        third_rank = RANK_6_BB
        seventh_rank = RANK_2_BB
        one_step_shift = -NORTH
        two_step_shift = one_step_shift - NORTH
        left_atk_shift = -7
        right_atk_shift = -9
        left_file = H_FILE_BB
        right_file = A_FILE_BB

    pawns_not_promoting = bitboard & ~seventh_rank
    promoting_pawns = bitboard & seventh_rank

    # Captures and queen promotions
    if move_type == CAPTURES or move_type == ALL:
        left_atk = pawn_shift[colour](
            (pawns_not_promoting & ~left_file), NORTHWEST) & enemy_occ
        right_atk = pawn_shift[colour](
            (pawns_not_promoting & ~right_file), NORTHEAST) & enemy_occ

        promoted_push = pawn_shift[colour](promoting_pawns, NORTH) & empty
        promoted_left_atk = pawn_shift[colour](
            (promoting_pawns & ~left_file), NORTHWEST) & enemy_occ
        promoted_right_atk = pawn_shift[colour](
            (promoting_pawns & ~right_file), NORTHEAST) & enemy_occ

        while left_atk:
            index = bit_scan1(left_atk)
            left_atk &= left_atk - 1
            move_list.append(((index - left_atk_shift) << 6) + index)

        while right_atk:
            index = bit_scan1(right_atk)
            right_atk &= right_atk - 1
            move_list.append(((index - right_atk_shift) << 6) + index)

        while promoted_push:
            index = bit_scan1(promoted_push)
            promoted_push &= promoted_push - 1
            from_to = ((index - one_step_shift) << 6) + index
            move_list.append(PROMOTION + QUEEN_PROMOTION + from_to)

        while promoted_left_atk:
            index = bit_scan1(promoted_left_atk)
            promoted_left_atk &= promoted_left_atk - 1
            from_to = ((index - left_atk_shift) << 6) + index
            move_list.append(PROMOTION + QUEEN_PROMOTION + from_to)

        while promoted_right_atk:
            index = bit_scan1(promoted_right_atk)
            promoted_right_atk &= promoted_right_atk - 1
            from_to = ((index - right_atk_shift) << 6) + index
            move_list.append(PROMOTION + QUEEN_PROMOTION + from_to)

    # Non-captures and underpromotions
    if move_type == QUIETS or move_type == ALL:
        one_step = pawn_shift[colour](pawns_not_promoting, NORTH) & empty
        two_steps = pawn_shift[colour]((one_step & third_rank), NORTH) & empty

        promoted_push = pawn_shift[colour](promoting_pawns, NORTH) & empty
        promoted_left_atk = pawn_shift[colour](
            (promoting_pawns & ~left_file), NORTHWEST) & enemy_occ
        promoted_right_atk = pawn_shift[colour](
            (promoting_pawns & ~right_file), NORTHEAST) & enemy_occ

        while one_step:
            index = bit_scan1(one_step)
            one_step &= one_step - 1
            move_list.append(((index - one_step_shift) << 6) + index)

        while two_steps:
            index = bit_scan1(two_steps)
            two_steps &= two_steps - 1
            move_list.append(((index - two_step_shift) << 6) + index)

        while promoted_push:
            index = bit_scan1(promoted_push)
            promoted_push &= promoted_push - 1
            generate_underpromotions(index - one_step_shift, index, move_list)

        while promoted_left_atk:
            index = bit_scan1(promoted_left_atk)
            promoted_left_atk &= promoted_left_atk - 1
            generate_underpromotions(index - left_atk_shift, index, move_list)

        while promoted_right_atk:
            index = bit_scan1(promoted_right_atk)
            promoted_right_atk &= promoted_right_atk - 1
            generate_underpromotions(index - right_atk_shift, index, move_list)


def get_rook_moves(sq, colour, move_type, occ, player_occ, move_list):
    moves = ratk_table[sq][occ & rook_masks[sq]]

    if move_type == QUIETS:
        moves &= ~occ
    elif move_type == CAPTURES:
        moves &= player_occ[colour ^ 1]
    elif move_type == ALL:
        moves &= ~player_occ[colour]

    while moves:
        index = bit_scan1(moves)
        moves &= moves - 1
        move_list.append((sq << 6) + index)


def get_bishop_moves(sq, colour, move_type, occ, player_occ, move_list):
    moves = batk_table[sq][occ & bishop_masks[sq]]

    if move_type == QUIETS:
        moves &= ~occ
    elif move_type == CAPTURES:
        moves &= player_occ[colour ^ 1]
    elif move_type == ALL:
        moves &= ~player_occ[colour]

    while moves:
        index = bit_scan1(moves)
        moves &= moves - 1
        move_list.append((sq << 6) + index)


def get_queen_moves(sq, colour, move_type, occ, player_occ, move_list):
    moves = batk_table[sq][occ & bishop_masks[sq]] | ratk_table[sq][
        occ & rook_masks[sq]]

    if move_type == QUIETS:
        moves &= ~occ
    elif move_type == CAPTURES:
        moves &= player_occ[colour ^ 1]
    elif move_type == ALL:
        moves &= ~player_occ[colour]

    while moves:
        index = bit_scan1(moves)
        moves &= moves - 1
        move_list.append((sq << 6) + index)


def generate_promotions(src_sq, dst_sq, move_list):
    from_to = (src_sq << 6) + dst_sq
    move_list.append(PROMOTION + KNIGHT_PROMOTION + from_to)
    move_list.append(PROMOTION + BISHOP_PROMOTION + from_to)
    move_list.append(PROMOTION + ROOK_PROMOTION + from_to)
    move_list.append(PROMOTION + QUEEN_PROMOTION + from_to)


def generate_underpromotions(src_sq, dst_sq, move_list):
    from_to = (src_sq << 6) + dst_sq
    move_list.append(PROMOTION + KNIGHT_PROMOTION + from_to)
    move_list.append(PROMOTION + BISHOP_PROMOTION + from_to)
    move_list.append(PROMOTION + ROOK_PROMOTION + from_to)
