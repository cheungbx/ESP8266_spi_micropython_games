# tetris.py
#
# ESP8266 (node MCU D1 mini)  micropython game for Tetris
# by Billy Cheung  2019 08 31
#
# SPI OLED
# GND
# VCC
# D0/Sck - D5 (=GPIO14=HSCLK)
# D1/MOSI- D7 (=GPIO13=HMOSI)
# RES    - D0 (=GPIO16)
# DC     - D4 (=GPIO2)
# CS     - D3 (=GPIO0)
# Speaker
# GPIO15   D8  Speaker
# n.c.   - D6  (=GPIO13=HMOSI)
#
# GPIO5    D1——   On to read ADC for Btn
# GPIO4    D2——   On to read ADC for Paddle
#
# buttons   A0
# A0 VCC-9K-U-9K-L-12K-R-9K-D-9K-A-12K-B-9K-GND
#
import gc
import sys
gc.collect()
print (gc.mem_free())
import utime
from utime import sleep_ms
import network
from math import sqrt
# all dislplay, buttons, paddle, sound logics are in game8266.mpy module
from game8266 import Game8266, Rect
g=Game8266()

g.frameRate = 30

# size = width, height = 200, 400
size = width, height = 64, 128
# color = {'black': (0, 0, 0), 'white':(255, 255, 255)}
color ={'black': 0, 'white':1}
sqrsize = 6
occupied_squares = []
top_of_screen = (0, 0)
top_x, top_y = top_of_screen[0], top_of_screen[1]
num_block = 4
pen_size = 1
mov_delay, r_delay = 300, 50
board_centre = 25
no_move = 0
events = {276: 'left', 275: 'right', 112: 'pause'}


def draw_board():
    pass

def drawScore () :
  global score, level
  g.display.text('S:{}'.format (score), 0,0,1)
  g.display.text('L:{}'.format (level), 50,0,1)

def draw_shape(shp_blcks):
    '''this draws list of blocks or a block to the background and blits
    background to screen'''
    if isinstance(shp_blcks, list):
        for blck in shp_blcks:
            g.display.fill_rect(blck.x, blck.y, sqrsize, sqrsize, 1)
    else:
        g.display.rect(blck.x, blck.y, sqrsize, sqrsize,1)


def row_filled(row_no):
    '''check if a row is fully occupied by a shape block'''
    for x_coord in range(0, width, sqrsize):
        if (x_coord, row_no) in occupied_squares:
            continue
        else:
            return False
    return True


def delete_row(row_no):
    '''removes all squares on a row from the occupied_squares list and then
    moves all square positions which have y-axis coord less than row_no down
    board'''
    global occupied_squares
    new_buffer = []
    x_coord, y_coord = 0, 1
    g.display.fill(1)
    for sqr in occupied_squares:
        if sqr[y_coord] != row_no:
            new_buffer.append(sqr)
    occupied_squares = new_buffer
    for index in range(len(occupied_squares)):
        if occupied_squares[index][y_coord] < row_no:
            occupied_squares[index] = (occupied_squares[index][x_coord],
                                    occupied_squares[index][y_coord] + sqrsize)
    for sqr in occupied_squares:
        rect = Rect(sqr[x_coord], sqr[y_coord], sqrsize, sqrsize)
        draw_shape(rect)


def move(shape_blcks, direction):
    '''input:- list of blocks making up a tetris shape
    output:- list of blocks making up a tetris shape
    function moves the input list of blocks that make up shape and then checks
    that the  list of blocks are all in positions that are valide. position is
    valid if it has not been occupied previously and is within the tetris board.
    If move is successful, function returns the moved shape and if move is not
    possible, function returns a false'''
    directs = {'down':(no_move, sqrsize), 'left':(-sqrsize, no_move),
        'right':(sqrsize, no_move), 'pause': (no_move, no_move)}
    delta_x, delta_y = directs[direction]
    for index in range(num_block):
        shape_blcks[index] = shape_blcks[index].move(delta_x, delta_y)

    if legal(shape_blcks):
        for index in range(num_block):
            g.display_rect(shape_blcks[index].move(-delta_x, -delta_y), 1)
        return True
    else:
        for index in range(num_block):
            shape_blcks[index] = shape_blcks[index].move(-delta_x, -delta_y)
        return False


def legal(shape_blcks):
    '''input: list of shape blocks
    checks whether a shape is in a legal portion of the board as defined in the
    doc of 'move' function'''

    for index in range(num_block):
        new_x, new_y = (shape_blcks[index].x, shape_blcks[index].y)

        if (((new_x, new_y) in occupied_squares or new_y >= height) or
            (new_x >= width or new_x < top_x)): #probly introduced a bug by removing the check for shape being less that y-axis origin
            return False
    return True


def create_newshape(start_x=0, start_y=0):
    '''A shape is a list of four rectangular blocks.
    Input:- coordinates of board at which shape is to be created
    Output:- a list of the list of the coordinates of constituent blocks of each
    shape relative to a reference block and shape name. Reference block  has
    starting coordinates of start_x and start_y. '''
    shape_names = ['S', 'O', 'I', 'L', 'T']
    shapes = {'S':[(start_x + 1*sqrsize, start_y + 2*sqrsize),
        (start_x, start_y), (start_x, start_y + 1*sqrsize),(start_x + 1*sqrsize,
                                                    start_y + 1*sqrsize)],

        'O':[(start_x + 1*sqrsize, start_y + 1*sqrsize), (start_x, start_y),
            (start_x, start_y + 1*sqrsize), (start_x + 1*sqrsize, start_y)],

        'I':[(start_x, start_y + 3*sqrsize), (start_x, start_y),
            (start_x, start_y + 2*sqrsize), (start_x, start_y + 1*sqrsize)],

        'L':[(start_x + 1*sqrsize, start_y + 2*sqrsize), (start_x, start_y),
            (start_x, start_y + 2*sqrsize), (start_x, start_y + 1*sqrsize)],

        'T':[(start_x + 1*sqrsize, start_y + 1*sqrsize),(start_x, start_y),
            (start_x - 1*sqrsize, start_y + 1*sqrsize),(start_x,
                                                        start_y + 1*sqrsize)]
        }
    a_shape = g.random(0, 4)
    return shapes[shape_names[a_shape]], shape_names[a_shape]
    #return shapes['O'], 'O' #for testing


