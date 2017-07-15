import os
import winsound
import thread

class AudioError(IOError):
    """
    An audio specific io error
    """

class Audio(object):
    __slots__ = ('audio_manager', 'filename', 'playing')

    def __init__(self, audio_manager, filename):
        if not os.path.exists(filename):
            raise AudioError('Failed to find audio file %s!' % filename)

        self.audio_manager = audio_manager
        self.filename = filename
        self.playing = False

    def play(self, loop=False, no_stop=False):
        if self.playing:
            return

        flags = winsound.SND_FILENAME | winsound.SND_ASYNC

        if loop:
            flags |= winsound.SND_LOOP

        if no_stop:
            flags |= winsound.SND_NOSTOP

        winsound.PlaySound(self.filename, flags)
        self.playing = True

    def stop(self):
        if not self.playing:
            return

        winsound.PlaySound(self.filename, winsound.SND_PURGE | winsound.SND_ASYNC)
        self.playing = False

    def destroy(self):
        self.audio_manager = None
        self.filename = ''
        self.playing = False

class AudioManager(object):
    __slots__ = ('audio')

    def __init__(self):
        self.audio = []

    def has_audio(self, audio):
        return audio in self.audio

    def add_audio(self, audio):
        if self.has_audio(audio):
            return

        self.audio.append(audio)

    def remove_audio(self, audio):
        if not self.has_audio(audio):
            return

        if audio.playing:
            audio.stop()

        self.audio.remove(audio)

    def load(self, filename):
        audio = Audio(self, filename)
        self.add_audio(audio)

        return audio

    def unload(self, audio):
        self.remove_audio(audio)
        audio.destroy()

    def destroy(self):
        self.audio = []
