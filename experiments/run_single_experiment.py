import argparse

from generators.continuous_noise_generator import ContinuousNoiseGenerator
from generators.gabor_generator import GaborGenerator, PlaidGenerator
from generators.patched_noise_generator import PatchedNoiseGenerator
from generators.pink_noise_generator import PinkNoise
from generators.proper_pink_noise_generator import PinkNoise as PinkNoise2
from generators.running_pink_noise_generator import RunningPinkNoise
from noise_processing.diff_noise_generator import DifferenceNoiseGenerator
from noise_processing.noise_with_csv_output import NoiseGeneratorWithCSVOutput
from outputs.pyglet_app import PygletOutput
from outputs.video_output import VideoOutput
from utils.image import cw_ssim, ssim, luminance_comparison, contrast_comparison, structural_similarity, \
    phase_invariant_similarity
from utils.patch_compare import PatchComparator
from utils.simple_functions import construct_file_name
from utils.updater import LinUpdater


# noinspection PyTypeChecker
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


def get_patch_value_updates(theta_speed: float = None, phase_speed: float = None, freq_speed: float = None):
    update_list = []
    if theta_speed is not None:
        update_list.append(
            ('theta', LinUpdater(initial_value=0, time_step=theta_speed).update)
        )

    if phase_speed is not None:
        update_list.append(
            ('phase', LinUpdater(initial_value=0., time_step=phase_speed).update)
        )

    if freq_speed is not None:
        update_list.append(
            ('freq', LinUpdater(initial_value=6., time_step=freq_speed).update)
        )

    return update_list


def get_position_updater(patch_shift=(0, 0), patch_position=(0, 0)):
    if patch_shift[0] or patch_shift[1]:
        x_updater = LinUpdater(initial_value=patch_position[0], time_step=patch_shift[0])
        y_updater = LinUpdater(initial_value=patch_position[1], time_step=patch_shift[1])

        return lambda dt: (x_updater.update(dt), y_updater.update(dt))
    else:
        return lambda dt: patch_position


def get_patch_generator(gabor=True):
    return GaborGenerator if gabor else PlaidGenerator


