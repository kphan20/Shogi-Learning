import torch
from torch import optim
import numpy as np
import sys
from mcts_copy import MCTS

sys.path.append("./..")
from shogi_game import ShogiGame
from variables import ACTION_SIZE

from model import ResCNN

# can train from saved model if given input
def policyIter(iters, episodes, sims, nn: ResCNN = ResCNN(2)):
    nnet = nn
    examples = []

    for i in range(iters):
        for e in range(episodes):
            examples += episode(nnet, sims)
        # add epochs and batch size
        trained_nnet = train(examples, nnet)
        # adjust win threshold
        if self_play(trained_nnet, nnet) > 0.55:
            nnet = trained_nnet

    return nnet


def model_move(mcts: MCTS, num_iters, game: ShogiGame, action_choices):
    for _ in range(num_iters):
        mcts.search(game)
    a = np.random.choice(action_choices, p=mcts.getPolicy(game.toString()))
    return game.getNextState(a)


# assumes games always start from default position
def self_play(new_nnet, old_nnet):
    new_mcts = MCTS(new_nnet)
    old_mcts = MCTS(old_nnet)
    game = ShogiGame()
    num_games = 10
    mcts_iters = 20
    win_count = 0
    action_choices = np.arange(ACTION_SIZE)

    # games where new net goes first
    for _ in range(num_games):
        # could do optimization with do while loop
        while not game.getGameEnded():
            game = model_move(new_mcts, mcts_iters, game, action_choices)

            if game.getGameEnded():
                win_count += 1
                break

            game = model_move(old_mcts, mcts_iters, game, action_choices)

        game = ShogiGame()

    # games where new net goes second
    for _ in range(num_games):
        game = model_move(old_mcts, mcts_iters, game, action_choices)

        while not game.getGameEnded():
            game = model_move(new_mcts, mcts_iters, game, action_choices)

            if game.getGameEnded():
                win_count += 1
                break

            game = model_move(old_mcts, mcts_iters, game, action_choices)

        game = ShogiGame()

    return win_count / (2 * num_games)


def episode(nn: ResCNN, sims):
    examples = []
    game = ShogiGame()
    mcts = MCTS(nn)
    action_choices = np.arange(ACTION_SIZE)
    max_moves = 500
    move_count = 0

    # iterates until terminal node is reached
    while True:
        for _ in range(sims):
            mcts.search(game)
        s = game.toString()
        policy = mcts.getPolicy(s)

        # putting in board tensor rather than string for not
        examples.append([game.toTensor(), policy, 0])  # placeholder reward
        # look into random.choices()
        # should we choose over distribution here or max?
        a = np.random.choice(action_choices, p=policy)
        game = game.getNextState(a)
        move_count += 1
        print(f"move made: {a}")
        if move_count > max_moves or game.getGameEnded():
            reward = 1
            for example in examples[::-1]:
                example[2] = reward
                reward *= -1
            return examples


def train(examples, nn: ResCNN, epochs, batch_size):
    # add gpu stuff later
    opt = optim.Adam(nn.parameters())
    examples_len = len(examples)
    batch_count = examples_len // batch_size

    for _ in range(epochs):
        nn.train()

        for _ in range(batch_count):
            samples = np.random.randint(examples_len, size=batch_size)
            boards, pis, vs = list(zip(*[examples[i] for i in samples]))
            boards = torch.stack(boards)

            out_pi, out_v = nn(boards)

            total_loss = policy_loss(pis, out_pi) + value_loss(vs, out_v)

            opt.zero_grad()
            total_loss.backward()
            opt.step()


# policy loss as defined in alpha zero paper
# - (target policy) * (sample policy)
def policy_loss(target: torch.Tensor, sample: torch.Tensor):
    return -torch.sum(target * sample) / target.size()[0]


# value loss as defined in alpha zero paper
# (target - sample)**2
def value_loss(target: torch.Tensor, sample: torch.Tensor):
    return torch.sum((target - sample.view(-1)) ** 2) / target.size()[0]
