# jump game
import pygame
from settings import *
from sprites import *
from os import path



class Game:
    def __init__(self):
        # initialize the game window
        self.running = True
        pygame.init()
        # initializing sound effects
        # making the screen
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        pygame.mixer.pause()
        self.font_name = FONT_NAME

        self.load_data()

    def load_data(self):
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, "img")
        sound_dir = path.join(self.dir, "sound")
        self.jump_sound = pygame.mixer.Sound(r"C:\Users\yasht\PycharmProjects\Platformer\game\sound\jump.wav")
        self.boost_sound = pygame.mixer.Sound(r"C:\Users\yasht\PycharmProjects\Platformer\game\sound\platform_part 15_snd_Boost16.wav")
        f = open(HS_FILE, "r")
        x = 0
        for i in f:
            x = i
        self.highscore = int(x)
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))


    def new(self):
        # start a new game
        self.score = 0
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.platforms = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()
        self.mob_timer = 0
        self.p1 = Player(self)
        for plat in PLAT_LIST:
            p = Platform(self, *plat)
        pygame.mixer.music.load(r"C:\Users\yasht\PycharmProjects\Platformer\game\sound\soundtrack2.ogg")
        pygame.mixer.music.play(loops=1)

        for i in range(6):
            c = Cloud(self)
            c.rect.y += random.randrange(50, 200)
        self.run()

    def run(self):
        # game loop
        self.playing = True
        while self.playing:
            self.clock.tick(fps)
            self.events()
            self.update()
            self.draw()
        pygame.mixer.music.fadeout(500)

    def update(self):
        # updating our loop
        self.all_sprites.update()
        now = pg.time.get_ticks()
        if now - self.mob_timer > mob_likely + random.choice([1000, 2000, -1000, -2000, 500, -500]):
            self.mob_timer = now
            Mobs(self)
        mob_hits = pygame.sprite.spritecollide(self.p1, self.mobs, False, pygame.sprite.collide_mask)
        if mob_hits:
            self.playing = False
        if self.p1.vel.y > 0:
            hits = pygame.sprite.spritecollide(self.p1, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.p1.pos.x < lowest.rect.right + 10 and self.p1.pos.x > lowest.rect.left -10:
                    if self.p1.pos.y < lowest.rect.centery:
                        self.p1.pos.y = lowest.rect.top
                        self.p1.vel.y = 0
                        self.p1.jumping = False
        self.platforms.update()
        if self.p1.rect.top <= HEIGHT / 4:
            if random.randrange(25) < 1:
                Cloud(self)
            self.p1.pos.y += max(abs(self.p1.vel.y), 2)
            for cloud in self.clouds:
                cloud.rect.y += max(abs(self.p1.vel.y / 2), 2)
            for mob in self.mobs:
                mob.rect.y += max(abs(self.p1.vel.y), 2)
            for plat in self.platforms:
                plat.rect.y += max(abs(self.p1.vel.y), 2)
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.score += 10
        pow_hits = pygame.sprite.spritecollide(self.p1, self.powerups, True)
        for pow in pow_hits:
            if pow.type == 'boost':
                self.boost_sound.play()
                self.p1.vel.y = -BOOST_POWER
                self.p1.jumping = False
        if self.p1.rect.bottom > HEIGHT:
            for sprites in self.all_sprites:
                sprites.rect.y -= max(self.p1.vel.y, 10)
                if sprites.rect.bottom < 0:
                    sprites.kill()
        if len(self.platforms) == 0:
            self.playing = False
        while len(self.platforms) < plat_likely:
            Width = random.randrange(90, 120)
            p = Platform(self, random.randrange(0, WIDTH - Width),
                         random.randrange(-75, -30))
            self.platforms.add(p)
            self.all_sprites.add(p)


    def events(self):
        # events in our game loop
        for event in pygame.event.get():
            # checking for quiting the game
            if event.type == pygame.QUIT:
                if self.running:
                    self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.p1.jump()
            if event.type == pygame.KEYUP:
                self.p1.jump_cut()

    def draw(self):
        # drawing our sprites in the loop
        self.screen.fill(light_blue)
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 22, red, WIDTH / 2, 15)
        pygame.display.flip()

    def show_start_screen(self):
        # start screen of our game
        pygame.mixer.music.load(r"C:\Users\yasht\PycharmProjects\Platformer\game\sound\soundtrack.ogg")
        pygame.mixer.music.play(loops=-1)
        pygame.mixer.music.fadeout(500)
        self.screen.fill(light_blue)
        self.draw_text(title, 64, black, WIDTH / 2, HEIGHT / 4)
        self.draw_text("space to jump, arrows to move", 22, white, WIDTH / 2, HEIGHT / 2)
        self.draw_text("press a key to start", 22, white, WIDTH / 2, HEIGHT / 1.5)
        pygame.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        # end screen of our
        if not self.running:
            return
        pygame.mixer.music.load(r"C:\Users\yasht\PycharmProjects\Platformer\game\sound\soundtrack.ogg")
        pygame.mixer.music.play(loops=-1)
        self.screen.fill(light_blue)
        self.draw_text("GAME OVER", 64, white, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Score =" + str(self.score), 22, white, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play again", 22, white, WIDTH / 2, HEIGHT * 3 / 4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("New High Score!", 22, white, WIDTH / 2, HEIGHT / 2 + 60)
            with open(path.join(self.dir, HS_FILE), "w") as f:
                f.write(str(self.score))
        else:
            self.draw_text("High Score:" + str(self.highscore), 22, white, WIDTH / 2, HEIGHT / 2 + 90)

        pygame.display.flip()
        self.wait_for_key()
        pygame.mixer.music.fadeout(500)

    def draw_text(self, text, size, color, x, y):
        font = pygame.font.Font("freesansbold.ttf", size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    waiting = False


g = Game()
g.show_start_screen()
while g.running:
    pygame.mixer.music.load(r"C:\Users\yasht\PycharmProjects\Platformer\game\sound\soundtrack2.ogg")
    pygame.mixer.music.play(loops=1)
    g.new()
    g.show_go_screen()
pygame.quit()
