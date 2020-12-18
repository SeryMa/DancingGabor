import argparse
from os import listdir

from experiments.graphs import create_graphs
from utils.simple_functions import create_slice_indices


# noinspection PyTypeChecker
def get_command_line_args():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", default=".", type=str, help="Folder of the experiment")
    parser.add_argument("--save", dest='live', help="Should save the plots rather than showing them",
                        action='store_false')
    parser.add_argument("--live", dest='live', help="Should display the plots rather than saving them",
                        action='store_true')
    parser.add_argument("--delimiter", default=';', type=str, help="CSV value delimiter")
    parser.add_argument("output_values", metavar='output_value', type=str, nargs='+', help="Output values to plot")
    return parser.parse_args().__dict__


def generate_graphs(folder='.', output_values: [str] = None, live=True, delimiter=';'):
    output_values = [] if output_values is None else output_values
    fieldnames = []
    data_slices = []
    base_labels = ['Gabor noise vs Gabor', 'Noise vs Gabor', 'Gabor noise vs Noise']
    labels = []
    titles = []
    for output_value in output_values:
        titles.append(f'{output_value} values')
        output_value = output_value.lower()

        data_slices.append(3)
        if output_value == 'diff':
            labels.append(['Diff max', 'Diff min', 'Diff mean'])
        else:
            labels.append(base_labels)

        if output_value == 'luminance':
            fieldnames.extend([
                'compare_lum_gabor_noise_vs_gabor',
                'compare_lum_noise_vs_gabor',
                'compare_lum_gabor_noise_vs_noise'
            ])
        elif output_value == 'contrast':
            fieldnames.extend([
                'compare_con_gabor_noise_vs_gabor',
                'compare_con_noise_vs_gabor',
                'compare_con_gabor_noise_vs_noise'
            ])
        elif output_value == 'structure':
            fieldnames.extend([
                'compare_str_gabor_noise_vs_gabor',
                'compare_str_noise_vs_gabor',
                'compare_str_gabor_noise_vs_noise'
            ])
        elif output_value == 'ssim':
            fieldnames.extend([
                'ssim_gabor_noise_vs_gabor',
                'ssim_noise_vs_gabor',
                'ssim_gabor_noise_vs_noise'
            ])
        elif output_value == 'cw_ssim':
            fieldnames.extend([
                'cw_ssim_gabor_noise_vs_gabor',
                'cw_ssim_noise_vs_gabor',
                'cw_ssim_gabor_noise_vs_noise'
            ])
        elif output_value == 'pattern_search_ssim':
            fieldnames.extend([
                'simple_ssim_gabor_noise_vs_patch_search',
                'simple_ssim_noise_vs_patch_search',
                'simple_ssim_gabor_noise_vs_noise',
            ])
        elif output_value == 'pattern_search_cw_ssim':
            fieldnames.extend([
                'cw_ssim_gabor_noise_vs_patch_search',
                'cw_ssim_noise_vs_patch_search',
                'cw_ssim_gabor_noise_vs_noise',
            ])
        elif output_value == 'diff':
            fieldnames.extend([
                'diff_gabor_noise_max',
                'diff_gabor_noise_min',
                'diff_gabor_noise_mean',
            ])
        else:
            raise ValueError(f'{output_value} is not a valid output value')

    for csv_file in [csv_file for csv_file in listdir(folder) if csv_file.endswith('.csv')]:
        create_graphs(len(titles),
                      [x for x in create_slice_indices(data_slices, initial_offset=1)],
                      labels, titles,
                      file_name=csv_file, live=live, delimiter=delimiter)


if __name__ == '__main__':
    generate_graphs(**get_command_line_args())
