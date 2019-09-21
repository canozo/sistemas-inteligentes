from .piece import Piece
from typing import List, Tuple


class Bishop(Piece):
    eval_white = [[-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
                  [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
                  [-1.0, 0.0, 5.0, 1.0, 1.0, 5.0, 0.0, -1.0],
                  [-1.0, 5.0, 5.0, 1.0, 1.0, 5.0, 5.0, -1.0],
                  [-1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, -1.0],
                  [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0],
                  [-1.0, 5.0, 0.0, 0.0, 0.0, 0.0, 5.0, -1.0],
                  [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]]

    eval_black = eval_white[::-1]

    @staticmethod
    def check_laser(chessboard: List[List[str]], x: int, y: int,
                    is_white: bool, check_mode: bool=False) -> List[Tuple[int, int]]:
        return Piece.get_laser((-1, -1, 1, 1, -1), chessboard, x, y, is_white, check_mode)

    @staticmethod
    def can_move(x: int, y: int, new_x: int, new_y: int, piece_in_path: bool, is_white: bool) -> bool:
        return abs(x-new_x) == abs(y-new_y)

    @staticmethod
    def controlled(table: List[List[bool]], chessboard: List[List[str]],
                   x: int, y: int, is_white: bool) -> List[List[bool]]:
        return Piece.possible_moves((-1, -1, 1, 1, -1), table, chessboard, x, y)
