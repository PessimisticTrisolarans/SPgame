import pygame
import random

# 初始化 Pygame
pygame.init()

# 设置窗口大小
window_width = 1000
window_height = 800
play_area_width = window_width - 200  # 游戏区域宽度
info_panel_width = 200  # 信息面板宽度
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Snake')

# 定义颜色
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
gray = (128, 128, 128)

class Snake:
    def __init__(self, x, y, block_size):
        self.block_size = block_size
        self.body = [[x, y]]
        self.directions = {'UP': (0, -block_size), 'DOWN': (0, block_size), 'LEFT': (-block_size, 0), 'RIGHT': (block_size, 0)}
        self.current_direction = None  # 初始化为 None
        self.grow = False

    def move(self):
        if self.current_direction is None:
            return  # 如果当前方向为 None，则不移动
        dx, dy = self.directions[self.current_direction]
        new_head = [self.body[-1][0] + dx, self.body[-1][1] + dy]
        if self.grow:
            self.body.append(new_head)
            self.grow = False
        else:
            self.body.pop(0)
            self.body.append(new_head)

    def change_direction(self, direction):
        opposite_direction = {'UP': 'DOWN', 'DOWN': 'UP', 'LEFT': 'RIGHT', 'RIGHT': 'LEFT'}
        if direction != opposite_direction.get(self.current_direction, None):
            self.current_direction = direction

    def grow_snake(self):
        self.grow = True

    def check_collision(self, play_area_width, window_height):
        head = self.body[-1]
        if (head[0] < 0 or head[0] >= play_area_width or
                head[1] < 0 or head[1] >= window_height or
                head in self.body[:-1]):
            return True
        return False


class Food:
    def __init__(self, snake_body, block_size, play_area_width, window_height, level):
        self.block_size = block_size
        self.play_area_width = play_area_width
        self.window_height = window_height
        self.foods = self.generate_foods(snake_body, min(level, 10))  # 根据level生成食物，但不超过10个

    def generate_foods(self, snake_body, num_foods):
        foods = []
        while len(foods) < num_foods:
            food_x = round(random.randrange(0, self.play_area_width - self.block_size) / self.block_size) * self.block_size
            food_y = round(random.randrange(0, self.window_height - self.block_size) / self.block_size) * self.block_size
            if [food_x, food_y] not in snake_body and [food_x, food_y] not in foods:  # 确保新食物不在蛇身上也不与其他食物重叠
                foods.append([food_x, food_y])
        return foods


class Scoreboard:
    def __init__(self, high_score_all_time):
        self.score = 0
        self.high_score_all_time = high_score_all_time
        self.level = 1

    def update_score(self, points):
        self.score += points
        if self.score % 100 == 0:
            self.level += 1

    def get_high_score_from_file(self):
        try:
            with open('scores_for_snake.txt', 'r') as file:
                scores = [int(line.strip()) for line in file.readlines()]
                return max(scores, default=0)
        except FileNotFoundError:
            return 0

    def save_score_to_file(self, score):
        with open('scores_for_snake.txt', 'a') as file:
            file.write(f"{score}\n")


