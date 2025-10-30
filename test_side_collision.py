"""Test script for front-vs-side bike collision detection.

This script creates scenarios where one bike's front collides with the side
of another bike to test the collision detection logic from functions.py.
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
pygame.display.set_caption("TRON Side Collision Test")

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 255, 255)
ORANGE = (255, 150, 0)
WHITE = (255, 255, 255)
TEAL = (0, 180, 150)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
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
SPEED = 3
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


def check_front_vs_side_collision(bike1, bike2, sprite_w, sprite_h):
	"""Check collision between bike1's front and bike2's side.
	Returns: (collision_detected, bike1_front_info, bike2_body_info)
	"""
	dx1, dy1 = bike1.dir
	mag1 = math.hypot(dx1, dy1)
	dx2, dy2 = bike2.dir
	mag2 = math.hypot(dx2, dy2)

	if mag1 == 0 or mag2 == 0:
		return False, None, None

	# Normalize direction vectors
	nx1, ny1 = dx1 / mag1, dy1 / mag1
	nx2, ny2 = dx2 / mag2, dy2 / mag2

	# Calculate rotation angles
	rad1 = math.atan2(-dy1, dx1)
	angle1_deg = math.degrees(rad1)
	rad2 = math.atan2(-dy2, dx2)
	angle2_deg = math.degrees(rad2)

	# Calculate bike1's front hitbox position (at 85% of bike length)
	front_offset = sprite_w * 0.85
	front1_x = bike1.pos[0] + 2 + nx1 * front_offset
	front1_y = bike1.pos[1] + 2 + ny1 * front_offset

	# Front hitbox dimensions - small rectangle at the tip
	front_hitbox_width = sprite_w * 0.25
	front_hitbox_height = sprite_h * 0.9

	# Calculate bike2's full body hitbox center
	back_margin = 4
	back_center_x2 = bike2.pos[0] + 2
	back_center_y2 = bike2.pos[1] + 2

	local_center2 = pygame.math.Vector2((sprite_w/2 - back_margin, 0))
	rotated_center2 = local_center2.rotate(-angle2_deg)
	center_x2 = back_center_x2 + rotated_center2.x
	center_y2 = back_center_y2 + rotated_center2.y

	# Full body hitboxes (90% of sprite size)
	full_body_width = sprite_w * 0.9
	full_body_height = sprite_h * 0.9

	# Create AABB for bike2's body
	bike2_body_aabb = pygame.Rect(0, 0, full_body_width, full_body_height)
	bike2_body_aabb.center = (center_x2, center_y2)

	# Check if bike1's front touches bike2's body
	collision = rotated_rect_intersects_rect(
		front1_x, front1_y, front_hitbox_width, front_hitbox_height,
		angle1_deg, bike2_body_aabb
	)

	front_info = (front1_x, front1_y, front_hitbox_width, front_hitbox_height, angle1_deg)
	body_info = (center_x2, center_y2, full_body_width, full_body_height, angle2_deg)

	return collision, front_info, body_info


def run_test():
	"""Run the side collision test with various scenarios."""
	# Create bikes
	player1 = Bike(blue_bike_sprite, BLUE, "Player 1")
	player2 = Bike(orange_bike_sprite, ORANGE, "Player 2")

	# Test scenarios - Blue bike hits Orange bike's side
	scenarios = [
		{
			"name": "Blue T-bones Orange from the left",
			"p1_pos": [WIDTH // 2 - 150, HEIGHT // 2],
			"p1_dir": dirs["RIGHT"],
			"p2_pos": [WIDTH // 2, HEIGHT // 2 - 100],
			"p2_dir": dirs["DOWN"],
			"description": "Blue moving right hits Orange's left side (perpendicular)"
		},
		{
			"name": "Blue T-bones Orange from above",
			"p1_pos": [WIDTH // 2, HEIGHT // 2 - 150],
			"p1_dir": dirs["DOWN"],
			"p2_pos": [WIDTH // 2 + 100, HEIGHT // 2],
			"p2_dir": dirs["LEFT"],
			"description": "Blue moving down hits Orange's top side (perpendicular)"
		},
		{
			"name": "Blue hits Orange from behind (rear-end)",
			"p1_pos": [WIDTH // 2 - 80, HEIGHT // 2],
			"p1_dir": dirs["RIGHT"],
			"p2_pos": [WIDTH // 2, HEIGHT // 2],
			"p2_dir": dirs["RIGHT"],
			"description": "Blue chasing Orange from behind, hits rear"
		},
		{
			"name": "Blue cuts across Orange's path",
			"p1_pos": [WIDTH // 2 - 100, HEIGHT // 2 - 20],
			"p1_dir": dirs["RIGHT"],
			"p2_pos": [WIDTH // 2 - 50, HEIGHT // 2 - 100],
			"p2_dir": dirs["DOWN"],
			"description": "Blue crosses in front of Orange, side impact"
		},
		{
			"name": "Blue misses Orange (near miss)",
			"p1_pos": [WIDTH // 2 - 150, HEIGHT // 2 - 35],
			"p1_dir": dirs["RIGHT"],
			"p2_pos": [WIDTH // 2, HEIGHT // 2 - 100],
			"p2_dir": dirs["DOWN"],
			"description": "Blue passes just ahead of Orange - no collision"
		}
	]

	current_scenario = 0
	scenario = scenarios[current_scenario]

	# Initialize first scenario
	player1.pos = list(scenario["p1_pos"])
	player1.dir = scenario["p1_dir"]
	player2.pos = list(scenario["p2_pos"])
	player2.dir = scenario["p2_dir"]

	clock = pygame.time.Clock()
	font = pygame.font.Font(None, 28)
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
					# Reset current scenario
					player1.pos = list(scenario["p1_pos"])
					player1.dir = scenario["p1_dir"]
					player2.pos = list(scenario["p2_pos"])
					player2.dir = scenario["p2_dir"]
					collision_detected = False
				elif event.key == pygame.K_n:
					# Next scenario
					current_scenario = (current_scenario + 1) % len(scenarios)
					scenario = scenarios[current_scenario]
					player1.pos = list(scenario["p1_pos"])
					player1.dir = scenario["p1_dir"]
					player2.pos = list(scenario["p2_pos"])
					player2.dir = scenario["p2_dir"]
					collision_detected = False
				elif event.key == pygame.K_p:
					# Previous scenario
					current_scenario = (current_scenario - 1) % len(scenarios)
					scenario = scenarios[current_scenario]
					player1.pos = list(scenario["p1_pos"])
					player1.dir = scenario["p1_dir"]
					player2.pos = list(scenario["p2_pos"])
					player2.dir = scenario["p2_dir"]
					collision_detected = False
				elif event.key == pygame.K_ESCAPE:
					running = False

		if not paused and not collision_detected:
			# Move bikes
			player1.pos[0] += player1.dir[0]
			player1.pos[1] += player1.dir[1]
			player2.pos[0] += player2.dir[0]
			player2.pos[1] += player2.dir[1]

			# Check collision
			result = check_front_vs_side_collision(player1, player2, bike_width, bike_height)
			if result[0]:
				collision_detected = True

		# Draw everything
		WIN.fill(BLACK)
		draw_tron_grid(WIN)

		# Draw bikes
		blit_bike_with_front_at(WIN, player1.sprite, player1.pos, player1.dir)
		blit_bike_with_front_at(WIN, player2.sprite, player2.pos, player2.dir)

		# Draw hitboxes
		result = check_front_vs_side_collision(player1, player2, bike_width, bike_height)
		if result[1] and result[2]:
			front_info = result[1]
			body_info = result[2]

			# Draw Blue's front hitbox (green if no collision, red if collision)
			front_color = RED if collision_detected else GREEN
			draw_rotated_rect(WIN, front_color, front_info[0], front_info[1],
							front_info[2], front_info[3], front_info[4], 2)

			# Draw Orange's body hitbox (always teal)
			draw_rotated_rect(WIN, TEAL, body_info[0], body_info[1],
							body_info[2], body_info[3], body_info[4], 2)

		# Show collision message if collision detected
		if collision_detected:
			collision_text = font.render("COLLISION! Blue loses", True, RED)
			WIN.blit(collision_text, (WIDTH // 2 - 120, 50))

		# Draw scenario info
		info_font = pygame.font.Font(None, 22)
		instructions = [
			f"Scenario {current_scenario + 1}/{len(scenarios)}: {scenario['name']}",
			scenario['description'],
			"",
			"Controls:",
			"  SPACE - Pause/Resume",
			"  R - Reset scenario",
			"  N - Next scenario",
			"  P - Previous scenario",
			"  ESC - Quit",
			"",
			f"Status: {'PAUSED' if paused else 'RUNNING'}",
			f"Collision: {'YES' if collision_detected else 'NO'}",
			"",
			"Blue bike front (green/red) vs Orange bike body (teal)"
		]

		y_offset = 10
		for instruction in instructions:
			text = info_font.render(instruction, True, WHITE if instruction else BLACK)
			WIN.blit(text, (10, y_offset))
			y_offset += 22

		pygame.display.update()

	pygame.quit()
	sys.exit()


if __name__ == "__main__":
	print("=== TRON Side Collision Test ===")
	print("Testing front-vs-side collision detection.")
	print("Blue bike's front should only collide with Orange bike's body.")
	print("\nControls:")
	print("  SPACE - Pause/Resume")
	print("  R - Reset scenario")
	print("  N - Next scenario")
	print("  P - Previous scenario")
	print("  ESC - Quit")
	print("\nStarting test...")
	run_test()
