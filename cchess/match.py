from typing import Tuple
import random
import cchess
import time


class Match:
    def __init__(self):
        self.board = cchess.Chess()
        self.gameover = False
        self.operations = 0

    def move(self, x: int, y: int, nx: int, ny: int, promote_to: str=None) -> int:
        if not self.board.gatekeeper(x, y, nx, ny, False, promote_to):
            # illegal move
            return 1

        else:
            # checkmate happened
            if self.board.check() and not self.board.has_legal_move():
                self.gameover = True

            # stalemate happened
            elif not self.board.has_legal_move():
                self.gameover = True

            return 0

    def ai_move(self, depth: int=3):
        self.operations = 0
        start_time = time.time()
        best_val, best_move = self.minimax(depth, root=True)
        elapsed = time.time() - start_time
        if elapsed > 0:
            print(f'{self.operations} operations done in {elapsed} seconds, '
                  f'{self.operations//elapsed} ops/s')
        if best_move is not None:
            x, y, nx, ny = best_move
            self.move(x, y, nx, ny, 'queen')
        else:
            print('the AI lost (probably)')

    def minimax(self, depth: int, alpha: int=-90000, beta: int=90000, is_max: bool=True, root: bool=False):
        self.operations += 1
        if depth == 0:
            return -self.board.evaluate(), None

        best_move = None
        legal_moves = self.board.get_legal_moves()
        random.shuffle(legal_moves)

        if root and len(legal_moves) > 0:
            best_move = legal_moves[0]

        best_move_val = 90000
        if is_max:
            best_move_val *= -1

        for move in legal_moves:
            x, y, nx, ny = move
            self.board.execute(x, y, nx, ny, 'queen')
            value, _ = self.minimax(depth-1, alpha, beta, not is_max)
            self.undo()

            if is_max:
                if value > best_move_val:
                    best_move_val = value
                    best_move = move
                alpha = max(alpha, value)
            else:
                if value < best_move_val:
                    best_move_val = value
                    best_move = move
                beta = min(beta, value)

            if beta <= alpha:
                break

        return best_move_val, best_move

    def undo(self):
        self.gameover = False
        self.board.undo()

    def status(self) -> Tuple[bool, bool]:
        # returns the current status of the game (is game over, is stalemate)
        return self.gameover, self.gameover and not self.board.check()
