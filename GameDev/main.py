import pygame
from datetime import datetime, timedelta
from random import randint, random
from text_element import TextElement

pygame.init()

class Game:
    def __init__(self):
        self.tile_size = 16
        self.screen_size = (1024, 768)
        self.screen = pygame.display.set_mode([self.screen_size[0],self.screen_size[1]])
        self.running = True
        self.gametime = 0
        self.last_tick = datetime.now()
        self.fps = 0
        self.fonts = [
            pygame.font.SysFont(None, 16),
            pygame.font.SysFont(None, 20),
            pygame.font.SysFont(None, 24),
            pygame.font.SysFont(None, 32)
        ]
        self.text_elements = {
            "notification": TextElement(self.screen, 20, 20, self.fonts[3], "", shadow=True, show=False),
            "fps": TextElement(self.screen, 20, 4, self.fonts[2], "0 fps", shadow=True, show=True)
        }
        self.surfaces = {
            "grass": pygame.Surface((self.tile_size, self.tile_size)),
            "water": pygame.Surface((self.tile_size, self.tile_size)),
            "mountain": pygame.Surface((self.tile_size, self.tile_size)),
            "snow": pygame.Surface((self.tile_size, self.tile_size)),
        }
        self.surfaces["grass"].fill((0,255,0))
        self.surfaces["water"].fill((0,0,255))
        self.surfaces["mountain"].fill((128,128,128))
        self.surfaces["snow"].fill((255,255,255))

    def input(self):
        pressed_keys = pygame.key.get_pressed()

    def update(self):
        if self.last_tick < datetime.now() + timedelta(seconds=1):
            self.gametime = self.gametime + 1
            
    def draw(self):
        self.screen.fill((0, 0, 0))



        for key in self.text_elements:
            self.text_elements[key].draw()

if __name__ == "__main__":
    game = Game()
    pygame.mouse.set_visible(True)
    last_second = datetime.now()
    frame = 0
    while game.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
        game.input()
        game.update()
        game.draw()
        pygame.display.flip()
        if last_second < datetime.now() - timedelta(seconds=1):
            last_second = datetime.now()
            fps = frame
            frame = 0
            game.fps = fps
            game.text_elements["fps"].update_text(str(fps)+" fps")
        else:
            frame = frame + 1

    pygame.quit()