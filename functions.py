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

	# pos_back is the top-left of the trail block, so offset to center of 5x5 block
	# BLOCK_SIZE is 5, so center is at +2 (accounting for 0-indexed pixels: 0,1,2,3,4 -> center at 2)
	back_center_x = pos_back[0] + 2
	back_center_y = pos_back[1] + 2

	# Vector from back to center (unrotated)
	local_center = pygame.math.Vector2((w/2 - back_margin, 0))

	# Rotate that vector
	rotated_center = local_center.rotate(-angle_deg)

	# Compute where the sprite's center should be
	center_x = back_center_x + rotated_center.x
	center_y = back_center_y + rotated_center.y

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
	global p1_wins, p2_wins, match_over, single_player, font, small_font, message_color, current_track

	if theme == "82":
		font = pygame.font.Font(tron_font, 50)
		small_font = pygame.font.Font(transrobotics, 20)
		message_color = (255, 255, 255)
	elif theme == "LEGACY":
		font = pygame.font.Font(tr2n, 75)
		small_font = pygame.font.Font(orbitron_regular, 20)
		message_color = (0, 255, 255)
	elif theme == "ARES":
		font = pygame.font.Font(tron_ares, 50)
		small_font = pygame.font.Font(orbitron_regular, 20)
		message_color = (255, 0, 0)
	elif theme == "RECONFIGURED":
		font = pygame.font.Font(pixel_font, 50)
		small_font = pygame.font.Font(pixel_font, 15)
		message_color = (0, 255, 0)
	elif theme == "UPRISING":
		font = pygame.font.Font(tr2n, 75)
		small_font = pygame.font.Font(orbitron_regular, 20)
		message_color = (0, 255, 255)

	menu_running = True
	# Flag to track if menu music has been initialized

	while menu_running:

		if theme == "82":
			WIN.blit(background_82, (0, 0))
			if tron_theme.exists() and current_track != str(tron_theme):
				pygame.mixer.music.load("music/tron_theme.mp3")
				pygame.mixer.music.play(-1)
				pygame.mixer.music.set_volume(1)
				current_track = str(tron_theme)
		elif theme == "LEGACY":
			WIN.blit(legacy_background, (0, 0))
			if current_track not in [str(song) for song in menu_music_legacy]:
				menu_song = random.choice(menu_music_legacy)
				selected_song = str(menu_song)
				pygame.mixer.music.stop()
				pygame.mixer.music.load(selected_song)
				pygame.mixer.music.play(-1)
				pygame.mixer.music.set_volume(1)
				current_track = selected_song
		elif theme == "ARES":
			WIN.blit(ares_background, (0, 0))
			if current_track not in [str(song) for song in menu_music_ares]:
				menu_song = random.choice(menu_music_ares)
				selected_song = str(menu_song)
				pygame.mixer.music.stop()
				pygame.mixer.music.load(selected_song)
				pygame.mixer.music.play(-1)
				pygame.mixer.music.set_volume(0.75)
				current_track = selected_song
		elif theme == "RECONFIGURED":
			WIN.blit(reconfigured_background, (0, 0))
			if current_track not in [str(song) for song in menu_music_reconfigured]:
				menu_song = random.choice(menu_music_reconfigured)
				selected_song = str(menu_song)
				pygame.mixer.music.stop()
				pygame.mixer.music.load(selected_song)
				pygame.mixer.music.play(-1)
				pygame.mixer.music.set_volume(0.75)
				current_track = selected_song
		elif theme == "UPRISING":
			WIN.blit(legacy_background, (0, 0))
			if current_track not in [str(song) for song in menu_music_uprising]:
				menu_song = random.choice(menu_music_uprising)
				selected_song = str(menu_song)
				pygame.mixer.music.stop()
				pygame.mixer.music.load(selected_song)
				pygame.mixer.music.play(-1)
				pygame.mixer.music.set_volume(1)
				current_track = selected_song
		# Custom title screen rendering with large "TRON" on separate line
		# For 82 theme, use tron_logo.png image; for others, use text
		if theme == "82":
			# Load and display the TRON logo image
			tron_logo_path = Path("images/tron_logo.png")
			if tron_logo_path.exists():
				tron_logo_img = pygame.image.load("images/tron_logo.png")
				# Scale the logo to a reasonable size (e.g., width of 400px)
				lightcycle_img = pygame.image.load("images/lightcycle_text.png")
				logo_width = 600
				logo_height = int(tron_logo_img.get_height() * (logo_width / tron_logo_img.get_width()))
				tron_title = pygame.transform.scale(tron_logo_img, (logo_width, logo_height))
				subtitle_width = 550
				subtitle_height = int(lightcycle_img.get_height() * (subtitle_width / lightcycle_img.get_width()))
				lightcycles_title = pygame.transform.scale(lightcycle_img, (subtitle_width, subtitle_height))
		elif theme == "RECONFIGURED":
			# Load and display the TRON logo image
			tron_logo_path = Path("images/tron_reconfigured_logo.png")
			if tron_logo_path.exists():
				tron_logo_img = pygame.image.load("images/tron_reconfigured_logo.png")
				logo_width = 650
				logo_height = int(tron_logo_img.get_height() * (logo_width / tron_logo_img.get_width()))
				tron_title = pygame.transform.scale(tron_logo_img, (logo_width, logo_height))
		elif theme == "UPRISING":
			# Load and display the TRON logo image
			tron_logo_path = Path("images/tron_uprising_logo.png")
			if tron_logo_path.exists():
				tron_logo_img = pygame.image.load("images/tron_uprising_logo.png")
				# Scale the logo to a reasonable size (e.g., width of 400px)
				lightcycle_img = pygame.image.load("images/lightcycle_text_legacy.png")
				logo_width = 600
				logo_height = int(tron_logo_img.get_height() * (logo_width / tron_logo_img.get_width()))
				tron_title = pygame.transform.scale(tron_logo_img, (logo_width, logo_height))
				subtitle_width = 550
				subtitle_height = int(lightcycle_img.get_height() * (subtitle_width / lightcycle_img.get_width()))
				lightcycles_title = pygame.transform.scale(lightcycle_img, (subtitle_width, subtitle_height))
			else:
				# Fallback to text if image doesn't exist
				large_font = pygame.font.Font(tron_font, 100)
				tron_title = large_font.render("TRON", True, message_color)
		elif theme == "LEGACY":
			large_font = pygame.font.Font(tr2n, 200)
			tron_title = large_font.render("TRON", True, message_color)
			lightcycle_img = pygame.image.load("images/lightcycle_text_legacy.png")
			subtitle_width = 550
			subtitle_height = int(lightcycle_img.get_height() * (subtitle_width / lightcycle_img.get_width()))
			lightcycles_title = pygame.transform.scale(lightcycle_img, (subtitle_width, subtitle_height))
		elif theme == "ARES":
			large_font = pygame.font.Font(tron_ares, 150)
			tron_title = large_font.render("TRON", True, message_color)

		# Render other title components
		if theme == "RECONFIGURED":
			title_font = pygame.font.Font(pixel_font, 25)
			lightcycles_title = font.render("L1GHTCYCL3S", True, message_color)
		elif theme != "82" and theme != "UPRISING" and theme != "LEGACY":
			lightcycles_title = font.render("LIGHTCYCLES", True, message_color)

		instruction_text = small_font.render("Press \"1\" for 1 Player or \"2\" for 2 Players", True, (180, 180, 180))

		# Calculate positions (centered)
		tron_x = (WIDTH - tron_title.get_width()) // 2
		tron_y = HEIGHT // 3

		if theme == "LEGACY" or theme == "UPRISING":
			lightcycles_x = (WIDTH - lightcycles_title.get_width()) // 2 + 25
		elif theme == "RECONFIGURED":
			lightcycles_x = (WIDTH - lightcycles_title.get_width()) // 2 + 25
		else:
			lightcycles_x = (WIDTH - lightcycles_title.get_width()) // 2
			
		if theme == "82":
			lightcycles_y = tron_y + tron_title.get_height() - 120
		elif theme == "LEGACY":
			lightcycles_y = tron_y + tron_title.get_height() - 30
		elif theme == "ARES":
			lightcycles_y = tron_y + tron_title.get_height() + 20
		elif theme == "RECONFIGURED":
			lightcycles_y = tron_y + tron_title.get_height() + 30
		elif theme == "UPRISING":
			lightcycles_y = tron_y + tron_title.get_height() + 20

		instruction_x = (WIDTH - instruction_text.get_width()) // 2
		if theme == "82":
			instruction_y = lightcycles_y + lightcycles_title.get_height() - 100
		elif theme == "UPRISING":
			instruction_y = lightcycles_y + lightcycles_title.get_height() + 50
		elif theme == "LEGACY":
			instruction_y = lightcycles_y + lightcycles_title.get_height() + 60
		else:
			instruction_y = lightcycles_y + lightcycles_title.get_height() + 30

		# Draw the title elements
		WIN.blit(tron_title, (tron_x, tron_y))
		WIN.blit(lightcycles_title, (lightcycles_x, lightcycles_y))
		WIN.blit(instruction_text, (instruction_x, instruction_y))
		pygame.display.flip()
		waiting = True
		while waiting:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_1:
						single_player = True
						p1_wins = 0
						p2_wins = 0
						match_over = False
						menu_running = False
						waiting = False
						difficulty_menu()
					elif event.key == pygame.K_2:
						single_player = False
						p1_wins = 0
						p2_wins = 0
						match_over = False
						menu_running = False
						waiting = False
						difficulty_menu()
					elif event.key == pygame.K_ESCAPE:
						pygame.quit()
						sys.exit()

def difficulty_menu():
	global SPEED, BLOCK_SIZE, difficulty

	difficulty_menu_running = True

	while difficulty_menu_running:
		if theme == "82":
			WIN.blit(background_82, (0, 0))
		elif theme == "LEGACY":
			WIN.blit(legacy_background, (0, 0))
		elif theme == "ARES":
			WIN.blit(ares_background, (0, 0))
		elif theme == "RECONFIGURED":
			WIN.blit(reconfigured_background, (0, 0))
		elif theme == "UPRISING":
			WIN.blit(legacy_background, (0, 0))
		show_message("CHOOSE DIFFICULTY", "Press \"1\" for \"NORMAL\" or \"2\" for \"CHALLENGE\"", message_color)
		waiting = True
		while waiting:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_1:
						difficulty = "NORMAL"
						SPEED = 6
						BLOCK_SIZE = 5
						difficulty_menu_running = False
						waiting = False
						theme_menu()
					elif event.key == pygame.K_2:
						difficulty = "CHALLENGE"
						SPEED = 8
						BLOCK_SIZE = 5
						difficulty_menu_running = False
						waiting = False
						theme_menu()
					elif event.key == pygame.K_ESCAPE:
						difficulty_menu_running = False
						waiting = False
						main_menu()

