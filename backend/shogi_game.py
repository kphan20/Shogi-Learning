from __future__ import annotations
import torch
from variables import (
    BLACK,
    CAPTURED_DICT,
    WHITE,
    DEFAULT_BOARD,
    ACTION_SIZE,
    KING_ID,
    PROM_PAWN_ID,
    GOLD_GEN_ID,
    PAWN_ID,
)
import numpy as np
from shogi_logic import get_moves, move_to_board, rotate_board
from move_conversion import move_to_action, action_to_move
from numpy.typing import NDArray


class ShogiGame:
    def __init__(
        self,
        captured_pieces={BLACK: dict(CAPTURED_DICT), WHITE: dict(CAPTURED_DICT)},
        board=np.array(DEFAULT_BOARD),
        current_player=BLACK,
        prev_state=None,
    ):
        # initializing captured pieces
        self.captured_pieces = captured_pieces
        self.board = board
        self.current_player = current_player
        self.prev_state = prev_state
        if not prev_state:
            self.prev_state = self

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
            offset = move_to_action(move)
            valids[int(offset)] = 1
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
        move = action_to_move(a)
        self.captured_pieces[self.current_player][move.piece[1]] -= 1
        if self.captured_pieces[self.current_player][move.piece[1]] < 0:
            raise ValueError("Invalid drop move.")
        # executes move
        new_board = move_to_board(self.board, self.current_player, move)
        return ShogiGame(
            self.captured_pieces, rotate_board(new_board), -self.current_player
        )

    # maybe find better alternative
    def toString(self):
        data = dict(self.__dict__)
        del data["prev_state"]
        return str(data)

    def toTensor(self):
        layers = []
        piece_iter = range(KING_ID, PROM_PAWN_ID + 1)
        prev = self.prev_state
        self._toTensor(
            piece_iter, layers, prev.board, prev.current_player, prev.captured_pieces
        )
        board = self.board
        player = self.current_player
        caps = self.captured_pieces
        self._toTensor(piece_iter, layers, board, player, caps)
        return torch.stack(layers)

    def _toTensor(
        self,
        piece_iter: range,
        layers: list,
        board: NDArray,
        player: int,
        captured_pieces: dict,
    ):
        for piece in piece_iter:
            layers.append(torch.from_numpy(np.where(board == player * piece, 1, 0)))
        for piece in piece_iter:
            layers.append(torch.from_numpy(np.where(board == -player * piece, 1, 0)))
        caps = captured_pieces[player]
        for piece in range(GOLD_GEN_ID, PAWN_ID + 1):
            layers.append(torch.full((9, 9), caps[piece]))
        caps = captured_pieces[-player]
        for piece in range(GOLD_GEN_ID, PAWN_ID + 1):
            layers.append(torch.full((9, 9), caps[piece]))
        layers.append(torch.full((9, 9), (player + 1) / 2))
