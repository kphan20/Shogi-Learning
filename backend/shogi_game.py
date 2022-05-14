from variables import *
import numpy as np
from shogi_logic import *
from numpy.typing import NDArray
from __future__ import annotations

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


class ShogiGame:
    def __init__(
        self,
        captured_pieces={BLACK: dict(CAPTURED_DICT), WHITE: dict(CAPTURED_DICT)},
        board=DEFAULT_BOARD,
        current_player=BLACK,
    ):
        # initializing captured pieces
        self.captured_pieces = captured_pieces
        self.board = board
        self.current_player = current_player

    def getGameEnded(self) -> bool:
        """
        Returns current status of game (in play, draw, loss)

        Returns:
            bool: currently returns whether game has been lost or not
        """
        # need to also check for draws - don't understand draw rules yet though
        player = self.current_player
        return len(get_moves(self.board, player, self.captured_pieces[player])) == 0

    def getValidMoves(self) -> NDArray:
        """
        Given the valid moves in a position, returns the one-hot vector
        that indicate the valid moves

        How moves are encoded into vector:
        Starting square offset = PLANE_SIZE * BOARD_SIZE * start rank + PLANE_SIZE * start file
        Move offset is determined by constants defined above
        Total offset = Starting square offset + Move offset

        Returns:
            NDArray: one-hot vector wit valid moves
        """
        player = self.current_player
        # current player perspective
        moves = get_moves(self.board, player, self.captured_pieces[player])

        # lots of constants to save from this logic
        valids = np.zeros(ACTION_SIZE)

        # this all assumes that the board is from the perspective of the
        # current player
        for move in moves:
            offset = PLANE_SIZE * (BOARD_SIZE * move.piece[0] + move.piece[1])
            # handles drop moves
            if move.dest[0] == -1:
                offset += DROP_OFFSET + move.dest[1] - 2
            else:
                x_diff = move.dest[0] - move.piece[0]
                y_diff = move.dest[1] - move.piece[1]
                # handles knight moves
                if x_diff == -2 and (y_diff + 1) % 2 == 0:
                    offset += (
                        KNIGHT_OFFSET
                        + (y_diff + 1) / 2
                        + move.promote * KNIGHT_PROM_OFFSET
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
            valids[offset] = 1
        return valids

    # assuming that a is from perspective of current player
    # also assumes valid move
    def getNextState(self, a: int) -> ShogiGame:
        """
        After executing move a, execute move
        and return next game state

        Args:
            a (int): index in valid move vector

        Returns:
            ShogiGame: state of game after move a
        """
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
            dest = (-1, offset - DROP_OFFSET + 2)
            prom = False
            # removes dropped piece from hand
            self.captured_pieces[self.current_player][dest[1]] -= 1
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
            dest = (start_x - 2, start_y + (a % 2 * 2 - 1))
            prom = offset >= KNIGHT_PROM_OFFSET

        # executes move
        new_board = move_to_board(
            self.board, self.current_player, Move((start_x, start_y), dest, prom)
        )
        return ShogiGame(
            self.captured_pieces, rotate_board(new_board), -self.current_player
        )

    # maybe find better alternative
    def toString(self):
        return str(self.__dict__)