def theme_menu():
	global theme, BLUE, ORANGE, WHITE, font, small_font

	theme_menu_running = True

	while theme_menu_running:
		if theme == "82":
			WIN.blit(background_82, (0, 0))
		elif theme == "LEGACY":
			WIN.blit(legacy_background, (0, 0))
		elif theme == "ARES":
			WIN.blit(ares_background, (0, 0))
		elif theme == "RECONFIGURED":
			WIN.blit(reconfigured_background, (0, 0))
		if theme == "RECONFIGURED":
			show_message("SELECT A THEME", "Press \"1\" for \"82\", \"2\" for \"LEGACY\", \"3\" for \"ARES\", or \"R\" for RECONFIGURED", message_color)
		elif theme == "UPRISING":
			show_message("SELECT A THEME", "Press \"1\" for \"82\", \"2\" for \"LEGACY\", \"3\" for \"ARES\", or \"U\" for UPRISING", message_color)
		else:
			show_message("SELECT A THEME", "Press \"1\" for \"82\", \"2\" for \"LEGACY\", or \"3\" for \"ARES\"", message_color)
		waiting = True
		while waiting:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_1:
						theme = "82"
						BLUE = (0, 106, 203)
						ORANGE = (255, 126, 0)
						WHITE = (200, 200, 200)
						font = pygame.font.Font(tron_font, 50)
						small_font = pygame.font.Font(transrobotics, 20)
						theme_menu_running = False
						waiting = False
						reset_game()
					elif event.key == pygame.K_2:
						theme = "LEGACY"
						BLUE = (2, 255, 255)
						ORANGE = (254, 148, 0)
						WHITE = (255, 255, 255)
						font = pygame.font.Font(tr2n, 75)
						small_font = pygame.font.Font(orbitron_regular, 20)
						theme_menu_running = False
						waiting = False
						reset_game()
					elif event.key == pygame.K_3:
						theme = "ARES"
						BLUE = (0, 255, 255)
						WHITE = (255, 255, 255)
						font = pygame.font.Font(tron_ares, 50)
						small_font = pygame.font.Font(orbitron_regular, 20)
						theme_menu_running = False
						waiting = False
						reset_game()
					elif event.key == pygame.K_r:
						theme = "RECONFIGURED"
						WHITE = (255, 255, 255)
						font = pygame.font.Font(pixel_font, 50)
						small_font = pygame.font.Font(pixel_font, 15)
						theme_menu_running = False
						waiting = False
						reset_game()
					elif event.key == pygame.K_u:
						theme = "UPRISING"
						BLUE = (2, 255, 255)
						ORANGE = (254, 148, 0)
						WHITE = (255, 255, 255)
						font = pygame.font.Font(tr2n, 75)
						small_font = pygame.font.Font(orbitron_regular, 20)
						theme_menu_running = False
						waiting = False
						reset_game()
					elif event.key == pygame.K_ESCAPE:
						theme_menu_running = False
						waiting = False
						difficulty_menu()

def draw_squircle(surface, center_x, center_y, size, color, roundness=0.7):
	"""Draw a rounded rectangle."""
	# Calculate corner radius based on roundness parameter
	# roundness controls how rounded the corners are (0 = square, 1 = very round)
	corner_radius = int(size * roundness * 0.5)

	# Calculate top-left position from center
	x = center_x - size / 2
	y = center_y - size / 2

	# Create rectangle
	rect = pygame.Rect(x, y, size, size)

	# Draw rounded rectangle outline
	pygame.draw.rect(surface, color, rect, width=1, border_radius=corner_radius)

def draw_squircle_grid(surface, squircle_size=30, spacing=40, roundness=0.7):
	"""Draw a background grid of squircles."""
	if theme == "LEGACY":
		bg_color = (0, 0, 16)
		squircle_color = TEAL
	elif theme == "ARES":
		bg_color = (10, 0, 0)
		squircle_color = DARKEST_RED
	elif theme == "RECONFIGURED":
		bg_color = (0, 10, 0)
		squircle_color = DARKER_GREEN
	elif theme == "UPRISING":
		bg_color = DARKER_TEAL
		squircle_color = (100, 100, 100)

	surface.fill(bg_color)

	width = surface.get_width()
	height = surface.get_height()

	# Create a transparent layer for squircles
	squircle_layer = pygame.Surface((width, height), pygame.SRCALPHA)

	# Calculate grid dimensions
	cols = width // spacing
	rows = height // spacing

	# Center the grid
	offset_x = (width - (cols * spacing)) / 2
	offset_y = (height - (rows * spacing)) / 2

	# Draw squircles in a grid pattern
	for row in range(rows + 1):
		for col in range(cols + 1):
			center_x = offset_x + col * spacing
			center_y = offset_y + row * spacing

			draw_squircle(squircle_layer, center_x, center_y, squircle_size, squircle_color, roundness)

	# Blit the squircle layer onto the main surface
	surface.blit(squircle_layer, (0, 0))

def draw_rotated_rect_debug(surface, color, center_x, center_y, width, height, angle_deg, line_width=2):
	"""Draw a rotated rectangle outline for debugging hitboxes."""
	import math
	half_w = width / 2
	half_h = height / 2
	corners = [
		(-half_w, -half_h),
		(half_w, -half_h),
		(half_w, half_h),
		(-half_w, half_h)
	]

	angle_rad = math.radians(angle_deg)
	cos_a = math.cos(angle_rad)
	sin_a = math.sin(angle_rad)

	rotated_corners = []
	for x, y in corners:
		rotated_x = x * cos_a - y * sin_a
		rotated_y = x * sin_a + y * cos_a
		rotated_corners.append((center_x + rotated_x, center_y + rotated_y))

	pygame.draw.polygon(surface, color, rotated_corners, line_width)

def draw_tron_grid(surface, desired_spacing=40):
	if theme == "LEGACY" or theme == "ARES" or theme == "UPRISING":
		draw_squircle_grid(WIN, 90, 120, .2)
	elif theme == "RECONFIGURED":
		# 8-bit style pixelated grid
		surface.fill((0, 10, 0))  # Dark green background

		width = surface.get_width()
		height = surface.get_height()

		# Use larger spacing for more 8-bit feel
		pixel_spacing = 60

		cols = width // pixel_spacing
		rows = height // pixel_spacing

		spacing_x = width / cols if cols > 0 else width
		spacing_y = height / rows if rows > 0 else height

		# Draw thick pixelated grid lines
		line_color = (0, 100, 0)  # Medium green
		line_thickness = 4

		# Vertical lines
		for i in range(cols + 1):
			x = int(i * spacing_x)
			pygame.draw.line(surface, line_color, (x, 0), (x, height), line_thickness)

		# Horizontal lines
		for j in range(rows + 1):
			y = int(j * spacing_y)
			pygame.draw.line(surface, line_color, (0, y), (width, y), line_thickness)

		# # Add decorative corner pixels at intersections for 8-bit style
		# corner_color = (0, 255, 0)  # Bright green
		# corner_size = 5
		# for i in range(cols + 1):
		# 	for j in range(rows + 1):
		# 		x = int(i * spacing_x)
		# 		y = int(j * spacing_y)
		# 		pygame.draw.rect(surface, corner_color, (x - corner_size // 2, y - corner_size // 2, corner_size, corner_size))
	elif theme == "82":
		color = WHITE
		surface.fill((0, 0, 25))

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

def show_message(text, subtext="", color=WHITE):
	# Add padding around the text
	padding_x = 20
	padding_y = 15
	spacing = 10  # vertical space between title and subtitle

	# Maximum width for text (screen width minus padding and some margin)
	max_text_width = WIDTH - 2 * padding_x - 40

	# Check if text needs to be split into two lines
	title = font.render(text, True, color)
	text_lines = []

	if title.get_width() > max_text_width:
		# Split text into two lines at a word boundary
		words = text.split()

		# Find the longest line1 that fits, ensuring line2 also fits
		best_split = 1
		for i in range(1, len(words)):
			line1 = " ".join(words[:i])
			line2 = " ".join(words[i:])

			line1_render = font.render(line1, True, color)
			line2_render = font.render(line2, True, color)

			# Both lines must fit within max_text_width
			if line1_render.get_width() <= max_text_width and line2_render.get_width() <= max_text_width:
				best_split = i
			else:
				# If line1 is too wide, we've gone too far
				if line1_render.get_width() > max_text_width:
					break

		line1 = " ".join(words[:best_split])
		line2 = " ".join(words[best_split:])
		text_lines = [line1, line2]
	else:
		text_lines = [text]

	# Render text surfaces
	title_surfaces = [font.render(line, True, color) for line in text_lines]

	if subtext != "":
		subtitle = small_font.render(subtext, True, (180, 180, 180))
		subtext_lines = []

		if subtitle.get_width() > max_text_width:
			# Split text into two lines at a word boundary
			words = subtext.split()

			# Find the longest line1 that fits, ensuring line2 also fits
			best_split = 1
			for i in range(1, len(words)):
				line1 = " ".join(words[:i])
				line2 = " ".join(words[i:])

				line1_render = small_font.render(line1, True, color)
				line2_render = small_font.render(line2, True, color)

				# Both lines must fit within max_text_width
				if line1_render.get_width() <= max_text_width and line2_render.get_width() <= max_text_width:
					best_split = i
				else:
					# If line1 is too wide, we've gone too far
					if line1_render.get_width() > max_text_width:
						break

			line1 = " ".join(words[:best_split])
			line2 = " ".join(words[best_split:])
			subtext_lines = [line1, line2]
		else:
			subtext_lines = [subtext]

		subtitle_surfaces = [small_font.render(line, True, (180, 180, 180)) for line in subtext_lines]

	# Determine box width & height based on text sizes
	max_title_width = max(surf.get_width() for surf in title_surfaces)
	total_title_height = sum(surf.get_height() for surf in title_surfaces) + spacing * (len(title_surfaces) - 1)

	if subtext != "":
		max_subtitle_width = max(sub_surf.get_width() for sub_surf in subtitle_surfaces)
		total_subtitle_height = sum(sub_surf.get_height() for sub_surf in subtitle_surfaces) + spacing * (len(subtitle_surfaces) - 1)
		box_width = max(max_title_width, max_subtitle_width) + 2 * padding_x
		box_height = total_title_height + total_subtitle_height + 2 * padding_y + spacing
	else:
		box_width = max_title_width + 2 * padding_x
		box_height = total_title_height + 2 * padding_y

	# Position box centered on screen
	box_x = WIDTH // 2 - box_width // 2
	box_y = HEIGHT // 2 - box_height // 2

	# Draw black background rectangle
	if theme == "82":
		pygame.draw.rect(WIN, (9, 35, 51), (box_x, box_y, box_width, box_height))
	elif theme == "UPRISING":
		pygame.draw.rect(WIN, (0, 0, 30), (box_x, box_y, box_width, box_height))
	else:
		pygame.draw.rect(WIN, BLACK, (box_x, box_y, box_width, box_height))

	# Draw outline rectangle
	if theme == "82":
		pygame.draw.rect(WIN, (128, 0, 128), (box_x, box_y, box_width, box_height), 3)
	else:
		pygame.draw.rect(WIN, color, (box_x, box_y, box_width, box_height), 3)

	# Draw the text centered inside the box
	current_y = box_y + padding_y
	for title_surf in title_surfaces:
		title_x = WIDTH // 2 - title_surf.get_width() // 2
		WIN.blit(title_surf, (title_x, current_y))
		current_y += title_surf.get_height() + spacing

	if subtext != "":
		# subtitle_x = WIDTH // 2 - subtitle.get_width() // 2
		# subtitle_y = current_y
		# WIN.blit(subtitle, (subtitle_x, subtitle_y))
		for subtitle_surf in subtitle_surfaces:
			subtitle_x = WIDTH // 2 - subtitle_surf.get_width() // 2
			WIN.blit(subtitle_surf, (subtitle_x, current_y))
			current_y += subtitle_surf.get_height() + spacing

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

