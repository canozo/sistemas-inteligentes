from match import Match
import sys
import chess.pgn
import io

promotions = {
    'q': 'queen',
    'r': 'rook',
    'b': 'bishop',
    'n': 'knight'
}

def main(args):
    for arg in args:
        pgn = open(arg)
        game = chess.pgn.read_game(pgn)
        while game is not None:
            if not game.errors:
                add_game(game)
            game = chess.pgn.read_game(pgn)


def add_game(game):
    match = Match()
    board = game.board()
    for move in game.mainline_moves():
        strmove = str(move)
        p = ''
        ox = 'abcdefgh'.find(strmove[0])
        oy = '87654321'.find(strmove[1])
        nx = 'abcdefgh'.find(strmove[2])
        ny = '87654321'.find(strmove[3])
        if len(str(move)) > 4:
            p = promotions[strmove[4]]

        error = match.move(ox, oy, nx, ny, p)
        if error:
            print(str(match.board))
            print(strmove)
            print(f'Gatekeeper again: {match.board.gatekeeper(ox, oy, nx, ny, False, p, True)}')
            return

if __name__ == '__main__':
    main(sys.argv[1:])
