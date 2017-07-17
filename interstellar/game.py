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
        self._x = 0
        self._y = 0
        self._caption = ''

    @property
    def size(self):
        return (self._width, self._height)

    @size.setter
    def size(self, size):
        self.width, self.height = size

    @property
    def width(self):
        #if self._width != self.root.winfo_width():
        #    self._width = self.root.winfo_width()

        return self._width

    @width.setter
    def width(self, width):
        if width is self._width:
            return

        self._width = width
        self.root.geometry('%dx%d' % (self._width, self._height))

    @property
    def height(self):
        #if self._height != self.root.winfo_height():
        #    self._height = self.root.winfo_height()

        return self._height

    @height.setter
    def height(self, height):
        if height is self._height:
            return

        self._height = height
        self.root.geometry('%dx%d' % (self._width, self._height))

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        if x is self._x:
            return

        self._x = x
        self.root.geometry('%dx%d+%d+%d' % (self._width, self._height, self._x, self._y))

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        if y is self._y:
            return

        self._y = y
        self.root.geometry('%dx%d+%d+%d' % (self._width, self._height, self._x, self._y))

    @property
    def position(self):
        return (self._x, self._y)

    @position.setter
    def position(self, position):
        self.x, self.y = position

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
        self.display.position = self.display.root.winfo_screenwidth() / 2 - self.display.width / 2, \
            self.display.root.winfo_screenheight() / 2 - self.display.height

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
        for event in pygame.event.get():
            pass

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
        self.canvas.pack(fill=Tkinter.BOTH, expand=True, anchor=Tkinter.CENTER)

    def setup(self):
        if self.active:
            raise SceneError('Scene has already been setup!')

        self.bind('<Configure>', self.reconfigure)

        if self.can_pause:
            self.bind('<KeyRelease-Return>', self.__pause)

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
            self.pause()
        else:
            self.active = True
            self.unpause()

    def pause(self):
        pass

    def unpause(self):
        pass

    def destroy(self):
        if not self.active:
            raise SceneError('Scene has not been setup!')

        self.unbind('<Configure>')

        if self.can_pause:
            self.unbind('<KeyRelease-Return>')

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

        self.music = self.music_array.select(True)

        self.logo = resource.ResourceImage(self.root, 'assets/menu/logo.png')
        self.logo.position = (self.master.width / 2, self.master.height / 4)
        self.logo.render(self.canvas)

        self.play_button = resource.ResourceLabel(40)
        self.play_button.position = (self.master.width / 2, self.master.height / 2)
        self.play_button.text = 'Play'
        self.play_button.render(self.canvas)

        self.options_button = resource.ResourceLabel(40)
        self.options_button.position = (self.master.width / 2, (self.master.height / 3) * 2)
        self.options_button.text = 'Options'
        self.options_button.render(self.canvas)

        self.quit_button = resource.ResourceLabel(40)
        self.quit_button.position = (self.master.width / 2, (self.master.height / 3) * 2.5)
        self.quit_button.text = 'Quit'
        self.quit_button.render(self.canvas)

    def setup(self):
        super(MainMenu, self).setup()

        self.music.play()

        self.play_button.clicked_handler = self.__play
        self.quit_button.clicked_handler = self.__quit
        self.options_button.clicked_handler = self.__options

    def __play(self):
        self.root.current_scene = GameLevel

    def __quit(self):
        self.root.shutdown = True

    def __options(self):
        self.root.current_scene = OptionsMenu

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

        self.music = self.root.audio_manager.load('assets/audio/music/options_menu.wav', True)

        self.options_label = resource.ResourceLabel(40, bind_events=False)
        self.options_label.position = (self.master.width / 2, self.master.height / 10)
        self.options_label.text = 'Game Options:'
        self.options_label.render(self.canvas)

        self.music_label = resource.ResourceLabel(40, bind_events=False)
        self.music_label.position = (self.master.width / 2.5, self.master.height / 3)
        self.music_label.text = 'Music:'
        self.music_label.render(self.canvas)

        self.music_button = resource.ResourceLabel(40)
        self.music_button.position = (self.master.width / 1.5, self.master.height / 3)
        self.music_button.text = self.music_active
        self.music_button.render(self.canvas)

        self.back_button = resource.ResourceLabel(40)
        self.back_button.position = (self.master.width / 10.7, (self.master.height / 4) * 3.7)
        self.back_button.text = 'Back'
        self.back_button.render(self.canvas)

    @property
    def music_active(self):
        return 'ON' if self.root.audio_manager.enabled else 'OFF'

    def setup(self):
        super(OptionsMenu, self).setup()

        self.music.play()
        self.back_button.clicked_handler = self.__back
        self.music_button.clicked_handler = self.__toggle_audio

    def __back(self):
        self.root.current_scene = MainMenu

    def __toggle_audio(self):
        self.root.audio_manager.toggle()
        self.music_button.text = self.music_active

    def destroy(self):
        self.root.audio_manager.unload(self.music)
        self.options_label.destroy()
        self.music_label.destroy()
        self.music_button.destroy()
        self.back_button.destroy()

        super(OptionsMenu, self).destroy()

class GameLevel(Scene):

    def __init__(self, root, master):
        super(GameLevel, self).__init__(root, master, can_pause=True)

        self.music_array = resource.ResourceAudioArray(self.root, [
            'assets/audio/music/level_0.wav',
            'assets/audio/music/level_1.wav',
            'assets/audio/music/level_2.wav'])

        self.music = self.music_array.select(True)
        self.ending_music = self.root.audio_manager.load('assets/audio/music/ending.wav', True)

        self.background = resource.ResourceScrolledImage(self.root, 'assets/stars.png')
        self.background.position = (self.master.width / 2, self.master.height / 2)
        self.background.speed = 1
        self.background.render(self.canvas)

        self.paused_label = resource.ResourceLabel(40, bind_events=False)
        self.paused_label.position = (self.master.width / 2, self.master.height / 2)
        self.paused_label.text = 'Paused'

        self.ship = sprite.Ship(self, sprite.ShipController)

        self.asteroids = []
        self.maximum_asteroids = 20

    def setup(self):
        super(GameLevel, self).setup()

        self.music.play()
        self.ship.setup()

    def update(self):
        self.ship.update()

        for asteroid in self.asteroids:
            asteroid.update()

        if len(self.asteroids) < self.maximum_asteroids:
            self.add_asteroid()

        self.background.update()
        super(GameLevel, self).update()

    def add_asteroid(self):
        asteroid = sprite.Asteroid(self, sprite.AsteroidController)
        self.asteroids.append(asteroid)

    def remove_asteroid(self, asteroid):
        asteroid.destroy()
        self.asteroids.remove(asteroid)

    def pause(self):
        self.paused_label.render(self.canvas)

    def unpause(self):
        self.paused_label.derender()

    def destroy(self):
        self.music_array.deselect()
        self.music_array.destroy()

        self.ending_music.stop()
        self.root.audio_manager.unload(self.ending_music)

        self.background.destroy()
        self.ship.destroy()
        self.paused_label.destroy()

        super(GameLevel, self).destroy()
