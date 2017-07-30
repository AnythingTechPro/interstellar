import os
import pygame
import random
import thread
import time
import _tkinter
import Tkinter
from interstellar import audio, util, resource, sprite, task, mechanism

class GameDisplay(object):

    def __init__(self):
        self.root = Tkinter.Tk(sync=True)
        self._width = 0
        self._height = 0
        self._x = 0
        self._y = 0
        self._caption = ''
        self._resizable = True

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

    @property
    def resizable(self):
        return self._resizable

    @resizable.setter
    def resizable(self, resizable):
        if resizable is self._resizable:
            return

        self._resizable = resizable
        self.root.resizable(resizable, resizable)

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
            self.display.root.winfo_screenheight() / 2 - self.display.height / 2

        # TODO: disable window resizing until dynamic window change event,
        # is implemented so all objects will resize appropriately.
        self.display.resizable = False

        self.task_manager = task.TaskManager()
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

        self.current_scene.explicit_update()

    def destroy(self):
        self.current_scene.destroy()
        self.audio_manager.destroy()
        self.display.destroy()

    def execute(self):
        self.update()
        self.display.update()

    def mainloop(self):
        self.task_manager.run()

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

        self.bind('Configure', self.reconfigure)

        if self.can_pause:
            self.bind('KeyRelease-Return', self.toggle_pause)

        self.active = True

    def update(self):
        self.canvas.update()

    def explicit_update(self):
        pass

    def reconfigure(self, event):
        self.canvas['width'], self.canvas['height'] = self.master.width, self.master.height

    def bind(self, event, *args, **kwargs):
        if not self.canvas:
            return None

        return self.canvas.bind('<%s>' % event, *args, **kwargs)

    def unbind(self, event, *args, **kwargs):
        if not self.canvas:
            return None

        return self.canvas.unbind('<%s>' % event, *args, **kwargs)

    def send(self, event, *args, **kwargs):
        if not self.canvas:
            return None

        return self.canvas.event_generate('<%s>' % event, *args, **kwargs)

    def toggle_pause(self, event):
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

        self.active = False
        self.unbind('Configure')

        if self.can_pause:
            self.unbind('KeyRelease-Return')

        self.canvas.destroy()
        self.canvas = None

