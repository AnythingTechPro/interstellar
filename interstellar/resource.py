import os
import random
import time
import pygame
import Tkinter
import tkFont
from PIL import Image, ImageTk
from interstellar import node, util

class ResourceImageError(node.NodeError):
    """
    A resource image specific runtime error
    """

class ResourceImage(node.Node):
    """
    A image object that manages and renders images to a canvas
    """

    __slots__ = ('root', '_parent', '_id', 'filepath', 'image', '_x', '_y',
        '_width', '_height')

    def __init__(self, root, filepath):
        super(ResourceImage, self).__init__()

        if not os.path.exists(filepath):
            raise ResourceImageError('Failed to load image %s!' % filepath)

        self.root = root
        self.filepath = filepath
        self.image = ImageTk.PhotoImage(Image.open(filepath))

    @node.Node.parent.setter
    def parent(self, parent):
        if parent is self._parent:
            raise ResourceImageError('Already attached to parent!')

        self._parent = parent

        if not self.image and self.filepath:
            self.image = ImageTk.PhotoImage(Image.open(self.filepath))

        self._id = parent.create_image(self._x, self._y, image=self.image, anchor=Tkinter.CENTER)

    @node.Node.x.setter
    def x(self, x):
        if self._x is x:
            return

        self._x = x

        if self._parent:
            self.move()

    @node.Node.y.setter
    def y(self, y):
        if self._y is y:
            return

        self._y = y

        if self._parent:
            self.move()

    @node.Node.position.setter
    def position(self, position):
        self._x, self._y = position

        if self._parent:
            self.move()

    @property
    def width(self):
        if self._width != self.image.width():
            self._width = self.image.width()

        return self._width

    @property
    def height(self):
        if self._height != self.image.height():
            self._height = self.image.height()

        return self._height

    def collide_point(self, target):
        min_x, min_y = self.x - self.width / 2, self.y - self.height / 2
        min_tx, min_ty = target.x - target.width / 2, target.y - target.height / 2

        max_x, max_y = self.x + self.width / 2, self.y + self.height / 2
        max_tx, max_ty = target.x + target.width / 2, target.y + target.height / 2

        return min_x <= max_tx and min_x >= min_tx and min_y <= max_ty and min_y >= min_ty

    def move(self):
        self._parent.coords(self._id, (self._x, self._y))

    def render(self, parent):
        if not parent:
            raise ResourceImageError('Cannot attach image to invalid parent!')

        self.parent = parent

    def unrender(self):
        if not self._parent:
            raise ResourceImageError('Cannot detach image from invalid parent')

        del self.image
        self.image = None
        self._parent = None

    def destroy(self):
        super(ResourceImage, self).destroy()

        self.root = None
        self.filepath = None

        del self.image
        self.image = None

class ResourceScrolledImage(node.Node):
    """
    An image that scrolls across the screen endlessly
    """

    def __init__(self, root, filename):
        super(ResourceScrolledImage, self).__init__(root)

        self.root = root
        self.image_0 = ResourceImage(root, filename)
        self.image_1 = ResourceImage(root, filename)
        self.speed = 0

    @node.Node.x.setter
    def x(self, x):
        self.image_0.x = x
        self.image_1.x = x

    @node.Node.y.setter
    def y(self, y):
        self.image_0.y = y
        self.image_1.y = self.image_0.y - self.image_1.height

    def update(self):
        if self.image_0.y - self.image_0.height / 2 >= self._parent.display.height:
            self.image_0.y = self.image_1.y - self.image_0.height

        if self.image_1.y - self.image_1.height / 2 >= self._parent.display.height:
            self.image_1.y = self.image_0.y - self.image_1.height

        self.image_0.y += self.speed
        self.image_1.y += self.speed

    def render(self, parent):
        self.image_0.render(parent)
        self.image_1.render(parent)

    def destroy(self):
        self.root = None
        self.image_0.destroy()
        self.image_1.destroy()
        self.speed = 0

