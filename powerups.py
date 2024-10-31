import pygame
import random
from constants import *

class PowerUp(pygame.sprite.Sprite):
    TYPES = {
        'speed': {'color': (0, 255, 255), 'duration': 5000, 'symbol': 'S'},
        'shield': {'color': (255, 215, 0), 'duration': 8000, 'symbol': 'I'},
        'spread_shot': {'color': (255, 165, 0), 'duration': 10000, 'symbol': 'M'},
        'health': {'color': (124, 252, 0), 'duration': 0, 'symbol': 'H'},
    }
    
    def __init__(self, pos, power_type):
        super().__init__()
        self.type = power_type
        self.props = self.TYPES[power_type]
        
        # Create power-up appearance
        self.image = pygame.Surface((30, 30))
        self.image.fill(self.props['color'])
        self.rect = self.image.get_rect(center=pos)
        
        # Add symbol
        font = pygame.font.Font(None, 25)
        symbol = font.render(self.props['symbol'], True, BLACK)
        symbol_rect = symbol.get_rect(center=(15, 15))
        self.image.blit(symbol, symbol_rect)
        
        self.start_time = None

    @staticmethod
    def random_position():
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = random.randint(50, SCREEN_HEIGHT - 50)
        return (x, y)

class PowerUpManager:
    def __init__(self, game):
        self.game = game
        self.powerup_group = pygame.sprite.Group()
        self.active_effects = {}
        self.spawn_timer = 0
        self.spawn_interval = 10000  # 10 seconds

    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Spawn new power-ups
        if current_time - self.spawn_timer > self.spawn_interval:
            self.spawn_timer = current_time
            if len(self.powerup_group) < 3:  # Maximum 3 power-ups at once
                power_type = random.choice(list(PowerUp.TYPES.keys()))
                pos = PowerUp.random_position()
                self.powerup_group.add(PowerUp(pos, power_type))

        # Update active effects
        for effect_type in list(self.active_effects.keys()):
            effect_data = self.active_effects[effect_type]
            if current_time - effect_data['start_time'] > effect_data['duration']:
                self.remove_effect(effect_type)

    def collect_powerup(self, powerup):
        if powerup.type == 'health':
            if self.game.player.lives < 3:
                self.game.player.lives += 1
        else:
            self.active_effects[powerup.type] = {
                'start_time': pygame.time.get_ticks(),
                'duration': powerup.props['duration']
            }
            self.apply_effect(powerup.type)

    def apply_effect(self, effect_type):
        if effect_type == 'speed':
            self.game.player.speed = PLAYER_SPEED * 1.5
        elif effect_type == 'shield':
            self.game.player.has_shield = True
        elif effect_type == 'spread_shot':
            self.game.player.spread_shot = True

    def remove_effect(self, effect_type):
        if effect_type == 'speed':
            self.game.player.speed = PLAYER_SPEED
        elif effect_type == 'shield':
            self.game.player.has_shield = False
        elif effect_type == 'spread_shot':
            self.game.player.spread_shot = False
        del self.active_effects[effect_type]

    def draw_active_effects(self, screen):
        x = 10
        y = 40
        for effect_type in self.active_effects:
            effect_data = self.active_effects[effect_type]
            remaining = effect_data['duration'] - (pygame.time.get_ticks() - effect_data['start_time'])
            width = 100 * (remaining / PowerUp.TYPES[effect_type]['duration'])
            
            pygame.draw.rect(screen, PowerUp.TYPES[effect_type]['color'], (x, y, width, 10))
            y += 15