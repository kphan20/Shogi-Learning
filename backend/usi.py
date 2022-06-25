from shogi_logic import rotate_board
from variables import (
    BISHOP_ID,
    BLACK,
    CAPTURED_DICT,
    KING_ID,
    KNIGHT_ID,
    LANCE_ID,
    PAWN_ID,
    ROOK_ID,
    SILVER_GEN_ID,
    GOLD_GEN_ID,
    PROMOTE_CONSTANT,
    WHITE,
)
from shogi_game import ShogiGame
import numpy as np


fen_mapping = {
    "P": PAWN_ID,
    "L": LANCE_ID,
    "N": KNIGHT_ID,
    "S": SILVER_GEN_ID,
    "G": GOLD_GEN_ID,
    "B": BISHOP_ID,
    "R": ROOK_ID,
    "K": KING_ID,
    "p": -PAWN_ID,
    "l": -LANCE_ID,
    "n": -KNIGHT_ID,
    "s": -SILVER_GEN_ID,
    "g": -GOLD_GEN_ID,
    "b": -BISHOP_ID,
    "r": -ROOK_ID,
    "k": -KING_ID,
}

piece_mapping = {int(v): k for k, v in fen_mapping.items()}


def fen_to_game(fen_str: str):
    info_parts = fen_str.split()

    ranks = info_parts[0].split("/")
    board = np.zeros((9, 9))
    for rank, pieces_str in enumerate(ranks):
        current_file = 0
        current_char = 0
        is_promotion = False
        while current_char < len(pieces_str):
            char = pieces_str[current_char]
            if char == "+":
                is_promotion = True
            elif char in fen_mapping:
                piece = fen_mapping[char]
                if is_promotion:
                    piece += -PROMOTE_CONSTANT * (piece < 0) + PROMOTE_CONSTANT * (
                        piece > 0
                    )
                board[rank][current_file] = piece
                current_file += 1
                is_promotion = False
            else:
                current_file += int(char)

            current_char += 1
    player_to_move = BLACK if info_parts[1] == "b" else WHITE

    captured_pieces = {BLACK: dict(CAPTURED_DICT), WHITE: dict(CAPTURED_DICT)}
    hands = info_parts[2]
    current_char = 0
    while current_char < len(hands):
        char = hands[current_char]
        current_char += 1
        piece_count = 1
        if char == "-":
            break
        if char not in fen_mapping:
            char = hands[current_char]
            # handles player having double digit pawns
            if char not in fen_mapping:
                piece_count = int(hands[current_char - 1 : current_char + 1])
                current_char += 1
                char = hands[current_char]
            else:
                piece_count = int(hands[current_char - 1])

            current_char += 1

        piece = fen_mapping[char]
        if piece > 0:
            captured_pieces[BLACK][piece] = piece_count
        else:
            captured_pieces[WHITE][abs(piece)] = piece_count

    # choosing to omit move count from fen string

    if player_to_move == WHITE:
        board = rotate_board(board)

    return ShogiGame(captured_pieces, board, player_to_move)


def game_to_fen(game: ShogiGame):
    board = game.board
    if game.current_player == WHITE:
        board = rotate_board(board)
    ranks = []
    for rank in board:
        runs = find_runs(rank)
        rank_str = ""
        for run in runs:
            piece = int(run[0])
            if piece == 0:
                rank_str += str(int(run[1]))
                continue

            piece_str = ""
            if piece not in piece_mapping:
                piece_str += "+"
                piece = (
                    piece
                    + -PROMOTE_CONSTANT * (piece > 0)
                    + PROMOTE_CONSTANT * (piece < 0)
                )
            piece_str += piece_mapping[piece]
            rank_str += piece_str * int(run[1])
        ranks.append(rank_str)

    player = "b" if game.current_player == BLACK else "w"

    order = [
        ROOK_ID,
        BISHOP_ID,
        GOLD_GEN_ID,
        SILVER_GEN_ID,
        KNIGHT_ID,
        LANCE_ID,
        PAWN_ID,
    ]
    black_hand = ""
    white_hand = ""
    for piece in order:
        count = game.captured_pieces[BLACK][piece]
        label = piece_mapping[piece]
        if count >= 1:
            black_hand += label if count == 1 else f"{count}{label}"
        count = game.captured_pieces[WHITE][piece]
        label = piece_mapping[-piece]
        if count >= 1:
            white_hand += label if count == 1 else f"{count}{label}"
    captured_pieces = black_hand + white_hand
    if captured_pieces == "":
        captured_pieces = "-"

    return " ".join(("/".join(ranks), player, captured_pieces))


# https://gist.github.com/alimanfoo/c5977e87111abe8127453b21204c1065
def find_runs(x):
    """Find runs of consecutive items in an array."""

    # ensure array
    x = np.asanyarray(x)
    if x.ndim != 1:
        raise ValueError("only 1D array supported")
    n = x.shape[0]

    # handle empty array
    if n == 0:
        return np.array([]), np.array([]), np.array([])

    else:
        # find run starts
        loc_run_start = np.empty(n, dtype=bool)
        loc_run_start[0] = True
        np.not_equal(x[:-1], x[1:], out=loc_run_start[1:])
        run_starts = np.nonzero(loc_run_start)[0]

        # find run values
        run_values = x[loc_run_start]

        # find run lengths
        run_lengths = np.diff(np.append(run_starts, n))

        return np.column_stack((run_values, run_lengths))
