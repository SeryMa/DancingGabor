import matplotlib.pyplot as plt
import numpy as np

from simple_functions import create_slice_indices

GRAPH_STYLE = {'marker': 'x', 'linestyle': 'dashed', 'markersize': 0.02}


def plot(axis, x, ys, title=''):
    for y in ys:
        axis.plot(x, y, **GRAPH_STYLE)

    axis.set_ylabel('Values')
    axis.set_title(title)
    # axis.legend()
    # axis.legend(fancybox=True, shadow=True, bbox_to_anchor=(1, .5), loc='center left', borderaxespad=0.)


def get_data(filename, delimiter=';'):
    return np.loadtxt(filename, delimiter=delimiter, skiprows=1).T


def get_axes(plots=3):
    # fig, axes = plt.subplots(plots, sharex='all', sharey='all', figsize=(10, 8))
    fig, axes = plt.subplots(plots, sharex='all', sharey='all', figsize=(11, 6))
    for ax in axes:
        ax.grid(True, linestyle='-')

    # The xlabel must be set after creating the plt
    plt.xlabel('Time [s]')
    return fig, [axes] if plots == 1 else axes


def create_graphs(axes_count: int, axes_slices: [[int]], axes_labels: [str], axes_titles: [str], file_name='test',
                  delimiter=';', live=False):
    data_file = file_name if file_name.endswith('.csv') else file_name + '.csv'
    output_file = file_name[:-4] if file_name.endswith('.csv') else file_name
    data = get_data(data_file, delimiter)

    fig, all_axes = get_axes(axes_count)
    plt.subplots_adjust(bottom=0.17, hspace=0.4, top=0.92)
    plt.setp(all_axes, yticks=np.arange(-0.2, 1.2, 0.2))

    for ax, data_slice, title in zip(all_axes, axes_slices, axes_titles):
        plot(ax, data[0], data[data_slice], title=title)

    fig.legend(axes_labels, loc='center', fancybox=True, shadow=True, bbox_to_anchor=(.512, 0.07), borderaxespad=0.)

    if live:
        plt.show()
    else:
        plt.savefig(output_file + '.pdf')
        plt.savefig(output_file + '.png')

    plt.close(fig)


def plot_main(file_name, titles, line_labels, delimiter=';', live=False):
    axes_titles = ['Recall', 'FPR']

    data = get_data(file_name + '.csv', delimiter)

    for title in titles:
        fig, all_axes = get_axes(len(axes_titles))
        plt.subplots_adjust(bottom=0.17, top=0.92)
        plt.setp(all_axes, yticks=np.arange(0.0, 1.2, 0.2))
        plt.ylim(bottom=-0.2, top=1.2)

        for ax, ax_title, data_slice in zip(all_axes, axes_titles, [x for x in create_slice_indices(
                [len(line_labels) for _ in axes_titles], initial_offset=1)]):
            plot(ax, data[0], data[data_slice], title=ax_title)

        fig.legend(line_labels, loc='center', ncol=3, fancybox=True, shadow=True, bbox_to_anchor=(.512, 0.07),
                   borderaxespad=0.)

        if live:
            plt.show()
        else:
            plt.savefig(f'{file_name}_{title}.pdf')
            plt.savefig(f'{file_name}_{title}.png')

        plt.close(fig)
