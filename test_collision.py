"""Test script for bike-to-bike collision detection.

This script creates a controlled scenario where two bikes move directly
toward each other to test the improved rotated rectangle collision detection.
"""

import pygame
import sys
import math
from pathlib import Path

from bike import Bike
from functions import rotated_rect_intersects_rect

pygame.init()

# Screen setup
WIDTH, HEIGHT = 900, 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TRON Collision Test")

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 255, 255)
ORANGE = (255, 150, 0)
WHITE = (255, 255, 255)
TEAL = (0, 180, 150)
GRID_COLOR = (20, 20, 30)

# Load legacy sprites
blue_legacy_big = pygame.image.load("images/blue_lightcycle_legacy.png").convert_alpha()
blue_legacy_big = pygame.transform.flip(blue_legacy_big, True, False)
orange_legacy_big = pygame.image.load("images/orange_lightcycle_legacy.png").convert_alpha()
orange_legacy_big = pygame.transform.flip(orange_legacy_big, True, False)

new_scale_factor = .04
bike_width = int(blue_legacy_big.get_width() * new_scale_factor)
bike_height = int(blue_legacy_big.get_height() * new_scale_factor)

blue_bike_sprite = pygame.transform.scale(blue_legacy_big, (bike_width, bike_height))
orange_bike_sprite = pygame.transform.scale(orange_legacy_big, (bike_width, bike_height))

# Game settings
SPEED = 3  # Slower speed for easier observation
BLOCK_SIZE = 5

# Direction vectors
dirs = {
	"UP": (0, -SPEED),
	"DOWN": (0, SPEED),
	"LEFT": (-SPEED, 0),
	"RIGHT": (SPEED, 0)
}


def draw_tron_grid(surface):
	"""Draw a TRON-style grid background."""
	grid_size = 30
	for x in range(0, WIDTH, grid_size):
		pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
	for y in range(0, HEIGHT, grid_size):
		pygame.draw.line(surface, GRID_COLOR, (0, y), (WIDTH, y), 1)


def blit_bike_with_front_at(screen, sprite, back_pos, direction, back_margin=4):
	"""Render a bike sprite rotated based on direction."""
	dx, dy = direction
	mag = math.hypot(dx, dy)
	if mag == 0:
		screen.blit(sprite, back_pos)
		return

	rad = math.atan2(-dy, dx)
	angle_deg = math.degrees(rad)
	rotated = pygame.transform.rotate(sprite, angle_deg)
	rotated_rect = rotated.get_rect()

	nx, ny = dx / mag, dy / mag
	sprite_w = sprite.get_width()
	local_center = pygame.math.Vector2((sprite_w/2 - back_margin, 0))
	rotated_center = local_center.rotate(-angle_deg)

	back_center_x = back_pos[0] + BLOCK_SIZE / 2
	back_center_y = back_pos[1] + BLOCK_SIZE / 2

	center_x = back_center_x + rotated_center.x
	center_y = back_center_y + rotated_center.y

	rotated_rect.center = (center_x, center_y)
	screen.blit(rotated, rotated_rect.topleft)


def draw_rotated_rect(surface, color, center_x, center_y, width, height, angle_deg, line_width=2):
	"""Draw a rotated rectangle outline for debugging."""
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


