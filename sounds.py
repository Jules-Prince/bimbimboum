# sounds.py
import pygame
import os

class SoundManager:
    def __init__(self):
        # Initialize the mixer
        pygame.mixer.init()
        
        # Load sound effects
        self.sounds = {
            'shoot': self.load_sound('laser.mp3'),
            'kill': self.load_sound('ough.mp3'),
            'shield': self.load_sound('shield.mp3')
        }
        
        # Set volume for all sounds
        self.set_volume(0.3)
    
    def load_sound(self, filename):
        try:
            sound_path = os.path.join('assets', 'sounds', filename)
            return pygame.mixer.Sound(sound_path)
        except:
            print(f"Couldn't load sound: {filename}")
            # Return a dummy sound object that does nothing
            return type('DummySound', (), {'play': lambda: None, 'set_volume': lambda x: None})()
    
    def play(self, sound_name):
        self.sounds[sound_name].play()
    
    def set_volume(self, volume):
        for sound in self.sounds.values():
            sound.set_volume(volume)