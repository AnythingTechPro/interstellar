import time
import _tkinter
import Tkinter
from interstellar import audio, resource, task

class GameDisplay(object):

    def __init__(self):
        self.root = Tkinter.Tk(sync=True)
        self._width = 0
        self._height = 0
        self._x = 0
        self._y = 0
        self._caption = ''
        self._resizable = True
        self._icon_filename = ''

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
        if self._x != self.root.winfo_x():
            self._x = self.root.winfo_x()

        return self._x

    @x.setter
    def x(self, x):
        if x is self._x:
            return

        self._x = x
        self.root.geometry('%dx%d+%d+%d' % (self._width, self._height, self._x, self._y))

    @property
    def y(self):
        if self._y != self.root.winfo_y():
            self._y = self.root.winfo_y()

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

    @property
    def icon(self):
        return self._icon_filename

    @icon.setter
    def icon(self, icon_filename):
        if icon_filename is self._icon_filename:
            return

        self._icon_filename = icon_filename
        self.root.iconbitmap(icon_filename)

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

        self.display.resizable = False
        self.display.icon = 'assets/icon.ico'
        self.task_manager = task.TaskManager()
        self.audio_manager = audio.AudioManager()
        self.score_board = resource.ResourceScoreBoard()
        self.shutdown = False
        self.last_scene = None
        self.current_scene = scene(self, self.display)

    def switch_scene(self, scene, *args, **kwargs):
        if self.current_scene:
            self.current_scene.destroy()
            self.last_scene = self.current_scene

        self.current_scene = scene(self, self.display, *args, **kwargs)
        self.current_scene.setup()

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