def check_rect_collision_with_trails(bike_rect, trail1, trail2):
	"""Check if a bike's hitbox rectangle collides with any trail blocks.

	Args:
		bike_rect: pygame.Rect representing the bike's axis-aligned bounding box
		trail1: list of (x, y) tuples representing trail blocks
		trail2: list of (x, y) tuples representing trail blocks

	Returns:
		True if collision detected, False otherwise
	"""
	# Check all trail blocks from both trails
	for trail in [trail1, trail2]:
		for trail_pos in trail:
			# Create a rectangle for the trail block (BLOCK_SIZE x BLOCK_SIZE)
			trail_rect = pygame.Rect(trail_pos[0], trail_pos[1], BLOCK_SIZE, BLOCK_SIZE)

			# Check if the bike's bounding box intersects the trail block
			if bike_rect.colliderect(trail_rect):
				return True

	return False

def rotated_rect_intersects_rect(center_x, center_y, width, height, angle_deg, rect):
	"""Check if a rotated rectangle intersects an axis-aligned rectangle.

	Uses Separating Axis Theorem (SAT) for accurate collision detection.

	Args:
		center_x, center_y: Center of the rotated rectangle
		width, height: Dimensions of the rotated rectangle
		angle_deg: Rotation angle in degrees
		rect: pygame.Rect representing an axis-aligned rectangle

	Returns:
		True if rectangles intersect, False otherwise
	"""
	import math

	# Get corners of the rotated rectangle
	half_w = width / 2
	half_h = height / 2
	corners = [
		(-half_w, -half_h),
		(half_w, -half_h),
		(half_w, half_h),
		(-half_w, half_h)
	]

	angle_rad = math.radians(angle_deg)
	cos_a = math.cos(angle_rad)
	sin_a = math.sin(angle_rad)

	rotated_corners = []
	for x, y in corners:
		rotated_x = x * cos_a - y * sin_a + center_x
		rotated_y = x * sin_a + y * cos_a + center_y
		rotated_corners.append((rotated_x, rotated_y))

	# Get corners of the axis-aligned rectangle
	rect_corners = [
		(rect.left, rect.top),
		(rect.right, rect.top),
		(rect.right, rect.bottom),
		(rect.left, rect.bottom)
	]

	# Test separation on axes parallel to the rotated rect's edges
	axes = []
	for i in range(4):
		p1 = rotated_corners[i]
		p2 = rotated_corners[(i + 1) % 4]
		edge = (p2[0] - p1[0], p2[1] - p1[1])
		# Normal to the edge (perpendicular)
		normal = (-edge[1], edge[0])
		mag = math.hypot(normal[0], normal[1])
		if mag > 0:
			axes.append((normal[0] / mag, normal[1] / mag))

	# Test separation on axes parallel to the axis-aligned rect's edges
	axes.append((1, 0))  # X-axis
	axes.append((0, 1))  # Y-axis

	# For each axis, project both rectangles and check for overlap
	for axis in axes:
		# Project rotated rectangle corners onto axis
		rot_projections = [corner[0] * axis[0] + corner[1] * axis[1] for corner in rotated_corners]
		rot_min = min(rot_projections)
		rot_max = max(rot_projections)

		# Project axis-aligned rectangle corners onto axis
		rect_projections = [corner[0] * axis[0] + corner[1] * axis[1] for corner in rect_corners]
		rect_min = min(rect_projections)
		rect_max = max(rect_projections)

		# Check for gap (no overlap)
		if rot_max < rect_min or rect_max < rot_min:
			return False  # Separating axis found, no collision

	return True  # No separating axis found, rectangles intersect

def rotated_rects_intersect(center1_x, center1_y, width1, height1, angle1_deg,
                              center2_x, center2_y, width2, height2, angle2_deg):
	"""Check if two rotated rectangles intersect using Separating Axis Theorem (SAT).

	Args:
		center1_x, center1_y: Center of first rotated rectangle
		width1, height1: Dimensions of first rotated rectangle
		angle1_deg: Rotation angle of first rectangle in degrees
		center2_x, center2_y: Center of second rotated rectangle
		width2, height2: Dimensions of second rotated rectangle
		angle2_deg: Rotation angle of second rectangle in degrees

	Returns:
		True if rectangles intersect, False otherwise
	"""
	import math

	def get_corners(center_x, center_y, width, height, angle_deg):
		"""Get the four corners of a rotated rectangle."""
		half_w = width / 2
		half_h = height / 2
		corners = [
			(-half_w, -half_h),
			(half_w, -half_h),
			(half_w, half_h),
			(-half_w, half_h)
		]

		angle_rad = math.radians(angle_deg)
		cos_a = math.cos(angle_rad)
		sin_a = math.sin(angle_rad)

		rotated_corners = []
		for x, y in corners:
			rotated_x = x * cos_a - y * sin_a + center_x
			rotated_y = x * sin_a + y * cos_a + center_y
			rotated_corners.append((rotated_x, rotated_y))
		return rotated_corners

	# Get corners of both rectangles
	corners1 = get_corners(center1_x, center1_y, width1, height1, angle1_deg)
	corners2 = get_corners(center2_x, center2_y, width2, height2, angle2_deg)

	# Get axes to test (perpendicular to edges of both rectangles)
	axes = []
	for corners in [corners1, corners2]:
		for i in range(4):
			p1 = corners[i]
			p2 = corners[(i + 1) % 4]
			edge = (p2[0] - p1[0], p2[1] - p1[1])
			# Normal to the edge (perpendicular)
			normal = (-edge[1], edge[0])
			mag = math.hypot(normal[0], normal[1])
			if mag > 0:
				axes.append((normal[0] / mag, normal[1] / mag))

	# For each axis, project both rectangles and check for overlap
	for axis in axes:
		# Project first rectangle corners onto axis
		proj1 = [corner[0] * axis[0] + corner[1] * axis[1] for corner in corners1]
		min1 = min(proj1)
		max1 = max(proj1)

		# Project second rectangle corners onto axis
		proj2 = [corner[0] * axis[0] + corner[1] * axis[1] for corner in corners2]
		min2 = min(proj2)
		max2 = max(proj2)

		# Check for gap (no overlap)
		if max1 < min2 or max2 < min1:
			return False  # Separating axis found, no collision

	return True  # No separating axis found, rectangles intersect

def draw_bike_glow(bike, alpha=80):
	"""Draw a faint oval glow underneath a bike."""
	import math

	# Determine glow dimensions based on bike direction
	dx, dy = bike.dir
	if dx == 0 and dy == 0:
		# Bike not moving yet, use circular glow
		width, height = 12, 12
	elif abs(dx) > abs(dy):
		# Moving horizontally - elongate horizontally
		width, height = 27, 12
	else:
		# Moving vertically - elongate vertically
		width, height = 12, 27

	# Create a surface for the glow with per-pixel alpha
	glow_surface = pygame.Surface((width * 2, height * 2), pygame.SRCALPHA)

	# Draw multiple ellipses with decreasing alpha for a gradient effect
	for i in range(3):
		current_width = width - (i * 3)
		current_height = height - (i * 3)
		current_alpha = alpha - (i * 15)
		if current_alpha < 0:
			current_alpha = 0
		if current_width > 0 and current_height > 0:
			rect = pygame.Rect(width - current_width, height - current_height,
			                   current_width * 2, current_height * 2)
			pygame.draw.ellipse(glow_surface, (*bike.color, current_alpha), rect)

	# Calculate the center of the bike sprite
	if theme == "LEGACY" or theme == "ARES" or theme == "UPRISING":
		sprite_width = legacy_width
	elif theme == "82":
		sprite_width = width_82
	elif theme == "RECONFIGURED":
		sprite_width = reconfigured_width

	# Get direction magnitude for centering calculation
	mag = math.hypot(dx, dy)

	# bike.pos is the top-left of the trail block, so offset to center of 5x5 block
	# BLOCK_SIZE is 5, so center is at +2 (accounting for 0-indexed pixels: 0,1,2,3,4 -> center at 2)
	back_center_x = bike.pos[0] + 2
	back_center_y = bike.pos[1] + 2

	if mag > 0:
		# Normalize direction
		nx, ny = dx / mag, dy / mag
		# Calculate center of sprite - same calculation as blit_bike_with_front_at
		# This ensures the glow is centered exactly with the bike sprite
		back_margin = 4
		center_offset = sprite_width / 2 - back_margin
		center_x = back_center_x + nx * center_offset
		center_y = back_center_y + ny * center_offset
	else:
		# Bike not moving, center on position
		center_x = back_center_x
		center_y = back_center_y

	# Blit the glow centered on the bike's center
	glow_x = center_x - width
	glow_y = center_y - height
	WIN.blit(glow_surface, (glow_x, glow_y))

def get_bike_rect(bike, sprite_width, sprite_height, back_margin=4):
	"""Calculate the tight bounding rectangle for a bike sprite."""
	dx, dy = bike.dir
	mag = math.hypot(dx, dy)

	if mag == 0:
		# Bike not moving, return a small rect at position
		return pygame.Rect(bike.pos[0], bike.pos[1], sprite_width, sprite_height)

	# Normalize direction
	nx, ny = dx / mag, dy / mag

	# Calculate angle for rotation
	rad = math.atan2(-dy, dx)
	angle_deg = math.degrees(rad)

	# Bike center position (accounting for trail block offset)
	back_center_x = bike.pos[0] + 2
	back_center_y = bike.pos[1] + 2

	# Vector from back to sprite center
	local_center = pygame.math.Vector2((sprite_width/2 - back_margin, 0))
	rotated_center = local_center.rotate(-angle_deg)

	center_x = back_center_x + rotated_center.x
	center_y = back_center_y + rotated_center.y

	# Create rect centered at sprite center
	# Use slightly smaller dimensions for tighter collision (90% of sprite size)
	tight_width = sprite_width * 0.9
	tight_height = sprite_height * 0.9

	rect = pygame.Rect(0, 0, tight_width, tight_height)
	rect.center = (center_x, center_y)

	return rect

