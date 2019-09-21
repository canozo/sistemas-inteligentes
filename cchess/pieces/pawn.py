from .piece import Piece
from typing import List, Tuple


class Pawn(Piece):
    eval_white = [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
                  [1.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0],
                  [5.0, 5.0, 1.0, 2.5, 2.5, 1.0, 5.0, 5.0],
                  [0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0],
                  [5.0, -5.0, -1.0, 0.0, 0.0, -1.0, -5.0, 5.0],
                  [5.0, 1.0, 1.0, -2.0, -2.0, 1.0, 1.0, 5.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

    eval_black = eval_white[::-1]

    @staticmethod
    def check_laser(chessboard: List[List[str]], x: int, y: int,
                    is_white: bool, check_mode: bool=False) -> List[Tuple[int, int]]:
        return []

    @staticmethod
    def can_move(x: int, y: int, new_x: int, new_y: int, piece_in_path: bool, is_white: bool) -> bool:
        dx = abs(x-new_x)
        dy = y-new_y

        if not is_white:
            dy = -dy

        if dx == 0 and dy == 1 and not piece_in_path:
            return True
        elif dx == 1 and dy == 1 and piece_in_path:
            return True
        elif dx == 0 and dy == 2 and not piece_in_path and is_white and y == 6:
            return True
        elif dx == 0 and dy == 2 and not piece_in_path and not is_white and y == 1:
            return True

        return False

    @staticmethod
    def controlled(table: List[List[bool]], chessboard: List[List[str]],
                   x: int, y: int, is_white: bool) -> List[List[bool]]:
        if (is_white and y == 0) or (not is_white and y == 7):
            return table

        if is_white:
            dy = y-1
        else:
            dy = y+1

        if x < 7:
            table[dy][x+1] = True
        if x > 0:
            table[dy][x-1] = True

        return table
