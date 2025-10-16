import pygame
pygame.init()

# --- Setup ---
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Example colors
BLUE = (0, 200, 255)
BLACK = (0, 0, 0)

# Bike info
bike_speed = 4
blue_bike_big = pygame.image.load("blue_cycle.png").convert_alpha()
scale_factor = .05
bike_width = int(blue_bike_big.get_width() * scale_factor)
bike_height = int(blue_bike_big.get_height() * scale_factor)
bike_img = pygame.transform.scale(blue_bike_big, (bike_width, bike_height))
bike_rect = bike_img.get_rect(center=(400, 300))
direction = pygame.Vector2(1, 0)  # start moving right
trail = []
paused = False  # toggle state

def rotate_bike(bike_rect, direction, new_dir):
    """Rotate bike around its rear wheel (the trail connection point)."""
    # Get pivot (rear of bike)
    pivot = pygame.Vector2(bike_rect.center)
    offset = pygame.Vector2(0, bike_rect.width // 2 - 6).rotate(-direction.angle_to((1, 0)))

    # Compute the actual pivot position in world space
    pivot_point = pivot + offset

    # Update direction
    direction.update(new_dir)

    # After changing direction, move the rect so that the pivot point stays fixed
    new_offset = pygame.Vector2(0, bike_rect.width // 2 - 6).rotate(-direction.angle_to((1, 0)))
    bike_rect.center = pivot_point - new_offset

    return direction

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Toggle pause with space
            if event.key == pygame.K_SPACE:
                paused = not paused

    # --- Movement control (only when not paused) ---
    if not paused:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            direction = pygame.Vector2(0, -1)
        elif keys[pygame.K_DOWN]:
            direction = pygame.Vector2(0, 1)
        elif keys[pygame.K_LEFT]:
            direction = pygame.Vector2(-1, 0)
        elif keys[pygame.K_RIGHT]:
            direction = pygame.Vector2(1, 0)

        # --- Move bike ---
        old_pos = bike_rect.center  # remember position *before* moving
        bike_rect.centerx += direction.x * bike_speed
        bike_rect.centery += direction.y * bike_speed

        # Add the *old position* to the trail
        trail.append(old_pos)

    # --- Draw everything ---
    screen.fill(BLACK)

    # 1️⃣ Draw the trail first
    if len(trail) > 1:
        pygame.draw.lines(screen, BLUE, False, trail, 4)

    # 2️⃣ Draw the bike *afterward*
    # Rotate sprite visually
    angle = -direction.angle_to(pygame.Vector2(1, 0))
    rotated_bike = pygame.transform.rotate(bike_img, angle)
    rotated_rect = rotated_bike.get_rect(center=bike_rect.center)
    screen.blit(rotated_bike, rotated_rect)

    # Optional: show "PAUSED" message
    if paused:
        font = pygame.font.Font(None, 60)
        text = font.render("PAUSED", True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=(400, 300)))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
