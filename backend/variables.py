import numpy as np

BOARD_SIZE = 9

EMPTY_SQUARE_ID = 0
KING_ID = 1
GOLD_GEN_ID = 2
ROOK_ID = 3
BISHOP_ID = 4
SILVER_GEN_ID = 5
LANCE_ID = 6
KNIGHT_ID = 7
PAWN_ID = 8
PROM_ROOK_ID = 9
PROM_BISH_ID = 10
# all have gold general movement - get rid of these?
PROM_SILG_ID = 11
PROM_LANCE_ID = 12
PROM_KNIGHT_ID = 13
PROM_PAWN_ID = 14

PROMOTE_CONSTANT = 6

# don't need to rotate flip these
ROOK_MOVES = [(-1, 0), (0, 1), (1, 0), (0, -1)]
BISHOP_MOVES = [(-1, 1), (1, 1), (1, -1), (-1, -1)]
KING_MOVES = ROOK_MOVES + BISHOP_MOVES

# variants for each player
# version 2 of moveset is obsolete if we flip the board
LANCE_MOVES = [(-1, 0)]
LANCE_MOVES_2 = [(1, 0)]
GOLD_GEN_MOVES = ROOK_MOVES + [(-1, -1), (-1, 1)]
GOLD_GEN_MOVES_2 = ROOK_MOVES + [(1, -1), (1, 1)]
SILVER_GEN_MOVES = BISHOP_MOVES + LANCE_MOVES
SILVER_GEN_MOVES_2 = BISHOP_MOVES + LANCE_MOVES_2
KNIGHT_MOVES = [(-2, -1), (-2, 1)]
KNIGHT_MOVES_2 = [(2, -1), (2, 1)]
PAWN_MOVES = LANCE_MOVES
PAWN_MOVES_2 = LANCE_MOVES_2

DEFAULT_BOARD = np.array(
    [
        [
            -LANCE_ID,
            -KNIGHT_ID,
            -SILVER_GEN_ID,
            -GOLD_GEN_ID,
            -KING_ID,
            -GOLD_GEN_ID,
            -SILVER_GEN_ID,
            -KNIGHT_ID,
            -LANCE_ID,
        ],
        [EMPTY_SQUARE_ID, -ROOK_ID]
        + [EMPTY_SQUARE_ID] * 5
        + [-BISHOP_ID, EMPTY_SQUARE_ID],
        [-PAWN_ID] * 9,
        [EMPTY_SQUARE_ID] * 9,
        [EMPTY_SQUARE_ID] * 9,
        [EMPTY_SQUARE_ID] * 9,
        [PAWN_ID] * 9,
        [EMPTY_SQUARE_ID, BISHOP_ID]
        + [EMPTY_SQUARE_ID] * 5
        + [ROOK_ID, EMPTY_SQUARE_ID],
        [
            LANCE_ID,
            KNIGHT_ID,
            SILVER_GEN_ID,
            GOLD_GEN_ID,
            KING_ID,
            GOLD_GEN_ID,
            SILVER_GEN_ID,
            KNIGHT_ID,
            LANCE_ID,
        ],
    ]
)

BLACK = 1
WHITE = -1

CAPTURED_DICT = {
    PAWN_ID: 0,
    BISHOP_ID: 0,
    ROOK_ID: 0,
    GOLD_GEN_ID: 0,
    SILVER_GEN_ID: 0,
    LANCE_ID: 0,
    KNIGHT_ID: 0,
}

ACTION_SIZE = 11259

PROMOTE_RANK = 2
