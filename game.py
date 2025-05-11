import pygame
import random
import sys
import math
from enum import Enum
import os

# Initialize pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()  # Initialize mixer for sounds

# Game states
class GameState(Enum):
    MENU = 1
    MODE_SELECT = 2
    DIFFICULTY_SELECT = 3
    CUSTOMIZATION = 4
    PLAYING = 5
    GAME_OVER = 6

# Game modes
class GameMode(Enum):
    HUMAN_VS_AI = 1
    AI_VS_AI = 2

# Power-up types
class PowerUpType(Enum):
    FREEZE = 1
    POINTS = 2

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
CELL_SIZE = 25 # Adjusted to make the grid fit better with sidebar
INFO_PANEL_WIDTH = 250 # Width for scores, timer, and legend
GAME_AREA_WIDTH = WIDTH - INFO_PANEL_WIDTH


# Pink aesthetic colors
PINK_LIGHT = (255, 200, 230)
PINK_MEDIUM = (255, 150, 200)
PINK_DARK = (230, 100, 170)
HOT_PINK = (255, 50, 150)
PASTEL_BLUE = (70, 130, 180)
PASTEL_GREEN = (180, 255, 200)
PASTEL_YELLOW = (255, 255, 180)
PASTEL_PURPLE = (220, 180, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ICE_BLUE = (0, 191, 255)
GOLD = (255, 215, 0)

# Game settings
TIME_LIMIT = 60
NORMAL_SPEED = 7
HARD_SPEED = 12
AI_NORMAL_SMARTNESS = 0.7 # Probability of making a smart move
AI_HARD_SMARTNESS = 0.9
FREEZE_DURATION = 5  # Seconds to freeze opponent
POINTS_BONUS = 20    # Points given by point power-up

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cute Territory Game")
clock = pygame.time.Clock()

# Initialize game variables
board = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
scores = {"blue": 0, "green": 0}
player_positions = {"blue": (1, 1), "green": (GRID_SIZE-2, GRID_SIZE-2)}
game_state = GameState.MENU
game_mode = GameMode.HUMAN_VS_AI
difficulty = "normal"

# Power-up variables
power_ups = []  # Will store (x, y, type) tuples
frozen_until = {"blue": 0, "green": 0}  # Timestamp when freeze effect ends

# Customization options
player_colors = {
    "blue": PASTEL_BLUE,
    "green": PASTEL_GREEN
}
custom_player_colors = {
    "blue": PASTEL_BLUE,
    "green": PASTEL_GREEN
}
available_colors = [PASTEL_BLUE, PASTEL_GREEN, PASTEL_YELLOW, PASTEL_PURPLE, HOT_PINK]

# Fonts
TITLE_FONT = pygame.font.Font(None, 64)
MENU_FONT = pygame.font.Font(None, 40)
GAME_FONT = pygame.font.Font(None, 30)

# Load sounds
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    music_path = os.path.join(current_dir, "background.mp3")

    if os.path.exists(music_path):
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.5) 
        has_music = True
    else:
        print(f"Music file not found at: {music_path}")
        has_music = False
except Exception as e:
    print(f"Error loading music: {e}")
    has_music = False

def spawn_power_up():
    if len(power_ups) < 3:
        for _ in range(10):
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)

            if board[x][y] is None and (x, y) not in [pos[:2] for pos in power_ups]:
                # Ensure power-ups don't spawn directly on players
                if (x,y) != player_positions["blue"] and (x,y) != player_positions["green"]:
                     # Check not too close to player current positions (more dynamic)
                    if (abs(x - player_positions["blue"][0]) > 2 or abs(y - player_positions["blue"][1]) > 2) and \
                       (abs(x - player_positions["green"][0]) > 2 or abs(y - player_positions["green"][1]) > 2):
                        power_type = random.choice(list(PowerUpType))
                        power_ups.append((x, y, power_type))
                        break

