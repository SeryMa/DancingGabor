from os import listdir

import numpy as np

from base_experiment_settings import get_position_updater
from experiments.graphs import plot_main
from experiments.run_main_exp_gabor_localization import variants, percentiles, length, patch_position, shift_value, \
    patch_size, NoiseGeneratorWithCSVOutput, ch_dir, experiment_end
from generators import VideoParsingGenerator


def evaluate_experiment(file_name, position):
    video_generator = VideoParsingGenerator(file_name, live=False)
    patch_shift = (0, 0) if position == 'S' else shift_value
    patch_position_updater = get_position_updater(patch_shift=patch_shift,
                                                  patch_position=patch_position)

    def evaluate_map(h_map: np.ndarray):
        out_correct = ''
        out_missed = ''
        x, y = np.rint(patch_position_updater(0)).astype('int')
        full_size = patch_size ** 2

        ps = np.percentile(h_map, percentiles)

        for p in ps:
            heat_mask = h_map >= p
            patch_mask = heat_mask[x:x + patch_size, y:y + patch_size]

            correct = np.sum(patch_mask)
            recall = correct / full_size
            out_correct += f'{recall};'

            false_positives = np.sum(heat_mask) - correct
            fpr = false_positives / (h_map.size - full_size)
            out_missed += f'{fpr};'

        return out_correct + out_missed

    # strip away the extension
    output_name = file_name[:-4]

    field_names = []
    csv_output_generators = []
    for p in percentiles:
        field_names.append(f'heat_correct_{p}_recall')

    for p in percentiles:
        field_names.append(f'heat_correct_{p}_fpr')

    # We have to drop the last delimiter or np.loadtxt will complain later
    csv_output_generators.append(lambda: evaluate_map(csv_generator.get_next_frame(0))[:-1])

    csv_generator = NoiseGeneratorWithCSVOutput(generator=video_generator,
                                                file_name=output_name + '.csv',
                                                field_names=field_names,
                                                output_generators=csv_output_generators)

    for i in range(30 * length):
        if i % 30 == 0:
            print(f'{i // 30}s out of {length}')

        dt = 1. / 30
        patch_position_updater(dt)
        csv_generator.get_next_frame(dt)


def main():
    # variants = ['S']
    # all_methods = ['true_ssim']
    for env in variants:
        for patch in variants:
            for position in variants:
                exp_name = f'gabor_localization_{env}{patch}{position}'

                ch_dir('5_' + exp_name)

                for heat_file in [all_files for all_files in listdir('.') if
                                  all_files.endswith('.avi') and 'heat' in all_files]:
                    # evaluate_experiment(heat_file, position)
                    output = heat_file[:-4]
                    plot_main(output, line_labels=[f'{p} percentile' for p in percentiles], titles=[exp_name])

                ch_dir('..')
                experiment_end()


if __name__ == '__main__':
    main()
