import pygame
import random

# 初始化 Pygame
pygame.init()

# 设置窗口大小
window_width = 1000
window_height = 800
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Snake')

# 定义颜色
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
gray = (128, 128, 128)

# 定义贪吃蛇的初始位置和长度
snake_block = 30  # 将网格大小从 20 增大到 30
snake_speed = 10
snake_list = []
snake_length = 1  # 初始长度设为1

# 生成随机初始位置
x1 = round(random.randrange(0, window_width - 200 - snake_block) / 30.0) * 30.0
y1 = round(random.randrange(0, window_height - snake_block) / 30.0) * 30.0

# 初始方向
x1_change = 0
y1_change = 0

# 生成食物
food_list = []

# 得分和等级
score = 0
level = 1

# 游戏循环
clock = pygame.time.Clock()
game_over = False
paused = False  # 用于跟踪游戏是否暂停

# 初始化贪吃蛇的位置
snake_list = [[x1, y1]]


def draw_grid():
    for x in range(0, window_width - 200, snake_block):
        pygame.draw.line(window, gray, (x, 0), (x, window_height))
    for y in range(0, window_height, snake_block):
        pygame.draw.line(window, gray, (0, y), (window_width - 200, y))


def display_controls():
    font = pygame.font.Font(None, 24)  # 使用 Pygame 内置字体
    control_text = font.render("Controls:", True, white)
    left_arrow = font.render("Left Arrow", True, white)
    right_arrow = font.render("Right Arrow", True, white)
    up_arrow = font.render("Up Arrow", True, white)
    down_arrow = font.render("Down Arrow", True, white)

    # 显示控制信息
    window.blit(control_text, (window_width - 180, 20))
    window.blit(left_arrow, (window_width - 180, 40))
    window.blit(right_arrow, (window_width - 180, 60))
    window.blit(up_arrow, (window_width - 180, 80))
    window.blit(down_arrow, (window_width - 180, 100))


def display_score_and_level(high_score_all_time):
    font = pygame.font.Font(None, 24)  # 使用 Pygame 内置字体

    # 计算文本的宽度
    score_text = font.render(f"Score: {score}", True, white)
    level_text = font.render(f"Level: {level}", True, white)
    high_score_text = font.render(f"High Score (All Time): {high_score_all_time}", True, white)

    # 获取文本的宽度
    score_text_width = score_text.get_width()
    level_text_width = level_text.get_width()
    high_score_text_width = high_score_text.get_width()

    # 计算文本的显示位置，确保它们不会超出屏幕
    score_x = window_width - 180
    level_x = window_width - 180
    high_score_x = window_width - high_score_text_width - 20  # 确保高分文本不会超出屏幕

    # 显示得分、等级和历史最高得分
    window.blit(score_text, (score_x, 140))
    window.blit(level_text, (level_x, 160))
    window.blit(high_score_text, (high_score_x, 180))


def get_high_score_from_file():
    try:
        with open('scores_for_snake.txt', 'r') as file:
            scores = [int(line.strip()) for line in file.readlines()]
            return max(scores, default=0)
    except FileNotFoundError:
        return 0


def save_score_to_file(score):
    with open('scores_for_snake.txt', 'a') as file:
        file.write(f"{score}\n")


def generate_food(snake_list, num_foods):
    food_list = []
    for _ in range(num_foods):
        while True:
            foodx = round(random.randrange(0, window_width - 200 - snake_block) / 30.0) * 30.0
            foody = round(random.randrange(0, window_height - snake_block) / 30.0) * 30.0
            if [foodx, foody] not in snake_list and [foodx, foody] not in food_list:
                food_list.append([foodx, foody])
                break
    return food_list


def update_snake_position(snake_list, x1, y1, x1_change, y1_change):
    # 更新贪吃蛇的位置
    if x1_change != 0 or y1_change != 0:  # 只有当方向改变时才更新位置
        x1 += x1_change
        y1 += y1_change

    # 检查是否撞墙
    if x1 >= window_width - 200 or x1 < 0 or y1 >= window_height or y1 < 0:
        return x1, y1, True

    # 更新贪吃蛇的位置
    snake_head = [x1, y1]
    snake_list.append(snake_head)

    if len(snake_list) > snake_length:
        del snake_list[0]

    # 检查是否撞到自己
    for segment in snake_list[:-1]:
        if segment == snake_head:
            return x1, y1, True

    return x1, y1, False


def draw_snake(snake_list):
    for segment in snake_list:
        pygame.draw.rect(window, white, [segment[0], segment[1], snake_block, snake_block])


