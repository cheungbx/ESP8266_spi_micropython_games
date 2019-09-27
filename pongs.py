# pongs.py
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
# GPIO15   D8  Speaker
# n.c.   - D6  (=GPIO13=HMOSI)
#
# GPIO5    D1——   On to read ADC for Btn
# GPIO4    D2——   On to read ADC for bat
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
pinPaddle2 = Pin(0, Pin.OUT)

buzzer = Pin(15, Pin.OUT)


def getPaddle (maxvalue=1024) :
  pinPaddle.on()
  pinPaddle2.off()
  pinBtn.off()
  sleep_ms(1)
  return int (ADC(0).read() / (1024 / maxvalue))
  
def getPaddle2 (maxvalue=1024) :
  pinPaddle2.on()
  pinPaddle.off()
  pinBtn.off()
  sleep_ms(1)
  return int (ADC(0).read() / (1024 / maxvalue))

def getBtn () :
  global Btns
  pinPaddle.off()
  pinPaddle2.off()
  pinBtn.on()
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

def pressed (btn, waitRelease=False) :
  if waitRelease and Btns :
    pinPaddle.off()
    pinPaddle2.off()
    pinBtn.on()
    while ADC(0).read() > 70 :
       sleep_ms (20)
  return (Btns & btn)

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



frameRate = 60

scores = [0,0]
maxScore = 15
gameOver = False
exitGame = False

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



class bat(Rect):
  def __init__(self, velocity, up_key, down_key, *args, **kwargs):
    self.velocity = velocity
    self.up_key = up_key
    self.down_key = down_key
    super().__init__(*args, **kwargs)

  def move_bat(self, board_height, bat_HEIGHT, ballY):
    getBtn()

    if self.up_key == 0  : # use AI
      self.y = max(min(ballY - 10 +  getrandbits(10) % 16, board_height-pong.bat_HEIGHT),0)

    elif self.up_key == -1 : # use Paddle
      self.y = getPaddle(board_height-pong.bat_HEIGHT) 
      
    elif self.up_key == -2 : # use 2nd Paddle
      self.y = getPaddle2(board_height-pong.bat_HEIGHT) 
      
    else :    
      if pressed(self.up_key):
        if self.y - self.velocity > 0:
            self.y -= self.velocity
            
      if pressed(self.down_key):
        if self.y + self.velocity < board_height - bat_HEIGHT :
            self.y += self.velocity
    self.y2 = self.y + pong.bat_HEIGHT

class Ball(Rect):
    def __init__(self, velocity, *args, **kwargs):
        self.velocity = velocity
        self.angle = 0
        super().__init__(*args, **kwargs)

    def move_ball(self):
        self.x += self.velocity
        self.y += self.angle
        self.x2 = self.x + pong.BALL_WIDTH
        self.y2 = self.y + pong.BALL_WIDTH


