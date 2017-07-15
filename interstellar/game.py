import os
import pygame
import random
import thread
import time
import _tkinter
import Tkinter
from interstellar import audio, util, resource, sprite

class GameDisplay(object):

    def __init__(self):
        self.root = Tkinter.Tk(sync=True)
        self._width = 0
        self._height = 0
        self._caption = ''

    @property
    def size(self):
        return (self._width, self._height)

    @size.setter
    def size(self, size):
        self._width, self._height = size
        self.root.geometry('%dx%d' % (self._width, self._height))

    @property
    def width(self):
        #if self._width != self.root.winfo_width():
        #    self._width = self.root.winfo_width()

        return self._width

    @property
    def height(self):
        #if self._height != self.root.winfo_height():
        #    self._height = self.root.winfo_height()

        return self._height

    @property
    def caption(self):
        return self._caption

    @caption.setter
    def caption(self, caption):
        self._caption = caption
        self.root.title(caption)

    def setup(self):
        self.root.configure(background='black')

    def update(self):
        self.root.update()

    def destroy(self):
        self.root.destroy()

class Game(object):

    def __init__(self, scene, width=1280, height=720, caption='Interstellar'):
        self.display = GameDisplay()
        self.display.size = (width, height)
        self.display.caption = caption
        self.audio_manager = audio.AudioManager()
        self.shutdown = False
        self._last_scene = None
        self._current_scene = scene(self, self.display)

    @property
    def current_scene(self):
        return self._current_scene

    @current_scene.setter
    def current_scene(self, scene):
        if self._current_scene:
            self._current_scene.destroy()
            self._last_scene = self._current_scene

        self._current_scene = scene(self, self.display)
        self._current_scene.setup()

    def setup(self):
        self.display.setup()
        self.current_scene.setup()

    def update(self):
        if self.current_scene.active:
            self.current_scene.update()

    def destroy(self):
        self.current_scene.destroy()
        self.audio_manager.destroy()
        self.display.destroy()

    def execute(self):
        self.update()
        self.display.update()

    def mainloop(self):
        while not self.shutdown:
            try:
                self.execute()
            except (_tkinter.TclError, KeyboardInterrupt, SystemExit):
                break

            #time.sleep(0.01)

        self.destroy()

class SceneError(RuntimeError):
    """
    A scene specific runtime error
    """

class Scene(object):
    """
    An object that manages and creates objects in a game
    """

    def __init__(self, root, master, can_pause=False):
        self.root = root
        self.master = master
        self.can_pause = can_pause
        self.active = False

        self.canvas = Tkinter.Canvas(self.master.root, width=self.master.width, height=self.master.height, background='black',
            highlightthickness=0)

        self.canvas.focus_set()

    def setup(self):
        if self.active:
            raise SceneError('Scene has already been setup!')

        self.bind('<Configure>', self.reconfigure)

        if self.can_pause:
            self.bind('<Return>', self.__pause)

        self.canvas.pack(fill=Tkinter.BOTH, expand=True, anchor=Tkinter.CENTER)
        self.active = True

    def update(self):
        self.canvas.update()

    def reconfigure(self, event):
        self.canvas['width'], self.canvas['height'] = self.master.width, self.master.height

    def bind(self, *args, **kwargs):
        if not self.canvas:
            return None

        return self.canvas.bind(*args, **kwargs)

    def unbind(self, *args, **kwargs):
        if not self.canvas:
            return None

        return self.canvas.unbind(*args, **kwargs)

    def __pause(self, event):
        if self.active:
            self.active = False
        else:
            self.active = True

    def destroy(self):
        if not self.active:
            raise SceneError('Scene has not been setup!')

        self.unbind('<Configure>')

        if self.can_pause:
            self.unbind('<Return>')

        self.canvas.destroy()
        self.canvas = None

        self.active = False

