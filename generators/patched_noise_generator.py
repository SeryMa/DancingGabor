import numpy as np

from generators.noise_generator import NoiseGenerator
from utils.array import normalize, apply_patch


class PatchedNoiseGenerator(NoiseGenerator):
    def __init__(self, width, height, generator: NoiseGenerator, patch_generators, contrast=0.5, **kwargs):
        self.background_generator = generator
        self.patch_generators = patch_generators
        super(PatchedNoiseGenerator, self).__init__(width, height)

        self.contrast = contrast

    def __update__(self, dt=1) -> None:
        background_noise = self.background_generator.get_next_frame(dt)
        normalize(background_noise)

        # The Patch is expected to have values in the interval [-1,1]
        for patch_generator, position_generator in self.patch_generators:
            patch = patch_generator.get_next_frame(dt)
            x, y = np.rint(position_generator(dt)).astype('int')

            # apply_patch(background_noise, patch, x, y, overwrite=True)
            apply_patch(background_noise, patch, x, y, contrast=self.contrast)

        self.last_frame = np.clip(background_noise, 0, 1)