class Pong:
    HEIGHT = 64
    WIDTH = 128

    bat_WIDTH = 2
    bat_HEIGHT = 15
    bat_VELOCITY = 3
    
    BALL_WIDTH = 2
    BALL_VELOCITY = 2
    BALL_ANGLE = 0

    COLOUR = 1
    scores = [0,0]
    maxScore = 15


    def init (self, onePlayer, demo, usePaddle):
        # Setup the screen
        global scores
        scores = [0,0]
        # Create the player objects.
        self.bats = []
        self.balls = []

        if demo or onePlayer :         
          self.bats.append(bat(  # The left bat, AI
            self.bat_VELOCITY,
            0,
            0,
            0,
            int(self.HEIGHT / 2 - self.bat_HEIGHT / 2),
            self.bat_WIDTH,
            self.bat_HEIGHT))
        elif usePaddle :
          self.bats.append(bat(  # The left bat, use Paddle
            self.bat_VELOCITY,
            -2,
            -2,
            0,
            int(self.HEIGHT / 2 - self.bat_HEIGHT / 2),
            self.bat_WIDTH,
            self.bat_HEIGHT))
        else : 
          
          self.bats.append(bat(  # The left bat, button controlled
            self.bat_VELOCITY,
            btnU,
            btnD,
            0,
            int(self.HEIGHT / 2 - self.bat_HEIGHT / 2),
            self.bat_WIDTH,
            self.bat_HEIGHT))
            
        if demo :        
          self.bats.append(bat(  # The right bat, AI
              self.bat_VELOCITY,
              0,
              0,
              self.WIDTH - self.bat_WIDTH-1,
              int(self.HEIGHT / 2 - self.bat_HEIGHT / 2),
              self.bat_WIDTH,
              self.bat_HEIGHT
              ))
        elif usePaddle :
          self.bats.append(bat(  # The right bat, buse Paddle
              self.bat_VELOCITY,
              -1,
              -1,
              self.WIDTH - self.bat_WIDTH-1,
              int(self.HEIGHT / 2 - self.bat_HEIGHT / 2),
              self.bat_WIDTH,
              self.bat_HEIGHT
              ))
        else :
           self.bats.append(bat(  # The right bat, button controlled
              self.bat_VELOCITY,
              btnB,
              btnA,
              self.WIDTH - self.bat_WIDTH-1,
              int(self.HEIGHT / 2 - self.bat_HEIGHT / 2),
              self.bat_WIDTH,
              self.bat_HEIGHT
              ))
      
        self.balls.append(Ball(
            self.BALL_VELOCITY,
            int(self.WIDTH / 2 - self.BALL_WIDTH / 2),
            int(self.HEIGHT / 2 - self.BALL_WIDTH / 2),
            self.BALL_WIDTH,
            self.BALL_WIDTH))

     
    def score(self, player, ball):
      global gameOver
      global scores
      scores[player] += 1
      ball.velocity = - ball.velocity
      ball.angle = getrandbits(10) % 4   - 2
      ball.x = int(self.WIDTH / 2 - self.BALL_WIDTH / 2)
      ball.y = int(self.HEIGHT / 2 - self.BALL_WIDTH / 2)
      ball.x2 = ball.x + self.BALL_WIDTH 
      ball.y2 = ball.y + self.BALL_WIDTH 
      playTone ('g4', 100)    

      if scores[player] >= maxScore :
        gameOver = True
    
    def check_ball_hits_wall(self):
      for ball in self.balls:

        if ball.x < 0:
          self.score(1, ball)


        if ball.x > self.WIDTH :
          self.score(0, ball)

        if ball.y > self.HEIGHT - self.BALL_WIDTH or ball.y < 0:
          ball.angle = -ball.angle

      
    def check_ball_hits_bat(self):
      for ball in self.balls:
          for bat in self.bats:
            #print (' {} {} {} {} : {} {} {} {}'.format (ball.x, ball.y, ball.x2, ball.y2, bat.x,bat.y, bat.x2, bat.y2))
            if ball.colliderect(bat):
                  ball.velocity = -ball.velocity
                  ball.angle = (getrandbits(10) % 4 ) - 2
                  playTone ('c6', 10)    
                  break

    def game_loop(self):
      global gameOver
      global exitGame
      global scores
      global frameRate

      exitGame = False
      while not exitGame:
        frameRate = 40
        usePaddle = False
        onePlayer = True
        demo = False
        gameOver = False
        display.fill(0)
        display.text('D-Demo L-Quit', 5, 0, 1)
        display.text('A 1-Button', 5, 20, 1)
        display.text('B 1-Paddle', 5,30,  1)
        display.text('U 2-Button', 5, 40,  1)
        display.text('R 2-Paddle', 5, 50,  1)
        display.show()

        #menu screen
        while True:
          getBtn()
          if pressed(btnL,True) :
            exitGame = True
            gameOver= True
            break
          elif pressed(btnA,True) :
            onePlayer = True
            usePaddle = False
            break
          elif pressed(btnB,True) :
            onePlayer = True
            usePaddle = True
            break
          elif pressed(btnU,True) :
            onePlayer = False
            usePaddle = False
            break
          elif pressed(btnR,True) :
            onePlayer = False
            usePaddle = True
            break
          elif pressed(btnD,True) :
            demo = True
            usePaddle = False
            frameRate = 120
            display.fill(0)
            display.text('DEMO', 5, 0, 1)
            display.text('A or B to Stop', 5, 30, 1)
            display.show()
            sleep_ms(2000)
            break

  
        self.init(onePlayer, demo, usePaddle)
        #game loop
        
        while not gameOver:

          timer=ticks_ms()         

          getBtn()

          self.check_ball_hits_bat()
          self.check_ball_hits_wall()
    

          # Redraw the screen.
          display.fill(0)

          for bat in self.bats:
            bat.move_bat(self.HEIGHT, self.bat_HEIGHT, self.balls[0].y)
            display.fill_rect(bat.x,bat.y,self.bat_WIDTH, self.bat_HEIGHT, self.COLOUR)
      
          for ball in self.balls:
            ball.move_ball()
            display.fill_rect(ball.x,ball.y,self.BALL_WIDTH ,self.BALL_WIDTH, self.COLOUR)
   
          display.text ('{} : {}'.format (scores[0], scores[1]), 45, 0, 1)

          if gameOver :
            display.fill_rect(25,25,100, 30,0)
            display.text ("Game Over", 30, 30, 1)
            display.show()
            playTone ('c5', 200)
            playTone ('g4', 200)
            playTone ('g4', 200)    
            playTone ('a4', 200)
            playTone ('g4', 400)
            playTone ('b4', 200)   
            playTone ('c5', 400)
          display.show()
          
          timer_dif = int(1000/frameRate) - ticks_diff(ticks_ms(), timer)

          if timer_dif > 0 :
            sleep_ms(timer_dif)


#if __name__ == '__main__':
pong = Pong()

pong.game_loop()
print ("game exit")

