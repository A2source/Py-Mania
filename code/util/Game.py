'''*************************************************************************
Name: Game
Date: Jan. 20, 2023
Course: Sun West DLC Computer Science 20
Program Description: This file contains all of the classes / functions that are related to gameplay. 
                     These include BG, Receptor, Note, HoldNote, Song, 
                     calc_note_data, play_intro, fps_display, song_data_display, and song_hit_data_display
********************************************************************'''

import os, configparser, operator, math
import pygame
from pygame.locals import *
from eyed3 import id3
from eyed3 import load
import psutil
import tween

from util.Util import is_dark, compare_from_range
from util.Classes import Text, Image, Timer

# pygame setup
pygame.font.init()

# setup the config parser. It loads the player_settings.ini file in '/config' and loads, as it says, settings.
p_settings = configparser.RawConfigParser()
p_settings.read_file(open('config/player_settings.ini'))

# create fonts
DETAILS_FONT = pygame.font.Font(os.path.join('fonts', 'metropolis.otf'), 20)
RATINGS_FONT = pygame.font.Font(os.path.join('fonts', 'bahnschrift.ttf'), 60)

# setting up the initial screen center values for placement of many objects
GAME_RECT = pygame.Rect(0, 0, 1280, 720)
centerX = GAME_RECT.centerx - 35
centerY = GAME_RECT.centery

# a list of note receptor positions on the screen
receptor_xy = [(centerX - 100, centerY - 100),
(centerX, centerY - 100),
(centerX + 100, centerY - 100),
(centerX + 100, centerY),
(centerX + 100, centerY + 100),
(centerX, centerY + 100),
(centerX - 100, centerY + 100),
(centerX - 100, centerY)]

# a list of the spawn positions of notes (off-screen)
note_spawn_pos = [tuple(map(operator.sub, receptor_xy[0], (600, 600))),
tuple(map(operator.sub, receptor_xy[1], (0, 650))),
tuple(map(operator.sub, receptor_xy[2], (-600, 600))),
tuple(map(operator.sub, receptor_xy[3], (-650, 0))),
tuple(map(operator.sub, receptor_xy[4], (-600, -600))),
tuple(map(operator.sub, receptor_xy[5], (0, -650))),
tuple(map(operator.sub, receptor_xy[6], (600, -600))),
tuple(map(operator.sub, receptor_xy[7], (650, 0)))]

## the BG class will be a gradient that is created upon game creation
# on second thought, it will be an image. Gradients are too process-heavy to draw in real time.
# the colour will be editable later (bg colour event)

class BG:
    def __init__(self, colour, texture):
        self.image = None
        self.image = pygame.image.load(os.path.join('assets', texture + '.png')).convert_alpha()
        
        # fill background with given colour
        self.image.fill(colour, special_flags=pygame.BLEND_MULT)
        
    def fill(self, colour, texture):
        self.image = pygame.image.load(os.path.join('assets', texture + '.png')).convert_alpha()
        self.image.fill(colour, special_flags=pygame.BLEND_MULT)
        
    def update(self, surf):
        surf.blit(self.image, (0, 0))


## the Receptor will be a class with a few different variables:
#   ID (the receptor ID, to target it for note creation and input detection
#   angle (or the angle that notes approach at)
#   scale (image size)
#   colour (the colour of the receptor)
#   texture (the sprite that should be loaded)
# this should allow for easy creation and editing later

