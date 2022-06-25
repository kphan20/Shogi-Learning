import sys

sys.path.append("./..")
from shogidb2.generate_examples import retrieve_games
from time import time, sleep
import torch
from model import ResCNN
from alpha_zero_training import train
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


if __name__ == "__main__":
    nn = ResCNN(19)
    q = Queue()
    opt = optim.Adam(nn.parameters())
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    get_p = Process(target=retrieve_games_wrapper, args=(723599, 723601, q))
    get_p.daemon = True
    start = time()
    get_p.start()

    train_with_queue(q, nn, opt, 100, 32, device)

    print(f"Training took {time() - start} seconds.")
