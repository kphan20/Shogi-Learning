from dataclasses import dataclass
from variables import *
import numpy as np
from numpy.typing import NDArray

# Used to represent a move
@dataclass
class Move:
    piece: tuple
    dest: tuple
    promote: bool

    def __init__(self, piece: tuple, dest: tuple, promote: bool = False):
        self.piece = piece
        self.dest = dest
        self.promote = promote


"""
IMPORTANT
Unless stated otherwise, assume that the board is oriented to match the 
direction of the player passed in player variable. If rotating the board
is too computationally expensive, this approach may be reconsidered.

List of methods in this file:

check_owned(piece, player): Checks whether piece belongs to player
rotate_board(board): Orients board towards other player
move_to_board(board, player, move): Adds move to copy of board and returns it
get_moves(board, player, cap_pieces): Gets all moves a player can do
force_promote(piece, rank): Checks if piece is required to promote
iterate_direction(board, player, rank, file, move, prom): Adds moves for pieces
    that can move multiple tiles in a direction
get_piece_moves(board, player, rank, file, move_set, prom): Given the piece's
    move set and whether it can promote, create moves
find_moves_for_piece(board, player, rank, file): Skeleton function that
    gets moves for specific piece it encounters
add_drops_piece(board, player, rank, file, piece, drops): For a given
    piece and square, add a drop move to drops if piece can be dropped
    at the square 
add_drops(board, player, rank, file, captured_pieces): Gets drops that
    are possible on an empty tile
checkmate_check(board, player): Checks if player is in
    checkmate (mainly for pawn drop rule)
iterate_direction_check(board, player, rank, file, move): For an 
    opposing piece that can move multiple squares, see if it checks 
    player's king. Board is oriented towards opposing player.
get_piece_moves_check(board, player, rank, file, move_set): Checks if 
    player's king lies in range of enemy piece. Board is oriented 
    towards opposing player.
find_moves_for_piece_check(board, player, rank, file): Checks whether 
    current enemy piece checks player's king. Board is oriented towards 
    opposing player.
check_check(board, player): For a given board, checks if player is in
    check. Board is oriented in direction of opposing player.
"""
# will be used in case I change my mind later
# actually prolly on the chopping block
def check_owned(piece: int, player: int) -> bool:
    return piece * player > 0


def rotate_board(board: NDArray) -> NDArray:
    """
    Orients board towards other player

    Args:
        board (NDArray): 2D representation of board

    Returns:
        NDArray: rotated board
    """
    return np.flip(np.flip(board, 1), 0)


# currently does not remove dropped piece from captured hand
def move_to_board(board: NDArray, player: int, move: Move) -> NDArray:
    """
    Executes move on copy of board and returns it

    Args:
        board (NDArray): 2D array of board representation
        player (int): integer indicating current player
        move (Move): move to be executed

    Returns:
        NDArray: new board with move executed
    """
    rank, file = move.piece
    new_rank, new_file = move.dest
    # creates copy of board
    new_board = np.copy(board)
    if rank == -1:
        # for drops, rank is -1 and file is piece dropped
        new_board[new_rank][new_file] = file * player
    else:
        # otherwise, move appropriate piece to new square
        piece = board[rank][file]
        if move.promote:
            piece += PROMOTE_CONSTANT
        new_board[new_rank][new_file] = piece
        new_board[rank][file] = EMPTY_SQUARE_ID
    return new_board


def get_moves(board: NDArray, player: int, cap_pieces: dict) -> list[Move]:
    """
    Gets all moves a player can do

    Args:
        board (NDArray): 2D array representation of board
        player (int): current player
        cap_pieces (dict): current player's captured pieces

    Returns:
        list[Move]: all legal moves in the position
    """
    moves = []
    for rank, row in enumerate(board):
        for file, piece in enumerate(row):
            if piece == EMPTY_SQUARE_ID:
                # if empty square, player can add drops
                moves += add_drops(board, player, rank, file, cap_pieces)
            elif check_owned(piece, player):
                # if piece owned by player, find moves for piece
                moves += find_moves_for_piece(board, player, rank, file)

    # filter out moves that result in check on player's king
    moves = [
        move
        for move in moves
        if not check_check(rotate_board(move_to_board(board, player, move)), player)
    ]
    return moves