def draw_sprites():
	"""Render both bikes on the screen."""
	player1.render(WIN, blit_bike_with_front_at, back_margin=4)
	player2.render(WIN, blit_bike_with_front_at, back_margin=4)

def draw_trails():
	for point in player1.trail:
		if theme == "RECONFIGURED":
			pygame.draw.rect(WIN, GREEN, (*point, BLOCK_SIZE, BLOCK_SIZE))
		else:
			pygame.draw.rect(WIN, BLUE, (*point, BLOCK_SIZE, BLOCK_SIZE))
	for point in player2.trail:
		if theme == "ARES":
			pygame.draw.rect(WIN, RED, (*point, BLOCK_SIZE, BLOCK_SIZE))
		elif theme == "RECONFIGURED":
			pygame.draw.rect(WIN, YELLOW, (*point, BLOCK_SIZE, BLOCK_SIZE))
		else:
			pygame.draw.rect(WIN, ORANGE, (*point, BLOCK_SIZE, BLOCK_SIZE))

def draw_debug_hitboxes():
	"""Draw debug visualization showing actual collision hitboxes."""
	import math

	if theme == "LEGACY" or theme == "ARES" or theme == "UPRISING":
		sprite_width = legacy_width
		sprite_height = legacy_height
	elif theme == "RECONFIGURED":
		sprite_width = reconfigured_width
		sprite_height = reconfigured_height
	elif theme == "82":
		sprite_width = width_82
		sprite_height = height_82

	back_margin = 4  # Same as used in blit_bike_with_front_at
	tight_width = sprite_width * 0.9
	tight_height = sprite_height * 0.9

	def draw_bike_hitboxes(bike, color_body, color_front):
		"""Draw hitboxes for a single bike."""
		pos_x, pos_y = bike.pos
		dir_x, dir_y = bike.dir
		angle = math.degrees(math.atan2(dir_y, dir_x))

		# Back center (center of 5x5 trail block)
		back_center_x = pos_x + 2
		back_center_y = pos_y + 2

		# Normalize direction
		mag = math.sqrt(dir_x**2 + dir_y**2)
		if mag > 0:
			nx = dir_x / mag
			ny = dir_y / mag
		else:
			nx, ny = 1, 0

		# Calculate body hitbox center (90% of sprite size)
		body_offset = sprite_width / 2 - back_margin
		body_center_x = back_center_x + nx * body_offset
		body_center_y = back_center_y + ny * body_offset

		# Draw body hitbox in semi-transparent color
		draw_rotated_rect_debug(WIN, color_body, body_center_x, body_center_y,
		                        tight_width, tight_height, angle, line_width=2)

		# Calculate front hitbox position
		# The outer edge of the front hitbox aligns with the sprite's front edge
		front_hitbox_width = sprite_width * 0.25
		front_hitbox_height = tight_height

		# Position the hitbox so its outer edge aligns with sprite edge
		# Sprite front edge is at (sprite_width - back_margin) from back
		# Hitbox center should be at: sprite_edge - (hitbox_width / 2)
		front_offset = (sprite_width - back_margin) - (front_hitbox_width / 2)
		front_center_x = back_center_x + nx * front_offset
		front_center_y = back_center_y + ny * front_offset

		# Draw front hitbox in bright color
		draw_rotated_rect_debug(WIN, color_front, front_center_x, front_center_y,
		                        front_hitbox_width, front_hitbox_height, angle, line_width=2)

	# Player 1 hitboxes (cyan body, white front)
	if theme == "RECONFIGURED":
		draw_bike_hitboxes(player1, GREEN, (255, 255, 0))
	else:
		draw_bike_hitboxes(player1, (0, 180, 180), (255, 255, 255))

	# Player 2 hitboxes (orange/red body, yellow front)
	if theme == "ARES":
		draw_bike_hitboxes(player2, (180, 0, 0), (255, 255, 0))
	elif theme == "RECONFIGURED":
		draw_bike_hitboxes(player2, YELLOW, (255, 255, 0))
	else:
		draw_bike_hitboxes(player2, (180, 100, 0), (255, 255, 0))

def draw_scoreboard():
	if theme == "RECONFIGURED":
		p1_text = small_font.render(f"Green: {p1_wins}", True, GREEN)
	else:
		p1_text = small_font.render(f"Blue: {p1_wins}", True, BLUE)

	if theme == "ARES":
		p2_text = small_font.render(f"Red: {p2_wins}", True, RED)
	elif theme == "RECONFIGURED":
		p2_text = small_font.render(f"Yellow: {p2_wins}", True, YELLOW)
	else:
		p2_text = small_font.render(f"Orange: {p2_wins}", True, ORANGE)

	# Space them evenly at the top center
	total_width = p1_text.get_width() + p2_text.get_width() + 50
	start_x = WIDTH // 2 - total_width // 2

	WIN.blit(p1_text, (start_x, 10))
	WIN.blit(p2_text, (start_x + p1_text.get_width() + 50, 10))

def reset_game():
	"""Reset the game for a new round."""
	global game_over, game_time_offset, last_powerup_spawn, player1, player2

	if theme == "LEGACY" or theme == "UPRISING":
		player1 = Bike(blue_legacy_sprite, BLUE, "Blue")
		player2 = Bike(orange_legacy_sprite, ORANGE, "Orange")
	elif theme == "ARES":
		player1 = Bike(blue_legacy_sprite, BLUE, "Blue")
		player2 = Bike(red_ares_sprite, RED, "Red")
	elif theme == "82":
		player1 = Bike(blue_82_sprite, BLUE, "Blue")
		player2 = Bike(orange_82_sprite, ORANGE, "Orange")
	elif theme == "RECONFIGURED":
		player1 = Bike(green_reconfigured_sprite, GREEN, "Green")
		player2 = Bike(yellow_reconfigured_sprite, YELLOW, "Yellow")

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

	NUM_OBSTACLES = random.randint(10, 15)
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
			powerups.append(PowerUp(x, y, size, ptype, theme))
			break

def draw_powerups():
	"""Render all power-ups on the screen."""
	for powerup in powerups:
		powerup.render(WIN, theme)

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
	global current_track

	if theme == "ARES":
		if init.exists():
			pygame.mixer.music.stop()
			pygame.mixer.music.load("music/init.mp3")
			pygame.mixer.music.play(-1)
			pygame.mixer.music.set_volume(0.75)
			current_track = str(init)
	elif theme == "LEGACY":
		if clu.exists():
			pygame.mixer.music.stop()
			pygame.mixer.music.load("music/clu.mp3")
			pygame.mixer.music.play(-1)
			pygame.mixer.music.set_volume(1)
			current_track = str(clu)
	elif theme == "82":
		if ring_game_and_escape1.exists():
			pygame.mixer.music.stop()
			pygame.mixer.music.load("music/ring_game_and_escape1.mp3")
			pygame.mixer.music.play(-1)
			pygame.mixer.music.set_volume(1)
			current_track = str(ring_game_and_escape1)
	elif theme == "RECONFIGURED":
		if the_son_of_flynn_reconfigured.exists():
			pygame.mixer.music.stop()
			pygame.mixer.music.load("music/the_son_of_flynn_reconfigured.mp3")
			pygame.mixer.music.play(-1)
			pygame.mixer.music.set_volume(0.75)
			current_track = str(the_son_of_flynn_reconfigured)
	elif theme == "UPRISING":
		if tesler_throwdown.exists():
			pygame.mixer.music.stop()
			pygame.mixer.music.load("music/tesler_throwdown.mp3")
			pygame.mixer.music.play(-1)
			pygame.mixer.music.set_volume(1)
			current_track = str(tesler_throwdown)
	for i in range(3, 0, -1):
		WIN.fill(BLACK)
		draw_tron_grid(WIN)
		if theme == "LEGACY" or theme == "ARES" or theme == "RECONFIGURED" or theme == "UPRISING":
			draw_bike_glow(player1)
			draw_bike_glow(player2)
		draw_obstacles()
		draw_powerups()
		draw_sprites()
		if show_debug_hitboxes:
			draw_debug_hitboxes()
		draw_scoreboard()
		if theme == "ARES":
			show_message(str(i), "", DARKER_RED)
		elif theme == "LEGACY":
			show_message(str(i), "", DARKER_BLUE)
		elif theme == "82":
			show_message(str(i), "", LIGHT_GRAY)
		elif theme == "RECONFIGURED":
			show_message(str(i), "", GREEN)
		elif theme == "UPRISING":
			show_message(str(i), "", DARKER_BLUE)
		pygame.display.update()
		pygame.time.delay(1000)

	# Flash "GO!"
	WIN.fill(BLACK)
	draw_tron_grid(WIN)
	if theme == "LEGACY" or theme == "ARES" or theme == "RECONFIGURED" or theme == "UPRISING":
		draw_bike_glow(player1)
		draw_bike_glow(player2)
	draw_obstacles()
	draw_powerups()
	draw_sprites()
	if show_debug_hitboxes:
		draw_debug_hitboxes()
	draw_scoreboard()
	if theme == "ARES":
		show_message("GO!", "", DARKER_RED)
	elif theme == "LEGACY":
		show_message("GO!", "", DARKER_BLUE)
	elif theme == "82":
		show_message("GO!", "", LIGHT_GRAY)
	elif theme == "RECONFIGURED":
		show_message("GO!", "", GREEN)
	elif theme == "UPRISING":
		show_message("GO!", "", DARKER_BLUE)
	pygame.display.update()
	pygame.time.delay(800)
	if theme == "ARES":
		game_song = random.choice(game_music_ares)
		selected_song = str(game_song)
		pygame.mixer.music.stop()
		pygame.mixer.music.load(selected_song)
		pygame.mixer.music.play(-1)
		pygame.mixer.music.set_volume(0.75)
		current_track = selected_song
	elif theme == "82":
		if ring_game_and_escape2.exists():
			pygame.mixer.music.stop()
			pygame.mixer.music.load("music/ring_game_and_escape2.mp3")
			pygame.mixer.music.play(-1)
			pygame.mixer.music.set_volume(1)
			current_track = str(ring_game_and_escape2)
	elif theme == "LEGACY":
		game_song = random.choice(game_music_legacy)
		selected_song = str(game_song)
		pygame.mixer.music.stop()
		pygame.mixer.music.load(selected_song)
		pygame.mixer.music.play(-1)
		pygame.mixer.music.set_volume(1)
		current_track = selected_song
	elif theme == "RECONFIGURED":
		game_song = random.choice(game_music_reconfigured)
		selected_song = str(game_song)
		pygame.mixer.music.stop()
		pygame.mixer.music.load(selected_song)
		pygame.mixer.music.play(-1)
		pygame.mixer.music.set_volume(1)
		current_track = selected_song
	elif theme == "UPRISING":
		game_song = random.choice(game_music_uprising)
		selected_song = str(game_song)
		pygame.mixer.music.stop()
		pygame.mixer.music.load(selected_song)
		pygame.mixer.music.play(-1)
		pygame.mixer.music.set_volume(1)
		current_track = selected_song

