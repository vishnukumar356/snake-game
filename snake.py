# ─────────────────────────────────────────────────────────────────
#  Snake Game — snake.py  (Python version using pygame)
#
#  Run:  python snake.py
#  Requires: pip install pygame-ce   (supports Python 3.8 – 3.14+)
#
#  Concepts covered (see comments throughout):
#    1.  pygame setup & the main window
#    2.  The game loop  (while True + clock.tick)
#    3.  Snake as a list of (x, y) tuples
#    4.  Movement & direction logic
#    5.  Collision detection
#    6.  Food spawning with random
#    7.  Score & high-score tracking
#    8.  Game states  (START / RUNNING / PAUSED / GAME_OVER)
#    9.  Drawing / rendering with pygame.draw
#   10.  Keyboard input with pygame.event
# ─────────────────────────────────────────────────────────────────

import pygame   # the game library
import random   # for placing food at a random position
import sys      # for sys.exit()


# ── 1. CONSTANTS ─────────────────────────────────────────────────
# Using UPPERCASE names for values that never change is a Python convention.

CELL_SIZE   = 30          # pixels per grid cell  (increase to make the board bigger)
COLS        = 30          # number of columns
ROWS        = 30          # number of rows
WIDTH       = COLS * CELL_SIZE    # 900 px
HEIGHT      = ROWS * CELL_SIZE    # 900 px
SPEED_FPS   = 8           # frames (ticks) per second  ← controls game speed
INFO_HEIGHT = 60          # extra pixels above the board for score display

# Colours  (R, G, B)
BLACK       = (  0,   0,   0)
DARK_BG     = ( 22,  33,  62)    # board background  #16213e
PANEL_BG    = ( 26,  26,  46)    # score panel       #1a1a2e
TEAL        = ( 78, 204, 163)    # snake head / UI   #4ecca3
TEAL_DARK   = ( 46, 175, 135)    # snake body        #2eaf87
RED         = (233,  69,  96)    # food              #e94560
WHITE       = (234, 234, 234)
GREY        = (136, 136, 136)
OVERLAY     = (  0,   0,   0, 140)   # semi-transparent (used with Surface)


# ── GAME STATES ───────────────────────────────────────────────────
# We use simple string constants as "state names" instead of numbers
# so the code reads like English.
STATE_START     = 'START'
STATE_RUNNING   = 'RUNNING'
STATE_PAUSED    = 'PAUSED'
STATE_GAME_OVER = 'GAME_OVER'


# ── 1. PYGAME SETUP ───────────────────────────────────────────────
# pygame.init() starts all pygame sub-systems (display, sound, fonts …).
# We create one window that is wider than the board to leave room for the
# score panel at the top.

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT + INFO_HEIGHT))
pygame.display.set_caption('🐍 Snake Game')

clock = pygame.time.Clock()   # used in the game loop to cap FPS

# Fonts — pygame.font.SysFont picks a system font by name.
font_large  = pygame.font.SysFont('Segoe UI', 36, bold=True)
font_medium = pygame.font.SysFont('Segoe UI', 22)
font_small  = pygame.font.SysFont('Segoe UI', 16)


# ── 3. SNAKE DATA STRUCTURE ───────────────────────────────────────
# The snake is a Python LIST of (col, row) tuples.
# Index 0 is always the HEAD.
#
#   [ (10, 10), (9, 10), (8, 10) ]
#     ^--- HEAD
#
# Each tuple holds a GRID position (not pixels).
# We multiply by CELL_SIZE when drawing.
#
# Movement works like this every tick:
#   • Calculate the new head position from the current direction
#   • insert(0, new_head)   — prepend new head   (like JS unshift)
#   • pop()                 — remove tail        (like JS pop)
#   • If food was eaten → skip pop()  → snake grows by 1


def init_game():
    """
    Reset all game variables to their starting values.
    Returns a dictionary holding the full game state.
    """
    mid_col = COLS // 2
    mid_row = ROWS // 2

    # Snake starts as 3 cells long in the middle, moving right
    snake = [
        (mid_col,     mid_row),   # head
        (mid_col - 1, mid_row),   # body
        (mid_col - 2, mid_row),   # tail
    ]

    state = {
        'snake':      snake,
        'direction':  'RIGHT',    # current direction
        'next_dir':   'RIGHT',    # buffered direction (see keyboard section)
        'food':       None,
        'score':      0,
        'high_score': 0,          # persists across restarts within one session
        'state':      STATE_START,
    }

    state['food'] = spawn_food(state['snake'])
    return state


# ── 6. FOOD SPAWNING ─────────────────────────────────────────────
# random.randrange(n) returns an integer in [0, n-1].
# We keep re-rolling until the chosen cell is NOT inside the snake.

