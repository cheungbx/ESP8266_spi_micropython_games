###############################################################################
## an implementation of a ***very*** basic tetris game in python using pygame
###############################################################################
'''rotate --- r
   pause ---- p
   direction buttons for movement'''


import sys
import pygame
import random

size = width, height = 200, 400
color = {'black': (0, 0, 0), 'white':(255, 255, 255)}
sqrsize = 20
occupied_squares = []
top_of_screen = (0, 0)
top_x, top_y = top_of_screen[0], top_of_screen[1]
num_block = 4
pen_size = 1
mov_delay, r_delay = 300, 50
board_centre = 80
no_move = 0
events = {276: 'left', 275: 'right', 112: 'pause'}


pygame.init()
screen = pygame.display.set_mode(size)
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((color['white']))
screen.blit(background, top_of_screen)
pygame.display.flip()


def tetris():
    ''' this is the controller of the whole game for now, maybe changed
    later on as game architecture changes.'''
    global mov_delay
while True:
    curr_shape = create_newshape(board_centre)
    l_of_blcks_ind = blck_x_axis = 0
    shape_name_ind = blck_y_axis = 1

    move_dir = 'down' #default move direction
    game = 'playing'  #default game state play:- is game paused or playing

    shape_blcks = [pygame.Rect(block[blck_x_axis], block[blck_y_axis],
        sqrsize, sqrsize) for block in curr_shape[l_of_blcks_ind]]
    if legal(shape_blcks):
        draw_shape(shape_blcks)
    else:
        break  #game over
    while True:
        if game == 'paused':
            for event in pygame.event.get(pygame.KEYDOWN):
                if event.key == pygame.K_p:
                    game = 'playing'
        else:
            for event in pygame.event.get((pygame.KEYDOWN, pygame.KEYUP,
                                           pygame.QUIT)):
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        mov_delay = 50
                        continue
                    elif event.key == pygame.K_r:
                        shape_blcks = rotate(shape_blcks, curr_shape[shape_name_ind])
                        draw_shape(shape_blcks)
                        pygame.time.delay(r_delay)
                        continue

                    elif event.key == pygame.K_p:
                        game = 'paused'
                        move_dir = events[event.key]
                        break

                    else:
                        if event.key in events.keys():
                            mov_delay = 50
                            move_dir = events[event.key]
                            move (shape_blcks, move_dir)
                            draw_shape(shape_blcks)
                            pygame.time.delay(mov_delay)
                            continue
                elif event.type == pygame.KEYUP:
                    if mov_delay != 300:
                        mov_delay = 300
                    move_dir  = 'down'
            moved = move(shape_blcks, move_dir)
            draw_shape(shape_blcks)
            pygame.time.delay(mov_delay)

            '''if block did not move and the direction for movement is down
            then shape has come to rest so we can exit loop and then a new
            shape is generated. if direction for movement is sideways and
            block did not move it should be moved down rather'''
            if not moved and move_dir == 'down':
                for block in shape_blcks:
                    occupied_squares.append((block[blck_x_axis],
                                             block[blck_y_axis]))
                break
            else:
                draw_shape(shape_blcks)
                pygame.time.delay(mov_delay)
            for row_no in range (height - sqrsize, 0, -sqrsize):
                if row_filled(row_no):
                    delete_row(row_no)


def draw_shape(shp_blcks):
'''this draws list of blocks or a block to the background and blits
background to screen'''
if isinstance(shp_blcks, list):
    for blck in shp_blcks:
        pygame.draw.rect(background, color['black'], blck, pen_size)
else:
    pygame.draw.rect(background, color['black'], shp_blcks, pen_size)
screen.blit(background, top_of_screen)
pygame.display.update()


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
background.fill(color['white'])
for sqr in occupied_squares:
    if sqr[y_coord] != row_no:
        new_buffer.append(sqr)
occupied_squares = new_buffer
for index in range(len(occupied_squares)):
    if occupied_squares[index][y_coord] < row_no:
        occupied_squares[index] = (occupied_squares[index][x_coord],
                                occupied_squares[index][y_coord] + sqrsize)
for sqr in occupied_squares:
    rect = pygame.Rect(sqr[x_coord], sqr[y_coord], sqrsize, sqrsize)
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
        background.fill((color['white']), shape_blcks[index].move(-delta_x,
                                                                  -delta_y))
    return True
else:
    for index in range(num_block):
        shape_blcks[index] = shape_blcks[index].move(-delta_x, -delta_y)
    return False


def legal(shape_blcks):
'''input: list of shape blocks
checks whether a shape is in a legal portion of the board as defined in the
doc of 'move' function'''
blck_x_axis, blck_y_axis = 0, 1
for index in range(num_block):
    new_x, new_y = (shape_blcks[index][blck_x_axis],
                    shape_blcks[index][blck_y_axis])

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
a_shape = random.randint(0, 4)
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
    blck_x_axis, blck_y_axis = 0, 1

    shape_coords = [(block[blck_x_axis], block[blck_y_axis]) for
        block in shape_blcks]

    ref_shape_ind = 3 # index of block along which shape is rotated
    start_x, start_y = (shape_coords[ref_shape_ind][blck_x_axis],
                        shape_coords[ref_shape_ind][blck_y_axis])
    new_shape_blcks = [(start_x + start_y-shape_coords[0][1],
                        start_y - (start_x - shape_coords[0][0])),
        (start_x + start_y-shape_coords[1][1],
         start_y - (start_x - shape_coords[1][0])),
        (start_x + start_y-shape_coords[2][1],
         start_y - (start_x - shape_coords[2][0])),
        (shape_coords[3][0], shape_coords[3][1])]
    if legal(new_shape_blcks):
        for index in range(num_block): # paint over the previous shape
            background.fill(color['white'], shape_blcks[index])
        return [pygame.Rect(block[blck_x_axis], block[blck_y_axis],
                                                 sqrsize, sqrsize) for
                                           block in new_shape_blcks]
    else:
        return shape_blcks

if __name__ == '__main__':
    tetris()