def rotate(shape_blcks, shape):
    '''input:- list of shape blocks
    ouput:- list of shape blocks
    function tries to rotate ie change orientation of blocks in the shape
    and this applied depending on the shape for example if a 'O' shape is passed
    to this function, the same shape is returned because the orientation of such
    shape cannot be changed according to tetris rules'''
    if shape == 'O':
        return shape_blcks
    else:
        #global no_move, occupied_squares, background

        shape_coords = [(block[0], block[1]) for
            block in shape_blcks]

        ref_shape_ind = 3 # index of block along which shape is rotated
        start_x, start_y = (shape_coords[ref_shape_ind].x,
                            shape_coords[ref_shape_ind].y)
        new_shape_blcks = [(start_x + start_y-shape_coords[0][1],
                            start_y - (start_x - shape_coords[0][0])),
            (start_x + start_y-shape_coords[1][1],
             start_y - (start_x - shape_coords[1][0])),
            (start_x + start_y-shape_coords[2][1],
             start_y - (start_x - shape_coords[2][0])),
            (shape_coords[3][0], shape_coords[3][1])]
        if legal(new_shape_blcks):
            for index in range(num_block): # paint over the previous shape
                g.display_rect(shape_blcks[index], 1)
            return [Rect(block[0], block[1], sqrsize, sqrsize) for block in new_shape_blcks]
        else:
            return shape_blcks

exitGame = False

while not exitGame:
  gameOver = False
  demo = False
  life = 3
  Score = 0

  #menu screen
  while True:
    g.display.fill(0)
    g.display.text('Tetris', 0, 0, 1)
    g.display.rect(90,0, g.max_vol*4+2,6,1)
    g.display.fill_rect(91,1, g.vol * 4,4,1)
    g.display.text('A Start  L Quit', 0, 10,  1)
    if demo :
        g.display.text('D AI-Player', 0,30, 1)
    else :
        g.display.text('D 1-Player', 0,30, 1)
    g.display.text('R Frame/s {}'.format(g.frameRate), 0,40, 1)
    g.display.text('B + U/D Sound', 0, 50, 1)
    g.display.show()

    g.getBtn()
    if g.setVol() :
        pass
    elif g.justReleased(g.btnL) :
        exitGame = True
        gameOver= True
        break
    elif g.justPressed(g.btnA) :
        if demo :
            g.display.fill(0)
            g.display.text('DEMO', 5, 0, 1)
            g.display.text('B to Stop', 5, 30, 1)
            g.display.show()
            sleep_ms(1000)
        break
    elif g.justPressed(g.btnD) :
        demo = not demo
    elif g.justPressed(g.btnR) :
        if g.pressed(g.btnB) :
            g.frameRate = g.frameRate - 5 if g.frameRate > 5 else 100
        else :
            g.frameRate = g.frameRate + 5 if g.frameRate < 100 else 5

  draw_board()
  # game loop
  while not gameOver:
    curr_shape = create_newshape(board_centre)
    l_of_blcks_ind = 0
    shape_name_ind = 1

    move_dir = 'down' #default move direction
    game = 'playing'  #default game state play:- is game paused or playing

    shape_blcks = [Rect(block[0], block[1],
        sqrsize, sqrsize) for block in curr_shape[l_of_blcks_ind]]
    if legal(shape_blcks):
        draw_shape(shape_blcks)
    else:
        break  #game over
    while True:
        g.getBtn()
        if game == 'paused':
            if g.justPressed(g.btnU) :
                game = 'playing'
        else:
            if g.justPressed(g.btnB) :
                gameOver = True
            elif g.justPressed(g.btnD) :
                mov_delay = 50
                continue
            elif g.justPressed(g.btnA) :
                shape_blcks = rotate(shape_blcks, curr_shape[shape_name_ind])
                draw_shape(shape_blcks)
                sleep_ms(r_delay)
                continue
            elif g.pressed(g.btnL | g.btnR):
                move_dir = 'left' if g.pressed(g.BtnL) else 'right'
                mov_delay = 50
                move (shape_blcks, move_dir)
                draw_shape(shape_blcks)
                sleep_ms(mov_delay)
                continue
            elif g.justPressed(g.btnU) :
                if mov_delay != 300:
                    mov_delay = 300
                move_dir  = 'down'
            moved = move(shape_blcks, move_dir)
            draw_shape(shape_blcks)
            sleep_ms(mov_delay)

            '''if block did not move and the direction for movement is down
            then shape has come to rest so we can exit loop and then a new
            shape is generated. if direction for movement is sideways and
            block did not move it should be moved down rather'''
            if not moved and move_dir == 'down':
  
              for block in shape_blcks:
                    occupied_squares.append(block[0],block[1])
              break
  
            else:
                draw_shape(shape_blcks)
            sleep_ms(mov_delay)
            g.display.show()

            for row_no in range (height - sqrsize, 0, -sqrsize):
                if row_filled(row_no):
                    delete_row(row_no)
            g.display.show()

