# ----------------------------------------------------------
# btntests  I2C OLED
#  ESP8266 (node MCU D1 mini)  micropython
# by Billy Cheung  2019 08 31
#
# I2C OLED SSD1306
# GPIO4   D2---  SDA OLED
# GPIO5   D1---  SCL  OLED
#
# Speaker
# GPIO15  D8     Speaker
#
#buttons
# GPIO12  D6——  Left  
# GPIO13  D7——  Right     
# GPIO14  D5——  UP    
# GPIO2   D4——   Down    
# GPIO0   D3——   A
#

import gc
import sys
gc.collect()
print (gc.mem_free())
import network
import utime
from utime import sleep_ms,ticks_ms, ticks_us, ticks_diff
from machine import Pin, I2C, PWM, ADC
from math import sqrt
import ssd1306
from random import getrandbits, seed


#---buttons

SCREEN_WIDTH  = const(128)
SCREEN_HEIGHT = const(64)
paddle_width = 22
btnL = Pin(12, Pin.IN, Pin.PULL_UP)
btnR = Pin(13, Pin.IN, Pin.PULL_UP)
btnU = Pin(14, Pin.IN, Pin.PULL_UP)
btnD = Pin(2, Pin.IN, Pin.PULL_UP)
btnA = Pin(0, Pin.IN, Pin.PULL_UP)
btnB = Pin(3, Pin.IN, Pin.PULL_UP)
buzzer = Pin(15, Pin.OUT)
# configure oled display I2C SSD1306
i2c = I2C(-1, Pin(5), Pin(4))   # SCL, SDA
display = ssd1306.SSD1306_I2C(128, 64, i2c)
# ESP8266 ADC A0 values 0-1023
adc = ADC(0)

def getBtn() :
  pass

def pressed (btn, wait_release=False) :
  if not btn.value():
    if btn.value():
      return False
    #wait for key release
    while wait_release and not btn.value() :
      sleep_ms (5)
    return True
  return False



def getPaddle (maxvalue=1024) :
  return int (ADC(0).read() / (1024 / maxvalue))

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

while not (pressed(btnL) and pressed(btnA)):
  display.fill(0)
  display.text("L+A to Exit", 0,0,1)
  getBtn()
  if pressed (btnU):
     display.text("U",20, 20,1)
     playTone('c4', 100)
  else :
     display.text(":",20, 20,1)
  if pressed(btnL):
     display.text("L",0, 35,1)
     playTone('d4', 100)
  else :
     display.text(":",0, 35,1)
  if pressed(btnR):
     display.text("R",40, 35,1)
     playTone('e4', 100)
  else :
     display.text(":",40, 35,1)

  if pressed(btnD):
     display.text("D",20, 50,1)
     playTone('f4', 100)
  else :
     display.text(":",20, 50,1)
  if pressed(btnA):
     display.text("A",80, 40,1)
     playTone('c5', 100)
  else :
     display.text(":",80, 40,1)
  if pressed(btnB):
     display.text("B",100, 40,1)
     playTone('d5', 100)
  else :
     display.text(":",100, 40,1)

  display.text (str(adc.read()), 0,10,1)

  display.text (str(getPaddle()), 80,10,1)
  display.show()


# wait till keys are released
pressed(btnL,True)
