from shogi_logic import Move
from variables import BOARD_SIZE

# possible number of moves starting from each square
PLANE_SIZE = 139

# offset for drop moves
DROP_OFFSET = 132

# offset for promotion moves
KNIGHT_PROM_OFFSET = 2
QUEEN_PROM_OFFSET = 64

KNIGHT_OFFSET = 0
QUEEN_OFFSET = 4

# offsets for queen moves
W_OFFSET = 0
E_OFFSET = 8
S_OFFSET = 16
SE_OFFSET = 24
SW_OFFSET = 32
NW_OFFSET = 40
NE_OFFSET = 48
N_OFFSET = 56


def move_to_action(move: Move):
    offset = PLANE_SIZE * (BOARD_SIZE * move.piece[0] + move.piece[1])
    # handles drop moves
    if move.piece[0] == -1:
        offset = PLANE_SIZE * (BOARD_SIZE * move.dest[0] + move.dest[1])
        offset += DROP_OFFSET + move.piece[1] - 2
    else:
        x_diff = move.dest[0] - move.piece[0]
        y_diff = move.dest[1] - move.piece[1]
        # handles knight moves
        if x_diff == -2 and (y_diff + 1) % 2 == 0:
            offset += (
                KNIGHT_OFFSET + (y_diff + 1) / 2 + move.promote * KNIGHT_PROM_OFFSET
            )
        # queen moves
        else:
            offset += QUEEN_OFFSET + move.promote * QUEEN_PROM_OFFSET
            if x_diff == 0:
                if y_diff < 0:
                    offset += W_OFFSET + -y_diff
                else:
                    offset += E_OFFSET + y_diff
            elif x_diff > 0:
                if y_diff == 0:
                    offset += S_OFFSET + x_diff
                elif y_diff < 0:
                    offset += SW_OFFSET + x_diff
                else:
                    offset += SE_OFFSET + x_diff
            else:
                if y_diff == 0:
                    offset += N_OFFSET + -x_diff
                elif y_diff < 0:
                    offset += NW_OFFSET + -x_diff
                else:
                    offset += NE_OFFSET + y_diff
    return offset


def action_to_move(a):
    # for each square in a row, there are PLANE_SIZE possible moves
    row_offset = PLANE_SIZE * BOARD_SIZE

    # gets the start square of the move
    start_x = a // row_offset
    start_y = (a % row_offset) // PLANE_SIZE

    # gets the type of move
    offset = (a % row_offset) % PLANE_SIZE

    # implementation inspired by AlphaZero paper
    # case where move is a drop
    if offset >= DROP_OFFSET:
        dest = (start_x, start_y)
        start_x, start_y = -1, offset - DROP_OFFSET + 2
        prom = False
        # removes dropped piece from hand
        # self.captured_pieces[self.current_player][dest[1]] -= 1
    # handles chess queen-like movement
    elif offset >= QUEEN_OFFSET:
        offset -= QUEEN_OFFSET
        prom = offset >= QUEEN_PROM_OFFSET
        offset %= QUEEN_PROM_OFFSET
        dist = offset % 8
        if offset >= N_OFFSET:
            dest = (start_x - dist, start_y)
        elif offset >= NE_OFFSET:
            dest = (start_x - dist, start_y + dist)
        elif offset >= NW_OFFSET:
            dest = (start_x - dist, start_y - dist)
        elif offset >= SW_OFFSET:
            dest = (start_x + dist, start_y - dist)
        elif offset >= SE_OFFSET:
            dest = (start_x + dist, start_y + dist)
        elif offset >= S_OFFSET:
            dest = (start_x + dist, start_y)
        elif offset >= E_OFFSET:
            dest = (start_x, start_y + dist)
        else:
            dest = (start_x, start_y - dist)
    # handles knight moves
    else:
        dest = (start_x - 2, start_y + (offset % 2 * 2 - 1))
        prom = offset >= KNIGHT_PROM_OFFSET
    return Move((start_x, start_y), dest, prom)
