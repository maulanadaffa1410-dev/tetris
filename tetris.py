import pygame
import random
import sys

# Window
WIDTH, HEIGHT = 1000, 700
FPS = 60

# Playfield
COLS, ROWS = 10, 20
CELL = 30
PLAY_WIDTH = COLS * CELL
PLAY_HEIGHT = ROWS * CELL
PLAY_X = 50
PLAY_Y = (HEIGHT - PLAY_HEIGHT) // 2

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
COLORS = [
    (0, 240, 240),  # I
    (0, 0, 240),    # J
    (240, 160, 0),  # L
    (240, 240, 0),  # O
    (0, 240, 0),    # S
    (240, 0, 0),    # Z
    (160, 0, 240),  # T
]

# Shapes (7 classic shapes)
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 0], [1, 1, 1]],
]


class Piece:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.x = COLS // 2 - len(shape[0]) // 2
        self.y = 0

    def rotate(self):
        # rotate clockwise
        self.shape = [list(row) for row in zip(*self.shape[::-1])]


def create_grid(locked_positions=None):
    grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
    if locked_positions:
        for (x, y), color in locked_positions.items():
            if 0 <= y < ROWS and 0 <= x < COLS:
                grid[y][x] = color
    return grid


def valid_space(piece, grid):
    for i, row in enumerate(piece.shape):
        for j, val in enumerate(row):
            if val:
                x = piece.x + j
                y = piece.y + i
                if x < 0 or x >= COLS or y >= ROWS:
                    return False
                if y >= 0 and grid[y][x]:
                    return False
    return True


def check_lost(locked):
    for (x, y) in locked:
        if y < 0:
            return True
    return False


def get_shape():
    idx = random.randrange(len(SHAPES))
    shape = [row[:] for row in SHAPES[idx]]
    color = COLORS[idx]
    return Piece(shape, color)


def clear_rows(grid, locked):
    cleared = 0
    for i in range(ROWS - 1, -1, -1):
        if all(grid[i][j] is not None for j in range(COLS)):
            cleared += 1
            for j in range(COLS):
                try:
                    del locked[(j, i)]
                except KeyError:
                    pass
            for key in sorted(list(locked), key=lambda k: k[1])[::-1]:
                x, y = key
                if y < i:
                    val = locked.pop(key)
                    locked[(x, y + 1)] = val
    return cleared


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, True, color)
    surface.blit(label, (WIDTH // 2 - label.get_width() // 2, HEIGHT // 2 - label.get_height() // 2))


def draw_grid(surface, grid):
    for i in range(ROWS):
        for j in range(COLS):
            rect = pygame.Rect(PLAY_X + j * CELL, PLAY_Y + i * CELL, CELL, CELL)
            pygame.draw.rect(surface, GRAY, rect, 1)
            if grid[i][j]:
                pygame.draw.rect(surface, grid[i][j], rect.inflate(-2, -2))


def draw_window(surface, grid, score, next_piece):
    surface.fill(BLACK)
    # Title
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('TETRIS', True, WHITE)
    surface.blit(label, (PLAY_X + PLAY_WIDTH + 40, PLAY_Y))

    # Draw play area
    pygame.draw.rect(surface, WHITE, (PLAY_X - 5, PLAY_Y - 5, PLAY_WIDTH + 10, PLAY_HEIGHT + 10), 5)
    draw_grid(surface, grid)

    # Sidebar: score and next
    font = pygame.font.SysFont('comicsans', 30)
    score_label = font.render(f'Score: {score}', True, WHITE)
    surface.blit(score_label, (PLAY_X + PLAY_WIDTH + 40, PLAY_Y + 80))

    next_label = font.render('Next:', True, WHITE)
    surface.blit(next_label, (PLAY_X + PLAY_WIDTH + 40, PLAY_Y + 140))

    # draw next piece
    for i, row in enumerate(next_piece.shape):
        for j, val in enumerate(row):
            if val:
                rect = pygame.Rect(PLAY_X + PLAY_WIDTH + 60 + j * CELL, PLAY_Y + 180 + i * CELL, CELL, CELL)
                pygame.draw.rect(surface, next_piece.color, rect.inflate(-2, -2))

    # Controls
    small = pygame.font.SysFont('comicsans', 20)
    lines = [
        'Controls: A left, D right, S down, W/F rotate',
        'Space: hard drop',
    ]
    for k, l in enumerate(lines):
        lbl = small.render(l, True, WHITE)
        surface.blit(lbl, (PLAY_X + PLAY_WIDTH + 40, PLAY_Y + 300 + k * 24))


def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Tetris')
    clock = pygame.time.Clock()

    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    fall_time = 0
    fall_speed = 0.5
    level_time = 0
    score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime() / 1000.0
        level_time += clock.get_rawtime() / 1000.0
        clock.tick(FPS)

        if level_time > 30:
            level_time = 0
            if fall_speed > 0.05:
                fall_speed -= 0.02

        if fall_time >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_d:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_s:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_w or event.key == pygame.K_f:
                    current_piece.rotate()
                    if not valid_space(current_piece, grid):
                        # try wall kicks (basic)
                        current_piece.x += 1
                        if not valid_space(current_piece, grid):
                            current_piece.x -= 2
                            if not valid_space(current_piece, grid):
                                current_piece.x += 1
                                # revert rotate
                                for _ in range(3):
                                    current_piece.rotate()
                elif event.key == pygame.K_SPACE:
                    # hard drop
                    drop = 0
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                        drop += 1
                    current_piece.y -= 1
                    score += drop * 2
                    change_piece = True

        shape_pos = []
        for i, row in enumerate(current_piece.shape):
            for j, val in enumerate(row):
                if val:
                    x = current_piece.x + j
                    y = current_piece.y + i
                    if y >= 0:
                        shape_pos.append((x, y))

        for x, y in shape_pos:
            if 0 <= y < ROWS and 0 <= x < COLS:
                grid[y][x] = current_piece.color

        if change_piece:
            for x, y in shape_pos:
                if y < 0:
                    # game over
                    run = False
                    break
                locked_positions[(x, y)] = current_piece.color
            cleared = clear_rows(grid, locked_positions)
            if cleared:
                # scoring: 100, 300, 500, 800
                if cleared == 1:
                    score += 100
                elif cleared == 2:
                    score += 300
                elif cleared == 3:
                    score += 500
                else:
                    score += 800

            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

            if check_lost(locked_positions):
                run = False

        draw_window(win, grid, score, next_piece)

        # Winning condition removed — game continues until game over

        pygame.display.update()

    # Game over screen
    win.fill(BLACK)
    draw_text_middle(win, 'GAME OVER', 60, (255, 0, 0))
    sub = pygame.font.SysFont('comicsans', 30).render(f'Final Score: {score}', True, WHITE)
    win.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.update()
    pygame.time.delay(3000)
    pygame.quit()


def main_menu():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Tetris - Menu')
    run = True
    while run:
        win.fill(BLACK)
        draw_text_middle(win, 'Press ENTER to Start', 50, WHITE)
        small = pygame.font.SysFont('comicsans', 22)
        lines = [
            'Controls:',
            'A: Left  D: Right  S: Soft drop',
            'W or F: Rotate  Space: Hard drop',
            'Reach 1000 to win. Fill up to lose.'
        ]
        for i, l in enumerate(lines):
            lbl = small.render(l, True, WHITE)
            win.blit(lbl, (WIDTH // 2 - lbl.get_width() // 2, HEIGHT // 2 + 50 + i * 26))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    run = False
                    main()


if __name__ == '__main__':
    main_menu()
