from collections import namedtuple
from functools import reduce
from itertools import chain, combinations
from random import getrandbits

_64BITS = 0xFFFFFFFFFFFFFFFF

WHITE = 0
BLACK = 1

PIECE_CONVERSION = {
    1: 'P',  # 白兵
    2: 'N',  # 白马
    3: 'B',  # 白象
    4: 'R',  # 白车
    5: 'Q',  # 白后
    6: 'K',  # 白王
    9: 'p',  # 黑兵
    10: 'n',  # 黑马
    11: 'b',  # 黑象
    12: 'r',  # 黑车
    13: 'q',  # 黑后
    14: 'k'  # 黑王
}

PIECE_MAP = {
    'P': 'wp',  # 白兵
    'N': 'wn',  # 白马
    'B': 'wb',  # 白象
    'R': 'wr',  # 白车
    'Q': 'wq',  # 白后
    'K': 'wk',  # 白王
    'p': 'bp',  # 黑兵
    'n': 'bn',  # 黑马
    'b': 'bb',  # 黑象
    'r': 'br',  # 黑车
    'q': 'bq',  # 黑后
    'k': 'bk'  # 黑王
}

RANKS = (RANK_1, RANK_2, RANK_3, RANK_4, RANK_5, RANK_6, RANK_7,
         RANK_8) = range(8)

FILES = (A_FILE, B_FILE, C_FILE, D_FILE, E_FILE, F_FILE, G_FILE,
         H_FILE) = range(8)

RANK_1_BB = 0xFF
RANK_2_BB = RANK_1_BB << 8
RANK_3_BB = RANK_2_BB << 8
RANK_4_BB = RANK_3_BB << 8
RANK_5_BB = RANK_4_BB << 8
RANK_6_BB = RANK_5_BB << 8
RANK_7_BB = RANK_6_BB << 8
RANK_8_BB = RANK_7_BB << 8

A_FILE_BB = 0x101010101010101
B_FILE_BB = A_FILE_BB << 1
C_FILE_BB = B_FILE_BB << 1
D_FILE_BB = C_FILE_BB << 1
E_FILE_BB = D_FILE_BB << 1
F_FILE_BB = E_FILE_BB << 1
G_FILE_BB = F_FILE_BB << 1
H_FILE_BB = G_FILE_BB << 1

COLOURS = (WHITE, BLACK) = range(2)

ALL_PIECES = 0
PIECE_TYPES = (PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING) = range(1, 7)

# First two bits used for piece type, third bit used for colour
NO_PIECE = 0
PIECES = (W_PAWN, W_KNIGHT, W_BISHOP, W_ROOK, W_QUEEN, W_KING, B_PAWN,
          B_KNIGHT, B_BISHOP, B_ROOK, B_QUEEN,
          B_KING) = list(chain(range(1, 7), range(9, 15)))

# Shift amounts for each direction (other directions obtained by negation)
EAST = 1
NORTHWEST = 7
NORTH = 8
NORTHEAST = 9

MIDGAME = 0
ENDGAME = 1

MATERIAL = [None for _ in range(15)]
MATERIAL[NO_PIECE] = (0, 0)
MATERIAL[PAWN] = (128, 213)
MATERIAL[KNIGHT] = (782, 865)
MATERIAL[BISHOP] = (830, 918)
MATERIAL[ROOK] = (1289, 1378)
MATERIAL[QUEEN] = (2529, 2687)
MATERIAL[KING] = (20000, 20000)

# Penalty for doubled pawns
DOUBLED = (11, 56)

# Penalty for isolated pawns
ISOLATED = (5, 15)

# Penalty for backward pawns
BACKWARD = (9, 24)

MATE = 100000
DRAW = 0
FUTILITY_MARGIN = 400

# Not using math.inf, as 'INFINITY + 1' is sometimes needed
INFINITY = 1000000

# Castling sides
KINGSIDE = 1
QUEENSIDE = 1 << 2

# Castling types
NO_CASTLING = 0
CASTLING_RIGHTS = (W_KINGSIDE, B_KINGSIDE, W_QUEENSIDE, B_QUEENSIDE) = list(
    (1 << i for i in range(4)))

# Move generation types
ALL = 0
QUIETS = 1
CAPTURES = 2
EVASIONS = 3

# Move types
NORMAL = 0
PROMOTION = 1 << 14
EN_PASSANT = 2 << 14
CASTLING = 3 << 14

# Promotion types
KNIGHT_PROMOTION = (KNIGHT - 2) << 12
BISHOP_PROMOTION = (BISHOP - 2) << 12
ROOK_PROMOTION = (ROOK - 2) << 12
QUEEN_PROMOTION = (QUEEN - 2) << 12

# Transposition table entry types
LOWER = 0
UPPER = 1
EXACT = 2

MoveDetailed = namedtuple('MoveDetailed', 'move captured')

StateInfo = namedtuple('StateInfo',
                       'zobrist en_passant castling_rights halfmove_clock')

TTEntry = namedtuple('TTEntry', 'zobrist move depth score type')
ZobristTuple = namedtuple('Zobrist', 'board en_passant castling colour')

PawnEntry = namedtuple('PawnEntry', 'key score_mg score_eg')

MaterialEntry = namedtuple('MaterialEntry', 'key material_score imbalance')

# Random 64-bit integer for each combination of square and piece
ZOBRIST_BOARD = [[None for _ in range(64)] for _ in range(16)]
for piece in PIECES:
    for sq in range(64):
        ZOBRIST_BOARD[piece][sq] = getrandbits(64)

# Random 64-bit integer for each en-passant file
ZOBRIST_ENPASSANT = [None for _ in range(8)]
for file_num in range(8):
    ZOBRIST_ENPASSANT[file_num] = getrandbits(64)

# Random 64-bit integer for each combination of castling rights
ZOBRIST_CASTLING = [0 for _ in range(16)]
# Individual castling rights
for cr in CASTLING_RIGHTS:
    ZOBRIST_CASTLING[cr] = getrandbits(64)
# Combinations of castling rights
for length in range(2, 5):
    combos = combinations(CASTLING_RIGHTS, length)
    for combo in combos:
        index = reduce(lambda x, y: x | y, combo)
        for cr in combo:
            ZOBRIST_CASTLING[index] ^= cr

ZOBRIST_COLOUR = getrandbits(64)
