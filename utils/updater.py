import numpy as np

from utils.simple_functions import get_perc


class Updater:
    def __init__(self, initial_time=0, initial_value=0):
        self.value = initial_value
        self.time = initial_time

    def __update_value__(self, dt=1):
        pass

    def update(self, dt=1):
        self.time += dt
        self.__update_value__(dt)
        return self.value


class NoUpdater(Updater):
    pass


class SinUpdater(Updater):
    def __init__(self, min_value=-1, max_value=-1, period=1, initial_time=0, initial_value=None):
        self.min = min_value
        self.max = max_value

        self.period = period

        if ((initial_value is not None) and
                (initial_value >= self.min) and
                (initial_value <= self.max)):
            initial_value = initial_value
        else:
            initial_value = get_perc(self.min, self.max, 0.5)

        super(SinUpdater, self).__init__(initial_time, initial_value)

    def __update_value__(self, dt=1):
        while self.time >= self.period:
            self.time -= self.period

        sine_position = np.sin(np.pi * 2 * get_perc(0, self.period, self.time))
        self.value = (((sine_position + 1) / 2) * (self.max - self.min)) + self.min


class LinUpdater(Updater):
    def __init__(self, time_step=1, initial_value=0):
        self.time_step = time_step
        super(LinUpdater, self).__init__(0, initial_value)

    def __update_value__(self, dt=1):
        self.value += dt * self.time_step


class BrownianUpdater(Updater):
    def __init__(self, time_step=1, initial_value=0):
        self.time_step = time_step
        super(BrownianUpdater, self).__init__(0, initial_value)

    def __update_value__(self, dt=1):
        if np.random.random() > 0.5:
            self.value += dt * self.time_step
        else:
            self.value -= dt * self.time_step


class CircularUpdater(SinUpdater):
    def __init__(self, center=0, distance=1, period=1, initial_time=0):
        super(CircularUpdater, self).__init__(center - distance, center + distance, period, initial_time, center)


# TODO: create an updater that takes as an input two updaters and creates the output as a composite
# Will it even be possible? It could possibly only utilize the `__update_value__` functions of those,
# but those expect to know the value before the change - so it's not very easy to do the composition
class CompositeUpdater(Updater):
    pass
