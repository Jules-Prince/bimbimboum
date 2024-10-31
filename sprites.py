import pygame
import math
from constants import *

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(GREEN)
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.position = pygame.math.Vector2(self.rect.center)
        
        # Stats
        self.speed = PLAYER_SPEED
        self.lives = 3
        self.has_shield = False
        self.spread_shot = False
        
        # Invulnerability
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 2000
        self.flash_interval = 200

    def move(self, dx: float, dy: float) -> None:
        if dx != 0 and dy != 0:
            # Normalize diagonal movement
            length = math.sqrt(dx * dx + dy * dy)
            dx /= length
            dy /= length

        self.position.x += dx * self.speed
        self.position.y += dy * self.speed
        
        # Keep player on screen
        self.position.x = max(PLAYER_SIZE // 2, min(SCREEN_WIDTH - PLAYER_SIZE // 2, self.position.x))
        self.position.y = max(PLAYER_SIZE // 2, min(SCREEN_HEIGHT - PLAYER_SIZE // 2, self.position.y))
        self.rect.center = self.position

    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Handle invulnerability
        if self.invulnerable:
            if current_time - self.invulnerable_timer > self.invulnerable_duration:
                self.invulnerable = False
                self.image = self.original_image
            else:
                # Flash effect
                if (current_time // self.flash_interval) % 2:
                    self.image = self.original_image
                else:
                    self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
                    self.image.fill(YELLOW)

        # Shield visual effect
        if self.has_shield:
            pygame.draw.circle(self.image, LIGHT_BLUE, 
                             (PLAYER_SIZE // 2, PLAYER_SIZE // 2), 
                             PLAYER_SIZE // 2 + 2, 2)

    def hit(self) -> bool:
        """Returns True if player dies from this hit"""
        if not self.invulnerable:
            self.lives -= 1
            self.make_invulnerable()
            return self.lives <= 0
        return False

    def make_invulnerable(self):
        self.invulnerable = True
        self.invulnerable_timer = pygame.time.get_ticks()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos, angle_offset=0):
        super().__init__()
        self.image = pygame.Surface((BULLET_SIZE, BULLET_SIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.position = pygame.math.Vector2(start_pos)
        self.rect.center = self.position

        # Calculate direction with angle offset
        direction = pygame.math.Vector2(target_pos) - pygame.math.Vector2(start_pos)
        if direction.length() > 0:
            direction = direction.normalize()
            
            # Apply angle offset
            if angle_offset != 0:
                angle = math.radians(angle_offset)
                direction = pygame.math.Vector2(
                    direction.x * math.cos(angle) - direction.y * math.sin(angle),
                    direction.x * math.sin(angle) + direction.y * math.cos(angle)
                )

        self.velocity = direction * BULLET_SPEED

    def update(self):
        self.position += self.velocity
        self.rect.center = self.position
        
        # Kill if off screen
        if not (0 <= self.position.x <= SCREEN_WIDTH and 0 <= self.position.y <= SCREEN_HEIGHT):
            self.kill()