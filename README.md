# ESP8266_spi_micropython_games
# A collection of micropython games written for ESP8266 Node MCU D1 Mini 
# with SPI OLED display SSD1306 
#
# list of games
# menus.py - menu system that should be called by main.py to be the first program running when boot up.
#            this will be the launcher for other games.
# btntests.py - button , paddle and beeper testing tool
# invaders.py - space invaders 
# snakes.py - snakes biting apple game
# pongs.py - 1 and 2 player ping pong games
# brekouts.py - brick game
# game8266.py - this is a common module required for all above games that controls the screens, buttons, paddles, and beepers, randominzatio and game refresh rates. 
# 
# note: due to the small CPU memory on the ESP8266, only 23K bytes, the above .py files need to be pre-compiled as byte codes using mpy-cross
# mpy-cross snakes.py
# the snakes.mpy file will be created.
# then you can copy that file into the flash memory of the ESP8266 using a terminal software e.g. rshell.
# e.g. cpy snakes.mpy /pyboard
# then to to repl to load the game.
# repl
# import snakes.
#
# Node MCU D1 mini is used for my build that have 4MB Flash memory, capable to store .mpy files (~5K byte) for many gams
#
#  The skematics of the set up can be found in the fizz files and jpg files
#  using ADC to sense the voltage dividers from either the paddle or the six buttons
#  and two control pins to activate either the paddle or the six buttons
#  Beeper for sound
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