def force_promote(piece: int, rank: int) -> bool:
    """
    Checks if piece is required to promote

    Args:
        piece (int): piece to be moved
        rank (int): piece's rank

    Returns:
        bool: indication whether forced promotion is necessary
    """
    # forced promotion rules for lance and pawn
    if piece in (LANCE_ID, PAWN_ID):
        return rank == 0
    # forced promotion rules for knight
    elif piece == KNIGHT_ID:
        return rank < 2
    # no forced promotion for other pieces
    return False


def iterate_direction(
    board: NDArray, player: int, rank: int, file: int, move: tuple, prom: bool
) -> list[Move]:
    """
    Adds moves for pieces that can move multiple tiles in a single direction

    Args:
        board (NDArray): 2D board representation
        player (int): current player
        rank (int): starting rank
        file (int): starting file
        move (tuple): direction to iterate in
        prom (bool): whether or not piece can promote

    Returns:
        list[Move]: all possible moves in the given direction
    """
    moves = []
    # piece to be moved
    piece = board[rank][file]

    # gets direction of move
    move_rank, move_file = move

    # used to initialize moves added to moves array
    start_point = (rank, file)

    # used in direction iteration loop
    new_rank, new_file = rank, file

    # if piece starts in promotion zone, can promote anytime
    can_prom = rank <= PROMOTE_RANK
    while True:
        new_rank += move_rank
        new_file += move_file

        # out of bounds check
        if (
            new_rank < 0
            or new_rank >= BOARD_SIZE
            or new_file < 0
            or new_file >= BOARD_SIZE
        ):
            break

        # toggles can_prom if piece enters promotion zone
        if not can_prom and new_rank <= PROMOTE_RANK:
            can_prom = True

        # gets piece at new position
        destination = board[new_rank][new_file]

        # if on empty square or enemy, add move
        if not check_owned(destination, player):
            # adds non-promotion move if force promotion isn't required
            if not force_promote(piece, new_rank):
                moves.append(Move(start_point, (new_rank, new_file)))
            # adds promotion move if possible
            if prom and can_prom:
                moves.append(Move(start_point, (new_rank, new_file), True))

        # if another piece encountered, stop searching
        if destination != 0:
            break
    return moves


def get_piece_moves(
    board: NDArray,
    player: int,
    rank: int,
    file: int,
    move_set: list[tuple],
    prom: bool,
) -> list[Move]:
    """
    Given the piece's move set and whether it can promote, create moves

    Args:
        board (NDArray): 2D representation of board
        player (int): current player
        rank (int): piece's rank
        file (int): piece's file
        move_set (list[tuple]): directions piece can move
        prom (bool): whether or not piece can promote

    Returns:
        list[Move]: list of possible moves
    """
    moves = []

    # current piece
    piece = board[rank][file]
    for move in move_set:
        new_rank, new_file = move
        new_rank += rank
        new_file += file

        # bounds check
        if (
            new_rank < 0
            or new_rank >= BOARD_SIZE
            or new_file < 0
            or new_file >= BOARD_SIZE
        ):
            continue

        # adds moves if destination square is not owned by player
        if not check_owned(board[new_rank][new_file], player):
            # add non-promotion move if not forced to promote
            if not force_promote(piece, new_rank):
                moves.append(Move((rank, file), (new_rank, new_file)))
            # adds promotion move if valid
            if prom and (rank <= PROMOTE_RANK or new_rank <= PROMOTE_RANK):
                moves.append(Move((rank, file), (new_rank, new_file), True))
    return moves