class Receptor():
    
    def __init__(self, ID, angle, scale, texture):

        # load settings
        p_settings.read_file(open('config/player_settings.ini'))

        # create receptors
        self.id = ID
        self.angle = angle
        self.scale = scale
        self.texture_string = texture
        
        # default colour of debug text
        self.default_colour = (0, 0, 0)
            
        # check HSP of background colour. if it is dark and the player has auto-swap turned on, make the skin dark
        if is_dark(list(map(int, p_settings.get('Visual', 'bg colour').split()))):
            self.default_colour = (255, 255, 255)
        
        if p_settings.getboolean('Visual', 'auto-swap receptor skin'):
            if is_dark(list(map(int, p_settings.get('Visual', 'bg colour').split()))):
                self.texture_string += '_dark'
        else:
            # else if the player has the skin forced.
            if p_settings.getint('Visual', 'receptor skin') == 1:
                self.texture_string += '_dark'
        
        # load the image from the set string
        self.image = pygame.image.load(os.path.join('assets', self.texture_string + '.png')).convert_alpha()
        self.being_pressed = False
        
        self.rect = self.image.get_rect()
        
        # create timer for holding notes
        self.hold_timer = Text('0', (self.image.get_rect().center[0], self.image.get_rect().center[1] - 10), DETAILS_FONT, 0.6, self.default_colour)

    def set_texture(self, texture):
        self.image = pygame.image.load(os.path.join('assets', texture + '.png')).convert_alpha()
        
    def fill_blank(self):
        transparent = Color(0, 0, 0, 0)
        self.image.fill(transparent)
        
    def press(self, pressed):
        # set pressed texture
        self.being_pressed = pressed
        
        if self.being_pressed == True:
            self.set_texture(self.texture_string + '-hit')
        else:
            self.set_texture(self.texture_string)
            
    def draw(self, surf):
        self.hold_timer.draw(surf)
            
    def update(self, ID, hold_time, pos_list, surf):
        # draw receptor assets to the screen
        surf.blit(pygame.transform.smoothscale_by(self.image, self.scale), pos_list[ID])
        
        if p_settings.getboolean('Debug', 'super debug mode'):
            self.hold_timer = Text(f'{round(hold_time * 1000)}', (pos_list[ID]), DETAILS_FONT, 0.6, self.default_colour)
            self.draw(surf)
        
        
## the Note class will include all of the note variables to make them work correctly:
#   ID (the note's id. used for tracking when it appears in the song)
#   recep id (similar to Receptor.id, it makes sure that the notes appear in the correct lane)
#   ms (millisecond value, this is the time that the note is supposed to appear in the song)
#   hold length (the note hold length in ms)
#   colour (note colour)
#   texture (note texture)
#   type (allows for multiple note types, specifically for the curving notes, but you could add your own if you want to)
#                                                              ~~~~^^^^^~~~~ cut content WOAH!
#   song (the current song. Used for setting hold length ms values)
    
class Note():

    def __init__(self, ID, receptor_list, recep_id, ms, hold_ms, texture, type, song):

        # load settings
        p_settings.read_file(open('config/player_settings.ini'))
        
        # create note data
        self.id = ID
        self.recep_id = recep_id
        self.ms = ms
        self.hold_ms = hold_ms
        self.beat = 0
        self.step = 0
        self.start_time = 0
        
        # get image from texture string and fill with colour from player_settings
        self.image = pygame.image.load(os.path.join('assets', texture + '.png')).convert_alpha()
        self.image.fill(list(map(int, p_settings.get('Visual', 'note colour').split())), special_flags=pygame.BLEND_MULT)
        
        # setup more variables (alive, hold notes, positions)
        self.type = type
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2()
        self.start_pos = pygame.math.Vector2()
        self.end_pos = pygame.math.Vector2()
        self.scale = 1
        self.alive = True
        self.root_alive = True
        self.holding = False
        self.actually_hit = False
        self.hold_notes = []
        
        self.start_pos.xy = (note_spawn_pos[self.recep_id])
        self.end_pos.xy = (centerX, centerY)
        self.pos = self.start_pos
        
        # setup the holding sprites of the note
        # if the length is > 0, setup root, middle, and end hold sprites
        self.hold_images = []
        hold_ms_in_steps = int(self.hold_ms / (song.sec_per_step * 1000))
        if hold_ms_in_steps > 0:
            for x in range(0, hold_ms_in_steps + 1):
            
                if x == 0:
                    # hold root
                    self.hold_notes.append(HoldNote(self, x, 'root', self.ms, receptor_list, recep_id, song))
                    
                elif x == hold_ms_in_steps:
                    # end of hold
                    self.hold_notes.append(HoldNote(self, x, 'end', self.ms + (song.sec_per_step * 1000) * x, receptor_list, recep_id, song))
                    
                else:
                    # middle
                    self.hold_notes.append(HoldNote(self, x, '', self.ms + (song.sec_per_step * 1000) * x, receptor_list, recep_id, song))
        
        self.beat_to_show = 0
        
        self.calc = None
        
        # setup the note's beat and step variables using the song sec_per_beat and step data
        self.init_beat_step(song)
    
    def update_colour(self):
        self.image.fill(list(map(int, p_settings.get('Visual', 'note colour').split())), special_flags=pygame.BLEND_MULT)
        
    def draw(self, surf):
        # draw notes
        for hold in self.hold_notes:
            if hold.alive:
                hold.draw(surf)
        
        if self.root_alive:
            surf.blit(pygame.transform.smoothscale_by(self.image, self.scale), self.pos.xy)
            
    def update(self, song, surf):
        
        # check status of holds
        if self.hold_ms <= 0:
            self.alive = self.root_alive
        
        for hold in self.hold_notes:
            hold.update(surf, song)
            
        if self.holding and self.actually_hit:
            for hold in self.hold_notes:
                hold.run_kill(song)
        
        # if note is alive, run the calculation to interpolate it's position.
        if self.alive:
            self.draw(surf)
            self.run_calc(song)
            if self.calc >= 0 and self.calc <= 1:
                self.pos = pygame.math.Vector2(self.start_pos + (self.end_pos - self.start_pos) * self.calc)
        
    def run_calc(self, song):
        # interpolate note position
        self.beat_to_show = song.conductor.dt / song.sec_per_beat + song.beats_shown
        self.calc = (0.87 - (self.beat - song.conductor.dt / song.sec_per_beat) / song.beats_shown)
            
    def init_beat_step(self, song):
        self.beat = self.ms / song.sec_per_beat / 1000
        self.step = self.ms / song.sec_per_step / 1000
        
    def kill(self):
        self.alive = False
            
    def kill_root(self):
        self.root_alive = False
        
    # handles note missing
    def run_kill(self, song):
        if self.root_alive:
            if self.calc > 1:
                self.kill_root() 
                return True
                
        else:
            return False


