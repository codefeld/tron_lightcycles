import pygame
import sys
import math
import time
import random

pygame.init()
pygame.mixer.init()

blue_wins = 0
orange_wins = 0

def blit_bike_with_front_at(screen, sprite, pos_back, dir_vector, back_margin=0):
	dx, dy = dir_vector

	# Compute angle (right = 0°)
	rad = math.atan2(-dy, dx)
	angle_deg = math.degrees(rad)

	# Original sprite dimensions
	w, h = sprite.get_width(), sprite.get_height()

	# Vector from back to center (unrotated)
	local_center = pygame.math.Vector2((w/2 - back_margin, 0))

	# Rotate that vector
	rotated_center = local_center.rotate(-angle_deg)

	# Compute where the sprite's center should be
	center_x = pos_back[0] + rotated_center.x
	center_y = pos_back[1] + rotated_center.y

	# Rotate the sprite
	rotated_sprite = pygame.transform.rotate(sprite, angle_deg)
	bike_rect = rotated_sprite.get_rect(center=(center_x, center_y))

	# Draw the rotated sprite
	screen.blit(rotated_sprite, bike_rect)

def get_front_pos(pos_back, dir_vector, sprite_width=None, back_margin=4):
	"""Compute front point automatically from sprite width."""
	dx, dy = dir_vector
	mag = math.hypot(dx, dy)
	if mag == 0:
		return pos_back
	nx, ny = dx / mag, dy / mag

	# Use sprite width if provided, otherwise default to 30
	length = (sprite_width or 30) - back_margin

	front_x = pos_back[0] + nx * length
	front_y = pos_back[1] + ny * length
	return [front_x, front_y]