def find_moves_for_piece(
    board: NDArray, player: int, rank: int, file: int
) -> list[Move]:
    """
    Skeleton function that gets moves for specific piece it encounters

    Args:
        board (NDArray): 2D representation of board
        player (int): current player
        rank (int): piece rank
        file (int): piece file

    Returns:
        list[Move]: piece's possible moves
    """
    # gets piece type
    piece = board[rank][file] * player

    moves = []
    if piece == KING_ID:
        moves += get_piece_moves(board, player, rank, file, KING_MOVES, False)
    elif piece in (
        GOLD_GEN_ID,
        PROM_SILG_ID,
        PROM_KNIGHT_ID,
        PROM_PAWN_ID,
        PROM_LANCE_ID,
    ):
        moves += get_piece_moves(board, player, rank, file, GOLD_GEN_MOVES, False)
    elif piece == BISHOP_ID:
        for move in BISHOP_MOVES:
            moves += iterate_direction(board, player, rank, file, move, True)
    elif piece == ROOK_ID:
        for move in ROOK_MOVES:
            moves += iterate_direction(board, player, rank, file, move, True)
    elif piece == PROM_BISH_ID:
        for move in BISHOP_MOVES:
            moves += iterate_direction(board, player, rank, file, move, False)
        moves += get_piece_moves(board, player, rank, file, ROOK_MOVES, False)
    elif piece == PROM_ROOK_ID:
        for move in ROOK_MOVES:
            moves += iterate_direction(board, player, rank, file, move, False)
        moves += get_piece_moves(board, player, rank, file, BISHOP_MOVES, False)
    elif piece == KNIGHT_ID:
        moves += get_piece_moves(board, player, rank, file, KNIGHT_MOVES, True)
    elif piece == PAWN_ID:
        # potentially get rid of PAWN_MOVES
        moves += get_piece_moves(board, player, rank, file, PAWN_MOVES, True)
    elif piece == LANCE_ID:
        moves += iterate_direction(board, player, rank, file, LANCE_MOVES[0], True)
    elif piece == SILVER_GEN_ID:
        moves += get_piece_moves(board, player, rank, file, SILVER_GEN_MOVES, True)

    return moves


def add_drops_piece(
    board: NDArray, player: int, rank: int, file: int, piece: int, drops: list[Move]
):
    """
    For a given piece and square, add a drop move to drops if piece can
    be dropped at the square

    Args:
        board (NDArray): 2D representation of the board
        player (int): current player
        rank (int): rank of desired square
        file (int): file of desired square
        piece (int): dropped piece
        drops (list[Move]): accumulator of valid drop moves
    """
    if piece == PAWN_ID:
        # rank check
        if rank == 0:
            return

        other_pawn = piece * player

        # checks if there is another pawn in the file
        if other_pawn in board[:, file]:
            return

        # creates copy of board with pawn placed
        new_board = np.copy(board)
        new_board[rank][file] = other_pawn

        # if enemy king in check, check if checkmate
        if board[rank - 1][file] == -player * KING_ID:
            # don't add drop move if results in checkmate
            if checkmate_check(rotate_board(new_board), -player):
                return

    if piece == LANCE_ID and rank == 0:
        return

    if piece == KNIGHT_ID and rank <= 1:
        return

    # if valid drop, add to drops array
    drops.append(Move((-1, piece), (rank, file)))


def add_drops(
    board: NDArray, player: int, rank: int, file: int, captured_pieces: dict
) -> list[Move]:
    """
    Gets drops that are possible on an empty tile.

    Args:
        board (NDArray): 2D representation of board
        player (int): current player
        rank (int): empty tile rank
        file (int): empty tile file
        captured_pieces (dict): pieces captured by current player
        other_captured_pieces (dict): pieces captured by opposing player

    Returns:
        list[Move]: valid drop moves
    """
    drops = []
    for captured_piece, count in captured_pieces.items():
        if count > 0:
            add_drops_piece(board, player, rank, file, captured_piece, drops)

    return drops


def checkmate_check(board: NDArray, player: int) -> bool:
    """
    Checks if player is in checkmate (mainly for pawn drop rule)
    Args:
        board (NDArray): 2D representation of board
        player (int): current player

    Returns:
        bool: whether or not player is checkmated
    """
    # if in check by pawn, player cannot drop pieces anyway - pass empty dict
    moves = get_moves(board, player, {})
    return len(moves) == 0


def iterate_direction_check(
    board: NDArray, player: int, rank: int, file: int, move: tuple
) -> bool:
    """
    For an opposing piece that can move multiple squares, see if it
    checks player's king. Board is oriented towards opposing player.

    Args:
        board (NDArray): 2D representation of board
        player (int): player potentially in check
        rank (int): opposing piece's start rank
        file (int): opposing piece's start file
        move (tuple): direction of opposing piece movement

    Returns:
        bool: whether opposing piece checks player's king or not
    """
    move_rank, move_file = move
    new_rank, new_file = rank, file
    while True:
        new_rank += move_rank
        new_file += move_file

        # out of bounds check
        if (
            new_rank < 0
            or new_rank >= BOARD_SIZE
            or new_file < 0
            or new_file >= BOARD_SIZE
        ):
            break

        # if destination square contains player's king, return true
        destination = board[new_rank][new_file] * player
        if destination == KING_ID:
            return True

        # if another piece encountered, stop searching
        if destination != 0:
            break
    return False


