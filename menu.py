import sys
import pygame
from constants import *

class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_selected = False
        self.is_waiting_for_key = False

    def draw(self, screen, font):
        color = LIGHT_BLUE if self.is_selected else DARK_GRAY
        if self.is_waiting_for_key:
            color = YELLOW
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)

        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class Slider:
    def __init__(self, x, y, width, height, value=0.5, text="Volume"):
        self.rect = pygame.Rect(x, y, width, height)
        self.value = value
        self.text = text
        self.is_selected = False
        self.is_dragging = False

    def draw(self, screen, font):
        # Draw slider background
        pygame.draw.rect(screen, DARK_GRAY, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)

        # Draw slider position
        pos_x = self.rect.x + (self.rect.width * self.value)
        slider_handle = pygame.Rect(pos_x - 5, self.rect.y, 10, self.rect.height)
        pygame.draw.rect(screen, LIGHT_BLUE if self.is_selected else WHITE, slider_handle)

        # Draw text
        text_surface = font.render(f"{self.text}: {int(self.value * 100)}%", True, WHITE)
        text_rect = text_surface.get_rect(midleft=(self.rect.x, self.rect.y - 10))
        screen.blit(text_surface, text_rect)

    def handle_mouse(self, pos):
        if self.is_dragging:
            x = max(self.rect.left, min(pos[0], self.rect.right))
            self.value = (x - self.rect.left) / self.rect.width
            self.value = max(0, min(1, self.value))
            return True
        return False

class Menu:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, MENU_FONT_SIZE)
        self.state = 'title'  # 'title', 'settings', 'controls'
        self.selected_button = 0
        self.waiting_for_key = None
        self.create_buttons()

    def create_buttons(self):
        center_x = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2 - 100

        self.title_buttons = [
            Button(center_x - BUTTON_WIDTH//2, start_y, 
                  BUTTON_WIDTH, BUTTON_HEIGHT, "Start Game"),
            Button(center_x - BUTTON_WIDTH//2, start_y + 70, 
                  BUTTON_WIDTH, BUTTON_HEIGHT, "Settings"),
            Button(center_x - BUTTON_WIDTH//2, start_y + 140, 
                  BUTTON_WIDTH, BUTTON_HEIGHT, "Quit")
        ]

        self.settings_buttons = [
            Button(center_x - BUTTON_WIDTH//2, start_y,
                  BUTTON_WIDTH, BUTTON_HEIGHT, "Controls"),
            Slider(center_x - SLIDER_WIDTH//2, start_y + 70,
                  SLIDER_WIDTH, SLIDER_HEIGHT, self.game.settings.sound_volume),
            Button(center_x - BUTTON_WIDTH//2, start_y + 140,
                  BUTTON_WIDTH, BUTTON_HEIGHT, "Back")
        ]

        self.controls_buttons = []
        y = start_y
        for action in self.game.settings.controls:
            key_name = self.game.settings.get_key_name(self.game.settings.controls[action])
            self.controls_buttons.append(
                Button(center_x - BUTTON_WIDTH//2, y,
                      BUTTON_WIDTH, BUTTON_HEIGHT, f"{action}: {key_name}")
            )
            y += 70

        self.controls_buttons.append(
            Button(center_x - BUTTON_WIDTH//2, y,
                  BUTTON_WIDTH, BUTTON_HEIGHT, "Back")
        )

    def get_current_buttons(self):
        if self.state == 'title':
            return self.title_buttons
        elif self.state == 'settings':
            return self.settings_buttons
        elif self.state == 'controls':
            return self.controls_buttons

    def handle_input(self, event):
        buttons = self.get_current_buttons()

        if self.waiting_for_key is not None:
            if event.type == pygame.KEYDOWN:
                action = list(self.game.settings.controls.keys())[self.waiting_for_key]
                self.game.settings.controls[action] = event.key
                self.game.settings.save_settings()
                self.waiting_for_key = None
                self.create_buttons()  # Refresh button text
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_button = (self.selected_button - 1) % len(buttons)
            elif event.key == pygame.K_DOWN:
                self.selected_button = (self.selected_button + 1) % len(buttons)
            elif event.key == pygame.K_RETURN:
                self.handle_selection()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for i, button in enumerate(buttons):
                if button.rect.collidepoint(mouse_pos):
                    self.selected_button = i
                    self.handle_selection()
                    if isinstance(button, Slider):
                        button.is_dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            for button in buttons:
                if isinstance(button, Slider):
                    button.is_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            for button in buttons:
                if isinstance(button, Slider) and button.is_dragging:
                    button.handle_mouse(mouse_pos)
                    self.game.settings.sound_volume = button.value
                    self.game.settings.save_settings()
                    self.game.sound_manager.set_volume(button.value)

    def handle_selection(self):
        buttons = self.get_current_buttons()
        selected = buttons[self.selected_button]

        if self.state == 'title':
            if selected.text == "Start Game":
                self.game.state = 'game'
            elif selected.text == "Settings":
                self.state = 'settings'
            elif selected.text == "Quit":
                pygame.quit()
                sys.exit()

        elif self.state == 'settings':
            if selected.text == "Controls":
                self.state = 'controls'
                self.selected_button = 0
            elif selected.text == "Back":
                self.state = 'title'
                self.selected_button = 0

        elif self.state == 'controls':
            if selected.text == "Back":
                self.state = 'settings'
                self.selected_button = 0
            else:
                self.waiting_for_key = self.selected_button

    def draw(self, screen):
        screen.fill(BLACK)
        
        # Draw title
        title_text = "TOP-DOWN SHOOTER"
        if self.state == 'settings':
            title_text = "SETTINGS"
        elif self.state == 'controls':
            title_text = "CONTROLS"
        
        title_surface = self.font.render(title_text, True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title_surface, title_rect)

        # Draw buttons
        buttons = self.get_current_buttons()
        for i, button in enumerate(buttons):
            button.is_selected = (i == self.selected_button)
            if self.waiting_for_key is not None and i == self.waiting_for_key:
                button.is_waiting_for_key = True
                button.text = "Press any key..."
            button.draw(screen, self.font)

        if self.waiting_for_key is not None:
            text = self.font.render("Press any key to bind...", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 50))
            screen.blit(text, text_rect)

        pygame.display.flip()