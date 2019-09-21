from typing import List, Tuple, Type
from pieces.piece import Piece
from pieces.rook import Rook
from pieces.bishop import Bishop
from pieces.knight import Knight
from pieces.queen import Queen
from pieces.king import King
from pieces.pawn import Pawn
import itertools

piece_num = {
    'p': -1,
    'r': -2,
    'n': -3,
    'b': -4,
    'q': -5,
    'k': -6,
    'b': -7,
    'n': -8,
    'r': -9,
    'P': 1,
    'R': 2,
    'N': 3,
    'B': 4,
    'Q': 5,
    'K': 6,
    'B': 7,
    'N': 8,
    'R': 9,
    ' ': 0
}


class Chess:
    def __init__(self):
        # game settings
        self.history = []
        self.white_turn = True
        self.en_passant = False
        self.en_passant_x = -1
        self.en_passant_y = -1
        self.white_controlled = None  # type: List[List[bool]]
        self.black_controlled = None  # type: List[List[bool]]
        self.chessboard = [['' for _ in range(8)] for _ in range(8)]  # type: List[List[str]]

        # initial position
        self.chessboard[0][0] = 'r'
        self.chessboard[0][1] = 'n'
        self.chessboard[0][2] = 'b'
        self.chessboard[0][3] = 'q'
        self.chessboard[0][4] = 'k'
        self.chessboard[0][5] = 'b'
        self.chessboard[0][6] = 'n'
        self.chessboard[0][7] = 'r'

        self.chessboard[1][0] = 'p'
        self.chessboard[1][1] = 'p'
        self.chessboard[1][2] = 'p'
        self.chessboard[1][3] = 'p'
        self.chessboard[1][4] = 'p'
        self.chessboard[1][5] = 'p'
        self.chessboard[1][6] = 'p'
        self.chessboard[1][7] = 'p'

        self.chessboard[7][0] = 'R'
        self.chessboard[7][1] = 'N'
        self.chessboard[7][2] = 'B'
        self.chessboard[7][3] = 'Q'
        self.chessboard[7][4] = 'K'
        self.chessboard[7][5] = 'B'
        self.chessboard[7][6] = 'N'
        self.chessboard[7][7] = 'R'

        self.chessboard[6][0] = 'P'
        self.chessboard[6][1] = 'P'
        self.chessboard[6][2] = 'P'
        self.chessboard[6][3] = 'P'
        self.chessboard[6][4] = 'P'
        self.chessboard[6][5] = 'P'
        self.chessboard[6][6] = 'P'
        self.chessboard[6][7] = 'P'

        # iniial controlled squares
        self.update_controlled()

    def gatekeeper(self, x: int, y: int, nx: int, ny: int, review_mode: bool, promote_to: str='', debug: bool=False) -> bool:
        legal = True
        piece = self.chessboard[y][x]
        destination = self.chessboard[ny][nx]
        piece_class = self.get_class(piece)

        # check that a piece was selected
        if piece == '':
            legal = False
        else:
            # piece selected was of the players color
            if self.white_turn != piece.isupper():
                legal = False

            # no friendly fire
            if legal and destination != '' and self.white_turn == destination.isupper():
                legal = False

            # check if player wants to castle
            if legal and piece.upper() == 'K' and not self.check() and abs(x-nx) == 2:
                legal = self.can_castle(x, y, nx, ny)

            # check if can do en passant
            elif legal and self.en_passant and piece.upper() == 'P'\
                    and nx == self.en_passant_x and ny == self.en_passant_y:
                legal = Pawn.can_move(x, y, nx, ny, True, piece.isupper())

            #  all normal moves
            elif legal and not piece_class.can_move(x, y, nx, ny, destination != '', piece.isupper()):
                legal = False

            # check that there's no jumping pieces
            if legal and piece.upper() not in ('N', 'K'):
                legal = not self.jumps(x, y, nx, ny)

            # check white king doesn't move to a controlled square
            if legal and piece.upper() == 'K' and self.white_turn and self.black_controlled[ny][nx]:
                legal = False

            # check black king doesn't move to a controlled square
            elif legal and piece.upper() == 'K' and not self.white_turn and self.white_controlled[ny][nx]:
                legal = False

            # check that we're not moving pinned pieces
            if legal and piece.upper() != 'K' and self.check_laser(x, y, nx, ny):
                legal = False

            # check if the player can promote
            if legal and piece.upper() == 'P' \
                    and ((self.white_turn and ny == 0) or (not self.white_turn and ny == 7)):
                legal = promote_to in ('queen', 'rook', 'bishop', 'knight')
            else:
                promote_to = ''

            # if the player is in check, see if he manages to get out of check
            if legal and self.check():
                attacking_pieces = self.get_attacking()

                # moving outside of check
                if piece.upper() == 'K':
                    if self.white_turn and self.black_controlled[ny][nx]:
                        legal = False
                    elif not self.white_turn and self.white_controlled[ny][nx]:
                        legal = False

                # if the king is being attacked by more than one piece, there's no way to block or take both of them
                elif len(attacking_pieces) > 1:
                    # TODO bug con GiuocoPiano.pgn #4
                    legal = False

                # take the attacking piece
                elif destination != '':
                    if (ny, nx) != attacking_pieces[0]:
                        legal = False

                # block the attacking piece
                elif destination == '':
                    # TODO bug con GiuocoPiano.pgn #1 y #2
                    ty, tx = attacking_pieces[0]
                    if (ny, nx) not in self.check_block(tx, ty, not self.white_turn):
                        legal = False

        if not review_mode and legal:
            self.execute(x, y, nx, ny, promote_to)

        return legal

    def execute(self, x: int, y: int, nx: int, ny: int, promote_to: str) -> None:
        game_state = (self.shittycopy(),
                      self.white_turn,
                      self.en_passant,
                      self.en_passant_x,
                      self.en_passant_y)
        self.history.append(game_state)

        if self.chessboard[y][x].upper() == 'K':
            if nx-x == 2:
                self.chessboard[y][nx-1] = self.chessboard[y][nx+1]
                self.chessboard[y][nx+1] = ''

            elif nx-x == -2:
                self.chessboard[y][nx+1] = self.chessboard[y][nx-2]
                self.chessboard[y][nx-2] = ''

        if self.en_passant and self.chessboard[y][x].upper() == 'P'\
                and ny == self.en_passant_y and nx == self.en_passant_x:
            if self.white_turn:
                self.chessboard[ny+1][nx] = ''
            else:
                self.chessboard[ny-1][nx] = ''

        if promote_to != '' and self.chessboard[y][x].upper() == 'P'\
                and ((self.white_turn and ny == 0) or (not self.white_turn and ny == 7)):
            if promote_to == 'queen':
                self.chessboard[ny][nx] = 'q'

            elif promote_to == 'knight':
                self.chessboard[ny][nx] = 'n'

            elif promote_to == 'bishop':
                self.chessboard[ny][nx] = 'b'

            elif promote_to == 'rook':
                self.chessboard[ny][nx] = 'r'

            if self.white_turn:
                self.chessboard[ny][nx] = self.chessboard[ny][nx].upper()

        else:
            self.chessboard[ny][nx] = self.chessboard[y][x]

        if self.en_passant:
            self.en_passant = False

        # get ready for a possible en passant on next turn
        if self.chessboard[ny][nx].upper() == 'P' and abs(y - ny) == 2:
            self.en_passant = True
            self.en_passant_x = x
            if self.white_turn:
                self.en_passant_y = y - 1
            elif not self.white_turn:
                self.en_passant_y = y + 1

        self.white_turn = not self.white_turn
        self.chessboard[y][x] = ''
        self.update_controlled()

    def shittycopy(self):
        chessboard = [['' for _ in range(8)] for _ in range(8)]
        for i, j in itertools.product(range(8), repeat=2):
            chessboard[i][j] = self.chessboard[i][j]
        return chessboard

    def undo(self):
        if len(self.history) > 0:
            self.chessboard, self.white_turn, self.en_passant, self.en_passant_x, self.en_passant_y = self.history.pop()
            self.update_controlled()

    def get_attacking(self) -> List[Tuple[int, int]]:
        attacking = []
        king_y = king_x = 0

        for i, j in itertools.product(range(8), repeat=2):
            piece = self.chessboard[i][j]
            if piece != '' and piece.upper() == 'K' and piece.isupper() == self.white_turn:
                king_x = j
                king_y = i

        for i, j in itertools.product(range(8), repeat=2):
            piece = self.chessboard[i][j]
            if piece != '' and piece.isupper() != self.white_turn:
                piece_class = self.get_class(piece)
                table = piece_class.controlled(
                    [[False for _ in range(8)] for _ in range(8)], self.chessboard, j, i, piece.isupper())
                if table[king_y][king_x]:
                    attacking.append((i, j))
        return attacking

    def can_castle(self, x: int, y: int, nx: int, ny: int) -> bool:
        dx = nx - x
        dy = ny - y

        if dy:
            return False

        if dx > 0:
            rook_x = nx + 1
            increment = 1
        else:
            rook_x = nx - 2
            increment = -1

        if rook_x < 0 or rook_x > 7:
            return False

        if self.chessboard[y][rook_x] == '':
            return False

        # TODO: check if they have moved
        # if self.chessboard[y][rook_x].has_moved or self.chessboard[y][x].has_moved:
        #     return False

        if self.jumps(x, y, rook_x, ny):
            return False

        i = x
        while i != nx + increment:
            if self.chessboard[y][x].isupper() and self.black_controlled[y][i]:
                return False
            elif not self.chessboard[y][x].isupper() and self.white_controlled[y][i]:
                return False
            i += increment

        return True

    def check_block(self, x: int, y: int, is_white: bool) -> List[Tuple[int, int]]:
        laser = []
        piece = self.chessboard[y][x]
        if piece.upper() in ('Q', 'R', 'B'):
            piece_class = self.get_class(piece)
            laser = piece_class.check_laser(self.chessboard, x, y, is_white, True)
        return laser

    def check_laser(self, x: int, y: int, nx: int, ny: int) -> bool:
        # is there a pin and am I executing correctly
        for i, j in itertools.product(range(8), repeat=2):
            piece = self.chessboard[i][j]
            if piece == '':
                continue
            if piece.isupper() == self.white_turn:
                continue
            if piece.upper() not in ('Q', 'R', 'B', 'N'):
                continue
            piece_class = self.get_class(piece)

            # is it pinning me?
            laser = piece_class.check_laser(self.chessboard, j, i, piece.isupper())
            if len(laser) == 0:
                continue
            if (y, x) not in laser:
                continue

            # am I moving outside of the laser?
            return (ny, nx) not in laser
        return False

    def jumps(self, x: int, y: int, nx: int, ny: int) -> bool:
        dx = abs(x-nx)
        dy = abs(y-ny)

        # check vertically
        if not dx:
            if ny-y < 0:
                increment = -1
            else:
                increment = 1

            i = y + increment
            while i != ny:
                if self.chessboard[i][nx] != '':
                    return True
                i += increment

        # check horizontally
        elif not dy:
            if nx-x < 0:
                increment = -1
            else:
                increment = 1

            i = x + increment
            while i != nx:
                if self.chessboard[ny][i] != '':
                    return True
                i += increment

        # check diagonally
        elif dx == dy:
            if nx-x < 0:
                increment_x = -1
            else:
                increment_x = 1

            if ny-y < 0:
                increment_y = -1
            else:
                increment_y = 1

            ix = x + increment_x
            iy = y + increment_y
            while ix != nx and iy != ny:
                if self.chessboard[iy][ix] != '':
                    return True
                ix += increment_x
                iy += increment_y

        return False

    def update_controlled(self) -> None:
        self.white_controlled = [[False for _ in range(8)] for _ in range(8)]
        self.black_controlled = [[False for _ in range(8)] for _ in range(8)]

        for i, j in itertools.product(range(8), repeat=2):
            piece = self.chessboard[i][j]
            if piece == '':
                continue
            piece_class = self.get_class(piece)
            if piece.isupper():
                self.white_controlled = piece_class.controlled(self.white_controlled, self.chessboard, j, i, True)
            else:
                self.black_controlled = piece_class.controlled(self.black_controlled, self.chessboard, j, i, False)

    def check(self) -> bool:
        king_y = king_x = 0
        for i, j in itertools.product(range(8), repeat=2):
            piece = self.chessboard[i][j]
            if piece.upper() == 'K' and piece.isupper() == self.white_turn:
                king_x = j
                king_y = i

        if self.white_turn:
            return self.black_controlled[king_y][king_x]
        else:
            return self.white_controlled[king_y][king_x]

    def has_legal_move(self) -> bool:
        for i, j, k, l in itertools.product(range(8), repeat=4):
            if self.gatekeeper(j, i, l, k, True, 'bishop'):
                return True
        return False

    def get_legal_moves(self) -> List[Tuple[int, int, int, int]]:
        moves = []
        for i, j, k, l in itertools.product(range(8), repeat=4):
            if self.gatekeeper(j, i, l, k, True, 'rook'):
                moves.append((j, i, l, k))
        return moves

    @staticmethod
    def get_class(piece_char: str) -> Type[Piece]:
        piece = piece_char.upper()
        if piece == 'P':
            return Pawn
        elif piece == 'N':
            return Knight
        elif piece == 'B':
            return Bishop
        elif piece == 'R':
            return Rook
        elif piece == 'Q':
            return Queen
        elif piece == 'K':
            return King
        else:
            return Piece

    def evaluate(self) -> float:
        # score based on the white side
        score = 0
        for i, j in itertools.product(range(8), repeat=2):
            piece_value = 0
            piece = self.chessboard[i][j]
            if piece == '':
                continue
            piece_class = self.get_class(piece)
            if piece.upper() == 'P':
                piece_value = 10
            elif piece.upper() == 'N':
                piece_value = 30
            elif piece.upper() == 'B':
                piece_value = 30
            elif piece.upper() == 'R':
                piece_value = 50
            elif piece.upper() == 'Q':
                piece_value = 90
            elif piece.upper() == 'K':
                piece_value = 900
            if piece.isupper():
                piece_value += piece_class.eval_white[i][j]
            else:
                piece_value += piece_class.eval_black[i][j]
                piece_value *= -1
            score += piece_value
        return score

    def pretty_str(self):
        res = ''
        for i, row in enumerate(self.chessboard):
            for piece in row:
                if piece == '':
                    res += ' '
                else:
                    res += piece
            res += f'| {8 - i}\n'
        res += '--------\n'
        res += 'abcdefgh'
        return res

    def numify(self):
        res = []
        for i, j in itertools.product(range(8), repeat=2):
            if self.chessboard[i][j] == '':
                res.append(0)
            else:
                res.append(1)
        return res