def p1_win():
	global game_over, match_over, win_color, win_text, p1_wins, current_track
	if theme == "82":
		if derezzed_sound_82_file.exists():
			pygame.mixer.music.stop()
			turn_channel.stop()
			derezz_channel.play(derezzed_sound_82)
	else:
		if derezzed_sound_file.exists():
			pygame.mixer.music.stop()
			derezz_channel.play(derezzed_sound)

	game_over = True

	# --- Draw final collision frame before pausing ---
	WIN.fill(BLACK)
	draw_tron_grid(WIN)
	if theme == "LEGACY" or theme == "ARES" or theme == "RECONFIGURED" or theme == "UPRISING":
		draw_bike_glow(player1)
		draw_bike_glow(player2)
	draw_trails()
	draw_obstacles()
	draw_powerups()
	draw_sprites()
	if show_debug_hitboxes:
		draw_debug_hitboxes()
	draw_scoreboard()
	pygame.display.update()

	# Small pause to show the collision frame
	if theme == "82":
		pygame.time.delay(2600)
	else:
		pygame.time.delay(1800)

	p1_wins += 1
	if theme == "RECONFIGURED":
		win_color = GREEN
	else:
		win_color = BLUE
	# Check for match victory
	if p1_wins >= MAX_SCORE:
		match_over = True
		if theme == "RECONFIGURED":
			win_text = "TEAM GREEN WINS THE MATCH!"
		else:
			win_text = "TEAM BLUE WINS THE MATCH!"
		if theme == "ARES":
			if new_directive.exists():
				pygame.mixer.music.load("music/new_directive.mp3")
				pygame.mixer.music.play(-1)
				pygame.mixer.music.set_volume(0.75)
				current_track = str(new_directive)
		elif theme == "LEGACY":
			if end_titles.exists():
				pygame.mixer.music.load("music/end_titles.mp3")
				pygame.mixer.music.play(-1)
				pygame.mixer.music.set_volume(1)
				current_track = str(end_titles)
		elif theme == "RECONFIGURED":
			if end_titles_reconfigured.exists():
				pygame.mixer.music.load("music/end_titles_reconfigured.mp3")
				pygame.mixer.music.play(-1)
				pygame.mixer.music.set_volume(0.75)
				current_track = str(end_titles_reconfigured)
		elif theme == "82":
			if ending_titles2.exists():
				pygame.mixer.music.load("music/ending_titles2.mp3")
				pygame.mixer.music.play(-1)
				pygame.mixer.music.set_volume(1)
				current_track = str(ending_titles2)
		elif theme == "UPRISING":
			if goodbye_renegade.exists():
				pygame.mixer.music.load("music/goodbye_renegade.mp3")
				pygame.mixer.music.play(-1)
				pygame.mixer.music.set_volume(1)
				current_track = str(goodbye_renegade)
	else:
		if theme == "RECONFIGURED":
			win_text = "TEAM GREEN WINS!"
		else:
			win_text = "TEAM BLUE WINS!"
		if theme == "ARES":
			if a_question_of_trust.exists():
				pygame.mixer.music.load("music/a_question_of_trust.mp3")
				pygame.mixer.music.play(-1)
				pygame.mixer.music.set_volume(0.75)
				current_track = str(a_question_of_trust)
		elif theme == "LEGACY":
			if the_grid.exists():
				pygame.mixer.music.load("music/the_grid.mp3")
				pygame.mixer.music.play(-1)
				pygame.mixer.music.set_volume(1)
				current_track = str(the_grid)
		elif theme == "RECONFIGURED":
			if the_grid_reconfigured.exists():
				pygame.mixer.music.load("music/the_grid_reconfigured.mp3")
				pygame.mixer.music.play(-1)
				pygame.mixer.music.set_volume(0.75)
				current_track = str(the_grid_reconfigured)
		elif theme == "82":
			if ending_titles1.exists():
				pygame.mixer.music.load("music/ending_titles1.mp3")
				pygame.mixer.music.play(-1)
				pygame.mixer.music.set_volume(1)
				current_track = str(ending_titles1)
		elif theme == "UPRISING":
			if renegades_pledge.exists():
				pygame.mixer.music.load("music/renegades_pledge.mp3")
				pygame.mixer.music.play(-1)
				pygame.mixer.music.set_volume(1)
				current_track = str(renegades_pledge)

def p2_win():
	global game_over, match_over, win_color, win_text, p2_wins, current_track
	if theme == "82":
		if derezzed_sound_82_file.exists():
			pygame.mixer.music.stop()
			turn_channel.stop()
			derezz_channel.play(derezzed_sound_82)
	else:
		if derezzed_sound_file.exists():
			pygame.mixer.music.stop()
			derezz_channel.play(derezzed_sound)

	game_over = True

	# --- Draw final collision frame before pausing ---
	WIN.fill(BLACK)
	draw_tron_grid(WIN)
	if theme == "LEGACY" or theme == "ARES" or theme == "RECONFIGURED" or theme == "UPRISING":
		draw_bike_glow(player1)
		draw_bike_glow(player2)
	draw_trails()
	draw_obstacles()
	draw_powerups()
	draw_sprites()
	if show_debug_hitboxes:
		draw_debug_hitboxes()
	draw_scoreboard()
	pygame.display.update()

	# Small pause to show the collision frame
	if theme == "82":
		pygame.time.delay(2600)
	else:
		pygame.time.delay(1800)

	p2_wins += 1
	if theme == "ARES":
		win_color = RED
	elif theme == "RECONFIGURED":
		win_color = YELLOW
	else:
		win_color = ORANGE
	# Check for match victory
	if p2_wins >= MAX_SCORE:
		match_over = True
		if theme == "ARES":
			win_text = "TEAM RED WINS THE MATCH!"
		elif theme == "RECONFIGURED":
			win_text = "TEAM YELLOW WINS THE MATCH!"
		else:
			win_text = "TEAM ORANGE WINS THE MATCH!"
		if single_player:
			if theme == "ARES":
				if expendable.exists():
					pygame.mixer.music.load("music/100%_expendable.mp3")
					pygame.mixer.music.play(-1)
					pygame.mixer.music.set_volume(0.75)
					current_track = str(expendable)
			elif theme == "LEGACY":
				if adagio_for_tron.exists():
					pygame.mixer.music.load("music/adagio_for_tron.mp3")
					pygame.mixer.music.play(-1)
					pygame.mixer.music.set_volume(1)
					current_track = str(adagio_for_tron)
			elif theme == "RECONFIGURED":
				if encom_reconfigured.exists():
					pygame.mixer.music.load("music/encom_reconfigured.mp3")
					pygame.mixer.music.play(-1)
					pygame.mixer.music.set_volume(0.75)
					current_track = str(encom_reconfigured)
			elif theme == "82":
				if sea_of_simulation.exists():
					pygame.mixer.music.load("music/sea_of_simulation.mp3")
					pygame.mixer.music.play(-1)
					pygame.mixer.music.set_volume(1)
					current_track = str(sea_of_simulation)
			elif theme == "UPRISING":
				if luxs_sacrifice.exists():
					pygame.mixer.music.load("music/luxs_sacrifice.mp3")
					pygame.mixer.music.play(-1)
					pygame.mixer.music.set_volume(1)
					current_track = str(luxs_sacrifice)
		else:
			if theme == "ARES":
				if new_directive.exists():
					pygame.mixer.music.load("music/new_directive.mp3")
					pygame.mixer.music.play(-1)
					pygame.mixer.music.set_volume(0.75)
					current_track = str(new_directive)
			elif theme == "LEGACY":
				if end_titles.exists():
					pygame.mixer.music.load("music/end_titles.mp3")
					pygame.mixer.music.play(-1)
					pygame.mixer.music.set_volume(1)
					current_track = str(end_titles)
			elif theme == "RECONFIGURED":
				if end_titles_reconfigured.exists():
					pygame.mixer.music.load("music/end_titles_reconfigured.mp3")
					pygame.mixer.music.play(-1)
					pygame.mixer.music.set_volume(0.75)
					current_track = str(end_titles_reconfigured)
			elif theme == "82":
				if ending_titles2.exists():
					pygame.mixer.music.load("music/ending_titles2.mp3")
					pygame.mixer.music.play(-1)
					pygame.mixer.music.set_volume(1)
					current_track = str(ending_titles2)
			elif theme == "UPRISING":
				if goodbye_renegade.exists():
					pygame.mixer.music.load("music/goodbye_renegade.mp3")
					pygame.mixer.music.play(-1)
					pygame.mixer.music.set_volume(1)
					current_track = str(goodbye_renegade)
	else:
		if theme == "ARES":
			win_text = "TEAM RED WINS!"
		elif theme == "RECONFIGURED":
			win_text = "TEAM YELLOW WINS!"
		else:
			win_text = "TEAM ORANGE WINS!"
		if single_player:
			if theme == "ARES":
				if in_the_image_of.exists():
					pygame.mixer.music.load("music/in_the_image_of.mp3")
					pygame.mixer.music.play(-1)
					pygame.mixer.music.set_volume(0.75)
					current_track = str(in_the_image_of)
			elif theme == "LEGACY":
				if rinzler.exists():
					pygame.mixer.music.load("music/rinzler.mp3")
					pygame.mixer.music.play(-1)
					pygame.mixer.music.set_volume(1)
					current_track = rinzler
			elif theme == "RECONFIGURED":
				if rinzler_reconfigured.exists():
					pygame.mixer.music.load("music/rinzler_reconfigured.mp3")
					pygame.mixer.music.play(-1)
					pygame.mixer.music.set_volume(1)
					current_track = str(rinzler_reconfigured)
			elif theme == "82":
				if weve_got_company.exists():
					pygame.mixer.music.load("music/weve_got_company.mp3")
					pygame.mixer.music.play(-1)
					pygame.mixer.music.set_volume(1)
					current_track = str(weve_got_company)
			elif theme == "UPRISING":
				if the_games.exists():
					pygame.mixer.music.load("music/the_games.mp3")
					pygame.mixer.music.play(-1)
					pygame.mixer.music.set_volume(1)
					current_track = str(the_games)
		else:
			if theme == "ARES":
				if a_question_of_trust.exists():
					pygame.mixer.music.load("music/a_question_of_trust.mp3")
					pygame.mixer.music.play(-1)
					pygame.mixer.music.set_volume(0.75)
					current_track = str(a_question_of_trust)
			elif theme == "LEGACY":
				if the_grid.exists():
					pygame.mixer.music.load("music/the_grid.mp3")
					pygame.mixer.music.play(-1)
					pygame.mixer.music.set_volume(1)
					current_track = str(the_grid)
			elif theme == "RECONFIGURED":
				if the_grid_reconfigured.exists():
					pygame.mixer.music.load("music/the_grid_reconfigured.mp3")
					pygame.mixer.music.play(-1)
					pygame.mixer.music.set_volume(0.75)
					current_track = str(the_grid_reconfigured)
			elif theme == "82":
				if ending_titles1.exists():
					pygame.mixer.music.load("music/ending_titles1.mp3")
					pygame.mixer.music.play(-1)
					pygame.mixer.music.set_volume(1)
					current_track = str(ending_titles1)
			elif theme == "UPRISING":
				if renegades_pledge.exists():
					pygame.mixer.music.load("music/renegades_pledge.mp3")
					pygame.mixer.music.play(-1)
					pygame.mixer.music.set_volume(1)
					current_track = str(renegades_pledge)

