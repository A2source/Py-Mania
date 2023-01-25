'''*************************************************************************
Name: Option
Date: Jan. 20, 2023
Course: Sun West DLC Computer Science 20
Program Description: This file houses the classes used in the options menu.
                     The Option class is contained here.
********************************************************************'''

import configparser, os
import pygame
from pygame.locals import *

from util.Classes import Text, Image, Button
from util.Util import is_dark

# init fonts
pygame.font.init()

# setup the config parser. It loads the player_settings.ini file in '/config' and loads, as it says, settings.
p_settings = configparser.RawConfigParser()
p_settings.read_file(open('config/player_settings.ini'))

# set up screen center values
GAME_RECT = pygame.Rect(0, 0, 1280, 720)
centerX = GAME_RECT.centerx - 35
centerY = GAME_RECT.centery

# create fonts
DETAILS_FONT = pygame.font.Font(os.path.join('fonts', 'metropolis.otf'), 20)
DETAILS_FONT_BIG = pygame.font.Font(os.path.join('fonts', 'metropolis.otf'), 60)

## the Option class is used in the options menu for easy option creation and expansion. multiple different types of options are present (bool, float, etc)

## GENERAL VARIABLES
#   default colour (the default colour of the text displayed)
#   hovering (is the mouse hovering over that options selection point?)
#   rect (where to get the mouse collision)
#   x & y (position in space)
#   header (the section in the config file to look at)
#   option (the option in that section to look at)
#   type (which type of option it is. bool, float, int, colour, keybind, header)
#   status (the variable loaded from config. saved for editing / reference)
#   new variable (the variable to save to config when the user is done changing)
#   active (if the option is being selected (or another option's menu isn't open). basically controls if the user can change it or not.)
#   info box (where info on the option is stored. A list of strings with the option description, and the box image)

## BOOL OPTION
#   uncheck (the unchecked checkbox image)
#   check (checked checkbox image)
#   image (use the right image if option is True or False)
# in this case, option status will be True or False

## FLOAT & INT OPTIONS
#   typing (is the user currently in typing mode?
#   bg (the background rect. If it is being hovered and you click, "typing" is true)
#   min (minimum value)
#   max (maximum value. user entered variable is clamped between min and max)
# in this case, status will be float or int respectively

## COLOUR OPTION
#   image (the box in the menu which displays the currently saved colour)
#   menu image (background of the colour picker menu)
#   menu assets (a list of every asset to be loaded when the colour picker menu is open. A colour gradient to click on, and three texts (r, g, & b values respectively))
# in this case, status will be a pygame Color object

## KEYBIND OPTION
#   menu assets (the assets that are loaded when the menu is opened. A set of 8 buttons to set keybinds)
#   instructions (the instructions that are drawn when a user needs to enter the key)
#   current key (what key is currently being changed)
# in this case, status will be a list of key names

## HEADER
#   the header is just a bigger text asset. It divides the different config sections, and just uses the "header" arg as the text to display.
# in this case, status is nothing (as there is no option to change)

