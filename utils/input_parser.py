from generators.circular_noise_generator import *
from generators.continuous_noise_generator import *
from generators.gabor_generator import *
from generators.patched_noise_generator import *
from generators.pink_noise_generator import *
from generators.single_color_generator import *
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
    return lambda dt: updater.update(dt)


def get_noise(width, height, **kwargs):
    if 'white' in kwargs:
        return WhiteNoise(width, height)

    elif 'pink' in kwargs:
        return PinkNoise(width, height, **kwargs['pink'])

    elif 'single' in kwargs:
        return SingleColor(width, height, **kwargs['single'])

    elif 'continuous' in kwargs:
        specs = kwargs['continuous']
        generator = get_noise(width, height, **specs)

        if 'interpolation' not in kwargs or specs['interpolation'] == 'simple':
            interpolation = interpolate
        else:
            raise ValueError(
                f"The interpolation function {specs['interpolation']} wasn't recognized. Try using 'simple' instead")

        return ContinuousNoiseGenerator(width, height, generator=generator, interpolation=interpolation, **specs)

    elif 'circular' in kwargs:
        specs = kwargs['circular']
        generator = get_noise(width, height, **specs)

        if 'interpolation' not in specs or specs['interpolation'] == 'simple':
            interpolation = interpolate
        else:
            raise ValueError(f"The interpolation function {specs['interpolation']} wasn't recognized. Try using 'simple' instead")

        return CircularNoiseGenerator(width, height, generator=generator, interpolation=interpolation, **specs)

    elif 'patched' in kwargs:
        specs = kwargs['patched']
        generator = get_noise(width, height, **specs)

        patch_generators = []
        for patch in specs['patches']:
            patch_generators.append((
                get_noise(width, height, **patch),
                get_position_updater(**patch)
            ))

        return PatchedNoiseGenerator(width, height, generator=generator, patch_generators=patch_generators, **specs)

    elif 'gabor' in kwargs:
        specs = kwargs['gabor']
        update_list = []
        if 'updates' in specs:
            for patch in specs['updates']:
                update_list.append((
                    patch['value'],
                    get_value_updater(**patch)
                ))

        return GaborGenerator(update_list=update_list, **specs)

    elif 'plaid' in kwargs:
        specs = kwargs['plaid']
        update_list = []
        if 'updates' in specs:
            for patch in specs['updates']:
                update_list.append((
                    patch['value'],
                    get_value_updater(**patch)
                ))

        return PlaidGenerator(update_list=update_list, **specs)

    else:
        raise ValueError(f"Any noise type wasn't recognized.")