def ai_control(current_game_time):
	"""AI for p2 bike that avoids collisions and seeks power-ups."""
	# Check turn cooldown
	if not player2.can_turn(current_game_time, turn_cooldown):
		return

	# Emergency wall avoidance - check if AI is dangerously close to any wall
	WALL_DANGER_ZONE = 60  # Distance from wall that triggers emergency turn (reduced to make AI more aggressive)
	pos_x, pos_y = player2.pos
	dir_x, dir_y = player2.dir

	# Check if heading toward a wall and too close
	if dir_x > 0 and pos_x > 900 - WALL_DANGER_ZONE:  # Heading right toward right wall
		# Turn up or down
		new_dir = dirs["DOWN"] if pos_y < 450 else dirs["UP"]
		if not player2.is_zigzag(new_dir, dirs, current_game_time):
			player2.last_turn_direction = player2.dir
			player2.dir = new_dir
			player2.last_turn_time = current_game_time
		return
	elif dir_x < 0 and pos_x < WALL_DANGER_ZONE:  # Heading left toward left wall
		# Turn up or down
		new_dir = dirs["DOWN"] if pos_y < 450 else dirs["UP"]
		if not player2.is_zigzag(new_dir, dirs, current_game_time):
			player2.last_turn_direction = player2.dir
			player2.dir = new_dir
			player2.last_turn_time = current_game_time
		return
	elif dir_y > 0 and pos_y > 900 - WALL_DANGER_ZONE:  # Heading down toward bottom wall
		# Turn left or right
		new_dir = dirs["RIGHT"] if pos_x < 450 else dirs["LEFT"]
		if not player2.is_zigzag(new_dir, dirs, current_game_time):
			player2.last_turn_direction = player2.dir
			player2.dir = new_dir
			player2.last_turn_time = current_game_time
		return
	elif dir_y < 0 and pos_y < WALL_DANGER_ZONE:  # Heading up toward top wall
		# Turn left or right
		new_dir = dirs["RIGHT"] if pos_x < 450 else dirs["LEFT"]
		if not player2.is_zigzag(new_dir, dirs, current_game_time):
			player2.last_turn_direction = player2.dir
			player2.dir = new_dir
			player2.last_turn_time = current_game_time
		return

	possible_dirs = [dirs["UP"], dirs["DOWN"], dirs["LEFT"], dirs["RIGHT"]]

	def will_collide(pos, dir_vec, steps=20):
		"""Predict if moving forward will cause a collision using simplified hitbox detection."""
		# Get sprite dimensions based on theme
		if theme == "LEGACY" or theme == "ARES" or theme == "UPRISING":
			sprite_w = legacy_width
			sprite_h = legacy_height
		elif theme == "RECONFIGURED":
			sprite_w = reconfigured_width
			sprite_h = reconfigured_height
		elif theme == "82":
			sprite_w = width_82
			sprite_h = height_82

		back_margin = 4
		# Calculate rotation angle for the test direction
		mag = math.hypot(dir_vec[0], dir_vec[1])
		if mag == 0:
			return True

		# Use a simplified rectangular hitbox check instead of full rotated rectangle
		# This is much faster and still reasonably accurate for AI purposes
		front_length = sprite_w - back_margin
		nx_norm, ny_norm = dir_vec[0] / mag, dir_vec[1] / mag

		# Define a safety margin around the bike
		# Increased from 0.15 to 0.25, and adding extra margin for walls
		safety_margin = sprite_w * 0.25
		wall_margin = 100  # Large fixed margin for wall detection to ensure AI turns away from edges early

		# Look ahead specified steps with larger step size for performance
		step_increment = max(1, SPEED)  # Check every SPEED pixels instead of every pixel
		for i in range(step_increment, steps * SPEED + 1, step_increment):
			# Calculate test position
			test_pos_x = pos[0] + nx_norm * i
			test_pos_y = pos[1] + ny_norm * i

			# Check wall collisions with margin
			fx = test_pos_x + nx_norm * front_length
			fy = test_pos_y + ny_norm * front_length
			if fx < wall_margin or fx >= WIDTH - wall_margin or fy < wall_margin or fy >= HEIGHT - wall_margin:
				return True

			# Check for head-on collision with player1
			# Calculate player1's position and direction
			p1_x, p1_y = player1.pos
			p1_dx, p1_dy = player1.dir
			p1_mag = math.hypot(p1_dx, p1_dy)

			if p1_mag > 0:
				# Normalize player1's direction
				p1_nx, p1_ny = p1_dx / p1_mag, p1_dy / p1_mag

				# Check if player1 is moving toward us (opposite directions)
				# Dot product of normalized directions: -1 means exactly opposite, < -0.7 means roughly opposite
				dot_product = nx_norm * p1_nx + ny_norm * p1_ny

				if dot_product < -0.7:  # Bikes are moving toward each other
					# Check if player1 is in front of us
					dist_to_p1 = math.hypot(test_pos_x - p1_x, test_pos_y - p1_y)
					if dist_to_p1 < sprite_w * 3:  # Within 3 bike lengths
						return True

			# Check trail collisions using a simple radius check (much faster)
			# Skip only the very recent trail to avoid false positives with the tail
			TRAIL_SAFETY_MARGIN = 5  # Only skip the last 5 positions to avoid immediate tail collision
			test_point = (int(test_pos_x), int(test_pos_y))

			# Quick check: is the test point near any trail?
			for trail_pos in player1.trail:
				distance = abs(test_pos_x - trail_pos[0]) + abs(test_pos_y - trail_pos[1])  # Manhattan distance
				if distance < safety_margin:
					return True

			# Check own trail with safety margin
			own_trail_to_check = player2.trail[:-TRAIL_SAFETY_MARGIN] if len(player2.trail) > TRAIL_SAFETY_MARGIN else []
			for trail_pos in own_trail_to_check:
				distance = abs(test_pos_x - trail_pos[0]) + abs(test_pos_y - trail_pos[1])
				if distance < safety_margin:
					return True

			# Check obstacle collisions with margin
			for obs in obstacles:
				# Simple AABB check with margin
				if (test_pos_x - safety_margin < obs.x + obs.size and
					test_pos_x + safety_margin > obs.x and
					test_pos_y - safety_margin < obs.y + obs.size and
					test_pos_y + safety_margin > obs.y):
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

	def is_powerup_reachable(bike_pos, powerup):
		"""Check if power-up is reachable by testing if we can get closer to it."""
		target_dirs = get_direction_to_powerup(bike_pos, powerup)

		# Check if ANY of the directions toward the power-up are safe
		for target_dir in target_dirs:
			# Don't turn 180 degrees from current direction
			if (player2.dir == dirs["UP"] and target_dir == dirs["DOWN"]) or \
			   (player2.dir == dirs["DOWN"] and target_dir == dirs["UP"]) or \
			   (player2.dir == dirs["LEFT"] and target_dir == dirs["RIGHT"]) or \
			   (player2.dir == dirs["RIGHT"] and target_dir == dirs["LEFT"]):
				continue

			# If this direction is safe, power-up is potentially reachable
			if not will_collide(bike_pos, target_dir, steps=15):
				return True

		# No safe route found toward the power-up
		return False

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

	# Try to move toward power-up if one exists, is reasonably close, AND is reachable
	if nearest_powerup and min_distance < 300 and is_powerup_reachable(player2.pos, nearest_powerup):
		target_dirs = get_direction_to_powerup(player2.pos, nearest_powerup)

		# Check if we can safely move toward the power-up
		for target_dir in target_dirs:
			# Don't turn 180 degrees
			if (player2.dir == dirs["UP"] and target_dir == dirs["DOWN"]) or \
			   (player2.dir == dirs["DOWN"] and target_dir == dirs["UP"]) or \
			   (player2.dir == dirs["LEFT"] and target_dir == dirs["RIGHT"]) or \
			   (player2.dir == dirs["RIGHT"] and target_dir == dirs["LEFT"]):
				continue

			# Check if this direction is safe and not a zigzag
			if not will_collide(player2.pos, target_dir, steps=15):# and not player2.is_zigzag(target_dir, dirs, current_game_time):
				player2.last_turn_direction = player2.dir
				player2.dir = target_dir
				player2.last_turn_time = current_game_time
				return

	# If current direction is safe, keep going
	if not will_collide(player2.pos, player2.dir):
		return

	# Otherwise, pick the safest turn (evaluate all safe directions)
	def evaluate_direction_safety(direction, max_steps=50):
		"""Calculate how many steps the AI can safely move in a direction."""
		# Use the will_collide function to test different lookahead distances
		# Binary search to find the maximum safe distance
		low, high = 0, max_steps
		safe_steps = 0

		while low <= high:
			mid = (low + high) // 2
			if not will_collide(player2.pos, direction, steps=mid):
				safe_steps = mid
				low = mid + 1
			else:
				high = mid - 1

		return safe_steps

	safe_dirs = [d for d in possible_dirs if not will_collide(player2.pos, d)]

	# Filter out 180-degree turns
	safe_dirs = [d for d in safe_dirs if not (
		(player2.dir == dirs["UP"] and d == dirs["DOWN"]) or
		(player2.dir == dirs["DOWN"] and d == dirs["UP"]) or
		(player2.dir == dirs["LEFT"] and d == dirs["RIGHT"]) or
		(player2.dir == dirs["RIGHT"] and d == dirs["LEFT"])
	)]

	if safe_dirs:
		# Evaluate safety of each direction and pick the safest
		best_dir = None
		best_safety = -1

		for direction in safe_dirs:
			safety = evaluate_direction_safety(direction)
			if safety > best_safety:
				best_safety = safety
				best_dir = direction

		if best_dir:# and not player2.is_zigzag(best_dir, dirs, current_game_time):
			player2.last_turn_direction = player2.dir
			player2.dir = best_dir
			player2.last_turn_time = current_game_time

