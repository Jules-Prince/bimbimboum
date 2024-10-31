import pygame
import random
import math
from constants import *

class BaseEnemy(pygame.sprite.Sprite):
    def __init__(self, pos=None):
        super().__init__()
        if pos is None:
            self.position = self.random_spawn_position()
        else:
            self.position = pygame.math.Vector2(pos)
        self.rect.center = self.position
        
    def random_spawn_position(self):
        side = random.randint(0, 3)
        if side == 0:  # top
            return pygame.math.Vector2(
                random.randint(0, SCREEN_WIDTH),
                -self.rect.height
            )
        elif side == 1:  # right
            return pygame.math.Vector2(
                SCREEN_WIDTH + self.rect.width,
                random.randint(0, SCREEN_HEIGHT)
            )
        elif side == 2:  # bottom
            return pygame.math.Vector2(
                random.randint(0, SCREEN_WIDTH),
                SCREEN_HEIGHT + self.rect.height
            )
        else:  # left
            return pygame.math.Vector2(
                -self.rect.width,
                random.randint(0, SCREEN_HEIGHT)
            )

class BasicEnemy(BaseEnemy):
    def __init__(self, pos=None):
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        super().__init__(pos)
        self.speed = ENEMY_SPEED
        self.health = 1
        self.score_value = 10

    def update(self, player_pos):
        direction = pygame.math.Vector2(player_pos) - self.position
        if direction.length() > 0:
            direction = direction.normalize()
        self.position += direction * self.speed
        self.rect.center = self.position

class FastEnemy(BaseEnemy):
    def __init__(self, pos=None):
        self.image = pygame.Surface((ENEMY_SIZE - 5, ENEMY_SIZE - 5))
        self.image.fill((255, 150, 150))
        self.rect = self.image.get_rect()
        super().__init__(pos)
        self.speed = ENEMY_SPEED * 1.5
        self.health = 1
        self.score_value = 15

    def update(self, player_pos):
        direction = pygame.math.Vector2(player_pos) - self.position
        if direction.length() > 0:
            direction = direction.normalize()
        self.position += direction * self.speed
        self.rect.center = self.position

class TankEnemy(BaseEnemy):
    def __init__(self, pos=None):
        self.image = pygame.Surface((ENEMY_SIZE + 10, ENEMY_SIZE + 10))
        self.image.fill((139, 0, 0))
        self.rect = self.image.get_rect()
        super().__init__(pos)
        self.speed = ENEMY_SPEED * 0.7
        self.health = 3
        self.score_value = 25

    def update(self, player_pos):
        direction = pygame.math.Vector2(player_pos) - self.position
        if direction.length() > 0:
            direction = direction.normalize()
        self.position += direction * self.speed
        self.rect.center = self.position

class CirclingEnemy(BaseEnemy):
    def __init__(self, pos=None):
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect()
        super().__init__(pos)
        self.speed = ENEMY_SPEED * 0.8
        self.angle = random.uniform(0, 2 * math.pi)
        self.circle_radius = 100
        self.circle_speed = 0.05
        self.health = 1
        self.score_value = 20

    def update(self, player_pos):
        # Move toward player while circling
        direction = pygame.math.Vector2(player_pos) - self.position
        distance = direction.length()
        
        if distance > self.circle_radius:
            # Move toward player if too far
            if direction.length() > 0:
                direction = direction.normalize()
            self.position += direction * self.speed
        else:
            # Circle around player
            self.angle += self.circle_speed
            offset = pygame.math.Vector2(
                math.cos(self.angle) * self.circle_radius,
                math.sin(self.angle) * self.circle_radius
            )
            self.position = pygame.math.Vector2(player_pos) + offset
            
        self.rect.center = self.position

class EnemySpawner:
    def __init__(self, game):
        self.game = game
        self.enemy_types = [
            (BasicEnemy, 60),    # (class, weight)
            (FastEnemy, 20),
            (TankEnemy, 10),
            (CirclingEnemy, 10)
        ]
        self.total_weight = sum(weight for _, weight in self.enemy_types)
        self.spawn_rate = 0.02
        self.time_elapsed = 0
        
    def update(self, dt):
        self.time_elapsed += dt
        # Increase spawn rate over time
        self.spawn_rate = min(0.05, 0.02 + (self.time_elapsed / 60000) * 0.03)
        
        if random.random() < self.spawn_rate:
            self.spawn_enemy()
            
    def spawn_enemy(self):
        roll = random.randint(1, self.total_weight)
        cumulative_weight = 0
        
        for enemy_class, weight in self.enemy_types:
            cumulative_weight += weight
            if roll <= cumulative_weight:
                enemy = enemy_class()
                self.game.enemies.add(enemy)
                self.game.all_sprites.add(enemy)
                break