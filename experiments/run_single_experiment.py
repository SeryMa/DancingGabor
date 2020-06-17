import argparse

from experiments.graphs import create_graphs
from generators.continuous_noise_generator import ContinuousNoiseGenerator
from generators.gabor_generator import GaborGenerator, PlaidGenerator
from generators.patched_noise_generator import PatchedNoiseGenerator
from generators.pink_noise_generator import PinkNoise
from noise_processing.diff_noise_generator import DifferenceNoiseGenerator
from noise_processing.noise_with_csv_output import NoiseGeneratorWithCSVOutput
from outputs.pyglet_app import PygletOutput
from outputs.video_output import VideoOutput
from utils.image import get_rms_contrast, get_luminance, ssim
from utils.patch_compare import PatchComparator
from utils.simple_functions import construct_file_name, create_slice_indices
from utils.updater import LinUpdater


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
            ('phase', LinUpdater(initial_value=0.00, time_step=phase_speed).update)
        )

    if freq_speed is not None:
        update_list.append(
            ('freq', LinUpdater(initial_value=0.00, time_step=freq_speed).update)
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


def run_experiment(size=500, length=10, ppd=80, exp_name='test', live=True, output_diff=False, delimiter=';',
                   gabor=True,
                   theta_speed: int = None, phase_speed: int = None, freq_speed: int = None, patch_position=(0, 0),
                   patch_shift_x=0, patch_shift_y=0, contrast=0.5, period=1, output_values: [str] = None,
                   granularity=0):
    width = height = size

    base_noise = ContinuousNoiseGenerator(width, height, PinkNoise(width, height), period=period)
    patch_generator = get_patch_generator(gabor)(patch_size_deg=size / ppd, ppd=ppd,
                                                 update_list=get_patch_value_updates(theta_speed, phase_speed,
                                                                                     freq_speed))
    noise_with_gabor = PatchedNoiseGenerator(width, height, base_noise, [(patch_generator, get_position_updater())],
                                             contrast=contrast)

    if output_diff:
        diff_noise = DifferenceNoiseGenerator(noise_with_gabor, period)
    else:
        diff_noise = None

    output_name = construct_file_name(exp_name)
    with open(output_name + '.log', 'w') as f:
        f.writelines([f'Log file for experiment {output_name}',
                      f'The experiment presents one big {"gabor" if gabor else "plaid"} patch in pink noise scene. '
                      f'New pink noise is generated every {period:.2f} s',
                      f'Experiment settings:',
                      f'Scene dimensions: {size}',
                      f'Length [s]: {length}',
                      f'Contrast: {contrast:.2f}',
                      f'Patch position: {patch_position}',
                      f'Position update (x, y) [s^-1]: {(patch_shift_x, patch_shift_y)}',
                      f'Theta update [s^-1]: {theta_speed or 0:.2f}',
                      f'Phase update [s^-1]: {phase_speed or 0:.2f}',
                      f'Frequency update [s^-1]: {freq_speed or 0:.2f}',
                      ])

    output_values = ['Luminance', 'Contrast', 'SSIM'] if output_values is None else output_values
    fieldnames = []
    output_generators = []
    data_slices = []
    base_labels = ['Noise with gabor', 'Noise without gabor', 'Gabor']
    labels = []
    titles = []
    for output_value in output_values:
        titles.append(f'{output_value} values')
        output_value = output_value.lower()
        if output_value == 'luminance':
            fieldnames.extend([
                'luminance_with_gabor',
                'luminance_without_gabor',
                'luminance_gabor',
            ])
            output_generators.extend([
                lambda: get_luminance(noise_with_gabor.get_next_frame(0)),
                lambda: get_luminance(base_noise.get_next_frame(0)),
                lambda: get_luminance(patch_generator.get_normalized_patch()),
            ])
            data_slices.append(3)
            labels.append(base_labels)
        elif output_value == 'contrast':
            fieldnames.extend([
                'contrast_with_gabor',
                'contrast_without_gabor',
                'contrast_gabor',
            ])
            output_generators.extend([
                lambda: get_rms_contrast(noise_with_gabor.get_next_frame(0)),
                lambda: get_rms_contrast(base_noise.get_next_frame(0)),
                lambda: get_rms_contrast(patch_generator.get_normalized_patch()),
            ])
            data_slices.append(3)
            labels.append(base_labels)
        elif output_value == 'ssim':
            fieldnames.extend([
                'ssim_gabor_noise_vs_gabor',
                'ssim_noise_vs_gabor',
            ])
            output_generators.extend([
                lambda: ssim(noise_with_gabor.get_next_frame(0),
                             patch_generator.get_normalized_patch()),
                lambda: ssim(base_noise.get_next_frame(0),
                             patch_generator.get_normalized_patch()),
            ])
            data_slices.append(2)
            labels.append(base_labels[0:2])
        elif output_value == 'full_ssim' and granularity:
            patch_comparator = PatchComparator(size / ppd, ppd, gabor, granularity=granularity)

            fieldnames.extend([
                'ssim_gabor_noise_vs_gabor',
                'ssim_noise_vs_gabor',
                'ssim_gabor_noise_vs_patch_search',
                'ssim_noise_vs_patch_search',
            ])
            output_generators.extend([
                lambda: ssim(noise_with_gabor.get_next_frame(0),
                             patch_generator.get_normalized_patch()),
                lambda: ssim(base_noise.get_next_frame(0),
                             patch_generator.get_normalized_patch()),
                lambda: patch_comparator.get_best_ssim_match(noise_with_gabor.get_next_frame(0)),
                lambda: patch_comparator.get_best_ssim_match(base_noise.get_next_frame(0)),
            ])
            data_slices.append(4)
            labels.append(base_labels[0:2] + base_labels[0:2])
        elif output_value == 'diff' and output_diff:
            fieldnames.extend([
                'diff_gabor_noise_max',
                'diff_gabor_noise_min',
                'diff_gabor_noise_mean',
            ])
            output_generators.extend([
                lambda: diff_noise.get_next_frame(0).max(),
                lambda: diff_noise.get_next_frame(0).min(),
                lambda: diff_noise.get_next_frame(0).mean(),
            ])
            data_slices.append(3)
            labels.append(['Diff max', 'Diff min', 'Diff mean'])
        else:
            raise ValueError(f'{output_value} is not a valid output value')

    noise_generator = NoiseGeneratorWithCSVOutput(generator=diff_noise or noise_with_gabor,
                                                  file_name=output_name + ".csv",
                                                  fieldnames=fieldnames, output_generators=output_generators)

    if live:
        output_values = PygletOutput(noise_generator.get_next_frame, width, height)
    else:
        secondary_outputs = [('original', noise_with_gabor.get_next_frame)] if output_diff else []
        output_values = VideoOutput(noise_generator.get_next_frame, width, height, secondary_outputs=secondary_outputs,
                                    FPS=50, length=length, video_name=output_name + ".avi")

    output_values.run()
    hasattr(output_values, '__del__') and output_values.__del__()
    noise_generator.__del__()

    # GRAPHS part starts here!
    create_graphs(len(titles), [x for x in create_slice_indices(data_slices, initial_offset=1)], labels, titles,
                  file_name=output_name, live=live, delimiter=delimiter)


if __name__ == '__main__':
    run_experiment(**get_command_line_args())