class Option():

    def __init__(self, header, option, info, x, y, surf, type, min=0, max=0):
        #  setup initial text colour (and colour of other things, like outlines of boxes)
        bg_dark = is_dark(list(map(int, p_settings.get('Visual', 'bg colour').split())))
        
        if bg_dark:
            self.default_colour = (255, 255, 255)
        else:
            self.default_colour = (0, 0, 0)
        
        # set float and int textbox colour
        self.rect_col = (255, 255, 255)
        self.rect_hover_col = (200, 200, 200)
        self.rect_sel_col = (135, 135, 135)
        self.cur_rect_col = self.rect_col
        
        # set display text and rect of that text
        self.text = Text(option, (x, y), DETAILS_FONT_BIG, 0.95, self.default_colour)
        self.rect = self.text.rect
        
        # mouse hovering variables (and one for the colour picker)
        self.hovering = False
        self.hovering_colour = False
        
        # position
        self.x = x
        self.y = y
        
        # is typing?
        self.typing = False
        self.bg = None
        
        # float and int min and max vars
        self.min = min
        self.max = max
        
        # if the min or max is negative, set this (for fixing typing later)
        self.can_be_negative = False
        
        if self.min < 0 or self.max < 0:
            self.can_be_negative = True
        
        # header and option vars
        self.header = header
        self.option = option
        
        # load from config
        player_settings = p_settings.read_file(open('config/player_settings.ini'))
        
        # set type, and new var save
        self.type = type
        self.new_var = ''
        
        # is option active? (or is the options menu open?)
        self.active = True
        self.menu_active = False
        
        # info box bg image
        self.info_box = Image('info_box', 0, 0, 0.9)
        self.info_box.image.get_rect().center = surf.get_rect().center
        self.info_box.xpos += 200
        self.info_box.ypos += 525
        
        # turn info string into a list of strings, to be drawn later (pygame font renderer can't do \n so I have to improvise)
        self.info = info.split('\n')
        print(self.info)
        self.info_text = {}
        for x in range(1, len(self.info) + 1):
            self.info_text[f'string{x - 1}'] = Text(self.info[x - 1], (self.info_box.xpos + 50, self.info_box.ypos + 20 + (x - 1) * 40), DETAILS_FONT_BIG, 0.55, (255, 255, 255))
        
        # bool option vars
        if type == 'bool':
            self.status = p_settings.getboolean(header, option)
            self.uncheck = Image('box', self.rect.midright[0], self.rect.topright[1] - 5, 0.9)
            self.check = Image('box_checked', self.rect.midright[0], self.rect.topright[1] - 5, 0.9)
            self.image = self.uncheck
            self.check_rect = self.image.image.get_rect()
        
        # float option vars
        elif type == 'float':
            self.status = p_settings.getfloat(header, option)
            self.image = Text(str(self.max), (self.rect.midright[0] + 18, self.rect.topright[1]), DETAILS_FONT_BIG, 0.95, (0, 0, 0))
            
            self.bg = pygame.Rect(self.rect.midright[0] + 13, self.rect.topright[1], self.image.rect.w + 25, 60)
            self.image = Text(str(self.status), (self.rect.midright[0] + 18, self.rect.topright[1]), DETAILS_FONT_BIG, 0.95, (0, 0, 0))
        
        # int option vars (has to be different, because config needs getint or getfloat)
        elif type == 'int':
            self.status = p_settings.getint(header, option)
            self.image = Text(str(self.max), (self.rect.midright[0] + 18, self.rect.topright[1]), DETAILS_FONT_BIG, 0.95, (0, 0, 0))
            
            self.bg = pygame.Rect(self.rect.midright[0] + 13, self.rect.topright[1], self.image.rect.w + 25, 60)
            self.image = Text(str(self.status), (self.rect.midright[0] + 18, self.rect.topright[1]), DETAILS_FONT_BIG, 0.95, (0, 0, 0))
        
        # colour option vars
        elif type == 'colour':
            # convert config's saved string into a list (which can be used as a Color object)
            self.status = list(map(int, p_settings.get(header, option).split()))
            
            self.image = pygame.Rect(self.rect.midright[0] + 13, self.rect.topright[1] - 5, 75, 75)
            
            self.menu_image = Image('full_box', 270, 5, 0.9, 'center')
            
            self.menu_assets = {}
            
            # menu bg
            self.menu_assets['asset0'] = Image('colours', self.menu_image.rect.center[0] - 235, self.menu_image.rect.y + 125, 0.8, 'center')
            
            # r
            self.menu_assets['asset1'] = Text(str(self.status[0]), (self.menu_image.rect.center[0] - 250, self.menu_image.rect.center[1] + 150), DETAILS_FONT_BIG, 1.2, self.status,'center')
            
            # g
            self.menu_assets['asset2'] = Text(str(self.status[1]), (self.menu_image.rect.center[0] - 10, self.menu_image.rect.center[1] + 150), DETAILS_FONT_BIG, 1.2, self.status,'center')
            
            # b
            self.menu_assets['asset3'] = Text(str(self.status[2]), (self.menu_image.rect.center[0] + 250, self.menu_image.rect.center[1] + 150), DETAILS_FONT_BIG, 1.2, self.status,'center')
        
        # keybind option vars
        elif type == 'keybind':
            # same logic as colour status, just for keybinds
            self.status = list(map(str, p_settings.get(header, option).split()))
            self.image = Button('Edit Keybinds', self.rect.midright[0] + 20, self.rect.topright[1] - 5, 150, 75, (189, 189, 189), (230, 230, 230), DETAILS_FONT, (0, 0, 0))
            self.menu_image = Image('full_box', 265, 5, 0.9, 'center')
            
            self.menu_assets = {}
            self.current_key = None
            
            self.instructions = Text('- Input Key -', (surf.get_rect().centerx + 77, surf.get_rect().centery + 285), DETAILS_FONT_BIG, 0.6, (255, 255, 255), 'center')
            
            # positions of the buttons in the menu
            positions = [(centerX - 170, centerY - 170), 
            (centerX + 40, centerY - 170),
            (centerX + 250, centerY - 170),
            (centerX + 250, centerY),
            (centerX + 250, centerY + 170),
            (centerX + 40, centerY + 170),
            (centerX - 170, centerY + 170),
            (centerX - 170, centerY)]
            
            # add each button
            for x in range(0, 8):
                self.menu_assets[f'asset{x}'] = Button(self.status[x], positions[x][0], positions[x][1], 200, 100, (189, 189, 189), (215, 215, 215), DETAILS_FONT, (0, 0, 0))
                self.menu_assets[f'asset{x}'].rect.center = positions[x]
        
        # header option vars
        elif type == 'header':
            
            # beeeg text
            self.text = Text(header, (x, y), DETAILS_FONT_BIG, 1.5, self.default_colour)
            self.text.rect.y += 40
            self.text.rect.h += 10
            
    def set_keybind(self, id, events):
        
        # setup which key to change
        keybind = self.menu_assets.get(f'asset{id}')
        self.typing = True
        self.current_key = id
        print(self.typing)
        print(self.current_key)
        
    def update(self, events, surf, can_interact):
        
        # draw everythang
        self.draw(surf)
        
        # check bool option status and set image
        if self.type == 'bool':
            if self.status:
                self.image = self.check
            else:
                self.image = self.uncheck
        
        # change float and int option display text
        elif self.type == 'float' or self.type == 'int':
            self.image = Text(str(self.status), (self.rect.midright[0] + 25, self.rect.topright[1]), DETAILS_FONT_BIG, 0.95, (0, 0, 0))
        
        # mouse position get
        mpos = pygame.mouse.get_pos()
        
        if self.type == 'colour':
            # for colour option, check if user is hovering over small colour box and menu colour picker
            self.hovering = self.image.collidepoint(mpos)
            
            if self.menu_active:
                self.hovering_colour = self.menu_assets.get('asset0').rect.collidepoint(mpos)
                
        elif self.type == 'keybind':
            
            # if not menu active, update menu open button and check hovering
            if not self.menu_active:
                self.image.update(events, surf)
                self.hovering = self.image.rect.collidepoint(mpos)
                
            else:
                # else, open menu and update menu buttons instead
                self.hovering = False
                for x in range(0, len(self.menu_assets)):
                    button = self.menu_assets.get(f'asset{x}')
                    
                    if not self.typing:
                        button.update(events, surf, self.set_keybind, x, events)
                        
                    self.hovering = button.hovering
        
        elif self.type == 'float' or self.type == 'int':
            # check bg rect hovering
            self.hovering = self.bg.collidepoint(mpos)
            
            # set rect colour (if typing, hovering, or none)
            if self.active:
                if self.hovering and not self.typing:
                    self.cur_rect_col = self.rect_hover_col
                elif self.typing:
                    self.cur_rect_col = self.rect_sel_col
                else:
                    self.cur_rect_col = self.rect_col
        
        elif self.type != 'header':
            # and if not header, set option active if hovering
            self.hovering = self.image.rect.collidepoint(mpos)
            
        for event in events:
            if self.active:
                
                # I check MOUSEBUTTONUP event so that a keybind input isn't immediatly pressed if your mouse overlaps with it
                if event.type == pygame.MOUSEBUTTONUP and self.hovering:
                    if event.button == 1 and self.type == 'keybind' and can_interact:
                        self.menu_active = True
                
                # if you are hovering over option, and interactions are allowed
                if event.type == pygame.MOUSEBUTTONDOWN and self.hovering and can_interact:
                    if event.button == 1:

                        # play interaction sound
                        pygame.mixer.Sound('sounds/interact.wav').play()

                        if self.type == 'bool':
                            # swap bool from false to true or vice versa
                            p_settings.set(self.header, self.option, str(not self.status))
                            
                            # set status
                            self.status = p_settings.getboolean(self.header, self.option)
                            
                            # save to config
                            with open('config/player_settings.ini', 'w') as file:
                                p_settings.write(file)
                                
                        elif self.type == 'float' or self.type == 'int':
                            # set typing mode
                            self.typing = True
                            
                        elif self.type == 'colour':
                            # set colour picker menu active
                            self.menu_active = True
                
                # same thing if hovering over colour picker gradient
                elif event.type == pygame.MOUSEBUTTONDOWN and self.hovering_colour and self.menu_active:
                    if event.button == 1:
                        
                        # get the colour at the mouse position and set the var to save to that colour
                        self.status = surf.get_at(mpos)
                        self.new_var = str(self.status).replace(',', '').replace('(', '').replace(')', '').split()
                        self.new_var = ' '.join(self.new_var)
                        
                        # set colour in config
                        p_settings.set(self.header, self.option, self.new_var)
                        
                        # update rbg text
                        self.menu_assets['asset1'] = Text(str(self.status[0]), (self.menu_image.rect.center[0] - 250, self.menu_image.rect.center[1] + 150), DETAILS_FONT_BIG, 1.2, self.status,'center')
                        self.menu_assets['asset2'] = Text(str(self.status[1]), (self.menu_image.rect.center[0] - 10, self.menu_image.rect.center[1] + 150), DETAILS_FONT_BIG, 1.2, self.status,'center')
                        self.menu_assets['asset3'] = Text(str(self.status[2]), (self.menu_image.rect.center[0] + 250, self.menu_image.rect.center[1] + 150), DETAILS_FONT_BIG, 1.2, self.status,'center')
                        
                        # save to config file
                        with open('config/player_settings.ini', 'w') as file:
                            p_settings.write(file)
                
                # if not hovering and you click, stop typing (int and float option)
                elif event.type == pygame.MOUSEBUTTONDOWN and self.typing and not self.hovering and not self.type == 'keybind':
                    if event.button == 1:
                        self.typing = False
                
                if event.type == pygame.KEYDOWN:
                    
                    # if you hit escape and colour picker is open, close it
                    if event.key == pygame.K_ESCAPE:
                        if self.type == 'colour':
                            self.menu_active = False
                        
                        # same thing for keybind menu
                        elif self.type == 'keybind':
                            if not self.typing:
                                self.menu_active = False
                    
                    if self.typing:

                        # play interaction sound
                        pygame.mixer.Sound('sounds/interact.wav').play()

                        # if you are typing and option is keybind option:
                        if self.type == 'keybind':
                            
                            # set status in the right position to the hit key
                            print(self.status)
                            print(self.current_key)
                            self.status[self.current_key] = pygame.key.name(event.key)
                            
                            # set var to save to config
                            self.new_var = str(self.status).replace(',', '').replace('[', '').replace(']', '').replace("'", '').split()
                            self.new_var = ' '.join(self.new_var)
                            
                            # set in  config
                            p_settings.set(self.header, self.option, self.new_var)
                            
                            # update text on the button in the keybind changer menu
                            self.menu_assets.get(f'asset{self.current_key}').text = pygame.key.name(event.key).replace("'", '').replace('[', '').replace(']', '')
                            
                            # save to config file
                            with open('config/player_settings.ini', 'w') as file:
                                p_settings.write(file)
                            
                            print(self.status[self.current_key])
                            
                            # stop setting keybind
                            self.typing = False
                        
                        # else if option type is int or float
                        else:
                            
                            # legal characters
                            chars = '1234567890-'
                            
                            # floats have decimals
                            if self.type == 'float':
                                chars += '.'
                                
                            print(self.new_var)
                            
                            if pygame.key.name(event.key) in chars:
                                
                                # if you type a negative and the variable can be negative, add it to the start
                                if pygame.key.name(event.key) == '-':
                                    if self.can_be_negative:
                                        if self.new_var.startswith('-'):
                                            new_string = self.new_var.replace('-', '')
                                            self.new_var = new_string
                                            
                                        else:
                                            new_string = '-' + self.new_var
                                            self.new_var = new_string
                                
                                elif pygame.key.name(event.key) == '.' and len(self.new_var) == 0:
                                    # fix a bug that tries to convert '.' into a float
                                    self.new_var = '0.'
                                
                                else:

                                    # check if entered number is between min and max. clamp it.
                                    if self.type == 'float':
                                        print(self.new_var + pygame.key.name(event.key))
                                        if self.max >= float(self.new_var + pygame.key.name(event.key)) >= self.min:
                                            self.new_var += pygame.key.name(event.key)
                                            
                                    elif self.type == 'int':
                                        if self.max >= int(self.new_var + pygame.key.name(event.key)) >= self.min:
                                            self.new_var += pygame.key.name(event.key)
                                
                                self.status = self.new_var
                                print(self.status)
                                
                                # if var is legal, set it in config
                                if self.new_var != '' and self.new_var != '-' and self.new_var != '.':
                                    if self.type == 'float':
                                        p_settings.set(self.header, self.option, float(self.new_var))
                                    elif self.type == 'int':
                                        p_settings.set(self.header, self.option, int(self.new_var))
                                else:
                                    p_settings.set(self.header, self.option, 0)
                            
                            # backspace to delete a char, and set it if legal
                            elif event.key == pygame.K_BACKSPACE:
                                self.new_var = self.new_var[:-1]
                                self.status = self.new_var
                                 
                                if self.new_var != '' and self.new_var != '-' and self.new_var != '.':
                                    p_settings.set(self.header, self.option, float(self.new_var))
                                else:
                                    p_settings.set(self.header, self.option, 0)
                            
                            # close typing if enter
                            elif event.key == pygame.K_RETURN:
                                self.typing = False
                            
                            # save config file
                            with open('config/player_settings.ini', 'w') as file:
                                p_settings.write(file)
        
    def draw(self, surf):
        
        # draw float and int option bg rect
        if self.type == 'float' or self.type == 'int':
            pygame.draw.rect(surf, self.cur_rect_col, self.bg)
        
        # draw option menu display text
        self.text.draw(surf)
        
        # if colour type, draw rect as the status and outline it
        if self.type == 'colour':
            pygame.draw.rect(surf, self.default_colour, self.image.inflate(10, 10))
            pygame.draw.rect(surf, self.status, self.image)
            
            # if menu active, draw all menu assets
            if self.menu_active:
                self.menu_image.draw(surf)
                
                for x in range(0, len(self.menu_assets)):
                    asset = self.menu_assets.get('asset{}'.format(x))
                    asset.draw(surf)
        
        # if keybind type, draw button and outline too
        elif self.type == 'keybind':
            pygame.draw.rect(surf, self.default_colour, self.image.rect.inflate(6, 6))
            self.image.draw(surf)
            
        # if not header then option status display
        else:
            if self.type != 'header':
                self.image.draw(surf)
    
    # a function to draw specific pieces on top of every option (mostly for info box)
    def draw_post(self, surf):    
        
        # if keybind menu open, don't draw info
        if self.type == 'keybind':
            if self.active:
                if self.hovering and not self.menu_active:
                    self.info_box.draw(surf)
                    
                    # draw each string in info list
                    for x in range(len(self.info_text)):
                        text = self.info_text.get(f'string{x}')
                        text.draw(surf)
                
                # if menu active then draw menu buttons and instructions
                elif self.menu_active:
                    self.menu_image.draw(surf)
                    
                    for x in range(0, len(self.menu_assets)):
                        button = self.menu_assets.get(f'asset{x}')
                        button.draw(surf)
                        
                    if self.typing:
                        self.instructions.draw(surf)
        else:
            # for every other option, draw info boxes (and description strings) if the option is being hovered
            if self.active:
                if self.hovering and not self.menu_active:
                    self.info_box.draw(surf)
                    
                    for x in range(len(self.info_text)):
                        text = self.info_text.get(f'string{x}')
                        text.draw(surf)