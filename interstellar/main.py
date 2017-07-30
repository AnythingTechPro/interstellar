import __builtin__
import pygame
from interstellar.game import Game, MainMenu

def main():
    pygame.display.init()
    pygame.mixer.init(44100, size=-16, channels=2, buffer=1024)
    pygame.mixer.set_num_channels(32)
    pygame.joystick.init()

    __builtin__.game = Game(MainMenu)
    game.setup()
    game.mainloop()

if __name__ == '__main__':
    main()
