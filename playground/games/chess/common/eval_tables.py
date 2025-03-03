from playground.games.chess.common.consts import (B_BISHOP, B_KING, B_KNIGHT,
                                              B_PAWN, B_QUEEN, B_ROOK, BISHOP,
                                              ENDGAME, KNIGHT, MIDGAME, QUEEN,
                                              ROOK, W_BISHOP, W_KING, W_KNIGHT,
                                              W_PAWN, W_QUEEN, W_ROOK)

# Piece-square table for white pawns
w_pawn_table = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),
                (0, -10), (-5, -3), (10, 7), (13, -1), (21, 7), (17, 6),
                (6, 1), (-3, -20), (-11, -6), (-10, -6), (15, -1), (22, -1),
                (26, -1), (28, 2), (4, -2), (-24, -5), (-9, 4), (-18, -5),
                (8, -4), (22, -5), (33, -6), (25, -13), (-4, -3), (-16, -7),
                (6, 18), (-3, 2), (-10, 2), (1, -9), (12, -13), (6, -8),
                (-12, 11), (1, 9), (-6, 25), (-8, 17), (5, 19), (11, 29),
                (-14, 29), (0, 8), (-12, 4), (-14, 12), (-10, -1), (6, -6),
                (-5, 18), (-11, 22), (-2, 22), (-14, 17), (12, 2), (-1, 9),
                (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]

# Piece-square table for white knights
w_knight_table = [(-169, -105), (-96, -74), (-80, -46), (-79, -18), (-79, -18),
                  (-80, -46), (-96, -74), (-169, -105), (-79, -70), (-39, -56),
                  (-24, -15), (-9, 6), (-9, 6), (-24, -15), (-39, -56),
                  (-79, -70), (-64, -38), (-20, -33), (4, -5), (19, 27),
                  (19, 27), (4, -5), (-20, -33), (-64, -38),
                  (-28, -36), (5, 0), (41, 13), (47, 34), (47, 34), (41, 13),
                  (5, 0), (-28, -36), (-29, -41), (13, -20), (42, 4), (52, 35),
                  (52, 35), (42, 4), (13, -20), (-29, -41), (-11, -51),
                  (28, -38), (63, -17), (55, 19), (55, 19), (63, -17),
                  (28, -38), (-11, -51), (-67, -64), (-21, -45), (6, -37),
                  (37, 16), (37, 16), (6, -37), (-21, -45), (-67, -64),
                  (-200, -98), (-80, -89), (-53, -53), (-32, -16), (-32, -16),
                  (-53, -53), (-80, -89), (-200, -98)]

# Piece-square table for white bishops
w_bishop_table = [(-44, -63), (-4, -30), (-11, -35), (-28, -8), (-28, -8),
                  (-11, -35), (-4, -30), (-44, -63), (-18, -38), (7, -13),
                  (14, -14), (3, 0), (3, 0), (14, -14), (7, -13), (-18, -38),
                  (-8, -18), (24, 0), (-3, -7), (15, 13), (15, 13), (-3, -7),
                  (24, 0), (-8, -18), (1, -26), (8, -3), (26, 1), (37, 16),
                  (37, 16), (26, 1), (8, -3), (1, -26), (-7, -24), (30, -6),
                  (23, -10), (28, 17), (28, 17), (23, -10),
                  (30, -6), (-7, -24), (-17, -26), (4, 2), (-1, 1), (8, 16),
                  (8, 16), (-1, 1), (4, 2), (-17, -26), (-21, -34), (-19, -18),
                  (10, -7), (-6, 9), (-6, 9), (10, -7), (-19, -18), (-21, -34),
                  (-48, -51), (-3, -40), (-12, -39), (-25, -20), (-25, -20),
                  (-12, -39), (-3, -40), (-48, -51)]

