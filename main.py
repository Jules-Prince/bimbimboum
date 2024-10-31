import pygame
import sys
from game import Game
from menu import Menu
from settings import Settings
from sounds import SoundManager
from constants import *

class GameManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Top-Down Shooter")
        self.clock = pygame.time.Clock()
        
        self.settings = Settings()
        self.sound_manager = SoundManager()
        self.sound_manager.set_volume(self.settings.sound_volume)
        
        self.state = 'title'  # 'title' or 'game'
        self.menu = Menu(self)
        self.game = None

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if self.state == 'title':
                self.menu.handle_input(event)
            elif self.state == 'game':
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = 'title'
                    self.game = None
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r and self.game.game_over:
                    self.game = Game(self.settings, self.sound_manager)
        return True

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            
            running = self.handle_events()
            
            # Update and draw
            if self.state == 'title':
                self.menu.draw(self.screen)
            elif self.state == 'game':
                if self.game is None:
                    self.game = Game(self.settings, self.sound_manager)
                self.game.update()
                self.game.draw(self.screen)

            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = GameManager()
    game.run()