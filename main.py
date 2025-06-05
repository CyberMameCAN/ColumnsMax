import pygame
import random

WIDTH, HEIGHT = 350, 750
GRID_W, GRID_H = 7, 15
TILE_SIZE = WIDTH // GRID_W
COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255)
]
BONUS_COLOR = (255, 255, 255)
COLORS.append(BONUS_COLOR)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Columns MAX Clone")
clock = pygame.time.Clock()

board = [[None for _ in range(GRID_H)] for _ in range(GRID_W)]

def draw_grid():
    for x in range(GRID_W):
        for y in range(GRID_H):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)
            color = board[x][y]
            if color:
                pygame.draw.rect(screen, color, rect.inflate(-4, -4))

def draw_current_block(cur_block, pos):
    for i, color in enumerate(cur_block):
        x, y = pos[0], pos[1] - i
        if 0 <= x < GRID_W and 0 <= y < GRID_H:
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, color, rect.inflate(-4, -4))

# def get_new_block():
#     return [random.choice(COLORS) for _ in range(3)]
def get_new_block():
    block = []
    for _ in range(3):
        if random.random() < 0.06:
            block.append(BONUS_COLOR)
        else:
            block.append(random.choice(COLORS[:-1]))  # BONUS_COLOR除く
    return block


def can_move(block_pos, board, dx, dy):
    x, y = block_pos
    for i in range(3):
        nx = x + dx
        ny = y - i + dy
        if not (0 <= nx < GRID_W and 0 <= ny < GRID_H):
            return False
        if ny >= 0 and board[nx][ny]:
            return False
    return True

def fix_block(board, block, block_pos):
    x, y = block_pos
    for i, color in enumerate(block):
        bx, by = x, y - i
        if 0 <= bx < GRID_W and 0 <= by < GRID_H:
            board[bx][by] = color

def is_block_landed(board, block, block_pos):
    x, y = block_pos
    for i in range(3):
        by = y - i + 1
        if by >= GRID_H or (by >= 0 and board[x][by]):
            return True
    return False

def is_match(c1, c2, c3):
    # Noneは消せない
    if c1 is None or c2 is None or c3 is None:
        return False
    colors = [c for c in [c1, c2, c3] if c != BONUS_COLOR]
    # 全部ボーナスセルならNG
    if len(colors) == 0:
        return False
    # 通常色が1色以上あって、その色+ボーナスセルで構成ならOK
    ref_color = colors[0]
    return all((c == ref_color or c == BONUS_COLOR) for c in [c1, c2, c3])

def find_matches(board):
    matches = set()
    for x in range(GRID_W):
        for y in range(GRID_H):
            color = board[x][y]
            if not color:
                continue
            for dx, dy in [(1, 0), (0, 1), (1, 1), (-1, 1)]:
                cells = []
                for step in range(3):
                    nx, ny = x + dx * step, y + dy * step
                    if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
                        cells.append(board[nx][ny])
                    else:
                        break
                if len(cells) == 3 and is_match(*cells):
                    for step in range(3):
                        nx, ny = x + dx * step, y + dy * step
                        matches.add((nx, ny))
    return matches

def remove_and_drop(board, matches):
    for x, y in matches:
        board[x][y] = None
    for x in range(GRID_W):
        new_col = [board[x][y] for y in range(GRID_H) if board[x][y]]
        for y in range(GRID_H):
            board[x][GRID_H - 1 - y] = new_col[-1 - y] if y < len(new_col) else None

def is_game_over(board, block_pos):
    x, y = block_pos
    for i in range(3):
        bx, by = x, y - i
        if 0 <= bx < GRID_W and 0 <= by < GRID_H:
            if board[bx][by]:
                return True
    return False

font = pygame.font.SysFont(None, 28)
def draw_info():
    info = f"Score: {score}   Level: {level}"
    txt = font.render(info, True, (255, 255, 255))
    screen.blit(txt, (10, HEIGHT - 35))

def reset_game():
    global board, cur_block, block_pos, score, level, fall_speed, chain_count, pending_chain, chain_wait, game_over, paused

    board = [[None for _ in range(GRID_H)] for _ in range(GRID_W)]
    cur_block = get_new_block()
    block_pos = [GRID_W // 2, 2]
    score = 0
    level = 1
    fall_speed = 0.5
    chain_count = 0
    pending_chain = False
    chain_wait = 0.0
    paused = False
    game_over = False

score = 0
level = 1

chain_count = 0
next_level_score = 200

cur_block = get_new_block()
block_pos = [GRID_W // 2, 2]

fall_time = 0.0
fall_speed = 0.5

chain_wait = 0.0
pending_chain = False

paused = False
game_over = False

running = True
while running:
    dt = clock.tick(60) / 1000.0
    fall_time += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if not game_over:
                    paused = not paused
            elif game_over:
                if event.key == pygame.K_SPACE:
                    reset_game()
            elif not paused:
                if not pending_chain:
                    if event.key == pygame.K_LEFT:
                        if can_move(block_pos, board, -1, 0):
                            block_pos[0] -= 1
                    if event.key == pygame.K_RIGHT:
                        if can_move(block_pos, board, 1, 0):
                                block_pos[0] += 1
                    if event.key == pygame.K_UP:
                        cur_block = [cur_block[-1]] + cur_block[:-1]
                    if event.key == pygame.K_DOWN:
                        if not is_block_landed(board, cur_block, block_pos):
                            block_pos[1] += 1
                            score += 1

    if not game_over and not paused:
        if not pending_chain:
            if fall_time > fall_speed:
                if not is_block_landed(board, cur_block, block_pos):
                    block_pos[1] += 1
                else:
                    fix_block(board, cur_block, block_pos)
                    pending_chain = True
                    chain_wait = 0
                fall_time = 0.0
        else:
            chain_wait += dt
            if chain_wait > 0.3:
                matches = find_matches(board)
                if matches:
                    chain_count += 1
                    chain_score = len(matches) * 10 * (1 + 0.5 * (chain_count - 1))
                    score += int(chain_score)
                    remove_and_drop(board, matches)
                    chain_wait = 0
                else:
                    chain_count = 0
                    if score >= level * next_level_score:
                        level += 1
                        fall_speed = max(0.1, 0.5 - (level - 1) * 0.05)
                    cur_block = get_new_block()
                    block_pos = [GRID_W // 2, 2]
                    # --- ここでゲームオーバーチェック ---
                    if is_game_over(board, block_pos):
                        game_over = True
                    pending_chain = False

    screen.fill((0, 0, 0))
    draw_grid()
    if not pending_chain:
        draw_current_block(cur_block, block_pos)
    draw_info()
    if paused and not game_over:
        txt = font.render("PAUSE", True, (80, 200, 255))
        screen.blit(txt, (WIDTH // 2 - 60, HEIGHT // 2 - 20))
    if game_over:
        txt = font.render("GAME OVER", True, (255, 80, 80))
        screen.blit(txt, (WIDTH // 2 - 80, HEIGHT // 2 - 20))
        txt2 = font.render("Restart by SPACE Key", True, (255, 255, 180))
        screen.blit(txt2, (WIDTH // 2 - 110, HEIGHT // 2 + 20))

    pygame.display.flip()

pygame.quit()
