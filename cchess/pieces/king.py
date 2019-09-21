from .piece import Piece
from typing import List, Tuple
import itertools


class King(Piece):
    eval_white = [[-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
                  [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
                  [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
                  [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
                  [-2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
                  [-1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
                  [2.0, 2.0,  0.0,  0.0,  0.0,  0.0, 2.0, 2.0],
                  [2.0, 3.0, 1.0,  0.0,  0.0, 1.0, 3.0, 2.0]]

    eval_black = eval_white[::-1]

    @staticmethod
    def check_laser(chessboard: List[List[str]], x: int, y: int,
                    is_white: bool, check_mode: bool=False) -> List[Tuple[int, int]]:
        return []

    @staticmethod
    def can_move(x: int, y: int, new_x: int, new_y: int, piece_in_path: bool, is_white: bool) -> bool:
        dx = abs(x-new_x)
        dy = abs(y-new_y)
        return (dx == dy == 1) or (dx == 0 and dy == 1) or (dx == 1 and dy == 0)

    @staticmethod
    def controlled(table: List[List[bool]], chessboard: List[List[str]],
                   x: int, y: int, is_white: bool) -> List[List[bool]]:
        for i, j in itertools.product(range(8), repeat=2):
            if King.can_move(x, y, j, i, False, is_white):
                table[i][j] = True
        return table
