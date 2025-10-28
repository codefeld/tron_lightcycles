import math
import pygame
import random
import sys
from main import *

from obstacle import Obstacle
from powerup import PowerUp


def blit_bike_with_front_at(screen, sprite, pos_back, dir_vector, back_margin=0):
	dx, dy = dir_vector

	# Compute angle (right = 0°)
	rad = math.atan2(-dy, dx)
	angle_deg = math.degrees(rad)

	# Original sprite dimensions
	w = sprite.get_width()

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
	# Compute front point automatically from sprite width.
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
	"""Reset bike positions and trails for a new round."""
	top_left = [dirs["DOWN"], [WIDTH // 4, 35]]
	top_right = [dirs["DOWN"], [3 * WIDTH // 4, 35]]
	bottom_left = [dirs["UP"], [WIDTH // 4, HEIGHT - 35]]
	bottom_right = [dirs["UP"], [3 * WIDTH // 4, HEIGHT - 35]]
	left_top = [dirs["RIGHT"], [35, HEIGHT // 4]]
	left_bottom = [dirs["RIGHT"], [35, 3 * HEIGHT // 4]]
	right_top = [dirs["LEFT"], [WIDTH - 35, HEIGHT // 4]]
	right_bottom = [dirs["LEFT"], [WIDTH - 35, 3 * HEIGHT // 4]]

	pos = [
		top_left,
		top_right,
		bottom_left,
		bottom_right,
		right_top,
		right_bottom,
		left_top,
		left_bottom
	]

	p1_start = random.choice(pos)
	pos.remove(p1_start)

	# Ensure bikes don't start in adjacent corners
	if p1_start == top_left:
		while True:
			p2_start = random.choice(pos)
			if p2_start != left_top:
				break
	elif p1_start == top_right:
		while True:
			p2_start = random.choice(pos)
			if p2_start != right_top:
				break
	elif p1_start == bottom_left:
		while True:
			p2_start = random.choice(pos)
			if p2_start != left_bottom:
				break
	elif p1_start == bottom_right:
		while True:
			p2_start = random.choice(pos)
			if p2_start != right_bottom:
				break
	elif p1_start == right_top:
		while True:
			p2_start = random.choice(pos)
			if p2_start != top_right:
				break
	elif p1_start == right_bottom:
		while True:
			p2_start = random.choice(pos)
			if p2_start != bottom_right:
				break
	elif p1_start == left_top:
		while True:
			p2_start = random.choice(pos)
			if p2_start != top_left:
				break
	elif p1_start == left_bottom:
		while True:
			p2_start = random.choice(pos)
			if p2_start != bottom_left:
				break

	# Set player 1 position and direction
	player1.dir = p1_start[0]
	player1.pos = p1_start[1]
	player1.reset_trail()
	player1.reset_status()

	# Set player 2 position and direction
	player2.dir = p2_start[0]
	player2.pos = p2_start[1]
	player2.reset_trail()
	player2.reset_status()

def main_menu():
	global blue_wins, orange_wins, match_over, single_player

	menu_running = True

	while menu_running:

		WIN.blit(background, (0, 0))
		show_message("TRON LIGHTCYCLES", "Press \"1\" for 1 Player or \"2\" for 2 Players")
		if armory.exists():
			pygame.mixer.music.load("armory.mp3")
			pygame.mixer.music.play(-1)
		waiting = True
		while waiting:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_1:
						single_player = True
						blue_wins = 0
						orange_wins = 0
						match_over = False
						menu_running = False
						waiting = False
						theme_menu()
						#reset_game()
					elif event.key == pygame.K_2:
						single_player = False
						blue_wins = 0
						orange_wins = 0
						match_over = False
						menu_running = False
						waiting = False
						theme_menu()
						#reset_game()
					elif event.key == pygame.K_ESCAPE:
						pygame.quit()
						sys.exit()

def theme_menu():
	global theme

	theme_menu_running = True

	while theme_menu_running:
		WIN.blit(background, (0, 0))
		show_message("SELECT A THEME", "Press \"1\" for \"'82\" or \"2\" for \"LEGACY\"")
		waiting = True
		while waiting:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_1:
						theme = "82"
						theme_menu_running = False
						waiting = False
						reset_game()
					elif event.key == pygame.K_2:
						theme = "LEGACY"
						theme_menu_running = False
						waiting = False
						reset_game()
					elif event.key == pygame.K_ESCAPE:
						pygame.quit()
						sys.exit()

def draw_tron_grid(surface, desired_spacing=40):
	if theme == "LEGACY":
		color = TEAL
		surface.fill((0, 0, 16))
	elif theme == "82":
		color = WHITE
		surface.fill((0, 0, 20))

	width = surface.get_width()
	height = surface.get_height()

	# Compute number of full cells that fit
	cols = width // desired_spacing
	rows = height // desired_spacing

	# Adjust spacing so grid fits exactly
	spacing_x = width / cols if cols > 0 else width
	spacing_y = height / rows if rows > 0 else height

	# Draw vertical lines including the final right line
	for i in range(cols + 1):
		x = int(i * spacing_x)
		pygame.draw.line(surface, color, (x, 0), (x, height), 1)
	# Ensure a final line at the very right edge
	pygame.draw.line(surface, color, (width - 1, 0), (width - 1, height), 1)

	# Draw horizontal lines including the final bottom line
	for j in range(rows + 1):
		y = int(j * spacing_y)
		pygame.draw.line(surface, color, (0, y), (width, y), 1)
	# Ensure a final line at the very bottom edge
	pygame.draw.line(surface, color, (0, height - 1), (width, height - 1), 1)

	glow = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
	for i in range(3):
		alpha = 40 - i * 10
		glow_color = (color[0], color[1], color[2], alpha)
		# Vertical glow lines
		for k in range(cols + 1):
			x = int(k * spacing_x)
			pygame.draw.line(glow, glow_color, (x, 0), (x, height), 3 + i)
		pygame.draw.line(glow, glow_color, (width - 1, 0), (width - 1, height), 3 + i)
		# Horizontal glow lines
		for l in range(rows + 1):
			y = int(l * spacing_y)
			pygame.draw.line(glow, glow_color, (0, y), (width, y), 3 + i)
		pygame.draw.line(glow, glow_color, (0, height - 1), (width, height - 1), 3 + i)

	surface.blit(glow, (0, 0))

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
		box_height = title.get_height() + 2 * padding_y

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

def segments_intersect(p1, p2, p3, p4):
	# Check if line segment p1->p2 intersects with line segment p3->p4
	def ccw(A, B, C):
		# Check if three points are in counter-clockwise order
		return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

	# Two segments intersect if the endpoints of one segment are on opposite sides of the other segment
	return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)

def check_trail_crossing(new_p1, new_p2, trail):
	# Check if a new trail segment (new_p1 -> new_p2) crosses any existing trail segments
	if len(trail) < 2:
		return False

	# Check against all consecutive segments in the trail
	for i in range(len(trail) - 1):
		trail_p1 = trail[i]
		trail_p2 = trail[i + 1]

		# Skip if checking against the immediate previous segment (would always intersect at endpoint)
		if trail_p2 == new_p1:
			continue

		if segments_intersect(new_p1, new_p2, trail_p1, trail_p2):
			return True

	return False

def check_collision(pos, trail1_set, trail2_set):
	x, y = pos
	if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
		return True
	if pos in trail1_set or pos in trail2_set:
		return True
	return False

def draw_sprites():
	"""Render both bikes on the screen."""
	player1.render(WIN, blit_bike_with_front_at, back_margin=4)
	player2.render(WIN, blit_bike_with_front_at, back_margin=4)

def draw_scoreboard():
	blue_text = small_font.render(f"Blue: {blue_wins}", True, BLUE)
	orange_text = small_font.render(f"Orange: {orange_wins}", True, ORANGE)

	# Space them evenly at the top center
	total_width = blue_text.get_width() + orange_text.get_width() + 50
	start_x = WIDTH // 2 - total_width // 2

	WIN.blit(blue_text, (start_x, 10))
	WIN.blit(orange_text, (start_x + blue_text.get_width() + 50, 10))

def reset_game():
	"""Reset the game for a new round."""
	global game_over, game_time_offset, last_powerup_spawn

	reset_sprites()
	clear_powerups()
	generate_obstacles()

	game_over = False

	# Redraw background clean
	WIN.fill(BLACK)
	pygame.display.update()

	countdown()
	game_time_offset = pygame.time.get_ticks()
	last_powerup_spawn = 0

def generate_obstacles():
	"""Generate random obstacles avoiding player positions."""
	global obstacles
	obstacles = []

	NUM_OBSTACLES = random.randint(5, 15)
	MAX_ATTEMPTS = 100  # Avoid infinite loops

	while len(obstacles) < NUM_OBSTACLES:
		attempt = 0
		while attempt < MAX_ATTEMPTS:
			size = random.randint(30, 60)
			x = random.randrange(0, WIDTH - size, OBSTACLE_SIZE)
			y = random.randrange(0, HEIGHT - size, OBSTACLE_SIZE)

			# Create temp obstacle to check for collisions
			temp_obstacle = Obstacle(x, y, size)

			# Avoid spawning near players (150 pixel margin)
			if temp_obstacle.is_near_position(player1.pos, 150) or \
			   temp_obstacle.is_near_position(player2.pos, 150):
				attempt += 1
				continue

			# Check for overlap with existing obstacles
			overlap = any(temp_obstacle.overlaps_with(obs) for obs in obstacles)

			if not overlap:
				obstacles.append(temp_obstacle)
				break

			attempt += 1

		# If we exceeded attempts, just skip this obstacle
		if attempt >= MAX_ATTEMPTS:
			break

def draw_obstacles():
	"""Render all obstacles on the screen."""
	for obstacle in obstacles:
		obstacle.render(WIN, theme)

def spawn_powerup():
	"""Spawn a new random power-up not overlapping obstacles or trails."""
	global powerups
	ptype = random.choice(PowerUp.TYPES)
	size = POWERUP_SIZE

	for _ in range(30):  # try 30 times
		x = random.randrange(0, WIDTH - size, POWERUP_SIZE)
		y = random.randrange(0, HEIGHT - size, POWERUP_SIZE)

		# Avoid obstacles
		overlap = any(obs.contains_point(x, y) for obs in obstacles)

		# Avoid trails - check if powerup overlaps with any trail positions
		if not overlap:
			for trail_pos in player1.trail + player2.trail:
				tx, ty = trail_pos
				# Check if powerup rectangle overlaps with trail block
				if (x < tx + BLOCK_SIZE and x + size > tx and
				    y < ty + BLOCK_SIZE and y + size > ty):
					overlap = True
					break

		if not overlap:
			powerups.append(PowerUp(x, y, size, ptype))
			break

def draw_powerups():
	"""Render all power-ups on the screen."""
	for powerup in powerups:
		powerup.render(WIN)

def clear_powerups():
	"""Remove all power-ups from the board."""
	global powerups
	powerups.clear()

def check_powerup_collision(pos, bike, current_time):
	"""Check if a bike hits a power-up and apply effect."""
	global powerups

	for pu in powerups[:]:
		if pu.contains_point(pos[0], pos[1]):
			pu.apply_effect(bike, current_time)
			powerups.remove(pu)

def check_trail_powerup_collisions(current_time):
	"""Check if any trails cross over power-ups."""
	global powerups

	for pu in powerups[:]:
		# Check if player1's trail crosses this power-up
		for trail_pos in player1.trail:
			tx, ty = trail_pos
			# Check if trail block overlaps with power-up
			if (tx < pu.x + pu.size and tx + BLOCK_SIZE > pu.x and
			    ty < pu.y + pu.size and ty + BLOCK_SIZE > pu.y):
				pu.apply_effect(player1, current_time)
				powerups.remove(pu)
				break

		# Check if still exists (might have been removed by player1)
		if pu not in powerups:
			continue

		# Check if player2's trail crosses this power-up
		for trail_pos in player2.trail:
			tx, ty = trail_pos
			# Check if trail block overlaps with power-up
			if (tx < pu.x + pu.size and tx + BLOCK_SIZE > pu.x and
			    ty < pu.y + pu.size and ty + BLOCK_SIZE > pu.y):
				pu.apply_effect(player2, current_time)
				powerups.remove(pu)
				break

def countdown():
	if clu.exists():
		pygame.mixer.music.stop()
		pygame.mixer.music.load("clu.mp3")
		pygame.mixer.music.play(-1)
	for i in range(3, 0, -1):
		draw_tron_grid(WIN)
		draw_obstacles()
		draw_powerups()
		draw_sprites()
		draw_scoreboard()
		show_message(str(i))
		pygame.display.update()
		pygame.time.delay(1000)

	# Flash "GO!"
	draw_tron_grid(WIN)
	draw_obstacles()
	draw_powerups()
	draw_sprites()
	draw_scoreboard()
	show_message("GO!")
	pygame.display.update()
	pygame.time.delay(800)
	game_song = random.choice(game_music)
	if game_song.exists():
		selected_song = str(game_song)
		pygame.mixer.music.stop()
		pygame.mixer.music.load(selected_song)
		pygame.mixer.music.play(-1)

def blue_win():
	global game_over, match_over, win_color, win_text, blue_wins
	if derezzed_sound_file.exists():
		pygame.mixer.music.stop()
		derezzed_sound.play()
	game_over = True

	# --- Draw final collision frame before pausing ---
	WIN.fill(BLACK)
	draw_tron_grid(WIN)
	for point in player1.trail:
		pygame.draw.rect(WIN, BLUE, (*point, BLOCK_SIZE, BLOCK_SIZE))
	for point in player2.trail:
		pygame.draw.rect(WIN, ORANGE, (*point, BLOCK_SIZE, BLOCK_SIZE))
	draw_obstacles()
	draw_powerups()
	draw_sprites()
	draw_scoreboard()
	pygame.display.update()

	# Small pause to show the collision frame
	pygame.time.delay(1800)

	blue_wins += 1
	win_color = BLUE
	# Check for match victory
	if blue_wins >= MAX_SCORE:
		match_over = True
		win_text = "TEAM BLUE WINS THE MATCH!"
		if end_titles.exists():
			pygame.mixer.music.load("end_titles.mp3")
			pygame.mixer.music.play(-1)
	else:
		win_text = "TEAM BLUE WINS!"
		if the_grid.exists():
			pygame.mixer.music.load("the_grid.mp3")
			pygame.mixer.music.play(-1)

def orange_win():
	global game_over, match_over, win_color, win_text, orange_wins
	if derezzed_sound_file.exists():
		pygame.mixer.music.stop()
		derezzed_sound.play()
	game_over = True

	# --- Draw final collision frame before pausing ---
	WIN.fill(BLACK)
	draw_tron_grid(WIN)
	for point in player1.trail:
		pygame.draw.rect(WIN, BLUE, (*point, BLOCK_SIZE, BLOCK_SIZE))
	for point in player2.trail:
		pygame.draw.rect(WIN, ORANGE, (*point, BLOCK_SIZE, BLOCK_SIZE))
	draw_obstacles()
	draw_powerups()
	draw_sprites()
	draw_scoreboard()
	pygame.display.update()

	# Small pause to show the collision frame
	pygame.time.delay(1800)

	orange_wins += 1
	win_color = ORANGE
	# Check for match victory
	if orange_wins >= MAX_SCORE:
		match_over = True
		win_text = "TEAM ORANGE WINS THE MATCH!"
		if single_player:
			if adagio_for_tron.exists():
				pygame.mixer.music.load("adagio_for_tron.mp3")
				pygame.mixer.music.play(-1)
		else:
			if end_titles.exists():
				pygame.mixer.music.load("end_titles.mp3")
				pygame.mixer.music.play(-1)
	else:
		win_text = "TEAM ORANGE WINS!"
		if single_player:
			if rinzler.exists():
				pygame.mixer.music.load("rinzler.mp3")
				pygame.mixer.music.play(-1)
		else:
			if the_grid.exists():
				pygame.mixer.music.load("the_grid.mp3")
				pygame.mixer.music.play(-1)

def ai_control(current_game_time):
	"""AI for orange bike that avoids collisions and seeks power-ups."""
	# Check turn cooldown
	if not player2.can_turn(current_game_time, turn_cooldown):
		return

	possible_dirs = [dirs["UP"], dirs["DOWN"], dirs["LEFT"], dirs["RIGHT"]]

	def will_collide(pos, dir_vec, steps=12):
		"""Predict if moving forward will cause a collision."""
		x, y = pos
		dx, dy = dir_vec
		# Look ahead specified steps
		for i in range(1, steps + 1):
			nx = x + dx * i
			ny = y + dy * i
			curr_pos = (int(nx), int(ny))
			if nx < 0 or nx >= WIDTH or ny < 0 or ny >= HEIGHT:
				return True
			# Use set-based collision detection (O(1) instead of O(n))
			if curr_pos in player1.trail_set or curr_pos in player2.trail_set:
				return True
			# Check obstacle collisions
			for obs in obstacles:
				if obs.contains_point(nx, ny):
					return True
		return False

	def get_direction_to_powerup(bike_pos, powerup):
		"""Calculate which direction moves toward a power-up."""
		bx, by = bike_pos
		px, py = powerup.x + powerup.size // 2, powerup.y + powerup.size // 2

		dx = px - bx
		dy = py - by

		# Determine primary and secondary directions
		directions = []
		if abs(dx) > abs(dy):
			# Horizontal movement is more important
			if dx > 0:
				directions.append(dirs["RIGHT"])
			else:
				directions.append(dirs["LEFT"])
			if dy > 0:
				directions.append(dirs["DOWN"])
			elif dy < 0:
				directions.append(dirs["UP"])
		else:
			# Vertical movement is more important
			if dy > 0:
				directions.append(dirs["DOWN"])
			else:
				directions.append(dirs["UP"])
			if dx > 0:
				directions.append(dirs["RIGHT"])
			elif dx < 0:
				directions.append(dirs["LEFT"])

		return directions

	# Find nearest power-up
	nearest_powerup = None
	min_distance = float('inf')
	if powerups:
		for powerup in powerups:
			px, py = powerup.x + powerup.size // 2, powerup.y + powerup.size // 2
			distance = math.hypot(px - player2.pos[0], py - player2.pos[1])
			if distance < min_distance:
				min_distance = distance
				nearest_powerup = powerup

	# Try to move toward power-up if one exists and is reasonably close
	if nearest_powerup and min_distance < 300:
		target_dirs = get_direction_to_powerup(player2.pos, nearest_powerup)

		# Check if we can safely move toward the power-up
		for target_dir in target_dirs:
			# Don't turn 180 degrees
			if (player2.dir == dirs["UP"] and target_dir == dirs["DOWN"]) or \
			   (player2.dir == dirs["DOWN"] and target_dir == dirs["UP"]) or \
			   (player2.dir == dirs["LEFT"] and target_dir == dirs["RIGHT"]) or \
			   (player2.dir == dirs["RIGHT"] and target_dir == dirs["LEFT"]):
				continue

			# Check if this direction is safe
			if not will_collide(player2.pos, target_dir, steps=15):
				player2.dir = target_dir
				player2.last_turn_time = current_game_time
				return

	# If current direction is safe, keep going
	if not will_collide(player2.pos, player2.dir):
		return

	# Otherwise, pick a safer turn (normal collision avoidance)
	safe_dirs = [d for d in possible_dirs if not will_collide(player2.pos, d)]
	if safe_dirs:
		new_dir = random.choice(safe_dirs)
		# Prevent turning back directly
		if (player2.dir == dirs["UP"] and new_dir == dirs["DOWN"]) or \
		   (player2.dir == dirs["DOWN"] and new_dir == dirs["UP"]) or \
		   (player2.dir == dirs["LEFT"] and new_dir == dirs["RIGHT"]) or \
		   (player2.dir == dirs["RIGHT"] and new_dir == dirs["LEFT"]):
			pass
		else:
			player2.dir = new_dir
			player2.last_turn_time = current_game_time

def step_move_player(bike, other_bike, effective_speed, sprite_width, back_margin=4):
	"""Move a bike and check for collisions."""
	if effective_speed <= 0:
		return False

	# Normalize direction vector
	mag = math.hypot(bike.dir[0], bike.dir[1])
	if mag == 0:
		return False
	nx, ny = bike.dir[0] / mag, bike.dir[1] / mag

	# front offset from back
	front_length = sprite_width - back_margin

	# fractional stepping ensures smooth motion at lower speeds
	remaining = effective_speed
	step_size = 1.0  # pixel increment
	while remaining > 0:
		step = min(step_size, remaining)
		remaining -= step

		# move the back point fractionally
		bike.pos[0] += nx * step
		bike.pos[1] += ny * step

		# compute current front position
		fx = bike.pos[0] + nx * front_length
		fy = bike.pos[1] + ny * front_length
		front_int = (int(fx), int(fy))

		# Also check middle and back positions to prevent phasing through trails when turning
		back_int = (int(bike.pos[0]), int(bike.pos[1]))
		mid_x = bike.pos[0] + nx * (front_length / 2)
		mid_y = bike.pos[1] + ny * (front_length / 2)
		mid_int = (int(mid_x), int(mid_y))

		# collision test (using sets for O(1) lookup) - check front, middle, and back
		for check_pos in [front_int, mid_int, back_int]:
			if check_collision(check_pos, bike.trail_set, other_bike.trail_set):
				# Determine winner based on which bike collided
				if bike == player1:
					orange_win()
				else:
					blue_win()
				return True

		# Check obstacle collisions at front, middle, and back
		for obs in obstacles:
			if obs.contains_point(fx, fy) or obs.contains_point(mid_x, mid_y) or obs.contains_point(bike.pos[0], bike.pos[1]):
				if bike == player1:
					orange_win()
				else:
					blue_win()
				return True

		# Add trail points for rendering and collision detection
		new_pos = (int(bike.pos[0]), int(bike.pos[1]))
		bike.add_trail_point(new_pos)

	return False

def run_game():
	"""Main game loop."""
	global game_over, win_text, win_color, game_time_offset, last_powerup_spawn

	# --- Start Screen ---
	WIN.blit(background, (0, 0))
	main_menu()
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

			current_time = pygame.time.get_ticks() - game_time_offset

			if current_time - last_powerup_spawn > POWERUP_SPAWN_INTERVAL:
				spawn_powerup()
				last_powerup_spawn = current_time

			# Player 1 (WASD) — Disable turning if frozen
			if not player1.is_frozen(current_time):
				if player1.can_turn(current_time, turn_cooldown):
					if keys[pygame.K_w] and player1.dir != dirs["DOWN"]:
						player1.dir = dirs["UP"]
						player1.last_turn_time = current_time
					elif keys[pygame.K_s] and player1.dir != dirs["UP"]:
						player1.dir = dirs["DOWN"]
						player1.last_turn_time = current_time
					elif keys[pygame.K_a] and player1.dir != dirs["RIGHT"]:
						player1.dir = dirs["LEFT"]
						player1.last_turn_time = current_time
					elif keys[pygame.K_d] and player1.dir != dirs["LEFT"]:
						player1.dir = dirs["RIGHT"]
						player1.last_turn_time = current_time

			# Player 2 (Arrows or AI) — Disable turning if frozen
			if not player2.is_frozen(current_time):
				if single_player:
					ai_control(current_time)
				if player2.can_turn(current_time, turn_cooldown):
					if keys[pygame.K_UP] and player2.dir != dirs["DOWN"]:
						player2.dir = dirs["UP"]
						player2.last_turn_time = current_time
					elif keys[pygame.K_DOWN] and player2.dir != dirs["UP"]:
						player2.dir = dirs["DOWN"]
						player2.last_turn_time = current_time
					elif keys[pygame.K_LEFT] and player2.dir != dirs["RIGHT"]:
						player2.dir = dirs["LEFT"]
						player2.last_turn_time = current_time
					elif keys[pygame.K_RIGHT] and player2.dir != dirs["LEFT"]:
						player2.dir = dirs["RIGHT"]
						player2.last_turn_time = current_time

			# Get effective speeds considering status effects
			effective_speed_p1 = player1.get_effective_speed(SPEED, current_time)
			effective_speed_p2 = player2.get_effective_speed(SPEED, current_time)

			# Move both bikes
			collided1 = step_move_player(player1, player2, effective_speed_p1, bike_width, back_margin=4)
			if not collided1:
				# Move player 2 (only if game not already ended)
				collided2 = step_move_player(player2, player1, effective_speed_p2, bike_width, back_margin=4)

			p1_front = player1.get_front_pos(bike_width)
			p2_front = player2.get_front_pos(bike_width)

			# --- Bike-to-Bike Collision Check (tight hitboxes) ---
			# Head-on collision threshold (fronts nearly touching)
			if math.hypot(p1_front[0] - p2_front[0], p1_front[1] - p2_front[1]) < bike_width * 0.25:
				if derezzed_sound_file.exists():
					pygame.mixer.music.stop()
					derezzed_sound.play()
				game_over = True

				# --- Draw final collision frame before pausing ---
				WIN.fill(BLACK)
				draw_tron_grid(WIN)
				for point in player1.trail:
					pygame.draw.rect(WIN, BLUE, (*point, BLOCK_SIZE, BLOCK_SIZE))
				for point in player2.trail:
					pygame.draw.rect(WIN, ORANGE, (*point, BLOCK_SIZE, BLOCK_SIZE))
				draw_obstacles()
				draw_powerups()
				draw_sprites()
				draw_scoreboard()
				pygame.display.update()

				# Small pause to show the collision frame
				pygame.time.delay(1800)

				win_text = "DRAW!"
				win_color = TEAL
				if arena.exists():
					pygame.mixer.music.load("arena.mp3")
					pygame.mixer.music.play(-1)
			else:
				# Side impacts: one front hitting another's body
				# (tighter box — about 40% of the sprite area)
				hit_margin_x = bike_width * 0.4
				hit_margin_y = bike_height * 0.4

				if (abs(p1_front[0] - player2.pos[0]) < hit_margin_x and abs(p1_front[1] - player2.pos[1]) < hit_margin_y):
					orange_win()

				elif (abs(p2_front[0] - player1.pos[0]) < hit_margin_x and abs(p2_front[1] - player1.pos[1]) < hit_margin_y):
					blue_win()

			# --- Power-up collisions ---
			check_powerup_collision(p1_front, player1, current_time)
			check_powerup_collision(p2_front, player2, current_time)
			check_trail_powerup_collisions(current_time)

			# Render everything
			WIN.fill(BLACK)
			draw_tron_grid(WIN)
			for point in player1.trail:
				pygame.draw.rect(WIN, BLUE, (*point, BLOCK_SIZE, BLOCK_SIZE))
			for point in player2.trail:
				pygame.draw.rect(WIN, ORANGE, (*point, BLOCK_SIZE, BLOCK_SIZE))
			draw_obstacles()
			draw_powerups()
			draw_sprites()
			draw_scoreboard()
			pygame.display.update()

		else:
			# --- GAME OVER STATE ---
			if match_over:
				show_message(win_text, "Press ESC to quit", win_color)
				draw_scoreboard()
				pygame.display.update()

				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						running = False
					elif event.type == pygame.KEYDOWN:
						if event.key == pygame.K_ESCAPE:
							main_menu()

			else:
				show_message(win_text, "Press SPACE to continue", win_color)
				draw_scoreboard()
				pygame.display.update()

				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						running = False
					elif event.type == pygame.KEYDOWN:
						if event.key == pygame.K_SPACE:
							reset_game()
						elif event.key == pygame.K_ESCAPE:
							main_menu()

	pygame.quit()