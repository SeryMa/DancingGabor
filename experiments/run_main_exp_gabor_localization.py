import argparse
from typing import List, Tuple, Callable

import numpy as np
from numpy import ndarray

from base_experiment_settings import *
from generators.continuous_noise_generator import ContinuousNoiseGenerator
from generators.gabor_generator import GaborGenerator
from generators.patched_noise_generator import PatchedNoiseGenerator
from generators.pink_noise_generator import PinkNoise
from generators.single_noise_generator import SingleNoiseGenerator
from noise_processing.diff_noise_generator import DifferenceNoiseGenerator, PureDifferenceNoiseGenerator, \
    AvgDifferenceNoiseGenerator
from noise_processing.heat_map_generator import HeatMapGenerator
from outputs.video_output import VideoOutput
from utils.array import transform_to_probabilistic_distribution, value_fill
from utils.image import ssim, cw_ssim
from utils.patch_compare import PatchComparator
from utils.simple_functions import construct_file_name


def get_command_line_args():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp_name", default="test", type=str,
                        help="Name of the output files")

    parser.add_argument("--size", default=500, type=int, help="Size")
    parser.add_argument("--length", default=10, type=int, help="Length of observation")

    parser.add_argument("--patch_position", default=(0, 0), type=lambda x, y: (int(x), int(y)),
                        help="Position of the patch")

    parser.add_argument("--contrast", default=0.5, type=float, help="Contrast used to display patch")
    return parser.parse_args().__dict__


variants = ['D', 'S']
diff_methods = ['avg_diff', 'pure_diff', 'threshold_diff']
ssim_methods = ['pattern_ssim', 'true_ssim', 'true_cw_ssim']
all_methods = [*diff_methods, *ssim_methods]

# TODO: what percentiles to use
percentiles = [100, 99, 95, 90, 80, 70]

scene_size = 1000
length = 6
fps = 20
period = 2

granularity = 20

ppd = 50
patch_size_deg = 4

width = height = scene_size
patch_size = patch_size_deg * ppd

