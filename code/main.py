'''*************************************************************************
Name: main
Date: Jan. 20, 2023
Course: Sun West DLC Computer Science 20
Program Description: This part of the program controls all of the "main" functions (the main scenes of the game). 
                     Intro, Title Screen, Lists, Options, Freeplay, and Chart Editor are controlled here.
********************************************************************'''

# very first in the program is to import everything that we need
import os, math, operator, random, time, json, configparser, webbrowser
import pygame
import tween

from util.Classes import Timer, Image, Text, Button, TextInput, Transition
from util.Game import BG, Receptor, Note, HoldNote, Song
from util.Game import calc_note_data, play_intro, fps_display, song_data_display, song_hit_data_display
from util.Util import is_dark, compare_from_range, exit
from util.Option import Option
from util.Chart import ChartGrid, ChartNote, ChartHoldNote
from util.Chart import save_json, chart_note_data_display
from util.Freeplay import FreeplaySong
from util.List import SongList

# pygame setup
pygame.init()
pygame.font.init()

# setup the config parser. It loads the player_settings.ini file in '/config' and loads, as it says, settings.
p_settings = configparser.RawConfigParser()
p_settings.read_file(open('config/player_settings.ini'))

# center window on the screen
os.environ['SDL_VIDEO_CENTERED'] = '1'

# setup the display to blit everything to
DISPLAYSURF = pygame.display.set_mode((1280, 720), pygame.SRCALPHA | pygame.SCALED, 32)

# set app display name
display_string = 'Py-Mania' # made this a variable, for easy editing later
pygame.display.set_caption(display_string)
pygame.display.set_icon(pygame.image.load(os.path.join('assets/icon.png')).convert_alpha())

# create fonts
DETAILS_FONT = pygame.font.Font(os.path.join('fonts', 'metropolis.otf'), 20)
DETAILS_FONT_MEDIUM = pygame.font.Font(os.path.join('fonts', 'metropolis.otf'), 35)
DETAILS_FONT_BIG = pygame.font.Font(os.path.join('fonts', 'metropolis.otf'), 60)
RATINGS_FONT = pygame.font.Font(os.path.join('fonts', 'bahnschrift.ttf'), 60)
    
# grab the bg colour from player_settings
bg_colour = list(map(int, p_settings.get('Visual', 'bg colour').split()))

# for future use (modding)
# which texture for the background to load
bg_string = 'bg-grey'

# receptor screen values
# setting up the initial screen center values for placement of many objects
GAME_RECT = pygame.Rect(0, 0, 1280, 720)
centerX = GAME_RECT.centerx - 35
centerY = GAME_RECT.centery

# receptor value variables
# setup the dictionary of note receptors
receptors = {}

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

# just in case anyone adds custom keycounts per song or something (I won't change it, but it is here for the future)
# key_count variable that is used to set up many things related to the receptors (setting up, adding notes)
key_count = 8

# the first thing that needs to be done is to set up the background
# use bg_colour and bg_string from before
background = BG(bg_colour, bg_string)

# not used for much, just here to track global time. Mostly for FPS, but not for song millisecond tracking.
global_clock = pygame.time.Clock()

# main function that controls which state happens. This is the different parts of the game (playing, in the menu, etc)
# it also allows the transitions to happen correctly
def main(mode, transition):
    
    # activate correct scene. Pass transition through into the new scene.
    
    if mode == 'intro':
        intro_main()
    
    elif mode == 'title':
        title_main(transition)
        
    elif mode == 'freeplay':
        freeplay_main(transition)
        
    elif mode == 'chart':
        chart_main(None, None, transition)
        
    elif mode == 'options':
        options_main(transition)
        
    elif mode == 'list':
        list_main(transition)
        
## intro_main() runs a small introduction to the game including the pygame logo and my name. Then, the game starts!
def intro_main():

    # setup timer
    intro_timer = Timer(0)
    
    # create logo image
    intro_logo = Image('pygame', 0, 0, 0.3)
    intro_logo.ypos = 250
    intro_logo.xpos = 400
    
    # create intro text
    intro_text = Text('[A2] Presents', (0, 0), DETAILS_FONT_BIG, 1, (255, 255, 255), 'center')
    intro_text.rect.center = DISPLAYSURF.get_rect().center
    
    # begin timer
    intro_timer.start(0)
    
    # get fps from config
    fps = p_settings.getint('Gameplay', 'fps limit')

    intro_sound = True
    
    ## loop
    while (1):
        
        # reset bg
        DISPLAYSURF.fill(0)
        
        # increment timer
        intro_timer.count()
        
        # check events
        event_list = pygame.event.get()
        for event in event_list:
            # quit game
            if event.type == pygame.QUIT:
                exit()
                
            elif event.type == pygame.KEYDOWN:  
            
                # if enter is hit, skip intro
                if event.key == pygame.K_RETURN:
                    main('title', None)
        
        # play intro sound
        if round(intro_timer.dt, 2) == 0.42 and intro_sound:
            print('bro')
            intro_sound = False
            pygame.mixer.Sound('sounds/intro.wav').play()
        
        # draw logo at correct time
        if intro_timer.dt > 0.4 and  intro_timer.dt < 1.7:
            intro_logo.draw(DISPLAYSURF)
            
        # draw text at correct time  
        elif intro_timer.dt > 3 and intro_timer.dt < 4.9:
            intro_text.draw(DISPLAYSURF)
        
        # stop intro
        elif round(intro_timer.dt, 1) == 6.2:
            main('title', None)
        
        # fade out assets
        if intro_timer.dt > 1.5:
            intro_logo.image.fill((225, 225, 225), special_flags=pygame.BLEND_MULT)
            
        if intro_timer.dt > 4.6:
            intro_text.image.fill((225, 225, 225), special_flags=pygame.BLEND_MULT)
        
        # update display
        pygame.display.update()