def check_bike_collision(bike1, bike2, sprite_w, sprite_h):
	"""Check if two bikes are colliding using rotated rectangle collision."""
	dx1, dy1 = bike1.dir
	mag1 = math.hypot(dx1, dy1)
	dx2, dy2 = bike2.dir
	mag2 = math.hypot(dx2, dy2)

	if mag1 == 0 or mag2 == 0:
		return False

	# Calculate rotation angles
	rad1 = math.atan2(-dy1, dx1)
	angle1_deg = math.degrees(rad1)
	rad2 = math.atan2(-dy2, dx2)
	angle2_deg = math.degrees(rad2)

	# Calculate sprite centers
	back_margin = 4

	back_center_x1 = bike1.pos[0] + 2
	back_center_y1 = bike1.pos[1] + 2
	back_center_x2 = bike2.pos[0] + 2
	back_center_y2 = bike2.pos[1] + 2

	local_center1 = pygame.math.Vector2((sprite_w/2 - back_margin, 0))
	rotated_center1 = local_center1.rotate(-angle1_deg)
	center_x1 = back_center_x1 + rotated_center1.x
	center_y1 = back_center_y1 + rotated_center1.y

	local_center2 = pygame.math.Vector2((sprite_w/2 - back_margin, 0))
	rotated_center2 = local_center2.rotate(-angle2_deg)
	center_x2 = back_center_x2 + rotated_center2.x
	center_y2 = back_center_y2 + rotated_center2.y

	# Use tight hitboxes (90% to ensure immediate detection when hitboxes touch)
	tight_width = sprite_w * 0.9
	tight_height = sprite_h * 0.9

	# Check collision between two rotated rectangles
	# Create AABBs for both bikes
	p1_aabb = pygame.Rect(0, 0, tight_width, tight_height)
	p1_aabb.center = (center_x1, center_y1)
	p2_aabb = pygame.Rect(0, 0, tight_width, tight_height)
	p2_aabb.center = (center_x2, center_y2)

	# Check if either rotated rectangle intersects the other's AABB
	if rotated_rect_intersects_rect(center_x1, center_y1, tight_width, tight_height, angle1_deg, p2_aabb):
		return True, (center_x1, center_y1, angle1_deg), (center_x2, center_y2, angle2_deg), tight_width, tight_height
	elif rotated_rect_intersects_rect(center_x2, center_y2, tight_width, tight_height, angle2_deg, p1_aabb):
		return True, (center_x1, center_y1, angle1_deg), (center_x2, center_y2, angle2_deg), tight_width, tight_height

	return False, None, None, None, None


