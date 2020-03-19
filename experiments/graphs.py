import argparse

import matplotlib.pyplot as plt
import numpy as np


def get_command_line_args():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_name", default='output.csv', type=str, help="File name of the csv file")
    parser.add_argument("--delimiter", default=';', type=str, help="Value delimiter")
    return parser.parse_args().__dict__


GRAPH_STYLE = {'marker': 'x', 'linestyle': 'dashed', 'markersize': 0.02}


def plot(axis, x, ys, labels=None, title=''):
    if labels is None:
        labels = []

    for y, label in zip(ys, labels):
        axis.plot(x, y, label=label, **GRAPH_STYLE)

    axis.set_ylabel('Values')
    axis.set_title(title)
    # axis.legend()
    axis.legend(fancybox=True, shadow=True, bbox_to_anchor=(1, .5), loc='center left', borderaxespad=0.)


def get_data(filename, delimiter=';'):
    return np.loadtxt(filename, delimiter=delimiter, skiprows=1).T


def get_axes(plots=3):
    ret = plt.subplots(plots, sharex='all', figsize=(15, 8))
    plt.subplots_adjust(left=0.08, right=0.8, hspace=0.4, top=0.92)

    # The xlabel must be set after creating the plt
    plt.xlabel('Time [s]')
    return ret


if __name__ == '__main__':
    args = get_command_line_args()
    filename = args['file_name']
    delimiter = args['delimiter']

    data = get_data(filename, delimiter)
    fig, (ax1, ax2, ax3) = get_axes()

    # luminance plot:
    plot(ax1, data[0], [data[1], data[3], data[5]], labels=['Noise with gabor', 'Noise without gabor', 'Gabor'],
         title='Luminance values')

    # contrast plot
    plot(ax2, data[0], [data[2], data[4], data[6]], labels=['Noise with gabor', 'Noise without gabor', 'Gabor'],
         title='Contrast values')

    # SSIM
    plot(ax3, data[0], [data[7], data[8]], labels=['SSIM - noise vs gabor', 'SSIM - gabor noise vs gabor'],
         title='SSIM values')

    plt.show()
