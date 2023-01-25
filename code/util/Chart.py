'''*************************************************************************
Name: Chart
Date: Jan. 20, 2023
Course: Sun West DLC Computer Science 20
Program Description: This file contains all of the classes / functions that are related to the chart editor. 
                     ChartGrid, ChartNote, ChartHoldNote, chart_note_data_display, and save_json are here.
********************************************************************'''

import configparser, os
import pygame
from pygame.locals import *

from util.Classes import Image, Text

# init fonts
pygame.font.init()

# setup the config parser. It loads the player_settings.ini file in '/config' and loads, as it says, settings.
p_settings = configparser.RawConfigParser()
p_settings.read_file(open('config/player_settings.ini'))

# create font
DETAILS_FONT = pygame.font.Font(os.path.join('fonts', 'metropolis.otf'), 20)

# set up screen center values
GAME_RECT = pygame.Rect(0, 0, 1280, 720)
centerX = GAME_RECT.centerx - 35
centerY = GAME_RECT.centery


## the ChartGrid class will be used in the chart editor, to place notes into the chart
#   rect (the actual grid segment itself)
#   colour (what colour should it be?)
#   multiplier (depending on where out it is from the center, grid has a certain amount of ms added to it (based on how many ms a step is in the song))
#   hovering note (the uncoloured note that appears over a grid when you hover over it)
#   hover colour (grid segment hovering colour?)
#   idle colour (grid segment idle colour?)
#   hovering (hovering over grid segment with mouse?)
#   note (the note added to the grid)
#   recep id (which receptor the grid segment is a part of)
#   current ms (what the current ms value of the grid segment is (because of scrolling, it can change))
#   initial ms (what is the initial ms value of this grid segment?)
#   position in beats (current grid position in beats)
#   debug text (super debug mode text. just the current ms of the grid)

class ChartGrid():
    
    def __init__(self, x, y, w, h, ID, ms, colour, hover_col):
        
        # rect and rect colour
        self.rect = pygame.Rect(x, y, w, h)
        self.colour = colour
        
        # the mult is setup automatically in the chart_main()
        self.mult = ms
        
        # setup hovering note image
        self.hover_note = Image('note', self.rect.x, self.rect.y, 0.5)
        
        # grid segment hovering colour and init colour
        self.hover_col = hover_col
        self.init_col = colour
        
        # hovering and set note var
        self.hovering = False
        self.note = None
        
        # grid segment recep id, the current ms, and the init ms)
        self.recep_id = ID
        self.cur_ms = round(ms * 1000, 2)
        self.init_ms = self.cur_ms
        
        # current pos in beats
        self.pos_in_beats = 0
        
        # debug text setup
        self.text = Text(str(self.cur_ms), (self.rect.x, self.rect.y), DETAILS_FONT, 0.5, (255, 255, 255))
        
    def draw(self, surf, text_surf):
        # draw grid rect
        pygame.draw.rect(surf, self.colour, self.rect)
        
        # if super debug on, draw ms text
        if p_settings.getboolean('Debug', 'super debug mode'):
            self.text.draw(text_surf)
        
    def update(self, events, receptors, note_list, spawn_pos_list, surf, text_surf, song):
        
        # run draw and update text to current ms
        self.draw(surf, text_surf)
        self.text = Text(str(int(self.cur_ms)), (self.rect.x, self.rect.y), DETAILS_FONT, 0.45, (255, 255, 255))
            
        # get mouse pos and set colour
        mpos = pygame.mouse.get_pos()
        self.hovering = self.rect.collidepoint(mpos)
        
        # if hovering, draw note image and set colour
        if self.hovering:
            self.colour = self.hover_col
            self.hover_note.draw(surf)
        else:
            # else set init colour
            self.colour = self.init_col
            
        for event in events:
        
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.hovering and song != None:
                        
                        # if you click, first check if you are not already hovering over a note in the chart editor
                        notes_hovering = []
                        for note in note_list:

                            if note != None:
                                if note.rect.collidepoint(mpos):
                                    notes_hovering.append(True)
                        
                        # if not, add note
                        if notes_hovering.count(True) <= 0:
                            self.add_note(note_list, receptors, spawn_pos_list, self.cur_ms - p_settings.getfloat('Gameplay', 'global offset'), 'note', '', song)
                    
                    # if no song loaded
                    elif song == None:
                        # put warning here
                        print('l + bozo')
                            
    def add_note(self, note_list, receptors, spawn_pos_list, ms, texture, type, song):
        print(f'added note at {self.cur_ms}ms')
        
        # add new note to chart based off of current ms value and recep id
        note_list.append(ChartNote(len(note_list), receptors, self.recep_id, spawn_pos_list[self.recep_id], ms - p_settings.getfloat('Gameplay', 'global offset'), 0, texture, 0.5, type, song))
        
    def remove_note(self, note_list, note):
        print(f'removed note at {self.cur_ms}ms')
        del note_list[f'note{note.id}']
        
