'''*************************************************************************
Name: Classes
Date: Jan. 20, 2023
Course: Sun West DLC Computer Science 20
Program Description: This file houses all of the utility Python classes that are reused throughout the project. 
                     Image, Text, Timer, Button, and TextInput classes are housed here.
********************************************************************'''

import time, os, configparser
import tween
import pygame
from pygame.locals import *

# setup the config parser. It loads the player_settings.ini file in '/config' and loads, as it says, settings.
p_settings = configparser.RawConfigParser()
p_settings.read_file(open('config/player_settings.ini'))

## the Image class will be used to easily create a surface / graphic
#   texture (the texture of the image)
#   x (x pos)
#   y (y pos)

class Image():
    
    def __init__(self, texture, x, y, scale, align='topleft'):
        self.image = pygame.image.load(os.path.join('assets', texture + '.png')).convert_alpha()
        self.scale = scale
        
        image_rect = self.image.get_rect()
        image_rect.x = x
        image_rect.y = y
        self.xpos = image_rect.x
        self.ypos = image_rect.y
        self.rect = image_rect
        self.pos = pygame.math.Vector2(self.xpos, self.ypos)
        
        self.rect.h *= self.scale
        self.rect.w *= self.scale
        
        # set alingment (if specified)
        setattr(self.image.get_rect(), align, self.pos)
        
    def draw(self, surf):
        surf.blit(pygame.transform.smoothscale_by(self.image, self.scale), (self.xpos, self.ypos))
        
        
## the Text class will be used to optimize performance (just displaying the fps as text made the fps drop - ironic, isn't it?))
#   text (font string)
#   font (text font)
#   scale (text size)
#   colour (text colour)
#   alignment (text alignment (example: right, middle, left))
#   pos (x and y pos)
#   align (align rect to which point?)
#   antialias (is text anti-aliased?)

class Text():
    
    def __init__(self, text, pos, font, scale, colour, align="topleft", antialias=True):
        # create text data
        self.image = font.render(text, antialias, colour)
        self.rect = self.image.get_rect()
        self.scale = scale
        # set align
        setattr(self.rect, align, pos)
        
        self.alive = True
        
    def draw(self, surf):
        if self.alive:
            surf.blit(pygame.transform.smoothscale_by(self.image, self.scale), self.rect)       
       
       
## the Timer class will be used to count ms from a certain point
#   clock (the timer that counts the total ms held)
#   current_ms (total time elapsed in milliseconds)
#   dt (the change in time, or "delta time")
#   counting (is timer counting?)
#   id (the id of the timer)

class Timer():
    
    def __init__(self, ID):
        # setip initial variables
        self.counting = False
        self.clock = None
        self.current_ms = 0
        self.dt = 0
        
        # to create different timers for each receptor
        self.id = ID
        
    def start(self, start_ms):
        
        # start a timer
        if self.clock is not None:
            raise Exception('Timer is running. Please stop the current timer first.')
        
        self.clock = time.perf_counter() - start_ms
            
        self.counting = True
        
    def count(self, use_offset=False, grid=None):
        # calc timer with or without global offset?
        if use_offset:
            self.dt = time.perf_counter() - self.clock - (p_settings.getfloat('Gameplay', 'global offset') / 1000)
        else:
            self.dt = time.perf_counter() - self.clock
        
        # for chart grid. count each grid's ms based on how far away the grid segment is from the center
        if grid != None:
            for x in range(0, len(grid)):
                for y in range(0, len(grid[x])):
                    segment = grid[x][y]
                    segment.cur_ms = self.dt * 1000 + segment.mult * 1000

    def reset(self, set_zero=False):
        
        # reset / stop timer
        if self.clock is None:
            raise Exception('Timer is not running. Please start a timer first.')

        if set_zero:
            self.dt = 0

        else:
            self.dt = time.perf_counter() - self.clock
        
        self.counting = False
        self.clock = None
        
    def pause(self, pause):
        # pause and resume (mostly for songs)
        self.counting = pause
        
        if self.clock == None:
            self.clock = time.perf_counter()
    
    
