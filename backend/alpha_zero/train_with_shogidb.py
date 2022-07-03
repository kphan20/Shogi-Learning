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
from ray import tune
from ray.tune import CLIReporter
from ray.tune.schedulers import ASHAScheduler


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


def load_data(data_dir):
    dataset = MovesDataset(data_dir)
    train_length = len(dataset) // 3 * 2
    train_set, test_set = random_split(
        dataset, [train_length, len(dataset) - train_length]
    )
    return train_set, test_set


def train_with_tuning(config, data_dir=None, checkpoint_dir=None):
    nn = ResCNN(config["layers"])
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    opt = optim.Adam(nn.parameters(), lr=config["lr"])

    if checkpoint_dir:
        model_state, optimizer_state = torch.load(
            os.path.join(checkpoint_dir, "checkpoint")
        )
        nn.load_state_dict(model_state)
        opt.load_state_dict(optimizer_state)

    train_set, test_set = load_data(data_dir)

    train_loader = DataLoader(
        train_set,
        batch_size=config["batch_size"],
        shuffle=True,
        pin_memory=str(device) != "cpu",
    )
    # test_loader = DataLoader(test_set, batch_size=config["batch_size"], shuffle=False)

    def checkpoint_func(epoch, nnet, optimizer, epoch_loss, epoch_steps):
        with tune.checkpoint_dir(epoch) as checkpoint_dir:
            path = os.path.join(checkpoint_dir, "checkpoint")
            torch.save((nnet.state_dict(), optimizer.state_dict()), path)
        tune.report(loss=(epoch_loss / epoch_steps))

    losses = train_with_dataloader(train_loader, nn, opt, 10, device, checkpoint_func)
    # return losses


from functools import partial

if __name__ == "__main__":
    data_dir = os.path.join("shogidb2", "queries")
    config = {
        "layers": tune.randint(2, 16),
        "lr": tune.loguniform(1e-4, 1e-1),
        "batch_size": tune.choice([32, 64, 128, 256]),
    }

    scheduler = ASHAScheduler(
        metric="loss", mode="min", max_t=10, grace_period=1, reduction_factor=2
    )

    reporter = CLIReporter(metric_columns=["loss", "training_iteration"])
    result = tune.run(
        partial(train_with_tuning, data_dir=data_dir),
        config=config,
        num_samples=10,
        scheduler=scheduler,
        progress_reporter=reporter,
        resources_per_trial={"gpu": 1},
    )

    best_trial = result.get_best_trial("loss", "min", "last")
    print("Best trial config: {}".format(best_trial.config))
    print("Best trial final training loss: {}".format(best_trial.last_result["loss"]))

    print(os.path.join(best_trial.checkpoint.value, "checkpoint"))
    # print(losses)
    # epoch = range(1, len(losses) + 1)
    # plt.xticks(epoch)
    # plt.plot(epoch, losses, "rx-")
    # plt.xlabel("Epoch number")
    # plt.ylabel("Training loss")
    # plt.title("Training loss over epochs")
    # plt.savefig("figure.png")
