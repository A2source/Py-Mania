'''*************************************************************************
Name: List
Date: Jan. 20, 2023
Course: Sun West DLC Computer Science 20
Program Description: This file contains all of the classes relating to the list menu.
                     It contains the SongList class.
********************************************************************'''

import os
import pygame
from pygame.locals import *

from util.Classes import Text, Button

# init fonts
pygame.font.init()

# setup fonts
DETAILS_FONT_MEDIUM = pygame.font.Font(os.path.join('fonts', 'metropolis.otf'), 35)
DETAILS_FONT_BIG = pygame.font.Font(os.path.join('fonts', 'metropolis.otf'), 60)
RATINGS_FONT = pygame.font.Font(os.path.join('fonts', 'bahnschrift.ttf'), 60)

## the SongList class is used in the list menu to create the list itself. Title, description, and song list are saved
#   rect (the body of the list object)
#   open (is the list open?)
#   idle colour (colour of list bg when not selected)
#   hover colour (colour when the list is being hovered over)
#   data (a list containing title, description, songs, and chart strings, to load into the program)
#   title (the title string of the list)
#   description (a list of strings (each line is a different element in the list))
#   songs to load (a 2d list of [song, chart] combos to load)
#   title, description, and song texts (the actual text objects containing the other variables)
#   play button (the button to hit that starts the list)
#   full rect (the rect that the list should be when opened (full size))

class SongList():
    
    def __init__(self, list_data, list_path, x, y):
        
        # setup rect
        self.rect = pygame.Rect(x, y, 800, 100)
        self.hovering = False
        self.was_hovering = False
        
        self.open = False
        
        # create colours
        self.idle_colour = (80, 80, 80)
        self.hover_colour = (120, 120, 120)
        self.colour = self.idle_colour
        
        # there's a bunch of finnicky stuff here with loading the text file. \n's have to be removed at each step to make the displayed string look correct
        self.data = list_data
        
        self.title = self.data[0].replace('\n', '')
        self.desc = self.data[1]
        
        songs_to_load = self.data[2].replace('\n', '').split('.json')
        self.songs_to_load = []
        
        for x in range(0, len(songs_to_load)):
            self.songs_to_load.append(songs_to_load[x].split(','))
            
        # remove empty string that is added to the end (for some reason. probably the removing \n stuff)
        del self.songs_to_load[-1]
        
        print()
        print(' ## LIST DATA ## ')
        print(f'Title: {self.title}')
        print(f'Description: {self.desc}')
        print(f'Songs and Charts to load: {self.songs_to_load}')
        
        # now the list data is formatted as a list to be loaded into the game!
        self.title_text = Text(self.title, (self.rect.center[0], self.rect.center[1] + 5), DETAILS_FONT_MEDIUM, 1, (255, 255, 255), 'center')
        
        # setup description string list
        self.desc = self.desc.split('\n')
        self.desc_text = []
        for x in range(0, len(self.desc)):
            self.desc_text.append(Text(self.desc[x - 1], (self.rect.x + 5, self.title_text.rect.bottomleft[1] - 10 + x * 40), DETAILS_FONT_BIG, 0.6, (255, 255, 255)))
        
        # do the same for the songs
        self.song_chart_texts = []
        for x in range(0, len(self.songs_to_load)):
            self.song_chart_texts.append(Text(f'{self.songs_to_load[x][0]} - {self.songs_to_load[x][1]}.json', (self.rect.x + 5, self.desc_text[len(self.desc_text)-1].rect.bottomleft[1] + 20 + x * 40), DETAILS_FONT_BIG, 0.6, (255, 255, 255)))
        
        # and charts
        if len(self.song_chart_texts) > 0:
            self.play_button = Button('Play', self.rect.center[0] - 250, self.song_chart_texts[len(self.song_chart_texts)-1].rect.bottomleft[1] + 20, 500, 75, (45, 45, 45), (120, 120, 120), RATINGS_FONT, (255, 255, 255))
            
        elif len(self.song_chart_texts) <= 0:
            # warning if list contains no songs (error!)
            self.play_button = Button('No Songs', self.rect.center[0] - 250, self.desc_text[len(self.desc_text)-1].rect.bottomleft[1] + 20, 500, 75, (45, 45, 45), (120, 120, 120), RATINGS_FONT, (255, 0, 0))
        
        # check if songs actually exist.
        all_good = True
        for x in range(0, len(self.song_chart_texts)):
            
            if not os.path.exists(f'songs/{self.songs_to_load[x][0]}/{self.songs_to_load[x][0]}.mp3'):
                all_good = False
                break
       
        # if a song doesn't exist, flag it and disable list frrom playing
        if not all_good:
            self.play_button = Button('Invalid Song(s)', self.rect.center[0] - 250, self.song_chart_texts[len(self.song_chart_texts)-1].rect.bottomleft[1] + 20, 500, 75, (45, 45, 45), (120, 120, 120), RATINGS_FONT, (255, 0, 0))
            
        self.play_button_hovering = False
        
        # setup desired full rect using rect.union and create desired height to be used later
        full_rect = self.rect.union(self.play_button.rect)
        self.opened_height = full_rect.h + 50
        
    def draw(self, surf):
        
        # draw rect and text
        pygame.draw.rect(surf, self.colour, self.rect)
        self.title_text.draw(surf)
        
        # if open, iterate through each string in the lists and draw
        if self.open:
            for string in self.desc_text:
                string.draw(surf)
                
            for song_chart_combos in self.song_chart_texts:
                song_chart_combos.draw(surf)
        
    def update(self, events, surf):
        
        self.draw(surf)
        
        # if open, make play button work
        if self.open:
            self.play_button.update(events, surf)
        
        # get mouse position and list / play button hover status
        mpos = pygame.mouse.get_pos()
        self.hovering = self.rect.collidepoint(mpos)
        self.play_button_hovering = self.play_button.hovering
        
        if self.hovering != self.was_hovering and self.hovering:
            # play hover sound
            pygame.mixer.Sound('sounds/hover.wav').play()

        self.was_hovering = self.hovering
        
        # set colour based on hover
        if self.hovering and not self.play_button.hovering:
            self.colour = self.hover_colour

        else:
            self.colour = self.idle_colour
        
        # set height to open if opened. Else, default height
        if self.open:
            self.rect.h = self.opened_height
            
        else:
            self.rect.h = 100
            
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    
                    # if left click, set open to the opposite of itself
                    if self.hovering and not self.play_button_hovering:
                        self.open = not self.open
                        
                        # play interacting sound
                        pygame.mixer.Sound('sounds/interact.wav').play()
                        
                    elif self.play_button.hovering:
                        print('ya')
                        # load songs and stuff
                        # this is done in list_main()
                        
                        # play interacting sound
                        pygame.mixer.Sound('sounds/interact.wav').play()
                    
                    elif not self.hovering:
                        self.open = False
                        
                        # play interacting sound
                        pygame.mixer.Sound('sounds/interact.wav').play()