def step_move_player(bike, other_bike, effective_speed, sprite_width, sprite_height, back_margin=4):
	"""Move a bike and check for collisions using rotated rectangle collision detection."""
	if effective_speed <= 0:
		return False

	# Normalize direction vector
	mag = math.hypot(bike.dir[0], bike.dir[1])
	if mag == 0:
		return False
	nx, ny = bike.dir[0] / mag, bike.dir[1] / mag

	# front offset from back
	front_length = sprite_width - back_margin

	# Calculate rotation angle
	rad = math.atan2(-bike.dir[1], bike.dir[0])
	angle_deg = math.degrees(rad)

	# Use 90% of sprite dimensions for tight hitbox
	tight_width = sprite_width * 0.9
	tight_height = sprite_height * 0.9

	# Skip the last few trail blocks to avoid self-collision with recent trail
	# At SPEED=5 and 60 FPS, the bike moves 5 pixels per frame
	# The bike sprite is ~20-40 pixels long, so we need to skip enough blocks
	# to clear the bike's entire length plus turning radius
	TRAIL_SAFETY_MARGIN = 50  # Number of recent trail blocks to skip for own trail

	# Helper function to check if a position would cause collision
	def would_collide(test_x, test_y):
		"""Check if moving to position (test_x, test_y) would cause a collision."""
		# Check wall collisions (using front position)
		fx = test_x + nx * front_length
		fy = test_y + ny * front_length
		if fx < 0 or fx >= WIDTH or fy < 0 or fy >= HEIGHT:
			return True

		# Calculate front hitbox position
		# The front hitbox is a small rectangle at the tip of the bike
		# Its outer edge should align perfectly with the sprite's front edge
		back_margin = 4
		front_hitbox_width = sprite_width * 0.25
		front_hitbox_height = tight_height

		# Position the hitbox so its outer edge aligns with sprite edge
		# Sprite front edge is at (sprite_width - back_margin) from back
		# Hitbox center should be at: sprite_edge - (hitbox_width / 2)
		front_offset = (sprite_width - back_margin) - (front_hitbox_width / 2)
		front_center_x = test_x + 2 + nx * front_offset
		front_center_y = test_y + 2 + ny * front_offset

		# Also calculate body hitbox for turn collision detection
		# The body extends from the back position
		back_margin = 4
		body_center_offset = sprite_width / 2 - back_margin
		body_center_x = test_x + 2 + nx * body_center_offset
		body_center_y = test_y + 2 + ny * body_center_offset
		body_width = sprite_width * 0.9
		body_height = tight_height

		# Create a broad-phase AABB for the front of the bike to quickly reject distant objects
		# This optimization dramatically improves performance with long trails
		front_aabb = pygame.Rect(0, 0, front_hitbox_width + 20, front_hitbox_height + 20)
		front_aabb.center = (front_center_x, front_center_y)

		# Also create a broad-phase AABB for the body
		body_aabb_broad = pygame.Rect(0, 0, body_width + 20, body_height + 20)
		body_aabb_broad.center = (body_center_x, body_center_y)

		# Check other bike's trail (all positions)
		# No inflation - hitboxes must actually touch
		for trail_pos in other_bike.trail:
			trail_rect = pygame.Rect(trail_pos[0], trail_pos[1], BLOCK_SIZE, BLOCK_SIZE)
			# Quick AABB rejection test - skip expensive rotated rect check if not close
			# Check both front and body AABBs
			if front_aabb.colliderect(trail_rect):
				# Check if front hitbox intersects trail
				if rotated_rect_intersects_rect(front_center_x, front_center_y, front_hitbox_width, front_hitbox_height, angle_deg, trail_rect):
					return True
			if body_aabb_broad.colliderect(trail_rect):
				# Also check if body hitbox intersects trail (important for turns)
				if rotated_rect_intersects_rect(body_center_x, body_center_y, body_width, body_height, angle_deg, trail_rect):
					return True

		# Check own trail (skip recent positions to avoid false collisions)
		own_trail_to_check = bike.trail[:-TRAIL_SAFETY_MARGIN] if len(bike.trail) > TRAIL_SAFETY_MARGIN else []
		for trail_pos in own_trail_to_check:
			trail_rect = pygame.Rect(trail_pos[0], trail_pos[1], BLOCK_SIZE, BLOCK_SIZE)
			# Quick AABB rejection test - skip expensive rotated rect check if not close
			# Check both front and body AABBs
			if front_aabb.colliderect(trail_rect):
				# Check if front hitbox intersects trail
				if rotated_rect_intersects_rect(front_center_x, front_center_y, front_hitbox_width, front_hitbox_height, angle_deg, trail_rect):
					return True
			if body_aabb_broad.colliderect(trail_rect):
				# Also check if body hitbox intersects trail (important for turns)
				if rotated_rect_intersects_rect(body_center_x, body_center_y, body_width, body_height, angle_deg, trail_rect):
					return True

		# Check obstacle collisions
		for obs in obstacles:
			obs_rect = pygame.Rect(obs.x, obs.y, obs.size, obs.size)
			# Quick AABB rejection test - skip expensive rotated rect check if not close
			if not front_aabb.colliderect(obs_rect):
				continue
			# Check if front hitbox intersects obstacle
			if rotated_rect_intersects_rect(front_center_x, front_center_y, front_hitbox_width, front_hitbox_height, angle_deg, obs_rect):
				return True

		# Check bike-to-bike collision
		if other_bike is not None:
			# Calculate other bike's position and hitbox
			other_mag = math.hypot(other_bike.dir[0], other_bike.dir[1])
			if other_mag > 0:
				# Calculate other bike's rotation angle
				other_rad = math.atan2(-other_bike.dir[1], other_bike.dir[0])
				other_angle_deg = math.degrees(other_rad)

				# Calculate other bike's sprite center
				other_back_center_x = other_bike.pos[0] + 2
				other_back_center_y = other_bike.pos[1] + 2
				other_nx = other_bike.dir[0] / other_mag
				other_ny = other_bike.dir[1] / other_mag
				other_center_offset = sprite_width / 2 - back_margin
				other_center_x = other_back_center_x + other_nx * other_center_offset
				other_center_y = other_back_center_y + other_ny * other_center_offset

				# Check if this bike's hitbox would intersect the other bike's hitbox
				# Use the full body hitbox for bike-to-bike collision
				if rotated_rects_intersect(
					body_center_x, body_center_y, body_width, body_height, angle_deg,
					other_center_x, other_center_y, tight_width, tight_height, other_angle_deg
				):
					return True

		return False

	# Move step-by-step, checking BEFORE each move
	steps = max(1, int(effective_speed))
	step_size = effective_speed / steps
	distance_moved = 0.0
	distance_since_last_trail = 0.0
	collided_player = 0

	for step in range(steps):
		# Calculate the next position
		next_x = bike.pos[0] + nx * step_size
		next_y = bike.pos[1] + ny * step_size

		# Check if moving to this position would cause collision
		if would_collide(next_x, next_y):
			# Collision detected - do a binary search to find the exact tangent position
			# Start with current position (safe) and next position (collision)
			safe_x, safe_y = bike.pos[0], bike.pos[1]
			collide_x, collide_y = next_x, next_y

			# Binary search for the exact tangent point (10 iterations gives sub-pixel precision)
			for _ in range(10):
				mid_x = (safe_x + collide_x) / 2
				mid_y = (safe_y + collide_y) / 2

				if would_collide(mid_x, mid_y):
					# Mid point collides, search in first half
					collide_x, collide_y = mid_x, mid_y
				else:
					# Mid point is safe, search in second half
					safe_x, safe_y = mid_x, mid_y

			# Move to the tangent position (midpoint between final safe and collide positions)
			# This ensures the hitbox edge is exactly at the collision boundary
			tangent_x = (safe_x + collide_x) / 2
			tangent_y = (safe_y + collide_y) / 2
			bike.pos[0] = tangent_x
			bike.pos[1] = tangent_y

			if bike == player1:
				collided_player = 1
			else:
				collided_player = 2
			break

		# Update position (only if no collision)
		bike.pos[0] = next_x
		bike.pos[1] = next_y
		distance_moved += step_size
		distance_since_last_trail += step_size

		# Add trail point every BLOCK_SIZE pixels to ensure continuous trail
		if distance_since_last_trail >= BLOCK_SIZE:
			new_pos = (int(bike.pos[0]), int(bike.pos[1]))
			bike.add_trail_point(new_pos)
			distance_since_last_trail = 0.0

	# Add final trail point if we haven't added one recently
	if distance_since_last_trail > 0:
		new_pos = (int(bike.pos[0]), int(bike.pos[1]))
		bike.add_trail_point(new_pos)

	return collided_player