class Game:
    def __init__(self, window, play_area_width, window_height, info_panel_width, block_size, snake_speed):
        self.window = window
        self.play_area_width = play_area_width
        self.window_height = window_height
        self.info_panel_width = info_panel_width
        self.block_size = block_size
        self.snake_speed = snake_speed
        self.clock = pygame.time.Clock()
        self.game_over = False
        self.paused = False
        self.started = False  # 玩家按下方向键后开始游戏
        self.snake = Snake(self.round_to_grid(play_area_width // 2), self.round_to_grid(window_height // 2), block_size)
        self.scoreboard = Scoreboard(self.get_high_score_from_file())
        self.food = Food(self.snake.body, self.block_size, self.play_area_width, self.window_height, self.scoreboard.level)  # 传入初始level

    def round_to_grid(self, value):
        return round(value / self.block_size) * self.block_size

    def draw_grid(self):
        for x in range(0, self.play_area_width, self.block_size):
            pygame.draw.line(self.window, gray, (x, 0), (x, self.window_height))
        for y in range(0, self.window_height, self.block_size):
            pygame.draw.line(self.window, gray, (0, y), (self.play_area_width, y))

    def display_controls(self):
        font = pygame.font.Font(None, 24)
        control_text = font.render("Controls:", True, white)
        left_arrow = font.render("Left Arrow", True, white)
        right_arrow = font.render("Right Arrow", True, white)
        up_arrow = font.render("Up Arrow", True, white)
        down_arrow = font.render("Down Arrow", True, white)
        self.window.blit(control_text, (self.play_area_width + 20, 20))
        self.window.blit(left_arrow, (self.play_area_width + 20, 40))
        self.window.blit(right_arrow, (self.play_area_width + 20, 60))
        self.window.blit(up_arrow, (self.play_area_width + 20, 80))
        self.window.blit(down_arrow, (self.play_area_width + 20, 100))

    def display_score_and_level(self):
        font = pygame.font.Font(None, 24)
        score_text = font.render(f"Score: {self.scoreboard.score}", True, white)
        level_text = font.render(f"Level: {self.scoreboard.level}", True, white)
        high_score_text = font.render(f"High Score (All Time): {self.scoreboard.high_score_all_time}", True, white)
        self.window.blit(score_text, (self.play_area_width + 20, 140))
        self.window.blit(level_text, (self.play_area_width + 20, 160))
        self.window.blit(high_score_text, (self.play_area_width + 5, 180))

    def run(self):
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.snake.change_direction('LEFT')
                        self.started = True
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction('RIGHT')
                        self.started = True
                    elif event.key == pygame.K_UP:
                        self.snake.change_direction('UP')
                        self.started = True
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction('DOWN')
                        self.started = True
                    elif event.key == pygame.K_p:
                        self.paused = not self.paused

            if not self.paused and self.started:
                self.snake.move()
                if self.snake.check_collision(self.play_area_width, self.window_height):
                    self.game_over = True

                # 检查蛇是否吃到食物
                for food_pos in self.food.foods:
                    if self.snake.body[-1] == food_pos:
                        self.snake.grow_snake()
                        self.scoreboard.update_score(10)
                        self.food.foods.remove(food_pos)  # 移除被吃掉的食物
                        break

                # 如果所有食物都被吃完了，重新生成食物
                if len(self.food.foods) == 0:
                    self.food = Food(self.snake.body, self.block_size, self.play_area_width, self.window_height, self.scoreboard.level)

            # 绘制背景
            self.window.fill(black)
            pygame.draw.rect(self.window, black, (self.play_area_width, 0, self.info_panel_width, self.window_height))  # 信息面板背景
            self.draw_grid()
            self.display_controls()
            self.display_score_and_level()

            # 绘制食物
            for food_pos in self.food.foods:
                pygame.draw.rect(self.window, red, [food_pos[0], food_pos[1], self.block_size, self.block_size])

            # 绘制贪吃蛇
            for segment in self.snake.body:
                pygame.draw.rect(self.window, white, [segment[0], segment[1], self.block_size, self.block_size])

            # 当游戏暂停时显示"paused"
            if self.paused:
                font = pygame.font.Font(None, 48)
                paused_text = font.render("Paused", True, white)
                self.window.blit(paused_text, (self.play_area_width // 2 - 50, self.window_height // 2 - 50))

            pygame.display.update()
            self.clock.tick(self.snake_speed)

            if self.game_over:
                self.handle_game_over()

    def handle_game_over(self):
        # 游戏结束后的处理
        font = pygame.font.Font(None, 48)
        game_over_text = font.render("Game Over", True, white)
        restart_text = font.render("Press R to Restart | Press Q to Exit", True, white)
        waiting_for_input = True

        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting_for_input = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # 按R键重新开始游戏
                        self.reset_game()
                        self.game_over = False
                        waiting_for_input = False
                    elif event.key == pygame.K_q:  # 按Q键退出游戏
                        waiting_for_input = False
                        self.save_score_to_file(self.scoreboard.score)
                        pygame.quit()
                        exit()

            # 绘制游戏结束信息
            self.window.fill(black)
            pygame.draw.rect(self.window, black, (self.play_area_width, 0, self.info_panel_width, self.window_height))  # 信息面板背景
            self.draw_grid()
            self.display_controls()
            self.display_score_and_level()
            self.window.blit(game_over_text, (self.play_area_width // 2 - 100, self.window_height // 2 - 50))
            self.window.blit(restart_text, (self.play_area_width // 2 - 100, self.window_height // 2 + 10))

            pygame.display.update()
            self.clock.tick(10)  # 减慢帧率，防止闪烁

    def reset_game(self):
        self.snake = Snake(self.round_to_grid(play_area_width // 2), self.round_to_grid(window_height // 2), self.block_size)
        self.scoreboard = Scoreboard(self.get_high_score_from_file())
        self.food = Food(self.snake.body, self.block_size, self.play_area_width, self.window_height, self.scoreboard.level)
        self.game_over = False
        self.paused = False
        self.started = False  # 重置游戏开始标志

    def get_high_score_from_file(self):
        try:
            with open('scores_for_snake.txt', 'r') as file:
                scores = [int(line.strip()) for line in file.readlines()]
                return max(scores, default=0)
        except FileNotFoundError:
            return 0

    def save_score_to_file(self, score):
        with open('scores_for_snake.txt', 'a') as file:
            file.write(f"{score}\n")

if __name__ == '__main__':
    game = Game(window, play_area_width, window_height, info_panel_width, 30, 10)
    game.run()
