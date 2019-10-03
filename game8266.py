# game8266.py
# game hat module to use SSD1306 SPI OLED and 6 buttons
# Buttons are read through A0 using many resistors in a  Voltage Divider circuit
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

import utime
from utime import sleep_ms,ticks_ms, ticks_us, ticks_diff
from machine import Pin, SPI, PWM, ADC
import ssd1306
from random import getrandbits, seed

class Game8266():

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

    def __init__(self):

        # configure oled display SPI SSD1306
        self.hspi = SPI(1, baudrate=8000000, polarity=0, phase=0)
        #DC, RES, CS
        self.display = ssd1306.SSD1306_SPI(128, 64, self.hspi, Pin(2), Pin(16), Pin(0))
        self.timer = 0
        seed(ticks_us())

        #---buttons

        self.btnU = 1 << 1
        self.btnL = 1 << 2
        self.btnR = 1 << 3
        self.btnD = 1 << 4
        self.btnA = 1 << 5
        self.btnB = 1 << 6
        self.frameRate = 30
        self.screenW = 128
        self.screenH = 64
        self.Btns = 0

        self.pinBtn = Pin(5, Pin.OUT)
        self.pinPaddle = Pin(4, Pin.OUT)
        self.adc = ADC(0)

        self.buzzer = Pin(15, Pin.OUT)

    def getPaddle (self) :
      self.pinPaddle.on()
      self.pinBtn.off()
      sleep_ms(1)
      return self.adc.read()

    def pressed (self,btn, waitRelease=False) :
      if waitRelease and self.Btns :
        self.pinPaddle.off()
        self.pinBtn.on()
        while self.adc.read() > 70 :
           sleep_ms (20)
      return (self.Btns & btn)


    def getBtn(self) :
      self.pinPaddle.off()
      self.pinBtn.on()
      self.Btns = 0
      a0=self.adc.read()
      if a0  < 564 :
        if a0 < 361 :
          if a0 > 192 :
            if a0 > 278 :
              self.Btns |= self.btnU | self.btnA
            else :
              self.Btns |= self.btnL
          else:
            if a0 > 70 :
              self.Btns |= self.btnU
        else :
          if a0 > 482 :
            if a0 > 527 :
              self.Btns |= self.btnD
            else :
              self.Btns |= self.btnU | self.btnB
          else:
            if a0 > 440 :
              self.Btns |= self.btnL | self.btnA
            else :
              self.Btns |= self.btnR
      else:
          if a0 < 728 :
            if a0 < 653 :
              if a0 > 609 :
                self.Btns |= self.btnD | self.btnA
              else :
                self.Btns |= self.btnR | self.btnA
            elif a0 > 683 :
              self.Btns |= self.btnA
            else :
              self.Btns |= self.btnL | self.btnB
          elif a0 < 829 :
            if a0 > 794 :
              self.Btns |= self.btnD | self.btnB
            else :
              self.Btns |= self.btnR | self.btnB
          elif a0 > 857 :
            self.Btns |= self.btnB
          else :
            self.Btns |= self.btnA | self.btnB
      return self.Btns

    def playTone(self, tone, tone_duration, rest_duration=0):
        beeper = PWM(self.buzzer, freq=self.tones[tone], duty=512)
        sleep_ms(tone_duration)
        beeper.deinit()
        sleep_ms(rest_duration)

    def playSound(self, freq, tone_duration, rest_duration=0):
        beeper = PWM(self.buzzer, freq, duty=512)
        sleep_ms(tone_duration)
        beeper.deinit()
        sleep_ms(rest_duration)

    def random (self, x, y) :
        return  getrandbits(10) % (y+1) + x

    def display_and_wait(self,frames_per_s) :
        self.display.show()
        timer_dif = int(1000/frames_per_s) - ticks_diff(ticks_ms(), self.timer)
        if timer_dif > 0 :
            sleep_ms(timer_dif)
            self.timer=ticks_ms()


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
