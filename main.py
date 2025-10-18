import pygame
import sys
import math
import time
import random

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 900, 900

blue_wins = 0
orange_wins = 0
MAX_SCORE = 5
match_over = False
single_player = False

obstacles = []
OBSTACLE_SIZE = 20  # Try 15–30 for good visibility

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

	# Clear trails (fresh lists)
	p1_trail = []
	p2_trail = []

def main_menu():
	global blue_wins, orange_wins, match_over, single_player

	menu_running = True
	pygame.mixer.music.load("the_game_has_changed.mp3")
	pygame.mixer.music.play(-1)

	while menu_running:

		WIN.blit(background, (0, 0))
		show_message("TRON LIGHTCYCLES", "Press \"1\" for 1 Player or \"2\" for 2 Players")
		pygame.mixer.music.load("the_game_has_changed.mp3")
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
						reset_game()
					elif event.key == pygame.K_2:
						single_player = False
						blue_wins = 0
						orange_wins = 0
						match_over = False
						menu_running = False
						waiting = False
						reset_game()
					elif event.key == pygame.K_ESCAPE:
						pygame.quit()
						sys.exit()

def draw_tron_grid(surface, color, desired_spacing=40):
    surface.fill((0, 0, 16))  # dark navy background

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

# Screen setup
info = pygame.display.Info()
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
	total_width = blue_text.get_width() + orange_text.get_width() + 50
	start_x = WIDTH // 2 - total_width // 2

	WIN.blit(blue_text, (start_x, 10))
	WIN.blit(orange_text, (start_x + blue_text.get_width() + 50, 10))

def reset_game():
	global p1_pos, p2_pos, p1_dir, p2_dir, p1_trail, p2_trail, game_over

	reset_sprites()
	generate_obstacles()

	game_over = False

	# Redraw background clean
	WIN.fill(BLACK)
	pygame.display.update()

	countdown()

def generate_obstacles():
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

            # Avoid spawning near players
            if (abs(x - p1_pos[0]) < 3 * OBSTACLE_SIZE and abs(y - p1_pos[1]) < 3 * OBSTACLE_SIZE) or \
               (abs(x - p2_pos[0]) < 3 * OBSTACLE_SIZE and abs(y - p2_pos[1]) < 3 * OBSTACLE_SIZE):
                attempt += 1
                continue

            # Check for overlap with existing obstacles
            overlap = False
            for (ox, oy, osize) in obstacles:
                if x < ox + osize and x + size > ox and y < oy + osize and y + size > oy:
                    overlap = True
                    break

            if not overlap:
                obstacles.append((x, y, size))
                break

            attempt += 1

        # If we exceeded attempts, just skip this obstacle
        if attempt >= MAX_ATTEMPTS:
            break

def draw_obstacles():
    for (ox, oy, size) in obstacles:
        # Draw the black core
        core = pygame.Rect(ox, oy, size, size)
        pygame.draw.rect(WIN, BLACK, core)
        
        # Draw a thin white outline
        pygame.draw.rect(WIN, (255, 255, 255), core, 2)  # 2 px outline

def countdown():
	pygame.mixer.music.stop()
	pygame.mixer.music.load("clu.mp3")
	pygame.mixer.music.play(-1)
	font = pygame.font.Font(None, 100)
	for i in range(3, 0, -1):
		draw_tron_grid(WIN, TEAL)
		draw_obstacles()
		draw_sprites()
		show_message(str(i))
		pygame.display.update()
		pygame.time.delay(1000)

	# Flash "GO!"
	draw_tron_grid(WIN, TEAL)
	draw_obstacles()
	draw_sprites()
	show_message("GO!")
	pygame.display.update()
	pygame.time.delay(800)
	pygame.mixer.music.stop()
	pygame.mixer.music.load("derezzed.mp3")
	pygame.mixer.music.play(-1)

def blue_win():
	global game_over, match_over, win_color, win_text, blue_wins
	pygame.mixer.music.stop()
	derezzed_sound.play()
	game_over = True

	# --- Draw final collision frame before pausing ---
	WIN.fill(BLACK)
	draw_tron_grid(WIN, TEAL)
	draw_obstacles()
	for point in p1_trail:
		pygame.draw.rect(WIN, BLUE, (*point, BLOCK_SIZE, BLOCK_SIZE))
	for point in p2_trail:
		pygame.draw.rect(WIN, ORANGE, (*point, BLOCK_SIZE, BLOCK_SIZE))
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
		win_text = "BLUE TEAM WINS THE MATCH!"
	else:
		win_text = "BLUE TEAM WINS!"
		
	pygame.mixer.music.load("end_titles.mp3")
	pygame.mixer.music.play(-1)

def orange_win():
	global game_over, match_over, win_color, win_text, orange_wins
	pygame.mixer.music.stop()
	derezzed_sound.play()
	game_over = True

	# --- Draw final collision frame before pausing ---
	WIN.fill(BLACK)
	draw_tron_grid(WIN, TEAL)
	draw_obstacles()
	for point in p1_trail:
		pygame.draw.rect(WIN, BLUE, (*point, BLOCK_SIZE, BLOCK_SIZE))
	for point in p2_trail:
		pygame.draw.rect(WIN, ORANGE, (*point, BLOCK_SIZE, BLOCK_SIZE))
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
		win_text = "ORANGE TEAM WINS THE MATCH!"
	else:
		win_text = "ORANGE TEAM WINS!"
	pygame.mixer.music.load("end_titles.mp3")
	pygame.mixer.music.play(-1)

