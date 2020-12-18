from generators.gabor_generator import GaborGenerator, PlaidGenerator
from utils.image import covariance, get_luminance, get_rms_contrast, \
    __luminance_comparison, __contrast_comparison, __structural_similarity, __phase_invariant_similarity, simple_combine
from utils.updater import LinUpdater

luminance_comparison = __luminance_comparison
contrast_comparison = __contrast_comparison
structural_similarity = __structural_similarity
phase_invariant_similarity = __phase_invariant_similarity


class PatchComparator:
    K1 = 0.01
    K2 = 0.03
    # Thanks to pre-generated patterns we can fix the dynamic at 1
    DYNAMIC_RANGE = 1

    C1 = (K1 * DYNAMIC_RANGE) ** 2
    C2 = (K2 * DYNAMIC_RANGE) ** 2

    def __init__(self, deg, ppd, detect_gabor=True, granularity=100, freq_max=100,
                 alpha=1, beta=1, gamma=1, simple=True):
        #  Theta and Phase are periodical values that are repeated after 180 degrees resp 1 phase
        #  Freq can go possibly to infinity. Value 100 is chosen to fit the experiment
        update_list = {
            'theta': 180 / granularity,
            'phase': 1 / granularity,
            'freq': freq_max / granularity,
        }

        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

        self.simple = simple

        self.pattern_patches = []
        for value, speed in update_list.items():
            update = (value, LinUpdater(initial_value=0, time_step=speed).update)
            patch_generator_constructor = GaborGenerator if detect_gabor else PlaidGenerator
            patch_generator = patch_generator_constructor(patch_size_deg=deg, ppd=ppd, update_list=[update])

            # TODO: check the +1 - it might be redundant
            for i in range(granularity + 1):
                patch = patch_generator.get_normalized_patch()
                patch_luminance = get_luminance(patch)
                patch_contrast = get_rms_contrast(patch)
                self.pattern_patches.append((patch, patch_luminance, patch_contrast))

                patch_generator.get_next_frame()

    def get_best_ssim_match(self, image):
        image_luminance = get_luminance(image)
        image_variance = get_rms_contrast(image)

        return max([
            self.__ssim(pattern_luminance, pattern_variance,
                        image_luminance, image_variance,
                        image, pattern)
            for pattern, pattern_luminance, pattern_variance in self.pattern_patches
        ])

    def __ssim(self, pattern_luminance, pattern_contrast, image_luminance, image_contrast, image, pattern) -> float:
        structure = structural_similarity(covariance(image, pattern), pattern_contrast, image_contrast,
                                          self.C2 / 2) if self.simple else phase_invariant_similarity(image, pattern,
                                                                                                      self.C2 / 2)

        return simple_combine([
            (luminance_comparison(pattern_luminance, image_luminance, self.C1), self.alpha),
            (contrast_comparison(pattern_contrast, image_contrast, self.C2), self.beta),
            (structure, self.gamma)
        ])
