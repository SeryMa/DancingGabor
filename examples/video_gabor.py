import argparse

from numpy import pi

from base_experiment_settings import *
from generators.gabor_generator import GaborGenerator
from generators.patched_noise_generator import PatchedNoiseGenerator
from generators.proper_pink_noise_generator import PinkNoise as DynamicPinkNoise
from noise_processing import AvgDifferenceNoiseGenerator
from outputs.video_output import VideoOutput

base_size = 500


def get_command_line_args():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", default=base_size, type=int, help="Size")

    parser.add_argument("--patch_position", default=(base_size // 2, base_size // 2),
                        type=lambda x, y: (int(x), int(y)),
                        help="Position of the patch")

    parser.add_argument("--theta_speed", default=None, type=int, help="Speed of change for theta")
    parser.add_argument("--freq_speed", default=None, type=int, help="Speed of change for frequency")
    parser.add_argument("--phase_speed", default=None, type=int, help="Speed of change for phase")

    parser.add_argument("--contrast", default=0.5, type=float, help="Contrast used to display patch")
    return parser.parse_args().__dict__


period = 5

ppd = 30
patch_size_deg = 2
contrast = 0.5
patch_shift = (0, 0)

if __name__ == '__main__':
    args = get_command_line_args()
    width = height = args['size']
    patch_position = args['patch_position']

    fps = 30
    length = 10
    deg = 1 / 100

    # base_noise = ContinuousNoiseGenerator(width, height, PinkNoise(width, height), period=period)
    base_noise = DynamicPinkNoise(width, height, length=length, fps=fps, deg=deg)
    # base_noise = RunningPinkNoise(width, height, period * 20)
    patch_generator = GaborGenerator(
        patch_size_deg=patch_size_deg,
        ppd=ppd,
        theta=90,
        # update_list=get_patch_value_updates(args['theta_speed'], args['phase_speed'], args['freq_speed']))
        update_list=get_patch_value_updates('phase', -pi / 10)
    )
    noise_with_gabor = PatchedNoiseGenerator(width, height, base_noise,
                                             [(patch_generator,
                                               get_position_updater(patch_shift=patch_shift,
                                                                    patch_position=patch_position))],
                                             contrast=contrast)
    # diff_noise = PureDifferenceNoiseGenerator(noise_with_gabor)
    # diff_noise = DifferenceNoiseGenerator(noise_with_gabor, period)
    diff_noise = AvgDifferenceNoiseGenerator(noise_with_gabor, period)

    # noise_generator = noise_with_gabor
    # noise_generator = diff_noise
    noise_generator = base_noise

    output = VideoOutput(noise_generator.get_next_frame, width, height, length=length, video_name=f'test3_d{deg}.avi')
    output.run()
