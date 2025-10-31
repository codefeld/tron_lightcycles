import pygame
from pathlib import Path
import os
import random

from bike import Bike
# from obstacle import Obstacle
# from powerup import PowerUp

from functions import *

pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(5)

turn_channel = pygame.mixer.Channel(0)
derezz_channel = pygame.mixer.Channel(0)

turn_channel.set_volume(0.5)

derezz_channel.set_volume(1)

derezzed_sound_82_file = Path("music/derezzed_sound_82.mp3")
turn_sound_82_file = Path("music/turn_sound_82.mp3")
weve_got_company = Path("music/weve_got_company.mp3")
ring_game_and_escape1 = Path("music/ring_game_and_escape1.mp3")
ring_game_and_escape2 = Path("music/ring_game_and_escape2.mp3")
sea_of_simulation = Path("music/sea_of_simulation.mp3")
ending_titles1 = Path("music/ending_titles1.mp3")
ending_titles2 = Path("music/ending_titles2.mp3")
tower_music = Path("music/tower_music.mp3")
tron_theme = Path("music/tron_theme.mp3")

clu = Path("music/clu.mp3")
derezzed_sound_file = Path("music/derezzed_sound.mp3")
derezzed = Path("music/derezzed.mp3")
end_titles = Path("music/end_titles.mp3")
the_game_has_changed = Path("music/the_game_has_changed.mp3")
the_grid = Path("music/the_grid.mp3")
fall = Path("music/fall.mp3")
disc_wars = Path("music/disc_wars.mp3")
#armory = Path("music/armory.mp3")
recognizer = Path("music/recognizer.mp3")
rinzler = Path("music/rinzler.mp3")
adagio_for_tron = Path("music/adagio_for_tron.mp3")
arena = Path("music/arena.mp3")

init = Path("music/init.mp3")
infiltrator = Path("music/infiltrator.mp3")
a_question_of_trust = Path("music/a_question_of_trust.mp3")
expendable = Path("music/100%_expendable.mp3")
echoes = Path("music/echoes.mp3")
this_changes_everything = Path("music/this_changes_everything.mp3")
target_identified = Path("music/target_identified.mp3")
new_directive = Path("music/new_directive.mp3")
building_better_worlds = Path("music/building_better_worlds.mp3")
in_the_image_of = Path("music/in_the_image_of.mp3")
what_have_you_done = Path("music/what_have_you_done.mp3")
# daemonize = Path("music/daemonize.mp3")

game_music_legacy = [derezzed, fall, disc_wars, the_game_has_changed]
game_music_ares = [infiltrator, target_identified]

WIDTH, HEIGHT = 900, 900

themes = ["82", "LEGACY", "ARES"]

theme = random.choice(themes)

message_color = ""

# Colors
BLACK = (0, 0, 0)
GRID_COLOR = (20, 20, 30)
BLUE = (0, 255, 255)
ORANGE = (255, 150, 0)
RED = (255, 0, 0)
DARKER_RED = (200, 0, 0)
DARKEST_RED = (150, 0, 0)
LIGHT_RED = (255, 50, 50)
TEAL = (0, 180, 150)
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)

blue_wins = 0
orange_wins = 0
MAX_SCORE = 5
match_over = False
single_player = False

obstacles = []
OBSTACLE_SIZE = 20

game_time_offset = 0

# --- POWER-UP SYSTEM ---
powerups = []
POWERUP_SIZE = 20
last_powerup_spawn = 0
POWERUP_SPAWN_INTERVAL = 3000
first_powerup_spawned = False

# Screen setup
info = pygame.display.Info()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
background_82 = pygame.image.load("images/tron_82_grid_background.jpg")
background_82 = pygame.transform.scale(background_82, (WIDTH, HEIGHT))
legacy_background = pygame.image.load("images/tron_legacy_grid.png")
legacy_background = pygame.transform.scale(legacy_background, (WIDTH, HEIGHT))
ares_background = pygame.image.load("images/tron_ares_grid.png")
ares_background = pygame.transform.scale(ares_background, (WIDTH, HEIGHT))
pygame.display.set_caption("TRON: Lightcycles")

