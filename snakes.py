# ----------------------------------------------------------
# Snakes Game
# ESP8266 (node MCU D1 mini)  micropython
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
import gc
import sys
gc.collect()
print (gc.mem_free())
import network
import utime
from utime import sleep_ms
from game8266 import Game8266, Rect
g=Game8266()
frameRate = 30

SNAKE_SIZE    = 4
SNAKE_LENGTH  = 4
SNAKE_EXTENT  = 2
COLS          = (g.screenW  - 4) // SNAKE_SIZE
ROWS          = (g.screenH - 4) // SNAKE_SIZE
OX            = (g.screenW  - COLS * SNAKE_SIZE) // 2
OY            = (g.screenH - ROWS * SNAKE_SIZE) // 2
COLOR_BG      = 0
COLOR_WALL    = 1
COLOR_SNAKE   = 1
COLOR_APPLE   = 1
COLOR_SCORE   = 1
COLOR_LOST_BG = 1
COLOR_LOST_FG = 0
MODE_MENU     = 0
MODE_START    = 1
MODE_READY    = 2
MODE_PLAY     = 3
MODE_LOST     = 4
MODE_EXIT     = 5


# ----------------------------------------------------------
# Game management
# ----------------------------------------------------------

def tick():
    if not game['refresh']:
        clearSnakeTail()

    if game['mode'] == MODE_PLAY:
        handleButtons()
        moveSnake()
        if game['refresh']:
            game['refresh'] = False
        if didSnakeEatApple():
            g.playTone('d6', 20)
            g.playTone('c5', 20)
            g.playTone('f4', 20)
            game['score'] += 1
            game['refresh'] = True
            extendSnakeTail()
            spawnApple()
        if didSnakeBiteItsTail() or didSnakeHitTheWall():
            g.playTone('c4', 500)
            game['mode'] = MODE_LOST
            game['refresh'] = True
    elif game['mode'] == MODE_LOST:
        sleep_ms(2000)
        game['mode'] = MODE_MENU
    elif game['mode'] == MODE_START:
        resetSnake()
        spawnApple()
        game['mode'] = MODE_READY
        game['score'] = 0
        game['time']  = 0
    elif game['mode'] == MODE_READY:
        game['refresh'] = False

        handleButtons()
        moveSnake()
        if snakeHasMoved():
            g.playTone('c5', 100)
            game['mode'] = MODE_PLAY
    elif game['mode'] == MODE_EXIT:
        return
    else:
        handleButtons()

    draw()
    game['time'] += 1


def spawnApple():
    apple['x'] = g.random (1, COLS - 2)
    apple['y'] = g.random (1, ROWS - 2)

def handleButtons():

  g.getBtn()
  if game['mode'] != MODE_MENU :
    if g.Btns & g.btnL:
        dirSnake(-1, 0)
    elif g.Btns & g.btnR:
        dirSnake(1, 0)
    elif g.Btns & g.btnU:
        dirSnake(0, -1)
    elif g.Btns & g.btnD:
        dirSnake(0, 1)
  else :
    if g.pressed(g.btnA,True):
      game['mode'] = MODE_START
      game['frame'] = 15
    elif g.pressed(g.btnB,True):
      game['mode'] = MODE_START
      game['frame'] = 20
    elif g.pressed(g.btnU,True):
      game['mode'] = MODE_START
      game['frame'] = 25
    elif g.pressed(g.btnL,True):
      game['mode'] = MODE_EXIT




# ----------------------------------------------------------
# Snake management
# ----------------------------------------------------------

def resetSnake():
    x = COLS // 2
    y = ROWS // 2
    snake['x'] = []
    snake['y'] = []
    for _ in range(SNAKE_LENGTH):
        snake['x'].append(x)
        snake['y'].append(y)
    snake['head'] = SNAKE_LENGTH - 1
    snake['len']  = SNAKE_LENGTH
    snake['vx'] = 0
    snake['vy'] = 0

def dirSnake(dx, dy):
    snake['vx'] = dx
    snake['vy'] = dy

