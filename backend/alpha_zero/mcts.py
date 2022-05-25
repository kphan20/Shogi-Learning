import math
import sys

sys.path.append("./..")
from shogi_game import ShogiGame
import numpy as np
from variables import *
import torch.nn as nn
import torch

# Heavily inspired by https://github.com/suragnair/alpha-zero-general/blob/master/MCTS.py
class MCTS:
    def __init__(self, nnet: nn.Module, q=[], n=[], c_puct=0.2):
        self.nnet = nnet
        self.q = q
        self.n = n
        # controls level of exploration
        self.c_puct = c_puct

        self.Qsa = {}  # Q table
        # original implementation used tuples for Nsa
        # will use dict of action values instead
        self.Nsa = {}  # times s,a is visited
        self.Ns = {}  # stores times s is visited
        self.Ps = {}  # initial policy priors

        self.Es = {}  # stores if game ended
        self.Vs = {}  # stores valid moves for s

    def predict(self, game: ShogiGame):
        # try to understand cuda code for optimization
        self.nnet.eval()
        # expands to include batch size of one
        input = game.toTensor().expand(1, -1, -1, -1)
        with torch.no_grad():
            pi, v = self.nnet(input)
        return pi.numpy()[0], v.numpy()[0]

    def search(self, current_game: ShogiGame):

        # will be representing board states with string
        s = current_game.toString()

        # gets status of previously unencountered game state
        if s not in self.Es:
            self.Es[s] = current_game.getGameEnded()

        # exits terminal game state
        if self.Es[s]:
            # returns 1 since that means other player
            # checkmated
            # print("finished 1")
            return 1

        if s not in self.Ps:
            # assuming that predict will return probability distribution
            # over moves and a value for the board state
            self.Ps[s], v = self.predict(current_game)

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
                print("something went wrong")
                self.Ps[s] += valids
                self.Ps[s] /= np.sum(self.Ps[s])

            self.Vs[s] = valids
            self.Ns[s] = 0
            # print("finished 2")
            return -v

        # see if this is fast enough or if iteration
        # through len(valids) or ACTION_SIZE better
        valids = self.Vs[s]
        valids = np.argwhere(valids)
        cur_best = -float("inf")
        best_act = -1

        # need to calculate the action size
        # see using len is faster
        for a in valids:
            a = int(a)

            q_val = self.Qsa.get((s, a))
            if q_val:
                # upper confidence bound calculation
                u = q_val + self.c_puct * self.Ps[s][a] * math.sqrt(self.Ns[s]) / (
                    1 + self.Nsa[s][a]
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
            self.Qsa[sa_tup] = (self.Nsa[s][best_act] * self.Qsa[sa_tup] + v) / (
                self.Nsa[s][best_act] + 1
            )
            self.Nsa[s][best_act] += 1
        else:
            self.Qsa[sa_tup] = v
            if self.Nsa.get(s):
                self.Nsa[s][best_act] = 1
            else:
                self.Nsa[s] = {best_act: 1}

        self.Ns[s] += 1
        # print("finished 3")
        return -v

    # given the string representation, get visit count policy
    def getPolicy(self, state: str):
        action_dict = self.Nsa[state]
        policy = np.zeros(ACTION_SIZE)
        for action, count in action_dict.items():
            policy[action] = count
        return policy / self.Ns[state]


from model import ResCNN
import time
from shogi_game import action_to_move

# sys.setrecursionlimit(3000)

game = ShogiGame()
total_time = 0
string = game.toString()
for i in range(1):
    test = MCTS(ResCNN(2))
    start = time.time()
    for _ in range(3):
        # print(f"iteration {_}")
        test.search(game)
    total_time += time.time() - start
print(total_time)
results = np.argwhere(test.getPolicy(string)).flatten()
for result in results:
    print(action_to_move(result))
