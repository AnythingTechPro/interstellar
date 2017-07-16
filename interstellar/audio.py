import os
import winsound
import thread

class AudioError(IOError):
    """
    An audio specific io error
    """

class Audio(object):
    __slots__ = ('audio_manager', 'filename', 'loop', 'no_stop', 'pending', 'playing')

    def __init__(self, audio_manager, filename, loop=False, no_stop=False):
        if not os.path.exists(filename):
            raise AudioError('Failed to find audio file %s!' % filename)

        self.audio_manager = audio_manager
        self.filename = filename
        self.loop = loop
        self.no_stop = no_stop
        self.pending = False
        self.playing = False

    def play(self):
        if self.playing or not self.audio_manager.enabled:
            return

        flags = winsound.SND_FILENAME | winsound.SND_ASYNC

        if self.loop:
            flags |= winsound.SND_LOOP

        if self.no_stop:
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
        self.loop = False
        self.no_stop = False
        self.pending = False
        self.playing = False

class AudioManager(object):
    __slots__ = ('audio', 'enabled')

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
