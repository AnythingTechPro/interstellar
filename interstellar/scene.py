import os
import pygame
import random
import thread
import time
import Tkinter
from PIL import ImageGrab
from interstellar import audio, util, resource, sprite, mechanism

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
        self.bind('F1', self.take_screenshot)

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

    def take_screenshot(self, event):
        x1, y1 = self.master.x + 3, self.master.y + 26
        x2, y2 = x1 + self.master.width, y1 + self.master.height
        return ImageGrab.grab().crop((x1, y1, x2, y2)).save('screenshot-%d.jpg' % \
            int(time.time()))

    def destroy(self):
        if not self.active:
            raise SceneError('Scene has not been setup!')

        self.active = False
        self.unbind('Configure')
        self.unbind('F1')

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
        self.testing_notice.position = (self.master.width / 11.8, (self.master.height / 4) * 3.9)
        self.testing_notice.text = 'Experimental build!'
        self.testing_notice.color = 'blue'
        self.testing_notice.render(self.canvas)

    def setup(self):
        super(MainMenu, self).setup()

        self.music.play()

        self.play_button.clicked_handler = self.__play
        self.quit_button.clicked_handler = self.__quit
        self.options_button.clicked_handler = self.__options

    def __play(self):
        self.root.switch_scene(GameLevel)

    def __quit(self):
        self.root.shutdown = True

    def __options(self):
        self.root.switch_scene(OptionsMenu)

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
        self.options_label.color = 'yellow'
        self.options_label.render(self.canvas)

        self.audio_label = resource.ResourceLabel(40, bind_events=False)
        self.audio_label.position = (self.master.width / 2.5, self.master.height / 3)
        self.audio_label.text = 'Audio:'
        self.audio_label.render(self.canvas)

        self.audio_button = resource.ResourceLabel(40)
        self.audio_button.position = (self.master.width / 1.5, self.master.height / 3)
        self.audio_button.text = self.music_active
        self.audio_button.render(self.canvas)

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
        self.audio_button.clicked_handler = self.__toggle_audio

    def __back(self):
        self.root.switch_scene(MainMenu)

    def __toggle_audio(self):
        self.root.audio_manager.toggle()
        self.audio_button.text = self.music_active

    def destroy(self):
        self.root.audio_manager.unload(self.music)
        self.options_label.destroy()
        self.audio_label.destroy()
        self.audio_button.destroy()
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

        self.explosion_sound = audio.AudioSound('assets/audio/sfx/explosion_0.wav')

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
        self.health_label.position = (self.time_label.x, self.master.height / 7)
        self.health_label.render(self.canvas)

        self.ship = sprite.Ship(self, sprite.ShipController)
        self.background.speed = self.ship.controller.speed / 2

        self.asteroid_choices = [[item, item.PROBABILITY] for item in [
            sprite.Asteroid,
            sprite.ShieldMechanismAsteroid,
            sprite.InstantKillMechanismAsteroid,
            sprite.FullHealthMechanismAsteroid,
            sprite.DoubleHealthMechanismAsteroid,
        ]]

        self.asteroids = []
        self.maximum_asteroids = 20

    @property
    def distance(self):
        return 'Distance: %d IAU' % self.ship.controller.current_distance

    @property
    def health(self):
        return 'Health: %d' % self.ship.health

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
        if self.explosion_sound.playing:
            self.explosion_sound.stop()

        self.explosion.can_play = True
        self.explosion.position = (x, y)
        self.explosion_sound.play()

    def pause(self):
        self.paused_label.render(self.canvas)

    def unpause(self):
        self.paused_label.derender()

    def end(self):
        high_score = self.root.score_board.is_high_score(self.ship.controller.current_distance)
        self.root.score_board.score = self.ship.controller.current_distance

        self.root.switch_scene(DeathMenu, high_score)

    def destroy(self):
        self.music_array.deselect()
        self.music_array.destroy()
        self.music.stop()
        self.explosion_sound.destroy()

        self.distance_label.destroy()
        self.health_label.destroy()
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

    def __init__(self, root, master, is_high_score):
        super(DeathMenu, self).__init__(root, master)

        self.is_high_score = is_high_score

        self.music = self.root.audio_manager.load('assets/audio/music/ending.wav', True)

        self.death_label = resource.ResourceLabel(40, bind_events=False)
        self.death_label.position = (self.master.width / 2, self.master.height / 4)
        self.death_label.text = 'You Died!'
        self.death_label.render(self.canvas)

        self.score_label = resource.ResourceLabel(30, bind_events=False)
        self.score_label.position = (self.master.width / 5, self.master.height / 2)
        self.score_label.text = '%s\n%d IAU' % ('High Score!' if is_high_score else 'Score:', self.root.score_board.score)
        self.score_label.render(self.canvas)

        self.replay_button = resource.ResourceLabel(40)
        self.replay_button.position = (self.master.width / 1.2, self.master.height / 2)
        self.replay_button.text = 'Retry'
        self.replay_button.render(self.canvas)

        self.main_menu_button = resource.ResourceLabel(40)
        self.main_menu_button.position = (self.master.width / 1.5, self.master.height / 1.5)
        self.main_menu_button.text = 'Return To Menu'
        self.main_menu_button.render(self.canvas)

    def setup(self):
        super(DeathMenu, self).setup()

        self.music.play()

        self.replay_button.clicked_handler = self.__replay
        self.main_menu_button.clicked_handler = self.__main_menu

    def __replay(self):
        self.root.switch_scene(GameLevel)

    def __main_menu(self):
        self.root.switch_scene(MainMenu)

    def destroy(self):
        self.music.stop()
        self.root.audio_manager.unload(self.music)

        self.death_label.destroy()
        self.score_label.destroy()
        self.replay_button.destroy()
        self.main_menu_button.destroy()

        super(DeathMenu, self).destroy()
