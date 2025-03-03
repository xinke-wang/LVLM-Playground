import operator
import re

from gmpy2 import bit_scan1

import playground.games.chess.common.flood_fill as ff
from playground.games.chess.common.attack_tables import pseudo_attacks
from playground.games.chess.common.consts import (
    A_FILE_BB, B_BISHOP, B_FILE_BB, B_KING, B_KNIGHT, B_PAWN, B_QUEEN, B_ROOK,
    BLACK, C_FILE_BB, D_FILE_BB, E_FILE_BB, EAST, F_FILE_BB, G_FILE_BB,
    H_FILE_BB, KING, NORTH, RANK_1_BB, RANK_2_BB, RANK_3_BB, RANK_4_BB,
    RANK_5_BB, RANK_6_BB, RANK_7_BB, RANK_8_BB, W_BISHOP, W_KING, W_KNIGHT,
    W_PAWN, W_QUEEN, W_ROOK, WHITE)

# FEN string for starting chess position
starting_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

# Regular expressions for common chess notation
rank = r'[rnbqkpRNBQKP1-8]{1,8}'
board_fen = rank + '/' + rank + '/' + rank + '/' + rank + '/' + rank + '/' \
    + rank + '/' + rank + '/' + rank
regex_fen = re.compile(
    r'^' + board_fen +
    r' [wb] (?:(?:K?Q?k?q?)|-) (?:(?:[a-h][1-8])|-) \d+ \d+$')
regex_square = re.compile(r'[a-h][1-8]')
regex_san = re.compile(
    r'^(?:(?P<qCastle>O-O-O)|(?P<kCastle>O-O)|(?P<srcPiece>[NbRQK])?'
    r'(?P<srcHint>[a-h1-8]{1,2})?(?P<action>x)?(?P<dstSquare>[a-h][1-8])'
    r'(?P<promote>=[NbRQ])?)(?P<check>[+#])?')

# Used for converting files from letters to numbers
notation_to_index = {
    'a': 1,
    'b': 2,
    'c': 3,
    'd': 4,
    'e': 5,
    'f': 6,
    'g': 7,
    'h': 8
}

# Used for converting files from numbers to letters
index_to_notation = {
    1: 'a',
    2: 'b',
    3: 'c',
    4: 'd',
    5: 'e',
    6: 'f',
    7: 'g',
    8: 'h'
}

# Used for converting squares from algebraic notation to index notation
san_to_index = {
    'a8': 56,
    'b8': 57,
    'c8': 58,
    'd8': 59,
    'e8': 60,
    'f8': 61,
    'g8': 62,
    'h8': 63,
    'a7': 48,
    'b7': 49,
    'c7': 50,
    'd7': 51,
    'e7': 52,
    'f7': 53,
    'g7': 54,
    'h7': 55,
    'a6': 40,
    'b6': 41,
    'c6': 42,
    'd6': 43,
    'e6': 44,
    'f6': 45,
    'g6': 46,
    'h6': 47,
    'a5': 32,
    'b5': 33,
    'c5': 34,
    'd5': 35,
    'e5': 36,
    'f5': 37,
    'g5': 38,
    'h5': 39,
    'a4': 24,
    'b4': 25,
    'c4': 26,
    'd4': 27,
    'e4': 28,
    'f4': 29,
    'g4': 30,
    'h4': 31,
    'a3': 16,
    'b3': 17,
    'c3': 18,
    'd3': 19,
    'e3': 20,
    'f3': 21,
    'g3': 22,
    'h3': 23,
    'a2': 8,
    'b2': 9,
    'c2': 10,
    'd2': 11,
    'e2': 12,
    'f2': 13,
    'g2': 14,
    'h2': 15,
    'a1': 0,
    'b1': 1,
    'c1': 2,
    'd1': 3,
    'e1': 4,
    'f1': 5,
    'g1': 6,
    'h1': 7
}