## the ChartNote class is basically the same as the Note class but built to work in the chart editor. Refer to the comments on the Note class (they are basically the same).
#   selected (is the note being selected?)

class ChartNote():

    def __init__(self, ID, receptor_list, recep_id, pos, ms, hold_ms, texture, scale, type, song):
        # exactly the same as Note
        self.id = ID
        self.recep_id = recep_id
        self.ms = ms
        self.hold_ms = hold_ms
        self.beat = 0
        self.step = 0
        self.start_time = 0
        
        self.texture = texture
        
        self.image = pygame.image.load(os.path.join('assets', texture + '.png')).convert_alpha()
        self.image.fill(list(map(int, p_settings.get('Visual', 'note colour').split())), special_flags=pygame.BLEND_MULT)
        
        self.type = type
        self.rect = pygame.Rect(self.image.get_rect().x, self.image.get_rect().y, self.image.get_rect().w * scale, self.image.get_rect().h * scale)
        self.pos = pygame.math.Vector2()
        self.start_pos = pygame.math.Vector2()
        self.end_pos = pygame.math.Vector2()
        self.scale = scale
        self.alive = True
        self.root_alive = True
        
        # setup selected var
        self.selected = False
        self.receptor_list = receptor_list
        
        self.start_pos.xy = pos
        self.end_pos.xy = (centerX, centerY)
        self.pos = self.start_pos
        
        # same as Note
        self.hold_notes = []
        self.hold_ms_in_steps = int(self.hold_ms / (song.sec_per_step * 1000))
        print(f'Hold MS in steps: {self.hold_ms_in_steps}')
        if self.hold_ms_in_steps > 0:
            for x in range(0, self.hold_ms_in_steps + 1):
            
                if x == 0:
                    # hold root
                    self.hold_notes.append(ChartHoldNote(self, x, 'root', self.ms, receptor_list, recep_id, song))
                    
                elif x == self.hold_ms_in_steps:
                    # end of hold
                    self.hold_notes.append(ChartHoldNote(self, x, 'end', self.ms + (song.sec_per_step * 1000) * x, receptor_list, recep_id, song))
                    
                else:
                    # middle
                    self.hold_notes.append(ChartHoldNote(self, x, '', self.ms + (song.sec_per_step * 1000) * x, receptor_list, recep_id, song))
        
        self.beat_to_show = 0
        
        self.calc = None
        
        self.init_beat_step(song)
        
    def draw(self, surf):
        
        # draw stuff
        for hold in self.hold_notes:
            if hold.alive:
                hold.draw(surf)
        
        if self.root_alive:
            surf.blit(pygame.transform.smoothscale_by(self.image, self.scale), self.pos.xy)
    
    def update(self, song, cur_ms, note_list, events, hitsounds, surf):
        
        self.draw(surf)
        
        # get mouse pos
        mpos = pygame.mouse.get_pos()
        
        # is the root alive? set it based on calc
        self.root_alive = not self.run_kill(song, hitsounds)
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                # if left click and hovering, select note and change image
                if event.button == 1:
                    if self.rect.collidepoint(mpos) and self.root_alive:
                        self.selected = True
                        self.image.fill((0, 0, 0, 0))
                        self.image = pygame.image.load(os.path.join('assets', self.texture + '_selected' + '.png')).convert_alpha()
                        self.image.fill(list(map(int, p_settings.get('Visual', 'note colour').split())), special_flags=pygame.BLEND_MULT)
                        
                    elif not self.rect.collidepoint(mpos):
                        # deselect
                        self.selected = False
                        self.image = pygame.image.load(os.path.join('assets', self.texture + '.png')).convert_alpha()
                        self.image.fill(list(map(int, p_settings.get('Visual', 'note colour').split())), special_flags=pygame.BLEND_MULT)
                
                # if right click and hovering, delete note
                elif event.button == 3:
                    
                    if self.rect.collidepoint(mpos):
                        print(f'removed note at {self.ms}ms')
                        note_list.remove(self)
                        
            elif event.type == pygame.KEYDOWN:  
                if self.selected:
                    # if "q" key pressed, lower sustain amount of note by 1 step
                    if event.key == pygame.K_q:
                    
                        # if -1 hold length is not less than 0, remove it
                        if self.hold_ms_in_steps - 1 >= 0:
                            self.hold_ms_in_steps -= 1
                            self.hold_ms -= song.sec_per_step * 1000
                        
                        # re init note hold images
                        self.hold_notes = []
                        for x in range(0, self.hold_ms_in_steps + 1):
                        
                            if x == 0:
                                # hold root
                                self.hold_notes.append(ChartHoldNote(self, x, 'root', self.ms, self.receptor_list, self.recep_id, song))
                                
                            elif x == self.hold_ms_in_steps:
                                # end of hold
                                self.hold_notes.append(ChartHoldNote(self, x, 'end', self.ms + (song.sec_per_step * 1000) * x, self.receptor_list, self.recep_id, song))
                                
                            else:
                                # middle
                                self.hold_notes.append(ChartHoldNote(self, x, '', self.ms + (song.sec_per_step * 1000) * x, self.receptor_list, self.recep_id, song))
                                
                    elif event.key == pygame.K_e:
                        
                        # same as removing, but adding doesn't need a check
                        self.hold_ms_in_steps += 1
                        self.hold_ms += song.sec_per_step * 1000
                        
                        # re init note hold images
                        self.hold_notes = []
                        for x in range(0, self.hold_ms_in_steps + 1):
                        
                            if x == 0:
                                # hold root
                                self.hold_notes.append(ChartHoldNote(self, x, 'root', self.ms, self.receptor_list, self.recep_id, song))
                                
                            elif x == self.hold_ms_in_steps:
                                # end of hold
                                self.hold_notes.append(ChartHoldNote(self, x, 'end', self.ms + (song.sec_per_step * 1000) * x, self.receptor_list, self.recep_id, song))
                                
                            else:
                                # middle
                                self.hold_notes.append(ChartHoldNote(self, x, '', self.ms + (song.sec_per_step * 1000) * x, self.receptor_list, self.recep_id, song))
                       
        
        # update each hold piece
        for hold in self.hold_notes:
            hold.update(surf, song)
            
        for hold in self.hold_notes:
            hold.alive = not hold.run_kill(song)
        
        # run calc. if alive, lerp pos
        self.run_calc(song)
        if self.root_alive: 
            if 0 <= self.calc <= 1:
                self.pos = pygame.math.Vector2(self.start_pos + (self.end_pos - self.start_pos) * self.calc)
                self.rect.x = self.pos.x
                self.rect.y = self.pos.y
        
    def run_calc(self, song):
        self.beat_to_show = song.conductor.dt / song.sec_per_beat + song.beats_shown
        self.calc = (0.87 - (self.beat - song.conductor.dt / song.sec_per_beat) / song.beats_shown)
            
    def init_beat_step(self, song):
        self.beat = self.ms / song.sec_per_beat / 1000
        self.step = self.ms / song.sec_per_step / 1000
        
    # handles note missing
    def run_kill(self, song, hitsounds):
        
        # only blit note if it is moving (or should be alive)
        if self.calc != None:
            if self.calc > 0.88:
                    
                return True
                
            elif self.calc < 0.1:
                return True
                
            else:
                return False
                
        else:
            return False


