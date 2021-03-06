# btntests.py
#
# ESP8266 (node MCU D1 mini)  micropython
# by Billy Cheung  2019 08 31
#
# see detail pin configurations in game8266.py
#
import gc
import sys
gc.collect()
print (gc.mem_free())
import network
import utime
from utime import sleep_ms,ticks_ms, ticks_us, ticks_diff
from machine import Pin, SPI, PWM, ADC
from random import getrandbits, seed

import game8266
from game8266 import gamehat

g = gamehat()

# while not (pressed(btnL) and pressed(btnA)):
while True :
  g.display.fill(0)
  g.display.text("L+A to Exit", 0,0,1)
  g.getBtn()
  if g.pressed (g.btnU):
     g.display.text("U",20, 20,1)
     g.playTone('c4', 100)
  else :
     g.display.text(":",20, 20,1)
  if g.pressed(g.btnL):
     g.display.text("L",0, 35,1)
     g.playTone('d4', 100)
  else :
     g.display.text(":",0, 35,1)
  if g.pressed(g.btnR):
     g.display.text("R",40, 35,1)
     g.playTone('e4', 100)
  else :
     g.display.text(":",40, 35,1)

  if g.pressed(g.btnD):
     g.display.text("D",20, 50,1)
     g.playTone('f4', 100)
  else :
     g.display.text(":",20, 50,1)
  if g.pressed(g.btnA):
     g.display.text("A",80, 40,1)
     g.playTone('c5', 100)
  else :
     g.display.text(":",80, 40,1)
  if g.pressed(g.btnB):
     g.display.text("B",100, 40,1)
     g.playTone('d5', 100)
  else :
     g.display.text(":",100, 40,1)

  g.display.text (str(ADC(0).read()), 0,10,1)

  g.display.text (str(g.getPaddle()), 80,10,1)

  g.getPaddle()

  g.display.show()


# wait till keys are released
g.pressed(g.btnL,True)