# Player settings
SPEED = 5
BLOCK_SIZE = 5

if derezzed_sound_file.exists():
	derezzed_sound = pygame.mixer.Sound("music/derezzed_sound.mp3")

if derezzed_sound_82_file.exists():
	derezzed_sound_82 = pygame.mixer.Sound("music/derezzed_sound_82.mp3")

if turn_sound_82_file.exists():
	turn_sound_82 = pygame.mixer.Sound("music/turn_sound_82.mp3")

dirs = {
	"UP": (0, -SPEED),
	"DOWN": (0, SPEED),
	"LEFT": (-SPEED, 0),
	"RIGHT": (SPEED, 0)
}

# Load sprites
# blue_bike_big = pygame.image.load("images/blue_cycle.png").convert_alpha()
# orange_bike_big = pygame.image.load("images/orange_cycle.png").convert_alpha()
# red_bike_big = pygame.image.load("images/red_cycle.png").convert_alpha()

# blue_bike_big = pygame.transform.flip(blue_bike_big, True, False)
# orange_bike_big = pygame.transform.flip(orange_bike_big, True, False)
# red_bike_big = pygame.transform.flip(red_bike_big, True, False)

# scale_factor = .05
# bike_width = int(blue_bike_big.get_width() * scale_factor)
# bike_height = int(blue_bike_big.get_height() * scale_factor)

# blue_bike_sprite = pygame.transform.scale(blue_bike_big, (bike_width, bike_height))
# orange_bike_sprite = pygame.transform.scale(orange_bike_big, (bike_width, bike_height))
# red_bike_sprite = pygame.transform.scale(red_bike_big, (bike_width, bike_height))

blue_82_big = pygame.image.load("images/blue_lightcycle_82.png").convert_alpha()
blue_82_big = pygame.transform.flip(blue_82_big, True, False)
orange_82_big = pygame.image.load("images/orange_lightcycle_82.png").convert_alpha()
orange_82_big = pygame.transform.flip(orange_82_big, True, False)

blue_legacy_big = pygame.image.load("images/blue_lightcycle_legacy.png").convert_alpha()
blue_legacy_big = pygame.transform.flip(blue_legacy_big, True, False)
orange_legacy_big = pygame.image.load("images/orange_lightcycle_legacy.png").convert_alpha()
orange_legacy_big = pygame.transform.flip(orange_legacy_big, True, False)

red_ares_big = pygame.image.load("images/red_lightcycle_ares.png").convert_alpha()
red_ares_big = pygame.transform.flip(red_ares_big, True, False)

scale_factor_82 = .05
width_82 = int(blue_82_big.get_width() * scale_factor_82)
height_82 = int(blue_82_big.get_height() * scale_factor_82)

legacy_scale_factor = .04
legacy_width = int(blue_legacy_big.get_width() * legacy_scale_factor)
legacy_height = int(blue_legacy_big.get_height() * legacy_scale_factor)

blue_82_sprite = pygame.transform.scale(blue_82_big, (width_82, height_82))
orange_82_sprite = pygame.transform.scale(orange_82_big, (width_82, height_82))

blue_legacy_sprite = pygame.transform.scale(blue_legacy_big, (legacy_width, legacy_height))
orange_legacy_sprite = pygame.transform.scale(orange_legacy_big, (legacy_width, legacy_height))

red_ares_sprite = pygame.transform.scale(red_ares_big, (legacy_width, legacy_height))

# Create bike instances
player1 = ""
player2 = ""

clock = pygame.time.Clock()

tron_font = os.path.join("fonts", "TRON.ttf")

transrobotics = os.path.join("fonts", "SFTransRobotics.ttf")

tr2n = os.path.join("fonts", "TR2N.ttf")

orbitron_bold = os.path.join("fonts", "Orbitron-Bold.ttf")
orbitron_regular = os.path.join("fonts", "Orbitron-Medium.ttf")

tron_ares = os.path.join("fonts", "TronAres.ttf")

turn_cooldown = 50 

if __name__ == '__main__':
	run_game()