# Piece-square table for white rooks
w_rook_table = [(-24, -2), (-13, -6), (-7, -3), (2, -2), (2, -2), (-7, -3),
                (-13, -6), (-24, -2), (-18, -10), (-10, -7), (-5, 1), (9, 0),
                (9, 0), (-5, 1), (-10, -7), (-18, -10), (-21, 10), (-7, -4),
                (3, 2), (-1, -2), (-1, -2), (3, 2), (-7, -4), (-21, 10),
                (-13, -5), (-5, 2), (-4, -8), (-6, 8), (-6, 8), (-4, -8),
                (-5, 2), (-13, -5), (-24, -8), (-12, 5), (-1, 4), (6, -9),
                (6, -9), (-1, 4), (-12, 5), (-24, -8), (-24, 3), (-4, -2),
                (4, -10), (10, 7), (10, 7), (4, -10), (-4, -2), (-24, 3),
                (-8, 1), (6, 2), (10, 17), (12, -8), (12, -8),
                (10, 17), (6, 2), (-8, 1), (-22, 12), (-24, -6), (-6, 13),
                (4, 7), (4, 7), (-6, 13), (-24, -6), (-22, 12)]

# Piece-square table for white queens
w_queen_table = [(3, -69), (-5, -57), (-5, -47), (4, -26), (4, -26), (-5, -47),
                 (-5, -57), (3, -69), (-3, -55), (5, -31), (8, -22), (12, -4),
                 (12, -4), (8, -22), (5, -31), (-3, -55), (-3, -39), (6, -18),
                 (13, -9), (7, 3), (7, 3), (13, -9), (6, -18), (-3, -39),
                 (4, -23), (5, -3), (9, 13), (8, 24),
                 (8, 24), (9, 13), (5, -3), (4, -23), (0, -29), (14, -6),
                 (12, 9), (5, 21), (5, 21), (12, 9), (14, -6), (0, -29),
                 (-4, -38), (10, -18), (6, -12), (8, 1), (8, 1), (6, -12),
                 (10, -18), (-4, -38), (-5, -50), (6, -27), (10, -24), (8, -8),
                 (8, -8), (10, -24), (6, -27), (-5, -50), (-2, -75), (-2, -52),
                 (1, -43), (-2, -36), (-2, -36), (1, -43), (-2, -52),
                 (-2, -75)]

# Piece-square table for white kings
w_king_table = [(272, 0), (325, 41), (273, 80), (190, 93), (190, 93), (273,
                                                                       80),
                (325, 41), (272, 0), (277, 57), (305, 98), (241, 138),
                (183, 131), (183, 131), (241, 138), (305, 98), (277, 57),
                (198, 86), (253, 138), (168, 165), (120, 173), (120, 173),
                (168, 165), (253, 138), (198, 86), (169, 103), (191, 152),
                (136, 168), (108, 169), (108, 169), (136, 168), (191, 152),
                (169, 103), (145, 98), (176, 166), (112, 197), (69, 194),
                (69, 194), (112, 197), (176, 166), (145, 98), (122, 87),
                (159, 164), (85, 174), (36, 189), (36, 189), (85, 174),
                (159, 164), (122, 87), (87, 40), (120, 99), (64, 128),
                (25, 141), (25, 141), (64, 128), (120, 99), (87, 40), (64, 5),
                (87, 60), (49, 75), (0, 75), (0, 75), (49, 75), (87, 60),
                (64, 5)]

# Generate piece-square tables for black pieces with squares vertically flipped
b_pawn_table = [None for _ in range(64)]
b_knight_table = [None for _ in range(64)]
b_bishop_table = [None for _ in range(64)]
b_rook_table = [None for _ in range(64)]
b_queen_table = [None for _ in range(64)]
b_king_table = [None for _ in range(64)]
for sq in range(64):
    b_pawn_table[sq] = (w_pawn_table[sq ^ 56][MIDGAME],
                        w_pawn_table[sq ^ 56][ENDGAME])
    b_knight_table[sq] = (w_knight_table[sq ^ 56][MIDGAME],
                          w_knight_table[sq ^ 56][ENDGAME])
    b_bishop_table[sq] = (w_bishop_table[sq ^ 56][MIDGAME],
                          w_bishop_table[sq ^ 56][ENDGAME])
    b_rook_table[sq] = (w_rook_table[sq ^ 56][MIDGAME],
                        w_rook_table[sq ^ 56][ENDGAME])
    b_queen_table[sq] = (w_queen_table[sq ^ 56][MIDGAME],
                         w_queen_table[sq ^ 56][ENDGAME])
    b_king_table[sq] = (w_king_table[sq ^ 56][MIDGAME],
                        w_king_table[sq ^ 56][ENDGAME])

