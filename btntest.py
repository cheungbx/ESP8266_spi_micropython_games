# ----------------------------------------------------------
#  Snake Game 
#  ESP8266 (node MCU D1 mini)  micropython
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

import os
import sys
import gc
import utime
from utime import sleep_ms, ticks_ms, ticks_us, ticks_diff
from machine import Pin, SPI, PWM, ADC
import ssd1306
from random import getrandbits, seed


# configure oled display SPI SSD1306
hspi = SPI(1, baudrate=8000000, polarity=0, phase=0)
#DC, RES, CS 
display = ssd1306.SSD1306_SPI(128, 64, hspi, Pin(2), Pin(16), Pin(0)) 



#---buttons

btnU = 1
btnL = 2
btnR = 3
btnD = 4
btnA = 5
btnB = 6

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
  if waitRelease :
    pinPaddle.off() 
    pinBtn.on() 
    while ADC(0).read() > 70 :
       sleep_ms (20)
  return (Btns & 1 << btn)
  
def lastpressed (btn) :
  global lastBtns
  return (lastBtns & 1 << btn)


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
          Btns |= 1 << btnU | 1 << btnA
        else :
          Btns |= 1 << btnL        
      else:
        if a0 > 70 :
          Btns |= 1 << btnU
    else :
      if a0 > 482 :
        if a0 > 527 :
          Btns |= 1 << btnD   
        else :
          Btns |= 1 << btnU | 1 << btnB 
      else:  
        if a0 > 440 :
          Btns |= 1 << btnL | 1 << btnA 
        else :
          Btns |= 1 << btnR   
  else:
      if a0 < 728 :
        if a0 < 653 :
          if a0 > 609 :
            Btns |= 1 << btnD | 1 << btnA 
          else :
            Btns |= 1 << btnR | 1 << btnA 
        elif a0 > 675 :
          Btns |= 1 << btnA  
        else :
          Btns |= 1 << btnL | 1 << btnB
      elif a0 < 829 :
        if a0 > 794 :
          Btns |= 1 << btnD | 1 << btnB
        else : 
          Btns |= 1 << btnR | 1 << btnB  
      elif a0 > 857 : 
        Btns |= 1 << btnB            
      else :
        Btns |= 1 << btnA | 1 << btnB    
        
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