class ResourceFrameImage(node.Node):
    """
    A class for creating GIF like images with multiple playback frames
    """

    def __init__(self, root, frames, callback=None):
        super(ResourceFrameImage, self).__init__()

        if not isinstance(frames, list):
            raise ResourceImageError('Frame image objects only support list arrays!')

        self.root = root
        self.frames = frames
        self.callback = callback
        self.images = {}
        self.can_play = False

        for index in xrange(len(self.frames)):
            self.images[index] = ResourceImage(self.root, self.frames[index])

        self.current_index = 0
        self.current_image = None

    @node.Node.x.setter
    def x(self, x):
        for image in self.images.values():
            image.x = x

    @node.Node.y.setter
    def y(self, y):
        for image in self.images.values():
            image.y = y

    @node.Node.position.setter
    def position(self, position):
        for image in self.images.values():
            image.position = position

    @property
    def current_frame(self):
        return self.images[self.current_index]

    def update(self):
        if not self.can_play:
            return

        if self.current_index >= len(self.images):
            self.current_index = 0

            if callable(self.callback):
                self.callback()

        if self.current_image and self.current_image.parent:
            self.current_image.unrender()

        self.current_image = self.images[self.current_index]
        self.current_image.render(self.root)

        self.current_index += 1

    def destroy(self):
        self.root = None
        self.frames = []
        self.images = {}
        self.callback = None
        self.can_explode = False
        self.current_index = 0
        self.current_image = None

        super(ResourceFrameImage, self).destroy()

class ResourceLabelError(node.NodeError):
    """
    A resource label specific runtime error
    """

class ResourceLabel(node.Node):
    """
    A tkinter label object with special properties...
    """

    __slots__ = ('font_size', 'font_family', 'bind_events', '_font', '_text', '_width', '_height', '_label',
        'enter_handler', 'exit_handler', 'clicked_handler', 'is_hovering', 'is_clicked', 'hover_sound', 'clicked_sound')

    def __init__(self, font_size, font_family='Pixeled', bind_events=True):
        super(ResourceLabel, self).__init__()

        util.load_font('assets/font/Pixeled.ttf')

        self.font_size = font_size
        self.font_family = font_family
        self.bind_events = bind_events
        self._font = tkFont.Font(family=self.font_family, size=self.font_size)
        self._text = None
        self._width = font_size
        self._height = font_size / 2
        self._label = None

        self.enter_handler = None
        self.exit_handler = None
        self.clicked_handler = None

        self.is_hovering = False
        self.is_clicked = False

        self.hover_sound = pygame.mixer.Sound('assets/audio/sfx/button_over.wav')
        self.clicked_sound = pygame.mixer.Sound('assets/audio/sfx/button_down.wav')

    @node.Node.parent.setter
    def parent(self, parent):
        if parent is self._parent:
            return

        self._parent = parent
        self.label = Tkinter.Label(parent, text=self._text, font=self._font,
            background='black', foreground='white')

        # move the label object into position; the position can be set before
        # or after the label has been parented.
        self.move()

    @node.Node.x.setter
    def x(self, x):
        if x is self._x:
            return

        self._x = x

        if self._parent:
            self.move()

    @node.Node.y.setter
    def y(self, y):
        if y is self._y:
            return

        self._y = y

        if self._parent:
            self.move()

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, font):
        self._font = font

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text

        if self.label:
            self.label['text'] = text

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        if label is self._label:
            return

        if self._label and self.bind_events:
            self.unbindall()

        self._label = label
        label.pack()

        if self.bind_events:
            self.bindall()

    def bind(self, event, *args, **kwargs):
        if not self._label:
            return None

        self._label.bind('<%s>' % event, *args, **kwargs)

    def unbind(self, event, *args, **kwargs):
        if not self._label:
            return None

        self._label.unbind('<%s>' % event, *args, **kwargs)

    def send(self, event, *args, **kwargs):
        if not self._label:
            return None

        self._label.event_generate('<%s>' % event, *args, **kwargs)

    def bindall(self):
        self.bind('Enter', self.enter)
        self.bind('Leave', self.exit)
        self.bind('Button-1', self.click)

    def unbindall(self):
        self.unbind('Enter')
        self.unbind('Leave')
        self.unbind('Button-1')

    def enter(self, event):
        self.is_hovering = True
        self.hover_sound.play()
        self.label['foreground'] = 'red'

        if self.enter_handler:
            self.enter_handler()

    def exit(self, event):
        self.is_hovering = False

        # instead of stopping the audio entirely, fade out to help reduce
        # that annoying audio tearing...
        self.hover_sound.fadeout(1)
        self.label['foreground'] = 'white'

        if self.exit_handler:
            self.exit_handler()

    def click(self, event):
        if not self.is_hovering:
            return

        self.clicked_sound.play()

        if self.clicked_handler:
            self.clicked_handler()
        else:
            self.clicked()

    def clicked(self):
        pass

    def move(self):
        self.label.place(x=self._x, y=self._y, anchor=Tkinter.CENTER)

    def render(self, parent):
        if not parent:
            raise ResourceLabelError('Cannot attach image to invalid parent!')

        self.parent = parent

    def derender(self):
        if not self._parent:
            raise ResourceLabelError('Cannot detach image from invalid parent!')

        self._label.pack_forget()
        self._label.destroy()

        self._parent = None

    def destroy(self):
        self.hover_sound.stop()
        self.clicked_sound.stop()

        del self._font
        self._font = None

        if self._label:
            self.unbindall()
            self._label.destroy()

        self.font_size = 0
        self.font_family = 0
        self.bind_events = False
        self._text = None
        self._label = None
        self.is_hovering = False
        self.is_clicked = False

        super(ResourceLabel, self).destroy()

