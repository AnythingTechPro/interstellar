import __builtin__
import pygame
from interstellar import game, scene

def main():
    pygame.display.init()
    pygame.mixer.init(44100, size=-16, channels=2, buffer=1024)
    pygame.mixer.set_num_channels(16)
    pygame.joystick.init()

    __builtin__.game = game.Game(scene.MainMenu)
    game.setup()
    game.mainloop()

if __name__ == '__main__':
    main()