## the HoldNote class is used to add sustaining data and gameplay for notes
#   parent (the parent note. use position and ms data from it)
#   type (root, middle, or end sprite?)
#   ms (millisecond placement of hold note piece)
#   receptor_list (the list of receptors. used to get the angle of the receptor and rotate the sprites)
#   recep_id (the parent_note's receptor ID. used to get angle.)
#   song (the current song, again, for ms data)

class HoldNote():
    
    def __init__(self, parent, id, type, ms, receptor_list, recep_id, song):

        # setup images
        if type == 'root':
            # hold root
            self.image = Image('note_hold_root', parent.pos[0], parent.pos[1], 1)
            
        elif type == 'end':
            # end of hold
            self.image = Image('note_hold_end', parent.pos[0], parent.hold_notes[len(parent.hold_notes)-2].image.rect.y - 160, 1)
            
        else:
            # middle
            self.image = Image('note_hold', parent.pos[0], parent.pos[1] - 180 * id, 1)
        
        # fill from player_settings
        self.image.image.fill(list(map(int, p_settings.get('Visual', 'note colour').split())), special_flags=pygame.BLEND_MULT)
        
        # rotate hold images
        recep = receptor_list.get(f'receptor{recep_id}')
        self.recep = recep
        self.image.image = pygame.transform.rotate(self.image.image, recep.angle)
        
        # setup more variables
        self.alive = True
        self.ms = ms
        self.recep_id = recep_id
        
        self.calc = None
        
        self.init_beat_step(song)
        
        self.parent = parent
        
    def kill(self):
        self.alive = False
        
    # handles killing while holding
    def run_kill(self, song):
        if self.alive:
            # if calculation hits a good looking point
            if self.calc > 0.87:
                self.kill() 
                return True
                
        else:
            return False
        
    def draw(self, surf):
        self.image.draw(surf)
        
    def update(self, surf, song):
        
        # if alive, run calc to interpolate position
        if self.alive:
            self.run_calc(song)
            if self.calc != None:
                if self.calc >= 0 and self.calc <= 1:
                    if self.recep.angle == 45 or self.recep.angle == -45 or self.recep.angle == -135 or self.recep.angle == -225:
                        self.image.xpos = pygame.math.Vector2(self.parent.start_pos + (self.parent.end_pos - self.parent.start_pos) * self.calc) + pygame.math.Vector2(-15, -15)
                        self.image.ypos = pygame.math.Vector2(self.parent.start_pos + (self.parent.end_pos - self.parent.start_pos) * self.calc) + pygame.math.Vector2(-15, -15)
                    
                    else:
                        self.image.xpos = pygame.math.Vector2(self.parent.start_pos + (self.parent.end_pos - self.parent.start_pos) * self.calc)
                        self.image.ypos = pygame.math.Vector2(self.parent.start_pos + (self.parent.end_pos - self.parent.start_pos) * self.calc)
                        
                else:
                    
                    # make sure that you can't see long hold notes while they are not being moved
                    self.image.xpos = 1280
                    self.image.ypos = 720
            
    def run_calc(self, song):
        # run calc
        self.beat_to_show = song.conductor.dt / song.sec_per_beat + song.beats_shown
        self.calc = (0.87 - (self.beat - song.conductor.dt / song.sec_per_beat) / song.beats_shown)
            
    def init_beat_step(self, song):
        self.beat = self.ms / song.sec_per_beat / 1000
        self.step = self.ms / song.sec_per_step / 1000
        
        
