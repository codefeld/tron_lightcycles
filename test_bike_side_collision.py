#!/usr/bin/env python3
"""Test script for bike-to-bike side collision detection.

This script tests that when one bike collides into the side of another bike,
their hitboxes touch but do not overlap (tangent collision).
"""

import pygame
import sys
from pathlib import Path

# Add the project directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from bike import Bike
from functions import *
import main

# Initialize pygame
pygame.init()
pygame.mixer.init()

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

# Set up global variables needed by functions
main.WIDTH = WIDTH
main.HEIGHT = HEIGHT
main.WIN = WIN
main.theme = "82"
main.width_82 = width_82
main.height_82 = height_82
main.blue_82_sprite = blue_82_sprite
main.orange_82_sprite = orange_82_sprite
main.obstacles = []
main.powerups = []
main.show_debug_hitboxes = True
main.SPEED = 5
main.BLOCK_SIZE = 5

# Import necessary globals
from main import (WIDTH, HEIGHT, WIN, theme, width_82, height_82,
                  blue_82_sprite, orange_82_sprite, obstacles, powerups,
                  show_debug_hitboxes, SPEED, BLOCK_SIZE)

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
    # Blue bike: positioned left, moving right
    player1 = Bike(blue_82_sprite, BLUE, "Blue")
    player1.pos = [300, 450]
    player1.dir = (SPEED, 0)  # Moving right
    player1.trail = [(300, 450)]

    # Orange bike: positioned above blue bike's path, moving down
    player2 = Bike(orange_82_sprite, ORANGE, "Orange")
    player2.pos = [450, 300]
    player2.dir = (0, SPEED)  # Moving down
    player2.trail = [(450, 300)]

    # Set global players for functions
    main.player1 = player1
    main.player2 = player2

    clock = pygame.time.Clock()
    paused = True
    frame_count = 0
    collision_detected = False
    collision_frame = None

    # Font for display
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
            current_time = pygame.time.get_ticks()

            # Move player1 (blue) - should not collide
            collided1 = step_move_player(player1, player2, current_time)

            # Move player2 (orange) - may collide with player1
            collided2 = step_move_player(player2, player1, current_time)

            # Add to trails
            player1.trail.append(tuple(player1.pos))
            player2.trail.append(tuple(player2.pos))

            if collided1 or collided2:
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
                dist = ((player1.pos[0] - player2.pos[0])**2 +
                       (player1.pos[1] - player2.pos[1])**2)**0.5
                print(f"\nDistance between bike centers: {dist:.2f} pixels")

                # Calculate expected tangent distance
                # For side collision, the hitboxes should just touch
                expected_dist = (width_82 * 0.9) * 0.9  # Approximate (both body hitboxes at 90%)
                print(f"Expected tangent distance (approx): {expected_dist:.2f} pixels")

                overlap = expected_dist - dist
                if overlap > 0.5:
                    print(f"\n[WARNING] Hitboxes may be overlapping by ~{overlap:.2f} pixels")
                elif overlap < -2:
                    print(f"\n[WARNING] Bikes may be too far apart (~{-overlap:.2f} pixels gap)")
                else:
                    print(f"\n[SUCCESS] Hitboxes appear to be tangent (within tolerance)")

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
        blit_bike_with_front_at(WIN, player1.sprite, player1.pos, player1.dir, 4)
        blit_bike_with_front_at(WIN, player2.sprite, player2.pos, player2.dir, 4)

        # Draw hitboxes
        draw_debug_hitboxes()

        # Draw info text
        info_texts = [
            f"Frame: {frame_count}",
            f"Blue pos: ({player1.pos[0]:.1f}, {player1.pos[1]:.1f})",
            f"Orange pos: ({player2.pos[0]:.1f}, {player2.pos[1]:.1f})",
        ]

        if collision_detected:
            info_texts.append(f"COLLISION at frame {collision_frame}")
            # Calculate and display current distance
            dist = ((player1.pos[0] - player2.pos[0])**2 +
                   (player1.pos[1] - player2.pos[1])**2)**0.5
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
            # Wait for user to close or press Q
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
