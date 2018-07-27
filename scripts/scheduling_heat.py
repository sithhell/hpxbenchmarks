#!/usr/bin/env python

import sys
import json
from pprint import pprint

import numpy as np
from matplotlib import cm
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.colors as colors
from mpl_toolkits.axes_grid1 import make_axes_locatable
import os

if len(sys.argv) < 2:
    print('Usage: %s <results_base> sub_dirs...' % sys.argv[0])
    sys.exit(1)

results_base = sys.argv[1]

print('Analyzing results in %s' % results_base)

results = []
if len(sys.argv) == 2:
    results = [os.path.join(results_base, f) for f in os.listdir(results_base)
            if os.path.isdir(os.path.join(results_base, f))]
else:
    results = [os.path.join(results_base, f) for f in sys.argv[2:]]

pprint(results)

data = []

# load data ...
# data is accessed as:
# data[runtime][threads][granularity]
num_tasks = '1000' # could be 0, 10 or 100 as well...
granularities = [
    '1000/100000',
    #'1/10000',
    #'10/10000',
    #'100/10000',
    '1000/10000',
    #'1/1000',
    #'10/1000',
    #'100/1000',
    '1000/1000',
    #'1/100',
    #'10/100',
    #'100/100',
    '1000/100',
    #'1/10',
    #'10/10',
    #'100/10',
    #'1000/10',
    #'1/1',
    #'10/1',
    #'100/1',
    #'1000/1',
    #'1/0',
    #'10/0',
    #'100/0',
    '1000/0',
]


runtimes = ('seq', 'hpx', 'omp_for', 'omp_task', 'std')

max_speedup = 0
max_thread = 0

for results_dir in results:
    name = os.path.split(results_dir)[-1]
    times = {}
    thread_nums = []
    for runtime in runtimes:
        times[runtime] = []
        for threads in range(1, 17):
            try:
                if runtime == 'omp_for':
                    jdata = json.load(open('%s/scheduling/%s_scheduling_t%s.json' % (results_dir, 'omp', threads)))
                elif runtime == 'omp_task':
                    jdata = json.load(open('%s/scheduling/%s_scheduling_t%s.json' % (results_dir, 'omp', threads)))
                else:
                    jdata = json.load(open('%s/scheduling/%s_scheduling_t%s.json' % (results_dir, runtime, threads)))

                if not threads in thread_nums:
                    t = int(threads)
                    if t > max_thread:
                        max_thread = t
                    thread_nums.append(t)

                thread_times = []

                if runtime == 'omp_for':
                    base_name = 'omp_homogeneous_for'
                elif runtime == 'omp_task':
                    base_name = 'omp_homogeneous_seq'
                else:
                    base_name = jdata['benchmarks'][0]['name'].split('/')[0]

                for granularity in granularities:
                    time = float((x for x in jdata['benchmarks']
                        if x['name'] == '%s/%s/real_time' % (base_name, granularity)).next()['real_time'])
                    thread_times.append(time)
                if runtime == 'seq':
                    times[runtime].append(np.array(thread_times))
                else:
                    times[runtime].append(times['seq'][0] / np.array(thread_times))
                    this_max = np.max(times[runtime][-1])
                    if this_max > max_speedup:
                        max_speedup = this_max
                    #max_speedup = np.max(np.max(times[runtime][-1]), max_speedup)

            except:
                break
    print(name, len(times), len(thread_nums))
    data.append((name, max_speedup, thread_nums, times))
    max_speedup=0


print(max_speedup)

#pprint(data)

class MidpointNormalize(colors.Normalize):
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))

pgf_with_latex = {
    "pgf.texsystem": "xelatex",         # use Xelatex which is TTF font aware
    "text.usetex": True,                # use LaTeX to write all text
    "font.family": "serif",             # use serif rather than sans-serif
    "font.serif": "TeX Gyre Pagella",             # use 'Ubuntu' as the standard font
    "font.sans-serif": [],
    "font.monospace": "Anonymous Pro",    # use Ubuntu mono if we have mono
    "axes.labelsize": 11,               # LaTeX default is 10pt font.
    "font.size": 11,
    "figure.titlesize": 11,               # Make the legend/label fonts a little smaller
    "figure.titleweight": 1,               # Make the legend/label fonts a little smaller
    "legend.fontsize": 11,               # Make the legend/label fonts a little smaller
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "pgf.rcfonts": False,               # Use pgf.preamble, ignore standard Matplotlib RC
    "text.latex.unicode": True,
    "pgf.preamble": [
        r'\usepackage{fontspec}',
        r'\setmainfont[Mapping=tex-text]{TeX Gyre Pagella}',
        r'\setsansfont[Mapping=tex-text]{TeX Gyre Adventor}',
        r'\setmonofont[Mapping=tex-text]{Anonymous Pro}',
        r'\newfontfamily\chapfont[Mapping=tex-text]{TeX Gyre Adventor}',
    ]
}