## the list_main() function which controls the list menu
def list_main(transition):
    
    # setup the config parser. It loads the player_settings.ini file in '/config' and loads, as it says, settings.
    p_settings = configparser.RawConfigParser()
    p_settings.read_file(open('config/player_settings.ini'))

    # setup transition
    started_from_here = False
    can_interact = False
    loading_list = False
    
    # init background (update currently read settings too)
    p_settings.read_file(open('config/player_settings.ini'))
    background = BG(list(map(int, p_settings.get('Visual', 'bg colour').split())), bg_string)
    
    # setup list database
    list_list = []
    list_paths = []
    
    # for each text file in the '/list' folder, add it to the list of lists to load
    print()
    for list_file in os.listdir('lists'):
        if f'lists/{list_file}'.endswith('.txt'):
            list_list.append(list_file)
            list_paths.append(f'lists/{list_file}')
            print(f'.txt detected! x{len(list_list)}')
    
    print()
    print(list_list)
    
    # lists are formatted like this:
    
    # "#" symbols are the delimitors
    
    # #
    # (List title goes here)
    #
    # #
    # (List description goes here)
    #
    # #
    # (Song 1), (Chart .json name)
    # (Song 2), (Chart .json name)
    #
    # ^ this can go on forever (the 32-bit integer limit)
    
    formatted_lists = []
    
    # for each text file detected, format it into a "list data" list to be sent into the SongList class
    for file in list_list:
        open_file = open(f'lists/{file}', 'r')
        read_file = open_file.read()
        read_file = read_file.split('#')
        
        formatted = []
        
        for x in range(0, len(read_file)):
            read_file[x] = read_file[x].replace(r'\n', '')
            formatted.append(read_file[x])
        
        # remove empty string at the beginning
        formatted.pop(0)
        formatted_lists.append(formatted)

    print(formatted_lists)
    
    lists_to_load = []
    
    # create SongList objects using the now formatted lists
    for x in range(0, len(formatted_lists)):
        lists_to_load.append(SongList(formatted_lists[x], list_paths[x], DISPLAYSURF.get_rect().center[0] - 400, 50 + 120 * x))
        
    # setup last list, for clamping
    last_list = lists_to_load[len(lists_to_load)-1]
    
    # get fps from config
    fps = p_settings.getint('Gameplay', 'fps limit')
    
    # set window name
    display_string = f'Py-Mania - In The Menus'
    
    # setup variable for scroll checking
    ev_y = 0
    is_open = []
    
    ## loop
    while (1):
        
        # fps limit
        global_clock.tick_busy_loop(fps)
        
        # reset screen
        DISPLAYSURF.fill(0)
        
        event_list = pygame.event.get()
        for event in event_list:
            # if program "x" is hit
            if event.type == pygame.QUIT:
                exit()
                
            elif event.type == pygame.KEYDOWN:  
                if event.key == pygame.K_ESCAPE:
                    # start transition back to title
                    if not transition.transitioning:
                        transition.reset()
                        transition.start()
                        started_from_here = True
                        
            elif event.type == pygame.MOUSEWHEEL:
                
                ev_y = event.y * 30
                
                # clamp list positions
                if lists_to_load[0].rect.y + ev_y <= 35 and last_list.rect.midbottom[1] + ev_y >= 600:
                
                    # when mousewheel is used, add / subtract y value of each list and its assets
                    for song_list in lists_to_load:
                        song_list.rect.y += ev_y
                        song_list.title_text.rect.y += ev_y
                        
                        for string in song_list.desc_text:
                            string.rect.y += ev_y
                            
                        for song_chart_combos in song_list.song_chart_texts:
                            song_chart_combos.rect.y += ev_y
                            
                        song_list.play_button.rect.y += ev_y
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
            
                # if hovering over the list's play button and left mouse is clicked, load list in gameplay_main()
                if event.button == 1:
                    for x in range(0, len(lists_to_load)):
                        song_list = lists_to_load[x]
                        
                        # if list is playable
                        if song_list.play_button.hovering and song_list.play_button.text != 'No Songs' and song_list.play_button.text != 'Invalid Song(s)':
                            transition.reset()
                            transition.start()
                            started_from_here = True
                            loading_list = True
                            list_to_load = song_list.songs_to_load
                            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                
                    # reset list positions if a list is open and outside of the scroll threshold, and then you close it
                    # took me a while to get to this conclusion!
                    if not lists_to_load[0].rect.y + ev_y <= 35 or not last_list.rect.midbottom[1] + ev_y >= 600:
                        for x in range(0, len(lists_to_load)):
                            
                            # set first list to init pos
                            song_list = lists_to_load[0]         
                            song_list.rect.y = 35
                            song_list.title_text.rect.y = song_list.rect.topleft[1] + 35
                            
                            for y in range(0, len(song_list.desc_text)):
                                string = song_list.desc_text[y]
                                string.rect.y = song_list.title_text.rect.bottomleft[1] - 10+ y * 40
                                
                            for y in range(0, len(song_list.song_chart_texts)):
                                song_chart_combos = song_list.song_chart_texts[y]
                                song_chart_combos.rect.y = song_list.desc_text[len(song_list.desc_text)-1].rect.bottomleft[1] + 20 + y * 40
                                
                            song_list.play_button.rect.y = song_list.song_chart_texts[len(song_list.song_chart_texts)-1].rect.bottomleft[1] + 20
                            
                            # change every other list's position back
                            if x + 1 < len(lists_to_load):
                                next_list = lists_to_load[x + 1]
                                next_list.rect.y = song_list.rect.bottomleft[1] + 10
                                next_list.title_text.rect.y = song_list.rect.bottomleft[1] + 35
                                
                                for y in range(0, len(next_list.desc_text)):
                                    string = next_list.desc_text[y]
                                    string.rect.y = song_list.rect.bottomleft[1] + 70 + y * 40
                                        
                                for y in range(0, len(next_list.song_chart_texts)):
                                    song_chart_combo = next_list.song_chart_texts[y]
                                    song_chart_combo.rect.y = next_list.desc_text[len(next_list.desc_text)-1].rect.bottomleft[1] + 20 + y * 40
                                
                                if len(next_list.song_chart_texts) > 0:
                                    next_list.play_button.rect.y = next_list.song_chart_texts[len(next_list.song_chart_texts)-1].rect.bottomleft[1] + 20
        
        # blit background
        background.update(DISPLAYSURF)
        
        # update lists
        for x in range(0, len(lists_to_load)):
            song_list = lists_to_load[x]
            song_list.update(event_list, DISPLAYSURF)
            
            # set position of all of the assets, regardless of where it has been scrolled to
            if x + 1 < len(lists_to_load):
                next_list = lists_to_load[x + 1]
                next_list.rect.y = song_list.rect.bottomleft[1] + 10
                next_list.title_text.rect.y = song_list.rect.bottomleft[1] + 35
                
                for y in range(0, len(next_list.desc_text)):
                    string = next_list.desc_text[y]
                    string.rect.y = song_list.rect.bottomleft[1] + 70 + y * 40
                        
                for y in range(0, len(next_list.song_chart_texts)):
                    song_chart_combo = next_list.song_chart_texts[y]
                    song_chart_combo.rect.y = next_list.desc_text[len(next_list.desc_text)-1].rect.bottomleft[1] + 20 + y * 40
                
                if len(next_list.song_chart_texts) > 0:
                    next_list.play_button.rect.y = next_list.song_chart_texts[len(next_list.song_chart_texts)-1].rect.bottomleft[1] + 20
                    
        
        # if transition is occuring, update tweens and transitions (also deny interactions with any list)
        if transition.transitioning:
            can_interact = False
            transition.update(DISPLAYSURF)
            transition.image.draw(DISPLAYSURF)
            tween.update(global_clock.get_time() / 1500)
            
        else:
            # reactivate interaction
            can_interact = True
        
        # if you hit escape, go back to title
        if transition.halfway and started_from_here and not loading_list:
            main('title', transition)
        
        # else if you are loading a list, run gameplay_main() with the list parameters put in
        elif transition.halfway and started_from_here and loading_list:
            gameplay_main(None, None, list_to_load, -1, False, 'list', transition)
        
        # update app display
        pygame.display.update()
        
        # update window name
        pygame.display.set_caption(display_string)

## freeplay_main() func, used to select a song out of the list of songs to play
def freeplay_main(transition):
    
    # setup the config parser. It loads the player_settings.ini file in '/config' and loads, as it says, settings.
    p_settings = configparser.RawConfigParser()
    p_settings.read_file(open('config/player_settings.ini'))
    
    # setup transition
    started_from_here = False
    can_interact = True
    
    # init background (update currently read settings too)
    p_settings.read_file(open('config/player_settings.ini'))
    background = BG(list(map(int, p_settings.get('Visual', 'bg colour').split())), bg_string)
    
    # setup song database
    song_list = []
    
    print()
    
    # load every song in the 'songs' directory into the song list to be converted into "FreeplaySong"s
    for song_name in os.listdir('songs'):
        for file in os.listdir(f'songs/{song_name}'):
            if f'songs/{song_name}/{file}'.endswith('.json'):
                song_box = FreeplaySong(song_name, file, 5 + 6 * len(song_list), 50 + 180 * len(song_list), DETAILS_FONT_MEDIUM, 1, (0, 0, 0), 'freeplay_box', 0.8)
                song_list.append(song_box)
                print(f'goofy ah json detected! x{len(song_list)}')
    
    # setup last song as a variable (for screen clamping)
    last_song = song_list[len(song_list)-1]
    
    print()
    for song in song_list:
        print(song.chart_name)
        
    # setup loading stuff
    song_to_load = None
    chart_to_load = None
    loading_song = False
    
    # get fps from config
    fps = p_settings.getint('Gameplay', 'fps limit')
    
    # set window name
    display_string = f'Py-Mania - In The Menus'
    
    ## loop
    while (1):
        
        # fps limit
        global_clock.tick_busy_loop(fps)
        
        # reset screeb
        DISPLAYSURF.fill(0)
        
        event_list = pygame.event.get()
        for event in event_list:
        
            # quit program
            if event.type == pygame.QUIT:
                exit()
                
            elif event.type == pygame.KEYDOWN:
                # go back to title screen
                if event.key == pygame.K_ESCAPE and can_interact:
                    can_interact = False
                    transition.reset()
                    transition.start()
                    started_from_here = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    
                    # if left clicked and not transitioning, set flags to load the song and chart in gameplay_main()
                    for song in song_list:
                        if song.hovering and can_interact:
                            transition.reset()
                            # remove transition sound
                            transition.play_transition_sound = False
                            transition.start()
                            started_from_here = True
                            loading_song = True
                            
                            song_to_load = song.song_name
                            chart_to_load = song.chart_name

            elif event.type == pygame.MOUSEWHEEL:
                
                # use mousewheel to scroll each FreeplaySong and it's assets. Clamp positions on the screen as well.
                if song_list[0].image.ypos + event.y * 80 <= 50 and last_song.image.ypos + event.y * 80 >= 400:
                    for box in song_list:
                        ev_y = event.y * 80
                        box.image.ypos += ev_y
                        box.image.rect.y += ev_y
                        box.title_text.rect.y += ev_y
                        box.chart_text.rect.y += ev_y
                        box.artist_text.rect.y += ev_y
                        
                        if event.y > 0:
                            box.image.xpos += 4
                            box.image.rect.x += 4
                            box.title_text.rect.x += 4
                            box.chart_text.rect.x += 4
                            box.artist_text.rect.x += 4

                        elif event.y < 0:
                            box.image.xpos -= 4
                            box.image.rect.x -= 4
                            box.title_text.rect.x -= 4
                            box.chart_text.rect.x -= 4
                            box.artist_text.rect.x -= 4
        
        # blit background
        background.update(DISPLAYSURF)
        
        # update each FreeplaySong object
        for freeplay_song in song_list:
            freeplay_song.update(event_list, DISPLAYSURF)
        
        # disable interaction with freeplay song if transitioning
        if transition.transitioning:
            can_interact = False
            transition.update(DISPLAYSURF)
            transition.image.draw(DISPLAYSURF)
            tween.update(global_clock.get_time() / 1500)
            
        else:
            # else you can!
            can_interact = True
        
        # if you hit escape to go back to title...
        if transition.halfway and started_from_here and not loading_song:
            main('title', transition)
        
        # else, load desired song and chart into gameplay_main()!
        elif transition.halfway and started_from_here and loading_song:
            gameplay_main(song_to_load, chart_to_load, None, 0, False, 'freeplay', transition)
        
        # update app display
        pygame.display.update()
        
        # update window name
        pygame.display.set_caption(display_string)

## chart_main controls the chart editor.

# the chart editor consists of a low-opacity strum-grid in the middle, and a line-grid going out in all 8 directions.
# notes are placed / deleted with left click, on those grid points.

# beat, step, and ms variables are written in the top-right and saved by calc'ing the current pos in the song

# the position of the song is saved when you pause it (by calc'ing current_ms). Step lengths are calc'd by using that song sec_per_step util to see how much it should be.
# scrolling increments 1 step, so use that step to ms calc to determine how many ms are moved into the future / past by scrolling

# when you hit space to play, the loaded song is played back from the saved ms value. ChartNote placement and values are lerp'd and calc'd as they would be
# in gameplay, but they are not killed indefinetly when they reach the middle (as to make it all editable and viewable).

# save button in the top left, config option for auto-saving every x minutes

# bottom left two input boxes and a load button. Type the song name into a box, the .json name into the other box, and hit "load" to load it (warning first).

