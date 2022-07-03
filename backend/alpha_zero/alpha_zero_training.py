import torch
from torch import optim
from torch.utils.data import DataLoader
import numpy as np
import sys
import os
from mcts_iter import MCTS

sys.path.append("./..")
from shogi_game import ShogiGame
from shogi_logic import rotate_board
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
    a = np.random.choice(action_choices, p=mcts.getPolicy(game))
    return game.getNextState(a)


# assumes games always start from default position
def self_play(new_nnet: ResCNN, old_nnet: ResCNN):
    new_nnet.eval()
    old_nnet.eval()
    new_mcts = MCTS(new_nnet)
    old_mcts = MCTS(old_nnet)
    game = ShogiGame()
    num_games = 1
    mcts_iters = 20
    win_count = 0
    draws = 0
    max_move_count = 300
    action_choices = np.arange(ACTION_SIZE)

    # games where new net goes first
    for _ in range(num_games):
        moves = 0
        # could do optimization with do while loop
        while moves < max_move_count and not game.getGameEnded():
            game = model_move(new_mcts, mcts_iters, game, action_choices)
            moves += 1
            if game.getGameEnded():
                win_count += 1
                break

            game = model_move(old_mcts, mcts_iters, game, action_choices)
            moves += 1
            print(moves)
        if not game.getGameEnded():
            draws += 1

        game = ShogiGame()

    # games where new net goes second
    for _ in range(num_games):
        game = model_move(old_mcts, mcts_iters, game, action_choices)

        moves = 1
        while moves < max_move_count and not game.getGameEnded():
            game = model_move(new_mcts, mcts_iters, game, action_choices)
            moves += 1

            if game.getGameEnded():
                win_count += 1
                break

            game = model_move(old_mcts, mcts_iters, game, action_choices)
            moves += 1
        if not game.getGameEnded():
            draws += 1
        game = ShogiGame()

    return win_count / (2 * num_games), draws


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

        policy = mcts.getPolicy(game)

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


def train(
    examples, nn: ResCNN, opt: optim.Optimizer, epochs, batch_size, device: torch.device
):
    # opt = optim.Adam(nn.parameters())
    examples_len = len(examples)
    batch_count = examples_len // batch_size
    nn.to(device)
    losses = []
    for _ in range(epochs):
        nn.train()
        epoch_loss = 0
        epoch_steps = 0
        for _ in range(batch_count):
            samples = np.random.randint(examples_len, size=batch_size)
            boards, pis, vs = list(zip(*[examples[i] for i in samples]))
            boards = torch.stack(boards)

            boards, pis, vs = (
                boards.to(device),
                torch.FloatTensor(np.array(pis)).to(device),
                torch.FloatTensor(np.array(vs).astype(np.float64)).to(device),
            )

            out_pi, out_v = nn(boards)

            total_loss = policy_loss(pis, out_pi) + value_loss(vs, out_v)
            # print(total_loss)
            opt.zero_grad()
            total_loss.backward()
            opt.step()

            epoch_loss += total_loss.item()
            epoch_steps += 1
        losses.append(epoch_loss / epoch_steps)
    save_checkpoint(nn, opt)
    return losses


def train_with_dataloader(
    data_loader: DataLoader,
    nn: ResCNN,
    opt: optim.Optimizer,
    epochs,
    device: torch.device,
    checkpoint_func: function = None,
):
    nn.to(device)
    losses = []
    for epoch in range(epochs):
        nn.train()
        epoch_loss = 0
        epoch_steps = 0
        print(f"epoch {epoch}")
        for data in data_loader:
            boards, pis, vs = data

            boards, pis, vs = (
                boards.to(device),
                pis.to(device),
                vs.float().to(device),
            )

            out_pi, out_v = nn(boards)

            total_loss = policy_loss(pis, out_pi) + value_loss(vs, out_v)

            opt.zero_grad(set_to_none=True)
            total_loss.backward()
            opt.step()

            epoch_loss += total_loss.item()
            epoch_steps += 1
            if epoch_steps % 50 == 49:
                print(epoch_loss / epoch_steps)
        losses.append(epoch_loss / epoch_steps)
        if checkpoint_func:
            checkpoint_func(epoch + 1, nn, opt, epoch_loss, epoch_steps)
    return losses


# policy loss as defined in alpha zero paper
# - (target policy) * (sample policy)
def policy_loss(target: torch.Tensor, sample: torch.Tensor):
    return -torch.sum(target * sample) / target.size()[0]


# value loss as defined in alpha zero paper
# (target - sample)**2
def value_loss(target: torch.Tensor, sample: torch.Tensor):
    return torch.sum((target - sample.view(-1)) ** 2) / target.size()[0]


def save_checkpoint(
    nnet: ResCNN, optimizer: optim.Optimizer, filename="checkpoint.pth"
):
    if not os.path.exists("checkpoints"):
        os.mkdir("checkpoints")
    torch.save(
        {
            "model_state_dict": nnet.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
        },
        os.path.join("checkpoints", filename),
    )


def load_checkpoint(
    nnet: ResCNN, path="checkpoints/checkpoint.pth", optimizer: optim.Optimizer = None
):
    # look into map location
    checkpoint = torch.load(path, map_location=torch.device("cpu"))

    if len(checkpoint["model_state_dict"]) != len(nnet.state_dict()):
        raise ValueError("Invalid number of layers.")

    nnet.load_state_dict(checkpoint["model_state_dict"])
    if optimizer:
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])


# trained_nn = ResCNN(19)
# load_checkpoint(trained_nn)
# base_nn = ResCNN(19)

# print(self_play(trained_nn, base_nn))

# from alpha_zero_training import load_checkpoint, policy_loss, value_loss

# from shogi_game import ShogiGame

# game = ShogiGame()

# valids = game.getValidMoves()
# nnet = ResCNN(19)
# trained = ResCNN(19)
# load_checkpoint(trained)

# data = game.toTensor().expand(1, -1, -1, -1)
# u_p, u_v = nnet(data)
# t_p, t_v = trained(data)

# print(np.sum(t_p.detach().numpy() * valids))
# print(np.sum(u_p.detach().numpy() * valids))

# print(u_v)
# print(t_v)

# print(f"first {policy_loss(t_p, u_p)}")
# print(value_loss(t_v, u_v))
