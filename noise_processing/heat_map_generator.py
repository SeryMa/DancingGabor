import numpy as np

from generators.noise_generator import NoiseGenerator
from noise_processing.image_proceser import ImageProceser
from utils.image import get_rms_contrast


class HeatMapGenerator(ImageProceser):
    def __init__(self, generator: NoiseGenerator, map_function=get_rms_contrast, **kwargs):
        super(HeatMapGenerator, self).__init__(generator, process_functions=[map_function], **kwargs)

    def __process__(self, dt=1) -> None:
        super(HeatMapGenerator, self).__process__(dt)
        self.value_windows = self.value_windows[0]

        output_map = np.ones((self.width, self.height))

        for x in range(self.width_dim - 1):
            for y in range(self.height_dim - 1):
                width_offset = x * self.step
                height_offset = y * self.step
                output_map[
                width_offset:width_offset + self.step,
                height_offset:height_offset + self.step] *= (self.value_windows[x, y] + self.value_windows[x + 1, y] +
                                                             self.value_windows[x, y + 1] + self.value_windows[
                                                                 x + 1, y + 1]) / 4

        self.last_frame = output_map