def draw_board():
    # Draw the game area background (sidebar will be drawn over screen.fill)
    game_area_surface = pygame.Surface((GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE))
    game_area_surface.fill(PINK_LIGHT) # Background for the grid area

    for x_grid in range(GRID_SIZE):
        for y_grid in range(GRID_SIZE):
            rect = pygame.Rect(x_grid * CELL_SIZE, y_grid * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            
            # Draw base cell
            if board[x_grid][y_grid] is None:
                pygame.draw.rect(game_area_surface, WHITE, rect)
            elif board[x_grid][y_grid] == "blue":
                pygame.draw.rect(game_area_surface, custom_player_colors["blue"], rect)
            elif board[x_grid][y_grid] == "green":
                pygame.draw.rect(game_area_surface, custom_player_colors["green"], rect)
            
            pygame.draw.rect(game_area_surface, PINK_MEDIUM, rect, 1) # Grid lines

    # Draw power-ups on the game_area_surface
    for x_pu, y_pu, power_type in power_ups:
        center_x = x_pu * CELL_SIZE + CELL_SIZE // 2
        center_y = y_pu * CELL_SIZE + CELL_SIZE // 2

        if power_type == PowerUpType.FREEZE:
            pygame.draw.circle(game_area_surface, ICE_BLUE, (center_x, center_y), CELL_SIZE // 2 - 2)
            for angle_deg in range(0, 360, 60):
                rad = math.radians(angle_deg)
                line_x = center_x + math.cos(rad) * (CELL_SIZE // 3)
                line_y = center_y + math.sin(rad) * (CELL_SIZE // 3)
                pygame.draw.line(game_area_surface, WHITE, (center_x, center_y), (line_x, line_y), 2)
        elif power_type == PowerUpType.POINTS:
            pygame.draw.circle(game_area_surface, GOLD, (center_x, center_y), CELL_SIZE // 2 - 2)
            star_points = []
            for i in range(5):
                angle = i * 2 * math.pi / 5 - math.pi / 2
                outer_x = center_x + math.cos(angle) * (CELL_SIZE // 3)
                outer_y = center_y + math.sin(angle) * (CELL_SIZE // 3)
                star_points.append((outer_x, outer_y))
                angle += math.pi / 5
                inner_x = center_x + math.cos(angle) * (CELL_SIZE // 6)
                inner_y = center_y + math.sin(angle) * (CELL_SIZE // 6)
                star_points.append((inner_x, inner_y))
            pygame.draw.polygon(game_area_surface, WHITE, star_points)

    # Draw players on the game_area_surface
    for player, pos in player_positions.items():
        x_player, y_player = pos
        center = (x_player * CELL_SIZE + CELL_SIZE // 2, y_player * CELL_SIZE + CELL_SIZE // 2)
        current_time = pygame.time.get_ticks() / 1000

        if frozen_until[player] > current_time:
            pygame.draw.circle(game_area_surface, ICE_BLUE, center, CELL_SIZE // 2)
            pygame.draw.circle(game_area_surface, custom_player_colors[player], center, CELL_SIZE // 2 - 3)
            for i in range(4):
                angle = i * math.pi / 2
                ice_x = center[0] + math.cos(angle) * (CELL_SIZE // 2 - 1)
                ice_y = center[1] + math.sin(angle) * (CELL_SIZE // 2 - 1)
                pygame.draw.circle(game_area_surface, WHITE, (int(ice_x), int(ice_y)), 2)
        else:
            pygame.draw.circle(game_area_surface, custom_player_colors[player], center, CELL_SIZE // 2 - 2)
    
    screen.blit(game_area_surface, (0,0)) # Blit the prepared game area to the main screen


def draw_scores_and_timer(elapsed_time):
    # Sidebar background - fill the rest of the screen
    sidebar_rect = pygame.Rect(GRID_SIZE * CELL_SIZE, 0, INFO_PANEL_WIDTH, HEIGHT)
    screen.fill(PINK_LIGHT, sidebar_rect) # Fill sidebar area

    sidebar_x_offset = GRID_SIZE * CELL_SIZE + 20 # Start drawing elements 20px into the sidebar
    
    blue_score_text = f"Blue: {scores['blue']}"
    green_score_text = f"Green: {scores['green']}"
    time_left = TIME_LIMIT - elapsed_time
    time_text = f"Time: {int(time_left) if time_left >= 0 else 0}" # Ensure time doesn't go negative

    blue_surface = GAME_FONT.render(blue_score_text, True, custom_player_colors["blue"])
    green_surface = GAME_FONT.render(green_score_text, True, custom_player_colors["green"])
    time_surface = GAME_FONT.render(time_text, True, BLACK)

    screen.blit(blue_surface, (sidebar_x_offset, 50))
    screen.blit(green_surface, (sidebar_x_offset, 90))
    screen.blit(time_surface, (sidebar_x_offset, 130))

    mode_text = f"Mode: {'Human vs AI' if game_mode == GameMode.HUMAN_VS_AI else 'AI vs AI'}"
    diff_text = f"Difficulty: {difficulty.capitalize()}"

    mode_surface = GAME_FONT.render(mode_text, True, BLACK)
    diff_surface = GAME_FONT.render(diff_text, True, BLACK)

    screen.blit(mode_surface, (sidebar_x_offset, 180)) # Adjusted Y
    screen.blit(diff_surface, (sidebar_x_offset, 210)) # Adjusted Y

    legend_y_start = 250 # Adjusted Y
    legend_title = GAME_FONT.render("Power-ups:", True, BLACK)
    screen.blit(legend_title, (sidebar_x_offset, legend_y_start))

    pygame.draw.circle(screen, ICE_BLUE, (sidebar_x_offset + 10, legend_y_start + 30), 10)
    freeze_text = GAME_FONT.render("Freeze opponent", True, BLACK)
    screen.blit(freeze_text, (sidebar_x_offset + 30, legend_y_start + 25))

    pygame.draw.circle(screen, GOLD, (sidebar_x_offset + 10, legend_y_start + 60), 10)
    points_text = GAME_FONT.render(f"+{POINTS_BONUS} points", True, BLACK)
    screen.blit(points_text, (sidebar_x_offset + 30, legend_y_start + 55))

    current_time = pygame.time.get_ticks() / 1000
    frozen_text_y_offset = legend_y_start + 90 # Adjusted Y

    if frozen_until["blue"] > current_time:
        freeze_remain = math.ceil(frozen_until["blue"] - current_time) # Use ceil for display
        freeze_msg = f"Blue frozen: {freeze_remain}s"
        freeze_surf = GAME_FONT.render(freeze_msg, True, ICE_BLUE)
        screen.blit(freeze_surf, (sidebar_x_offset, frozen_text_y_offset))
        frozen_text_y_offset += 30

    if frozen_until["green"] > current_time:
        freeze_remain = math.ceil(frozen_until["green"] - current_time) # Use ceil for display
        freeze_msg = f"Green frozen: {freeze_remain}s"
        freeze_surf = GAME_FONT.render(freeze_msg, True, ICE_BLUE)
        screen.blit(freeze_surf, (sidebar_x_offset, frozen_text_y_offset))


def move_agent(agent, human_input=None):
    current_time = pygame.time.get_ticks() / 1000
    if frozen_until[agent] > current_time:
        return

    x, y = player_positions[agent]
    moved = False
    new_x, new_y = x, y

    if agent == "blue" and game_mode == GameMode.HUMAN_VS_AI and human_input is not None:
        if human_input == pygame.K_UP and y > 0:
            new_y -= 1
            moved = True
        elif human_input == pygame.K_DOWN and y < GRID_SIZE - 1:
            new_y += 1
            moved = True
        elif human_input == pygame.K_LEFT and x > 0:
            new_x -= 1
            moved = True
        elif human_input == pygame.K_RIGHT and x < GRID_SIZE - 1:
            new_x += 1
            moved = True
    else: # AI movement for 'green' or 'blue' in AI vs AI
        possible_moves = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]: # Prioritize cardinal directions
            temp_x, temp_y = x + dx, y + dy
            if 0 <= temp_x < GRID_SIZE and 0 <= temp_y < GRID_SIZE:
                possible_moves.append((temp_x, temp_y))
        # Add diagonal moves if needed, but usually cardinal is better for this grid game.

        if not possible_moves:
            return

        smartness = AI_HARD_SMARTNESS if difficulty == "hard" else AI_NORMAL_SMARTNESS
        
        # AI prioritizes power-ups > uncaptured/opponent cells > own cells
        best_move = None
        
        # 1. Check for power-ups
        for p_x_check, p_y_check in possible_moves:
            for pu_x, pu_y, _ in power_ups:
                if p_x_check == pu_x and p_y_check == pu_y:
                    best_move = (p_x_check, p_y_check)
                    break
            if best_move: break
        
        if best_move is None:
            # 2. Prefer uncaptured cells or opponent cells
            good_moves = []
            for p_x_check, p_y_check in possible_moves:
                if board[p_x_check][p_y_check] != agent: # Includes None or opponent's color
                    good_moves.append((p_x_check, p_y_check))
            
            if good_moves:
                if random.random() < smartness: # Smart choice among good moves
                    # Could add more logic here, e.g., move towards center, or cut off opponent
                    best_move = random.choice(good_moves)
                else: # Random choice among good moves
                    best_move = random.choice(good_moves)
            else: # Only own cells are available
                best_move = random.choice(possible_moves) if possible_moves else (x,y)
        
        new_x, new_y = best_move
        moved = True


    if moved and (new_x != x or new_y != y): # Ensure actual movement happened
        previous_cell_owner = board[new_x][new_y]

        if previous_cell_owner != agent: 
            scores[agent] += 1
            if previous_cell_owner is not None: # Cell was owned by opponent
                opponent = "green" if agent == "blue" else "blue"
                if scores[opponent] > 0 : # Prevent negative scores from territory loss
                    scores[opponent] -=1 
        
        board[new_x][new_y] = agent
        player_positions[agent] = (new_x, new_y)
        check_power_ups(agent, new_x, new_y)


def check_power_ups(agent, x, y):
    global power_ups 
    
    # Iterate over a copy of the list when removing items
    for power_up_data in list(power_ups):
        p_x, p_y, p_type = power_up_data
        if x == p_x and y == p_y:
            power_ups.remove(power_up_data) # Remove the collected power-up
            
            if p_type == PowerUpType.FREEZE:
                opponent = "green" if agent == "blue" else "blue"
                frozen_until[opponent] = pygame.time.get_ticks() / 1000 + FREEZE_DURATION
            elif p_type == PowerUpType.POINTS:
                scores[agent] += POINTS_BONUS
            
            # Spawn a new power-up (could be delayed if needed)
            pygame.time.set_timer(pygame.USEREVENT + 1, 2000) # Timer to spawn new power-up after 2s
            return # Assume only one power-up per cell


def game_over_screen():
    screen.fill(PINK_LIGHT)

    if scores["blue"] > scores["green"]:
        winner = "Blue"
        winner_color = custom_player_colors["blue"]
    elif scores["green"] > scores["blue"]:
        winner = "Green"
        winner_color = custom_player_colors["green"]
    else:
        winner = "Tie"
        winner_color = BLACK

    for i in range(50):
        x_bg = random.randint(0, WIDTH)
        y_bg = random.randint(0, HEIGHT)
        size = random.randint(5, 15)
        pygame.draw.circle(screen, PINK_MEDIUM, (x_bg, y_bg), size, 1)

    winner_text_str = f"{winner} Wins!" if winner != "Tie" else "It's a Tie!"
    winner_surface = TITLE_FONT.render(winner_text_str, True, winner_color)

    pulse = math.sin(pygame.time.get_ticks() * 0.003) * 10
    winner_rect = winner_surface.get_rect(center=(WIDTH//2, HEIGHT//2 - 50 + pulse))
    screen.blit(winner_surface, winner_rect)

    scores_text = f"Blue: {scores['blue']}  Green: {scores['green']}"
    scores_surface = MENU_FONT.render(scores_text, True, BLACK)
    scores_rect = scores_surface.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
    screen.blit(scores_surface, scores_rect)

    again_text = "Play Again (Enter)"
    again_surface = MENU_FONT.render(again_text, True, BLACK)
    again_button_rect = again_surface.get_rect(center=(WIDTH//2, HEIGHT//2 + 120))
    again_button_bg = again_button_rect.inflate(40, 20)
    pygame.draw.rect(screen, PINK_MEDIUM, again_button_bg, border_radius=10)
    pygame.draw.rect(screen, HOT_PINK, again_button_bg, 3, border_radius=10)
    screen.blit(again_surface, again_button_rect)

    menu_text = "Main Menu (Esc)"
    menu_surface = MENU_FONT.render(menu_text, True, BLACK)
    menu_button_rect = menu_surface.get_rect(center=(WIDTH//2, HEIGHT//2 + 180))
    menu_button_bg = menu_button_rect.inflate(40, 20)
    pygame.draw.rect(screen, PINK_MEDIUM, menu_button_bg, border_radius=10)
    pygame.draw.rect(screen, HOT_PINK, menu_button_bg, 3, border_radius=10)
    screen.blit(menu_surface, menu_button_rect)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event_go in pygame.event.get():
            if event_go.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event_go.type == pygame.KEYDOWN:
                if event_go.key == pygame.K_RETURN:
                    return GameState.PLAYING # Game reset will happen in game_loop
                elif event_go.key == pygame.K_ESCAPE:
                    return GameState.MENU # Game reset will happen in game_loop
            elif event_go.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event_go.pos
                if again_button_bg.collidepoint(mouse_pos):
                    return GameState.PLAYING
                elif menu_button_bg.collidepoint(mouse_pos):
                    return GameState.MENU
    return GameState.MENU 

def draw_menu():
    screen.fill(PINK_LIGHT)
    button_rects_menu = [] 

    for _ in range(50):
        x_bg = random.randint(0, WIDTH)
        y_bg = random.randint(0, HEIGHT)
        size = random.randint(5, 15)
        
        # Simple circles for "cute" animated background
        # Using a temporary surface for alpha effect if desired, but simpler is often better for menus
        pygame.draw.circle(screen, PINK_MEDIUM, (x_bg,y_bg),size, random.randint(0,1)) # 0 for filled, 1 for outline


    title_text_str = "Cute Territory Game"
    title_surface = TITLE_FONT.render(title_text_str, True, HOT_PINK)
    title_rect = title_surface.get_rect(center=(WIDTH//2, 100))

    shadow_surface = TITLE_FONT.render(title_text_str, True, PINK_DARK)
    shadow_rect = shadow_surface.get_rect(center=(WIDTH//2 + 4, 104))
    screen.blit(shadow_surface, shadow_rect)
    screen.blit(title_surface, title_rect)

    buttons_data = [
        ("Play", 200, GameState.MODE_SELECT),
        ("Customize", 270, GameState.CUSTOMIZATION),
        ("Quit", 340, None) 
    ]

    for text, y_pos, next_state in buttons_data:
        button_surface = MENU_FONT.render(text, True, BLACK)
        button_rect = button_surface.get_rect(center=(WIDTH//2, y_pos))
        button_bg = button_rect.inflate(80, 20)
        pygame.draw.rect(screen, PINK_MEDIUM, button_bg, border_radius=10)
        pygame.draw.rect(screen, HOT_PINK, button_bg, 3, border_radius=10)
        screen.blit(button_surface, button_rect)
        button_rects_menu.append((button_bg, next_state, text)) 

    pygame.display.flip()

    waiting = True
    while waiting:
        for event_menu in pygame.event.get():
            if event_menu.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event_menu.type == pygame.KEYDOWN:
                if event_menu.key == pygame.K_RETURN: 
                    return GameState.MODE_SELECT
                elif event_menu.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event_menu.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event_menu.pos
                for rect, next_st, text_btn in button_rects_menu:
                    if rect.collidepoint(mouse_pos):
                        if text_btn == "Quit":
                            pygame.quit()
                            sys.exit()
                        return next_st
    return GameState.MENU 

def draw_mode_select():
    screen.fill(PINK_LIGHT)
    mode_button_rects = []

    for _ in range(30):
        x_bg = random.randint(0, WIDTH)
        y_bg = random.randint(0, HEIGHT)
        size = random.randint(5, 15)
        pygame.draw.circle(screen, PINK_MEDIUM, (x_bg, y_bg), size, 1)

    title_text_str = "Select Game Mode"
    title_surface = TITLE_FONT.render(title_text_str, True, HOT_PINK)
    title_rect = title_surface.get_rect(center=(WIDTH//2, 100))
    screen.blit(title_surface, title_rect)

    modes_data = [
        ("Human vs AI", GameMode.HUMAN_VS_AI, 200),
        ("AI vs AI", GameMode.AI_VS_AI, 270)
    ]

    for text, mode_val, y_pos in modes_data:
        mode_surface = MENU_FONT.render(text, True, BLACK)
        mode_rect = mode_surface.get_rect(center=(WIDTH//2, y_pos))
        button_bg = mode_rect.inflate(150, 20)
        pygame.draw.rect(screen, PINK_MEDIUM, button_bg, border_radius=10)
        pygame.draw.rect(screen, HOT_PINK, button_bg, 3, border_radius=10)
        screen.blit(mode_surface, mode_rect)
        mode_button_rects.append((button_bg, mode_val))

    back_text_str = "Back"
    back_surface = MENU_FONT.render(back_text_str, True, BLACK)
    back_rect_btn = back_surface.get_rect(center=(WIDTH//2, 340))
    back_bg_btn = back_rect_btn.inflate(80, 20)
    pygame.draw.rect(screen, PINK_MEDIUM, back_bg_btn, border_radius=10)
    pygame.draw.rect(screen, HOT_PINK, back_bg_btn, 3, border_radius=10)
    screen.blit(back_surface, back_rect_btn)

    pygame.display.flip()

    waiting = True
    global game_mode # Make sure we modify the global game_mode
    while waiting:
        for event_ms in pygame.event.get():
            if event_ms.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event_ms.type == pygame.KEYDOWN:
                if event_ms.key == pygame.K_ESCAPE:
                    return GameState.MENU, game_mode 
            elif event_ms.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event_ms.pos
                for rect, mode_v in mode_button_rects:
                    if rect.collidepoint(mouse_pos):
                        return GameState.DIFFICULTY_SELECT, mode_v
                if back_bg_btn.collidepoint(mouse_pos):
                    return GameState.MENU, game_mode 
    return GameState.MENU, game_mode

def draw_difficulty_select():
    screen.fill(PINK_LIGHT)
    diff_button_rects = []

    for _ in range(30):
        x_bg = random.randint(0, WIDTH)
        y_bg = random.randint(0, HEIGHT)
        size = random.randint(5, 15)
        pygame.draw.circle(screen, PINK_MEDIUM, (x_bg, y_bg), size, 1)

    title_text_str = "Select Difficulty"
    title_surface = TITLE_FONT.render(title_text_str, True, HOT_PINK)
    title_rect = title_surface.get_rect(center=(WIDTH//2, 100))
    screen.blit(title_surface, title_rect)

    difficulties_data = [
        ("Normal", "normal", 200),
        ("Hard", "hard", 270)
    ]

    for text, diff_val, y_pos in difficulties_data:
        diff_surface = MENU_FONT.render(text, True, BLACK)
        diff_rect = diff_surface.get_rect(center=(WIDTH//2, y_pos))
        button_bg = diff_rect.inflate(100, 20)
        pygame.draw.rect(screen, PINK_MEDIUM, button_bg, border_radius=10)
        pygame.draw.rect(screen, HOT_PINK, button_bg, 3, border_radius=10)
        screen.blit(diff_surface, diff_rect)
        diff_button_rects.append((button_bg, diff_val))

    back_text_str = "Back"
    back_surface = MENU_FONT.render(back_text_str, True, BLACK)
    back_rect_btn = back_surface.get_rect(center=(WIDTH//2, 340))
    back_bg_btn = back_rect_btn.inflate(80, 20)
    pygame.draw.rect(screen, PINK_MEDIUM, back_bg_btn, border_radius=10)
    pygame.draw.rect(screen, HOT_PINK, back_bg_btn, 3, border_radius=10)
    screen.blit(back_surface, back_rect_btn)

    pygame.display.flip()
    
    waiting = True
    global difficulty # Make sure we modify the global difficulty
    while waiting:
        for event_ds in pygame.event.get():
            if event_ds.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event_ds.type == pygame.KEYDOWN:
                if event_ds.key == pygame.K_ESCAPE:
                    return GameState.MODE_SELECT, difficulty 
            elif event_ds.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event_ds.pos
                for rect, diff_v in diff_button_rects:
                    if rect.collidepoint(mouse_pos):
                        # No need to call reset_game() here, it's called when PLAYING state starts
                        return GameState.PLAYING, diff_v
                if back_bg_btn.collidepoint(mouse_pos):
                    return GameState.MODE_SELECT, difficulty
    return GameState.MODE_SELECT, difficulty


def draw_customization():
    screen.fill(PINK_LIGHT)
    global custom_player_colors 
    
    # Work with copies for live preview until saved
    temp_blue_color = custom_player_colors["blue"]
    temp_green_color = custom_player_colors["green"]
    
    running_customization = True
    while running_customization: # Loop to allow screen updates within the function
        screen.fill(PINK_LIGHT) # Redraw background each frame

        for _ in range(30):
            x_bg = random.randint(0, WIDTH)
            y_bg = random.randint(0, HEIGHT)
            if random.random() < 0.7:
                size = random.randint(5, 10)
                pygame.draw.circle(screen, PINK_MEDIUM, (x_bg - size//2, y_bg - size//2), size//2 +1)
                pygame.draw.circle(screen, PINK_MEDIUM, (x_bg + size//2, y_bg - size//2), size//2 +1)
                pygame.draw.polygon(screen, PINK_MEDIUM, [(x_bg-size, y_bg - size//3),(x_bg+size,y_bg - size//3),(x_bg,y_bg+size*1.2)])
            else:
                size = random.randint(8, 15)
                star_points = []
                for j_star in range(5):
                    angle = j_star * 2 * math.pi / 5 - math.pi / 2
                    star_points.append((x_bg + math.cos(angle) * size, y_bg + math.sin(angle) * size))
                    angle += math.pi / 5
                    inner_size = size * 0.4
                    star_points.append((x_bg + math.cos(angle) * inner_size, y_bg + math.sin(angle) * inner_size))
                pygame.draw.polygon(screen, PASTEL_YELLOW, star_points)

        title_text_str = "Customize Your Game"
        title_surface = TITLE_FONT.render(title_text_str, True, HOT_PINK)
        title_rect = title_surface.get_rect(center=(WIDTH//2, 70))
        screen.blit(title_surface, title_rect)

        section_text_str = "Player Colors"
        section_surface = MENU_FONT.render(section_text_str, True, PINK_DARK)
        section_rect = section_surface.get_rect(center=(WIDTH//2, 140))
        screen.blit(section_surface, section_rect)

        blue_text_surf = GAME_FONT.render("Blue Player", True, BLACK)
        blue_text_rect = blue_text_surf.get_rect(topleft=(WIDTH//4 - 80, 180)) # Adjusted position
        screen.blit(blue_text_surf, blue_text_rect)

        blue_color_option_rects = []
        for i, color_opt in enumerate(available_colors):
            color_rect_shape = pygame.Rect(WIDTH//4 - 70 + i * 45, 210, 30, 30) # Spaced out
            pygame.draw.rect(screen, color_opt, color_rect_shape, border_radius=5)
            if color_opt == temp_blue_color:
                pygame.draw.rect(screen, HOT_PINK, color_rect_shape, 3, border_radius=5)
            blue_color_option_rects.append((color_rect_shape, color_opt))

        green_text_surf = GAME_FONT.render("Green Player", True, BLACK)
        green_text_rect = green_text_surf.get_rect(topleft=(WIDTH*3//4 - 100, 180)) # Adjusted position
        screen.blit(green_text_surf, green_text_rect)

        green_color_option_rects = []
        for i, color_opt in enumerate(available_colors):
            color_rect_shape = pygame.Rect(WIDTH*3//4 - 90 + i * 45, 210, 30, 30) # Spaced out
            pygame.draw.rect(screen, color_opt, color_rect_shape, border_radius=5)
            if color_opt == temp_green_color:
                pygame.draw.rect(screen, HOT_PINK, color_rect_shape, 3, border_radius=5)
            green_color_option_rects.append((color_rect_shape, color_opt))

        preview_text_surf = MENU_FONT.render("Preview", True, PINK_DARK)
        preview_rect = preview_text_surf.get_rect(center=(WIDTH//2, 290))
        screen.blit(preview_text_surf, preview_rect)

        blue_preview_center_pos = (WIDTH//3, 350)
        green_preview_center_pos = (WIDTH*2//3, 350)
        pygame.draw.circle(screen, temp_blue_color, blue_preview_center_pos, 30)
        pygame.draw.circle(screen, temp_green_color, green_preview_center_pos, 30)

        blue_prev_text_surf = GAME_FONT.render("Blue Player", True, BLACK)
        green_prev_text_surf = GAME_FONT.render("Green Player", True, BLACK)
        screen.blit(blue_prev_text_surf, blue_prev_text_surf.get_rect(center=(WIDTH//3, 400)))
        screen.blit(green_prev_text_surf, green_prev_text_surf.get_rect(center=(WIDTH*2//3, 400)))

        back_text_str = "Save & Back"
        back_surface = MENU_FONT.render(back_text_str, True, BLACK)
        back_rect_btn = back_surface.get_rect(center=(WIDTH//2, HEIGHT - 60)) 
        back_bg_btn = back_rect_btn.inflate(40, 20)
        pygame.draw.rect(screen, PINK_MEDIUM, back_bg_btn, border_radius=10)
        pygame.draw.rect(screen, HOT_PINK, back_bg_btn, 3, border_radius=10)
        screen.blit(back_surface, back_rect_btn)

        pygame.display.flip() # Update the full display

        for event_cust in pygame.event.get():
            if event_cust.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event_cust.type == pygame.KEYDOWN:
                if event_cust.key == pygame.K_ESCAPE:
                    custom_player_colors["blue"] = temp_blue_color # Save changes
                    custom_player_colors["green"] = temp_green_color
                    running_customization = False # Exit loop
                    return GameState.MENU
            elif event_cust.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event_cust.pos
                for rect_b, color_b in blue_color_option_rects:
                    if rect_b.collidepoint(mouse_pos):
                        temp_blue_color = color_b
                        # No need to return, loop will redraw with new temp color
                        break 
                
                for rect_g, color_g in green_color_option_rects:
                    if rect_g.collidepoint(mouse_pos):
                        temp_green_color = color_g
                        break
                
                if back_bg_btn.collidepoint(mouse_pos):
                    custom_player_colors["blue"] = temp_blue_color # Save changes
                    custom_player_colors["green"] = temp_green_color
                    running_customization = False # Exit loop
                    return GameState.MENU
    
    # Fallback return if loop exits unexpectedly (shouldn't happen)
    custom_player_colors["blue"] = temp_blue_color 
    custom_player_colors["green"] = temp_green_color
    return GameState.MENU


def reset_game():
    global board, scores, player_positions, power_ups, frozen_until

    board = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    scores = {"blue": 0, "green": 0}
    player_positions = {"blue": (1, 1), "green": (GRID_SIZE-2, GRID_SIZE-2)}
    power_ups = []
    frozen_until = {"blue": 0, "green": 0}

    board[player_positions["blue"][0]][player_positions["blue"][1]] = "blue"
    board[player_positions["green"][0]][player_positions["green"][1]] = "green"
    scores["blue"] = 1
    scores["green"] = 1

    for _ in range(random.randint(2,3)): 
        spawn_power_up()
    
    # Clear any pending power-up spawn timers
    pygame.time.set_timer(pygame.USEREVENT + 1, 0)


def game_loop():
    global game_state, game_mode, difficulty

    if has_music:
        try:
            if not pygame.mixer.music.get_busy():
                 pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Error playing music: {e}")

    ai_player_turn_timer = 0 
    start_time_playing_state = 0 
    power_up_spawn_timer = pygame.time.get_ticks() # For periodic power-up spawn

    running = True
    while running:
        current_game_speed_divisor = HARD_SPEED if difficulty == "hard" else NORMAL_SPEED
        # Frame delay for AI: higher value means slower AI, lower means faster
        ai_move_delay_frames = int(60 / current_game_speed_divisor)


        if game_state == GameState.MENU:
            game_state = draw_menu()
            if has_music and not pygame.mixer.music.get_busy():
                try: pygame.mixer.music.play(-1)
                except: pass


        elif game_state == GameState.MODE_SELECT:
            new_gs, new_gm = draw_mode_select()
            game_state = new_gs
            game_mode = new_gm # Update global game_mode

        elif game_state == GameState.DIFFICULTY_SELECT:
            new_gs, new_diff = draw_difficulty_select()
            game_state = new_gs
            difficulty = new_diff # Update global difficulty
            # If new_gs is PLAYING, reset_game and start_time_playing_state will be handled below

        elif game_state == GameState.CUSTOMIZATION:
            game_state = draw_customization()

        elif game_state == GameState.PLAYING:
            if start_time_playing_state == 0: # First frame entering PLAYING state
                 reset_game()
                 start_time_playing_state = pygame.time.get_ticks()
                 ai_player_turn_timer = 0 # Reset AI timer
                 power_up_spawn_timer = pygame.time.get_ticks() # Reset power-up spawn timer


            elapsed_time_seconds = (pygame.time.get_ticks() - start_time_playing_state) // 1000
            if elapsed_time_seconds >= TIME_LIMIT:
                game_state = GameState.GAME_OVER
                start_time_playing_state = 0 
                continue 

            # --- Event Handling for PLAYING state ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False # Exit main loop
                if event.type == pygame.KEYDOWN:
                    if game_mode == GameMode.HUMAN_VS_AI:
                        if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                            move_agent("blue", human_input=event.key) # Human moves immediately
                    if event.key == pygame.K_ESCAPE: 
                        game_state = GameState.MENU 
                        start_time_playing_state = 0 
                        if has_music: pygame.mixer.music.pause() # Pause music for menu
                        # No 'continue' here, let the loop transition normally to MENU state drawing
                
                if event.type == pygame.USEREVENT + 1: # Timer for spawning power-up
                    spawn_power_up()
                    pygame.time.set_timer(pygame.USEREVENT + 1, 0) # Clear the timer


            # --- AI Movement (if applicable) controlled by timer ---
            ai_player_turn_timer += 1
            if ai_player_turn_timer >= ai_move_delay_frames:
                ai_player_turn_timer = 0
                if game_mode == GameMode.HUMAN_VS_AI:
                    move_agent("green") # AI (Green) moves
                elif game_mode == GameMode.AI_VS_AI:
                    move_agent("blue")  # AI (Blue) moves
                    move_agent("green") # AI (Green) moves
            
            # --- Periodic Power-up Spawning (alternative to event-based) ---
            current_ticks = pygame.time.get_ticks()
            if current_ticks - power_up_spawn_timer > 5000: # Spawn every 5 seconds
                spawn_power_up()
                power_up_spawn_timer = current_ticks


            # --- Drawing ---
            screen.fill(PINK_LIGHT) # Clear screen or fill with background color
            draw_board() # Draws the grid, players, power-ups onto the screen
            draw_scores_and_timer(elapsed_time_seconds) # Draws the sidebar info
            
            pygame.display.flip()
            clock.tick(60)

        elif game_state == GameState.GAME_OVER:
            game_state = game_over_screen()
            start_time_playing_state = 0 
            # Music can continue or stop/change here. If going to menu, menu will handle it.
            if game_state == GameState.MENU and has_music:
                pygame.mixer.music.unpause() if pygame.mixer.music.get_busy() else pygame.mixer.music.play(-1)


        else: 
            print(f"Unknown game state: {game_state}")
            game_state = GameState.MENU # Default to menu if in unknown state

    pygame.quit()
    sys.exit()
    
if __name__ == '__main__':
    game_loop()