import numpy as np
import time
from collections import defaultdict


class Piece:
    @staticmethod
    class MovementException(Exception):
        pass

    @staticmethod
    def illegal_direction(direction: (int, int)):
        if not (direction[0] == 0 or direction[1] == 0):
            return Piece.MovementException("Pieces can only move in one direction!")
        elif direction[0] not in {1, -1} and direction[1] not in {1, -1}:
            return Piece.MovementException("Direction should be normed!")
        else:
            return Piece.MovementException("Unknown exception occurred")

    def __init__(self, board, piece_id, shape: (int, int), position: (int, int), key=False):
        self.board = board
        self.id = piece_id
        self.shape = shape
        self.position = position
        self.key = key

    def move(self, direction: (int, int)):
        space = self.get_space(direction)
        print("Direction:", direction)
        while self.board.available(space)[0]:
            time.sleep(.5)
            print(f"Current space for {self.id}:", space)
            print(f"Current position for {self.id}:", self.position)
            self.position = add(self.position, direction)
            space = set(add(pair, direction) for pair in space)

    def can_move(self, direction: (int, int)):
        space = self.get_space(direction)
        return self.board.available(space)

    def get_space(self, direction: (int, int)):
        space_shapes = {"vertical": (self.shape[0], 1), "horizontal": (1, self.shape[1])}

        if Board.directions[direction] in {'up', 'down'}:
            space_shape = space_shapes['vertical']
        elif Board.directions[direction] in {'left', 'right'}:
            space_shape = space_shapes['horizontal']
        else:
            raise Piece.illegal_direction(direction)
        space = set()

        if Board.directions[direction] == "down":
            offset = (0, self.shape[1] - 1)
        elif Board.directions[direction] == 'right':
            offset = (self.shape[0] - 1, 0)
        else:
            offset = (0, 0)

        for x_coord in range(space_shape[0]):
            for y_coord in range(space_shape[1]):
                space.add(add(self.position, direction, offset, (x_coord, y_coord)))

        return space


class Board:
    directions = {(1, 0): "right", (-1, 0): "left", (0, 1): "down", (0, -1): "up"}

    def __init__(self, board_json):
        self.board_shape, self.exit_space, self.pieces = self.gen_board(board_json)

    def available(self, space: set):
        for piece in self.pieces:
            for x in range(piece.position[0], piece.position[0] + piece.shape[0]):
                for y in range(piece.position[1], piece.position[1] + piece.shape[1]):
                    if (x, y) in space:
                        return False, f"{(x, y)} occupied by Piece {piece.id}"
        for x, y in space:
            if x < 0 or y < 0 or x >= self.board_shape[0] or y >= self.board_shape[1]:
                return False, f"{(x, y)} out of bounds"
        return True, "ok"

    def gen_board(self, board_json):
        board_shape = board_json['board_shape']
        exit_space = board_json['exit_space']
        pieces = []
        for piece in board_json['pieces']:
            pieces.append(Piece(self, piece['id'], piece['shape'], piece['position'], piece['key']))
        return board_shape, exit_space, pieces

    def solve(self, states: dict, moves: list):
        solved = False
        for piece in self.pieces:
            time.sleep(.1)
            print(f"Trying piece {piece.id}")
            if not solved:
                for direction in Board.directions.keys():
                    can_move, why = piece.can_move(direction)
                    if can_move:
                        piece.move(direction)
                        print(f"Trying: Moved piece {piece.id} {Board.directions[direction]}")
                        if piece.key and self.exit_space == (piece.position, piece.position + piece.shape):
                            solved = True
                            moves.append(f"Moved piece {piece.id} {Board.directions[direction]}")
                        elif not states[self.pieces]:
                            states[self.pieces] = True
                            moves.append(f"Moved piece {piece.id} {Board.directions[direction]}")
                            self.solve(states, moves)
                            states[self.pieces] = False
                            moves.pop()
                            print(f"Moving piece {piece.id} {Board.directions[direction]} failed: no space")
                            piece.move(tuple(np.array(direction)*-1))
                            return
                        else:
                            print(f"Moving piece {piece.id} {Board.directions[direction]} failed: board state already seen")
                            piece.move(tuple(np.array(direction)*-1))
                            return
                    else:
                        print(f"Piece {piece.id} can't move {Board.directions[direction]}: {why}")
        print("solved")
        return


def solve(board: Board):
    states = defaultdict(bool)
    moves = []
    t_i = time.perf_counter()
    board.solve(states, moves)
    time_elapsed = time.perf_counter() - t_i
    print(f"Board solved in {time_elapsed} seconds.")
    for move in moves:
        print(move)


def add(*tuples):
    if len(tuples) == 1:
        return tuples[0]
    else:
        return tuple(np.add(tuples[0], add(*(tuples[1:]))))


if __name__ == "__main__":
    bj = {
            'board_shape': (4, 5),
            'exit_space': ((1, 3), (2, 4)),
            'pieces':
                [
                    {'id': 0, 'shape': (1, 2), 'position': (0, 0), 'key': False},
                    {'id': 1, 'shape': (1, 2), 'position': (0, 2), 'key': False},
                    {'id': 2, 'shape': (1, 1), 'position': (0, 4), 'key': False},
                    {'id': 3, 'shape': (2, 2), 'position': (1, 0), 'key': True},
                    {'id': 4, 'shape': (2, 1), 'position': (1, 2), 'key': False},
                    {'id': 5, 'shape': (1, 1), 'position': (1, 3), 'key': False},
                    {'id': 6, 'shape': (1, 1), 'position': (2, 3), 'key': False},
                    {'id': 7, 'shape': (1, 2), 'position': (3, 0), 'key': False},
                    {'id': 8, 'shape': (1, 2), 'position': (3, 2), 'key': False},
                    {'id': 9, 'shape': (1, 2), 'position': (3, 4), 'key': False},
                ]
         }

    original_board = Board(bj)
    solve(original_board)
