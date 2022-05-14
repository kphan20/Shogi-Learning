import unittest
from shogi_logic import *
import numpy as np


class TestShogiMethods(unittest.TestCase):
    def setUp(self):
        self.pawn_board = np.array(
            [
                [-PAWN_ID] + 8 * [0],
                BOARD_SIZE * [0],
                BOARD_SIZE * [0],
                BOARD_SIZE * [0],
                BOARD_SIZE * [0],
                BOARD_SIZE * [0],
                BOARD_SIZE * [0],
                BOARD_SIZE * [0],
                [PAWN_ID] + 8 * [0],
            ]
        )
        self.default_board = DEFAULT_BOARD
        self.empty_board = np.zeros((BOARD_SIZE, BOARD_SIZE))

    def test_check_owned(self):
        self.assertTrue(check_owned(1, 1))
        self.assertTrue(check_owned(-1, -1))
        self.assertFalse(check_owned(1, -1))
        self.assertFalse(check_owned(-1, 1))

    def test_iterate_direction(self):
        pass

    def test_get_moves(self):
        result = get_moves(self.default_board, 1, {})
        self.assertEqual(len(result), 30)
        result = get_moves(rotate_board(self.default_board), -1, {})
        self.assertEqual(len(result), 30)
        result = get_moves(self.empty_board, 1, {PAWN_ID: 1})
        # pieces = {}
        # for move in result:
        #     row, col = move.piece
        #     print(move.dest)
        #     print(move.promote)
        #     piece_id = self.empty_board[row][col]
        #     if pieces.get(piece_id):
        #         pieces[piece_id] += 1
        #     else:
        #         pieces[piece_id] = 1
        #     if piece_id == -SILVER_GEN_ID:
        #         print(move.dest)
        # print(pieces)
        # print(self.empty_board)
        self.assertEqual(len(result), 72)


if __name__ == "__main__":
    unittest.main()
