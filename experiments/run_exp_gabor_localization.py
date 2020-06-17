import argparse

from experiments.base_experiment_settings import *
from experiments.run_single_experiment import get_patch_value_updates, get_position_updater, get_patch_generator
from generators.continuous_noise_generator import ContinuousNoiseGenerator
from generators.patched_noise_generator import PatchedNoiseGenerator
from generators.pink_noise_generator import PinkNoise
from noise_processing.diff_noise_generator import DifferenceNoiseGenerator
from noise_processing.heat_map_generator import HeatMapGenerator
from outputs.video_output import VideoOutput
from utils.array import transform_to_probabilistic_distribution
from utils.image import get_rms_contrast
from utils.patch_compare import PatchComparator
from utils.simple_functions import construct_file_name


def get_command_line_args():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp_name", default="test", type=str,
                        help="Name of the output files")

    parser.add_argument("--size", default=500, type=int, help="Size")
    parser.add_argument("--length", default=10, type=int, help="Length of observation")

    parser.add_argument("--patch_position", default=(0, 0), type=(int, int), help="Position of the patch")

    parser.add_argument("--contrast", default=0.5, type=float, help="Contrast used to display patch")

    parser.add_argument("--live", default=True, type=bool, help="Should live preview be shown")
    parser.add_argument("--delimiter", default=';', type=str, help="CSV value delimiter")
    return parser.parse_args().__dict__


def run_experiment(scene_size=500, length=10, ppd=30, exp_name='test', gabor=True,
                   theta_speed: int = None, phase_speed: int = None, freq_speed: int = None,
                   patch_position=(0, 0), patch_shift=(0, 0), patch_size_deg=2,
                   contrast=0.5, period=1, granularity=0):
    width = height = scene_size

    base_noise = ContinuousNoiseGenerator(width, height, PinkNoise(width, height), period=period)
    patch_generator = get_patch_generator(gabor)(patch_size_deg=patch_size_deg, ppd=ppd,
                                                 update_list=get_patch_value_updates(theta_speed, phase_speed,
                                                                                     freq_speed))
    noise_with_gabor = PatchedNoiseGenerator(width, height, base_noise,
                                             [(patch_generator, get_position_updater(patch_position=patch_position))],
                                             contrast=contrast)
    diff_noise = DifferenceNoiseGenerator(noise_with_gabor, period)

    patch_comparator = PatchComparator(patch_size_deg, ppd, gabor, granularity=granularity)

    patch_size = patch_size_deg * ppd

    def process_function(x1, x2, y1, y2, scene_contrast, diff_mean):
        # window = noise_with_gabor.get_next_frame(0)[x1:x2, y1: y2]
        #
        # if window.shape != (patch_size, patch_size):
        #     x = y = 0
        #     if window.shape[0] < patch_size and x1 == 0:
        #         x = patch_size // 2
        #     if window.shape[1] < patch_size and y1 == 0:
        #         y = patch_size // 2
        #
        #     window = value_fill(window, x, y, (patch_size, patch_size), value=0)

        # ssim = patch_comparator.get_best_ssim_match(window)
        # contrast_diff = get_rms_contrast(window) - scene_contrast
        movement = diff_noise.get_next_frame(0)[x1:x2, y1:y2].max() - diff_mean

        # return [ssim, contrast_diff, movement]
        return movement

    def get_scene_properties():
        return {
            'scene_contrast': get_rms_contrast(noise_with_gabor.get_next_frame(0)),
            'diff_mean': diff_noise.get_next_frame(0).mean(),
        }

    heat_map = HeatMapGenerator(diff_noise, window_size=patch_size,
                                aggregate_funciton=transform_to_probabilistic_distribution,
                                compute_cached_values=get_scene_properties,
                                process_function=process_function)

    output_name = construct_file_name(exp_name)
    with open(output_name + '.log', 'w') as f:
        f.writelines([f'Log file for experiment {output_name}',
                      f'The experiment presents one big {"gabor" if gabor else "plaid"} patch in pink noise scene. '
                      f'New pink noise is generated every {period:.2f} s',
                      f'Experiment settings:',
                      f'Scene dimensions: {scene_size}',
                      f'Length [s]: {length}',
                      f'Contrast: {contrast:.2f}',
                      f'Patch position: {patch_position}',
                      f'Position update (x, y) [s^-1]: {patch_shift}',
                      f'Theta update [s^-1]: {theta_speed or 0:.2f}',
                      f'Phase update [s^-1]: {phase_speed or 0:.2f}',
                      f'Frequency update [s^-1]: {freq_speed or 0:.2f}',
                      ])

    secondary_outputs = [('original', noise_with_gabor.get_next_frame)]
    video_output = VideoOutput(heat_map.get_next_frame, width, height, secondary_outputs=secondary_outputs,
                               FPS=50, length=length, video_name=output_name + ".avi")

    video_output.run()
    video_output.__del__()


if __name__ == '__main__':
    # run_experiment(**get_command_line_args())

    ch_dir()
    ch_dir('gabor_localization')

    for patch_update in patch_updates:
        settings = {
            f'{patch_update}_speed': patch_updates[patch_update]['middle'],
        }

        run_experiment(scene_size=base_size,
                       length=5,
                       exp_name=f'patch_{patch_update}_granularity_20',
                       granularity=20,
                       patch_position=(base_size // 2, base_size // 2),
                       **settings)

        experiment_end()