# Combine piece-square tables into one list, indexed by piece
psq_table = [None for _ in range(15)]
psq_table[W_PAWN] = w_pawn_table
psq_table[W_KNIGHT] = w_knight_table
psq_table[W_BISHOP] = w_bishop_table
psq_table[W_ROOK] = w_rook_table
psq_table[W_QUEEN] = w_queen_table
psq_table[W_KING] = w_king_table
psq_table[B_PAWN] = b_pawn_table
psq_table[B_KNIGHT] = b_knight_table
psq_table[B_BISHOP] = b_bishop_table
psq_table[B_ROOK] = b_rook_table
psq_table[B_QUEEN] = b_queen_table
psq_table[B_KING] = b_king_table

# Material imbalance scores for the player's pieces
player_imbalance = [[1438], [40, 38], [32, 255, -62], [0, 104, 4, 0],
                    [-26, -2, 47, 105, -208], [-189, 24, 117, 133, -134, -6]]

# Material imbalance scores for the enemy's pieces
enemy_imbalance = [[0], [36, 0], [9, 63, 0], [59, 65, 42, 0],
                   [46, 39, 24, -24, 0], [97, 100, -42, 137, 268, 0]]

# Mobility scores for knights
knight_mobility = [(-62, -81), (-53, -56), (-12, -30), (-4, -14), (3, 8),
                   (13, 15), (22, 23), (28, 27), (33, 33)]

# Mobility scores for bishops
bishop_mobility = [(-48, -59), (-20, -23), (16, -3), (26, 13), (38, 24),
                   (51, 42), (55, 54), (63, 57), (63, 65), (68, 73), (81, 78),
                   (81, 86), (91, 88), (98, 97)]

# Mobility scores for rooks
rook_mobility = [(-58, -76), (-27, -18), (-15, 28), (-10, 55), (-5, 69),
                 (-2, 82), (9, 112), (16, 118), (30, 132), (29, 142),
                 (32, 155), (38, 165), (46, 166), (48, 169), (58, 171)]

# Mobility scores for queens
queen_mobility = [(-39, -36), (-21, -15), (3, 8), (3, 18), (14, 34), (22, 54),
                  (28, 61), (41, 73), (43, 79), (48, 92), (56, 94), (60, 104),
                  (60, 113), (66, 120), (67, 123), (70, 126), (71, 133),
                  (73, 136), (79, 140), (88, 143), (88, 148), (99, 166),
                  (102, 170), (102, 175), (106, 184), (109, 191), (113, 206),
                  (116, 212)]

# Combine mobility tables into one list, indexed by piece type
mobility = [None for _ in range(7)]
mobility[KNIGHT] = knight_mobility
mobility[BISHOP] = bishop_mobility
mobility[ROOK] = rook_mobility
mobility[QUEEN] = queen_mobility

# Scores for strength of pawn shelter
shelter_strength = [[-6, 81, 93, 58, 39, 18, 25],
                    [-43, 61, 35, -49, -29, -11, -63],
                    [-10, 75, 23, -2, 32, 3, -45],
                    [-39, -13, -29, -52, -48, -67, -166]]

# Scores for strength of pawn storm
unblocked_storm = [[89, 107, 123, 93, 57, 45, 51],
                   [44, -18, 123, 46, 39, -7,
                    23], [4, 52, 162, 37, 7, -14, -2],
                   [-10, -14, 90, 15, 2, -7, -16]]

# Generate scores for pawn structure
connected_bonus = [[[[[None, None] for rank_num in range(8)]
                     for defenders in range(3)] for phalanx in range(2)]
                   for opposed in range(2)]
seed = [0, 13, 24, 18, 65, 100, 175, 330]
for opposed in range(2):
    for aligned in range(2):
        for defenders in range(3):
            for rank_num in range(1, 7):
                v = 17 * defenders
                if aligned:
                    v += (seed[rank_num] + (
                        (seed[rank_num + 1] - seed[rank_num]) // 2)) >> opposed
                else:
                    v += seed[rank_num] >> opposed
                connected_bonus[opposed][aligned][defenders][rank_num][
                    MIDGAME] = v
                connected_bonus[opposed][aligned][defenders][rank_num][
                    ENDGAME] = (v * (rank_num - 2)) // 4