def ai_control():
    """Simple AI for orange bike that avoids walls, trails, and obstacles."""
    global p2_dir, last_turn_time_p2

    # Time limit to prevent over-turning
    current_time = pygame.time.get_ticks()
    if current_time - last_turn_time_p2 < turn_cooldown:
        return  # wait for cooldown before next turn

    possible_dirs = [dirs["UP"], dirs["DOWN"], dirs["LEFT"], dirs["RIGHT"]]

    def will_collide(pos, dir_vec):
        """Predict if moving forward will cause a collision."""
        x, y = pos
        dx, dy = dir_vec
        # Look 10 steps ahead
        for i in range(1, 12):
            nx = x + dx * i
            ny = y + dy * i
            if nx < 0 or nx >= WIDTH or ny < 0 or ny >= HEIGHT:
                return True
            if (int(nx), int(ny)) in p1_trail or (int(nx), int(ny)) in p2_trail:
                return True
            for (ox, oy, size) in obstacles:
                if ox <= nx <= ox + size and oy <= ny <= oy + size:
                    return True
        return False

    # Prefer current direction if safe
    if not will_collide(p2_pos, p2_dir):
        return

    # Otherwise, pick a safer turn
    safe_dirs = [d for d in possible_dirs if not will_collide(p2_pos, d)]
    if safe_dirs:
        new_dir = random.choice(safe_dirs)
        # Prevent turning back directly
        if (p2_dir == dirs["UP"] and new_dir == dirs["DOWN"]) or \
           (p2_dir == dirs["DOWN"] and new_dir == dirs["UP"]) or \
           (p2_dir == dirs["LEFT"] and new_dir == dirs["RIGHT"]) or \
           (p2_dir == dirs["RIGHT"] and new_dir == dirs["LEFT"]):
            pass
        else:
            p2_dir = new_dir
            last_turn_time_p2 = current_time

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

		# # Player 2 (Arrow keys)
		# if current_time - last_turn_time_p2 > turn_cooldown:
		# 	if keys[pygame.K_UP] and p2_dir != dirs["DOWN"]:
		# 		p2_dir = dirs["UP"]
		# 		last_turn_time_p2 = current_time
		# 	elif keys[pygame.K_DOWN] and p2_dir != dirs["UP"]:
		# 		p2_dir = dirs["DOWN"]
		# 		last_turn_time_p2 = current_time
		# 	elif keys[pygame.K_LEFT] and p2_dir != dirs["RIGHT"]:
		# 		p2_dir = dirs["LEFT"]
		# 		last_turn_time_p2 = current_time
		# 	elif keys[pygame.K_RIGHT] and p2_dir != dirs["LEFT"]:
		# 		p2_dir = dirs["RIGHT"]
		# 		last_turn_time_p2 = current_time
		if single_player == True:
			ai_control()
		else:
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
			orange_win()
		elif check_collision(tuple(map(int, p2_front)), p2_trail[:-1], p1_trail):
			blue_win()

		# --- Bike-to-Bike Collision Check (tight hitboxes) ---
		# Head-on collision threshold (fronts nearly touching)
		if math.hypot(p1_front[0] - p2_front[0], p1_front[1] - p2_front[1]) < bike_width * 0.25:
			pygame.mixer.music.stop()
			derezzed_sound.play()
			game_over = True

			# --- Draw final collision frame before pausing ---
			WIN.fill(BLACK)
			draw_tron_grid(WIN, TEAL)
			draw_obstacles()
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
				orange_win()

			elif (abs(p2_front[0] - p1_pos[0]) < hit_margin_x and abs(p2_front[1] - p1_pos[1]) < hit_margin_y):
				blue_win()

		# Check obstacle collisions
		# Player 1 obstacle collision
		for (ox, oy, size) in obstacles:
			if ox <= p1_front[0] <= ox + size and oy <= p1_front[1] <= oy + size:
				orange_win()
				break

		for (ox, oy, size) in obstacles:
			if ox <= p2_front[0] <= ox + size and oy <= p2_front[1] <= oy + size:
				blue_win()
				break




		# Draw layers
		WIN.fill(BLACK)
		draw_tron_grid(WIN, TEAL)

		WIN.fill(BLACK)
		draw_tron_grid(WIN, TEAL)
		for point in p1_trail:
			pygame.draw.rect(WIN, BLUE, (*point, BLOCK_SIZE, BLOCK_SIZE))
		for point in p2_trail:
			pygame.draw.rect(WIN, ORANGE, (*point, BLOCK_SIZE, BLOCK_SIZE))

		# Draw bikes
		draw_sprites()

		draw_obstacles()

		pygame.display.update()

	else:
	# --- GAME OVER STATE ---
		if match_over:
			show_message(win_text, "PRESS ESC TO QUIT", win_color)
			draw_scoreboard()
			pygame.display.update()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						main_menu()

		else:
			show_message(win_text, "PRESS SPACE TO PLAY AGAIN", win_color)
			draw_scoreboard()
			pygame.display.update()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_SPACE:
						reset_game()


pygame.quit()