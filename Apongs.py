# invaders.py
#
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
#
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
seed(ticks_us())

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
  sleep_ms(1)
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


def playTone(tone, tone_duration, rest_duration=0):
  beeper = PWM(buzzer, freq=tones[tone], duty=512)
  utime.sleep_ms(tone_duration)
  beeper.deinit()
  utime.sleep_ms(rest_duration)

def playSound(freq, tone_duration, rest_duration=0):
  beeper = PWM(buzzer, freq, duty=512)
  utime.sleep_ms(tone_duration)
  beeper.deinit()
  utime.sleep_ms(rest_duration)
       


frameRate = 30
screenW = const(128)
screenH = const(64)
xMargin = const (5)
yMargin = const(10)
screenL = const (5)
screenR = const(117)
screenT = const (10)
screenB = const (58)

state =[]


class Rect (object):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.x2 = x + w - 1
        self.y2 = y + h - 1
    def move_ip (self, vx, vy) :
        self.x = self.x + vx
        self.y = self.y + vy
        self.x2 = self.x2 + vx
        self.y2 = self.y2 + vy

    def colliderect (self, rect1) :
      if (self.x2 >= rect1.x and
        self.x <= rect1.x2 and
        self.y2 >= rect1.y and
        self.y <= rect1.y2) :
        return True
      else:
        return False

import math
GAME_NOT_STARTED = 0
GAME_ACTIVE = 1
GAME_WIN = 2
GAME_LOSE = 3

BALL_SPEED = 5

BALL_W = 3
BALL_H = 3

PADDLE_W = 2
PADDLE_H = 15

MAX_ANGLE = 30


# Views:
def splash(w, h):
  for n in range(0, w, 20):
    display.fill_rect(n,0,10,h)
    display.rect (0,17,w,30)
    display.text('PONG!',0,20,1)
    display.text('Click to',80,20,1)
    display.text('START!',80,30,1)


def paddle(user):
  display.fill_rect(user['x'], user['y'],PADDLE_W,PADDLE_H,1)
  

def ball(x, y):
  display.fill_rect(x,y,BALL_W,BALL_H)


def deck(player, ai, ball_data):
  yield from paddle(player)
  yield from paddle(ai)
  yield from ball(ball_data['x'], ball_data['y'])


def view(state):
  if state['state'] == GAME_NOT_STARTED:
    yield from splash(w=state['display']['width'],
                      h=state['display']['height'])
  else:
    yield from deck(player=state['player'],
                    ai=state['ai'],
                    ball_data=state['ball'])
    if state['state'] == GAME_WIN:
      display.text('YOU WIN!',0,20, 1)
    elif state['state'] == GAME_LOSE:
      display.text('YOU LOSE!',0,20, 1)


# Works with state:
def intersects(ball, paddle):
  return paddle['x'] - BALL_W <= ball['x'] <= paddle['x'] + PADDLE_W and \
         paddle['y'] - BALL_H <= ball['y'] <= paddle['y'] + PADDLE_H


def get_velocity(angle):
  return {'vx': BALL_SPEED * math.cos(angle),
          'vy': BALL_SPEED * math.sin(angle)}


def velocity_for_intersection(ball, paddle):
  relative = paddle['y'] + PADDLE_H / 2 - ball['y']
  normalized = relative / (PADDLE_H / 2)
  angle = normalized * MAX_ANGLE
  return get_velocity(angle)


def get_new_game_state(w, h):
  angle = getrandbits(8) % MAX_ANGLE + 360 - MAX_ANGLE
  return {'player': {'x': 0, 'y': 0},
          'ai': {'x': w - 2,
                 'y': h - 15},
          'ball': {'x': 5,
                   'y': 5,
                   'velocity': get_velocity(angle)},
          'score': 0}


def update_ball(ball, player, ai, h):
  ball['x'] += ball['velocity']['vx']
  ball['y'] += ball['velocity']['vy']

  if ball['y'] < 0 or ball['y'] > h:
      ball['velocity']['vy'] = -ball['velocity']['vy']

  if intersects(ball, player):
      ball['velocity'] = velocity_for_intersection(ball, player)
  elif intersects(ball, ai):
      ball['velocity'] = velocity_for_intersection(ball, ai)

  return ball


def update_paddle(paddle, h):
  if paddle['y'] < 0:
      paddle['y'] = 0
  elif paddle['y'] > (h - PADDLE_H):
      paddle['y'] = h - PADDLE_H
  return paddle


def update_player(player, joystick, h):
  player['y'] = min(max (int(getPaddle()/(1024/60)),10),60)
  return update_paddle(player, h)


def update_ai(ai, ball, h):
  if ai['y'] < ball['y']:
      ai['y'] += (ball['y'] - ai['y']) % 10
  elif ai['y'] + PADDLE_H > ball['y']:
      ai['y'] += 0 - (ball['y'] - ai['y']) % 10
  return update_paddle(ai, h)


def update_game_state(ball, w):
  if ball['x'] < 0:
      return GAME_LOSE
  elif ball['x'] > w:
      return GAME_WIN
  else:
      return GAME_ACTIVE


def controller(state):
  if state['state'] == GAME_ACTIVE:
    state['ball'] = update_ball(
            state['ball'],
            state['player'],
            state['ai'],
            state['display']['height'])
    state['player'] = update_player(state['player'],
                                    state['joystick'],
                                    state['display']['height'])
    state['ai'] = update_ai(state['ai'],
                            state['ball'],
                            state['display']['height'])
    state['state'] = update_game_state(state['ball'],
                                       state['display']['width'])
  elif state['joystick']['clicked']:
    state.update(get_new_game_state(state['display']['width'],
                                    state['display']['height']))
    state['state'] = GAME_ACTIVE
  return state

state = [ 'state': GAME_NOT_STARTED]

while True :
  timer = ticks_ms()
  state = controller(state)
  display.show()
  timer_dif = int(1000/frameRate) - ticks_diff(ticks_ms(), timer)
  if timer_dif > 0 :
      sleep_ms(timer_dif)
  

