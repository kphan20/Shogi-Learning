import math
from shogi_game import ShogiGame
import numpy as np
from variables import *

# Heavily inspired by https://github.com/suragnair/alpha-zero-general/blob/master/MCTS.py
class MCTS:
    def __init__(self, game, nnet, q=[], n=[], c_puct=0.2):
        self.game = game
        self.nnet = nnet
        self.q = q
        self.n = n
        # controls level of exploration
        self.c_puct = c_puct

        self.Qsa = {}  # Q table
        self.Nsa = {}  # times s,a is visited
        self.Ns = {}  # stores times s is visited
        self.Ps = {}  # initial policy priors

        self.Es = {}  # stores if game ended
        self.Vs = {}  # stores valid moves for s

    def search(self, current_game: ShogiGame):
        # TODO implement predict

        # will be representing board states with string
        s = current_game.toString()

        # gets status of previously unencountered game state
        if s not in self.Es:
            self.Es[s] = current_game.getGameEnded()

        # exits terminal game state
        if self.Es[s]:
            # returns 1 since that means other player
            # checkmated
            return 1

        if s not in self.Ps:
            # assuming that predict will return probability distribution
            # over moves and a value for the board state
            self.Ps[s], v = self.nnet.predict(current_game)

            # masks illegal moves
            valids = current_game.getValidMoves()
            self.Ps[s] = self.Ps[s] * valids
            sum_Ps_s = np.sum(self.Ps[s])

            # normalizes move probability distribution
            if sum_Ps_s > 0:
                self.Ps[s] /= sum_Ps_s
            else:
                # handle errors
                # this block should not happen since that means the
                # current game state is terminal
                pass

            self.Vs[s] = valids
            self.Ns[s] = 0

            return -v

        # see if this is fast enough or if iteration
        # through len(valids) or ACTION_SIZE better
        valids = np.nonzero(self.Vs[s])
        cur_best = -float("inf")
        best_act = -1

        # need to calculate the action size
        # see using len is faster
        for a in valids:
            q_val = self.Qsa.get((s, a))
            if q_val:
                # upper confidence bound calculation
                u = q_val + self.c_puct * self.Ps[s][a] * math.sqrt(self.Ns[s]) / (
                    1 + self.Nsa[(s, a)]
                )
            else:
                # can initialize to 0
                u = self.c_puct * self.Ps[s][a] * math.sqrt(self.Ns[s] + 1e-8)

            if u > cur_best:
                cur_best = u
                best_act = a

        next_s = current_game.getNextState(best_act)

        v = self.search(next_s)

        sa_tup = (s, best_act)

        # updates the value of the q function
        if sa_tup in self.Qsa:
            self.Qsa[sa_tup] = (self.Nsa[sa_tup] * self.Qsa[sa_tup] + v) / (
                self.Nsa[sa_tup] + 1
            )
            self.Nsa[sa_tup] += 1
        else:
            self.Qsa[sa_tup] = v
            self.Nsa[sa_tup] = 1

        self.Ns[s] += 1
        return -v