def moveSnake():
    h = snake['head']
    x = snake['x'][h]
    y = snake['y'][h]
    h = (h + 1) % snake['len']
    snake['x'][h] = x + snake['vx']
    snake['y'][h] = y + snake['vy']
    snake['head'] = h

def snakeHasMoved():
    return snake['vx'] or snake['vy']

def didSnakeEatApple():
    h = snake['head']
    return snake['x'][h] == apple['x'] and snake['y'][h] == apple['y']

def extendSnakeTail():
    i = snake['head']
    n = snake['len']
    i = (i + 1) % n
    x = snake['x'][i]
    y = snake['y'][i]
    for _ in range(SNAKE_EXTENT):
        snake['x'].insert(i, x)
        snake['y'].insert(i, y)
    snake['len'] += SNAKE_EXTENT

def didSnakeBiteItsTail():
    h = snake['head']
    n = snake['len']
    x = snake['x'][h]
    y = snake['y'][h]
    i = (h + 1) % n
    for _ in range(n-1):
        if snake['x'][i] == x and snake['y'][i] == y:
            return True
        i = (i + 1) % n
    return False

def didSnakeHitTheWall():
    h = snake['head']
    x = snake['x'][h]
    y = snake['y'][h]
    return x < 0 or x == COLS or y < 0 or y == ROWS

# ----------------------------------------------------------
# Graphic display
# ----------------------------------------------------------

def draw():
    if game['mode'] == MODE_MENU:
        drawGameMenu()
    elif game['mode'] == MODE_LOST:
        drawGameover()
    elif game['refresh']:
        clearScreen()
        drawWalls()
        drawSnake()
    else:
        drawSnakeHead()
    drawScore()
    drawApple()
    g.display.show()

def clearScreen():
    color = COLOR_LOST_BG if game['mode'] == MODE_LOST else COLOR_BG
    g.display.fill(color)
def drawGameMenu():
    clearScreen();
    g.display.text("SNAKE",35,10,1)
    g.display.text("A - SLOW",20,20,1)
    g.display.text("B - FAST",20,30,1)
    g.display.text("U - SUPER",20,40,1)
    g.display.text("L - EXIT",20,50,1)
def drawGameover():
    g.display.fill_rect(20,20,100,30,0)
    g.display.text("GAME OVER",20,20,1)


def drawWalls():
    color = COLOR_LOST_FG if game['mode'] == MODE_LOST else COLOR_WALL
    g.display.rect(0, 0, g.screenW, g.screenH,color)

def drawSnake():
    isTimeToBlink = game['time'] % 4 < 2
    color = COLOR_LOST_FG if game['mode'] == MODE_LOST and isTimeToBlink else COLOR_SNAKE
    n = snake['len']
    for i in range(n):
        drawDot(snake['x'][i], snake['y'][i], color)

def drawSnakeHead():
    h = snake['head']
    drawDot(snake['x'][h], snake['y'][h], COLOR_SNAKE)

def clearSnakeTail():
    h = snake['head']
    n = snake['len']
    t = (h + 1) % n
    drawDot(snake['x'][t], snake['y'][t], COLOR_BG)

def drawScore():
    g.display.text(str(game['score']),2,2,1)

def drawApple():
    drawDot(apple['x'], apple['y'], COLOR_APPLE)

def drawDot(x, y, color):
    g.display.fill_rect(OX + x * SNAKE_SIZE, OY + y * SNAKE_SIZE, SNAKE_SIZE, SNAKE_SIZE,color)



# ----------------------------------------------------------
# Initialization
# ----------------------------------------------------------


game = {
    'mode':    MODE_MENU,
    'score':   0,
    'time':    0,
    'frame':   15,
    'refresh': True
}

snake = {
    'x':    [],
    'y':    [],
    'head': 0,
    'len':  0,
    'vx':   0,
    'vy':   0
}

apple = { 'x': 0, 'y': 0 }

# ----------------------------------------------------------
# Main loop
# ----------------------------------------------------------
while game['mode'] != MODE_EXIT :
  tick()
  g.display_and_wait(game['frame'])