def spawn_food(snake):
    """Pick a random free grid cell that the snake does not occupy."""
    while True:
        candidate = (
            random.randrange(COLS),
            random.randrange(ROWS),
        )
        if candidate not in snake:   # Python 'in' checks list membership
            return candidate


# ── 4. MOVEMENT ───────────────────────────────────────────────────
# Direction is one of 'UP' | 'DOWN' | 'LEFT' | 'RIGHT'.
# Each direction changes col or row by ±1.

DIRECTION_DELTA = {
    'UP':    ( 0, -1),   # row decreases going up
    'DOWN':  ( 0,  1),
    'LEFT':  (-1,  0),
    'RIGHT': ( 1,  0),
}

# Opposite directions — used to prevent 180° reversal
OPPOSITE = {
    'UP': 'DOWN', 'DOWN': 'UP',
    'LEFT': 'RIGHT', 'RIGHT': 'LEFT',
}


def move_snake(gs):
    """
    Advance the snake by one cell.
    gs  — the game-state dictionary returned by init_game().
    Returns True if the move was valid, False if the snake died.
    """
    # Apply the buffered direction (only if it's not a direct reversal)
    gs['direction'] = gs['next_dir']

    dc, dr = DIRECTION_DELTA[gs['direction']]
    head_col, head_row = gs['snake'][0]
    new_head = (head_col + dc, head_row + dr)

    # ── 5. COLLISION DETECTION ────────────────────────────────────

    # Wall collision
    if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
        return False   # snake hit a wall → game over

    # Self collision  — 'in' checks every element of the list
    if new_head in gs['snake']:
        return False   # snake hit itself → game over

    # Move forward: prepend new head
    gs['snake'].insert(0, new_head)

    # Food collision
    if new_head == gs['food']:
        gs['score'] += 10
        # Update high score
        if gs['score'] > gs['high_score']:
            gs['high_score'] = gs['score']
        # Spawn new food WITHOUT removing the tail → snake grows
        gs['food'] = spawn_food(gs['snake'])
    else:
        gs['snake'].pop()   # normal move: remove the tail

    return True   # move was valid


# ── 9. DRAWING / RENDERING ────────────────────────────────────────
# pygame draws with pygame.draw.rect() and pygame.draw.circle().
# Every frame we:
#   1. Fill the background
#   2. Draw the score panel
#   3. Draw the food
#   4. Draw each snake segment
#   5. Draw overlays (PAUSED / GAME OVER / START screen)
#   6. pygame.display.flip() — push the buffer to the screen


def draw_rounded_rect(surface, color, rect, radius=6):
    """Helper: draw a rectangle with rounded corners."""
    pygame.draw.rect(surface, color, rect, border_radius=radius)


def draw(screen, gs):
    """Render the current game state to the screen."""

    board_top = INFO_HEIGHT   # Y-offset where the board begins

    # ── Score panel (top bar) ─────────────────────────────────────
    screen.fill(PANEL_BG)
    score_surf  = font_medium.render(f'Score:  {gs["score"]}',      True, WHITE)
    high_surf   = font_medium.render(f'High:  {gs["high_score"]}',  True, TEAL)
    hint_surf   = font_small.render('P = pause   R = restart   Q = quit', True, GREY)
    screen.blit(score_surf, (16, 8))
    screen.blit(high_surf,  (200, 8))
    screen.blit(hint_surf,  (16, 38))

    # ── Board background ──────────────────────────────────────────
    board_rect = pygame.Rect(0, board_top, WIDTH, HEIGHT)
    pygame.draw.rect(screen, DARK_BG, board_rect)

    # ── Food ──────────────────────────────────────────────────────
    fx, fy = gs['food']
    food_center = (
        fx * CELL_SIZE + CELL_SIZE // 2,
        board_top + fy * CELL_SIZE + CELL_SIZE // 2,
    )
    pygame.draw.circle(screen, RED, food_center, CELL_SIZE // 2 - 2)

    # ── Snake ─────────────────────────────────────────────────────
    for i, (col, row) in enumerate(gs['snake']):
        color = TEAL if i == 0 else TEAL_DARK   # head is brighter
        rect  = pygame.Rect(
            col * CELL_SIZE + 1,
            board_top + row * CELL_SIZE + 1,
            CELL_SIZE - 2,
            CELL_SIZE - 2,
        )
        draw_rounded_rect(screen, color, rect, radius=4)

    # ── Overlays ──────────────────────────────────────────────────
    state = gs['state']

    if state == STATE_START:
        _draw_overlay(screen, board_top,
                      title='🐍 Snake Game', title_color=TEAL,
                      subtitle='Press ENTER to start')

    elif state == STATE_PAUSED:
        _draw_overlay(screen, board_top,
                      title='PAUSED', title_color=TEAL,
                      subtitle='Press P to resume')

    elif state == STATE_GAME_OVER:
        _draw_overlay(screen, board_top,
                      title='GAME OVER', title_color=RED,
                      subtitle=f'Score: {gs["score"]}   |   Press R to restart')

    # ── Flip display buffer ───────────────────────────────────────
    # Nothing appears on screen until we call flip().
    pygame.display.flip()


def _draw_overlay(screen, board_top, title, title_color, subtitle):
    """Draw a semi-transparent overlay with a centred title and subtitle."""
    # Create a transparent surface the size of the board
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))   # RGBA — 150/255 opacity
    screen.blit(overlay, (0, board_top))

    cx = WIDTH // 2
    cy = board_top + HEIGHT // 2

    title_surf = font_large.render(title, True, title_color)
    sub_surf   = font_medium.render(subtitle, True, WHITE)

    screen.blit(title_surf, title_surf.get_rect(center=(cx, cy - 24)))
    screen.blit(sub_surf,   sub_surf.get_rect(center=(cx, cy + 20)))