class ResourceAudioArrayError(RuntimeError):
    """
    A audio array specific runtime error
    """

class ResourceAudioArray(object):
    """
    An object that contains multiple audio tracks to randomly select...
    """

    def __init__(self, root, audio):
        if not isinstance(audio, list):
            raise ResourceAudioArrayError('List array objects are only supported!')

        self.root = root
        self.audio = audio
        self.current = None

    def select(self, *args, **kwargs):
        use_pygame = kwargs.get('use_pygame', False)
        audio_filename = random.choice(self.audio)

        if not use_pygame:
            self.current = self.root.audio_manager.load(audio_filename, *args, **kwargs)
        else:
            self.current = pygame.mixer.Sound(audio_filename)

        return self.current

    def deselect(self, *args, **kwargs):
        use_pygame = kwargs.get('use_pygame', False)

        if not use_pygame:
            self.root.audio_manager.unload(self.current, *args, **kwargs)
        else:
            # instead of stopping the audio entirely, fade out to help reduce
            # that annoying audio tearing...
            self.current.fadeout(1)

        self.current = None

    def destroy(self):
        self.root = None
        self.audio = []
        self.current = None

class ResourceTimer(object):
    """
    An object that manages the amount time since it was constructed
    """

    __slots__ = ('start_time')

    def __init__(self):
        self.start_time = time.time()

    @property
    def current_time(self):
        return time.time() - self.start_time

    def destroy(self):
        self.start_time = 0

class ResourceTimerLabel(ResourceLabel):
    """
    A label object that displays time from a ResourceTimer
    """

    __slots__ = ('timer')

    def __init__(self, *args, **kwargs):
        super(ResourceTimerLabel, self).__init__(*args, **kwargs)

        self.timer = ResourceTimer()
        self.text = self.current_time

    @property
    def current_time(self):
        minutes, seconds = divmod(self.timer.current_time, 60)

        if not minutes:
            string = 'Time: %d' % seconds
        else:
            string = 'Time: %d:%d' % (minutes, seconds)

        return string

    def update(self):
        self.text = self.current_time

        super(ResourceTimerLabel, self).update()

    def destroy(self):
        self.timer.destroy()
        self.timer = None

        super(ResourceTimerLabel, self).setup()
