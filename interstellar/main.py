import pygame
from interstellar.game import Game, MainMenu

def main():
    pygame.display.init()
    pygame.mixer.init(44100, size=-16, channels=2, buffer=1024)
    pygame.mixer.set_num_channels(16)
    pygame.joystick.init()

    game = Game(MainMenu)
    game.setup()
    game.mainloop()

if __name__ == '__main__':
    main()