class MainMenu(Scene):

    def __init__(self, root, master):
        super(MainMenu, self).__init__(root, master)

        self.music_array = resource.ResourceAudioArray(self.root, [
            'assets/audio/music/main_menu_0.wav',
            'assets/audio/music/main_menu_1.wav',
            'assets/audio/music/main_menu_2.wav'])

        self.music = self.music_array.select()

        self.logo = resource.ResourceImage(self.root, 'assets/menu/logo.png')
        self.logo.position = (self.master.width / 2, self.master.height / 4)
        self.logo.render(self.canvas)

        self.play_button = resource.ResourceLabel(40, 'Pixeled')
        self.play_button.position = (self.master.width / 2, self.master.height / 2)
        self.play_button.text = 'Play'
        self.play_button.render(self.canvas)

        self.options_button = resource.ResourceLabel(40, 'Pixeled')
        self.options_button.position = (self.master.width / 2, (self.master.height / 3) * 2)
        self.options_button.text = 'Options'
        self.options_button.render(self.canvas)

        self.quit_button = resource.ResourceLabel(40, 'Pixeled')
        self.quit_button.position = (self.master.width / 2, (self.master.height / 3) * 2.5)
        self.quit_button.text = 'Quit'
        self.quit_button.render(self.canvas)

    def setup(self):
        super(MainMenu, self).setup()

        self.music.play(True)

        self.play_button.clicked_handler = self.__play
        self.quit_button.clicked_handler = self.__quit
        self.options_button.clicked_handler = self.__options

    def __play(self):
        self.root.current_scene = GameLevel

    def __quit(self):
        self.root.shutdown = True

    def __options(self):
        self.root.current_scene = OptionsMenu

    def update(self):
        self.play_button.update()
        self.quit_button.update()
        self.options_button.update()

        super(MainMenu, self).update()

    def destroy(self):
        self.music_array.deselect()
        self.music_array.destroy()

        self.play_button.destroy()
        self.quit_button.destroy()
        self.options_button.destroy()

        super(MainMenu, self).destroy()

class OptionsMenu(Scene):

    def __init__(self, root, master):
        super(OptionsMenu, self).__init__(root, master)

        self.music = self.root.audio_manager.load('assets/audio/music/options_menu.wav')

        self.options_label = resource.ResourceLabel(40, 'Pixeled', False)
        self.options_label.position = (self.master.width / 2, self.master.height / 10)
        self.options_label.text = 'Game Options:'
        self.options_label.render(self.canvas)

        self.back_button = resource.ResourceLabel(40, 'Pixeled')
        self.back_button.position = (self.master.width / 10.7, (self.master.height / 4) * 3.7)
        self.back_button.text = 'Back'
        self.back_button.render(self.canvas)

    def setup(self):
        super(OptionsMenu, self).setup()

        self.music.play(True)

        self.back_button.clicked_handler = self.__back

    def __back(self):
        self.root.current_scene = MainMenu

    def update(self):
        self.options_label.update()
        self.back_button.update()

        super(OptionsMenu, self).update()

    def destroy(self):
        self.root.audio_manager.unload(self.music)
        self.options_label.destroy()
        self.back_button.destroy()

        super(OptionsMenu, self).destroy()

class GameLevel(Scene):

    def __init__(self, root, master):
        super(GameLevel, self).__init__(root, master, can_pause=True)

        self.music_array = resource.ResourceAudioArray(self.root, [
            'assets/audio/music/level_0.wav',
            'assets/audio/music/level_1.wav',
            'assets/audio/music/level_2.wav'])

        self.music = self.music_array.select()
        self.ending_music = self.root.audio_manager.load('assets/audio/music/ending.wav')

        self.background = resource.ResourceImage(self.root, 'assets/stars.png')
        self.background.position = (self.master.width / 2, self.master.height / 2)
        self.background.render(self.canvas)

        self.ship = sprite.Ship(self, sprite.ShipController)

        self.asteroids = []
        self.maximum_asteroids = 20

    def setup(self):
        super(GameLevel, self).setup()

        self.music.play(True)
        self.ship.setup()

    def update(self):
        self.ship.update()

        for asteroid in self.asteroids:
            asteroid.update()

        if len(self.asteroids) < self.maximum_asteroids:
            self.add_asteroid()

        super(GameLevel, self).update()

    def add_asteroid(self):
        asteroid = sprite.Asteroid(self, sprite.AsteroidController)
        self.asteroids.append(asteroid)

    def remove_asteroid(self, asteroid):
        asteroid.destroy()
        self.asteroids.remove(asteroid)

    def destroy(self):
        self.music_array.deselect()
        self.music_array.destroy()

        self.ending_music.stop()
        self.root.audio_manager.unload(self.ending_music)

        self.background.destroy()
        self.ship.destroy()

        super(GameLevel, self).destroy()
