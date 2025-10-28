import pygame
import sys
import math
import random
from pathlib import Path

from bike import Bike
from obstacle import Obstacle
from powerup import PowerUp

from functions import *

pygame.init()
pygame.mixer.init()

clu = Path("clu.mp3")
derezzed_sound_file = Path("derezzed_sound.mp3")
derezzed = Path("derezzed.mp3")
end_titles = Path("end_titles.mp3")
the_game_has_changed = Path("the_game_has_changed.mp3")
the_grid = Path("the_grid.mp3")
fall = Path("fall.mp3")
disc_wars = Path("disc_wars.mp3")
armory = Path("armory.mp3")
rinzler = Path("rinzler.mp3")
adagio_for_tron = Path("adagio_for_tron.mp3")
arena = Path("arena.mp3")
game_music = [derezzed, fall, disc_wars, the_game_has_changed]

WIDTH, HEIGHT = 900, 900

# Colors
BLACK = (0, 0, 0)
GRID_COLOR = (20, 20, 30)
BLUE = (0, 255, 255)
ORANGE = (255, 150, 0)
TEAL = (0, 180, 150)

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
POWERUP_SPAWN_INTERVAL = 5000  # spawn every ~5 seconds
first_powerup_spawned = False

# Screen setup
info = pygame.display.Info()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
background = pygame.image.load("grid.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
pygame.display.set_caption("TRON Lightcycles")

# Player settings
SPEED = 5
BLOCK_SIZE = 5

if derezzed_sound_file.exists():
	derezzed_sound = pygame.mixer.Sound("derezzed_sound.mp3")

dirs = {
	"UP": (0, -SPEED),
	"DOWN": (0, SPEED),
	"LEFT": (-SPEED, 0),
	"RIGHT": (SPEED, 0)
}

# Load sprites
blue_bike_big = pygame.image.load("blue_cycle.png").convert_alpha()
orange_bike_big = pygame.image.load("orange_cycle.png").convert_alpha()
blue_bike_big = pygame.transform.flip(blue_bike_big, True, False)
orange_bike_big = pygame.transform.flip(orange_bike_big, True, False)
scale_factor = .05
bike_width = int(blue_bike_big.get_width() * scale_factor)
bike_height = int(blue_bike_big.get_height() * scale_factor)
blue_bike_sprite = pygame.transform.scale(blue_bike_big, (bike_width, bike_height))
orange_bike_sprite = pygame.transform.scale(orange_bike_big, (bike_width, bike_height))

# Create bike instances
player1 = Bike(blue_bike_sprite, BLUE, "Blue")
player2 = Bike(orange_bike_sprite, ORANGE, "Orange")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

turn_cooldown = 50

if __name__ == '__main__':
	run_game()