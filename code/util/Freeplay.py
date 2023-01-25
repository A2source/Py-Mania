'''*************************************************************************
Name: Freeplay
Date: Jan. 20, 2023
Course: Sun West DLC Computer Science 20
Program Description: This file contains all of the classes relating to the freeplay menu.
                     Contains FreeplaySong class.
********************************************************************'''

import os, configparser
from eyed3 import id3
from eyed3 import load
import pygame
from pygame.locals import *

from util.Classes import Text, Image
from util.Util import is_dark

# setup the config parser. It loads the player_settings.ini file in '/config' and loads, as it says, settings.
p_settings = configparser.RawConfigParser()
p_settings.read_file(open('config/player_settings.ini'))

## the FreeplaySong class is used in the freeplay menu. It displays song and chart name, and below, artist name
#   font (font to use)
#   image string (image png name. in '/assets')
#   dark image string (image string with "_dark" added to it)
#   default colour (white or black, based on bg darkness)
#   hover colour (colour the text should be if hovered)
#   hovering (is hovering?)
#   was hovering (detect if hovering previously occured. used to play sfx)
#   song path (full path of song)
#   song tag (id3 tag data of song)
#   song data (the loaded id3 tag)
#   song name (name of song to load)
#   chart name (name of chart to load)
#   info (the id3 tag data as a single variable)
#   font size (size of the font)
#   title, chart, and artist text (the text objects to draw)

class FreeplaySong():
    
    def __init__(self, name, chart_name, x, y, font, font_size, font_colour, image_string, image_scale):

        # read settings
        p_settings.read_file(open('config/player_settings.ini'))
        
        # setup font and image string
        self.font = font
        
        self.light_image_string = image_string
        # add "_dark" on
        self.dark_image_string = image_string + '_dark'
        
        # is dark or light?
        if is_dark(list(map(int, p_settings.get('Visual', 'bg colour').split()))):
            self.image = Image(self.dark_image_string, x, y, image_scale, 'midleft')
            self.default_colour = (0, 0, 0)
            self.hover_colour = (90, 90, 90)
        else:
            self.image = Image(self.light_image_string, x, y, image_scale, 'midleft')
            self.default_colour = (255, 255, 255)
            self.hover_colour = (170, 170, 170)

        self.hovering = False
        self.was_hovering = False
        
        # parse song data to load into the game
        song_path = f'songs/{name}/{name}.mp3'
        song_tag = id3.Tag()
        song_tag.parse(os.path.join(song_path))
        song_data = load(os.path.join(song_path))
        
        # song and chart name setup
        self.song_name = name
        self.chart_name = chart_name.replace('.json', '')
        
        self.info = song_data.tag
        
        self.font_size = font_size
        
        # add song title with chart name next to it (but smaller)
        # CONSCIENCE - test
        # TEST SONG - hard
        self.title_text = Text(self.info.title, (self.image.rect.midleft[0] + 5, self.image.rect.topleft[1] + 28), self.font, self.font_size, self.default_colour, 'midleft')
        self.chart_text = Text(f'- {self.chart_name}', (self.title_text.rect.midright[0] + 5, self.image.rect.midleft[1] - 22), self.font, self.font_size / 1.5, self.default_colour, 'midleft')
        
        self.artist_text = Text(self.info.artist, (self.image.rect.midleft[0] + 5, self.title_text.rect.bottomleft[1] + 35), self.font, self.font_size / 1.4, self.default_colour)
        
    def draw(self, surf):
        
        # draw it all yeah!
        self.image.draw(surf)
        self.title_text.draw(surf)
        self.chart_text.draw(surf)
        self.artist_text.draw(surf)
        
    def update(self, events, surf):
        
        self.draw(surf)
        
        # get mouse position and hover
        mpos = pygame.mouse.get_pos()
        self.hovering = self.image.rect.collidepoint(mpos)

        if self.hovering != self.was_hovering and self.hovering:
            # play hover sound
            pygame.mixer.Sound('sounds/hover.wav').play()

        self.was_hovering = self.hovering
        
        # if hovering, change colour of the text
        if self.hovering:

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and self.hovering:
                        # play interacting sound
                        pygame.mixer.Sound('sounds/interact.wav').play()

            self.title_text = Text(self.info.title, (self.image.rect.midleft[0] + 5, self.image.rect.topleft[1] + 28), self.font, self.font_size, self.hover_colour, 'midleft')
            self.chart_text = Text(f'- {self.chart_name}', (self.title_text.rect.midright[0] + 5, self.image.rect.midleft[1] - 22), self.font, self.font_size / 1.5, self.hover_colour, 'midleft')
            self.artist_text = Text(self.info.artist, (self.image.rect.midleft[0] + 5, self.title_text.rect.bottomleft[1] + 35), self.font, self.font_size / 1.4, self.hover_colour)
            
        else:
            self.title_text = Text(self.info.title, (self.image.rect.midleft[0] + 5, self.image.rect.topleft[1] + 28), self.font, self.font_size, self.default_colour, 'midleft')
            self.chart_text = Text(f'- {self.chart_name}', (self.title_text.rect.midright[0] + 5, self.image.rect.midleft[1] - 22), self.font, self.font_size / 1.5, self.default_colour, 'midleft')
            self.artist_text = Text(self.info.artist, (self.image.rect.midleft[0] + 5, self.title_text.rect.bottomleft[1] + 35), self.font, self.font_size / 1.4, self.default_colour)