def get_piece_moves_check(
    board: NDArray, player: int, rank: int, file: int, move_set: list[tuple]
) -> bool:
    """
    Checks if player's king lies in range of enemy piece. Board is
    oriented towards opposing player.

    Args:
        board (NDArray): 2D representation of board
        player (int): player who could be in check
        rank (int): opposing piece rank
        file (int): opposing piece file
        move_set (list[tuple]): moves that opposing piece can execute

    Returns:
        bool: whether opposing piece checks player's king or not
    """
    for move in move_set:
        new_rank, new_file = move
        new_rank += rank
        new_file += file

        # bounds check
        if (
            new_rank < 0
            or new_rank >= BOARD_SIZE
            or new_file < 0
            or new_file >= BOARD_SIZE
        ):
            continue

        # if player's king is in range, return true
        if board[new_rank][new_file] * player == KING_ID:
            return True
    return False


def find_moves_for_piece_check(
    board: NDArray, player: int, rank: int, file: int
) -> bool:
    """
    Checks whether current enemy piece checks player's king. Board is
    oriented towards opposing player.

    Args:
        board (NDArray): 2D representation of board
        player (int): player who is potentially in check
        rank (int): opposing piece rank
        file (int): opposing piece file

    Returns:
        bool: if opposing piece checks player's king
    """
    # gets opposing player's piece
    piece = board[rank][file] * -player

    result = False

    if piece == KING_ID:
        result = get_piece_moves_check(board, player, rank, file, KING_MOVES)
    elif piece in (
        GOLD_GEN_ID,
        PROM_SILG_ID,
        PROM_KNIGHT_ID,
        PROM_PAWN_ID,
        PROM_LANCE_ID,
    ):
        result = get_piece_moves_check(board, player, rank, file, GOLD_GEN_MOVES)
    elif piece == BISHOP_ID:
        for move in BISHOP_MOVES:
            result = iterate_direction_check(board, player, rank, file, move)
            if result:
                break
    elif piece == ROOK_ID:
        for move in ROOK_MOVES:
            result = iterate_direction_check(board, player, rank, file, move)
            if result:
                break
    elif piece == PROM_BISH_ID:
        for move in BISHOP_MOVES:
            result = iterate_direction_check(board, player, rank, file, move)
            if result:
                break
        if not result:
            result = get_piece_moves_check(board, player, rank, file, ROOK_MOVES)
    elif piece == PROM_ROOK_ID:
        for move in ROOK_MOVES:
            result = iterate_direction_check(board, player, rank, file, move)
            if result:
                break
        if not result:
            result = get_piece_moves_check(board, player, rank, file, BISHOP_MOVES)
    elif piece == KNIGHT_ID:
        result = get_piece_moves_check(board, player, rank, file, KNIGHT_MOVES)
    elif piece == PAWN_ID:
        # potentially get rid of PAWN_MOVES
        result = get_piece_moves_check(board, player, rank, file, PAWN_MOVES)
    elif piece == LANCE_ID:
        result = iterate_direction_check(board, player, rank, file, LANCE_MOVES[0])
    elif piece == SILVER_GEN_ID:
        result = get_piece_moves_check(board, player, rank, file, SILVER_GEN_MOVES)

    return result


def check_check(board: NDArray, player: int) -> bool:
    """
    For a given board, checks if player is in check. Board is oriented
    in direction of opposing player.

    Args:
        board (NDArray): 2D board representation
        player (int): player that could be in check

    Returns:
        bool: whether player is in check or not
    """

    for rank, row in enumerate(board):
        for file, piece in enumerate(row):
            # checks if piece belongs to opposing player
            if player * piece < 0:
                # breaks if player's king is in check
                if find_moves_for_piece_check(board, player, rank, file):
                    return True
    return False


# METHODS ONLY USED BY FRONTEND CLIENT
def find_drops_for_piece(board: NDArray, player: int, dropped_piece: int):
    drops = []
    for rank, row in enumerate(board):
        for file, piece in enumerate(row):
            if piece == EMPTY_SQUARE_ID:
                add_drops_piece(board, player, rank, file, dropped_piece, drops)

    return drops
