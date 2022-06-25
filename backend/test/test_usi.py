import unittest
from usi import fen_to_game, game_to_fen
from shogi_game import ShogiGame


class TestUSILogic(unittest.TestCase):
    def test_starting_position(self):
        fen_starting = "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1"
        game = fen_to_game(fen_starting)
        self.assertEqual(
            fen_starting,
            game_to_fen(game) + " 1",
            "Conversion back to fen should match",
        )
        self.assertEqual(
            game.toString().replace(".", ""),
            ShogiGame().toString(),
            "Default board should be the same",
        )

    def test_random_position(self):
        fen_example = "8l/1l+R2P3/p2pBG1pp/kps1p4/Nn1P2G2/P1P1P2PP/1PS6/1KSG3+r1/LN2+p3L w Sbgn3p 124"
        game = fen_to_game(fen_example)
        self.assertEqual(
            fen_example,
            game_to_fen(game) + " 124",
            "Conversion back to fen should match",
        )