## the ChartHoldNote class is the same as the HoldNote class, but changed in the same way that the ChartNote differs from the Note class. Built to work in editor.

class ChartHoldNote():
    
    def __init__(self, parent, id, type, ms, receptor_list, recep_id, song):
        
        # init hold image
        if type == 'root':
            # hold root
            self.image = Image('note_hold_root', parent.pos[0], parent.pos[1], 0.5)
            
        elif type == 'end':
            # end of hold
            self.image = Image('note_hold_end', parent.pos[0], parent.hold_notes[len(parent.hold_notes)-2].image.rect.y - 160, 0.5)
            
        else:
            # middle
            self.image = Image('note_hold', parent.pos[0], parent.pos[1] - 180 * id, 0.5)
        
        # set colour
        self.image.image.fill(list(map(int, p_settings.get('Visual', 'note colour').split())), special_flags=pygame.BLEND_MULT)
        
        # rotate the image, based on recep id (wacky in chart editor for some reason)
        recep = receptor_list.get(f'receptor{recep_id}')
        self.recep = recep
        angle = -recep.angle
        self.image.image = pygame.transform.rotate(self.image.image, angle + 135)
        
        # setup VARS
        self.alive = True
        self.ms = ms
        self.recep_id = recep_id
        
        self.calc = None
        
        self.init_beat_step(song)
        
        # parent note and hold ID (hold id is used to place images)
        self.parent = parent
        self.id = id
        
    def kill(self):
        self.alive = False
        
    # handles killing while playing song
    def run_kill(self, song):
        if self.calc > 0.87: 
            return True
            
        elif self.calc < 0.1:
            return False
                
        else:
            return False
        
    def draw(self, surf):
        self.image.draw(surf)
        
    def update(self, surf, song):
        
        # run calc. if alive, lerp
        self.run_calc(song)
        if self.calc != None:
            if self.alive:
                if 0 <= self.calc <= 1:
                    self.image.xpos = pygame.math.Vector2(self.parent.start_pos + (self.parent.end_pos - self.parent.start_pos) * self.calc)
                    self.image.ypos = pygame.math.Vector2(self.parent.start_pos + (self.parent.end_pos - self.parent.start_pos) * self.calc)
                
                # put hold out of frame if not supposed to be drawn
                else:
                    self.image.xpos = 1280
                    self.image.ypos = 720
            
    def run_calc(self, song):
        self.beat_to_show = song.conductor.dt / song.sec_per_beat + song.beats_shown
        self.calc = (0.87 - (self.beat - song.conductor.dt / song.sec_per_beat) / song.beats_shown)
            
    def init_beat_step(self, song):
        self.beat = self.ms / song.sec_per_beat / 1000
        self.step = self.ms / song.sec_per_step / 1000
        
        
