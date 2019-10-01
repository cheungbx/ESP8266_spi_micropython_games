import os
import sys
import gc
from machine import Pin, ADC
from utime import sleep_ms, ticks_ms, ticks_diff
module_name = ""

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
        elif a0 > 683 :
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


def do_menu () :
  global module_name

  pinBtn = Pin(5, Pin.OUT)
  pinPaddle = Pin(4, Pin.OUT)

  from machine import SPI
  import ssd1306

  # configure oled display I2C SSD1306
  hspi = SPI(1, baudrate=8000000, polarity=0, phase=0)
  #DC, RES, CS
  display = ssd1306.SSD1306_SPI(128, 64, hspi, Pin(2), Pin(16), Pin(0))

  SKIP_NAMES = ("boot", "main", "menus")


  files = [item[0] for item in os.ilistdir(".") if item[1] == 0x8000]


  module_names = [
      filename.rsplit(".", 1)[0]
      for filename in files
      if (filename.endswith(".py") or  filename.endswith(".mpy") ) and not filename.startswith("_")
  ]
  module_names = [module_name for module_name in module_names if not module_name in SKIP_NAMES]
  module_names.sort()
  tot_file = len(module_names)
  tot_rows = const(5)
  screen_pos = 0
  file_pos = 0

  launched = False
  while not launched :
    gc.collect()
    display.fill(0)
    display.text(sys.platform + " " + str(gc.mem_free()), 5, 0, 1)
    i = 0
    for j in range (file_pos, min(file_pos+tot_rows, tot_file)) :
      current_row = 12 + 10 *i
      if i == screen_pos :
        display.fill_rect(5, current_row, 118, 10, 1)
        display.text(str(j) + " " + module_names[j], 5, current_row, 0)
      else:
        display.fill_rect(5, current_row, 118, 10, 0)
        display.text(str(j) + " " + module_names[j], 5, current_row, 1)
      i+=1
    display.show()
    getBtn()

    if pressed(btnU,True):
      if screen_pos > 0 :
        screen_pos -= 1
      else :
          if file_pos > 0 :
            file_pos = max (0, file_pos - tot_rows)
            screen_pos=tot_rows-1

    if pressed(btnD,True):
      if screen_pos < min(tot_file - file_pos - 1, tot_rows -1) :
        screen_pos = min(tot_file-1, screen_pos + 1)
      else :
        if file_pos + tot_rows < tot_file :
          file_pos = min (tot_file, file_pos + tot_rows)
          screen_pos=0

    if pressed(btnR,True):
      display.fill(0)
      display.text("launching " , 5, 20, 1)
      display.text(module_names[file_pos + screen_pos], 5, 40, 1)
      display.show()
      sleep_ms(1000)
      module_name = module_names[file_pos + screen_pos]
      return True

    if pressed(btnL,True):
      launched = True
      display.fill(0)
      display.text("exited ", 5, 24, 1)
      display.show()
      return False
    display.show()

go_on = True
while go_on :

  go_on = do_menu()
  if go_on :
    gc.collect()
    module = __import__(module_name)
    del sys.modules[module_name]
    gc.collect()
