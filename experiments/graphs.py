import matplotlib.pyplot as plt
import numpy as np

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
    fig, axes = plt.subplots(plots, sharex='all', figsize=(15, 8))
    plt.subplots_adjust(left=0.08, right=0.8, hspace=0.4, top=0.92)

    # The xlabel must be set after creating the plt
    plt.xlabel('Time [s]')
    return fig, [axes] if plots == 1 else axes


def create_graphs(axes_count: int, axes_slices: [[int]], axes_labels: [[str]], axes_titles: [str], file_name='test',
                  delimiter=';', live=False):
    data = get_data(file_name + '.csv', delimiter)

    fig, all_axes = get_axes(axes_count)

    for ax, data_slice, labels, title in zip(all_axes, axes_slices, axes_labels, axes_titles):
        plot(ax, data[0], data[data_slice], labels=labels, title=title)

    if live:
        plt.show()
    else:
        plt.savefig(file_name + '.pdf')
        plt.savefig(file_name + '.png')

    plt.close(fig)