# display data of currently selected note
def chart_note_data_display(note, surf):
    
    # setup text object for each variable of a note
    note_title = Text(f'Note {note.id}', (5, 200), DETAILS_FONT, 0.8, (250, 250, 250))
    recep_id = Text(f'Receptor: {note.recep_id}', (5, note_title.rect.y + 20), DETAILS_FONT, 0.8, (250, 250, 250))
    ms = Text(f'MS: {note.ms}', (5, recep_id.rect.y + 20), DETAILS_FONT, 0.8, (250, 250, 250))
    hold_ms = Text(f'Hold Length: {note.hold_ms}', (5, ms.rect.y + 20), DETAILS_FONT, 0.8, (250, 250, 250))
    tex_string = Text(f'Texture: {note.texture}', (5, hold_ms.rect.y + 20), DETAILS_FONT, 0.8, (250, 250, 250))
    
    # draw the text
    note_title.draw(surf)
    recep_id.draw(surf)
    ms.draw(surf)
    hold_ms.draw(surf)
    tex_string.draw(surf)

    
## save_json() function is used to, well, save chart json file 
def save_json(note_list, song_data):

    if len(note_list) > 0:
        # parse song data from the list of data
        song = song_data[0]
        chart_name = song_data[1]

        # sort the note list by millisecond value (to save it in order)
        note_list = sorted(note_list, key=lambda c_note: c_note.ms)

        # chart JSON format

        ## "note{}": [
        ##  ID,
        ##  recep_id,
        ##  ms,
        ##  hold_ms,
        ##  texture,
        ##  type
        ## ]

        # open json (if it exists. if it doesn't, python automatically creates that file)
        chart_json = open(f'songs/{song.name}/{chart_name}.json', 'w')

        # start writing the json stuff
        chart_json.write('''{''')
        chart_json.write(f'''
        "offset": {p_settings.getfloat('Gameplay', 'global offset')},''')

        # write note data for each note
        for x in range(0, len(note_list)-1):
            note = note_list[x]
            chart_json.write(f'''
        
        "note{x}": [
            {x},
            {note.recep_id},
            {note.ms + p_settings.getfloat('Gameplay', 'global offset')},
            {note.hold_ms},
            {'"' + note.texture + '"'},
            {'"' + str(note.type) + '"'}
        ],
        ''')

        # format the final note in the correct json formatting (remove ',' after last ']')
        chart_json.write(f'''
        
        "note{len(note_list)-1}": [
            {len(note_list)-1},
            {note_list[len(note_list)-1].recep_id},
            {note_list[len(note_list)-1].ms + p_settings.getfloat('Gameplay', 'global offset')},
            {note.hold_ms},
            {'"' + note_list[len(note_list)-1].texture + '"'},
            {'"' + note_list[len(note_list)-1].type + '"'}
        ]
        ''')

        chart_json.write('''
    }''')

        # save the json file!
        chart_json.close()
