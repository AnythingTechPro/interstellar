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

        self.delay = 0

    def setup(self):
        game.task_manager.add_delayed(self.delay, lambda task: self.destroy())

    def update(self):
        pass

    def move(self, x, y):
        pass

    def destroy(self):
        self.delay = 0
        self._parent._attachment = None

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

        super(ShieldMechanism, self).setup()

    def move(self, x, y):
        self.image.position = (x, y)

    def destroy(self):
        self._parent.can_damage = True

        if self.image:
            self.image.destroy()

        self.image = None

        super(ShieldMechanism, self).destroy()

class InstantKillMechanism(Mechanism):
    NAME = 'InstantKill'

    def __init__(self, parent):
        super(InstantKillMechanism, self).__init__(parent)

        self.delay = 7
        self.previous_damage = parent.damage

    def setup(self):
        self._parent.damage = 100

        super(InstantKillMechanism, self).setup()

    def destroy(self):
        self._parent.damage = self.previous_damage
        self.previous_damage = 0

        super(InstantKillMechanism, self).destroy()

class FullHealthMechanism(Mechanism):
    NAME = 'FullHealth'

    def __init__(self, parent):
        super(FullHealthMechanism, self).__init__(parent)

        self.delay = 0

    def setup(self):
        self._parent.health = 100

        super(FullHealthMechanism, self).setup()

class DoubleHealthMechanism(Mechanism):
    NAME = 'DoubleHealth'

    def __init__(self, parent):
        super(DoubleHealthMechanism, self).__init__(parent)

        self.delay = 0

    def setup(self):
        new_health = self._parent.health * 2

        if new_health > 100:
            new_health = 100

        self._parent.health = new_health

        super(DoubleHealthMechanism, self).setup()
