import argparse

import numpy as np

from base_experiment_settings import *
from generators.continuous_noise_generator import ContinuousNoiseGenerator
from generators.gabor_generator import GaborGenerator
from generators.patched_noise_generator import PatchedNoiseGenerator
from generators.pink_noise_generator import PinkNoise
from noise_processing.diff_noise_generator import DifferenceNoiseGenerator, PureDifferenceNoiseGenerator, \
    AvgDifferenceNoiseGenerator
from noise_processing.heat_map_generator import HeatMapGenerator
from outputs.video_output import VideoOutput
from utils.array import transform_to_probabilistic_distribution, value_fill
from utils.image import ssim
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


scene_size = 1000
length = 10
fps = 30
period = 2

granularity = 20

ppd = 50
patch_size_deg = 4
contrast = 0.5
patch_position = (scene_size // 2, scene_size // 2)
# patch_position = (0, 0)
patch_shift = (0, 0)


def run_experiment(exp_name,
                   theta_speed: int = None,
                   phase_speed: int = None,
                   freq_speed: int = None, ):
    width = height = scene_size

    base_noise = ContinuousNoiseGenerator(width, height, PinkNoise(width, height), period=period)
    update_list = [] if theta_speed is None else [
        *get_patch_value_updates('theta', theta_speed),
        *get_patch_value_updates('phase', phase_speed),
        *get_patch_value_updates('freq', freq_speed, initial_value=6),
    ]
    patch_generator = GaborGenerator(
        patch_size_deg=patch_size_deg,
        ppd=ppd,
        update_list=update_list)
    noise_with_gabor = PatchedNoiseGenerator(width, height, base_noise,
                                             [(patch_generator, get_position_updater(patch_position=patch_position))],
                                             contrast=contrast)

    patch_size = patch_size_deg * ppd

    # TODO: tmp variable to be used in later check
    diff_noise = None
    if 'ssim' in exp_name:
        if 'true' in exp_name:
            def get_ssim(window):
                return ssim(window, patch_generator.get_normalized_patch(), alpha=0, beta=-0.5, gamma=0.5)
        else:
            patch_comparator = PatchComparator(patch_size_deg, ppd, detect_gabor=True, granularity=granularities)

            def get_ssim(window):
                return patch_comparator.get_best_ssim_match(window)

        def get_window_ssim(x1, x2, y1, y2):
            window = noise_with_gabor.get_next_frame(0)[x1:x2, y1: y2]

            if window.shape != (patch_size, patch_size):
                x = y = 0
                if window.shape[0] < patch_size and x1 == 0:
                    x = patch_size // 2
                if window.shape[1] < patch_size and y1 == 0:
                    y = patch_size // 2

                window = value_fill(window, x, y, (patch_size, patch_size), value=0)

            return get_ssim(window)

        heat_map = HeatMapGenerator(noise_with_gabor, window_size=patch_size,
                                    aggregate_function=transform_to_probabilistic_distribution,
                                    process_function=get_window_ssim)

    else:
        def get_window_diff(x1, x2, y1, y2, diff_mean):
            movement = np.abs(diff_noise.get_next_frame(0)[x1:x2, y1:y2].mean() - diff_mean)
            return movement

        def get_scene_properties():
            return {
                'diff_mean': diff_noise.get_next_frame(0).mean(),
            }

        if 'pure' in exp_name:
            diff_noise = PureDifferenceNoiseGenerator(noise_with_gabor)
        elif 'avg' in exp_name:
            diff_noise = AvgDifferenceNoiseGenerator(noise_with_gabor, period)
        else:
            diff_noise = DifferenceNoiseGenerator(noise_with_gabor, period)

        heat_map = HeatMapGenerator(diff_noise, window_size=patch_size,
                                    aggregate_function=transform_to_probabilistic_distribution,
                                    compute_cached_values=get_scene_properties,
                                    process_function=get_window_diff)

    output_name = construct_file_name(exp_name)
    with open(output_name + '.log', 'w') as f:
        f.writelines([f'Log file for experiment {output_name}',
                      f'The experiment presents one gabor patch in pink noise scene. '
                      f'New pink noise is generated every {period:.2f} s',
                      f'PPD: {ppd}',
                      f'Experiment settings:',
                      f'Scene dimensions: {scene_size}',
                      f'Length [s]: {length}',
                      f'Contrast: {contrast:.2f}',
                      f'Patch position: {patch_position}',
                      f'Patch size [deg]: {patch_size_deg}',
                      f'Position update (x, y) [s^-1]: {patch_shift}',
                      f'Theta update [s^-1]: {theta_speed or 0:.2f}',
                      f'Phase update [s^-1]: {phase_speed or 0:.2f}',
                      f'Frequency update [s^-1]: {freq_speed or 0:.2f}',
                      ])

    secondary_outputs = [('original', noise_with_gabor.get_next_frame)]
    if diff_noise is not None:
        secondary_outputs.append(('diff', diff_noise.get_next_frame))

    video_output = VideoOutput(heat_map.get_next_frame, width, height, secondary_outputs=secondary_outputs,
                               FPS=fps, length=length, video_name=output_name + ".avi")

    video_output.run()
    video_output.__del__()


def main():
    for exp in [
        'static_gabor',
        'avg_diff',
        'pure_diff',
        'static_gabor_avg_diff',
        'threshold',
        'ref_ssim',
        'ssim',
        'true_ssim'
    ]:
        ch_dir(f'gabor_localization_{exp}')

        if 'static_gabor' in exp:
            settings = {}
        else:
            settings = {
                'phase_speed': patch_updates['phase']['middle'],
                'freq_speed': patch_updates['freq']['slow'],
                'theta_speed': patch_updates['theta']['middle'],
            }

        run_experiment(exp_name=f'exp_{exp}', **settings)

        ch_dir('..')

    experiment_end()


if __name__ == '__main__':
    main()