def chart_main(song_to_load, chart_to_load, transition):

    # setup the config parser. It loads the player_settings.ini file in '/config' and loads, as it says, settings.
    p_settings = configparser.RawConfigParser()
    p_settings.read_file(open('config/player_settings.ini'))
    
    # stop menu music
    pygame.mixer.music.stop()

    # setup transition
    started_from_here = False
    can_interact = True
    
    # init background (update currently read settings too)
    p_settings.read_file(open('config/player_settings.ini'))
    background = BG(list(map(int, p_settings.get('Visual', 'bg colour').split())), bg_string)
    
    # start similarly to gameplay_main()
    
    # receptor postions
    receptor_xy = [(centerX - 50, centerY - 50),
    (centerX, centerY - 50),
    (centerX + 50, centerY - 50),
    (centerX + 50, centerY),
    (centerX + 50, centerY + 50),
    (centerX, centerY + 50),
    (centerX - 50, centerY + 50),
    (centerX - 50, centerY)]
    
    # note spawn positions
    note_spawn_pos = [tuple(map(operator.sub, receptor_xy[0], (650, 650))),
    tuple(map(operator.sub, receptor_xy[1], (0, 650))),
    tuple(map(operator.sub, receptor_xy[2], (-650, 650))),
    tuple(map(operator.sub, receptor_xy[3], (-650, 0))),
    tuple(map(operator.sub, receptor_xy[4], (-650, -650))),
    tuple(map(operator.sub, receptor_xy[5], (0, -650))),
    tuple(map(operator.sub, receptor_xy[6], (650, -650))),
    tuple(map(operator.sub, receptor_xy[7], (650, 0)))]
    
    # setup receptors
    for x in range(0, key_count):
        receptors["receptor{0}".format(x)] = Receptor(x, 90 + x * 45, 0.5, 'receptor')
        
        recep = receptors.get('receptor{}'.format(x))
        receptor_texture = recep.texture_string
        DISPLAYSURF.blit(recep.image, receptor_xy[x])
        
    recep_timer = Timer(0)
            
    # load song
    if song_to_load == None:
        # if no song, set everything to 0
        current_song = song_to_load
        sec_per_step = 0
        sec_per_beat = 0
    else:
        # if there is a song, laod it and setup song position variables
        current_song = Song(song_to_load)
        sec_per_step = current_song.sec_per_step
        sec_per_beat = current_song.sec_per_beat
    
    # set current beat (for metronome)
    cur_beat = 0
    prev_beat = -1
    
    # add grid sections
    
    # setup grid colours
    grid_cols = [(255, 255, 255), (220, 220, 220)]
    grid_hover_col = (120, 120, 120)
    
    # for transparency, create new surface to blit grid assets to
    GRIDSURF = pygame.Surface((1280, 720), pygame.SRCALPHA)
    GRIDSURF.set_alpha(100)
    
    # setup the grid. it is a 2d list, one sub-list for each receptor. Grids are setup this way to make referencing a certain receptor easy
    grid = [[], [], [], [], [], [], [], []]
    grid_size = 36
    
    # setup each receptor grid. Offset in different directions based on which id it is.
    # set mult of ms for each grid here (basically add song's sec_per_step to each grid, making it time accurate)
    
    # recep 0
    for x in range(0, 10):
        grid[0].append(ChartGrid(receptor_xy[0][0] - grid_size * x, receptor_xy[0][1] - grid_size * x, grid_size, grid_size, 0, 0 + sec_per_step * x, grid_cols[x % 2], grid_hover_col))
    
    # recep 1
    for x in range(0, 10):
        grid[1].append(ChartGrid(receptor_xy[1][0], receptor_xy[1][1] - grid_size * x, grid_size, grid_size, 1, 0 + sec_per_step * x, grid_cols[x % 2], grid_hover_col))
        
    # recep 2
    for x in range(0, 10):
        grid[2].append(ChartGrid(receptor_xy[2][0] + grid_size * x, receptor_xy[2][1] - grid_size * x, grid_size, grid_size, 2, 0 + sec_per_step * x, grid_cols[x % 2], grid_hover_col))
        
    # recep 3
    for x in range(0, 18):
        grid[3].append(ChartGrid(receptor_xy[3][0] + grid_size * x, receptor_xy[3][1], grid_size, grid_size, 3, 0 + sec_per_step * x, grid_cols[x % 2], grid_hover_col))
        
    # recep 4
    for x in range(0, 10):
        grid[4].append(ChartGrid(receptor_xy[4][0] + grid_size * x, receptor_xy[4][1] + grid_size * x, grid_size, grid_size, 4, 0 + sec_per_step * x, grid_cols[x % 2], grid_hover_col))
        
    # recep 5
    for x in range(0, 10):
        grid[5].append(ChartGrid(receptor_xy[5][0], receptor_xy[5][1] + grid_size * x, grid_size, grid_size, 5, 0 + sec_per_step * x, grid_cols[x % 2], grid_hover_col))
        
    # recep 6
    for x in range(0, 10):
        grid[6].append(ChartGrid(receptor_xy[6][0] - grid_size * x, receptor_xy[6][1] + grid_size * x, grid_size, grid_size, 6, 0 + sec_per_step * x, grid_cols[x % 2], grid_hover_col))
        
    # recep 7
    for x in range(0, 17):
        grid[7].append(ChartGrid(receptor_xy[7][0] - grid_size * x, receptor_xy[7][1], grid_size, grid_size, 7, 0 + sec_per_step * x, grid_cols[x % 2], grid_hover_col))
    
    # get keybinds from config
    keybinds = list(map(str, p_settings.get('Gameplay', 'keybindings').split()))
    
    # setup chart notes
    note_list = []
    
    # if there is a song to load, parse the JSON of the chart and create a list of notes to load into the editor.
    if song_to_load != None:
        if os.path.exists(f'songs/{current_song.name}/{chart_to_load}.json'):
            chart_JSON = open(f'songs/{current_song.name}/{chart_to_load}.json', 'r')
            string_JSON = chart_JSON.read()
            loaded_JSON = json.loads(string_JSON)
            
            # for each note in loaded json, add it to note list
            for x in range(0, len(loaded_JSON)-1):
                print(loaded_JSON[f'note{x}'])
                
                note = loaded_JSON.get(f'note{x}')
                note_list.append(ChartNote(note[0], receptors, note[1], note_spawn_pos[note[1]], note[2] - (loaded_JSON['offset']), note[3], note[4].replace('"', ''), 0.5, note[5], current_song))


    # setup HUD
    details_box = Image('big_box', 1175, -90, 0.9)
    
    # setup metronome flag. if it is active, a tick will happen on each beat
    metronome_text = Text('Metronome', (5, 70), DETAILS_FONT, 1, (255, 255, 255))
    metronome_box_check = Image('box_checked', metronome_text.image.get_rect().midright[0] + 5, metronome_text.rect.y - 13, 0.6)
    metronome_box_uncheck = Image('box', metronome_text.image.get_rect().midright[0] + 5, metronome_text.rect.y - 13, 0.6)
    metronome_box = metronome_box_uncheck
    metronome = False

    # hitsound flag. if activated, notes will play a sound when they should be hit.
    hitsound_text = Text('Hitsounds', (5, 110), DETAILS_FONT, 1, (255, 255, 255))
    hitsound_box_check = Image('box_checked', hitsound_text.image.get_rect().midright[0] + 5, hitsound_text.rect.y - 13, 0.6)
    hitsound_box_uncheck = Image('box', hitsound_text.image.get_rect().midright[0] + 5, hitsound_text.rect.y - 13, 0.6)
    hitsound_box = hitsound_box_uncheck
    hitsounds = False

    # setup chart saving and loading buttons
    save_button = Button('Save', 5, 5, 150, 50, (200, 200, 200), (230, 230, 230), DETAILS_FONT, (0, 0, 0))
    load_button = Button('Load', 5, 665, 150, 50, (200, 200, 200), (230, 230, 230), DETAILS_FONT, (0, 0, 0))

    # if song exists, set default text to that. if not, text is nothing.
    if current_song != None:
        load_field = TextInput(current_song.name, 5, 575, 200, 25, (255, 255, 255), (200, 200, 200), (140, 140, 140), DETAILS_FONT, (0, 0, 0), 0.65)

    else:
        load_field = TextInput('', 5, 575, 200, 25, (255, 255, 255), (200, 200, 200), (140, 140, 140), DETAILS_FONT, (0, 0, 0), 0.65)

    # same thing for chart text.
    if chart_to_load != None:
        chart_name_field = TextInput(chart_to_load, 5, 625, 200, 25, (255, 255, 255), (200, 200, 200), (140, 140, 140), DETAILS_FONT, (0, 0, 0), 0.65)

    else:
        chart_name_field = TextInput('', 5, 625, 200, 25, (255, 255, 255), (200, 200, 200), (140, 140, 140), DETAILS_FONT, (0, 0, 0), 0.65)

    # text that shows what each input area is for
    load_text = Text('Song Name', (5, load_field.rect.y - 15), DETAILS_FONT, 0.8, (255, 255, 255))
    chart_name_text = Text('Chart .JSON Name', (5, chart_name_field.rect.y - 15), DETAILS_FONT, 0.8, (255, 255, 255))

    # text that appears when you hit the save button,
    saved_text = Text('Chart Saved.', (DISPLAYSURF.get_rect().center[0], DISPLAYSURF.get_rect().center[1]), DETAILS_FONT_BIG, 1, (0, 0, 0), 'center')
    saved_timer = Timer(0)
    saved_timer.start(0)
    saved_timer.count()
    saved_timer.reset(True)
    saved_timer.dt = 0

    # for timing, create just_saved variable
    just_saved = False

    # the box that appears when a note is selected
    note_data_box = Image('info_box', -430, 170, 0.75)
    
    # setup "info" button (takes you to py-mania wiki)
    if is_dark(list(map(int, p_settings.get('Visual', 'bg colour').split()))):
        info_box = Image('info_button_dark', 1240, 85, 0.35)
        
    else:
        info_box = Image('info_button', 1240, 85, 0.35)
        
    info_box.rect.x = 1240
    info_box.rect.y = 85
        
    # get fps from config
    fps = p_settings.getint('Gameplay', 'fps limit')

    # set window name
    if song_to_load == None:
        display_string = f'Py-Mania - Chart Editor (Empty Chart)'
    else:
        display_string = f'Py-Mania - Chart Editor ({current_song.name})'

        ## loop
    while (1):

        # FPS limit
        global_clock.tick_busy_loop(fps)

        # if song is loded, set current millisecond to song conductor
        if current_song != None:
            current_ms = current_song.conductor.dt * 1000
        else:
            current_ms = 0

        # reset screen
        DISPLAYSURF.fill(0)

        # get mouse position
        mpos = pygame.mouse.get_pos()

        # set cur beat for metronome
        if current_song != None:
            cur_beat = current_song.pos_in_beats

        # if the song is playing, update it's timer
        if current_song != None:
            if current_song.playing:
                current_song.update(False, grid)

        # if beat has changed, play metronome (if active)
        if metronome:
            if prev_beat != cur_beat:
                pygame.mixer.Sound('sounds/metronome.wav').play()

        # for metronome setup
        prev_beat = cur_beat

        event_list = pygame.event.get()
        for event in event_list:
            # quit
            if event.type == pygame.QUIT:
                exit()

            elif event.type == pygame.KEYDOWN:

                # start screen transition if escape is pressed
                if event.key == pygame.K_ESCAPE:
                    if can_interact:
                        can_interact = False
                        pygame.mixer.music.stop()
                        transition.reset()
                        transition.start()
                        started_from_here = True
                        transition.play_menu_music = True

                # if song is loaded, take inputs
                if current_song != None:

                    # receptor inputs
                    for x in range(0, key_count):
                        # get the hit key and convert it into a string that is it's name
                        key_pressed = pygame.key.name(event.key).replace("'", '').replace('[', '').replace(']', '')

                        # compare key name to the one saved in the keybinds list loaded from config
                        if key_pressed == keybinds[x]:
                            if p_settings.getboolean('Chart Editor', 'type to chart'):
                                print(current_song.playing)
                                if current_song.playing:
                                
                                    if hitsounds:
                                        pygame.mixer.Sound('sounds/hitsound.wav').play()
                                    # p_settings.getfloat('Gameplay', 'global offset')
                                    note_list.append(ChartNote(len(note_list)+1, receptors, x, note_spawn_pos[x], current_ms, 0, 'note', 0.5, '', current_song))

                    # if space is hit, pause or unpause the song (if you are not typing into a box at the moment)
                    if event.key == pygame.K_SPACE:
                        if not load_field.typing and not chart_name_field.typing:
                            if current_ms == 0:
                                current_song.start(0)
                            else:
                                current_song.pos_in_steps = int(current_ms / current_song.sec_per_step)
                                current_song.pause(not current_song.playing)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:

                    # if left click and can interact, update the boxes if they are hovered. If save button is clicked, show saved text
                    if can_interact:
                        if metronome_box.rect.collidepoint(mpos):
                            metronome = not metronome
                            # play interaction sound
                            pygame.mixer.Sound('sounds/interact.wav').play()
                            print(metronome)

                        elif hitsound_box.rect.collidepoint(mpos):
                            hitsounds = not hitsounds
                            # play interaction sound
                            pygame.mixer.Sound('sounds/interact.wav').play()
                            print(hitsounds)

                        elif save_button.rect.collidepoint(mpos) and current_song != None:
                            if len(note_list) > 0:

                                print(saved_timer.dt)

                                if saved_timer.counting:
                                    saved_timer.reset(True)

                                just_saved = True
                                print('saved')
                        
                        # open my wiki :)
                        elif info_box.rect.collidepoint(mpos):
                            webbrowser.open_new_tab('https://github.com/A2sourceReleases/Py-Mania/wiki/Chart%20Editor%20Basics')

            elif event.type == pygame.MOUSEWHEEL:

                # if song is loaded and mousewheel is used
                if current_song != None:

                    # only scroll if song it not currently playing
                    if not current_song.playing:

                        # scroll into the future! (or past!)
                        if event.y > 0:
                            if current_song.pause_time + current_song.sec_per_step <= current_song.length * 1000:

                                # update each time based variable
                                current_song.pause_time += current_song.sec_per_step
                                current_ms += current_song.sec_per_step
                                current_song.conductor.dt += current_song.sec_per_step

                                # update each grid segment
                                for x in range(0, len(grid)):
                                    for y in range(0, len(grid[x])):
                                        segment = grid[x][y]
                                        segment.cur_ms += current_song.sec_per_step * 1000
                        else:
                            # scroll negative
                            if current_song.pause_time - current_song.sec_per_step >= 0:
                                current_song.pause_time -= current_song.sec_per_step
                                current_ms -= current_song.sec_per_step
                                current_song.conductor.dt -= current_song.sec_per_step

                                for x in range(0, len(grid)):
                                    for y in range(0, len(grid[x])):
                                        segment = grid[x][y]
                                        segment.cur_ms -= current_song.sec_per_step * 1000
                            else:
                                # clamp value to above 0
                                current_song.pause_time = 0
                                current_ms = 0

                                for x in range(0, len(grid)):
                                    for y in range(0, len(grid[x])):
                                        segment = grid[x][y]
                                        segment.cur_ms = segment.init_ms

                        # update the song's variables while paused
                        current_song.update_paused()

        # no bg colour here!
        background.update(DISPLAYSURF)

        # blit grid to screen
        DISPLAYSURF.blit(GRIDSURF, (0, 0))

        # update grid
        for x in range(0, len(grid)):
            for y in range(0, len(grid[x])):
                segment = grid[x][y]

                if y + 1 < len(grid[x]):
                    next_segment = grid[x][y + 1]

                segment.update(event_list, receptors, note_list, note_spawn_pos, GRIDSURF, DISPLAYSURF, current_song)

        # update receptors
        for x in range(0, key_count):
            recep = receptors.get('receptor{}'.format(x))
            recep.update(x, recep_timer.dt, receptor_xy, DISPLAYSURF)

        # update notes
        for note in note_list:
            if note != None:
                note.update(current_song, current_ms, note_list, event_list, hitsounds, DISPLAYSURF)
                
                # run hitsounds
                if round(note.calc, 2) == 0.88 and hitsounds and current_song.playing:
                    pygame.mixer.Sound('sounds/hitsound.wav').play()

        # update HUD
        if p_settings.getboolean('Chart Editor', 'show song data'):
            details_box.draw(DISPLAYSURF)
            song_data_display(current_song, None, None, 'chart', DISPLAYSURF)

        # draw metronome stuff
        metronome_text.draw(DISPLAYSURF)

        # update metronome box
        if metronome:
            metronome_box = metronome_box_check
        else:
            metronome_box = metronome_box_uncheck
        metronome_box.draw(DISPLAYSURF)

        # exact same thing for hitsound box
        hitsound_text.draw(DISPLAYSURF)

        if hitsounds:
            hitsound_box = hitsound_box_check
        else:
            hitsound_box = hitsound_box_uncheck
        hitsound_box.draw(DISPLAYSURF)

        # if a song is loaded, update save button
        if current_song != None:
            save_button.update(event_list, DISPLAYSURF, save_json, note_list, [current_song, chart_name_field.saved_var])

        # update load button. put load_json as the func argument and put a list of data as the argument for the function
        load_button.update(event_list, DISPLAYSURF, load_json, 'chart', [load_field.saved_var, chart_name_field.saved_var, transition])

        # update song load field and chart load field
        load_field.update(DISPLAYSURF, event_list)
        load_text.draw(DISPLAYSURF)

        chart_name_field.update(DISPLAYSURF, event_list)
        chart_name_text.draw(DISPLAYSURF)

        # update "saved" display text based on a timer
        if just_saved and not saved_timer.counting:
            saved_timer.start(0)
            print(just_saved)
            
        elif just_saved and saved_timer.dt < 0.8:
            print(saved_timer.dt)
            saved_text.draw(DISPLAYSURF)
            saved_timer.count()

        if saved_timer.dt > 0.8:
            saved_timer.reset(True)
            just_saved = False
        
        # update each chart note
        for chart_note in note_list:
            
            # if a note is selected, draw that note's data to the screen
            if chart_note != None:
                if chart_note.selected and p_settings.getboolean('Chart Editor', 'show extra data'):
                    note_data_box.draw(DISPLAYSURF)
                    chart_note_data_display(chart_note, DISPLAYSURF)
                    
        # draw info button
        info_box.draw(DISPLAYSURF)
            
        # update transition
        if transition.transitioning:
            transition.update(DISPLAYSURF)
            transition.image.draw(DISPLAYSURF)
            tween.update(global_clock.get_time() / 1500)
        
        # go back to title screen
        if transition.halfway and started_from_here:
            main('title', transition)
            
        # update app display
        pygame.display.update(current_song, DISPLAYSURF)
        
        # update window name
        pygame.display.set_caption(display_string)

