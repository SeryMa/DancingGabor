import numpy as np

from generators.noise_generator import NoiseGenerator
from noise_processing.noise_processor import NoiseProcessor
from utils.array import get_windows


class ImageProceser(NoiseProcessor):
    def __init__(self, generator: NoiseGenerator, window_size: int = 10, step: int = None, process_functions=None,
                 **kwargs):
        super(ImageProceser, self).__init__(generator)

        self.window_size = window_size
        self.step = step if step is not None else self.window_size // 2
        self.process_functions = process_functions or []

        self.height_dim = (self.height + self.step) // self.step
        self.width_dim = (self.width + self.step) // self.step
        self.value_windows = None

    def __process__(self, dt=1) -> None:
        window_iterator = get_windows(self.last_frame, self.window_size, self.window_size, self.step)

        flat_map = [
            [process_function(window) for process_function in self.process_functions]
            for window in window_iterator
        ]
        self.value_windows = np.reshape(flat_map, (self.width_dim, self.height_dim, len(self.process_functions))).T