## the Song class will be used to handle all of the music playing and tracking related aspects of the project
#   path (the song path to load)
#   tag (the id3 tag of the song)
#   info (the tag data)
#   current track (the current track)
#   bpm (beats per minute of the song)
#   length (length of the song in seconds)
#   song position (current ms position in the song)
#   second per beat (how many seconds it takes for a beat to occur. used for note timings)
#   second per step (how many seconds it takes for a step to occur. a step occurs 4x in a beat. used for note timings)
#   song position in beats (current song position, but in beats. used for note timings)

# I will be using ideas from https://shinerightstudio.com/posts/music-syncing-in-rhythm-games/ to make the timing line up correctly

class Song():
    
    def __init__(self, song, path_mode=False):
    
        # setup variables
        if path_mode:
            self.path = song
        else:
            self.path = 'songs/' + song + '/' + song + '.mp3'
        self.name = song
        self.tag = id3.Tag()
        self.tag.parse(os.path.join(self.path))
        self.info = load(os.path.join(self.path))
        
        # load music and init
        pygame.mixer.music.load(self.path)
        pygame.mixer.music.set_volume(0.25)
        self.playing = False
        
        # create variables for each important data value of the song
        self.bpm = self.tag.bpm
        self.length = int(self.info.info.time_secs)
        self.artist = self.tag.artist
        
        # pausing time, for various places
        self.pause_time = 0
        
        #print so I know
        print('')
        print('## SONG DETAILS ##')
        print('Path:', self.path)
        print('Current Song:', song)
        print('Artist:', self.artist)
        print('BPM:', self.bpm)
        print('Length:', self.length, '(seconds)')
        print('')
        
        # create value for tracking note placement
        self.sec_per_beat = 60 / self.bpm
        self.sec_per_step = 60 / self.bpm / 4
        self.conductor = Timer(0)
        self.pos_in_beats = 0
        self.pos_in_steps = 0
        
        # for gameplay. test if a song is done, and run end accordingle
        self.finished = False
        
        # setup for intro
        self.intro_playing = True
        
        # this is essentially scroll speed
        self.beats_shown = p_settings.getfloat('Gameplay', 'Scroll Speed')
        
    def start(self, ref):
        
        # pause song
        if self.conductor.dt > 0 and not self.intro_playing:
            self.conductor.pause(False)
            
        else:
            # resume song
            self.conductor.start(ref)
            print(self.conductor.dt)
        
        self.playing = True
        
        if ref >= 0:
            # if music paused or starting from 0
            pygame.mixer.music.play(0, self.pause_time)
            
        else:
            # else, the intro is playing and set accordingly
            self.intro_playing = True
        
    def update(self, use_offset=True, grid=None):
        
        # check song finished
        if math.floor(self.conductor.dt) == self.length:
            self.finished = True
        
        # if song is playing, count current pos and calc current place
        if self.playing:
            self.conductor.count(use_offset, grid)
            self.pos_in_beats = math.floor(self.conductor.dt / self.sec_per_beat)
            self.pos_in_steps = math.floor(self.conductor.dt / self.sec_per_step)
        
        # if intro is playing, calc when intro is done.
        if self.intro_playing:
            if self.pos_in_beats == 0:
                self.intro_playing = False
                self.start(0)
            
    def update_paused(self):
        # for chart editor, update variables without needing to play song
        self.pos_in_beats = int(self.pause_time / self.sec_per_beat)
        self.pos_in_steps = int(self.pause_time / self.sec_per_step)
        
    def pause(self, pause):
        # set paused
        self.playing = pause
        
        if not pause:
            # if the song is being paused, set pause time to resume from later
            self.conductor.reset()

            # set pause time
            self.pause_time = self.conductor.dt
            print('Paused at {:.2f} ms'.format(self.pause_time * 1000))

            # stop music
            pygame.mixer.music.stop()
            
        else:
            # unpause song from saved pause time
            print('Resuming at {:.2f} ms!'.format(self.pause_time * 1000))
            pygame.mixer.music.play(0, self.pause_time)
            self.conductor.start(self.pause_time)


