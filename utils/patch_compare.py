import numpy as np

from generators.gabor_generator import GaborGenerator, PlaidGenerator
from utils.image import covariance, get_luminance
from utils.updater import LinUpdater


class PatchComparator:
    K1 = 0.01
    K2 = 0.03
    # Thanks to pre-generated patterns we can fix the dynamic at 1
    DYNAMIC_RANGE = 1

    C1 = (K1 * DYNAMIC_RANGE) ** 2
    C2 = (K2 * DYNAMIC_RANGE) ** 2

    def __init__(self, deg, ppd, detect_gabor=True, granularity=100, freq_max=100):
        #  Theta and Phase are periodical values that are repeated after 180 degrees resp 1 phase
        #  Freq can go possibly to infinity. Value 100 is chosen to fit the experiment
        update_list = {
            'theta': 180 / granularity,
            'phase': 1 / granularity,
            'freq': freq_max / granularity,
        }

        self.pattern_patches = []
        for value, speed in update_list.items():
            update = (value, LinUpdater(initial_value=0, time_step=speed).update)
            patch_generator_constructor = GaborGenerator if detect_gabor else PlaidGenerator
            patch_generator = patch_generator_constructor(patch_size_deg=deg, ppd=ppd, update_list=[update])

            # TODO: check the +1 - it might be redundant
            for i in range(granularity + 1):
                patch = patch_generator.get_normalized_patch()
                patch_luminance = get_luminance(patch)
                patch_variance = np.var(patch)
                self.pattern_patches.append((patch, patch_luminance, patch_variance))

                patch_generator.get_next_frame()

    def get_best_ssim_match(self, image):
        image_luminance = get_luminance(image)
        image_variance = np.var(image)

        return max([
            self.__ssim(pattern_luminance, pattern_variance,
                        image_luminance, image_variance,
                        covariance(image, pattern))
            for pattern, pattern_luminance, pattern_variance in self.pattern_patches
        ])

    def __ssim(self, pattern_luminance, pattern_variance, image_luminance, image_variance, cov) -> float:
        numerator = (2 * pattern_luminance * image_luminance + self.C1) * (2 * cov + self.C2)
        denominator = (pattern_luminance ** 2 + image_luminance ** 2 + self.C1) * (
                pattern_variance + image_variance + self.C2)

        return numerator / denominator
