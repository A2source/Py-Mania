'''*************************************************************************
Name: Util
Date: Jan. 20, 2023
Course: Sun West DLC Computer Science 20
Program Description: This file contains a few utility functions that are used multiple times throughout the project.
                     exit, is_dark, and compare_from_range are present.
********************************************************************'''

import pygame
import math, sys

## exit() function exits!
def exit():
    
    # quit everything
    pygame.quit()
    sys.exit()

    
# function to check brightness of colour (for default font colour / freeplay image colour)
# http://alienryderflex.com/hsp.html
def is_dark(colour):

    # setup colour variable
    [r, g, b, a] = colour
    
    # run HSP calc
    hsp = math.sqrt(0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b))
    
    # if light return false
    if (hsp > 127.5):
        return False
        
    else:
        # else return true
        return True
        

# +/- util
def compare_from_range(init, value, range):
    
    # just a +/- comparison of two numbers. return true if in range, false if not
    if value <= init + range and value >= init - range:
        return True
    else:
        return False