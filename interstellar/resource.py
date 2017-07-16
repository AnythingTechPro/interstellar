import os
import random
import pygame
import Tkinter
import tkFont
from PIL import Image, ImageTk
from interstellar import node

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

    def destroy(self):
        super(ResourceImage, self).destroy()

        self.root = None
        self.filepath = None

        del self.image
        self.image = None

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

    def bind(self, *args, **kwargs):
        if not self._label:
            return None

        self._label.bind(*args, **kwargs)

    def unbind(self, *args, **kwargs):
        if not self._label:
            return None

        self._label.unbind(*args, **kwargs)

    def bindall(self):
        self.bind('<Enter>', self.enter)
        self.bind('<Leave>', self.exit)
        self.bind('<Button-1>', self.click)

    def unbindall(self):
        self.unbind('<Enter>')
        self.unbind('<Leave>')
        self.unbind('<Button-1>')

    def enter(self, event):
        self.is_hovering = True
        self.hover_sound.play()
        self.label['foreground'] = 'red'

        if self.enter_handler:
            self.enter_handler()

    def exit(self, event):
        self.is_hovering = False
        self.hover_sound.stop()
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

    def update(self):
        if not self._label:
            return

        self.label.place(x=self._x, y=self._y, anchor=Tkinter.CENTER)

    def render(self, parent):
        if not parent:
            raise ResourceLabelError('Cannot attach image to invalid parent!')

        self.parent = parent

    def destroy(self):
        self.hover_sound.stop()
        self.clicked_sound.stop()

        del self._font
        self._font = None

        if self._label:
            self.unbindall()

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

        if self.current:
            self.deselect()

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
            self.current.stop()

        self.current = None

    def destroy(self):
        self.root = None
        self.audio = []
        self.current = None