## calc_note_data handles displaying the ranking of the current note that you just hit.
# it will show your offset ms, and then find what that rank is by comparing it to the database

def calc_note_data(hit_ms, acc_database, note_list, rank_text):
    
    # if the rank text is given, make it alive
    if rank_text != None:
        rank_text.alive = True
    
    # setup colour variables
    rank_colours = [(0, 255, 0), (255, 69, 0), (255, 0, 0), (139, 0, 0), (139, 0, 0)]
    rank_colours_light = [(214, 255, 214), (255, 167, 135), (255, 170, 170), (139, 0, 0)]
    col_to_use = None
    
    ## the ranks are calculated based off of your accuracy in specific millisecond ranges. The ranges are listed below.
    ## the function compares your ms accuracy to the accuracy ranges, and sets the rank accordingly.
    
    # perfect = 50
    # great = 100
    # good = 116.67
    # bad = 133.33
    ranks = [50, 100, 116.67, 133.3]
    
    # iterate through possible ranks to give based on ms accuracy
    i = 0
    if hit_ms != None:
        for x in ranks:
            
            # compare the user's ms accuracy to the list of possible ranks (using compare from range)
            rank = compare_from_range(0, abs(hit_ms), x)
            
            # set the actual rank
            if rank:
                break
            
            # iterate through to next rank (if next rank is not "miss", that is handeled outside)
            if i + 1 != 4:
                i += 1
    else:
        # if else, you missed (skill issue + l + fell off)
        i = 4
    
    # setup rank text with correct colour
    print('Rank:', i)
    if i <= len(ranks)-1:
        
        # add the hit rank to the list of current rank values
        acc_database[i] += 1
        
        col_to_use = rank_colours_light[i]
        display_ms = Text('{} ms.'.format(str(hit_ms)), (centerX + 35, centerY + 55), DETAILS_FONT, 1, col_to_use, 'center', True)
    
    # if you missed, don't display ms text
    if hit_ms == None:
        display_ms = Text('', (centerX + 35, centerY + 45), DETAILS_FONT, 1, (0, 0, 0), 'center', True)
        
    # now it's time to copy osu's ranking formula and calc the average accuracy! thanks ppy!
    # https://osu.ppy.sh/wiki/en/Gameplay/Accuracy#osu!mania
    
    n = len(note_list)
    a = acc_database
    accuracy = (300 * (n + a[0]) + 200 * (a[1]) + 100 * (a[2]) + 50 * (a[3])) / (300 * (n + a[0] + a[1] + a[2] + a[3] + a[4]))
    
    # setup the rank image
    rating_strings = ['Perfect!', 'Great!', 'Good!', 'Bad', 'Miss']
    display_txt = Text(rating_strings[i], (centerX + 65, centerY + 35), RATINGS_FONT, 0.2, rank_colours[i], 'center', True)
    
    # if show ms is false, don't display it
    if not p_settings.getboolean('Visual', 'show ms'):
        display_ms = None
    
    # return all
    return display_ms, accuracy, display_txt
    

## play_intro(), used to play gameplay intro
def play_intro(assets, the_tween, starting, surf):
    
    # if in starting mode, tween assets in
    if starting:
        for x in range(0, len(assets)):
            
            if x == 0:
                the_tween = tween.to(assets[x], 'xpos', surf.get_rect().center[0] - 470, 1.8, 'easeOutExpo')
            else:
                the_tween = tween.to(assets[x].rect, 'centerx', surf.get_rect().center[0] - 20, 1.8, 'easeOutExpo')
        
    else:
        
        # tween assets out!
        for x in range(0, len(assets)):
        
            if x == 0:
                tween.to(assets[x], 'xpos', -1000, 2, 'easeInExpo')
            else:
                tween.to(assets[x].rect, 'centerx', -1000, 2, 'easeInExpo')


## fps_display will display the current FPS and RAM usage
#   I will use time.get_fps() to display the current FPS
#   I will use a library called "psutil" to display RAM usage
#   colours will change depending on current FPS and RAM

