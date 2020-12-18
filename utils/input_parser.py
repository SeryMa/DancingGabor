from generators.circular_noise_generator import *
from generators.continuous_noise_generator import *
from generators.gabor_generator import *
from generators.patched_noise_generator import *
from generators.pink_noise_generator import *
from generators.single_color_generator import *
from heat_map_generator import *
from noise_processing.diff_noise_generator import *
from noise_processing.image_proceser import *
from utils.image import get_rms_contrast
from utils.updater import *


def get_updater(**kwargs):
    if 'sin' in kwargs:
        return SinUpdater(**kwargs['sin'])
    elif 'circ' in kwargs:
        return CircularUpdater(**kwargs['circ'])
    elif 'brown' in kwargs:
        return BrownianUpdater(**kwargs['brown'])
    elif 'lin' in kwargs:
        return LinUpdater(**kwargs['lin'])
    elif 'none' in kwargs:
        return NoUpdater(**kwargs['none'])
    else:
        return NoUpdater()


def get_position_updater(**kwargs):
    x_updater = get_updater(**kwargs['x']) if 'x' in kwargs else NoUpdater()
    y_updater = get_updater(**kwargs['y']) if 'y' in kwargs else x_updater

    return lambda dt: (x_updater.update(dt), y_updater.update(dt))


def get_value_updater(**kwargs):
    updater = get_updater(**kwargs)
    return updater.update


def get_noise(width, height, **kwargs):
    if 'white' in kwargs:
        kwargs.pop('white')
        return WhiteNoise(width, height), kwargs

    elif 'pink' in kwargs:
        kwargs.pop('pink')
        return PinkNoise(width, height), kwargs

    elif 'single' in kwargs:
        specs = kwargs.pop('single')
        return SingleColor(width, height, **specs), kwargs

    elif 'diff' in kwargs:
        generator, specs = get_noise(width, height, **kwargs.pop('diff'))

        # TODO: Fill in the missing diff function
        return DifferenceNoiseGenerator(generator=generator, **specs), kwargs

    elif 'heat' in kwargs:
        generator, specs = get_noise(width, height, **kwargs.pop('heat'))

        def process_function(x1, x2, y1, y2):
            return get_rms_contrast(generator.get_next_frame(0)[x1:x2, y1:y2])

        return HeatMapGenerator(generator=generator, process_function=process_function, **specs), kwargs

    elif 'process' in kwargs:
        generator, specs = get_noise(width, height, **kwargs.pop('process'))

        return ImageProcesser(generator=generator), kwargs

    elif 'circular' in kwargs:
        generator, specs = get_noise(width, height, **kwargs.pop('circular'))

        return CircularNoiseGenerator(width, height, generator=generator, **specs), kwargs

    elif 'continuous' in kwargs:
        generator, specs = get_noise(width, height, **kwargs.pop('continuous'))

        interpolation = interpolate
        if 'interpolation' in kwargs:
            interpolation_type = specs.pop('interpolation')

            if interpolation_type != 'simple':
                raise ValueError(
                    f"The interpolation function {interpolation_type} wasn't recognized. Try using 'simple' instead")

        return ContinuousNoiseGenerator(width, height, generator=generator, interpolation=interpolation,
                                        **specs), kwargs

    elif 'patched' in kwargs:
        generator, specs = get_noise(width, height, **kwargs.pop('patched'))

        patch_generators = []
        if 'patches' in specs:
            for patch in specs.pop('patches'):
                patch_generator, _ = get_noise(width, height, **patch)
                patch_generators.append((patch_generator, get_position_updater(**patch)))

        return PatchedNoiseGenerator(width, height, generator=generator, patch_generators=patch_generators), kwargs

    elif 'gabor' in kwargs:
        specs = kwargs.pop('gabor')

        update_list = []
        if 'updates' in specs:
            for patch in specs.pop('updates'):
                update_list.append((
                    patch.pop('value'),
                    get_value_updater(**patch)
                ))

        return GaborGenerator(update_list=update_list, **specs), kwargs

    elif 'plaid' in kwargs:
        specs = kwargs.pop('plaid')

        update_list = []
        if 'updates' in specs:
            for patch in specs.pop('updates'):
                update_list.append((
                    patch.pop('value'),
                    get_value_updater(**patch)
                ))

        return PlaidGenerator(update_list=update_list, **specs), kwargs

    else:
        return None, kwargs