# title_main controls the title screen of the game
def title_main(transition):
    
    # setup the config parser. It loads the player_settings.ini file in '/config' and loads, as it says, settings.
    p_settings = configparser.RawConfigParser()
    p_settings.read_file(open('config/player_settings.ini'))
    
    # setup transition
    started_from_here = False
    if transition == None:
        screen_transition = Transition('sweep', 2)
        pygame.mixer.music.load('sounds/music/menu.mp3')
        pygame.mixer.music.set_volume(0.15)
        pygame.mixer.music.play(-1, 0)
        
    else:
        screen_transition = transition
        
    # init background (update currently read settings too)
    p_settings.read_file(open('config/player_settings.ini'))
    background = BG(list(map(int, p_settings.get('Visual', 'bg colour').split())), bg_string)
    
    print()
    print('title')
    
    # setup title button colours
    BUTTON_COL = (189, 189, 189)
    BUTTON_HOVER_COL = (215, 215, 215)
    
    # create title buttons
    list_button = Button('LIST SELECT', 0, 525, 380, 75, BUTTON_COL, BUTTON_HOVER_COL, RATINGS_FONT, (0, 0, 0))
    play_button = Button('FREEPLAY', 0, 350, 380, 75, BUTTON_COL, BUTTON_HOVER_COL, RATINGS_FONT, (0, 0, 0))
    options_button = Button('OPTIONS', 0, 450, 380, 75, BUTTON_COL, BUTTON_HOVER_COL, RATINGS_FONT, (0, 0, 0))
    exit_button = Button('EXIT', 0, 550, 380, 75, BUTTON_COL, BUTTON_HOVER_COL, RATINGS_FONT, (0, 0, 0))
    
    # position buttons correctly
    list_button.rect.center = DISPLAYSURF.get_rect().center
    
    play_button.rect.center = DISPLAYSURF.get_rect().center
    play_button.rect.y += 100
    
    options_button.rect.center = DISPLAYSURF.get_rect().center
    options_button.rect.y += 200
    
    exit_button.rect.center = DISPLAYSURF.get_rect().center
    exit_button.rect.y += 300
    
    # setup logo image. If background is dark, load the alt image
    # also set up version text. Change colour if light or dark.
    version_string = 'Py-Mania v1.0'
    
    if is_dark(list(map(int, p_settings.get('Visual', 'bg colour').split()))):
        logo = Image('py-mania-logo_dark', 40, 25, 1)
        version = Text(version_string, (1295, 710), DETAILS_FONT, 0.85, (255, 255, 255), 'midright')
    
    else:
        logo = Image('py-mania-logo', 40, 25, 1)
        version = Text(version_string, (1295, 710), DETAILS_FONT, 0.85, (0, 0, 0), 'midright')

    # setup main function to load
    # this is used as an argument in the main() function (the one that switches between states)
    mode_to_switch = ''
    
    # get fps from config
    fps = p_settings.getint('Gameplay', 'fps limit')

    ## loop
    while(1):
        # FPS limit
        global_clock.tick_busy_loop(fps)
        
        # clear screen
        DISPLAYSURF.fill(0)
        
        
        # get mouse position (for version text)
        mpos = pygame.mouse.get_pos()
        
        event_list = pygame.event.get()
        for event in event_list:
        
            # quit program
            if event.type == pygame.QUIT:
                exit()
            
            # if delete key pressed, enter chart editor mode
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DELETE:
                    if not screen_transition.transitioning:
                        screen_transition.reset()
                        screen_transition.play_transition_sound = False
                        screen_transition.start()
                        started_from_here = True
                        mode_to_switch = 'chart'
                        print('chart')

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not screen_transition.transitioning:
                    
                        # switch to the correct main function, based on which button was pressed
                        if list_button.hovering:
                            screen_transition.reset()
                            screen_transition.play_transition_sound = False
                            screen_transition.start()
                            started_from_here = True
                            mode_to_switch = 'list'
                            print('list')
                        
                        elif play_button.hovering:
                            screen_transition.reset()
                            screen_transition.play_transition_sound = False
                            screen_transition.start()
                            started_from_here = True
                            mode_to_switch = 'freeplay'
                            print('freeplay')
                            
                        elif options_button.hovering:
                            screen_transition.reset()
                            screen_transition.play_transition_sound = False
                            screen_transition.start()
                            started_from_here = True
                            mode_to_switch = 'options'
                            print('options')
                            
                        elif exit_button.hovering:
                            exit()
                        
                        # open git page
                        elif version.rect.collidepoint(mpos):
                            webbrowser.open_new_tab('https://github.com/A2sourceReleases/Py-Mania')
        
        # blit background
        background.update(DISPLAYSURF)
        
        # update title buttons
        list_button.update(event_list, DISPLAYSURF)
        play_button.update(event_list, DISPLAYSURF)
        options_button.update(event_list, DISPLAYSURF)
        exit_button.update(event_list, DISPLAYSURF)
        
        # draw logo
        logo.draw(DISPLAYSURF)
        
        # draw text assets
        version.draw(DISPLAYSURF)
        
        # update transition tween if transitioning
        if screen_transition.transitioning:
            screen_transition.update(DISPLAYSURF)
            screen_transition.image.draw(DISPLAYSURF)
            tween.update(global_clock.get_time() / 1500)
        
        # if halfway, run the correct main function (mode_to_switch is set when you press a title screen button)
        if screen_transition.halfway and started_from_here:
            main(mode_to_switch, screen_transition)
        
        # update display
        pygame.display.update()
        
        # update window name
        pygame.display.set_caption(display_string)
        
