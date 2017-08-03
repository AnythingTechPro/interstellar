import os
import winsound
import pygame

class AudioError(IOError):
    """
    An audio specific io error
    """

class Audio(object):
    """
    Wrapper around pygame's sound module using mixer
    """

    def __init__(self, audio_manager, filename, loop=False):
        if not os.path.exists(filename):
            raise AudioError('Failed to find audio file %s!' % filename)

        self.audio_manager = audio_manager
        self.filename = filename
        self.loop = loop
        self.pending = False
        self.playing = False

    def play(self):
        if self.playing or not self.audio_manager.enabled:
            return

        pygame.mixer.music.load(self.filename)
        pygame.mixer.music.play(-1 if self.loop else 1)
        self.playing = True

    def stop(self):
        if not self.playing:
            return

        pygame.mixer.music.fadeout(1)
        self.playing = False

    def destroy(self):
        self.audio_manager = None
        self.filename = ''
        self.loop = False
        self.no_stop = False
        self.pending = False
        self.playing = False

class AudioManager(object):
    """
    A class that manages all audio wrappers
    """

    def __init__(self):
        self.audio = []
        self.enabled = True

    def has_audio(self, audio):
        return audio in self.audio

    def add_audio(self, audio, pending=False):
        if self.has_audio(audio):
            return

        self.audio.append(audio)

    def remove_audio(self, audio, pending=True):
        if not self.has_audio(audio):
            return

        if audio.playing:
            audio.stop()

        self.audio.remove(audio)

    def load(self, filename, *args, **kwargs):
        audio = Audio(self, filename, *args, **kwargs)
        self.add_audio(audio)

        return audio

    def unload(self, audio, *args, **kwargs):
        self.remove_audio(audio, *args, **kwargs)
        audio.destroy()

    def start_all(self):
        for audio in self.audio:

            if not audio.pending:
                continue

            audio.play()
            audio.pending = False

    def stop_all(self):
        for audio in self.audio:

            if audio.pending:
                continue

            audio.stop()
            audio.pending = True

    def toggle(self):
        if not self.enabled:
            self.enabled = True
            self.start_all()
        else:
            self.enabled = False
            self.stop_all()

    def destroy(self):
        self.audio = []
        self.enabled = False

class AudioSoundError(RuntimeError):
    """
    An audio sound specific runtime error
    """

class AudioSound(object):
    """
    A wrapper around pygame's mixer Sound component
    """

    def __init__(self, filepath):
        if not os.path.exists(filepath):
            raise AudioSoundError('Failed to load sound %s!' % filepath)

        self.sound = pygame.mixer.Sound(filepath)
        self.sound_playing = False

    @property
    def playing(self):
        return self.sound_playing

    def play(self):
        if self.sound_playing or not game.audio_manager.enabled:
            return

        self.sound.play()
        self.sound_playing = True

    def stop(self):
        if not self.sound_playing:
            return

        # attempt to reduce audio tear...
        self.sound.fadeout(1)
        self.sound_playing = False

    def destroy(self):
        del self.sound
        self.sound = None
        self.sound_playing = False
