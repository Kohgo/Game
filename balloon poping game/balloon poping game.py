import pygame
import random
import sys

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Balloon Pop - Reveal on Pop")

# Load background
try:
# Load background and sounds from same folder
    background_img = pygame.image.load(r"background.png")
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

except pygame.error:
    print("Background image not found! Using solid color instead")
    background_img = None

# Load sound effects
try:

    pump_sound = pygame.mixer.Sound(r"pump.mp3")
    pop_sound = pygame.mixer.Sound(r"pop.mp3")

except pygame.error:
    print("Sound files not found! Sound will be disabled.")
    pump_sound = None
    pop_sound = None

font = pygame.font.SysFont('Arial', 36)
clock = pygame.time.Clock()

# Colors
RED = (255, 100, 100)
DARK_RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PLAYER_COLORS = [(255, 0, 0), (0, 180, 0), (0, 0, 255), (200, 200, 0)]

# Game variables
MAX_PUMPS = random.randint(50, 100)
current_player = 0
game_over = False
scores = [0] * 4
total_pumps = 0
pumps_remaining = 5
explosion_radius = 0
shake_offset = 0
shake_timer = 0
revealed_max = None

def show_text(text, x, y, color=BLACK, size=36, bold=False):
    font = pygame.font.SysFont('Arial', size, bold=bold)
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

def draw_balloon(presses):
    global explosion_radius

    if game_over:
        if explosion_radius < 200:
            explosion_radius += 5
        pygame.draw.circle(screen, (255, 165, 0), (WIDTH//2, HEIGHT//2), explosion_radius)
        pygame.draw.circle(screen, (255, 255, 0), (WIDTH//2, HEIGHT//2), explosion_radius-20)

        if revealed_max is not None:
            show_text(f"Balloon would pop at: {revealed_max} pumps", 
                     WIDTH//2-200, HEIGHT//2+50, DARK_RED, 42, True)
        return

    radius = 50 + presses * 5
    center_x = WIDTH // 2 + shake_offset
    center_y = HEIGHT // 2 + shake_offset

    color_progress = min(1.0, presses / MAX_PUMPS)
    color = (
        int(RED[0] + (DARK_RED[0]-RED[0]) * color_progress),
        int(RED[1] + (DARK_RED[1]-RED[1]) * color_progress),
        int(RED[2] + (DARK_RED[2]-RED[2]) * color_progress)
    )

    pygame.draw.circle(screen, color, (center_x, center_y), radius)
    pygame.draw.circle(screen, BLACK, (center_x, center_y), radius, 2)
    pygame.draw.rect(screen, BLACK, (center_x-5, center_y+radius-5, 10, 15))
    show_text(str(presses), center_x-15, center_y-15, BLACK, 28)

def reset_game():
    global MAX_PUMPS, game_over, explosion_radius, total_pumps, pumps_remaining, revealed_max
    MAX_PUMPS = random.randint(50, 100)
    game_over = False
    explosion_radius = 0
    total_pumps = 0
    pumps_remaining = 5
    revealed_max = None

def next_player():
    global current_player, pumps_remaining
    current_player = (current_player + 1) % 4
    pumps_remaining = 5

# Main game loop
while True:
    if background_img:
        screen.blit(background_img, (0, 0))
    else:
        screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if not game_over:
                if event.key == pygame.K_SPACE and pumps_remaining > 0:
                    total_pumps += 1
                    pumps_remaining -= 1

                    if pump_sound:
                        pump_sound.play()

                    if total_pumps > MAX_PUMPS * 0.8:
                        shake_timer = 5

                    if total_pumps >= MAX_PUMPS:
                        game_over = True
                        shake_timer = 30
                        scores[current_player] += 1
                        revealed_max = MAX_PUMPS
                        if pop_sound:
                            pop_sound.play()

                elif event.key == pygame.K_RETURN and pumps_remaining < 5:
                    next_player()

            elif event.key == pygame.K_r:
                reset_game()
                scores = [0] * 4

            elif game_over and event.key == pygame.K_RETURN:
                reset_game()
                next_player()

    if shake_timer > 0:
        shake_offset = random.randint(-5, 5)
        shake_timer -= 1
    else:
        shake_offset = 0

    draw_balloon(total_pumps)

    show_text(f"PLAYER {current_player + 1}", 20, 20, PLAYER_COLORS[current_player], 42, True)
    show_text(f"Pumps left: {pumps_remaining}/5", 20, 70)

    if not game_over:
        if pumps_remaining > 0:
            show_text("SPACE: Pump  |  ENTER: Pass Turn", WIDTH//2-180, HEIGHT-60, BLACK, 32)
        else:
            show_text("PRESS ENTER TO PASS TURN", WIDTH//2-150, HEIGHT-60, (200, 0, 0), 32)
    else:
        show_text(f"PLAYER {current_player + 1} POPPED IT!", WIDTH//2-180, HEIGHT-100, DARK_RED, 42, True)
        show_text("ENTER: New Balloon  |  R: Reset Game", WIDTH//2-200, HEIGHT-50, BLACK, 32)

    for i in range(4):
        show_text(f"P{i+1}: {scores[i]} pops", WIDTH-150, 30 + i*40, PLAYER_COLORS[i], 32)

    pygame.display.flip()
    clock.tick(60)
