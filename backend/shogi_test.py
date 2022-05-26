import unittest
from shogi_logic import *
import numpy as np


def print_moves(result):
    for move in result:
        print(move.dest)
        print(move.promote)


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
        self.check = self.pawn_board = np.array(
            [
                [-ROOK_ID] + 8 * [0],
                BOARD_SIZE * [0],
                BOARD_SIZE * [0],
                BOARD_SIZE * [0],
                BOARD_SIZE * [0],
                BOARD_SIZE * [0],
                BOARD_SIZE * [0],
                BOARD_SIZE * [0],
                [KING_ID] + 8 * [0],
            ]
        )
        self.check2 = np.copy(self.default_board)
        self.check2[6][4] = -ROOK_ID
        self.pawn_prom = np.array(
            [
                [-PAWN_ID] + 8 * [0],
                [PAWN_ID] + 8 * [0],
                BOARD_SIZE * [0],
                BOARD_SIZE * [0],
                BOARD_SIZE * [0],
                BOARD_SIZE * [0],
                BOARD_SIZE * [0],
                BOARD_SIZE * [0],
                BOARD_SIZE * [0],
            ]
        )

    def test_check_owned(self):
        self.assertTrue(check_owned(1, 1))
        self.assertTrue(check_owned(-1, -1))
        self.assertFalse(check_owned(1, -1))
        self.assertFalse(check_owned(-1, 1))

    def test_iterate_direction(self):
        pass

    def test_get_moves(self):
        # tests with standard starting position
        result = get_moves(self.default_board, BLACK, {})
        self.assertEqual(len(result), 30)

        # rotates starting position so white is starting
        result = get_moves(rotate_board(self.default_board), WHITE, {})
        self.assertEqual(len(result), 30)

        # testing pawn drops on empty board
        result = get_moves(self.empty_board, BLACK, {PAWN_ID: 1})
        self.assertEqual(len(result), 72)

        # first under check test (king and rook on board)
        result = get_moves(self.check, BLACK, {})
        self.assertEqual(len(result), 2)

        # second under check test (starting position with rook/king)
        result = get_moves(self.check2, BLACK, {})
        self.assertEqual(len(result), 5)

        # tests pawn force promotion
        result = get_moves(self.pawn_prom, BLACK, {})
        # print_moves(result)
        self.assertEqual(len(result), 1)


if __name__ == "__main__":
    unittest.main()
