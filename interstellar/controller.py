import pygame

class Controller(object):
    """
    A class that handles controller input
    """

    def __init__(self, root):
        self.root = root

    def update(self):
        for event in pygame.event.get():
            print event

class GameController(Controller):
    """
    """