# options menu main function!
# allows player to choose many different options about their game
def options_main(transition):
    
    # setup the config parser. It loads the player_settings.ini file in '/config' and loads, as it says, settings.
    p_settings = configparser.RawConfigParser()
    p_settings.read_file(open('config/player_settings.ini'))
    
    # setup transition
    #transition.reset()
    started_from_here = False
    can_interact = True
    
    # init background (update currently read settings too)
    p_settings.read_file(open('config/player_settings.ini'))
    background = BG(list(map(int, p_settings.get('Visual', 'bg colour').split())), bg_string)
    
    # https://docs.python.org/3.7/library/configparser.html
    # my friend
    
    # setup options to draw
    options = []
    
    # option, header, x, y, surf, type
    
    offset = 30
    
    # create an option object for each and every section of the config file (fond in '/config')
    options.append(Option('Gameplay', None, '', 5, -40, DISPLAYSURF, 'header'))
    options.append(Option('Gameplay', 'FPS Limit', 'The FPS limit of the program.', 5, options[len(options) - 1].text.rect.midbottom[1] + offset, DISPLAYSURF, 'int', 1, 999))
    options.append(Option('Gameplay', 'Global Offset', 'The offset of notes compared to the song.\nIf you experience lag, or are hitting a consistent\nms value away from 0,\nit is recommended to change this value.', 5, options[len(options) - 1].text.rect.midbottom[1] + offset, DISPLAYSURF, 'float', -1000.00, 1000.00))
    options.append(Option('Gameplay', 'Keybindings', 'Customize your keybindings!', 5, options[len(options) - 1].text.rect.midbottom[1] + offset, DISPLAYSURF, 'keybind'))
    options.append(Option('Gameplay', 'Scroll Speed', 'The speed at which notes scroll.\n(Higher value means slower speed)', 5, options[len(options) - 1].text.rect.midbottom[1] + offset, DISPLAYSURF, 'float', 1.00, 6.00))
    options.append(Option('Gameplay', 'Hitsounds', 'A sound plays when you hit a note.', 5, options[len(options) - 1].text.rect.midbottom[1] + offset, DISPLAYSURF, 'bool'))
    
    options.append(Option('Visual', None, '', 5, options[len(options) - 1].text.rect.midbottom[1] + offset, DISPLAYSURF, 'header'))
    options.append(Option('Visual', 'Show MS', 'Show MS accuracy when you hit a note?', 5, options[len(options) - 1].text.rect.midbottom[1] + offset, DISPLAYSURF, 'bool'))
    options.append(Option('Visual', 'Extra Info', 'Show data on hit note ranks?', 5, options[len(options) - 1].text.rect.midbottom[1] + offset, DISPLAYSURF, 'bool'))
    options.append(Option('Visual', 'Show App Data', 'Show FPS and RAM usage?', 5, options[len(options) - 1].text.rect.midbottom[1] + offset, DISPLAYSURF, 'bool'))
    options.append(Option('Visual', 'BG Colour', 'Set the BG colour to any value you like!\nDarker colours will activate dark mode for\nsome objects.\n(It is recommended to use lighter colours.)', 5, options[len(options) - 1].text.rect.midbottom[1] + offset, DISPLAYSURF, 'colour'))
    options.append(Option('Visual', 'Note Colour', 'Set note texture colour.', 5, options[len(options) - 1].text.rect.midbottom[1] + offset, DISPLAYSURF, 'colour'))
    options.append(Option('Visual', 'Timebar Colour', 'Set Timebar fill colour.', 5, options[len(options) - 1].text.rect.midbottom[1] + offset, DISPLAYSURF, 'colour'))
    options.append(Option('Visual', 'Auto-Swap Receptor Skin', 'If checked, when BG is dark, auto-swap the\ntexture of the receptors from light to dark.', 5, options[len(options) - 1].text.rect.midbottom[1] + offset, DISPLAYSURF, 'bool'))
    options.append(Option('Visual', 'Receptor Skin', 'If Auto-Swapping is disabled, set which\nreceptor skin to use.\n0 = Light\n1 = Dark', 5, options[len(options) - 1].text.rect.midbottom[1] + offset, DISPLAYSURF, 'int', 0, 1))
    
    options.append(Option('Chart Editor', None, '', 5, options[len(options) - 1].text.rect.midbottom[1] + offset, DISPLAYSURF, 'header'))
    options.append(Option('Chart Editor', 'Show Song Data', 'Show song title, BPM, and length?', 5, options[len(options) - 1].text.rect.midbottom[1] + offset, DISPLAYSURF, 'bool'))
    options.append(Option('Chart Editor', 'Show Extra Data', "Shows currently selected note's data on screen.", 5, options[len(options) - 1].text.rect.midbottom[1] + offset, DISPLAYSURF, 'bool'))
    options.append(Option('Chart Editor', 'Type to Chart', "Allows keyboard input to place notes if checked.", 5, options[len(options) - 1].text.rect.midbottom[1] + offset, DISPLAYSURF, 'bool'))
    
    options.append(Option('Debug', None, '', 5, options[len(options) - 1].text.rect.midbottom[1] + offset, DISPLAYSURF, 'header'))
    options.append(Option('Debug', 'Debug Mode', 'Show current Beat, Step, and MS.', 5, options[len(options) - 1].text.rect.midbottom[1] + offset, DISPLAYSURF, 'bool'))
    options.append(Option('Debug', 'Super Debug Mode', 'Show extra Debug values.', 5, options[len(options) - 1].text.rect.midbottom[1] + offset, DISPLAYSURF, 'bool'))
    
    options.append(Option('Extra', None, '', 5, options[len(options) - 1].text.rect.midbottom[1] + offset, DISPLAYSURF, 'header'))
    options.append(Option('Extra', 'Disable Intro', 'Game intro is disabled if checked.', 5, options[len(options) - 1].text.rect.midbottom[1] + offset, DISPLAYSURF, 'bool'))
    
    # menu open vars. also cur_menu_open, to detect escape key presses
    menu_open = False
    cur_menu_open = options[1]
    
    # last option in list (for position clamping)
    last_option = options[len(options) - 1]
    
    # get fps from config
    fps = p_settings.getint('Gameplay', 'fps limit')
    
    ## loop
    while(1):
        
        # FPS limit
        global_clock.tick_busy_loop(fps)
        
        # clear screen
        DISPLAYSURF.fill(0)
        
        event_list = pygame.event.get()
        for event in event_list:
        
            # quit program
            if event.type == pygame.QUIT:
                exit()
            
            if event.type == pygame.KEYDOWN:
                
                # if an option's menu is not open (colour menu or keybind menu), allow player to hit escape to go back to title
                if not cur_menu_open.menu_active and event.key == pygame.K_ESCAPE:
                    if not transition.transitioning:
                        transition.reset()
                        transition.start()
                        started_from_here = True
            
            # if you scroll and a menu is not open, clamp positions
            elif not cur_menu_open.menu_active and event.type == pygame.MOUSEWHEEL and options[0].text.rect.y + event.y * 35 <= 15 and last_option.text.rect.y + event.y * 35 >= 400:
                ev_y = event.y * 35
                
                # move each option's assets based on scroll
                for option in options:
                    option.text.rect.y += ev_y
                    
                    if option.type == 'float' or option.type == 'int':
                        option.image.rect.y += ev_y
                        option.bg.y += ev_y
                    
                    elif option.type == 'bool':

                        option.check.ypos += ev_y
                        option.check.rect.y += ev_y
                        option.uncheck.ypos += ev_y
                        option.uncheck.rect.y += ev_y
                    
                    elif option.type == 'colour':
                        option.image.y += ev_y
                    
                    elif option.type == 'keybind':
                        option.image.rect.y += ev_y
                        
        # blit background
        background.update(DISPLAYSURF)
        
        # draw options
        for option in options:
            
            # set currently selected option
            if not cur_menu_open.menu_active:
                if option.hovering:
                    cur_menu_open = option
            
            # activate ability to change option if it is hovered.
            if option.type != 'colour':
                
                if cur_menu_open != option:
                    option.active = False
                else:
                    option.active = True
                
                # update option
                option.update(event_list, DISPLAYSURF, can_interact)
                
        # make sure that the colour picker menu is drawn on-top of all of the other options 
        for option in options:
            if option.type == 'colour':  
                if not option.menu_active:
                
                    # same thing as before
                    if cur_menu_open != option:
                        option.active = False
                    else:
                        option.active = True
                    
                    option.update(event_list, DISPLAYSURF, can_interact)
        
        # draw currently open menu on-top of other colour options, regardless of place in the list
        for option in options:
            if option.menu_active and option.type == 'colour' or option.menu_active and option.type == 'keybind':
                cur_menu_open = option
                option.update(event_list, DISPLAYSURF, can_interact)
        
        # draw option info box over everything
        for option in options:
            option.draw_post(DISPLAYSURF)
        
        # update transition and stop interaction
        if transition.transitioning:
            can_interact = False
            transition.update(DISPLAYSURF)
            transition.image.draw(DISPLAYSURF)
            tween.update(global_clock.get_time() / 1500)
            
        else:
            can_interact = True
        
        # update bg (if colour changed) and go back to title
        if transition.halfway and started_from_here:
            main('title', transition)
        
        # update display       
        pygame.display.update()
        
        # update window name
        pygame.display.set_caption(display_string)
 
