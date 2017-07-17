
class NodeError(RuntimeError):
    """
    A node specific runtime error
    """

class Node(object):
    """
    An object that exists in the application which has special properties...
    """

    __slots__ = ('_parent', '_id', '_x', '_y', '_width', '_height', '_rotation')

    def __init__(self, parent=None):
        self._parent = parent
        self._id = None
        self._x = 0
        self._y = 0
        self._width = 0
        self._height = 0
        self._rotation = 0

    @property
    def parent(self):
        return self._parent

    @property
    def id(self):
        return self._id

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def position(self):
        return (self._x, self._y)

    @position.setter
    def position(self, position):
        self._x, self._y = position

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def rotation(self):
        return self._rotation

    def setup(self):
        pass

    def update(self):
        pass

    def destroy(self):
        self._parent = None
        self._id = None
        self._x = 0
        self._y = 0
        self._width = 0
        self._height = 0
        self._rotation = 0
