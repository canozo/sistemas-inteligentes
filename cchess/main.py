from match import Match
from pyglet.window import mouse
from pyglet.window import key
import pyglet
import itertools
import sys
import chess.pgn
import io
import numpy as np
import tensorflow as tf
from utils import *
from ops import *

MOVE_LIMIT = 6
GAME_LIMIT = 100

promotions = {
    '': '',
    'q': 'queen',
    'r': 'rook',
    'b': 'bishop',
    'n': 'knight'
}

promotions_num = ['', 'q', 'r', 'b', 'n']

known_size = 0
move_dict = {}
dict_move = []

train_games = []
train_labels = []

x_valid = []
y_valid = []

def add_game(game):
    global known_size
    count = 0
    this_match = Match()
    board = game.board()
    for move in game.mainline_moves():
        if count >= MOVE_LIMIT:
            # solo tomar el opening del juego
            return

        the_board = this_match.board.numify()
        strmove = str(move)
        p = ''
        ox = 'abcdefgh'.find(strmove[0])
        oy = '87654321'.find(strmove[1])
        nx = 'abcdefgh'.find(strmove[2])
        ny = '87654321'.find(strmove[3])
        if len(str(move)) > 4:
            p = strmove[4]

        error = this_match.move(ox, oy, nx, ny, promotions[p])
        if error:
            return

        count += 1
        tp_move = f'{ox}{oy}{nx}{ny}{promotions_num.index(p)}'
        if tp_move not in move_dict:
            # agregar el mov al diccionario
            print(f'agregando movimiento desconocido: {tp_move}')
            move_dict[tp_move] = known_size
            dict_move.append(tp_move)
            known_size += 1

        temp = [0 for _ in range(known_size)]
        temp[move_dict[tp_move]] = 1
        train_games.append(the_board)
        train_labels.append(temp)

if len(sys.argv) == 1:
    print('debe enviar nombre del archivo PGN como arg')
    exit()

args = sys.argv[1:]

for arg in args:
    pgn = open(arg)
    game = chess.pgn.read_game(pgn)
    limit = 0
    curr_pos = len(train_games)
    while game is not None and limit < GAME_LIMIT:
        if not game.errors:
            add_game(game)
        game = chess.pgn.read_game(pgn)
        limit += 1

    # agregar los juegos a los valid
    x_valid += train_games[curr_pos:]
    y_valid += train_labels[curr_pos:]

# fill los demas arrays
for label in train_labels[:-1]:
    label += [0] * (known_size - len(label))

# tf
data = np.array(train_games)
labels = np.array(train_labels)

print(f'labels.shape: {labels.shape}')
print(f'labels: {labels}')
print(f'move_dict: {move_dict}')
print(f'dict_move: {dict_move}')
print(f'number of labels: {len(labels)}')

x_train, y_train = data[:9000], labels[:9000]

x_valid = np.array(x_valid)
y_valid = np.array(y_valid)

img_h = img_w = 8
img_size_flat = img_h * img_w
n_classes = known_size

# parametros
learning_rate = 0.001  # The optimization initial learning rate
epochs = 30  # Total number of training epochs
batch_size = 100  # Training batch size
display_freq = 100  # Frequency of displaying the training results

# graph, modelo lineal
x = tf.compat.v1.placeholder(tf.float32, shape=[None, img_size_flat], name='X')
y = tf.compat.v1.placeholder(tf.float32, shape=[None, n_classes], name='Y')

W = weight_variable(shape=[img_size_flat, n_classes])

# bias
b = bias_variable(shape=[n_classes])

output_logits = tf.matmul(x, W)
y_pred = tf.nn.softmax(output_logits)

# nuestro modelo de predicciones
cls_prediction = tf.argmax(output_logits, axis=1, name='predictions')

# loss, optimizer, y accuracy
loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y, logits=output_logits), name='loss')
optimizer = tf.compat.v1.train.AdamOptimizer(learning_rate=learning_rate, name='Adam-op').minimize(loss)
correct_prediction = tf.equal(tf.argmax(output_logits, 1), tf.argmax(y, 1), name='correct_pred')
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32), name='accuracy')

init = tf.compat.v1.global_variables_initializer()

# iniciar sesion
sess = tf.compat.v1.Session()
sess.run(init)
global_step = 0

