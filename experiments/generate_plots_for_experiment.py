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

    for csv_file in [csv_file for csv_file in listdir(folder) if csv_file.endswith('.csv')]:
        create_graphs(len(titles),
                      [x for x in create_slice_indices(data_slices, initial_offset=1)],
                      labels, titles,
                      file_name=csv_file, live=live, delimiter=delimiter)


if __name__ == '__main__':
    generate_graphs(**get_command_line_args())