# ── 10. KEYBOARD INPUT ────────────────────────────────────────────
# pygame.event.get() returns all events that happened since the last call.
# We look for KEYDOWN events and update `next_dir` in the game state.
# Using `next_dir` instead of `direction` prevents reversals within one tick.

def handle_input(gs):
    """
    Process all pending pygame events.
    Returns False if the user closed the window, True otherwise.
    """
    for event in pygame.event.get():

        # Window close button
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:

            key = event.key

            # ── Direction keys ────────────────────────────────────
            if gs['state'] == STATE_RUNNING:
                if key == pygame.K_UP    and gs['direction'] != 'DOWN':
                    gs['next_dir'] = 'UP'
                elif key == pygame.K_DOWN  and gs['direction'] != 'UP':
                    gs['next_dir'] = 'DOWN'
                elif key == pygame.K_LEFT  and gs['direction'] != 'RIGHT':
                    gs['next_dir'] = 'LEFT'
                elif key == pygame.K_RIGHT and gs['direction'] != 'LEFT':
                    gs['next_dir'] = 'RIGHT'
                # WASD alternative
                elif key == pygame.K_w and gs['direction'] != 'DOWN':
                    gs['next_dir'] = 'UP'
                elif key == pygame.K_s and gs['direction'] != 'UP':
                    gs['next_dir'] = 'DOWN'
                elif key == pygame.K_a and gs['direction'] != 'RIGHT':
                    gs['next_dir'] = 'LEFT'
                elif key == pygame.K_d and gs['direction'] != 'LEFT':
                    gs['next_dir'] = 'RIGHT'

            # ── State transitions ─────────────────────────────────
            if key == pygame.K_RETURN or key == pygame.K_SPACE:
                if gs['state'] == STATE_START:
                    gs['state'] = STATE_RUNNING

            if key == pygame.K_p:
                if gs['state'] == STATE_RUNNING:
                    gs['state'] = STATE_PAUSED
                elif gs['state'] == STATE_PAUSED:
                    gs['state'] = STATE_RUNNING

            if key == pygame.K_r:
                # Restart but keep high score
                old_high = gs['high_score']
                gs.update(init_game())
                gs['high_score'] = old_high
                gs['state'] = STATE_RUNNING

            if key == pygame.K_q or key == pygame.K_ESCAPE:
                return False

    return True


# ── 2. GAME LOOP ─────────────────────────────────────────────────
# This is the heart of any game. It runs forever until the player quits.
#
#   while True:
#       1. Handle input     (what did the player press?)
#       2. Update state     (move the snake, check collisions)
#       3. Draw             (render the new state)
#       4. Wait             (clock.tick caps the loop to SPEED_FPS per second)
#
# clock.tick(SPEED_FPS) makes the loop sleep just long enough so that
# the game runs at exactly SPEED_FPS ticks per second — no faster.

def main():
    gs = init_game()   # gs = "game state" dictionary

    while True:
        # ── Step 1: Input ────────────────────────────────────────
        if not handle_input(gs):
            break   # player quit

        # ── Step 2: Update state ─────────────────────────────────
        if gs['state'] == STATE_RUNNING:
            alive = move_snake(gs)
            if not alive:
                gs['state'] = STATE_GAME_OVER

        # ── Step 3: Draw ─────────────────────────────────────────
        draw(screen, gs)

        # ── Step 4: Wait ─────────────────────────────────────────
        # clock.tick returns the ms elapsed; we don't need it here.
        clock.tick(SPEED_FPS)

    # Clean up pygame and exit
    pygame.quit()
    sys.exit()


# ── Entry point ───────────────────────────────────────────────────
# In Python, `if __name__ == '__main__':` means:
# "only run main() when this file is executed directly,
#  not when it is imported as a module by another file."
if __name__ == '__main__':
    main()