def fps_display(surf, clock):
    
    # get fps and ram usage from psutil
    current_fps = clock.get_fps()
    current_ram = psutil.virtual_memory()[3]/1000000000
    
    # setup fps text
    if current_fps > 30:
        # green text
        fps_state = (0, 255, 0)
        
    elif current_fps < 30 and current_fps > 15:
        # orange text
        fps_state = (255, 69, 0)
        
    elif current_fps < 15:
        # red text
        fps_state = (255, 0, 0)
    
    # create text objects
    fps_text = Text(str(int(current_fps)) + ' FPS', (1275, 5), DETAILS_FONT, 1, (fps_state), 'topright', True)
    mem_text = Text(str(int(current_ram)) + ' GB', (1280, fps_text.rect.y + 24), DETAILS_FONT, 0.9, (250, 250, 250), 'topright', True)
        
    # draw text
    fps_text.draw(surf)
    mem_text.draw(surf)
    

## song_data_display will display current step and beat
# for all intents and purposes, exactly the same as fps_display. just using it for debugging (and to look cool heh)

def song_data_display(song, acc_database, accuracy, mode, surf):

    # read settings
    p_settings.read_file(open('config/player_settings.ini'))

    # this is for chart mode. if given song is none, display 0
    if song == None:
        cur_beat = 0
        cur_step = 0
        cur_ms = 0

    else:
        # setup display variables
        cur_beat = song.pos_in_beats
        cur_step = song.pos_in_steps
        cur_ms = song.conductor.dt * 1000
    
    # if game mode, put it in top left of screen
    if mode == 'game':
        beat_text = Text(str(int(cur_beat)), (5, 5), DETAILS_FONT, 1, (250, 250, 250), 'topleft', True)
        step_text = Text(str(int(cur_step)), (5, beat_text.rect.y + 24), DETAILS_FONT, 0.9, (250, 250, 250), 'topleft', True)
        ms_text = Text(str(int(cur_ms)), (5, step_text.rect.y + 24), DETAILS_FONT, 0.8, (250, 250, 250), 'topleft', True)
        
    elif mode == 'chart':
        # else if chart mode, go in top right
        beat_text = Text(str(int(cur_beat)), (surf.get_rect().topright[0] - 4, 5), DETAILS_FONT, 1, (250, 250, 250), 'topright', True)
        step_text = Text(str(int(cur_step)), (surf.get_rect().topright[0] - 1, beat_text.rect.y + 24), DETAILS_FONT, 0.9, (250, 250, 250), 'topright', True)
        ms_text = Text(str(int(cur_ms)), (surf.get_rect().topright[0] + 5, step_text.rect.y + 24), DETAILS_FONT, 0.8, (250, 250, 250), 'topright', True)
    
    # display accuracy if not in chart mode
    if mode != 'chart':
        acc_text = Text('{:.2f}%'.format(accuracy * 100), (1270, 100), DETAILS_FONT, 1, (250, 250, 250), 'midright', True)
    
    # if debug mode or chart mode, draw text
    if p_settings.getboolean('Debug', 'debug mode') or mode == 'chart':
        beat_text.draw(surf)
        step_text.draw(surf)
        ms_text.draw(surf)
    
    # if extra info is on and not in chart, show display of each type of note hit
    if p_settings.getboolean('Visual', 'extra info') and mode != 'chart':
        song_hit_data_display(acc_database, surf)
    
    # if not chart mode, draw accuracy
    if mode != 'chart':
        acc_text.draw(surf)


## song_hit_data_display() shows how many of each note rating you have hit (perfect, good, bad, etc.)
def song_hit_data_display(acc_database, surf):

    # make text objects, using the accuracy database values as reference
    perf_text = Text('Perfects: ' + str(acc_database[0]), (1285, centerY - 50), DETAILS_FONT, 0.8, (250, 250, 250), 'midright', True)
    great_text = Text('Greats: ' + str(acc_database[1]), (1285, centerY - 25), DETAILS_FONT, 0.8, (250, 250, 250), 'midright', True)
    good_text = Text('Goods: ' + str(acc_database[2]), (1285, centerY), DETAILS_FONT, 0.8, (250, 250, 250), 'midright', True)
    bad_text = Text('Bads: ' + str(acc_database[3]), (1285, centerY + 25), DETAILS_FONT, 0.8, (250, 250, 250), 'midright', True)
    miss_text = Text('Misses: ' + str(acc_database[4]), (1285, centerY + 50), DETAILS_FONT, 0.8, (250, 250, 250), 'midright', True)
    
    # draw text
    perf_text.draw(surf)
    great_text.draw(surf)
    good_text.draw(surf)
    bad_text.draw(surf)
    miss_text.draw(surf)