import json
import time
from collections import defaultdict
import itertools
from termcolor import colored, cprint
from random import shuffle
import argparse


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

    def __repr__(self):
        return f"ID:{self.id} POS:{self.position}"

    def move(self, direction: (int, int), undo=False, wait=0):
        space = self.get_space(direction)
        if self.board.available(space)[0]:
            self.board.moved_from = Piece.area(self)
            self.position = add(self.position, direction)
            self.board.last_move = self, undo
            print(self.board.__repr__())
            time.sleep(wait)
            # space = set(add(pair, direction) for pair in space)

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

    @staticmethod
    def area(p):
        area = set()
        for x_coord in range(p.position[0], p.position[0] + p.shape[0]):
            for y_coord in range(p.position[1], p.position[1] + p.shape[1]):
                area.add((x_coord, y_coord))
        return area


class Board:
    directions = {(1, 0): "right", (-1, 0): "left", (0, 1): "down", (0, -1): "up"}

    def __init__(self, board_json):
        self.board_shape, self.exit_space, self.pieces = self.gen_board(board_json)
        self.last_move = None
        self.moved_from = None
        self.shape_colors = self.gen_colors()

    def __repr__(self):
        string_rep = '+' + '-'*self.board_shape[0]*3 + '+\n'
        for y_coord in range(self.board_shape[1]):
            string_rep += '|'
            for x_coord in range(self.board_shape[0]):
                piece = self.get_piece(x_coord, y_coord)
                if piece:
                    colors = self.shape_colors[piece.shape]
                    if self.last_move and piece == self.last_move[0] and not self.last_move[1]:
                        string_rep += colored(f' {piece.id} ', colors[0], colors[1], attrs=['reverse', 'bold'])
                    else:
                        string_rep += colored(f' {piece.id} ', colors[0], colors[1])
                elif self.moved_from and (x_coord, y_coord) in self.moved_from:
                    string_rep += ' # '
                else:
                    string_rep += '   '
            string_rep += '|\n'
        string_rep += '+' + '-' * self.board_shape[0]*3 + '+'
        return string_rep
        # for piece in self.pieces:
        #     string_rep += repr(piece) + "\n"
        # return string_rep[:-1]

    def __str__(self):
        string_rep = ''
        for piece in self.pieces:
            string_rep += repr(piece) + "\n"
        return string_rep[:-1]

    def get_piece(self, x_to_find, y_to_find):
        for piece in self.pieces:
            cover = Piece.area(piece)
            if (x_to_find, y_to_find) in cover:
                return piece

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

    def gen_colors(self):
        shapes = set()
        for piece in self.pieces:
            shapes.add(piece.shape)
        bg_colors = ['on_grey', 'on_red', 'on_magenta', 'on_blue', 'on_green', 'on_yellow', 'on_cyan'][:len(shapes)]
        tx_colors = ['white',   'cyan',   'green',      'yellow',  'magenta',  'blue',      'red'][:len(shapes)]
        return {shape: colors for shape, colors in zip(shapes, zip(tx_colors, bg_colors))}

    def gen_board(self, board_json):
        board_shape = tuple(board_json['board_shape'])
        exit_space = (tuple(coord) for coord in board_json['exit_space'])
        pieces = []
        piece_id = 0
        for piece in board_json['pieces']:
            pieces.append(Piece(self, str(piece_id), tuple(piece['shape']), tuple(piece['position']), piece['key']))
            piece_id += 1
        return board_shape, exit_space, pieces

    def solve(self, states: dict, moves: list, wait=0):

        move_count = 0
        for piece in self.pieces:
            for direction in Board.directions.keys():
                can_move, why = piece.can_move(direction)
                if can_move:
                    move_count += 1

        solved = False
        lock_count = 0
        piece_indices = list(range(len(self.pieces)))
        shuffle(piece_indices)
        for piece_no in itertools.cycle(piece_indices):
            piece = self.pieces[piece_no]
            if lock_count >= move_count:
                # print("stuck, backtracking")
                break

            elif not solved:
                for direction in Board.directions.keys():
                    can_move, why = piece.can_move(direction)
                    if can_move and not solved:
                        print(f'--> {len(moves)+1}')
                        piece.move(direction, wait=wait)
                        # print(f"Trying: Moved piece {piece.id} {Board.directions[direction]}")
                        if piece.key and self.exit_space == (piece.position, piece.position + piece.shape):
                            solved = True
                            moves.append(f"Moved piece {piece.id} {Board.directions[direction]}")
                            break
                        elif not states[str(self)]:
                            states[str(self)] = True
                            moves.append(f"Moved piece {piece.id} {Board.directions[direction]}")
                            solved, state = self.solve(states, moves, wait=wait)
                            states[state] = True
                            moves.pop()
                            print('<--/')
                            piece.move(tuple(coord*-1 for coord in direction), undo=True, wait=wait)
                            states[str(self)] = False
                        else:
                            print('<--#')
                            piece.move(tuple(coord*-1 for coord in direction), undo=True, wait=False)
                            lock_count += 1
                    elif not solved:
                        pass
                        # print(f"Piece {piece.id} can't move {Board.directions[direction]}: {why}")
            else:
                break
        if solved:
            print("solved")
            time.sleep(3)
        else:
            pass
            # print(f"{len(moves)} moves, returning to previous call")
        return solved, str(self)


def solve(board: Board, wait=0):
    time.sleep(wait)
    states = defaultdict(bool)
    moves = []
    t_i = time.perf_counter()
    solved, state = board.solve(states, moves, wait=wait)
    time_elapsed = time.perf_counter() - t_i
    print(f"Board {'' if solved else 'not '}solved in {time_elapsed} seconds.")
    for move in moves:
        print(move)


def add(*tuples):
    if len(tuples) == 1:
        return tuples[0]
    else:
        tuple_1 = tuples[0]
        tuple_2 = add(*(tuples[1:]))
        return tuple_1[0] + tuple_2[0], tuple_1[1] + tuple_2[1]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--step', type=float, action='store',
                        help='Seconds between moves; default is 2')
    parser.add_argument('--json', type=str, action='store',
                        help='Train the models and store them in classifiers/')
    args = parser.parse_args()

    if args.json:
        with open(args.json, 'r') as board:
            bj = json.load(board)
    else:
        bj = json.loads(r"""{
    "board_shape": [4, 5],
    "exit_space": [[1, 3], [2, 4]],
    "pieces":
        [
            {"shape": [1, 2], "position": [0, 0], "key": false},
            {"shape": [1, 2], "position": [0, 2], "key": false},
            {"shape": [1, 1], "position": [0, 4], "key": false},
            {"shape": [2, 2], "position": [1, 0], "key": true},
            {"shape": [2, 1], "position": [1, 2], "key": false},
            {"shape": [1, 1], "position": [1, 3], "key": false},
            {"shape": [1, 1], "position": [2, 3], "key": false},
            {"shape": [1, 2], "position": [3, 0], "key": false},
            {"shape": [1, 2], "position": [3, 2], "key": false},
            {"shape": [1, 1], "position": [3, 4], "key": false}
        ]
}""")

    if args.step:
        step = args.step
    else:
        step = 2

    cprint('Welcome to Klotski Solver!', attrs=['bold', 'underline'])
    time.sleep(max(2, step))
    original_board = Board(bj)
    print("Game Start")
    print(original_board.__repr__())
    solve(original_board, wait=step)