def reset_sprites():
	global p1_pos, p2_pos, p1_dir, p2_dir, p1_trail, p2_trail

	pos = [
		[dirs["DOWN"], [WIDTH // 4, 35]],
		[dirs["DOWN"], [3 * WIDTH // 4, 35]],
		[dirs["UP"], [WIDTH // 4, HEIGHT - 35]],
		[dirs["UP"], [3 * WIDTH // 4, HEIGHT - 35]],
		[dirs["RIGHT"], [35, HEIGHT // 4]],
		[dirs["RIGHT"], [35, 3 * HEIGHT // 4]],
		[dirs["LEFT"], [WIDTH - 35, HEIGHT // 4]],
		[dirs["LEFT"], [WIDTH - 35, 3 * HEIGHT // 4]]
	]

	random_poses = random.sample(pos, 2)


	p1_dir = random_poses[0][0]
	p2_dir = random_poses[1][0]

	p1_pos = random_poses[0][1]
	p2_pos = random_poses[1][1]

	print("(" + str(p1_dir) + ", " + str(p1_pos) + ")")
	print("(" + str(p2_dir) + ", " + str(p2_pos) + ")")

	# Clear trails (fresh lists)
	p1_trail = []
	p2_trail = []

def draw_tron_grid(surface, color, spacing=40):
	surface.fill((0, 0, 16))  # dark navy background

	# width, height = surface.get_size()

	width = WIDTH
	height = HEIGHT

	# draw vertical lines
	for x in range(0, width, spacing):
		pygame.draw.line(surface, color, (x, 0), (x, height), 1)

	# draw horizontal lines
	for y in range(0, height, spacing):
		pygame.draw.line(surface, color, (0, y), (width, y), 1)

	# add a glowing effect by drawing blurred edges
	glow = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
	for i in range(3):
		alpha = 40 - i * 10
		glow_color = (color[0], color[1], color[2], alpha)
		for x in range(0, width, spacing):
			pygame.draw.line(glow, glow_color, (x, 0), (x, height), 3 + i)
		for y in range(0, height, spacing):
			pygame.draw.line(glow, glow_color, (0, y), (width, y), 3 + i)
	surface.blit(glow, (0, 0))

# Screen setup
info = pygame.display.Info()
# WIDTH, HEIGHT = info.current_w, info.current_h
WIDTH, HEIGHT = 900, 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
background = pygame.image.load("grid.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
pygame.display.set_caption("TRON Lightcycles")

# Colors
BLACK = (0, 0, 0)
GRID_COLOR = (20, 20, 30)
BLUE = (0, 255, 255)
ORANGE = (255, 150, 0)
TEAL = (0, 180, 150)

# Player settings
SPEED = 5
BLOCK_SIZE = 5

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
blue_bike = pygame.transform.scale(blue_bike_big, (bike_width, bike_height))
orange_bike = pygame.transform.scale(orange_bike_big, (bike_width, bike_height))
# print(bike_width)

# Player state
reset_sprites()

clock = pygame.time.Clock()
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

turn_cooldown = 50  # milliseconds
last_turn_time_p1 = 0
last_turn_time_p2 = 0

def show_message(text, subtext="", color=TEAL):
	# Render text surfaces
	title = font.render(text, True, color)
	if subtext != "":
		subtitle = small_font.render(subtext, True, (180, 180, 180))

	# Add padding around the text
	padding_x = 20
	padding_y = 15
	spacing = 10  # vertical space between title and subtitle

	# Determine box width & height based on text sizes
	if subtext != "":
		box_width = max(title.get_width(), subtitle.get_width()) + 2 * padding_x
		box_height = title.get_height() + subtitle.get_height() + 2 * padding_y + spacing
	else:
		box_width = title.get_width() + 2 * padding_x
		box_height = title.get_height() + 2 * padding_y# + spacing

	# Position box centered on screen
	box_x = WIDTH // 2 - box_width // 2
	box_y = HEIGHT // 2 - box_height // 2

	# Draw black background rectangle
	pygame.draw.rect(WIN, BLACK, (box_x, box_y, box_width, box_height))

	# Draw blue outline rectangle
	pygame.draw.rect(WIN, color, (box_x, box_y, box_width, box_height), 3)

	# Draw the text centered inside the box
	title_x = WIDTH // 2 - title.get_width() // 2
	title_y = box_y + padding_y

	if subtext != "":
		subtitle_x = WIDTH // 2 - subtitle.get_width() // 2
		subtitle_y = title_y + title.get_height() + spacing

	WIN.blit(title, (title_x, title_y))
	if subtext != "":
		WIN.blit(subtitle, (subtitle_x, subtitle_y))

	pygame.display.update()

def check_collision(pos, trail1, trail2):
	x, y = pos
	if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
		return True
	if pos in trail1 or pos in trail2:
		return True
	return False

def draw_sprites():

	p1_back = (p1_pos[0], p1_pos[1])
	blit_bike_with_front_at(WIN, blue_bike, p1_back, p1_dir, back_margin=4)

	p2_back = (p2_pos[0], p2_pos[1])
	blit_bike_with_front_at(WIN, orange_bike, p2_back, p2_dir, back_margin=4)

	draw_scoreboard()

def draw_scoreboard():
	blue_text = small_font.render(f"Blue: {blue_wins}", True, BLUE)
	orange_text = small_font.render(f"Orange: {orange_wins}", True, ORANGE)

	# Space them evenly at the top center
	total_width = blue_text.get_width() + orange_text.get_width() + 50  # spacing between texts
	start_x = WIDTH // 2 - total_width // 2

	WIN.blit(blue_text, (start_x, 10))
	WIN.blit(orange_text, (start_x + blue_text.get_width() + 50, 10))

def reset_game():
	global p1_pos, p2_pos, p1_dir, p2_dir, p1_trail, p2_trail, game_over

	reset_sprites()

	game_over = False

	# Redraw background clean
	WIN.fill(BLACK)
	pygame.display.update()

	countdown()

def countdown():
	pygame.mixer.music.stop()
	pygame.mixer.music.load("clu.mp3")
	pygame.mixer.music.play(-1)
	font = pygame.font.Font(None, 100)
	for i in range(3, 0, -1):
		draw_tron_grid(WIN, TEAL)
		show_message(str(i))
		draw_sprites()
		pygame.display.update()
		pygame.time.delay(1000)

	# Flash "GO!"
	draw_tron_grid(WIN, TEAL)
	show_message("GO!")
	draw_sprites()
	pygame.display.update()
	pygame.time.delay(800)
	pygame.mixer.music.stop()
	pygame.mixer.music.load("derezzed.mp3")
	pygame.mixer.music.play(-1)

# --- Start Screen ---
WIN.blit(background, (0, 0))
show_message("TRON LIGHTCYCLES", "Press SPACE to start")
pygame.mixer.music.load("the_game_has_changed.mp3")
pygame.mixer.music.play(-1)
waiting = True
while waiting:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
			countdown()
			waiting = False

running = True
game_over = False
while running:
	if not game_over:
		clock.tick(60)
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

		keys = pygame.key.get_pressed()

		current_time = pygame.time.get_ticks()

		# Player 1 (WASD)
		if current_time - last_turn_time_p1 > turn_cooldown:
			if keys[pygame.K_w] and p1_dir != dirs["DOWN"]:
				p1_dir = dirs["UP"]
				last_turn_time_p1 = current_time
			elif keys[pygame.K_s] and p1_dir != dirs["UP"]:
				p1_dir = dirs["DOWN"]
				last_turn_time_p1 = current_time
			elif keys[pygame.K_a] and p1_dir != dirs["RIGHT"]:
				p1_dir = dirs["LEFT"]
				last_turn_time_p1 = current_time
			elif keys[pygame.K_d] and p1_dir != dirs["LEFT"]:
				p1_dir = dirs["RIGHT"]
				last_turn_time_p1 = current_time

		# Player 2 (Arrow keys)
		if current_time - last_turn_time_p2 > turn_cooldown:
			if keys[pygame.K_UP] and p2_dir != dirs["DOWN"]:
				p2_dir = dirs["UP"]
				last_turn_time_p2 = current_time
			elif keys[pygame.K_DOWN] and p2_dir != dirs["UP"]:
				p2_dir = dirs["DOWN"]
				last_turn_time_p2 = current_time
			elif keys[pygame.K_LEFT] and p2_dir != dirs["RIGHT"]:
				p2_dir = dirs["LEFT"]
				last_turn_time_p2 = current_time
			elif keys[pygame.K_RIGHT] and p2_dir != dirs["LEFT"]:
				p2_dir = dirs["RIGHT"]
				last_turn_time_p2 = current_time


		# Move players
		p1_pos[0] += p1_dir[0]
		p1_pos[1] += p1_dir[1]
		p2_pos[0] += p2_dir[0]
		p2_pos[1] += p2_dir[1]

		# Add to trails
		p1_trail.append(tuple(p1_pos))
		p2_trail.append(tuple(p2_pos))

		# Collisions

		p1_front = get_front_pos(p1_pos, p1_dir, bike_width)
		p2_front = get_front_pos(p2_pos, p2_dir, bike_width)

		if check_collision(tuple(map(int, p1_front)), p1_trail[:-1], p2_trail):
			pygame.mixer.music.stop()
			derezzed_sound.play()
			game_over = True

			# --- Draw final collision frame before pausing ---
			WIN.fill(BLACK)
			draw_tron_grid(WIN, TEAL)
			for point in p1_trail:
				pygame.draw.rect(WIN, BLUE, (*point, BLOCK_SIZE, BLOCK_SIZE))
			for point in p2_trail:
				pygame.draw.rect(WIN, ORANGE, (*point, BLOCK_SIZE, BLOCK_SIZE))
			draw_sprites()
			draw_scoreboard()
			pygame.display.update()

			# Small pause to show the collision frame
			pygame.time.delay(1800)

			win_text = "ORANGE TEAM WINS!"
			win_color = ORANGE
			orange_wins += 1
			pygame.mixer.music.load("end_titles.mp3")
			pygame.mixer.music.play(-1)
		elif check_collision(tuple(map(int, p2_front)), p2_trail[:-1], p1_trail):
			pygame.mixer.music.stop()
			derezzed_sound.play()
			game_over = True

			# --- Draw final collision frame before pausing ---
			WIN.fill(BLACK)
			draw_tron_grid(WIN, TEAL)
			for point in p1_trail:
				pygame.draw.rect(WIN, BLUE, (*point, BLOCK_SIZE, BLOCK_SIZE))
			for point in p2_trail:
				pygame.draw.rect(WIN, ORANGE, (*point, BLOCK_SIZE, BLOCK_SIZE))
			draw_sprites()
			draw_scoreboard()
			pygame.display.update()

			# Small pause to show the collision frame
			pygame.time.delay(1800)

			win_text = "BLUE TEAM WINS!"
			win_color = BLUE
			blue_wins += 1
			pygame.mixer.music.load("end_titles.mp3")
			pygame.mixer.music.play(-1)

		# --- Bike-to-Bike Collision Check (tight hitboxes) ---
		# Head-on collision threshold (fronts nearly touching)
		if math.hypot(p1_front[0] - p2_front[0], p1_front[1] - p2_front[1]) < bike_width * 0.25:
			pygame.mixer.music.stop()
			derezzed_sound.play()
			game_over = True

			# --- Draw final collision frame before pausing ---
			WIN.fill(BLACK)
			draw_tron_grid(WIN, TEAL)
			for point in p1_trail:
				pygame.draw.rect(WIN, BLUE, (*point, BLOCK_SIZE, BLOCK_SIZE))
			for point in p2_trail:
				pygame.draw.rect(WIN, ORANGE, (*point, BLOCK_SIZE, BLOCK_SIZE))
			draw_sprites()
			draw_scoreboard()
			pygame.display.update()

			# Small pause to show the collision frame
			pygame.time.delay(1800)

			win_text = "DRAW!"
			win_color = TEAL
			pygame.mixer.music.load("end_titles.mp3")
			pygame.mixer.music.play(-1)
		else:
			# Side impacts: one front hitting another's body
			# (tighter box — about 40% of the sprite area)
			hit_margin_x = bike_width * 0.4
			hit_margin_y = bike_height * 0.4

			if (abs(p1_front[0] - p2_pos[0]) < hit_margin_x and abs(p1_front[1] - p2_pos[1]) < hit_margin_y):
				pygame.mixer.music.stop()
				derezzed_sound.play()
				game_over = True

				# --- Draw final collision frame before pausing ---
				WIN.fill(BLACK)
				draw_tron_grid(WIN, TEAL)
				for point in p1_trail:
					pygame.draw.rect(WIN, BLUE, (*point, BLOCK_SIZE, BLOCK_SIZE))
				for point in p2_trail:
					pygame.draw.rect(WIN, ORANGE, (*point, BLOCK_SIZE, BLOCK_SIZE))
				draw_sprites()
				draw_scoreboard()
				pygame.display.update()

				# Small pause to show the collision frame
				pygame.time.delay(1800)

				win_text = "ORANGE TEAM WINS!"
				win_color = ORANGE
				orange_wins += 1
				pygame.mixer.music.load("end_titles.mp3")
				pygame.mixer.music.play(-1)

			elif (abs(p2_front[0] - p1_pos[0]) < hit_margin_x and abs(p2_front[1] - p1_pos[1]) < hit_margin_y):
				pygame.mixer.music.stop()
				derezzed_sound.play()
				game_over = True

				# --- Draw final collision frame before pausing ---
				WIN.fill(BLACK)
				draw_tron_grid(WIN, TEAL)
				for point in p1_trail:
					pygame.draw.rect(WIN, BLUE, (*point, BLOCK_SIZE, BLOCK_SIZE))
				for point in p2_trail:
					pygame.draw.rect(WIN, ORANGE, (*point, BLOCK_SIZE, BLOCK_SIZE))
				draw_sprites()
				draw_scoreboard()
				pygame.display.update()

				# Small pause to show the collision frame
				pygame.time.delay(1800)

				win_text = "BLUE TEAM WINS!"
				win_color = BLUE
				blue_wins += 1
				pygame.mixer.music.load("end_titles.mp3")
				pygame.mixer.music.play(-1)



		# Draw layers
		WIN.fill(BLACK)
		draw_tron_grid(WIN, TEAL)

		WIN.fill(BLACK)
		draw_tron_grid(WIN, TEAL)
		for point in p1_trail:
			pygame.draw.rect(WIN, BLUE, (*point, BLOCK_SIZE, BLOCK_SIZE))
		for point in p2_trail:
			pygame.draw.rect(WIN, ORANGE, (*point, BLOCK_SIZE, BLOCK_SIZE))

		draw_scoreboard()

		# Draw bikes
		draw_sprites()

		# draw_scoreboard()

		pygame.display.update()

	else:
		# --- GAME OVER STATE ---
		# Keep showing the final map, don't clear the screen
		show_message(win_text, "PRESS SPACE TO PLAY AGAIN", win_color)
		draw_scoreboard()
		pygame.display.update()

		# Wait for restart or quit
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					reset_game()

pygame.quit()