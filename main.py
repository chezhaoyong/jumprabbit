import pygame as pg
import random
import os
from settings import *
from sprites import *

class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        # 设置绘制时使用的字体
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()

    def load_data(self): # 加载数据
        self.dir = os.path.dirname(__file__)
        filepath = os.path.join(self.dir, HS_FILE)
        with open(filepath, 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0
        img_dir = os.path.join(self.dir, 'img')
        # 加载精灵图片
        self.spritesheet = Spritesheet(os.path.join(img_dir, SPRITESHEET))



    def new(self):
        self.score = 0
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.player = Player(self)
        self.all_sprites.add(self.player)
        for plat in PLATFORM_LIST:
            p = Platform(*plat)
            self.all_sprites.add(p)
            self.platforms.add(p)
        self.run()

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        self.all_sprites.update()
        # # 玩家在界面中时(y>0)，进行碰撞检测，检测玩家是否碰撞到平台
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                self.player.pos.y = hits[0].rect.top
                self.player.vel.y = 0
        # if player reaches top 1/4 of screen
        # 玩家到达游戏框 1/4 处时（注意，游戏框，头部为0，底部为游戏框长度，到到游戏框的1/4处，表示已经到达了顶部一部分了）
        if self.player.rect.top <= HEIGHT / 4:
            # 玩家位置移动（往下移动）
            self.player.pos.y += abs(self.player.vel.y)
            # 平台在游戏框外时，将其注销，避免资源浪费
            for plat in self.platforms:
                # 平台移动位置（往下移动，移动的距离与玩家相同，这样玩家才能依旧站立在原本的平台上）
                plat.rect.y += abs(self.player.vel.y)
                if plat.rect.top >= HEIGHT: 
                    plat.kill()
                    # 分数增加 - 平台销毁，分数相加
                    self.score += 10

         # 死亡 - 玩家底部大于游戏框高度
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                # 元素底部小于0 - 说明在游戏框外面，将其删除
                if sprite.rect.bottom < 0:
                    sprite.kill()

        # 平台个数为0，游戏结束
        if len(self.platforms) == 0:
            self.playing = False

        # 判断平台数，产生新的平台
        while len(self.platforms) < 6:
            width = random.randrange(50, 100)
            # 平台虽然是随机生成的，但会生成在某一个范围内
            p = Platform(random.randrange(0, WIDTH - width),
                         random.randrange(-75, -30),
                         width, 20)
            self.platforms.add(p)
            self.all_sprites.add(p)

    # 事件处理
    def events(self):
        for event in pg.event.get():
            # 关闭
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            # 跳跃
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()

    def draw(self):
        # 绘制
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        # 绘制文字 - 具体的分数
        self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)
        # 翻转
        pg.display.flip()

    # 开始游戏的钩子函数
    def show_start_screen(self):
        # game splash/start screen
        self.screen.fill(BGCOLOR) # 填充颜色
        # 绘制文字
        self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Left and right button move, space bar jump", 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press any key to start the game", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        # 画布翻转
        pg.display.flip()
        self.wait_for_key() # 等待用户敲击键盘中的仍以位置

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT: # 点击退出，结束等待循环
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP: # 按下键盘，结束等待循环
                    waiting = False

    def show_go_screen(self):
        # game over/continue
        if not self.running: # 是否在运行
            return
        self.screen.fill(BGCOLOR) # 游戏框背景颜色填充
        # 绘制文字
        self.draw_text("GAME OVER", 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Score: " + str(self.score), 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play again", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        # 判断分数
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NEW HIGH SCORE!", 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
            # 记录新的最高分到文件中 - 持久化
            with open(os.path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
        # 翻转
        pg.display.flip()
        # 等待敲击任意键，
        self.wait_for_key()

    # 绘制文字
    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size) # 设置字体与大小
        text_surface = font.render(text, True, color) # 设置颜色
        text_rect = text_surface.get_rect() # 获得字体对象
        text_rect.midtop = (x, y) # 定义位置
        self.screen.blit(text_surface, text_rect) # 在屏幕中绘制字体

g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()