def run_game():
	"""Main game loop."""
	global game_over, win_text, win_color, game_time_offset, last_powerup_spawn, show_ui_overlay, show_debug_hitboxes, current_track

	# --- Start Screen ---
	main_menu()
	running = True
	game_over = False
	show_ui_overlay = True  # Toggle for showing/hiding win message and scoreboard
	show_debug_hitboxes = False  # Toggle for debug hitbox visualization
	while running:
		if not game_over:
			clock.tick(60)

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_h:
						show_debug_hitboxes = not show_debug_hitboxes

			keys = pygame.key.get_pressed()

			current_time = pygame.time.get_ticks() - game_time_offset

			if current_time - last_powerup_spawn > POWERUP_SPAWN_INTERVAL:
				spawn_powerup()
				last_powerup_spawn = current_time

			# Player 1 (WASD) — Disable turning if frozen
			if not player1.is_frozen(current_time):
				if player1.can_turn(current_time, turn_cooldown):
					# Count how many direction keys are pressed
					p1_keys_pressed = sum([keys[pygame.K_w], keys[pygame.K_s], keys[pygame.K_a], keys[pygame.K_d]])

					# Only allow input if exactly one key is pressed
					if p1_keys_pressed == 1:
						new_dir = None
						if keys[pygame.K_w] and player1.dir != dirs["DOWN"] and player1.dir != dirs["UP"]:
							new_dir = dirs["UP"]
						elif keys[pygame.K_s] and player1.dir != dirs["UP"] and player1.dir != dirs["DOWN"]:
							new_dir = dirs["DOWN"]
						elif keys[pygame.K_a] and player1.dir != dirs["RIGHT"] and player1.dir != dirs["LEFT"]:
							new_dir = dirs["LEFT"]
						elif keys[pygame.K_d] and player1.dir != dirs["LEFT"] and player1.dir != dirs["RIGHT"]:
							new_dir = dirs["RIGHT"]

						# Only apply turn if not a zigzag
						if new_dir is not None: #and not player1.is_zigzag(new_dir, dirs, current_time):
							player1.last_turn_direction = player1.dir
							player1.dir = new_dir
							player1.last_turn_time = current_time

			# Player 2 (Arrows or AI) — Disable turning if frozen
			if not player2.is_frozen(current_time):
				if single_player:
					ai_control(current_time)
				else:
					if player2.can_turn(current_time, turn_cooldown):
						# Count how many direction keys are pressed
						p2_keys_pressed = sum([keys[pygame.K_UP], keys[pygame.K_DOWN], keys[pygame.K_LEFT], keys[pygame.K_RIGHT]])

						# Only allow input if exactly one key is pressed
						if p2_keys_pressed == 1:
							new_dir = None
							if keys[pygame.K_UP] and player2.dir != dirs["DOWN"] and player2.dir != dirs["UP"]:
								new_dir = dirs["UP"]
							elif keys[pygame.K_DOWN] and player2.dir != dirs["UP"] and player2.dir != dirs["DOWN"]:
								new_dir = dirs["DOWN"]
							elif keys[pygame.K_LEFT] and player2.dir != dirs["RIGHT"] and player2.dir != dirs["LEFT"]:
								new_dir = dirs["LEFT"]
							elif keys[pygame.K_RIGHT] and player2.dir != dirs["LEFT"] and player2.dir != dirs["RIGHT"]:
								new_dir = dirs["RIGHT"]

							# Only apply turn if not a zigzag
							if new_dir is not None:# and not player2.is_zigzag(new_dir, dirs, current_time):
								player2.last_turn_direction = player2.dir
								player2.dir = new_dir
								player2.last_turn_time = current_time

			# Get effective speeds considering status effects
			effective_speed_p1 = player1.get_effective_speed(SPEED, current_time)
			effective_speed_p2 = player2.get_effective_speed(SPEED, current_time)

			# Get sprite dimensions based on theme
			if theme == "LEGACY" or theme == "ARES" or theme == "UPRISING":
				sprite_w = legacy_width
				sprite_h = legacy_height
			elif theme == "RECONFIGURED":
				sprite_w = reconfigured_width
				sprite_h = reconfigured_height
			elif theme == "82":
				sprite_w = width_82
				sprite_h = height_82

			# Move both bikes
			collided1 = step_move_player(player1, player2, effective_speed_p1, sprite_w, sprite_h, back_margin=4)
			collided2 = step_move_player(player2, player1, effective_speed_p2, sprite_w, sprite_h, back_margin=4)
			if collided1 == 1:
				p2_win()
			elif collided1 == 2:
				p1_win()
			if collided2 == 1:
				p2_win()
			elif collided2 == 2:
				p1_win()

			p1_front = player1.get_front_pos(sprite_w)
			p2_front = player2.get_front_pos(sprite_w)

			# Check bike-to-bike collision - simply check if the sprite hitboxes overlap
			dx1, dy1 = player1.dir
			mag1 = math.hypot(dx1, dy1)
			dx2, dy2 = player2.dir
			mag2 = math.hypot(dx2, dy2)

			bikes_collided = False

			if mag1 > 0 and mag2 > 0:  # Both bikes are moving
				# Calculate rotation angles
				rad1 = math.atan2(-dy1, dx1)
				angle1_deg = math.degrees(rad1)
				rad2 = math.atan2(-dy2, dx2)
				angle2_deg = math.degrees(rad2)

				# Calculate sprite centers for both bikes
				back_margin = 4
				back_center_x1 = player1.pos[0] + 2
				back_center_y1 = player1.pos[1] + 2
				back_center_x2 = player2.pos[0] + 2
				back_center_y2 = player2.pos[1] + 2

				# Normalize direction vectors
				nx1, ny1 = dx1 / mag1, dy1 / mag1
				nx2, ny2 = dx2 / mag2, dy2 / mag2

				# Calculate sprite center offset (matching blit_bike_with_front_at logic)
				center_offset = sprite_w / 2 - back_margin
				center_x1 = back_center_x1 + nx1 * center_offset
				center_y1 = back_center_y1 + ny1 * center_offset
				center_x2 = back_center_x2 + nx2 * center_offset
				center_y2 = back_center_y2 + ny2 * center_offset

				# Check if the two sprite hitboxes intersect
				bikes_collided = rotated_rects_intersect(
					center_x1, center_y1, sprite_w, sprite_h, angle1_deg,
					center_x2, center_y2, sprite_w, sprite_h, angle2_deg
				)

			# Handle bike-to-bike collision ONLY if neither bike crashed into walls/trails
			if bikes_collided and collided1 == 0 and collided2 == 0:
				# Determine winner based on who hit whom from the side
				# Calculate front positions of both bikes
				p1_front_x = center_x1 + nx1 * (sprite_w / 2)
				p1_front_y = center_y1 + ny1 * (sprite_w / 2)
				p2_front_x = center_x2 + nx2 * (sprite_w / 2)
				p2_front_y = center_y2 + ny2 * (sprite_w / 2)

				# Calculate distances from each bike's front to the other bike's center
				dist_p1_front_to_p2_center = math.hypot(p1_front_x - center_x2, p1_front_y - center_y2)
				dist_p2_front_to_p1_center = math.hypot(p2_front_x - center_x1, p2_front_y - center_y1)

				# The bike whose front is closer to the other bike's center is the one that crashed
				# The other bike wins (was hit from the side)
				if dist_p1_front_to_p2_center < dist_p2_front_to_p1_center:
					# Player 1's front hit player 2's side - player 2 wins
					p2_win()
				elif dist_p2_front_to_p1_center < dist_p1_front_to_p2_center:
					# Player 2's front hit player 1's side - player 1 wins
					p1_win()
				else:
					# Perfect head-on collision - it's a draw (very rare)
					WIN.fill(BLACK)
					draw_tron_grid(WIN)
					if theme == "LEGACY" or theme == "ARES" or theme == "RECONFIGURED" or theme == "UPRISING":
						draw_bike_glow(player1)
						draw_bike_glow(player2)
					draw_trails()
					draw_obstacles()
					draw_powerups()
					draw_sprites()
					if show_debug_hitboxes:
						draw_debug_hitboxes()
					draw_scoreboard()
					pygame.display.update()
					if theme == "82":
						if derezzed_sound_82_file.exists():
							pygame.mixer.music.stop()
							turn_channel.stop()
							derezz_channel.play(derezzed_sound_82)
					else:
						if derezzed_sound_file.exists():
							pygame.mixer.music.stop()
							derezz_channel.play(derezzed_sound)
					game_over = True
					if theme == "82":
						pygame.time.delay(2600)
					else:
						pygame.time.delay(1800)
					win_text = "DRAW!"
					if theme == "ARES":
						win_color = DARKER_RED
						if this_changes_everything.exists():
							pygame.mixer.music.load("music/this_changes_everything.mp3")
							pygame.mixer.music.play(-1)
							pygame.mixer.music.set_volume(0.75)
							current_track = str(this_changes_everything)
					elif theme == "LEGACY":
						win_color = DARKER_BLUE
						if arena.exists():
							pygame.mixer.music.load("music/arena.mp3")
							pygame.mixer.music.play(-1)
							pygame.mixer.music.set_volume(1)
							current_track = str(arena)
					elif theme == "RECONFIGURED":
						win_color = GREEN
						if solar_sailer_reconfigured.exists():
							pygame.mixer.music.load("music/solar_sailer_reconfigured.mp3")
							pygame.mixer.music.play(-1)
							pygame.mixer.music.set_volume(0.75)
							current_track = str(solar_sailer_reconfigured)
					elif theme == "82":
						win_color = LIGHT_GRAY
						if tower_music.exists():
							pygame.mixer.music.load("music/tower_music.mp3")
							pygame.mixer.music.play(-1)
							pygame.mixer.music.set_volume(1)
							current_track = str(tower_music)
					elif theme == "UPRISING":
						win_color = DARKER_BLUE
						if rescuing_the_rebellion.exists():
							pygame.mixer.music.load("music/rescuing_the_rebellion.mp3")
							pygame.mixer.music.play(-1)
							pygame.mixer.music.set_volume(1)
							current_track = str(rescuing_the_rebellion)

			# --- Power-up collisions ---
			check_powerup_collision(p1_front, player1, current_time)
			check_powerup_collision(p2_front, player2, current_time)
			check_trail_powerup_collisions(current_time)

			# Render everything
			WIN.fill(BLACK)
			draw_tron_grid(WIN)
			if theme == "LEGACY" or theme == "ARES" or theme == "RECONFIGURED" or theme == "UPRISING":
				draw_bike_glow(player1)
				draw_bike_glow(player2)
			draw_trails()
			draw_obstacles()
			draw_powerups()
			draw_sprites()
			if show_debug_hitboxes:
				draw_debug_hitboxes()
			draw_scoreboard()
			pygame.display.update()

		else:
			# --- GAME OVER STATE ---
			if match_over:
				WIN.fill(BLACK)
				draw_tron_grid(WIN)
				if theme == "LEGACY" or theme == "ARES" or theme == "RECONFIGURED" or theme == "UPRISING":
					draw_bike_glow(player1)
					draw_bike_glow(player2)
				draw_trails()
				draw_obstacles()
				draw_powerups()
				draw_sprites()
				if show_debug_hitboxes:
					draw_debug_hitboxes()
				if show_ui_overlay:
					draw_scoreboard()
					show_message(win_text, "Press ESC to quit | SHIFT to hide", win_color)
				pygame.display.update()

				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						running = False
					elif event.type == pygame.KEYDOWN:
						if event.key == pygame.K_ESCAPE:
							show_ui_overlay = True
							main_menu()
						elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
							show_ui_overlay = not show_ui_overlay
						elif event.key == pygame.K_h:
							show_debug_hitboxes = not show_debug_hitboxes

			else:
				WIN.fill(BLACK)
				draw_tron_grid(WIN)
				if theme == "LEGACY" or theme == "ARES" or theme == "RECONFIGURED" or theme == "UPRISING":
					draw_bike_glow(player1)
					draw_bike_glow(player2)
				draw_trails()
				draw_obstacles()
				draw_powerups()
				draw_sprites()
				if show_debug_hitboxes:
					draw_debug_hitboxes()
				if show_ui_overlay:
					draw_scoreboard()
					show_message(win_text, "Press SPACE to continue | SHIFT to hide", win_color)
				pygame.display.update()

				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						running = False
					elif event.type == pygame.KEYDOWN:
						if event.key == pygame.K_SPACE:
							reset_game()
							show_ui_overlay = True
						elif event.key == pygame.K_ESCAPE:
							show_ui_overlay = True
							main_menu()
						elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
							show_ui_overlay = not show_ui_overlay
						elif event.key == pygame.K_h:
							show_debug_hitboxes = not show_debug_hitboxes

	pygame.quit()