matplotlib.rcParams.update(pgf_with_latex)

def heatmap(data, row_labels, col_labels, ax=None,
            cbar_kw={}, cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Arguments:
        data       : A 2D numpy array of shape (N,M)
        row_labels : A list or array of length N with the labels
                     for the rows
        col_labels : A list or array of length M with the labels
                     for the columns
    Optional arguments:
        ax         : A matplotlib.axes.Axes instance to which the heatmap
                     is plotted. If not provided, use current axes or
                     create a new one.
        cbar_kw    : A dictionary with arguments to
                     :meth:`matplotlib.Figure.colorbar`.
        cbarlabel  : The label for the colorbar
    All other arguments are directly passed on to the imshow call.
    """

    if not ax:
        ax = plt.gca()

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    cbar = None
    #cbar = ax.figure.colorbar(im, ax=ax, orientation='vertical', **cbar_kw)
    #cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)

    # Let the horizontal axes labeling appear on top.
    #ax.tick_params(top=False, bottom=True,
    #               labeltop=False, labelbottom=False)

    # Rotate the tick labels and set their alignment.
   # plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
   #          rotation_mode="anchor")

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    #ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    #ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    #ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    #ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar

fig, axes = plt.subplots(len(runtimes)-1, len(data), figsize=(5.78851, 5.78851 * (9./16.) * 2), sharex=False, sharey=True)
nrow_map = {r: i for (r, i) in zip(runtimes[1:], range(0, len(runtimes)-1))}
ncol_map = {d[0]: i for (d, i) in zip(data, range(0, len(data)))}

for d in data:
    ncol = ncol_map[d[0]]
    ax = None
    for runtime in runtimes[1:]:
        nrow = nrow_map[runtime]
        ax = axes[nrow][ncol]
        print(nrow, ncol)
        #normalize data
        plot_data =  np.transpose(np.array(d[3][runtime]))

        #print(plot_data)
        if runtime == 'omp_for':
            ax.set_title('OpenMP parallel for')
        elif runtime == 'omp_task':
            ax.set_title('OpenMP parallel task')
        elif runtime == 'hpx':
            ax.set_title('HPX \\texttt{std::async}')
        else:
            ax.set_title('C++ \\texttt{std::async}')
        #ax.set_title('Scheduling with different granularities, %s' % runtime)
        #ax.set_yticks(np.arange(len(granularities)))
        #ax.set_yticklabels([ float(g.split('/')[1])/1000 for g in granularities])
        #ax.set_xticks(np.arange(len(d[2])))
        #ax.set_xticklabels(d[2])

        upper_bound = round(np.max(plot_data))
        if (upper_bound % 2) != 0:
            upper_bound = upper_bound  + 3 - (upper_bound % 2)
        bounds = np.linspace(0, upper_bound, 1000)
        norm = colors.BoundaryNorm(boundaries=bounds, ncolors=256)
        #norm = MidpointNormalize(1.0)

        im, cbar = heatmap(plot_data, [ float(g.split('/')[1])/1000 for g in granularities], d[2], ax = ax, vmin=0, cmap="RdBu_r", cbarlabel="Speedup", norm=norm, cbar_kw=dict(ticks=np.arange(upper_bound + 1, step=2)))
        ax.set_xlim([0, d[2][-1]])
    ax.set_xlabel('\# Cores')
    #ax.set_ylabel(' ')
    plt.tight_layout()
    #fig.text(0.1, 0.6, 'Granularity [microseconds]',
    #             horizontalalignment='center', color='black', weight='bold',
    #             fontsize=11, rotation=90)
        #cax = ax.pcolormesh(
        #    np.arange(len(thread_nums)),
        #    np.arange(len(granularities)), plot_data, norm=norm, cmap='RdBu_r'
        #)

#        cax = ax.imshow(plot_data, cmap=cm.coolwarm, norm=norm)
#        print(ax.get_aspect())
#        ax.set_aspect(1.5)
#        ax.apply_aspect(1.5)

        #if ncol == len(runtimes)-2:
   #divider = make_axes_locatable(axes)
    #tax = divider.append_axes("left", size="5%", pad=0.05)
    #tax.set_label('blubb')
plt.show()
        #    cbar = fig.colorbar(cax, cax=tax, ticks=np.arange(upper_bound + 1, step=4), orientation='vertical')

#cbar.ax.set_ylabel('Speedup')
#fig.text(0.98, 0.5, "Speedup", rotation='90')


#pprint(np.transpose(data[0][1]['hpx']))

