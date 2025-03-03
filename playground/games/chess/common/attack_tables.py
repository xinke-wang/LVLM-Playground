import playground.games.chess.common.flood_fill as ff
from playground.games.chess.common.consts import (_64BITS, BISHOP, BLACK, KING,
                                              KNIGHT, QUEEN, ROOK, WHITE)

# The set of squares for possible rook attack blocker pieces
rook_masks = [
    0x101010101017e, 0x202020202027c, 0x404040404047a, 0x8080808080876,
    0x1010101010106e, 0x2020202020205e, 0x4040404040403e, 0x8080808080807e,
    0x1010101017e00, 0x2020202027c00, 0x4040404047a00, 0x8080808087600,
    0x10101010106e00, 0x20202020205e00, 0x40404040403e00, 0x80808080807e00,
    0x10101017e0100, 0x20202027c0200, 0x40404047a0400, 0x8080808760800,
    0x101010106e1000, 0x202020205e2000, 0x404040403e4000, 0x808080807e8000,
    0x101017e010100, 0x202027c020200, 0x404047a040400, 0x8080876080800,
    0x1010106e101000, 0x2020205e202000, 0x4040403e404000, 0x8080807e808000,
    0x1017e01010100, 0x2027c02020200, 0x4047a04040400, 0x8087608080800,
    0x10106e10101000, 0x20205e20202000, 0x40403e40404000, 0x80807e80808000,
    0x17e0101010100, 0x27c0202020200, 0x47a0404040400, 0x8760808080800,
    0x106e1010101000, 0x205e2020202000, 0x403e4040404000, 0x807e8080808000,
    0x7e010101010100, 0x7c020202020200, 0x7a040404040400, 0x76080808080800,
    0x6e101010101000, 0x5e202020202000, 0x3e404040404000, 0x7e808080808000,
    0x7e01010101010100, 0x7c02020202020200, 0x7a04040404040400,
    0x7608080808080800, 0x6e10101010101000, 0x5e20202020202000,
    0x3e40404040404000, 0x7e80808080808000
]

# The set of squares for possible bishop attack blocker pieces
bishop_masks = [
    0x40201008040200, 0x402010080400, 0x4020100a00, 0x40221400, 0x2442800,
    0x204085000, 0x20408102000, 0x2040810204000, 0x20100804020000,
    0x40201008040000, 0x4020100a0000, 0x4022140000, 0x244280000, 0x20408500000,
    0x2040810200000, 0x4081020400000, 0x10080402000200, 0x20100804000400,
    0x4020100a000a00, 0x402214001400, 0x24428002800, 0x2040850005000,
    0x4081020002000, 0x8102040004000, 0x8040200020400, 0x10080400040800,
    0x20100a000a1000, 0x40221400142200, 0x2442800284400, 0x4085000500800,
    0x8102000201000, 0x10204000402000, 0x4020002040800, 0x8040004081000,
    0x100a000a102000, 0x22140014224000, 0x44280028440200, 0x8500050080400,
    0x10200020100800, 0x20400040201000, 0x2000204081000, 0x4000408102000,
    0xa000a10204000, 0x14001422400000, 0x28002844020000, 0x50005008040200,
    0x20002010080400, 0x40004020100800, 0x20408102000, 0x40810204000,
    0xa1020400000, 0x142240000000, 0x284402000000, 0x500804020000,
    0x201008040200, 0x402010080400, 0x2040810204000, 0x4081020400000,
    0xa102040000000, 0x14224000000000, 0x28440200000000, 0x50080402000000,
    0x20100804020000, 0x40201008040200
]

# Initialise table for rook attacks, indexed by square
ratk_table = [{} for _ in range(64)]
for sq in range(64):
    occ = 0
    # Produce attacks with occupancies of all subsets of rook mask
    while True:
        ratk_table[sq][occ] = ff.rook_attacks(sq, occ)
        occ = (occ - rook_masks[sq]) & rook_masks[sq]  # Carry-Rippler
        if not occ:
            break

# Initialise table for bishop attacks, indexed by square
batk_table = [{} for _ in range(64)]
for sq in range(64):
    occ = 0
    # Produce attacks with occupancies of all subsets of bishop mask
    while True:
        batk_table[sq][occ] = ff.bishop_attacks(sq, occ)
        occ = (occ - bishop_masks[sq]) & bishop_masks[sq]  # Carry-Rippler
        if not occ:
            break

# Initialise table for non-pawn attacks, indexed by piece type and square
pseudo_attacks = [[0 for _ in range(64)] for _ in range(7)]
for sq in range(64):
    bb = 1 << sq
    clip_a_file = bb & 0xFEFEFEFEFEFEFEFE
    clip_h_file = bb & 0x7F7F7F7F7F7F7F7F
    clip_ab_files = bb & 0xFCFCFCFCFCFCFCFC
    clip_gh_files = bb & 0X3F3F3F3F3F3F3F3F

    pseudo_attacks[KNIGHT][sq] |= clip_ab_files << 6
    pseudo_attacks[KNIGHT][sq] |= clip_gh_files << 10
    pseudo_attacks[KNIGHT][sq] |= clip_a_file << 15
    pseudo_attacks[KNIGHT][sq] |= clip_h_file << 17
    pseudo_attacks[KNIGHT][sq] |= clip_gh_files >> 6
    pseudo_attacks[KNIGHT][sq] |= clip_ab_files >> 10
    pseudo_attacks[KNIGHT][sq] |= clip_h_file >> 15
    pseudo_attacks[KNIGHT][sq] |= clip_a_file >> 17
    pseudo_attacks[KNIGHT][sq] &= _64BITS

    pseudo_attacks[BISHOP][sq] |= batk_table[sq][0]
    pseudo_attacks[ROOK][sq] |= ratk_table[sq][0]
    pseudo_attacks[QUEEN][sq] |= batk_table[sq][0] | ratk_table[sq][0]

    pseudo_attacks[KING][sq] |= clip_h_file << 1
    pseudo_attacks[KING][sq] |= clip_a_file << 7
    pseudo_attacks[KING][sq] |= bb << 8
    pseudo_attacks[KING][sq] |= clip_h_file << 9
    pseudo_attacks[KING][sq] |= clip_a_file >> 1
    pseudo_attacks[KING][sq] |= clip_h_file >> 7
    pseudo_attacks[KING][sq] |= bb >> 8
    pseudo_attacks[KING][sq] |= clip_a_file >> 9
    pseudo_attacks[KING][sq] &= _64BITS

# Initialise table for pawn attacks, indexed by colour and square
pawn_attacks = [[0 for _ in range(64)] for _ in range(2)]
for sq in range(64):
    bb = 1 << sq
    clip_a_file = bb & 0xFEFEFEFEFEFEFEFE
    clip_h_file = bb & 0x7F7F7F7F7F7F7F7F

    pawn_attacks[WHITE][sq] |= clip_a_file << 7
    pawn_attacks[WHITE][sq] |= clip_h_file << 9

    pawn_attacks[BLACK][sq] |= clip_h_file >> 7
    pawn_attacks[BLACK][sq] |= clip_a_file >> 9
