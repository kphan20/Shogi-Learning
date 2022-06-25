import numpy as np
import requests
import sys

sys.path.append("../")
sys.path.append("../../")
from shogi_game import ShogiGame
from variables import (
    ACTION_SIZE,
    BISHOP_ID,
    BLACK,
    BOARD_SIZE,
    GOLD_GEN_ID,
    KING_ID,
    KNIGHT_ID,
    LANCE_ID,
    PAWN_ID,
    PROM_BISH_ID,
    PROM_KNIGHT_ID,
    PROM_LANCE_ID,
    PROM_PAWN_ID,
    PROM_ROOK_ID,
    PROM_SILG_ID,
    ROOK_ID,
    SILVER_GEN_ID,
)
from usi import fen_to_game
from shogi_game import move_to_action
from shogi_logic import Move
from multiprocessing import Queue


def generate_url(game_id):
    return f"https://api.shogidb2.com/eval/{game_id}/default.json"


def retrieve_games(id_start, id_end, queue: Queue):
    for game_id in range(id_start, id_end + 1):
        response = requests.get(generate_url(game_id))
        data = response.json()
        queue.put(process_data(data))


csa_piece_lookup = {
    "OU": KING_ID,
    "KI": GOLD_GEN_ID,
    "HI": ROOK_ID,
    "KA": BISHOP_ID,
    "GI": SILVER_GEN_ID,
    "FU": PAWN_ID,
    "KY": LANCE_ID,
    "KE": KNIGHT_ID,
    "RY": PROM_ROOK_ID,
    "UM": PROM_BISH_ID,
    "NK": PROM_KNIGHT_ID,
    "NG": PROM_SILG_ID,
    "TO": PROM_PAWN_ID,
    "NY": PROM_LANCE_ID,
}


def convert_coords(csa_str, ind):
    return BOARD_SIZE - int(csa_str[ind])


def csa_to_move(csa_string, current_game: ShogiGame):
    piece_id = csa_piece_lookup[csa_string[-2:]]
    destination = (int(csa_string[4]) - 1, convert_coords(csa_string, 3))

    # drop move
    if csa_string[1:3] == "00":
        return Move((-1, piece_id), destination)

    start = (int(csa_string[2]) - 1, convert_coords(csa_string, 1))

    return Move(
        start,
        destination,
        current_game.board[start[0]][start[1]] <= PAWN_ID and piece_id > PAWN_ID,
    )


def process_data(game_data):
    moves = game_data["evals"]
    examples = []
    current_player = BLACK
    prev_game = ShogiGame()
    for i in range(1, len(moves) - 1):
        move = moves[i]
        last_move = moves[i - 1]
        current_game = fen_to_game(last_move["sfen"])
        current_game.prev_state = prev_game

        prev_game = current_game
        suggested_move = move_to_action(
            csa_to_move(move["bestmove"]["csa"], current_game)
        )
        position_score = move["bestmove"]["score"]

        reward = (current_player * position_score > 0) * 2 - 1
        policy = np.zeros(ACTION_SIZE)
        policy[int(suggested_move)] = 1
        examples.append([current_game.toTensor(), policy, reward])
        current_player *= -1
    return examples
