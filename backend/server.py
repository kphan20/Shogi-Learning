from flask import Flask
from flask_socketio import SocketIO, send, emit
from shogi_logic import find_moves_for_piece, move_to_board, rotate_board, check_check
import numpy as np

# add secret key later
app = Flask(__name__)
app.config["DEBUG"] = True
# should change allowed origins later
socketio = SocketIO(app, cors_allowed_origins="*")


@socketio.on("connect")
def test_connect():
    emit("after connect", "Connection success")


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
    moves = [[list(move.piece), list(move.dest), move.promote] for move in moves]
    emit("possible moves", moves)


@socketio.on("disconnect")
def client_disconnect():
    print("Connection closed")


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0")
