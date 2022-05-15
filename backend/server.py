import random
from flask import Flask
from flask_socketio import SocketIO, send, emit
from shogi_logic import (
    Move,
    find_moves_for_piece,
    move_to_board,
    rotate_board,
    check_check,
    get_moves,
)
import numpy as np

# add secret key later
app = Flask(__name__)
app.config["DEBUG"] = True
# should change allowed origins later
socketio = SocketIO(app, cors_allowed_origins="*")


@socketio.on("connect")
def test_connect():
    emit("after connect", "Connection success")


def move_to_arr(move: Move):
    return [list(move.piece), list(move.dest), move.promote]


# given a piece and the board, calculate possible moves in the position
@socketio.on("move")
def send_moves(data):
    board = np.array(data["board"])
    player = data["color"]
    moves = find_moves_for_piece(board, player, data["rank"], data["file"])

    # filter illegal moves
    moves = [
        move
        for move in moves
        if not check_check(rotate_board(move_to_board(board, player, move)), player)
    ]

    # translates Move object into array
    moves = [move_to_arr(move) for move in moves]
    emit("possible moves", moves)


@socketio.on("get move")
def model_move(data):
    captured_dict = {int(k): int(v) for k, v in data["captured_dict"].items()}
    moves = get_moves(
        rotate_board(np.array(data["board"])),
        data["color"],
        captured_dict,
    )
    move = random.choice(moves)
    new_start = move.piece
    if move.piece[0] != -1:
        new_start = (8 - move.piece[0], 8 - move.piece[1])

    new_dest = (8 - move.dest[0], 8 - move.dest[1])
    move = move_to_arr(Move(new_start, new_dest, move.promote))
    print(move)
    emit("model move", move)


@socketio.on("disconnect")
def client_disconnect():
    print("Connection closed")


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0")