def run_experiment(size=500, length=10, ppd=60, fps=30, exp_name='test', live=True, output_diff=False, delimiter=';',
                   gabor=True, alpha=1, beta=1, gamma=1,
                   theta_speed: int = None, phase_speed: int = None, freq_speed: int = None, patch_position=(0, 0),
                   patch_shift_x=0, patch_shift_y=0, contrast=0.5, period=1, output_values: [str] = None,
                   granularity=0):
    width = height = size

    if 'run' in exp_name:
        base_noise = RunningPinkNoise(width, height, period=period * length)
    elif 'v2' in exp_name:
        base_noise = PinkNoise2(width, height, length=length, deg=1 / 100)
    else:
        base_noise = ContinuousNoiseGenerator(width, height, PinkNoise(width, height), period=period)

    patch_constructor = get_patch_generator(gabor)
    patch_generator = patch_constructor(patch_size_deg=size / ppd,
                                        ppd=ppd,
                                        update_list=get_patch_value_updates(theta_speed,
                                                                            phase_speed,
                                                                            freq_speed))
    noise_with_gabor = PatchedNoiseGenerator(width,
                                             height,
                                             base_noise,
                                             [(patch_generator,
                                               get_position_updater((patch_shift_x, patch_shift_y), patch_position))],
                                             contrast=contrast)

    if output_diff:
        diff_noise = DifferenceNoiseGenerator(noise_with_gabor, period)
    else:
        diff_noise = None

    output_name = construct_file_name(exp_name)
    with open(output_name + '.log', 'w') as f:
        f.writelines([f'Log file for experiment {output_name}\n',
                      f'The experiment presents one big {"gabor" if gabor else "plaid"} patch in pink noise scene.\n'
                      f'New pink noise is generated every {period:.2f} s\n',

                      f'\nExperiment settings:\n',
                      f'Scene dimensions: {size}\n',
                      f'Length [s]: {length}\n',
                      f'FPS: {fps}\n',
                      f'PPD: {ppd}\n',
                      f'Contrast: {contrast:.2f}\n',
                      f'Patch position: {patch_position}\n',
                      f'Position update (x, y) [s^-1]: {(patch_shift_x, patch_shift_y)}\n',
                      f'Theta update [s^-1]: {theta_speed or 0:.2f}\n',
                      f'Phase update [s^-1]: {phase_speed or 0:.2f}\n',
                      f'Frequency update [s^-1]: {freq_speed or 0:.2f}\n',
                      ])

    output_values = [] if output_values is None else output_values
    fieldnames = []
    output_generators = []
    for output_value in output_values:
        output_value = output_value.lower()
        if output_value == 'luminance':
            fieldnames.extend([
                'compare_lum_gabor_noise_vs_gabor',
                'compare_lum_noise_vs_gabor',
                'compare_lum_gabor_noise_vs_noise'
            ])
            output_generators.extend([
                lambda: luminance_comparison(noise_with_gabor.get_next_frame(0),
                                             patch_generator.get_normalized_patch()),
                lambda: luminance_comparison(base_noise.get_next_frame(0),
                                             patch_generator.get_normalized_patch()),
                lambda: luminance_comparison(noise_with_gabor.get_next_frame(0),
                                             base_noise.get_next_frame(0)),
            ])
        elif output_value == 'contrast':
            fieldnames.extend([
                'compare_con_gabor_noise_vs_gabor',
                'compare_con_noise_vs_gabor',
                'compare_con_gabor_noise_vs_noise'
            ])
            output_generators.extend([
                lambda: contrast_comparison(noise_with_gabor.get_next_frame(0),
                                            patch_generator.get_normalized_patch()),
                lambda: contrast_comparison(base_noise.get_next_frame(0),
                                            patch_generator.get_normalized_patch()),
                lambda: contrast_comparison(noise_with_gabor.get_next_frame(0),
                                            base_noise.get_next_frame(0)),
            ])
        elif output_value == 'structure':
            fieldnames.extend([
                'compare_str_gabor_noise_vs_gabor',
                'compare_str_noise_vs_gabor',
                'compare_str_gabor_noise_vs_noise'
            ])
            output_generators.extend([
                lambda: structural_similarity(noise_with_gabor.get_next_frame(0),
                                              patch_generator.get_normalized_patch()),
                lambda: structural_similarity(base_noise.get_next_frame(0),
                                              patch_generator.get_normalized_patch()),
                lambda: structural_similarity(noise_with_gabor.get_next_frame(0),
                                              base_noise.get_next_frame(0)),
            ])
        elif output_value == 'cw_structure':
            fieldnames.extend([
                'compare_cw_str_gabor_noise_vs_gabor',
                'compare_cw_str_noise_vs_gabor',
                'compare_cw_str_gabor_noise_vs_noise'
            ])
            output_generators.extend([
                lambda: phase_invariant_similarity(noise_with_gabor.get_next_frame(0),
                                                   patch_generator.get_normalized_patch()),
                lambda: phase_invariant_similarity(base_noise.get_next_frame(0),
                                                   patch_generator.get_normalized_patch()),
                lambda: phase_invariant_similarity(noise_with_gabor.get_next_frame(0),
                                                   base_noise.get_next_frame(0)),
            ])
        elif output_value == 'ssim':
            fieldnames.extend([
                'ssim_gabor_noise_vs_gabor',
                'ssim_noise_vs_gabor',
                'ssim_gabor_noise_vs_noise'
            ])
            output_generators.extend([
                lambda: ssim(noise_with_gabor.get_next_frame(0),
                             patch_generator.get_normalized_patch(),
                             alpha, beta, gamma),
                lambda: ssim(base_noise.get_next_frame(0),
                             patch_generator.get_normalized_patch(),
                             alpha, beta, gamma),
                lambda: ssim(noise_with_gabor.get_next_frame(0),
                             base_noise.get_next_frame(0),
                             alpha, beta, gamma),
            ])
        elif output_value == 'cw_ssim':
            fieldnames.extend([
                'cw_ssim_gabor_noise_vs_gabor',
                'cw_ssim_noise_vs_gabor',
                'cw_ssim_gabor_noise_vs_noise'
            ])
            output_generators.extend([
                lambda: cw_ssim(noise_with_gabor.get_next_frame(0),
                                patch_generator.get_normalized_patch(),
                                alpha, beta, gamma),
                lambda: cw_ssim(base_noise.get_next_frame(0),
                                patch_generator.get_normalized_patch(),
                                alpha, beta, gamma),
                lambda: cw_ssim(noise_with_gabor.get_next_frame(0),
                                base_noise.get_next_frame(0),
                                alpha, beta, gamma),
            ])
        elif output_value == 'pattern_search_ssim' and granularity:
            simple_patch_comparator = PatchComparator(size / ppd, ppd, gabor, granularity=granularity,
                                                      alpha=alpha, beta=beta, gamma=gamma)

            fieldnames.extend([
                'simple_ssim_gabor_noise_vs_patch_search',
                'simple_ssim_noise_vs_patch_search',
                'simple_ssim_gabor_noise_vs_noise',
            ])
            output_generators.extend([
                lambda: simple_patch_comparator.get_best_ssim_match(noise_with_gabor.get_next_frame(0)),
                lambda: simple_patch_comparator.get_best_ssim_match(base_noise.get_next_frame(0)),
                lambda: ssim(noise_with_gabor.get_next_frame(0),
                             base_noise.get_next_frame(0),
                             alpha, beta, gamma)
            ])
        elif output_value == 'pattern_search_cw_ssim' and granularity:
            complex_patch_comparator = PatchComparator(size / ppd, ppd, gabor, granularity=granularity,
                                                       alpha=alpha, beta=beta, gamma=gamma, simple=False)
            fieldnames.extend([
                'cw_ssim_gabor_noise_vs_patch_search',
                'cw_ssim_noise_vs_patch_search',
                'cw_ssim_gabor_noise_vs_noise',
            ])
            output_generators.extend([
                lambda: complex_patch_comparator.get_best_ssim_match(noise_with_gabor.get_next_frame(0)),
                lambda: complex_patch_comparator.get_best_ssim_match(base_noise.get_next_frame(0)),
                lambda: cw_ssim(noise_with_gabor.get_next_frame(0),
                                base_noise.get_next_frame(0),
                                alpha, beta, gamma),
            ])
        elif output_value == 'diff' and output_diff:
            fieldnames.extend([
                'diff_gabor_noise_max',
                'diff_gabor_noise_min',
                'diff_gabor_noise_mean',
            ])
            # noinspection PyArgumentList
            output_generators.extend([
                lambda: diff_noise.get_next_frame(0).max(),
                lambda: diff_noise.get_next_frame(0).min(),
                lambda: diff_noise.get_next_frame(0).mean(),
            ])
        else:
            raise ValueError(f'{output_value} is not a valid output value')

    noise_generator = NoiseGeneratorWithCSVOutput(generator=diff_noise or noise_with_gabor,
                                                  file_name=output_name + ".csv",
                                                  field_names=fieldnames, output_generators=output_generators)

    if live:
        output = PygletOutput(noise_generator.get_next_frame, width, height)
    else:
        secondary_outputs = [('original', noise_with_gabor.get_next_frame)] if output_diff else []
        output = VideoOutput(noise_generator.get_next_frame, width, height, secondary_outputs=secondary_outputs,
                             FPS=fps, length=length, video_name=output_name + ".avi")

    output.run()
    hasattr(output, '__del__') and output.__del__()
    noise_generator.__del__()


if __name__ == '__main__':
    run_experiment(**get_command_line_args())
