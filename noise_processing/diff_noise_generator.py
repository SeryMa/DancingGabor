from typing import Callable

import numpy as np

from generators.noise_generator import NoiseGenerator
from noise_processing.noise_processor import PersistentNoiseProcessor
from utils.simple_functions import simple_difference


class PureDifferenceNoiseGenerator(PersistentNoiseProcessor):
    def __init__(self, generator: NoiseGenerator,
                 diff_function: Callable[[np.ndarray, np.ndarray], np.ndarray] = simple_difference):
        super(PureDifferenceNoiseGenerator, self).__init__(generator)

        self.diff_function = diff_function
        self.last_frame_noise = self.noise_generator.get_next_frame(0)

    def __update__(self, dt=1) -> None:
        self.new_frame_noise = self.noise_generator.get_next_frame(0)

        self.__process__(dt)

        self.last_frame_noise = self.new_frame_noise

    def __process__(self, dt=1) -> None:
        self.frame = self.diff_function(self.new_frame_noise, self.last_frame_noise)


class DifferenceNoiseGenerator(PureDifferenceNoiseGenerator):
    def __init__(self, generator: NoiseGenerator, period=1,
                 diff_function: Callable[[np.ndarray, np.ndarray], np.ndarray] = simple_difference):
        super(DifferenceNoiseGenerator, self).__init__(generator, diff_function)

        self.period = period

    def __process__(self, dt=1) -> None:
        diff = self.diff_function(self.new_frame_noise, self.last_frame_noise)

        max_distance = self.diff_function(self.new_frame_noise.max(), self.new_frame_noise.min())

        # we expect that the values change at most from -1 to 1 in `period` [time units]
        # so values that are lower than `max_distance/period * dt`
        # are clipped since they respect the natural change of the scene
        trim = max_distance * dt / self.period
        self.frame = np.clip(diff, trim, None) - trim


class AvgDifferenceNoiseGenerator(PureDifferenceNoiseGenerator):
    def __init__(self, generator: NoiseGenerator, period=1, percentiles=10,
                 diff_function: Callable[[np.ndarray, np.ndarray], np.ndarray] = simple_difference):
        super(AvgDifferenceNoiseGenerator, self).__init__(generator, diff_function)

        self.period = period
        self.percentiles = range(0, 101, 100 // percentiles)
        perc_step = 2 / percentiles
        self.values = [*np.arange(1., 0., -perc_step), *np.arange(0., 1., perc_step), 1.]

    def __process__(self, dt=1) -> None:
        diff = self.new_frame_noise - self.last_frame_noise
        ps = np.percentile(diff, self.percentiles)
        iis = [diff >= p for p in ps]
        for i, val in zip(iis, self.values):
            diff[i] = val

        self.frame = diff