# Used for converting squares from index notation to algebraic notation
index_to_san = {
    56: 'a8',
    57: 'b8',
    58: 'c8',
    59: 'd8',
    60: 'e8',
    61: 'f8',
    62: 'g8',
    63: 'h8',
    48: 'a7',
    49: 'b7',
    50: 'c7',
    51: 'd7',
    52: 'e7',
    53: 'f7',
    54: 'g7',
    55: 'h7',
    40: 'a6',
    41: 'b6',
    42: 'c6',
    43: 'd6',
    44: 'e6',
    45: 'f6',
    46: 'g6',
    47: 'h6',
    32: 'a5',
    33: 'b5',
    34: 'c5',
    35: 'd5',
    36: 'e5',
    37: 'f5',
    38: 'g5',
    39: 'h5',
    24: 'a4',
    25: 'b4',
    26: 'c4',
    27: 'd4',
    28: 'e4',
    29: 'f4',
    30: 'g4',
    31: 'h4',
    16: 'a3',
    17: 'b3',
    18: 'c3',
    19: 'd3',
    20: 'e3',
    21: 'f3',
    22: 'g3',
    23: 'h3',
    8: 'a2',
    9: 'b2',
    10: 'c2',
    11: 'd2',
    12: 'e2',
    13: 'f2',
    14: 'g2',
    15: 'h2',
    0: 'a1',
    1: 'b1',
    2: 'c1',
    3: 'd1',
    4: 'e1',
    5: 'f1',
    6: 'g1',
    7: 'h1',
}

# Used for converting pieces from letters to numbers
piece_string_to_int = {
    'P': W_PAWN,
    'N': W_KNIGHT,
    'B': W_BISHOP,
    'R': W_ROOK,
    'Q': W_QUEEN,
    'K': W_KING,
    'p': B_PAWN,
    'n': B_KNIGHT,
    'b': B_BISHOP,
    'r': B_ROOK,
    'q': B_QUEEN,
    'k': B_KING
}

# Used for converting pieces from numbers to letters
piece_int_to_string = {
    W_PAWN: 'P',
    W_KNIGHT: 'N',
    W_BISHOP: 'B',
    W_ROOK: 'R',
    W_QUEEN: 'Q',
    W_KING: 'K',
    B_PAWN: 'p',
    B_KNIGHT: 'n',
    B_BISHOP: 'b',
    B_ROOK: 'r',
    B_QUEEN: 'q',
    B_KING: 'k'
}

# Generate a list of all squares on the board in algebraic notation
squares_san = []
for rank in '12345678':
    for file in 'abcdefgh':
        squares_san.append(file + rank)

# Used for converting squares from algebraic notation to coordinates
square_to_coords = {}
for row, rank in enumerate('87654321'):
    for col, file in enumerate('abcdefgh'):
        square_to_coords[file + rank] = (col, row)

# Used for getting the bitboard for the rank of a square
rank_of = [None for _ in range(64)]
for sq in range(64):
    rank_num = sq >> 3
    if rank_num == 0:
        rank_of[sq] = RANK_1_BB
    elif rank_num == 1:
        rank_of[sq] = RANK_2_BB
    elif rank_num == 2:
        rank_of[sq] = RANK_3_BB
    elif rank_num == 3:
        rank_of[sq] = RANK_4_BB
    elif rank_num == 4:
        rank_of[sq] = RANK_5_BB
    elif rank_num == 5:
        rank_of[sq] = RANK_6_BB
    elif rank_num == 6:
        rank_of[sq] = RANK_7_BB
    elif rank_num == 7:
        rank_of[sq] = RANK_8_BB

# Used for getting the bitboard for the file of a square
file_of = [None for _ in range(64)]
for sq in range(64):
    file_num = sq & 7
    if file_num == 0:
        file_of[sq] = A_FILE_BB
    elif file_num == 1:
        file_of[sq] = B_FILE_BB
    elif file_num == 2:
        file_of[sq] = C_FILE_BB
    elif file_num == 3:
        file_of[sq] = D_FILE_BB
    elif file_num == 4:
        file_of[sq] = E_FILE_BB
    elif file_num == 5:
        file_of[sq] = F_FILE_BB
    elif file_num == 6:
        file_of[sq] = G_FILE_BB
    elif file_num == 7:
        file_of[sq] = H_FILE_BB

# Gets all the squares in front, indexed by square and colour
forward_ranks = [[0 for _ in range(64)] for _ in range(2)]
for s1 in range(64):
    s1_rank = s1 >> 3
    for s2 in range(64):
        s2_rank = s2 >> 3
        if s2_rank > s1_rank:
            forward_ranks[WHITE][s1] |= 1 << s2
        elif s2_rank < s1_rank:
            forward_ranks[BLACK][s1] |= 1 << s2

# Gets the bitboards for the files adjacent to the square used as index
adjacent_files = [None for _ in range(64)]
for sq in range(64):
    adjacent_files[sq] = 0
    if not (1 << sq) & A_FILE_BB:
        adjacent_files[sq] |= file_of[sq - 1]
    if not (1 << sq) & H_FILE_BB:
        adjacent_files[sq] |= file_of[sq + 1]

