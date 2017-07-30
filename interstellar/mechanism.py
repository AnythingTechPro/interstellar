from interstellar import node, resource

class MechanismError(RuntimeError):
    """
    A mechanism specfic runtime error
    """

class Mechanism(node.Node):
    """
    An attachment object which is attached to, or effects a sprite
    """

    NAME = None
    PROBABILITY = 0

    def __init__(self, parent):
        super(Mechanism, self).__init__(parent)

    def setup(self):
        pass

    def update(self):
        pass

    def move(self, x, y):
        pass

    def destroy(self):
        pass

class ShieldMechanism(Mechanism):
    NAME = 'Shield'

    def __init__(self, parent):
        super(ShieldMechanism, self).__init__(parent)

        self.image = resource.ResourceImage(parent._parent, 'assets/shield.png')
        self.image.position = (parent.x, parent.y)
        self.image.render(self._parent._parent.canvas)

        self.delay = 15

    def setup(self):
        self._parent.can_damage = False
        game.task_manager.add_delayed(self.delay, self.__destroy)

    def move(self, x, y):
        self.image.position = (x, y)

    def __destroy(self, task):
        self._parent._attachment = None
        self.destroy()

        return task.done

    def destroy(self):
        self.delay = 0
        self._parent.can_damage = True

        self.image.destroy()
        self.image = None

class InstantKillMechanism(Mechanism):
    NAME = 'InstantKill'

    def __init__(self, parent):
        super(InstantKillMechanism, self).__init__(parent)

        self.delay = 7
        self.previous_damage = parent.damage

    def setup(self):
        self._parent.damage = 100
        game.task_manager.add_delayed(self.delay, self.__destroy)

    def __destroy(self, task):
        self._parent._attachment = None
        self._parent.damage = self.previous_damage

        return task.done

    def destroy(self):
        self.delay = 0
        self.previous_damage = 0
