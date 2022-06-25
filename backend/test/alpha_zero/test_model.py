import sys
import torch
import unittest

sys.path.append("./..")
# sys.path.append('../alpha_zero')
from shogi_game import ShogiGame
from alpha_zero.model import ResCNN
from variables import ACTION_SIZE


class TestNNModel(unittest.TestCase):
    def test_outputs(self):
        game = ShogiGame()

        nn = ResCNN(19)

        policy, v = nn(game.toTensor().expand(1, -1, -1, -1))

        self.assertEqual(policy.size(), (1, ACTION_SIZE))
        self.assertEqual(v.size(), (1, 1))

        policy, v = nn(torch.stack([ShogiGame().toTensor() for _ in range(5)]))

        self.assertEqual(policy.size(), (5, ACTION_SIZE))
        self.assertEqual(v.size(), (5, 1))