class MainMenu(Scene):

    def __init__(self, root, master):
        super(MainMenu, self).__init__(root, master)

        self.music_array = resource.ResourceAudioArray(self.root, [
            'assets/audio/music/main_menu_0.wav',
            'assets/audio/music/main_menu_1.wav',
            'assets/audio/music/main_menu_2.wav'])

        self.music = self.music_array.select(True)

        self.logo = resource.ResourceLabel(60, bind_events=False)
        self.logo.position = (self.master.width / 2, self.master.height / 4)
        self.logo.text = 'Interstellar'
        self.logo.color = 'yellow'
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

        self.testing_notice = resource.ResourceLabel(10, bind_events=False)
        self.testing_notice.position = (self.master.width / 8.4, (self.master.height / 4) * 3.9)
        self.testing_notice.text = 'NOTICE: Experimental build!'
        self.testing_notice.color = 'red'
        self.testing_notice.render(self.canvas)

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
        self.testing_notice.destroy()

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

        self.explosion = resource.ResourceFrameImage(self.canvas,
            ['assets/explosion/%d.png' % index for index in xrange(15)], self.explosion_callback)

        self.explosion_sound = pygame.mixer.Sound('assets/audio/sfx/explosion_0.wav')

        self.background = resource.ResourceScrolledImage(self.root, 'assets/stars.png')
        self.background.position = (self.master.width / 2, self.master.height / 2)
        self.background.render(self.canvas)

        self.paused_label = resource.ResourceLabel(40, bind_events=False)
        self.paused_label.position = (self.master.width / 2, self.master.height / 2)
        self.paused_label.text = 'Paused'

        self.time_label = resource.ResourceTimerLabel(10, bind_events=False)
        self.time_label.position = (self.master.width / 15, self.master.height / 15)
        self.time_label.render(self.canvas)

        self.distance_label = resource.ResourceTimerLabel(10, bind_events=False)
        self.distance_label.position = (self.master.width / 1.2, self.master.height / 15)
        self.distance_label.render(self.canvas)

        self.health_label = resource.ResourceTimerLabel(10, bind_events=False)
        self.health_label.position = (self.master.width / 15, self.master.height / 5)
        self.health_label.render(self.canvas)

        self.attachment_label = resource.ResourceTimerLabel(10, bind_events=False)
        self.attachment_label.position = (self.master.width / 10, self.master.height / 3)
        self.attachment_label.render(self.canvas)

        self.ship = sprite.Ship(self, sprite.ShipController)
        self.background.speed = self.ship.controller.speed / 2

        self.asteroid_choices = [
            sprite.Asteroid,
            sprite.ShieldMechanismAsteroid,
            sprite.InstantKillMechanismAsteroid,
        ]

        self.asteroid_choices = [[item, item.PROBABILITY] for item in
            self.asteroid_choices]

        self.asteroids = []
        self.maximum_asteroids = 20

    @property
    def distance(self):
        return 'Distance: %d Meters' % self.ship.controller.current_distance

    @property
    def health(self):
        return 'Health: %d' % self.ship.health

    @property
    def attachment(self):
        attachment = self.ship._attachment

        if not attachment:
            return 'Attachment: None'

        return 'Attachment: %s' % attachment.NAME

    def setup(self):
        super(GameLevel, self).setup()

        self.music.play()
        self.ship.setup()
        self.time_label.setup()

    def update(self):
        super(GameLevel, self).update()

        self.time_label.update()
        self.explosion.update()

        self.distance_label.text = self.distance
        self.health_label.text = self.health
        self.attachment_label.text = self.attachment

        for asteroid in self.asteroids:
            asteroid.update()

        if len(self.asteroids) < self.maximum_asteroids:
            self.add_asteroid()

        self.background.update()
        self.ship.update()

    def explicit_update(self):
        self.ship.explicit_update()

    def add_asteroid(self):
        asteroid = util.weighted_choice(self.asteroid_choices)(self, sprite.\
            AsteroidController)

        self.asteroids.append(asteroid)

    def explosion_callback(self):
        self.explosion.can_play = False

    def remove_asteroid(self, asteroid, use_effects=False):
        asteroid.destroy()
        self.asteroids.remove(asteroid)

    def explode(self, x, y):
        self.explosion.can_play = True
        self.explosion.position = (x, y)
        self.explosion_sound.play()

    def pause(self):
        self.paused_label.render(self.canvas)

    def unpause(self):
        self.paused_label.derender()

    def end(self):
        self.root.current_scene = DeathMenu

    def destroy(self):
        self.music_array.deselect()
        self.music_array.destroy()
        self.music.stop()

        self.distance_label.destroy()
        self.health_label.destroy()
        self.attachment_label.destroy()
        self.background.destroy()
        self.ship.destroy()

        for asteroid in self.asteroids:
            asteroid.destroy()

        self.asteroids = []
        self.explosion.destroy()
        self.paused_label.destroy()
        self.time_label.destroy()

        super(GameLevel, self).destroy()

class DeathMenu(Scene):
    """
    A scene that will take place after the player dies
    """

    def __init__(self, root, master):
        super(DeathMenu, self).__init__(root, master)

        self.music = self.root.audio_manager.load('assets/audio/music/ending.wav', True)

        self.death_label = resource.ResourceLabel(40, bind_events=False)
        self.death_label.position = (self.master.width / 2, self.master.height / 4)
        self.death_label.text = 'You Died!'
        self.death_label.render(self.canvas)

        self.replay_button = resource.ResourceLabel(40)
        self.replay_button.position = (self.master.width / 2, self.master.height / 2)
        self.replay_button.text = 'Retry'
        self.replay_button.render(self.canvas)

        self.main_menu = resource.ResourceLabel(40)
        self.main_menu.position = (self.master.width / 2, self.master.height / 1.5)
        self.main_menu.text = 'Return To Menu'
        self.main_menu.render(self.canvas)

    def setup(self):
        super(DeathMenu, self).setup()

        self.music.play()

        self.replay_button.clicked_handler = self.__goto_level
        self.main_menu.clicked_handler = self.__goto_main_menu

    def __goto_level(self):
        self.root.current_scene = GameLevel

    def __goto_main_menu(self):
        self.root.current_scene = MainMenu

    def destroy(self):
        self.music.stop()
        self.root.audio_manager.unload(self.music)

        self.death_label.destroy()

        super(DeathMenu, self).destroy()
