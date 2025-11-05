#!/usr/bin/env python3
"""Simple test script for bike-to-bike side collision detection.

This script creates a minimal test environment to verify that when one bike
collides into the side of another bike, their hitboxes touch but do not overlap
(tangent collision).
"""

import pygame
import math
import sys
from pathlib import Path

# Add the project directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from bike import Bike

# Initialize pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 900, 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bike Side Collision Test")

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 255, 255)
ORANGE = (255, 150, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
CYAN = (0, 180, 180)
YELLOW = (255, 255, 0)

# Load sprites
blue_82_big = pygame.image.load("images/blue_lightcycle_82.png").convert_alpha()
blue_82_big = pygame.transform.flip(blue_82_big, True, False)
orange_82_big = pygame.image.load("images/orange_lightcycle_82.png").convert_alpha()
orange_82_big = pygame.transform.flip(orange_82_big, True, False)

scale_factor_82 = .05
width_82 = int(blue_82_big.get_width() * scale_factor_82)
height_82 = int(blue_82_big.get_height() * scale_factor_82)

blue_82_sprite = pygame.transform.scale(blue_82_big, (width_82, height_82))
orange_82_sprite = pygame.transform.scale(orange_82_big, (width_82, height_82))

SPEED = 5
BLOCK_SIZE = 5

# Simplified rendering and collision functions

def blit_bike(screen, sprite, pos, dir_vector, back_margin=4):
    """Simplified bike rendering."""
    sprite_width = sprite.get_width()

    # Get direction
    dx, dy = dir_vector
    mag = math.hypot(dx, dy)
    if mag == 0:
        nx, ny = 1, 0
    else:
        nx, ny = dx / mag, dy / mag

    # Rotate sprite
    angle_rad = math.atan2(-dy, dx)
    angle_deg = math.degrees(angle_rad)
    rotated_sprite = pygame.transform.rotate(sprite, angle_deg)

    # Calculate where to blit
    back_center_x = pos[0] + 2.5
    back_center_y = pos[1] + 2.5

    center_offset = sprite_width / 2 - back_margin
    sprite_center_x = back_center_x + nx * center_offset
    sprite_center_y = back_center_y + ny * center_offset

    rotated_rect = rotated_sprite.get_rect()
    rotated_rect.center = (sprite_center_x, sprite_center_y)

    screen.blit(rotated_sprite, rotated_rect.topleft)

def draw_rotated_rect(screen, color, center_x, center_y, width, height, angle_deg, line_width=2):
    """Draw a rotated rectangle outline."""
    angle_rad = math.radians(angle_deg)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    # Rectangle corners (before rotation)
    hw = width / 2
    hh = height / 2
    corners = [
        (-hw, -hh),
        (hw, -hh),
        (hw, hh),
        (-hw, hh)
    ]

    # Rotate and translate corners
    rotated_corners = []
    for x, y in corners:
        rx = x * cos_a - y * sin_a + center_x
        ry = x * sin_a + y * cos_a + center_y
        rotated_corners.append((rx, ry))

    # Draw lines
    pygame.draw.lines(screen, color, True, rotated_corners, line_width)

def rotated_rects_intersect(x1, y1, w1, h1, angle1, x2, y2, w2, h2, angle2):
    """Check if two rotated rectangles intersect using SAT."""
    def get_corners(cx, cy, width, height, angle_rad):
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        hw = width / 2
        hh = height / 2
        corners = []
        for dx, dy in [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]:
            rx = dx * cos_a - dy * sin_a + cx
            ry = dx * sin_a + dy * cos_a + cy
            corners.append((rx, ry))
        return corners

    def get_axes(corners):
        axes = []
        for i in range(4):
            p1 = corners[i]
            p2 = corners[(i + 1) % 4]
            edge = (p2[0] - p1[0], p2[1] - p1[1])
            length = math.hypot(edge[0], edge[1])
            if length > 0:
                normal = (-edge[1] / length, edge[0] / length)
                axes.append(normal)
        return axes

    def project(corners, axis):
        dots = [c[0] * axis[0] + c[1] * axis[1] for c in corners]
        return min(dots), max(dots)

    corners1 = get_corners(x1, y1, w1, h1, math.radians(angle1))
    corners2 = get_corners(x2, y2, w2, h2, math.radians(angle2))

    axes = get_axes(corners1) + get_axes(corners2)

    for axis in axes:
        min1, max1 = project(corners1, axis)
        min2, max2 = project(corners2, axis)
        if max1 < min2 or max2 < min1:
            return False

    return True

def check_bike_collision(bike1, bike2, sprite_width, sprite_height):
    """Check if two bikes' hitboxes intersect."""
    back_margin = 4
    tight_width = sprite_width * 0.9
    tight_height = sprite_height * 0.9

    def get_bike_hitbox_center(bike):
        pos_x, pos_y = bike.pos
        dir_x, dir_y = bike.dir

        back_center_x = pos_x + 2
        back_center_y = pos_y + 2

        mag = math.hypot(dir_x, dir_y)
        if mag > 0:
            nx, ny = dir_x / mag, dir_y / mag
        else:
            nx, ny = 1, 0

        body_offset = sprite_width / 2 - back_margin
        body_center_x = back_center_x + nx * body_offset
        body_center_y = back_center_y + ny * body_offset

        angle_deg = math.degrees(math.atan2(dir_y, dir_x))

        return body_center_x, body_center_y, angle_deg

    x1, y1, angle1 = get_bike_hitbox_center(bike1)
    x2, y2, angle2 = get_bike_hitbox_center(bike2)

    return rotated_rects_intersect(
        x1, y1, tight_width, tight_height, angle1,
        x2, y2, tight_width, tight_height, angle2
    )

def draw_bike_hitboxes(screen, bike, sprite_width, sprite_height, color_body, color_front):
    """Draw hitboxes for visualization."""
    back_margin = 4
    tight_width = sprite_width * 0.9
    tight_height = sprite_height * 0.9

    pos_x, pos_y = bike.pos
    dir_x, dir_y = bike.dir

    back_center_x = pos_x + 2
    back_center_y = pos_y + 2

    mag = math.hypot(dir_x, dir_y)
    if mag > 0:
        nx, ny = dir_x / mag, dir_y / mag
    else:
        nx, ny = 1, 0

    angle_deg = math.degrees(math.atan2(dir_y, dir_x))

    # Body hitbox
    body_offset = sprite_width / 2 - back_margin
    body_center_x = back_center_x + nx * body_offset
    body_center_y = back_center_y + ny * body_offset

    draw_rotated_rect(screen, color_body, body_center_x, body_center_y,
                     tight_width, tight_height, angle_deg, line_width=2)

    # Front hitbox
    front_hitbox_width = sprite_width * 0.25
    front_hitbox_height = tight_height
    front_offset = (sprite_width - back_margin) - (front_hitbox_width / 2)
    front_center_x = back_center_x + nx * front_offset
    front_center_y = back_center_y + ny * front_offset

    draw_rotated_rect(screen, color_front, front_center_x, front_center_y,
                     front_hitbox_width, front_hitbox_height, angle_deg, line_width=2)

def test_side_collision():
    """Test a bike colliding into the side of another bike."""

    print("=" * 60)
    print("BIKE SIDE COLLISION TEST")
    print("=" * 60)
    print("\nTest scenario:")
    print("- Blue bike (player1) moves horizontally to the right")
    print("- Orange bike (player2) moves vertically downward")
    print("- Orange bike will collide into the side of blue bike")
    print("- Expected: Hitboxes should be tangent (touching but not overlapping)")
    print("\nPress SPACE to advance frame-by-frame")
    print("Press Q to quit")
    print("=" * 60)

    # Create bikes
    player1 = Bike(blue_82_sprite, BLUE, "Blue")
    player1.pos = [300, 450]
    player1.dir = (SPEED, 0)  # Moving right
    player1.trail = [(300, 450)]

    player2 = Bike(orange_82_sprite, ORANGE, "Orange")
    player2.pos = [450, 300]
    player2.dir = (0, SPEED)  # Moving down
    player2.trail = [(450, 300)]

    clock = pygame.time.Clock()
    paused = True
    frame_count = 0
    collision_detected = False
    collision_frame = None

    font = pygame.font.Font(None, 24)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = False
                elif event.key == pygame.K_q:
                    running = False

        if not paused and not collision_detected:
            # Move bikes
            player1.pos[0] += player1.dir[0]
            player1.pos[1] += player1.dir[1]
            player1.trail.append(tuple(player1.pos))

            player2.pos[0] += player2.dir[0]
            player2.pos[1] += player2.dir[1]
            player2.trail.append(tuple(player2.pos))

            # Check for collision
            if check_bike_collision(player1, player2, width_82, height_82):
                collision_detected = True
                collision_frame = frame_count
                print(f"\n{'!' * 60}")
                print(f"COLLISION DETECTED AT FRAME {frame_count}")
                print(f"{'!' * 60}")
                print(f"\nBlue bike position: ({player1.pos[0]:.2f}, {player1.pos[1]:.2f})")
                print(f"Blue bike direction: {player1.dir}")
                print(f"\nOrange bike position: ({player2.pos[0]:.2f}, {player2.pos[1]:.2f})")
                print(f"Orange bike direction: {player2.dir}")

                # Calculate distance between bikes
                dist = math.hypot(player1.pos[0] - player2.pos[0],
                                 player1.pos[1] - player2.pos[1])
                print(f"\nDistance between bike centers: {dist:.2f} pixels")

            frame_count += 1
            paused = True  # Pause after each frame

        # Draw
        WIN.fill(BLACK)

        # Draw trails
        for pos in player1.trail:
            pygame.draw.rect(WIN, player1.color, (pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))
        for pos in player2.trail:
            pygame.draw.rect(WIN, player2.color, (pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))

        # Draw bikes
        blit_bike(WIN, player1.sprite, player1.pos, player1.dir, 4)
        blit_bike(WIN, player2.sprite, player2.pos, player2.dir, 4)

        # Draw hitboxes
        draw_bike_hitboxes(WIN, player1, width_82, height_82, CYAN, WHITE)
        draw_bike_hitboxes(WIN, player2, width_82, height_82, (180, 100, 0), YELLOW)

        # Draw info text
        info_texts = [
            f"Frame: {frame_count}",
            f"Blue pos: ({player1.pos[0]:.1f}, {player1.pos[1]:.1f})",
            f"Orange pos: ({player2.pos[0]:.1f}, {player2.pos[1]:.1f})",
        ]

        if collision_detected:
            info_texts.append(f"COLLISION at frame {collision_frame}")
            dist = math.hypot(player1.pos[0] - player2.pos[0],
                             player1.pos[1] - player2.pos[1])
            info_texts.append(f"Distance: {dist:.2f}px")

        info_texts.append("")
        info_texts.append("SPACE: Next frame")
        info_texts.append("Q: Quit")

        y_offset = 10
        for text in info_texts:
            if "COLLISION" in text:
                color = RED
            else:
                color = WHITE
            surface = font.render(text, True, color)
            WIN.blit(surface, (10, y_offset))
            y_offset += 25

        pygame.display.flip()
        clock.tick(60)

        # Stop after collision is detected and displayed
        if collision_detected and frame_count > collision_frame + 5:
            print("\nTest complete. Close window or press Q to exit.")
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting = False
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            waiting = False
                            running = False
                clock.tick(30)

    pygame.quit()
    print("\nTest ended.")

if __name__ == '__main__':
    test_side_collision()
