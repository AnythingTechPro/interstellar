import time
import threading

class TaskResult(object):
    DONE = 0
    CONT = 1
    WAIT = 2

class TaskError(RuntimeError):
    """
    A task specific runtime error
    """

class Task(object):

    def __init__(self, id):
        self.id = id
        self.name = 'Task-%d' % id
        self.function = None
        self.timestamp = time.time()
        self.delay = 0.0
        self.can_delay = True
        self.args = []
        self.kwargs = {}
        self.active = False

    @property
    def done(self):
        return TaskResult.DONE

    @property
    def cont(self):
        return TaskResult.CONT

    @property
    def wait(self):
        return TaskResult.WAIT

    @property
    def duration(self):
        return time.time() - self.timestamp

    def execute(self):
        if not callable(self.function):
            raise TaskError('Failed to execute task %s, function not callable!' % self.name)

        if self.can_delay:
            if self.duration < self.delay:
                return self.wait
            else:
                self.timestamp = time.time()

        return self.function(self, *self.args, **self.kwargs)

    def run(self):
        if not self.active:
            raise TaskError('Failed to run task %s, never activated!' % self.name)

        return self.execute()

    def destroy(self):
        self.id = self.name = self.function = self.timestamp = self.args = self.kwargs = None

class TaskManagerError(RuntimeError):
    """
    A task manager specific runtime error
    """

class TaskManager(object):
    TIMEOUT = 0.01

    def __init__(self):
        self.running = {}
        self.waiting = {}
        self.id = 0

    @property
    def next_id(self):
        self.id += 1; return self.id

    def has(self, name):
        return name in self.running or name in self.waiting

    def delete(self, task, destroy):
        try:
            del self.waiting[task.name]
        except KeyError:
            del self.running[task.name]

        if destroy:
            task.destroy()

    def activate(self, task):
        if self.has(task.name):
            raise TaskManagerError('Failed to activate task %s, already activated!' % task.name)

        task.active = True
        self.waiting[task.name] = task

        return task

    def deactivate(self, task, destroy=False):
        if not self.has(task.name):
            raise TaskManagerError('Failed to deactivate task %s, never activated!' % task.name)

        task.active = False
        self.delete(task, destroy)

    def prepend(self, function, delay, *args, **kwargs):
        task = Task(self.next_id)
        task.function = function
        task.delay = delay
        task.args = args
        task.kwargs = kwargs

        return self.activate(task)

    def add(self, function, *args, **kwargs):
        return self.prepend(function, 0, *args, **kwargs)

    def add_delayed(self, delay, function, *args, **kwargs):
        return self.prepend(function, delay, *args, **kwargs)

    def add_deferred(self, function):

        def decorate(*args, **kwargs):
            return self.add(function, *args, **kwargs)

        return decorate

    def remove(self, task):
        self.deactivate(task, destroy=True)

    def cycle(self, task):
        self.deactivate(task)
        self.activate(task)

    def mainloop(self):
        while True:
            for name in list(self.waiting):
                self.running[name] = self.waiting.pop(name)

            for task in list(self.running.values()):
                result = task.run()

                if task.can_delay:
                    task.can_delay = False

                if result == TaskResult.DONE:
                    self.remove(task)
                elif result == TaskResult.CONT:
                    self.cycle(task)
                elif result == TaskResult.WAIT:
                    task.can_delay = True
                else:
                    self.remove(task)

            time.sleep(self.TIMEOUT)

    def run(self, threaded=True, daemon=True):
        try:
            if threaded:
                thread = threading.Thread(target=self.mainloop)
                thread.daemon = daemon
                thread.start()
            else:
                self.mainloop()
        except (KeyboardInterrupt, SystemExit):
            self.destroy()

    def destroy(self):
        for name in list(self.waiting):
            self.waiting.pop(name).destroy()

        for name in list(self.running):
            self.running.pop(name).destroy()

        self.id = 0
