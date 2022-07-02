import sys

sys.path.append("./..")
from shogidb2.generate_examples import retrieve_games, load_example
from time import time, sleep
import torch
from torch.utils.data import Dataset, DataLoader, random_split
from model import ResCNN
from alpha_zero_training import train, train_with_dataloader
from multiprocessing import Process, SimpleQueue as Queue
from torch import optim
import matplotlib.pyplot as plt


def retrieve_games_wrapper(start, end, queue):
    retrieve_games(start, end, queue)
    queue.put("STOP")
    sleep(1)


def train_with_queue(queue, nn, opt, epochs, batch_size, device):
    losses = []
    while True:
        example = queue.get()
        if example == "STOP":
            break
        losses.extend(train(example, nn, opt, epochs, batch_size, device))
    print("trained")
    epoch = range(1, len(losses) + 1)
    plt.xticks(epoch)
    plt.plot(epoch, losses, "rx-")
    plt.show()
    return


import pandas as pd
import glob
import os


class MovesDataset(Dataset):
    def __init__(self, filepath):
        self.moves_frame = pd.concat(
            (
                pd.read_csv(
                    f, names=["Current Game", "Previous Game", "Best Move", "Reward"]
                )
                for f in glob.glob(os.path.join(filepath, "*.csv"))
            ),
            ignore_index=True,
        )

    def __len__(self):
        return len(self.moves_frame)

    def __getitem__(self, index):
        if torch.is_tensor(index):
            index = index.tolist()

        moves = self.moves_frame.iloc[index].to_list()
        moves = load_example(*moves)
        return moves


def incremental_fetch(nn: ResCNN, opt: optim.Optimizer, device: torch.device):
    q = Queue()
    get_p = Process(target=retrieve_games_wrapper, args=(723599, 723601, q))
    get_p.daemon = True
    start = time()
    get_p.start()

    train_with_queue(q, nn, opt, 100, 32, device)

    print(f"Training took {time() - start} seconds.")


if __name__ == "__main__":
    nn = ResCNN(19)
    opt = optim.Adam(nn.parameters())
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    dataset = MovesDataset(os.path.join("shogidb2", "queries"))
    train_length = len(dataset) // 3 * 2
    train_set, val_set = random_split(
        dataset, [train_length, len(dataset) - train_length]
    )
    batch_size = 256
    epochs = 10
    train_loader = DataLoader(
        train_set, batch_size=batch_size, shuffle=True, pin_memory=str(device) != "cpu"
    )
    test_loader = DataLoader(val_set, batch_size=batch_size, shuffle=False)

    losses = train_with_dataloader(train_loader, nn, opt, epochs, device)
    print(losses)
    epoch = range(1, len(losses) + 1)
    plt.xticks(epoch)
    plt.plot(epoch, losses, "rx-")
    plt.xlabel("Epoch number")
    plt.ylabel("Training loss")
    plt.title("Training loss over epochs")
    plt.savefig("figure.png")
