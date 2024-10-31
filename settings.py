import json
import os
import pygame
from constants import DEFAULT_CONTROLS

class Settings:
    def __init__(self):
        self.filename = 'game_settings.json'
        self.controls = DEFAULT_CONTROLS.copy()
        self.sound_volume = 0.5
        self.load_settings()

    def load_settings(self):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.controls = {k: int(v) for k, v in data.get('controls', DEFAULT_CONTROLS).items()}
                    self.sound_volume = float(data.get('sound_volume', 0.5))
        except:
            print("Error loading settings, using defaults")
            self.controls = DEFAULT_CONTROLS.copy()
            self.sound_volume = 0.5

    def save_settings(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump({
                    'controls': self.controls,
                    'sound_volume': self.sound_volume
                }, f)
        except:
            print("Error saving settings")

    def get_key_name(self, key_code):
        if key_code == pygame.BUTTON_LEFT:
            return "Left Mouse"
        if key_code == pygame.BUTTON_RIGHT:
            return "Right Mouse"
        return pygame.key.name(key_code).upper()