## the Button class is used to, be a button. On the title screen, options menu, pause menu, etc.   
#   rect (button bg, and where click detection is based from)
#   colour (the button colour)
#   init colour (the idle colour (not hovering))
#   active colour (is mouse hovering? use this colour)
#   font (font to use for label)
#   font colour (colour of button font)
#   text (string to display on the button)
#   hovering (is the mouse hovering?)
#   was hovering (check if the button was being hovered previously. used to detect hovering to play sfx)

class Button():

    def __init__(self, text, x, y, w, h, colour, active_colour, font, font_colour):
        # init variables
        self.rect = pygame.Rect(x, y, w, h)
        self.colour = colour
        self.init_colour = colour
        self.active_colour = active_colour
        self.font = font
        self.font_colour = font_colour
        self.text = text
        self.hovering = False
        self.was_hovering = False
        
    def draw(self, surf):
        # draw background and text
        pygame.draw.rect(surf, self.colour, self.rect, 0)
        text = self.font.render(self.text, 1, self.font_colour)
        surf.blit(text, text.get_rect(center = self.rect.center))
        
    def update(self, events, surf, func=None, func_arg1=None, func_arg2=None):
        # get mouse pos and check if hovering
        mpos = pygame.mouse.get_pos()
        self.hovering = self.rect.collidepoint(mpos)

        if self.hovering != self.was_hovering and self.hovering:
            # play hover sound
            pygame.mixer.Sound('sounds/hover.wav').play()

        self.was_hovering = self.hovering
        
        # set hover colour
        if self.hovering:
            self.colour = self.active_colour
            
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:

                        # play interacting sound
                        pygame.mixer.Sound('sounds/interact.wav').play()
                        
                        # run function if the button has one.
                        if func != None:
                            if func_arg1 != None and func_arg2 == None:
                                func(func_arg1)
                                
                            elif func_arg1 != None and func_arg2 != None:
                                func(func_arg1, func_arg2)
                                
                            else:
                                func()
                
        else:
            # else not hovering
            self.colour = self.init_colour
        
        # draw button
        self.draw(surf)
        

## the TextInput class is used in the chart editor for the input boxes. a string is saved and can be used for later.
#   rect (the textbox that the player selects)
#   font (font to use for text)
#   font colour (colour of font)
#   hovering (is mouse hovering over box?)
#   typing (is typing mode on?)
#   font size (size of display font)
#   saved variable (variable saved in the box)
#   idle colour (idle colour of box)
#   hover colour (colour of box if hovering)
#   typing colour (colour of box if typing)
#   current text (currently inputted text)
#   initial string (what should be or what was the initial string?)

class TextInput():
    
    def __init__(self, init_text, x, y, w, h, colour, hover_colour, typing_colour, font, font_colour, font_size):
        # setup rect and font
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.font_col = font_colour
        
        # hovering and typing
        self.hovering = False
        self.typing = False
        
        # other vars
        self.font_size = font_size
        
        self.saved_var = init_text
        
        # setup colours
        self.idle_col = colour
        self.hover_col = hover_colour
        self.typing_col = typing_colour
        self.cur_col = self.idle_col
        
        # create text and init string
        self.text = Text(init_text, (self.rect.midleft[0] + 5, self.rect.midleft[1] + 5), self.font, self.font_size, self.font_col, 'midleft')
        self.init_string = init_text
        
    def draw(self, surf):   
        # DRAW IT ALL
        pygame.draw.rect(surf, self.cur_col, self.rect)
        self.text.draw(surf)
        
    def update(self, surf, events):
        
        self.draw(surf)
        
        # get mouse position and hovering
        mpos = pygame.mouse.get_pos()
        self.hovering = self.rect.collidepoint(mpos)
        
        # set colour occording to state
        if self.hovering and not self.typing:
            self.cur_col = self.hover_col
            
        elif self.typing:
            self.cur_col = self.typing_col
            
        else:
            self.cur_col = self.idle_col
            
        for event in events:
            
            # if clicked, type. if not hovering, dont type anymore.
            if event.type == pygame.MOUSEBUTTONDOWN:    
                if event.button == 1:
                    if self.hovering:
                        # play interaction sound
                        pygame.mixer.Sound('sounds/interact.wav').play()
                        self.typing = True
                    else:
                        self.typing = False
                        
            elif event.type == pygame.KEYDOWN:
                # get text input. limit string length, unless backspace or enter is pressed.
                if self.typing and len(self.saved_var) + 1 <= 24 or self.typing and event.key == pygame.K_BACKSPACE or self.typing and event.key == pygame.K_RETURN:
                    # set repeat key presses and key variable
                    pygame.key.set_repeat(430, 15)
                    key = pygame.key.name(event.key)

                    # play interaction sound
                    pygame.mixer.Sound('sounds/interact.wav').play()
                    
                    # get inputted key
                    if key == 'return': 
                        self.typing = False
                        
                    elif event.key == pygame.K_BACKSPACE:
                        self.saved_var = self.saved_var[:-1]
                        
                    elif key == 'left shift' or key == 'right shift':
                        self.saved_var = self.saved_var
                        
                    else:
                        self.saved_var += event.unicode
                    
                    # set display text and variable
                    print(self.saved_var)
                    self.text = Text(self.saved_var, (self.rect.midleft[0] + 5, self.rect.midleft[1] + 5), self.font, self.font_size, self.font_col, 'midleft')


