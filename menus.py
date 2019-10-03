import os
import sys
import gc
gc.collect()
print (gc.mem_free())
from machine import Pin, ADC
from utime import sleep_ms, ticks_ms, ticks_diff
module_name = ""

import game8266
from game8266 import Game8266

g = Game8266()
max_vol = 6
vol = 5
duty=[0,1,3,5,10,70,512]
tone_dur = 20

def do_menu () :
  global module_name, vol, max_vol

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
    g.display.fill(0)
    g.display.text('V:{} M:{}'.format(vol, gc.mem_free()), 5, 0, 1)
    i = 0
    for j in range (file_pos, min(file_pos+tot_rows, tot_file)) :
      current_row = 12 + 10 *i
      if i == screen_pos :
        g.display.fill_rect(5, current_row, 118, 10, 1)
        g.display.text(str(j) + " " + module_names[j], 5, current_row, 0)
      else:
        g.display.fill_rect(5, current_row, 118, 10, 0)
        g.display.text(str(j) + " " + module_names[j], 5, current_row, 1)
      i+=1
    g.display.show()
    g.getBtn()

    if g.pressed(g.btnU,True):
        g.playTone('c4', tone_dur)
        if screen_pos > 0 :
            screen_pos -= 1
        else :
            if file_pos > 0 :
                file_pos = max (0, file_pos - tot_rows)
                screen_pos=tot_rows-1

    if g.pressed(g.btnL):
        vol= max (vol-1, 0)
        g.tone_vol = duty[vol]
        g.playTone('d4', tone_dur)

    if g.pressed (g.btnR):
        vol = min (vol+1, max_vol)
        g.tone_vol = duty[vol]
        g.playTone('e4', tone_dur)

    if g.pressed(g.btnD,True):
        g.playTone('e4', tone_dur)
        if screen_pos < min(tot_file - file_pos - 1, tot_rows -1) :
            screen_pos = min(tot_file-1, screen_pos + 1)
        else :
            if file_pos + tot_rows < tot_file :
              file_pos = min (tot_file, file_pos + tot_rows)
              screen_pos=0

    if g.pressed(g.btnA,True):
        g.playTone('c5', tone_dur)
        g.display.fill(0)
        g.display.text("launching " , 5, 20, 1)
        g.display.text(module_names[file_pos + screen_pos], 5, 40, 1)
        g.display.show()
        sleep_ms(1000)
        module_name = module_names[file_pos + screen_pos]
        return True

    if g.pressed(g.btnB,True):
        g.playTone('d5', tone_dur)
        launched = True
        g.display.fill(0)
        g.display.text("exited ", 5, 24, 1)
        g.display.show()
        return False
    g.display.show()

go_on = True
while go_on :

  go_on = do_menu()
  if go_on :
    gc.collect()
    module = __import__(module_name)
    del sys.modules[module_name]
    gc.collect()