# Gets the bitboard for the squares between the two squares used as indices
bb_between = [[None for _ in range(64)] for _ in range(64)]
for sqr1 in range(64):
    for sqr2 in range(64):
        rook_n = ff.ratks_n(sqr1, 0) & ff.ratks_s(sqr2, 0)
        rook_s = ff.ratks_s(sqr1, 0) & ff.ratks_n(sqr2, 0)
        rook_e = ff.ratks_e(sqr1, 0) & ff.ratks_w(sqr2, 0)
        rook_w = ff.ratks_w(sqr1, 0) & ff.ratks_e(sqr2, 0)
        bishop_ne = ff.batks_ne(sqr1, 0) & ff.batks_sw(sqr2, 0)
        bishop_sw = ff.batks_sw(sqr1, 0) & ff.batks_ne(sqr2, 0)
        bishop_se = ff.batks_se(sqr1, 0) & ff.batks_nw(sqr2, 0)
        bishop_nw = ff.batks_nw(sqr1, 0) & ff.batks_se(sqr2, 0)
        bb_between[sqr1][
            sqr2] = rook_e | rook_w | rook_n | rook_s | bishop_ne | bishop_sw | bishop_se | bishop_nw  # noqa

# Gets the bitboard of squares with a given distance from another square
distance_ring = [[0 for _ in range(8)] for _ in range(64)]
for s1 in range(64):
    s1_rank = s1 >> 3
    s1_file = s1 & 7
    for s2 in range(64):
        if s1 != s2:
            s2_rank = s2 >> 3
            s2_file = s2 & 7
            distance = max(abs(s2_rank - s1_rank), abs(s2_file - s1_file))
            distance_ring[s1][distance] |= (1 << s2)

# Allows bitwise shift direction based on colour
pawn_shift = [None for _ in range(2)]
pawn_shift[WHITE] = operator.lshift
pawn_shift[BLACK] = operator.rshift

# Allows pawn push direction based on colour
pawn_push = [None for _ in range(2)]
pawn_push[WHITE] = NORTH
pawn_push[BLACK] = -NORTH

# Gets the bitboard of squares adjacent to the king, plus the squares
# two ranks in front for a king on its first rank
king_ring = [[None for _ in range(64)] for _ in range(2)]
for colour in range(2):
    for sq in range(64):
        king_ring[colour][sq] = pseudo_attacks[KING][sq]

        rank_num = sq >> 3
        file_num = sq & 7

        if rank_num ^ (colour * 7) == 0:
            king_ring[colour][sq] |= pseudo_attacks[KING][sq +
                                                          pawn_push[colour]]
        if file_num == 0:
            king_ring[colour][sq] |= pseudo_attacks[KING][sq + EAST]
        elif file_num == 7:
            king_ring[colour][sq] |= pseudo_attacks[KING][sq - EAST]


# Generates the indices of the set bits of a given bitboard
def gen_bitboard_indices(bb):
    while bb:
        yield bit_scan1(bb)
        bb &= bb - 1


# Flips a bitboard vertically
def flip_vertical(board):
    # Loop through the first half of the board, swapping each
    # bit with the bit on the opposite side of the board
    for sq in range(32):
        current_bit = bool(board & (1 << sq))
        flipped_bit = bool(board & (1 << (sq ^ 56)))
        board &= ~(1 << sq)
        board |= flipped_bit << sq
        board &= ~(1 << (sq ^ 56))
        board |= current_bit << (sq ^ 56)
    return board


# Returns all of the squares in front of the given
# bitboard from white's perspective
def forward_fill_white(bb):
    bb |= bb << 8
    bb |= bb << 8
    bb |= bb << 8
    bb |= bb << 8
    bb |= bb << 8
    bb |= bb << 8
    bb <<= 8
    return bb & 0xFFFFFFFFFFFFFFFF


# Returns all of the squares in front of the given
# bitboard from black's perspective
def forward_fill_black(bb):
    bb |= bb >> 8
    bb |= bb >> 8
    bb |= bb >> 8
    bb |= bb >> 8
    bb |= bb >> 8
    bb |= bb >> 8
    bb >>= 8
    return bb & 0xFFFFFFFFFFFFFFFF


# Allows access to the forward fill function by colour
forward_fill = [None for _ in range(2)]
forward_fill[WHITE] = forward_fill_white
forward_fill[BLACK] = forward_fill_black
