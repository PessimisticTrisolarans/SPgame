import pygame
import random

# 初始化pygame
pygame.init()

# 屏幕大小
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
# 网格参数
GRID_SIZE = 20
GRID_WIDTH, GRID_HEIGHT = SCREEN_WIDTH // 2 // GRID_SIZE, SCREEN_HEIGHT // GRID_SIZE
# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
# 新增网格线颜色
GRID_LINE_COLOR = (128, 128, 128)  # 灰色


# 设置屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris_simplicity")

# 字体设置
font = pygame.font.Font(None, 36)


# 方块类
class Block:
    SHAPES = [
        [[1, 1, 1, 1]],  # I
        [[1, 1], [1, 1]],  # O
        [[0, 1, 0], [1, 1, 1]],  # T
        [[1, 1, 0], [0, 1, 1]],  # S
        [[0, 1, 1], [1, 1, 0]],  # Z
        [[1, 1, 1], [0, 0, 1]],  # L
        [[1, 1, 1], [1, 0, 0]]  # J
    ]
    COLORS = [RED, GREEN, BLUE, (255, 255, 0), (0, 255, 255), (255, 0, 255), (128, 0, 128)]

    def __init__(self, shape=None, color=None, x=0, y=0):
        if shape is None:
            self.shape = random.choice(self.SHAPES)
        else:
            self.shape = shape

        if color is None:
            self.color = random.choice(self.COLORS)
        else:
            self.color = color

        self.x = x
        self.y = y

    def rotate(self):
        self.shape = list(zip(*self.shape[::-1]))


