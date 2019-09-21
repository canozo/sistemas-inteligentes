from abc import ABC, abstractmethod
from typing import List, Tuple
# TODO change the return table in possible_moves


class Piece(ABC):
    eval_white = None
    eval_black = None

    @staticmethod
    def get_laser(movements: Tuple[int, ...], chessboard: List[List[str]], x: int, y: int,
                  is_white: bool, check_mode: bool) -> List[Tuple[int, int]]:
        for i in range(4):
            piece_count = 0
            laser = [(y, x)]
            sum_x = movements[i]
            sum_y = movements[i+1]
            count_x = x + sum_x
            count_y = y + sum_y

            while 0 <= count_x <= 7 and 0 <= count_y <= 7:
                piece = chessboard[count_y][count_x]
                if piece != '':
                    if piece.isupper() == is_white:
                        break
                    elif check_mode and piece.upper() == 'K' and piece_count == 0:
                        return laser
                    elif check_mode:
                        break
                    elif piece.upper() == 'K' and piece_count == 1:
                        return laser
                    else:
                        piece_count += 1
                laser.append((count_y, count_x))
                count_x += sum_x
                count_y += sum_y
        return []

    @staticmethod
    def possible_moves(movements: Tuple[int, ...], table: List[List[bool]],
                       chessboard: List[List[str]], x: int, y: int) -> List[List[bool]]:
        for i in range(4):
            exit_loop = False
            sum_x = movements[i]
            sum_y = movements[i+1]
            count_x = x + sum_x
            count_y = y + sum_y

            while 0 <= count_x <= 7 and 0 <= count_y <= 7 and not exit_loop:
                piece = chessboard[count_y][count_x]
                exit_loop = piece != '' and piece.upper() != 'K'
                table[count_y][count_x] = True
                count_x += sum_x
                count_y += sum_y
        return table

    @staticmethod
    @abstractmethod
    def check_laser(chessboard: List[List[str]], x: int, y: int,
                    is_white: bool, check_mode: bool=False) -> List[Tuple[int, int]]:
        pass

    @staticmethod
    @abstractmethod
    def can_move(x: int, y: int, new_x: int, new_y: int, piece_in_path: bool, is_white: bool) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def controlled(table: List[List[bool]], chessboard: List[List[str]],
                   x: int, y: int, is_white: bool) -> List[List[bool]]:
        pass
