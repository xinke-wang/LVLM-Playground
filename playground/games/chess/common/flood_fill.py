# Returns rook attacks in the north direction
def ratks_n(sq, occ):
    sq = 1 << sq
    flood = sq
    sq = (sq << 8) & ~occ
    flood |= sq
    sq = (sq << 8) & ~occ
    flood |= sq
    sq = (sq << 8) & ~occ
    flood |= sq
    sq = (sq << 8) & ~occ
    flood |= sq
    sq = (sq << 8) & ~occ
    flood |= sq
    sq = (sq << 8) & ~occ
    flood |= sq
    sq = (sq << 8) & ~occ
    flood |= sq
    flood <<= 8
    return flood & 0xFFFFFFFFFFFFFFFF


# Returns rook attacks in the east direction
def ratks_e(sq, occ):
    occ |= 0x101010101010101
    sq = 1 << sq
    flood = sq
    sq = (sq << 1) & ~occ
    flood |= sq
    sq = (sq << 1) & ~occ
    flood |= sq
    sq = (sq << 1) & ~occ
    flood |= sq
    sq = (sq << 1) & ~occ
    flood |= sq
    sq = (sq << 1) & ~occ
    flood |= sq
    sq = (sq << 1) & ~occ
    flood |= sq
    sq = (sq << 1) & ~occ
    flood |= sq
    flood <<= 1
    flood &= ~0x101010101010101
    return flood & 0xFFFFFFFFFFFFFFFF


# Returns rook attacks in the south direction
def ratks_s(sq, occ):
    sq = 1 << sq
    flood = sq
    sq = (sq >> 8) & ~occ
    flood |= sq
    sq = (sq >> 8) & ~occ
    flood |= sq
    sq = (sq >> 8) & ~occ
    flood |= sq
    sq = (sq >> 8) & ~occ
    flood |= sq
    sq = (sq >> 8) & ~occ
    flood |= sq
    sq = (sq >> 8) & ~occ
    flood |= sq
    sq = (sq >> 8) & ~occ
    flood |= sq
    flood >>= 8
    return flood & 0xFFFFFFFFFFFFFFFF


# Returns rook attacks in the west direction
def ratks_w(sq, occ):
    occ |= 0x8080808080808080
    sq = 1 << sq
    flood = sq
    sq = (sq >> 1) & ~occ
    flood |= sq
    sq = (sq >> 1) & ~occ
    flood |= sq
    sq = (sq >> 1) & ~occ
    flood |= sq
    sq = (sq >> 1) & ~occ
    flood |= sq
    sq = (sq >> 1) & ~occ
    flood |= sq
    sq = (sq >> 1) & ~occ
    flood |= sq
    sq = (sq >> 1) & ~occ
    flood |= sq
    flood >>= 1
    flood &= ~0x8080808080808080
    return flood & 0xFFFFFFFFFFFFFFFF


# Returns bishop attacks in the north-east direction
def batks_ne(sq, occ):
    occ |= 0x101010101010101
    sq = 1 << sq
    flood = sq
    sq = (sq << 9) & ~occ
    flood |= sq
    sq = (sq << 9) & ~occ
    flood |= sq
    sq = (sq << 9) & ~occ
    flood |= sq
    sq = (sq << 9) & ~occ
    flood |= sq
    sq = (sq << 9) & ~occ
    flood |= sq
    sq = (sq << 9) & ~occ
    flood |= sq
    sq = (sq << 9) & ~occ
    flood |= sq
    flood <<= 9
    flood &= ~0x101010101010101
    return flood & 0xFFFFFFFFFFFFFFFF


# Returns bishop attacks in the south-east direction
def batks_se(sq, occ):
    occ |= 0x101010101010101
    sq = 1 << sq
    flood = sq
    sq = (sq >> 7) & ~occ
    flood |= sq
    sq = (sq >> 7) & ~occ
    flood |= sq
    sq = (sq >> 7) & ~occ
    flood |= sq
    sq = (sq >> 7) & ~occ
    flood |= sq
    sq = (sq >> 7) & ~occ
    flood |= sq
    sq = (sq >> 7) & ~occ
    flood |= sq
    sq = (sq >> 7) & ~occ
    flood |= sq
    flood >>= 7
    flood &= ~0x101010101010101
    return flood & 0xFFFFFFFFFFFFFFFF


# Returns bishop attacks in the south-west direction
def batks_sw(sq, occ):
    occ |= 0x8080808080808080
    sq = 1 << sq
    flood = sq
    sq = (sq >> 9) & ~occ
    flood |= sq
    sq = (sq >> 9) & ~occ
    flood |= sq
    sq = (sq >> 9) & ~occ
    flood |= sq
    sq = (sq >> 9) & ~occ
    flood |= sq
    sq = (sq >> 9) & ~occ
    flood |= sq
    sq = (sq >> 9) & ~occ
    flood |= sq
    sq = (sq >> 9) & ~occ
    flood |= sq
    flood >>= 9
    flood &= ~0x8080808080808080
    return flood & 0xFFFFFFFFFFFFFFFF


# Returns bishop attacks in the north-west direction
def batks_nw(sq, occ):
    occ |= 0x8080808080808080
    sq = 1 << sq
    flood = sq
    sq = (sq << 7) & ~occ
    flood |= sq
    sq = (sq << 7) & ~occ
    flood |= sq
    sq = (sq << 7) & ~occ
    flood |= sq
    sq = (sq << 7) & ~occ
    flood |= sq
    sq = (sq << 7) & ~occ
    flood |= sq
    sq = (sq << 7) & ~occ
    flood |= sq
    sq = (sq << 7) & ~occ
    flood |= sq
    flood <<= 7
    flood &= ~0x8080808080808080
    return flood & 0xFFFFFFFFFFFFFFFF


def rook_attacks(sq, occ):
    return ratks_n(sq, occ) | ratks_e(sq, occ) | ratks_s(sq, occ) | ratks_w(
        sq, occ)


def bishop_attacks(sq, occ):
    return batks_ne(sq, occ) | batks_se(sq, occ) | batks_sw(
        sq, occ) | batks_nw(sq, occ)
