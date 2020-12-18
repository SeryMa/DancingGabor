from typing import Callable, Tuple, Iterable

import numpy as np

from generators.noise_generator import NoiseGenerator
from utils.array import apply_patch


class PatchedNoiseGenerator(NoiseGenerator):
    """ `NoiseGenerator` that puts noise patches into one base noise image

    It takes one `NoiseGenerator` as a base for generating the base noise.
    Then an array of pairs (`positionGenerator`, `NoiseGenerators`).
    For every item in the array an position in the base noise image is generated.
    Into this position a noise image patch is inserted.

    Parameters
    ----------
    width : int
        Width of the generated noise

    height : int
        Height of the generated noise

    generator : NoiseGenerator
        Generator used to generate the base noise image

    patch_generators : Iterable[Tuple[NoiseGenerator, Callable[[float], Tuple[float, float]]]]
        List of patch generating pairs. First in pair is the patch generator.
        Second in the pair is function generating the position of the patch in the base image.
        The position generator should accept one parameter denoting the time that has passed since last generation.
        This can be used to generate patches that are moving in the base noise image.

    contrast : float, optional
        The weight with which the patch is applied into the image.
        Defaults to 0.5

    Attributes
    ----------
    width : int
        Width of the generated noise

    height : int
        Height of the generated noise

    frame : ndarray
        The last frame that has been generated

    contrast: float
        The weight with which the patch is applied into the image.
    """

    def __init__(self, width, height, generator: NoiseGenerator,
                 patch_generators: Iterable[Tuple[NoiseGenerator, Callable[[float], Tuple[float, float]]]],
                 contrast=0.5):
        self.background_generator = generator
        self.patch_generators = patch_generators
        super(PatchedNoiseGenerator, self).__init__(width, height)

        self.contrast = contrast

    def __update__(self, dt=1) -> None:
        background_noise = self.background_generator.get_next_frame(dt)

        for patch_generator, position_generator in self.patch_generators:
            patch = patch_generator.get_next_frame(dt)
            x, y = np.rint(position_generator(dt)).astype('int')

            # apply_patch(background_noise, patch, x, y, overwrite=True)
            apply_patch(background_noise, patch, x, y, contrast=self.contrast)

        # We do not want to call normalize,
        # because that could alter values that shouldn't be affected by the patch (eg edges)
        # So instead we just clip values that are way too high or low.
        self.frame = np.clip(background_noise, 0, 1)
