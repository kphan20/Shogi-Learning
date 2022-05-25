import random
from flask import Flask
from flask_socketio import SocketIO, emit
from shogi_logic import (
    Move,
    find_moves_for_piece,
    move_to_board,
    rotate_board,
    check_check,
    get_moves,
    find_drops_for_piece,
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


def process_dict(captured_dict: dict):
    return {int(k): int(v) for k, v in captured_dict.items()}


# given a piece and the board, calculate possible moves in the position
@socketio.on("move")
def send_moves(data):
    board = np.array(data["board"])
    player = data["color"]
    if data["rank"] == -1:
        moves = find_drops_for_piece(board, player, data["file"])
    else:
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
    model_captured_dict = process_dict(data["model_captured_dict"])
    board = rotate_board(np.array(data["board"]))
    player = data["color"]
    moves = get_moves(
        board,
        player,
        model_captured_dict,
    )

    # sends lost signal for model player
    if len(moves) == 0:
        emit("model lost")
        return

    # randomly sample move
    # replace this with actual model later
    move = random.choice(moves)

    new_board = rotate_board(move_to_board(board, player, move))
    player_captured_dict = process_dict(data["player_captured_dict"])
    player_moves = get_moves(new_board, -player, player_captured_dict)
    if len(player_moves) == 0:
        emit("player lost")
        return

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