contrast = 0.5
patch_position = (scene_size // 4, scene_size // 4)
# patch_position = (0, 0)
shift_value = (scene_size // (length * 2), scene_size // (length * 2))


def add_diff_noise(noise_type, base_noise, secondary_outputs):
    if noise_type == 'pure_diff':
        noise = PureDifferenceNoiseGenerator(base_noise)
    elif noise_type == 'avg_diff':
        noise = AvgDifferenceNoiseGenerator(base_noise, period)
    elif noise_type == 'threshold_diff':
        noise = DifferenceNoiseGenerator(base_noise, period)
    else:
        return

    secondary_outputs.append((f'{noise_type}', noise.get_next_frame))

    def get_scene_properties():
        return {
            'diff_mean': noise.get_next_frame(0).mean(),
        }

    def get_window_diff(x1, x2, y1, y2, diff_mean):
        movement = np.abs(noise.get_next_frame(0)[x1:x2, y1:y2].mean() - diff_mean)
        return movement

    # secondary_outputs.append((f'{noise_type}_heat', heat_map.get_next_frame))
    return HeatMapGenerator(noise, window_size=patch_size, step=patch_size // 4,
                            aggregate_function=transform_to_probabilistic_distribution,
                            compute_cached_values=get_scene_properties,
                            process_function=get_window_diff)


def add_ssim_noise(noise_type, base_noise, get_patch=None):
    if noise_type == 'pattern_ssim':
        patch_comparator = PatchComparator(patch_size_deg, ppd, detect_gabor=True, granularity=granularities['middle'])

        def get_ssim(window):
            return patch_comparator.get_best_ssim_match(window)
    elif noise_type == 'true_ssim':
        def get_ssim(window):
            return ssim(window, get_patch(), alpha=0, beta=-0.5, gamma=0.5)

    elif noise_type == 'true_cw_ssim':
        def get_ssim(window):
            return cw_ssim(window, get_patch(), alpha=0, beta=-0.5, gamma=0.5)
    else:
        return

    def get_window_pattern_ssim(x1, x2, y1, y2):
        window = base_noise.get_next_frame(0)[x1:x2, y1: y2]

        if window.shape != (patch_size, patch_size):
            x = y = 0
            if window.shape[0] < patch_size and x1 == 0:
                x = patch_size // 2
            if window.shape[1] < patch_size and y1 == 0:
                y = patch_size // 2

            window = value_fill(window, x, y, (patch_size, patch_size), value=0)

        return get_ssim(window)

    # secondary_outputs.append((f'{noise_type}_heat', heat_map.get_next_frame))
    return HeatMapGenerator(base_noise, window_size=patch_size, step=patch_size // 4,
                            aggregate_function=transform_to_probabilistic_distribution,
                            process_function=get_window_pattern_ssim)


def add_noise(noise_type, secondary_outputs, base_noise, get_patch=None):
    if noise_type in diff_methods:
        return add_diff_noise(noise_type, base_noise, secondary_outputs)
    elif noise_type in ssim_methods:
        return add_ssim_noise(noise_type, base_noise, get_patch)
    else:
        raise ValueError(f'{noise_type} is not a valid noise type')


def run_experiment(exp_name, env, patch, position, methods=None):
    methods = methods if methods is not None else all_methods

    base_noise = SingleNoiseGenerator(width, height, PinkNoise(width, height)) \
        if env == 'S' else ContinuousNoiseGenerator(width, height, PinkNoise(width, height), period=period)

    update_list = [] if patch == 'S' else [
        *get_patch_value_updates('theta', patch_updates['theta']['middle']),
        *get_patch_value_updates('phase', patch_updates['phase']['middle']),
        *get_patch_value_updates('freq', patch_updates['freq']['slow'], initial_value=6),
    ]
    patch_generator = GaborGenerator(
        patch_size_deg=patch_size_deg,
        ppd=ppd,
        update_list=update_list)
    patch_shift = (0, 0) if position == 'S' else shift_value
    patch_position_updater = get_position_updater(patch_shift=patch_shift,
                                                  patch_position=patch_position)
    noise_with_gabor = PatchedNoiseGenerator(width, height, base_noise,
                                             [(patch_generator, patch_position_updater)],
                                             contrast=contrast)

    output_name = construct_file_name(exp_name)
    with open(output_name + '.log', 'w') as f:
        f.writelines([f'Log file for experiment {output_name}',
                      f'The experiment presents one gabor patch in pink noise scene.'
                      f'Scene: {"static" if env == "S" else "dynamic"}'
                      f'Position: {"static" if position == "S" else "dynamic"}'
                      f'Patch: {"static" if patch == "S" else "dynamic"}'
                      ])

    # The type is needed so PyCharm won't complain later
    secondary_outputs: List[Tuple[str, Callable[[int], ndarray]]] = []
    for method in methods:
        try:
            heat_map = add_noise(method,
                                 secondary_outputs=secondary_outputs,
                                 base_noise=noise_with_gabor,
                                 get_patch=patch_generator.get_normalized_patch
                                 )
        except ValueError:
            print('Invalid noise type added')
        else:
            secondary_outputs.append((f'{method}_heat', heat_map.get_next_frame))

    def update_all(dt=1):
        frame = noise_with_gabor.get_next_frame(dt)

        # Update secondary outputs that won't be updated by the VideoOutput
        for _, update_sec_output in secondary_outputs:
            update_sec_output(dt)

        return frame

    video_output = VideoOutput(update_all, width, height, secondary_outputs=secondary_outputs,
                               FPS=fps, length=length, video_name=output_name + ".avi")

    video_output.run()
    video_output.__del__()

    return output_name


def main():
    # variants = ['S']
    # all_methods = ['true_ssim']
    for env in variants:
        for patch in variants:
            for position in variants:
                exp_name = f'gabor_localization_{env}{patch}{position}'
                ch_dir('5_' + exp_name)

                run_experiment(exp_name, env, patch, position, all_methods)
                # plot_main(output, line_labels=percentiles, titles=all_methods)

                ch_dir('..')
                experiment_end()


if __name__ == '__main__':
    main()