def run_test():
	import math
	"""Run the collision test with two bikes moving toward each other."""
	# Create bikes
	player1 = Bike(blue_bike_sprite, BLUE, "Player 1")
	player2 = Bike(orange_bike_sprite, ORANGE, "Player 2")

	# Test scenario: bikes passing close by each other
	# Player 1 starts on the left, moving right, slightly above center
	offset = 8  # Vertical offset to prevent collision
	player1.pos = [200, HEIGHT // 2 - offset]
	player1.dir = dirs["RIGHT"]

	# Player 2 starts on the right, moving left, slightly below center
	player2.pos = [WIDTH - 200, HEIGHT // 2 + offset]
	player2.dir = dirs["LEFT"]

	clock = pygame.time.Clock()
	font = pygame.font.Font(None, 36)
	collision_detected = False
	paused = False

	running = True
	while running:
		clock.tick(60)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					paused = not paused
				elif event.key == pygame.K_r:
					# Reset bikes
					player1.pos = [200, HEIGHT // 2 - offset]
					player1.dir = dirs["RIGHT"]
					player1.trail = []
					player2.pos = [WIDTH - 200, HEIGHT // 2 + offset]
					player2.dir = dirs["LEFT"]
					player2.trail = []
					collision_detected = False
				elif event.key == pygame.K_ESCAPE:
					running = False

		if not paused and not collision_detected:
			# Move bikes toward each other
			player1.pos[0] += player1.dir[0]
			player1.pos[1] += player1.dir[1]
			player2.pos[0] += player2.dir[0]
			player2.pos[1] += player2.dir[1]

			# Add trail
			trail_pos1 = (int(player1.pos[0]), int(player1.pos[1]))
			trail_pos2 = (int(player2.pos[0]), int(player2.pos[1]))
			player1.add_trail_point(trail_pos1)
			player2.add_trail_point(trail_pos2)

			# Check collision
			result = check_bike_collision(player1, player2, bike_width, bike_height)
			if result[0]:
				collision_detected = True

		# Draw everything
		WIN.fill(BLACK)
		draw_tron_grid(WIN)

		# Draw trails
		for point in player1.trail:
			pygame.draw.rect(WIN, BLUE, (*point, BLOCK_SIZE, BLOCK_SIZE))
		for point in player2.trail:
			pygame.draw.rect(WIN, ORANGE, (*point, BLOCK_SIZE, BLOCK_SIZE))

		# Draw bikes
		blit_bike_with_front_at(WIN, player1.sprite, player1.pos, player1.dir)
		blit_bike_with_front_at(WIN, player2.sprite, player2.pos, player2.dir)

		# Always draw hitboxes
		# Calculate hitbox parameters for both bikes
		dx1, dy1 = player1.dir
		mag1 = math.hypot(dx1, dy1)
		dx2, dy2 = player2.dir
		mag2 = math.hypot(dx2, dy2)

		if mag1 > 0 and mag2 > 0:
			# Calculate rotation angles
			rad1 = math.atan2(-dy1, dx1)
			angle1_deg = math.degrees(rad1)
			rad2 = math.atan2(-dy2, dx2)
			angle2_deg = math.degrees(rad2)

			back_margin = 4

			# Player 1 hitbox
			back_center_x1 = player1.pos[0] + 2
			back_center_y1 = player1.pos[1] + 2
			local_center1 = pygame.math.Vector2((bike_width/2 - back_margin, 0))
			rotated_center1 = local_center1.rotate(-angle1_deg)
			center_x1 = back_center_x1 + rotated_center1.x
			center_y1 = back_center_y1 + rotated_center1.y

			# Player 2 hitbox
			back_center_x2 = player2.pos[0] + 2
			back_center_y2 = player2.pos[1] + 2
			local_center2 = pygame.math.Vector2((bike_width/2 - back_margin, 0))
			rotated_center2 = local_center2.rotate(-angle2_deg)
			center_x2 = back_center_x2 + rotated_center2.x
			center_y2 = back_center_y2 + rotated_center2.y

			tight_w = bike_width * 0.85
			tight_h = bike_height * 0.85

			# Draw hitboxes - use white when colliding, cyan otherwise
			hitbox_color = WHITE if collision_detected else TEAL
			draw_rotated_rect(WIN, hitbox_color, center_x1, center_y1, tight_w, tight_h, angle1_deg, 2)
			draw_rotated_rect(WIN, hitbox_color, center_x2, center_y2, tight_w, tight_h, angle2_deg, 2)

		# Show collision message if collision detected
		if collision_detected:
			collision_text = font.render("COLLISION DETECTED!", True, WHITE)
			WIN.blit(collision_text, (WIDTH // 2 - 150, 50))

		# Draw instructions
		info_font = pygame.font.Font(None, 24)
		import math
		horizontal_dist = abs(player1.pos[0] - player2.pos[0])
		vertical_dist = abs(player1.pos[1] - player2.pos[1])
		total_dist = math.hypot(horizontal_dist, vertical_dist)
		instructions = [
			"SPACE: Pause/Resume",
			"R: Reset",
			"ESC: Quit",
			f"Status: {'PAUSED' if paused else 'RUNNING'}",
			f"Horizontal: {horizontal_dist:.0f}px",
			f"Vertical: {vertical_dist:.0f}px",
			f"Total Distance: {total_dist:.0f}px"
		]

		y_offset = 10
		for instruction in instructions:
			text = info_font.render(instruction, True, TEAL)
			WIN.blit(text, (10, y_offset))
			y_offset += 25

		pygame.display.update()

	pygame.quit()
	sys.exit()


if __name__ == "__main__":
	print("=== TRON Bike Collision Test ===")
	print("Two bikes will move toward each other head-on.")
	print("Watch for collision detection with hitbox visualization.")
	print("\nControls:")
	print("  SPACE - Pause/Resume")
	print("  R - Reset bikes")
	print("  ESC - Quit")
	print("\nStarting test...")
	run_test()
