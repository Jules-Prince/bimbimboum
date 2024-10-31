import pygame
import sys
import random
from typing import Optional, Tuple
from constants import *
from sprites import Player, Bullet
from enemies import EnemySpawner
from powerups import PowerUpManager
from effects import EffectManager

class Game:
    def __init__(self, settings, sound_manager):
        self.settings = settings
        self.sound_manager = sound_manager
        
        self.clock = pygame.time.Clock()
        self.dt = 0  # Delta time for frame-independent updates
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        
        # Initialize systems
        self.player = Player()
        self.all_sprites.add(self.player)
        
        self.enemy_spawner = EnemySpawner(self)
        self.powerup_manager = PowerUpManager(self)
        self.effect_manager = EffectManager()
        
        # Game state
        self.score = 0
        self.game_over = False
        self.last_shot = 0
        self.wave = 1
        self.wave_timer = pygame.time.get_ticks()
        self.font = pygame.font.Font(None, 36)

    def handle_input(self) -> None:
        keys = pygame.key.get_pressed()
        dx = (keys[self.settings.controls['RIGHT']] - 
              keys[self.settings.controls['LEFT']])
        dy = (keys[self.settings.controls['DOWN']] - 
              keys[self.settings.controls['UP']])
        self.player.move(dx, dy)

        # Shooting
        mouse_pressed = pygame.mouse.get_pressed()[0]
        if mouse_pressed:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot > SHOOT_DELAY:
                self.last_shot = current_time
                mouse_pos = pygame.mouse.get_pos()
                self.shoot(mouse_pos)

    def shoot(self, target_pos: Tuple[int, int]) -> None:
        # Normal shot
        bullet = Bullet(self.player.rect.center, target_pos)
        self.all_sprites.add(bullet)
        self.bullets.add(bullet)
        
        # Spread shot if power-up is active
        if self.player.spread_shot:
            spread_angles = [-15, 15]  # Degrees
            for angle in spread_angles:
                bullet = Bullet(self.player.rect.center, target_pos, angle)
                self.all_sprites.add(bullet)
                self.bullets.add(bullet)
        
        self.sound_manager.play('shoot')
        self.effect_manager.create_hit_effect(self.player.rect.center)

    def check_collisions(self) -> None:
        # Bullet-enemy collisions
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
        for enemy, bullets in hits.items():
            enemy.health -= len(bullets)
            if enemy.health <= 0:
                self.score += enemy.score_value
                self.effect_manager.create_explosion(enemy.rect.center, RED)
                self.sound_manager.play('kill')
                enemy.kill()
            else:
                self.effect_manager.create_hit_effect(enemy.rect.center)

        # Player-enemy collisions
        if not self.player.invulnerable:
            enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
            if enemy_hits:
                for enemy in enemy_hits:
                    self.effect_manager.create_explosion(enemy.rect.center, RED)
                if not self.player.has_shield:
                    self.sound_manager.play('shield')
                    if self.player.hit():  # Returns True if player dies
                        self.game_over = True
                        self.effect_manager.create_explosion(self.player.rect.center, GREEN, 40)
                        self.effect_manager.add_screen_shake(10, 30)
                else:
                    self.player.has_shield = False  # Remove shield

        # Player-powerup collisions
        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in powerup_hits:
            self.powerup_manager.collect_powerup(powerup)
            self.sound_manager.play('powerup')

    def update_wave(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.wave_timer > WAVE_DURATION:
            self.wave += 1
            self.wave_timer = current_time
            self.enemy_spawner.spawn_rate *= 1.2  # Increase spawn rate
            self.effect_manager.add_screen_shake(5, 20)

    def update(self) -> None:
        if not self.game_over:
            # Calculate delta time
            self.dt = self.clock.tick(FPS) / 1000.0
            
            self.handle_input()
            self.update_wave()
            
            # Update all systems
            self.player.update()
            self.enemy_spawner.update(self.dt)
            self.powerup_manager.update()
            self.effect_manager.update()
            
            # Update sprites
            self.bullets.update()
            self.enemies.update(pygame.math.Vector2(self.player.rect.center))
            self.powerups.update()
            
            self.check_collisions()

    def draw_hud(self, screen):
        # Score
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Wave
        wave_text = self.font.render(f'Wave: {self.wave}', True, WHITE)
        wave_rect = wave_text.get_rect(midtop=(SCREEN_WIDTH // 2, 10))
        screen.blit(wave_text, wave_rect)
        
        # Lives
        heart_width = 20
        heart_spacing = 5
        start_x = SCREEN_WIDTH - (heart_width + heart_spacing) * 3 - 10
        
        for i in range(self.player.lives):
            heart_rect = pygame.Rect(
                start_x + (heart_width + heart_spacing) * i,
                10,
                heart_width,
                heart_width
            )
            pygame.draw.rect(screen, RED, heart_rect)
        
        # Active power-ups
        self.powerup_manager.draw_active_effects(screen)

    def draw(self, screen) -> None:
        screen.fill(BLACK)
        
        # Draw all sprites
        self.all_sprites.draw(screen)
        self.powerups.draw(screen)
        
        # Draw effects
        self.effect_manager.draw(screen)
        
        # Draw HUD
        self.draw_hud(screen)
        
        if self.game_over:
            game_over_text = self.font.render(
                f'Game Over! Wave {self.wave} - Score {self.score}', 
                True, WHITE
            )
            restart_text = self.font.render('Press R to restart', True, WHITE)
            
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            
            screen.blit(game_over_text, text_rect)
            screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()