from variables import ACTION_SIZE
from move_conversion import action_to_move, move_to_action
import unittest


class TestMoveConversion(unittest.TestCase):
    def test_all_actions_map_correctly(self):
        moves = set()
        all_moves = set()
        repeats = 0
        for i in range(ACTION_SIZE):
            move = action_to_move(i)
            if move.piece == move.dest:
                repeats += 1
            if move not in moves:
                moves.add(move)
            all_moves.add((i, move))

        self.assertEqual(len(moves), 10125, "Number of unique moves should be 10125")
        self.assertEqual(repeats, 1296, "Number of repeats should be 1296")

        incorrect_mappings = 0
        for action, move in all_moves:
            a = move_to_action(move)
            if a != action:
                if move.piece != move.dest:
                    incorrect_mappings += 1

        self.assertEqual(
            incorrect_mappings, 0, "All moves should match their action value"
        )