## now for the meat and potatoes. the gameplay_main() handles the gameplay
# big function because of all of the note input logic :)

def gameplay_main(song_to_load, chart_to_load, list_to_load, list_pos, restarting, prev_mode, transition):

    # setup the config parser. It loads the player_settings.ini file in '/config' and loads, as it says, settings.
    p_settings = configparser.RawConfigParser()
    p_settings.read_file(open('config/player_settings.ini'))
    
    # setup transition
    started_from_here = False
    mode_to_switch = None
    previous_mode = prev_mode
    restarted = restarting
    can_interact = True
    
    # paused var
    paused = False
    
    # init background (update currently read settings too)
    p_settings.read_file(open('config/player_settings.ini'))
    background = BG(list(map(int, p_settings.get('Visual', 'bg colour').split())), bg_string)
    
    # first, the receptors are added, along with the keybindings and other gameplay settings
    
    # setup receptors
    # https://stackoverflow.com/questions/6181935/how-do-you-create-different-variable-names-while-in-a-loop
    for x in range(0, key_count):
        receptors["receptor{0}".format(x)] = Receptor(x, 45 + x * -45, 1, 'receptor') # makes it a receptor
        
        recep = receptors.get('receptor{}'.format(x)) # how I'm going to reliably access the receptor values
        receptor_texture = recep.texture_string
        DISPLAYSURF.blit(recep.image, receptor_xy[x])
    
    # grab keybinds from player_settings
    keybinds = list(map(str, p_settings.get('Gameplay', 'keybindings').split()))
    
    # loop that converts keybinds from a string into a list of strings
    for x in range(0, len(keybinds)):
        key = keybinds[x]
        keybinds[x] = str(key).replace('[', '').replace(']', '')
        
    print(keybinds)
    
    # setup song ms values
    start_ms = pygame.time.get_ticks()
    current_ms = -500
    
    # if list is loaded, set current song to load
    current_list = list_to_load
    if current_list != None:
        current_list_song = list_pos + 1
        
    else:
        current_list_song = 0
    
    # if a list is loaded, set list mode on and load correct song in list
    list_mode = False
    if list_to_load != None:
    
        # remember, list songs to load contain [song name, chart name] for each song (2d array)
        current_song = Song(list_to_load[current_list_song][0])
        list_mode = True
    
    else:
        # if not list, load song selected from freeplay
        current_song = Song(song_to_load)
    
    # time progression variables (time_prog used for timebar)
    cur_beat = None
    time_prog = 0
    
    # then, notes are added into a list to be loaded later
    note_list = {}
    
    # open chart json
    if chart_to_load == None:
        
        # if list, load the [song name, chart name] portion of the current song in the 2d array
        #                               ~~^^^^^^~~
        
        chart_JSON = open(f'songs/{current_song.name}/{list_to_load[current_list_song][1]}.json', 'r')
            
    else:
        
        # else, load provided json
        chart_JSON = open(f'songs/{current_song.name}/{chart_to_load}.json', 'r')
    
    # load json in string mode (load's', as in load string)
    string_JSON = chart_JSON.read()
    loaded_JSON = json.loads(string_JSON)
    
    # same as chart editor, convert note data in json into a list of notes to load in the game
    for x in range(0, len(loaded_JSON)-1):
        note = loaded_JSON.get(f'note{x}')
        note_list[f'note{x}'] = Note(note[0], receptors, note[1], note[2] - loaded_JSON['offset'], note[3], note[4].replace('"', ''), note[5], current_song)
        
    print()
    print('Amount of notes:', len(note_list))
    
    # an array containing 8 seperate timers (for each receptor. lets hold timers overlap.)
    recep_timers = []
    
    for x in range(0, key_count):
        recep_timers.append(Timer(x))
        
        timer = recep_timers[x]
        
        if timer.id == x:
            # I have to do this to avoid the first hold time measurement being based on the epoch.
            timer.start(0)
            timer.count()
            timer.reset(True)
    
    # add the box to go behind the fps stuff
    fps_box = Image('fps_box', 1175, -10, 0.9)
    acc_box = Image('full_rounded', 1160, 72, 0.65)
    display_box = Image('display_box', 0, -90, 0.65)
    note_dat_box = Image('big_box', 1135, centerY - 85, 0.8, 'center')
    
    # setup the first note to hit
    cur_note = 0
    cur_hit_notes = []
    
    # now that everything else is setup, I want to setup all of the bars and HUD assets
    
    timebar_rect = pygame.Rect(0, 710, 1280, 50)
    
    # rank that appears when you hit a note (good, perfect, miss, etc.)
    rank_shown = None
    rank_text = None
    rank_tween = None
    rank_timer = Timer(0)
    
    # gameplay variables
    
    # this is used to store how many of each note you have hit.
    # perfect, great, good, bad, miss
    accuracy_ranks = [0, 0, 0, 0, 0]
    average_acc = 0
    
    # setup the gameplay intro, to give the player time to be ready
    intro_assets = []
    intro_assets.append(Image('info_box', -1000, DISPLAYSURF.get_rect().center[1] - 55, 0.95))
    intro_assets.append(Text('Now Playing:', (intro_assets[0].rect.center[0] - 30, intro_assets[0].rect.center[1] - 35), DETAILS_FONT_BIG, 0.5, (255, 255, 255), 'center'))
    intro_assets.append(Text(current_song.info.tag.title, (intro_assets[1].rect.center[0] - 5, intro_assets[0].rect.center[1] - 30), DETAILS_FONT_BIG, 1.1, (255, 255, 255)))
    intro_assets.append(Text(f'by {current_song.info.tag.artist}', (intro_assets[2].rect.center[0] - 5, intro_assets[0].rect.center[1] + 55), DETAILS_FONT, 1, (255, 255, 255), 'center'))
    intro_assets.append(Image('note', -100, 0, 1))
    
    intro_tween = tween.to(intro_assets[0].rect, 'x', -1000, 0.01)
    
    intro_timer = Timer(0)
    
    intro_running = False
    intro_finished = False
    
    # setup the pause menu assets
    pause_menu_assets = []
    pause_menu_assets.append(Image('pause', 0, 0, 1))
    pause_menu_assets.append(Button('Resume', DISPLAYSURF.get_rect().center[0] - 170, DISPLAYSURF.get_rect().center[1] - 175, 325, 100, (180, 180, 180), (100, 100, 100), RATINGS_FONT, (255, 255, 255)))
    pause_menu_assets.append(Button('Restart', DISPLAYSURF.get_rect().center[0] - 170, DISPLAYSURF.get_rect().center[1] - 60, 325, 100, (180, 180, 180), (100, 100, 100), RATINGS_FONT, (255, 255, 255)))
    pause_menu_assets.append(Button('Exit', DISPLAYSURF.get_rect().center[0] - 170, DISPLAYSURF.get_rect().center[1] + 55, 325, 100, (180, 180, 180), (100, 100, 100), RATINGS_FONT, (255, 255, 255)))
    pause_menu_assets.append(Button('Exit to Title', DISPLAYSURF.get_rect().center[0] - 170, DISPLAYSURF.get_rect().center[1] + 170, 325, 100, (180, 180, 180), (100, 100, 100), RATINGS_FONT, (255, 255, 255)))
       
    # get fps from config
    fps = p_settings.getint('Gameplay', 'fps limit')
    
    # set app caption
    display_string = f'Py-Mania - {current_song.info.tag.artist} - {current_song.info.tag.title}'
    
    ### gameplay loop
    while(1):
           
        # FPS limit
        global_clock.tick_busy_loop(fps)
            
        # conductor.tick(fps)
        for x in range(0, key_count):
            timer = recep_timers[x]
            if x == timer.id:
                if timer.counting:
                    timer.count()
        
        # current beat is set here (pulled from current song)
        cur_beat = current_song.pos_in_beats
        
        # the current millisecond value in the song
        if current_song.playing:
            current_ms = (pygame.time.get_ticks() - start_ms) - p_settings.getfloat('Gameplay', 'Global Offset')
        
        # here the song position and other values are updated
        if current_song.playing:
            current_song.update(False)
        
        # clear screen
        DISPLAYSURF.fill(0)
        
        # note list stuff
        # this if fixes a bug that happens when a holding note is the last note in a song
        if not note_list.get(f'note{cur_note}').actually_hit:
        
            # add the current 'note to hit' to the note list if it is not already there
            if cur_hit_notes.count(note_list.get(f'note{cur_note}')) == 0 and cur_hit_notes.count(note_list.get(f'note{cur_note}')) < 1:
                cur_hit_notes.append(note_list.get(f'note{cur_note}'))
            
            # check the next note to see it if it a double, triple, quadruple, etc. If the notes share an ms value, add it to the list.
            if note_list.get(f'note{cur_note + 1}') != None and compare_from_range(note_list.get(f'note{cur_note}').ms, note_list.get(f'note{cur_note + 1}').ms, 250) and cur_hit_notes.count(note_list.get(f'note{cur_note + 1}')) == 0:
                cur_hit_notes.append(note_list.get(f'note{cur_note + 1}'))
        
        # handles (some) user input, also other pygame events
        event_list = pygame.event.get()
        for event in event_list:
        
            # quit program
            if event.type == pygame.QUIT:
                exit()
            
            if event.type == pygame.KEYDOWN:
                
                # receptor inputs
                for x in range(0, key_count):
                    # get the hit key and convert it into a string that is it's name
                    key_pressed = pygame.key.name(event.key).replace("'", '').replace('[', '').replace(']', '')
                    
                    # compare key name to the one saved in the keybinds list loaded from config
                    if key_pressed == keybinds[x] and not paused:
                        
                        timer = recep_timers[x]                        
                        
                        # change receptor texture
                        recep = receptors.get(f'receptor{x}')
                        recep.press(True)
                        
                        # if you hit a note and you are +/- 250 ms away from the desired hit time, calc note hit logic
                        if not transition.transitioning and not intro_running:
                            for hit_note in cur_hit_notes:
                                if not timer.counting:
                                    if hit_note.ms - current_song.conductor.dt * 1000 < 250 and hit_note.ms - current_song.conductor.dt * 1000 > -133.33 and hit_note.recep_id == x:

                                        # play hitsound
                                        if p_settings.getboolean('Gameplay', 'hitsounds'):
                                            pygame.mixer.Sound('sounds/hitsound.wav').play()

                                        # for hold note logic. set note actually_hit flag
                                        hit_note.actually_hit = True

                                        # calculate ms accuracy (how far away were you from desired time?) and kill root note
                                        accuracy_ms = round(hit_note.ms - current_song.conductor.dt * 1000, 2)
                                        hit_note.kill_root()

                                        # if note is normal note
                                        if hit_note.hold_ms <= 0:

                                            # show note hit data (perfect, bad, etc. and ms accurac) and update overall accuracy
                                            rank_shown, average_acc, rank_text = calc_note_data(accuracy_ms, accuracy_ranks, note_list, rank_text)

                                            # show rank as a tween
                                            if rank_tween != None:
                                                rank_tween.stop()

                                            rank_tween = tween.to(rank_text, 'scale', 0.7, 0.9, 'easeOutElastic')

                                            # timer that removes the rank after a while
                                            if rank_timer.counting:
                                                rank_timer.reset(True)

                                            rank_timer.start(0)

                                            # remove the just hit note from the notes that you can hit
                                            cur_hit_notes.remove(hit_note)

                                        # else if the note is a note with hold length
                                        else:

                                            # activate note hold mode
                                            hit_note.holding = True

                                            # turn on recep timer
                                            if timer.counting:
                                                timer.reset(True)

                                            timer.start(0)
                                            timer.count()

                                        # if note is not the last in the list, add the next one to the list of notes that you can hit
                                        if cur_note + 1 <= len(note_list) - 1:
                                            cur_note += 1

                                    # if you are falling behind, add the next note as a safety net
                                    elif hit_note.ms - current_song.conductor.dt * 1000 < -133.33:
                                        if note_list.get(f'note{cur_note + 1}') != None and cur_hit_notes.count(note_list.get(f'note{cur_note + 1}')) == 0:
                                            cur_hit_notes.append(note_list.get(f'note{cur_note + 1}'))
                
                # pause / unpause if the song is playing in the right conditions
                if event.key == pygame.K_ESCAPE and not intro_running and current_song.conductor.dt > 0 and not transition.transitioning:
                    paused = not paused
                    current_song.pause(not current_song.playing)
            
            # now time to handle when the user lets go of a receptor
            if event.type == pygame.KEYUP:
            
                # receptor inputs
                for x in range(0, key_count):
                    
                    # check keys and stuff (same as KEYDOWN)
                    key_pressed = pygame.key.name(event.key).replace("'", '').replace('[', '').replace(']', '')
                    if key_pressed == keybinds[x] and not paused:
                        
                        # set hold time based on timer
                        timer = recep_timers[x]
                        hold_time = int(timer.dt * 1000)
                        
                        recep = receptors.get('receptor{}'.format(x))
                        
                        # if the song is playing correctly
                        if not transition.transitioning and not intro_running:

                            # check hold time of notes that you can hit
                            for hit_note in cur_hit_notes:
                                if hit_note != None:
                                    if hit_note.actually_hit and hit_note.hold_ms > 0 and hit_note.recep_id == x:
                                         
                                        # kill hold if you let go early      
                                        if hold_time < hit_note.hold_ms - 100:
                                                 
                                            for hold in hit_note.hold_notes:
                                                hold.kill()
                                                
                                            print('you failed!')
                                            
                                            # show miss
                                            accuracy_ranks[4] += 1
                                            rank_shown, average_acc, rank_text = calc_note_data(None, accuracy_ranks, note_list, rank_text)
                                            
                                            # same as KEYDOWN
                                            if rank_tween != None:
                                                rank_tween.stop()
                                                
                                            rank_tween = tween.to(rank_text, 'scale', 0.7, 0.9, 'easeOutElastic')
                                            
                                            if rank_shown != None:
                                                rank_shown.alive = False
                                            
                                            if rank_timer.counting:
                                                rank_timer.reset(True)
                                                    
                                            rank_timer.start(0)
                                            
                                            # print hold time
                                            print('Receptor', str(recep.id), 'held for', hold_time, 'ms.')
                                        
                                        # if you hold the note for the right time
                                        elif hold_time >= hit_note.hold_ms - 100:
                                            
                                            # show accuracy, same as before
                                            rank_shown, average_acc, rank_text = calc_note_data(accuracy_ms, accuracy_ranks, note_list, rank_text)
                                            
                                            if rank_tween != None:
                                                rank_tween.stop()
                                            
                                            rank_tween = tween.to(rank_text, 'scale', 0.7, 0.9, 'easeOutElastic')
                                            
                                            if rank_timer.counting:
                                                rank_timer.reset(True)
                                                
                                            rank_timer.start(0)
                                                
                                            print('Receptor', str(recep.id), 'held for', hold_time, 'ms.')
                                        
                                        # fix bug that leaves behind a hold sprite if you let go before it kills
                                        for hold in hit_note.hold_notes:
                                            if hold.alive:
                                                hold.kill()
                                        
                                        # disable holding (you're done now!)
                                        hit_note.holding = False
                                        
                                        # remove note from list
                                        while cur_hit_notes.count(hit_note) > 0:
                                            cur_hit_notes.remove(hit_note)
                        
                        # un-press receptor
                        recep.press(False)
                        
                        # turn off recep timer
                        if timer.counting:
                            timer.reset(True)
                            timer.dt = 0
            
            # handle pause menu
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    
                    # if the game is paused and not transitioning
                    if paused and can_interact:
                        
                        # iterate through each pause menu asset
                        for x in range(1, len(pause_menu_assets)):
                            asset = pause_menu_assets[x]
                            
                            # update assets
                            if asset.hovering:
                            
                                if intro_timer.counting:
                                    intro_timer.reset(True)
                                
                                # handle clicking on each button in the pause menu
                                
                                if x == 1: # resume
                                    paused = not paused
                                    current_song.pause(not current_song.playing)
                                    
                                elif x == 2: # restart
                                    started_from_here = True
                                    restarted = True
                                    transition.reset()
                                    # remove transition sound
                                    transition.play_transition_sound = False
                                    transition.start()
                                    
                                elif x == 3: # exit to freeplay (or list, depends on where it came from)
                                    started_from_here = True
                                    mode_to_switch = previous_mode
                                    restarted = False
                                    transition.reset()
                                    # remove transition sound
                                    transition.play_transition_sound = False
                                    transition.start()

                                    transition.play_menu_music = True
                                
                                elif x == 4: # exit to title
                                    started_from_here = True
                                    restarted = False
                                    mode_to_switch = 'title'
                                    transition.reset()
                                    # remove transition sound
                                    transition.play_transition_sound = False
                                    transition.start()

                                    transition.play_menu_music = True
 
        # update screen
        background.update(DISPLAYSURF)
        
        # update receptors
        for x in range(0, key_count):
            recep = receptors.get(f'receptor{x}')
            recep.update(x, recep_timers[x].dt, receptor_xy, DISPLAYSURF)
            
        # update notes
        if current_song.playing:
            # if playing, check for misses / update note pos
            for x in range(0, len(note_list)):
                note = note_list.get(f'note{x}')
                
                # if the note is actually supposed to be here
                if note != None:
                    if note.alive:
                        note.update(current_song, DISPLAYSURF)
                        
                        # check for misses. run the note kill check
                        killed = note.run_kill(current_song)
                        if killed:
                            
                            # kill hold notes
                            for hold in note.hold_notes:
                                hold.kill()
                            
                            # display miss (again, exact same as KEYDOWN)
                            accuracy_ranks[4] += 1
                            rank_shown, average_acc, rank_text = calc_note_data(None, accuracy_ranks, note_list, rank_text)
                            
                            if rank_tween != None:
                                rank_tween.stop()
                                
                            rank_tween = tween.to(rank_text, 'scale', 0.7, 0.9, 'easeOutElastic')
                            
                            if rank_shown != None:
                                rank_shown.alive = False
                            
                            if rank_timer.counting:
                                rank_timer.reset(True)
                                    
                            rank_timer.start(0)
                            
                            # add next note to list
                            if cur_note + 1 <= len(note_list) - 1:
                                cur_note += 1
        
        # if paused, still draw notes!
        elif not current_song.playing and paused:
            for x in range(0, len(note_list)):
                note = note_list.get(f'note{x}')
                
                if note != None:
                    if note.alive:
                        note.draw(DISPLAYSURF)
        
        # draw HUD assets
        
        # time bar
        if current_song.playing and current_song.conductor.dt >= 0:
            time_prog = current_song.conductor.dt / current_song.length
            
        pygame.draw.rect(DISPLAYSURF, (0, 0, 0), pygame.Rect(0, 715, 1280, 50)) # timebar background
        pygame.draw.rect(DISPLAYSURF, list(map(int, p_settings.get('Visual', 'timebar colour').split())), pygame.Rect(0, 715, 1280*time_prog, 50)) # timebar

        # rank display stuff
        if rank_shown != None:
            rank_shown.draw(DISPLAYSURF)
            
        if rank_text != None:
            rank_text.draw(DISPLAYSURF)
            
        if rank_timer.counting:
            rank_timer.count()
        
        # run counter. remove rank asset after certain amount of time
        if rank_timer.dt >= 1.2 and rank_timer.counting:
            rank_text.alive = False
            
            if rank_shown != None:
                rank_shown.alive = False
                
            rank_timer.reset(True)
        
        # update tween
        if rank_tween != None:
            rank_tween._update(global_clock.get_time() / 1500)
        
        # now for a bunch of display stuff.
        # basically just grabbing the config bool and drawing the data if the user wants.
        
        if p_settings.getboolean('Visual', 'show app data'):
            fps_box.draw(DISPLAYSURF)
            
        # always display accuracy
        acc_box.draw(DISPLAYSURF)
        
        if p_settings.getboolean('Debug', 'debug mode'):
            display_box.draw(DISPLAYSURF)
        
        if p_settings.getboolean('Visual', 'extra info'):
            note_dat_box.draw(DISPLAYSURF)
        
        if p_settings.getboolean('Visual', 'show app data'):
            fps_display(DISPLAYSURF, global_clock)
        
        # this checks config in the function itself, because it is also used in the chart editor.
        song_data_display(current_song, accuracy_ranks, average_acc, 'game', DISPLAYSURF)
        
        # update pause menu
        if paused:
            for x in range(0, len(pause_menu_assets)):
                asset = pause_menu_assets[x]
                
                if x == 0: # background
                    asset.draw(DISPLAYSURF)
                    
                else: # update buttons (button functions are handeled in pygame.MOUSEBUTTONDOWN
                    asset.update(event_list, DISPLAYSURF)
        
        # update transition tween
        if transition.transitioning:
            can_interact = False
            transition.update(DISPLAYSURF)
            transition.image.draw(DISPLAYSURF)
            tween.update(global_clock.get_time() / 1500)
        
        # run scene switch logic, depending on a bunch of variables        
        if transition.halfway and started_from_here:
        
            # if you are in list mode
            if list_mode:
                
                # if you hit the restart button in the pause menu
                if restarted:
                    gameplay_main(None, None, current_list, current_list_song - 1, True, previous_mode, transition)
                    
                else:
                    
                    # else if you need to load the next list song
                    if current_list_song < len(current_list) and mode_to_switch == None:
                        gameplay_main(None, None, current_list, current_list_song, False, previous_mode, transition)
                        
                    else:
                        # if list is finished, go back to list menu
                        main(mode_to_switch, transition)
            
            # else if not list mode
            else:
                
                # if you hit restart button, restart current song
                if restarted:
                    gameplay_main(song_to_load, chart_to_load, None, None, True, previous_mode, transition)
                
                # else, go back to freeplay
                else:
                    main(mode_to_switch, transition)
        
        # the only part of the game that checks the finished flag of the transition
        elif transition.finished:
            
            # start intro
            intro_running = True
            can_interact = True
            
            # if you restarted, don't run intro
            if restarted:
                intro_running = False
                current_song.start(-1)
                
            else:
                # play the intro tween
                intro_timer.start(0)
                play_intro(intro_assets, intro_tween, True, DISPLAYSURF)
            
            # put transition back
            transition.reset()
        
        # run the intro
        if intro_running:
            
            # update intro assets and tween
            for asset in intro_assets:
                asset.draw(DISPLAYSURF)
                tween.update(global_clock.get_time() / 1500)
            
            # run intro counter
            intro_timer.count()
            
            # if timer is halfway, run second half of transition
            if int(intro_timer.dt) == 2:
                intro_tween.stop()
                play_intro(intro_assets, intro_tween, False, DISPLAYSURF)
            
            # if intro over, allow everything
            if int(intro_timer.dt) == 4:
                intro_running = False
                current_song.start(-1)
                
        # when current song is finished
        if current_song.finished and not transition.transitioning:
            print('handling end song')
            restarted = False
            
            # if in list mode
            if list_mode:
            
                # if you finished the last song in the list, go back to list menu
                if current_list_song == len(list_to_load)-1:
                    transition.reset()
                    transition.start()
                    mode_to_switch = 'list'
                    started_from_here = True
                    transition.play_menu_music = True
                
                # else, load next song in list
                else:
                    transition.reset()
                    transition.start()
                    mode_to_switch = None
                    started_from_here = True
                
            else:
                
                # else, go back to freeplay menu
                transition.reset()
                transition.start()
                mode_to_switch = 'freeplay'
                started_from_here = True
                transition.play_menu_music = True
        
        # update display        
        pygame.display.update()
        
        # update window name with song name and stuff
        pygame.display.set_caption(display_string)
        

## load_json() function, used to run chart in editor
def load_json(mode, load_data):
    
    # parse the data to load
    song_to_load = load_data[0]
    chart_to_load = load_data[1]
    transition = load_data[2]
    
    # run correct function, pass song data through as variables
    if mode == 'game':
        gameplay_main(song_to_load, chart_to_load, False, None, transition)
    elif mode == 'chart':
        
        # check if song exists before it is loaded
        if os.path.exists(f'songs/{song_to_load}/{song_to_load}.mp3'):
            chart_main(song_to_load, chart_to_load, transition)

# run game if name is main!
if __name__ == '__main__': 
    
    # check if user has intro enabled / disabled. Run accordingly.
    if p_settings.getboolean('Extra', 'disable intro'):
        main('title', None)
        
    else:
        main('intro', None)
