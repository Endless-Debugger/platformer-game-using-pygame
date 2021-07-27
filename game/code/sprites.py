import pygame as pg
from game.code.settings import *
vec = pg.math.Vector2
import random

class Spritesheet:
    # utility class for loading and parsing spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(SPRITESHEET).convert()

    def get_image(self, x, y, width, height):
        # grab an image out of a larger spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width // 2, height // 2))
        return image

class Player(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.game.spritesheet.get_image(614, 1063, 120, 191)
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.pos = vec(WIDTH / 2, HEIGHT - 40)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def jump(self):
        # jump only if standing on a platform
        self.rect.y += 2
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 2
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -PLAYER_JUMP
            self.game.jump_sound.play()

    def update(self):
        self.animate()
        self.acc = vec(0, PLAYER_GRAV)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC

        # apply friction
        self.acc.x += self.vel.x * PLAYER_FRICT
        # equations of motion
        self.vel += self.acc
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        self.pos += self.vel + 0.2 * self.acc
        # wrap around the sides of the screen
        if self.pos.x > WIDTH + self.rect.width / 2:
            self.pos.x = 0 - self.rect.width / 2
        if self.pos.x < 0 - self.rect.width / 2:
            self.pos.x = WIDTH + self.rect.width / 2
        self.rect.midbottom = self.pos

    def load_images(self):
        self.standing_frames = [self.game.spritesheet.get_image(614, 1063, 120, 191),
                                    self.game.spritesheet.get_image(690, 406, 120, 201)]
        for frame in self.standing_frames:
            frame.set_colorkey(black)

        self.walking_r = [self.game.spritesheet.get_image(678, 860, 120, 201),
                          self.game.spritesheet.get_image(692, 1458, 120, 207)]

        self.walking_l = []
        for frame in self.walking_r:
            self.walking_l.append(pg.transform.flip(frame, True, False))
            frame.set_colorkey(black)

        self.jumping_frame = self.game.spritesheet.get_image(382, 763, 150, 181)
        self.jumping_frame.set_colorkey(black)

    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False
        if self.walking:
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walking_l)
                bottom = self.rect.bottom
                if self.vel.x > 0:
                    self.image = self.walking_r[self.current_frame]
                else:
                    self.image = self.walking_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
                self.image.set_colorkey(black)
        if not self.jumping and not self.walking:
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (self.current_frame+1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        self.mask = pg.mask.from_surface(self.image)
    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -2.5:
                self.vel.y = -2.5


class Platform(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLATFORM_LAYER
        self.groups = game.all_sprites, game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        images = [self.game.spritesheet.get_image(0, 288, 380, 94),
                  self.game.spritesheet.get_image(213, 1662, 201, 100)]
        self.image = random.choice(images)
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if random.randrange(100) < pow_likely:
            Pow(self.game, self)

class Pow(pg.sprite.Sprite):
    def __init__(self, game, plat):
        self._layer = POW_LAYER
        self.groups = game.all_sprites, game.powerups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.type = random.choice(['boost'])
        self.image = self.game.spritesheet.get_image(820, 1805, 71, 70)
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top-5

    def update(self):
        self.rect.bottom = self.plat.rect.top-5
        if not self.game.platforms.has(self.plat):
            self.kill()


class Mobs(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = MOB_LAYER
        self.group = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.group)
        self.game = game
        self.image_up = self.game.spritesheet.get_image(566, 510, 122, 139)
        self.image_up.set_colorkey(black)
        self.image_down = self.game.spritesheet.get_image(568, 1534, 122, 135)
        self.image_down.set_colorkey(black)
        self.image = self.image_up
        self.rect = self.image.get_rect()
        self.rect.centerx = random.choice([-100, WIDTH + 100])

        self.vx = random.randrange(1, 4)
        if self.rect.centerx > WIDTH:
            self.vx *= -1
        self.rect.y = random.randrange(HEIGHT / 2)
        self.vy = 0
        self.dy = 0.5

    def update(self):
        self.rect.x += self.vx
        self.vy += self.dy
        if self.vy > 3 or self.vy < -3:
            self.dy *= -1
        center = self.rect.center
        if self.dy < 0:
            self.image = self.image_up
        else:
            self.image = self.image_down
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.rect.center = center
        self.rect.y += self.vy
        if self.rect.left > WIDTH+100 or self.rect.right < -100:
            self.kill()


class Cloud(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = CLOUD_LAYER
        self.groups = game.all_sprites, game.clouds
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.cloud_images = []
        image1 = pg.image.load(r"C:\Users\yasht\PycharmProjects\Platformer\game\img\cloud1.png")
        image2 = pg.image.load(r"C:\Users\yasht\PycharmProjects\Platformer\game\img\cloud2.png")
        image3 = pg.image.load(r"C:\Users\yasht\PycharmProjects\Platformer\game\img\cloud3.png")
        self.cloud_images.append(image1)
        self.cloud_images.append(image2)
        self.cloud_images.append(image3)
        self.image = random.choice(self.cloud_images)
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH-self.rect.width)
        self.rect.y = random.randrange(-100, -50)

    def update(self):
        if self.rect.top > HEIGHT *2:
            self.kill()