def game_loop():
    global x1, y1, x1_change, y1_change, snake_list, snake_length, score, level, game_over, paused, food_list

    # 初始化 snake_speed
    snake_speed = 10  # 你可以根据需要调整这个初始值

    # 生成初始食物
    food_list = generate_food(snake_list, min(level, 10))

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_change != snake_block:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change != -snake_block:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change != snake_block:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change != -snake_block:
                    y1_change = snake_block
                    x1_change = 0
                elif event.key == pygame.K_p:  # 按下P键时切换暂停状态
                    paused = not paused  # 切换暂停标志

        if not paused:  # 只有当游戏未暂停时才执行游戏逻辑
            # 更新贪吃蛇的位置
            x1, y1, game_over = update_snake_position(snake_list, x1, y1, x1_change, y1_change)

            # 绘制背景
            window.fill(black)

            # 绘制网格
            draw_grid()

            # 绘制食物
            for food in food_list:
                pygame.draw.rect(window, red, [food[0], food[1], snake_block, snake_block])

            # 绘制贪吃蛇
            draw_snake(snake_list)

            # 显示控制信息
            display_controls()

            # 显示得分和等级
            display_score_and_level(high_score_all_time)

            # 更新屏幕
            pygame.display.update()

            # 检查是否吃到食物
            for i, food in enumerate(food_list):
                if x1 == food[0] and y1 == food[1]:
                    food_list.pop(i)
                    snake_length += 1
                    score += 10
                    if score % 100 == 0:
                        level += 1
                        snake_speed += 1  # 增加速度以增加难度
                    break

            # 生成新的食物
            if len(food_list) < min(level, 10):
                new_foods = generate_food(snake_list, min(level, 10) - len(food_list))
                food_list.extend(new_foods)

            # 控制游戏速度
            clock.tick(snake_speed)

        else:  # 当游戏暂停时
            # 清屏并绘制背景
            window.fill(black)

            # 绘制网格、控制信息、得分和等级
            draw_grid()
            display_controls()
            display_score_and_level(high_score_all_time)

            # 绘制食物
            for food in food_list:
                pygame.draw.rect(window, red, [food[0], food[1], snake_block, snake_block])

            # 绘制贪吃蛇
            draw_snake(snake_list)

            # 显示“PAUSED”提示
            font = pygame.font.Font(None, 48)
            pause_text = font.render("PAUSED", True, white)
            window.blit(pause_text, (window_width // 2 - 50, window_height // 2 - 24))  # 屏幕中心显示

            # 更新屏幕
            pygame.display.update()

            # 在暂停状态下不更新游戏速度
            clock.tick(1)  # 减慢帧率，防止闪烁


def game_over_screen():
    global score, high_score_all_time, running

    # 显示游戏结束信息
    font = pygame.font.Font(None, 48)  # 使用具体的字体名称
    game_over_text = font.render("Game Over", True, white)
    restart_text = font.render("Press R to Restart | Press Q to Exit", True, white)
    waiting_for_input = True

    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting_for_input = False
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # 按R键重新开始游戏
                    waiting_for_input = False
                    # 重置游戏状态
                    reset_game()
                elif event.key == pygame.K_q:  # 按Q键退出游戏
                    waiting_for_input = False
                    running = False

        # 清屏并绘制背景
        window.fill(black)
        draw_grid()
        display_controls()
        display_score_and_level(high_score_all_time)

        # 显示游戏结束信息
        window.blit(game_over_text, (window_width // 2 - 100, window_height // 2 - 50))
        window.blit(restart_text, (window_width // 2 - 100, window_height // 2 + 10))

        # 更新屏幕
        pygame.display.update()

        # 控制游戏速度
        clock.tick(10)  # 减慢帧率，防止闪烁


def reset_game():
    global x1, y1, x1_change, y1_change, snake_list, snake_length, score, level, game_over, paused, food_list
    x1 = round(random.randrange(0, window_width - 200 - snake_block) / 30.0) * 30.0
    y1 = round(random.randrange(0, window_height - snake_block) / 30.0) * 30.0
    x1_change = 0
    y1_change = 0
    food_list = generate_food(snake_list, min(level, 10))
    score = 0
    level = 1
    snake_list = [[x1, y1]]
    snake_length = 1
    game_over = False
    paused = False


def display_initial_screen():
    initial_texts = [
        "Welcome to Snake Game",
        "Press Space to Start"
    ]
    font = pygame.font.Font(None, 48)

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # 按空格键开始游戏
                    waiting_for_input = False

        window.fill(black)

        # 绘制多行文字
        for i, text in enumerate(initial_texts):
            text_surface = font.render(text, True, white)
            text_rect = text_surface.get_rect(center=(window_width // 2, window_height // 2 + i * 50))
            window.blit(text_surface, text_rect)

        pygame.display.update()
        clock.tick(10)  # 减慢帧率，防止闪烁

    # 返回 True 表示用户已经按下空格键
    return True


high_score_all_time = get_high_score_from_file()  # 从文件中读取历史最高分

# 主循环
running = True

# 显示初始屏幕
if display_initial_screen():
    game_loop()  # 用户按下空格键后开始游戏循环

# 游戏结束后处理
if game_over:
    game_over_screen()