num_tr_iter = int(len(y_train) / batch_size)
for epoch in range(epochs):
    print('Training epoch: {}'.format(epoch + 1))
    x_train, y_train = randomize(x_train, y_train)
    for iteration in range(num_tr_iter):
        global_step += 1
        start = iteration * batch_size
        end = (iteration + 1) * batch_size
        x_batch, y_batch = get_next_batch(x_train, y_train, start, end)

        # Run optimization op (backprop)
        feed_dict_batch = {x: x_batch, y: y_batch}
        sess.run(optimizer, feed_dict=feed_dict_batch)

        if iteration % display_freq == 0:
            # Calculate and display the batch loss and accuracy
            loss_batch, acc_batch = sess.run([loss, accuracy],
                                            feed_dict=feed_dict_batch)

            print('iter {0:3d}:\t Loss={1:.2f},\tTraining Accuracy={2:.01%}'.
                format(iteration, loss_batch, acc_batch))

    # Run validation after every epoch
    feed_dict_valid = {x: x_valid, y: y_valid}
    loss_valid, acc_valid = sess.run([loss, accuracy], feed_dict=feed_dict_valid)
    print('---------------------------------------------------------')
    print('Epoch: {0}, validation loss: {1:.2f}, validation accuracy: {2:.01%}'.
        format(epoch + 1, loss_valid, acc_valid))
    print('---------------------------------------------------------')

game_window = pyglet.window.Window(height=512, width=512)
message_label = pyglet.text.Label(font_name='Times New Roman',
                                  font_size=36,
                                  color=(35, 203, 35, 255),
                                  x=game_window.width // 2,
                                  y=game_window.height // 2,
                                  anchor_x='center',
                                  anchor_y='center')
board_normal = pyglet.sprite.Sprite(pyglet.image.load('resources/board-normal.png'))
board_imgs = [[None for _ in range(8)] for _ in range(8)]
piece_held = None
match = Match()
ai_mode = True
promotion = None
old_pos = (0, 0)


def update_board():
    for i, j in itertools.product(range(8), repeat=2):
        piece = match.board.chessboard[i][j]
        if piece == '':
            continue
        if piece.isupper():
            piece_name = f'{piece}w'
        else:
            piece_name = f'{piece}b'
        board_imgs[i][j] = pyglet.sprite.Sprite(pyglet.image.load(f'resources/{piece_name}.png'))


@game_window.event
def on_draw():
    game_window.clear()
    board_normal.draw()
    chessboard = match.board.chessboard
    for x, y in itertools.product(range(8), repeat=2):
        if chessboard[y][x] != '':
            piece = board_imgs[y][x]
            if piece != piece_held:
                piece.x = x * 64
                piece.y = 448 - y * 64
            piece.draw()

    gameover, stalemate = match.status()
    if stalemate:
        message_label.text = 'Stalemate!'
        message_label.draw()
    elif gameover:
        if match.board.white_turn:
            message_label.text = 'Checkmate. Black won!'
        else:
            message_label.text = 'Checkmate. White won!'
        message_label.draw()


@game_window.event
def on_mouse_press(x, y, button, modifiers):
    global piece_held, old_pos
    if button == mouse.LEFT and not match.gameover:
        chessboard = match.board.chessboard
        piece = chessboard[7 - y//64][x//64]
        if piece != '':
            piece_held = board_imgs[7 - y//64][x//64]
            old_pos = (x//64, 7 - y//64)


@game_window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    if piece_held is not None:
        piece_held.x = x - 32
        piece_held.y = y - 32


@game_window.event
def on_mouse_release(xx, y, button, modifiers):
    global piece_held
    if piece_held is not None:
        dx, dy = xx//64, 7 - y//64
        ox, oy = old_pos
        error = match.move(ox, oy, dx, dy, promotion)
        update_board()
        if not error and ai_mode:
            np_board = np.array([match.board.numify()])
            [pred] = sess.run(cls_prediction, feed_dict={x: np_board})
            ox, oy, dx, dy, p = list(dict_move[pred])
            error = match.move(int(ox), int(oy), int(dx), int(dy), promotions_num[int(p)])
            if error:
                # tensorflow no puedo con el move, acudir a minimax
                match.ai_move()
            update_board()

    piece_held = None


@game_window.event
def on_text(text):
    if text == 'm':
        np_board = np.array([match.board.numify()])
        [pred] = sess.run(cls_prediction, feed_dict={x: np_board})
        ox, oy, dx, dy, p = list(dict_move[pred])
        error = match.move(int(ox), int(oy), int(dx), int(dy), promotions_num[int(p)])
        if error:
            # tensorflow no puedo con el move, acudir a minimax
            match.ai_move()
        update_board()
    elif text == 'u':
        match.undo()
        update_board()


@game_window.event
def on_key_press(symbol, modifiers):
    global match, promotion, ai_mode
    if symbol == key.N:
        match = Match()
        update_board()
    elif symbol == key.A:
        ai_mode = not ai_mode
    elif symbol == key.Q:
        promotion = 'queen'
    elif symbol == key.B:
        promotion = 'bishop'
    elif symbol == key.R:
        promotion = 'rook'
    elif symbol == key.K:
        promotion = 'knight'


@game_window.event
def on_close():
    sess.close()


# @game_window.event
# def on_key_release(symbol, modifiers):
#     global promotion
#     if symbol in (key.Q, key.B, key.R, key.K):
#         promotion = None


def main():
    update_board()
    pyglet.app.run()


if __name__ == '__main__':
    main()
