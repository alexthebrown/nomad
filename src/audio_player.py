import pygame

class AudioPlayer:
    def __init__(self):
        pygame.mixer.init()

    def play(self, path):
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
