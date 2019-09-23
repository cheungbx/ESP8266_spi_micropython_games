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
from utime import sleep_ms,ticks_ms, ticks_us, ticks_diff
from machine import Pin, SPI, PWM, ADC
from math import sqrt
import ssd1306
from random import getrandbits, seed

# configure oled display SPI SSD1306
hspi = SPI(1, baudrate=8000000, polarity=0, phase=0)
#DC, RES, CS
display = ssd1306.SSD1306_SPI(128, 64, hspi, Pin(2), Pin(16), Pin(0))



#---buttons

btnU = const (1 << 1)
btnL = const (1 << 2)
btnR = const (1 << 3)
btnD = const (1 << 4)
btnA = const (1 << 5)
btnB = const (1 << 6)

Btns = 0
lastBtns = 0

pinBtn = Pin(5, Pin.OUT)
pinPaddle = Pin(4, Pin.OUT)


buzzer = Pin(15, Pin.OUT)

adc = ADC(0)

def getPaddle () :
  pinPaddle.on()
  pinBtn.off()
  sleep_ms(20)
  return adc.read()

def pressed (btn, waitRelease=False) :
  global Btns
  if waitRelease and Btns :
    pinPaddle.off()
    pinBtn.on()
    while ADC(0).read() > 70 :
       sleep_ms (20)
  return (Btns & btn)

def lastpressed (btn) :
  global lastBtns
  return (lastBtns & btn)


def getBtn () :
  global Btns
  global lastBtns
  pinPaddle.off()
  pinBtn.on()
  lastBtns = Btns
  Btns = 0
  a0=ADC(0).read()
  if a0  < 564 :
    if a0 < 361 :
      if a0 > 192 :
        if a0 > 278 :
          Btns |= btnU | btnA
        else :
          Btns |= btnL
      else:
        if a0 > 70 :
          Btns |= btnU
    else :
      if a0 > 482 :
        if a0 > 527 :
          Btns |= btnD
        else :
          Btns |= btnU | btnB
      else:
        if a0 > 440 :
          Btns |= btnL | btnA
        else :
          Btns |= btnR
  else:
      if a0 < 728 :
        if a0 < 653 :
          if a0 > 609 :
            Btns |= btnD | btnA
          else :
            Btns |= btnR | btnA
        elif a0 > 675 :
          Btns |= btnA
        else :
          Btns |= btnL | btnB
      elif a0 < 829 :
        if a0 > 794 :
          Btns |= btnD | btnB
        else :
          Btns |= btnR | btnB
      elif a0 > 857 :
        Btns |= btnB
      else :
        Btns |= btnA | btnB


tones = {
    'c4': 262,
    'd4': 294,
    'e4': 330,
    'f4': 349,
    'f#4': 370,
    'g4': 392,
    'g#4': 415,
    'a4': 440,
    "a#4": 466,
    'b4': 494,
    'c5': 523,
    'c#5': 554,
    'd5': 587,
    'd#5': 622,
    'e5': 659,
    'f5': 698,
    'f#5': 740,
    'g5': 784,
    'g#5': 831,
    'a5': 880,
    'b5': 988,
    'c6': 1047,
    'c#6': 1109,
    'd6': 1175,
    ' ': 0
}


def playTone(tone, tone_duration, total_duration):
            beeper = PWM(buzzer, freq=tones[tone], duty=512)
            utime.sleep_ms(tone_duration)
            beeper.deinit()
            utime.sleep_ms(int(total_duration * 1000)-tone_duration)
            
# ----------------------------------------------------------
# Global variables
# ----------------------------------------------------------

SCREEN_WIDTH  = 128
SCREEN_HEIGHT = 64
SNAKE_SIZE    = 4
SNAKE_LENGTH  = 4
SNAKE_EXTENT  = 2
COLS          = (SCREEN_WIDTH  - 4) // SNAKE_SIZE
ROWS          = (SCREEN_HEIGHT - 4) // SNAKE_SIZE
OX            = (SCREEN_WIDTH  - COLS * SNAKE_SIZE) // 2
OY            = (SCREEN_HEIGHT - ROWS * SNAKE_SIZE) // 2
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
            playTone('d6', 20, 0.02)
            playTone('c5', 20, 0.02)
            playTone('f4', 20, 0.02)
            game['score'] += 1
            game['refresh'] = True
            extendSnakeTail()
            spawnApple()
        if didSnakeBiteItsTail() or didSnakeHitTheWall():
            playTone('c4', 500, 1)
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
            playTone('c5', 100, 0.5)
            game['mode'] = MODE_PLAY
    elif game['mode'] == MODE_EXIT:
        return
    else:
        handleButtons()

    draw()
    game['time'] += 1

    
def spawnApple():
    apple['x'] = getrandbits (6) %  (COLS - 1)
    apple['y'] = getrandbits (7) % (ROWS - 1)

def handleButtons():
  getBtn()
  if game['mode'] != MODE_MENU :
    if Btns & btnL:
        dirSnake(-1, 0)
    elif Btns & btnR:
        dirSnake(1, 0)
    elif Btns & btnU:
        dirSnake(0, -1)
    elif Btns & btnD:
        dirSnake(0, 1)
  else :
    if pressed(btnA,True):
      game['mode'] = MODE_START    
      game['frame'] = 15 
    elif pressed(btnB,True):
      game['mode'] = MODE_START
      game['frame'] = 22 
    elif pressed(btnL,True):
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
    display.show()

def clearScreen():
    color = COLOR_LOST_BG if game['mode'] == MODE_LOST else COLOR_BG
    display.fill(color)
def drawGameMenu():
    clearScreen();
    display.text("SNAKE",35,10,1)
    display.text("A - SLOW",20,20,1)    
    display.text("B - FAST",20,30,1)    
    display.text("L - EXIT",20,40,1)
def drawGameover():
    display.fill_rect(20,20,100,30,0)
    display.text("GAME OVER",20,20,1)

 
def drawWalls():
    color = COLOR_LOST_FG if game['mode'] == MODE_LOST else COLOR_WALL
    display.rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT,color)

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
    display.text(str(game['score']),2,2,1)

def drawApple():
    drawDot(apple['x'], apple['y'], COLOR_APPLE)

def drawDot(x, y, color):
    display.fill_rect(OX + x * SNAKE_SIZE, OY + y * SNAKE_SIZE, SNAKE_SIZE, SNAKE_SIZE,color)

def waitForUpdate():
    # wait the amount of them that makes up 30 frame per second
    timer_dif = int(1000/game['frame']) - ticks_diff(ticks_ms(), timer)
    if timer_dif > 0:
      sleep_ms(timer_dif)
    return


# ----------------------------------------------------------
# Initialization
# ----------------------------------------------------------

# Seed random numbers
seed(ticks_us())

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
  timer = ticks_ms()
  tick()
  waitForUpdate()