def draw_grid(grid):
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            pygame.draw.rect(screen, cell, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
            # 绘制网格线，这里使用 GRID_LINE_COLOR
            pygame.draw.line(screen, GRID_LINE_COLOR, (x * GRID_SIZE, y * GRID_SIZE), ((x + 1) * GRID_SIZE, y * GRID_SIZE), 1)
            pygame.draw.line(screen, GRID_LINE_COLOR, (x * GRID_SIZE, y * GRID_SIZE), (x * GRID_SIZE, (y + 1) * GRID_SIZE), 1)


def draw_block(block):
    for y, row in enumerate(block.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, block.color, ((block.x + x) * GRID_SIZE, (block.y + y) * GRID_SIZE, GRID_SIZE, GRID_SIZE))


def check_collision(block, grid):
    for y, row in enumerate(block.shape):
        for x, cell in enumerate(row):
            if cell:
                if (block.x + x < 0 or block.x + x >= GRID_WIDTH or
                        block.y + y >= GRID_HEIGHT or
                        grid[block.y + y][block.x + x] != BLACK):
                    return True
    return False


def merge_block(block, grid):
    for y, row in enumerate(block.shape):
        for x, cell in enumerate(row):
            if cell:
                grid[block.y + y][block.x + x] = block.color


def clear_lines(grid):
    lines_cleared = 0
    for y in range(GRID_HEIGHT):
        if all(cell != BLACK for cell in grid[y]):
            del grid[y]
            grid.insert(0, [BLACK] * GRID_WIDTH)
            lines_cleared += 1
    return lines_cleared


def get_high_score_from_file(): 
    try:
        with open('scores_for_simplicity.txt', 'r') as file:
            scores = [int(line.strip()) for line in file.readlines()]
            return max(scores, default=0)
    except FileNotFoundError:
        return 0


def reset_game():
    """重置游戏状态"""
    grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    current_block = Block(x=GRID_WIDTH // 2 - len(Block().shape[0]) // 2, y=0)
    score = 0
    high_score = 0
    game_over = False
    history = []
    return grid, current_block, score, high_score, game_over, history


def main():
    clock = pygame.time.Clock()
    running = True
    high_score_all_time = get_high_score_from_file()  # 从文件中读取历史最高分
    grid, current_block, score, high_score, game_over, history = reset_game()
    paused = False  # 新增：用于跟踪游戏是否暂停

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # 按R键重新开始游戏
                    if game_over:  # 只有在游戏结束时才重新开始
                        grid, current_block, score, high_score, game_over, history = reset_game()
                elif event.key == pygame.K_q and game_over:  # 按Q键退出游戏
                    running = False
                    game_over = True
                elif event.key == pygame.K_p:  # 新增：按P键暂停/继续游戏
                    paused = not paused  # 切换暂停状态
                elif not game_over and not paused:  # 修改：仅在非暂停状态下处理移动和旋转
                    if event.key == pygame.K_LEFT and not check_collision(
                            Block(current_block.shape, current_block.color, current_block.x - 1, current_block.y),
                            grid):
                        current_block.x -= 1
                    elif event.key == pygame.K_RIGHT and not check_collision(
                            Block(current_block.shape, current_block.color, current_block.x + 1, current_block.y),
                            grid):
                        current_block.x += 1
                    elif event.key == pygame.K_DOWN and not check_collision(
                            Block(current_block.shape, current_block.color, current_block.x, current_block.y + 1),
                            grid):
                        current_block.y += 1
                    elif event.key == pygame.K_UP:
                        new_block = Block(current_block.shape, current_block.color, current_block.x, current_block.y)
                        new_block.rotate()
                        if not check_collision(new_block, grid):
                            current_block = new_block
                    elif event.key == pygame.K_SPACE:  # 按下空格键后方块直接下落到最底部
                        while not check_collision(Block(current_block.shape, current_block.color, current_block.x, current_block.y + 1), grid):
                            current_block.y += 1
                        current_block.y -= 1  # 回退一步，防止碰撞

        if not game_over and not paused:  # 修改：仅在非暂停状态下更新游戏状态
            # 更新游戏状态
            current_block.y += 1
            if check_collision(current_block, grid):
                current_block.y -= 1
                merge_block(current_block, grid)
                score += clear_lines(grid) * 10
                if score > high_score:
                    high_score = score
                current_block = Block(x=GRID_WIDTH // 2 - len(current_block.shape[0]) // 2, y=0)
                if check_collision(current_block, grid):
                    game_over = True
                    history.append(score)  # 记录当前游戏的得分

        # 绘制游戏界面
        screen.fill(BLACK)

        # 绘制游玩区
        draw_grid(grid)

        # 绘制当前方块
        draw_block(current_block)

        # 绘制其他UI元素
        text_score = font.render(f"Score: {score}", True, WHITE)
        text_high_score = font.render(f"High Score (Current Game): {high_score}", True, WHITE)
        text_high_score_all_time = font.render(f"High Score (All Time): {high_score_all_time}", True, WHITE)
        screen.blit(text_score, (SCREEN_WIDTH // 2 + 20, 20))
        screen.blit(text_high_score, (SCREEN_WIDTH // 2 + 20, 60))
        screen.blit(text_high_score_all_time, (SCREEN_WIDTH // 2 + 20, 100))

        # 添加按键提示文字
        text_instructions = font.render("Controls: Left, Right, Down, Up, Space", True, WHITE)
        screen.blit(text_instructions, (SCREEN_WIDTH // 2 + 20, 140))

        if paused:  # 新增：显示暂停信息
            text_paused = font.render("PAUSED", True, WHITE)
            screen.blit(text_paused, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 50))

        if game_over:
            text_game_over = font.render("Game Over", True, WHITE)
            text_restart = font.render("Press R to Restart | Press Q to Exit", True, WHITE)
            screen.blit(text_game_over, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
            screen.blit(text_restart, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))

            # 显示历史记录
            y_offset = 100
            for i, h in enumerate(history[-5:]):  # 显示最近5次的历史记录
                text_history = font.render(f"Game {i+1}: {h}", True, WHITE)
                screen.blit(text_history, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + y_offset))
                y_offset += 30

        pygame.display.flip()
        clock.tick(5)  # 减慢方块下落速度

        # 游戏结束后，等待玩家输入
        if game_over:
            waiting_for_input = True
            while waiting_for_input:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        waiting_for_input = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:  # 按R键重新开始游戏
                            waiting_for_input = False
                            game_over = False
                            grid, current_block, score, high_score, game_over, history = reset_game()
                        elif event.key == pygame.K_q:  # 按Q键退出游戏
                            running = False
                            waiting_for_input = False
                            # 将分数保存到本地文件
                            with open('scores_for_simplicity.txt', 'a') as file:
                                file.write(f"{score}\n")  # 将分数写入文件
                            # 更新历史最高分
                            high_score_all_time = max(high_score_all_time, score)


if __name__ == "__main__":
    main()