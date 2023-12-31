import pygame
from pygame.locals import *
from util.constants import *


class Player(pygame.sprite.Sprite):
    def __init__(self):
        # player variables
        self.velocity = [0.0, 0.0]
        self.jump_charge = 0
        self.jump_direction = 0

        # load sprites
        self.sprites = {}
        for player_sprite in PLAYER_SPRITES:
            sprite = pygame.image.load(f'assets/player/{player_sprite}.png').convert_alpha()
            sprite = pygame.transform.scale(sprite, (PLAYER_SIZE[0], PLAYER_SIZE[1]))
            self.sprites[player_sprite] = sprite
        # frame control
        self.frame = "fall"
        self.direction = False
        self.run = 0
        self.running = False

        # sprite variables
        super().__init__()
        self.image = None
        self.rect = self.sprites["idle"].get_rect(bottomleft=(375, 375))
        self.hitbox_diff = (2/3, 3/4)
        self.hitbox = pygame.Rect(self.rect.x, self.rect.y,
                                  PLAYER_SIZE[0] * self.hitbox_diff[0], PLAYER_SIZE[1] * self.hitbox_diff[1])
        self.update_image()

    def check_collide(self, sprites):
        # Check collisions using pygame sprite detection
        self.hitbox.x = self.rect.x + PLAYER_SIZE[0] / 6
        self.hitbox.y = self.rect.y + PLAYER_SIZE[1] / 4
        collided = pygame.sprite.spritecollide(self, sprites, False)

        for collide in collided:
            if self.hitbox.colliderect(collide.rect):
                return collide

        return None

    def jump(self):
        if self.frame != "squat":
            return
        self.jump_charge = min(self.jump_charge, -TERMINAL_VELOCITY)
        self.velocity[0] = self.jump_direction * min(self.jump_charge, -TERMINAL_VELOCITY / 3)
        self.velocity[1] = self.jump_charge
        self.jump_charge = 0
        self.frame = "jump"
        jump.play()

    def update(self, keys, sprites):
        # x motion
        self.rect.x += self.velocity[0]
        # x collision
        collided = self.check_collide(sprites)
        if collided:
            if not self.frame.startswith("run"):
                bump.play()
            self.velocity[0] = -self.velocity[0] * 0.5
            self.frame = "oof"

            if self.direction:
                self.rect.right = collided.rect.left + PLAYER_SIZE[0] / 6
            else:
                self.rect.left = collided.rect.right - PLAYER_SIZE[0] / 6
            self.direction = not self.direction

        # Check bounds
        if self.hitbox.left < 16:
            if not self.frame.startswith("run"):
                self.direction = not self.direction
                bump.play()
            self.rect.left = 16 - PLAYER_SIZE[0] / 6
            self.velocity[0] = -self.velocity[0] * 0.5
            self.frame = "oof"
        elif self.hitbox.right > WIDTH - 16:
            if not self.frame.startswith("run"):
                self.direction = not self.direction
                bump.play()

            self.rect.right = WIDTH - 16 + PLAYER_SIZE[0] / 6
            self.velocity[0] = -self.velocity[0] * 0.5
            self.frame = "oof"

        # y motion
        self.velocity[1] = max(self.velocity[1] + GRAVITY, TERMINAL_VELOCITY)
        self.rect.y -= self.velocity[1]
        # y collision
        collided = self.check_collide(sprites)
        if collided:
            if self.velocity[1] < 0:
                if self.velocity[1] < 2 * GRAVITY:
                    fall.play() if self.velocity[1] <= TERMINAL_VELOCITY else land.play()
                self.frame = "fallen" if self.velocity[1] <= TERMINAL_VELOCITY or self.frame == "fallen" else "idle"
                self.rect.bottom = collided.rect.top
                self.velocity[1] = GRAVITY
                self.velocity[0] = 0
                self.jump_direction = 0
            else:
                self.rect.top = collided.rect.bottom - PLAYER_SIZE[1] / 4
                self.velocity[1] = GRAVITY
                self.frame = "oofeR"
                bump.play()
        if self.velocity[1] < 2 * GRAVITY and self.frame.startswith("run"):
            self.velocity[0] = SPEED if self.direction else -SPEED
            self.frame = "fall"

        # player control keys
        if keys[K_SPACE] and (self.frame == "idle" or self.frame == "squat"):
            self.jump_charge += 0.75
            self.frame = "squat"

        self.running = False
        if self.frame != "jump" and self.frame != "fall" and self.frame != "oof":
            if keys[K_d]:
                self.direction = True
                if self.frame != "squat":
                    self.rect.x += SPEED
                    self.running = True
                else:
                    self.jump_direction = 1
            elif keys[K_a]:
                self.direction = False
                if self.frame != "squat":
                    self.rect.x -= SPEED
                    self.running = True
                else:
                    self.jump_direction = -1

        # Control sprite frame
        if self.running:
            self.run = (self.run + SPEED/20) % 3
            self.frame = f'run{int(self.run)}'

        self.update_image()

    def update_image(self):
        self.image = self.sprites[self.frame]
        if not self.direction:
            self.image = pygame.transform.flip(self.image, True, False)