## the Transition class is used to transition between the different menus in the game.
#   type (what type of transition should it be? (currently "sweep" is the only one))
#   timer (the timer that counts how far into the transition we currently are)
#   length (what the length of the transition should be)
#   started (is the transition started?)
#   transitioning (True if the transition is currently running. used for denying input if the transition is happening)
#   halfway (flag for halfway through the transition. This is when the new main function is run (when the screen is completely filled), and when the second half of the transition begins)
#   finished (is the transition finished?)
#   tween (the current tween of the transition asset)
#   play menu music (a flag that checks if menu music should be played or not)
        
class Transition():
    
    def __init__(self, type, transition_length):
        
        # setup type and image for type
        self.type = type
        
        if self.type == 'sweep':
            self.image = Image('screen', 1280, 0, 1)
        
        # setup length and transition variables
        self.length = transition_length
        
        self.timer = Timer(0)
        self.started = False
        self.transitioning = False
        self.halfway = False
        self.finished = False
        
        # setup tween and tweening group
        self.group = tween.Group()
        self.tween = None

        self.play_menu_music = False
        self.play_transition_sound = True
        
    def start(self):
        
        # start the transition and run the first tween
        self.started = True
        self.transitioning = True
        if self.timer.counting:
            self.timer.reset()
        self.timer.start(0)
    
        if self.type == 'sweep':
            self.tween = tween.to(self.image, 'xpos', 0, int(self.length / 2) - 0.4, 'easeInExpo')

        # play transitioning sound
        if self.play_transition_sound:
            pygame.mixer.Sound('sounds/transition.wav').play()
            
    def finish(self):
        
        # sets the halfway flag which is used for scene switching and stuff
        self.halfway = True
        self.started = False
        
        # disable tween and start the next one
        if self.type == 'sweep':
            self.tween.stop()
            self.tween = tween.to(self.image, 'xpos', -1300, int(self.length / 2) - 0.2, 'easeOutExpo')

        # start menu music if flag is set
        if self.play_menu_music:
            pygame.mixer.music.load('sounds/music/menu.mp3')
            pygame.mixer.music.set_volume(0.15)
            pygame.mixer.music.play(-1, 0)

    def update(self, surf):
        
        # update timer
        self.timer.count()
        
        # if halfway through time, start second half of transition
        if int(self.timer.dt) == int(self.length / 2):
            self.finish()
        
        # check end of transition and finish it
        elif int(self.timer.dt) == self.length:
            self.transitioning = False
            self.finished = True
    
    def reset(self):
    
        # set all variables back to initial value and move image back to start
        self.started = False
        self.finished = False
        self.transitioning = False
        self.halfway = False

        self.play_menu_music = False
        self.play_transition_sound = True
        
        if self.type == 'sweep':
            self.image.xpos = 1280
        
        if self.timer.counting:
            self.timer.reset()