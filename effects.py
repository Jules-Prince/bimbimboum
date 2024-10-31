import pygame
import random
import math
from constants import *

class Particle:
    def __init__(self, pos, color, speed, lifetime):
        self.pos = pygame.math.Vector2(pos)
        self.velocity = pygame.math.Vector2(
            random.uniform(-speed, speed),
            random.uniform(-speed, speed)
        )
        # Ensure color values are integers
        self.color = tuple(int(c) for c in color[:3])  # Take only RGB values
        self.lifetime = lifetime
        self.birth_time = pygame.time.get_ticks()
        self.alive = True

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.birth_time > self.lifetime:
            self.alive = False
            return
        
        self.pos += self.velocity
        self.velocity *= 0.95  # Slow down over time

    def draw(self, screen):
        # Calculate alpha based on remaining lifetime
        remaining_time = self.lifetime - (pygame.time.get_ticks() - self.birth_time)
        alpha = int(255 * (remaining_time / self.lifetime))
        
        # Ensure the position is converted to integers
        pos = (int(self.pos.x), int(self.pos.y))
        # Draw directly to screen with current color
        pygame.draw.circle(screen, self.color, pos, 2)

class EffectManager:
    def __init__(self):
        self.particles = []
        self.screen_shake = 0
        self.screen_shake_intensity = 0
        
    def create_explosion(self, pos, color, count=20):
        for _ in range(count):
            self.particles.append(
                Particle(pos, color, 5, 500)  # 500ms lifetime
            )
            
    def create_hit_effect(self, pos):
        for _ in range(5):
            self.particles.append(
                Particle(pos, (255, 255, 255), 3, 200)
            )
            
    def add_screen_shake(self, intensity, duration):
        self.screen_shake = duration
        self.screen_shake_intensity = intensity

    def update(self):
        # Update particles
        current_time = pygame.time.get_ticks()
        self.particles = [p for p in self.particles if p.alive]
        for particle in self.particles:
            particle.update()
            
        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake -= 1

    def draw(self, screen):
        # Draw particles
        for particle in self.particles:
            if particle.alive:
                particle.draw(screen)
            
        # Apply screen shake
        if self.screen_shake > 0:
            offset = (
                random.randint(-self.screen_shake_intensity, self.screen_shake_intensity),
                random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
            )
            screen.blit(screen, offset)

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, images, pos, animation_speed):
        super().__init__()
        self.images = images
        self.image = images[0]
        self.rect = self.image.get_rect(center=pos)
        self.animation_speed = animation_speed
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.images)
            self.image = self.images[self.current_frame]