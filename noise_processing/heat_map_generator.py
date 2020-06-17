import numpy as np

from generators.noise_generator import NoiseGenerator
from noise_processing.noise_processor import NoiseProcessor
from utils.array import get_windows_indices


class HeatMapGenerator(NoiseProcessor):
    def __init__(self, generator: NoiseGenerator, process_function, window_size: int = 10, step: int = None,
                 aggregate_funciton=None, compute_cached_values=None):
        super(HeatMapGenerator, self).__init__(generator)

        self.window_size = window_size
        self.step = step if step is not None else self.window_size // 2
        self.process_function = process_function
        self.aggregate_function = aggregate_funciton
        self.compute_cached_values = compute_cached_values

        self.height_dim = (self.height // self.step) + 2
        self.width_dim = (self.width // self.step) + 2
        self.value_windows = None

    def __process__(self, dt=1) -> None:
        window_iterator = get_windows_indices(self.last_frame.shape, self.window_size, self.window_size, self.step)
        cached_values = self.compute_cached_values() if self.compute_cached_values else {}

        flat_map = [self.process_function(*window, **cached_values) for window in window_iterator]

        self.aggregate_function and self.aggregate_function(np.array(flat_map))

        self.value_windows = np.reshape(flat_map, (self.width_dim, self.height_dim)).T

        output_map = np.ones((self.width, self.height))

        for x in range(self.width_dim - 1):
            for y in range(self.height_dim - 1):
                width_offset = x * self.step
                height_offset = y * self.step
                output_map[
                width_offset:width_offset + self.step,
                height_offset:height_offset + self.step
                ] *= (self.value_windows[x, y] +
                      self.value_windows[x + 1, y] +
                      self.value_windows[x, y + 1] +
                      self.value_windows[x + 1, y + 1]) / 4

        self.last_frame = output_map
