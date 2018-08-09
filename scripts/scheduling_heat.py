#!/usr/bin/env python

import sys
import json
from pprint import pprint

import numpy as np
from matplotlib import cm
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.colors as colors
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable
import os
import re
import collections

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

results_json = {}

threads = []

for results_dir in results:
    name = os.path.split(results_dir)[-1]
    print(os.path.split(results_dir))

    tresults = [ f for f in os.listdir('%s/scheduling' % results_dir) if '_scheduling_t' in f ]
    for result in tresults:
        print(result)
        m = re.search('([a-z]+)_scheduling_t([0-9]+).json', result)
        runtime, thread = m.groups()
        if not name in results_json:
            results_json[name] = {}
        if not runtime in results_json[name]:
            results_json[name][runtime] = collections.OrderedDict()

        print('got %s' % thread)
        t = int(thread)
        if t > max_thread:
            max_thread = t
        if not t in threads:
            threads.append(t)

        results_json[name][runtime][t] = json.load(open('%s/scheduling/%s' % (results_dir, result)))

for results_dir in results:
    name = os.path.split(results_dir)[-1]
    print(os.path.split(results_dir))
    times = {}
    thread_nums = []
    for runtime in runtimes:
        times[runtime] = []
        if runtime == 'omp_for':
            jkey = 'omp'
        elif runtime == 'omp_task':
            jkey = 'omp'
        else:
            jkey = runtime

        for thread in sorted(threads):
            if runtime == 'seq' and thread > 1:
                continue

            jdata = results_json[name][jkey][thread]
            #if runtime == 'omp_for':
            #    jdata = json.load(open('%s/scheduling/%s_scheduling_t%s.json' % (results_dir, 'omp', threads)))
            #elif runtime == 'omp_task':
            #    jdata = json.load(open('%s/scheduling/%s_scheduling_t%s.json' % (results_dir, 'omp', threads)))
            #else:
            #    jdata = json.load(open('%s/scheduling/%s_scheduling_t%s.json' % (results_dir, runtime, threads)))

            if not thread in thread_nums:
                t = int(thread)
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

            print(base_name)
            #print('hae?', jkey, jdata['benchmarks'][0])
            for granularity in granularities:
                entry = [x for x in jdata['benchmarks'] if x['name'] == '%s/%s/real_time' % (base_name, granularity)]
                if len(entry) == 0:
                    print(jkey, granularity, threads, runtime, jdata)
                    break
                else:
                    time = float(entry[0]['real_time'])
                print (time)
                #time = float((x for x in jdata['benchmarks']
                #    if x['name'] == '%s/%s/real_time' % (base_name, granularity))['real_time'])
                thread_times.append(time)
            if runtime == 'seq':
                times[runtime].append(np.array(thread_times))
            else:
                times[runtime].append(times['seq'][0] / np.array(thread_times))
                this_max = np.max(times[runtime][-1])
                if this_max > max_speedup:
                    max_speedup = this_max
                #max_speedup = np.max(np.max(times[runtime][-1]), max_speedup)

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



runtime_map = {r: i for (r, i) in zip(runtimes[1:], range(0, len(runtimes)-1))}
data_map = {d[0]: i for (d, i) in zip(data, range(0, len(data)))}

figs = []
axes = []

for d in data:
    fig, taxes = plt.subplots(ncols=2, nrows=2, figsize=(5.78851, 5.78851 * (9./16.) * 2), sharex=False, sharey=True)
    figs.append(fig)
    axes.append(taxes.flatten())

# set axes titles
for axs in axes:
    for (r, ax) in zip(runtimes[1:], axs):
        if r == 'hpx':
            ax.set_title('\\texttt{hpx::async}', fontsize=11)
        elif r == 'std':
            ax.set_title('\\texttt{std::async}', fontsize=11)
        elif r == 'omp_for':
            ax.set_title('OpenMP for', fontsize=11)
        elif r == 'omp_task':
            ax.set_title('OpenMP task', fontsize=11)
        ax.set_aspect('equal', 'box')
    axs[0].set_ylabel('Speedup', fontsize=11)
    axs[2].set_ylabel('Speedup', fontsize=11)
    axs[2].set_xlabel('\# Cores', fontsize=11)
    axs[3].set_xlabel('\# Cores', fontsize=11)

for d in data:
    print d
    i = data_map[d[0]]
    for runtime in runtimes[1:]:
        j = runtime_map[runtime]
        print(i, j)

        #normalize data
        plot_data =  np.transpose(np.array(d[3][runtime]))
        print(runtime, plot_data)

        ax = axes[i][j]

        k = 0
        ax.set_xticks([ tick for tick in d[2] if tick > 1])
        if max_thread == 68:
            ax.set_xticklabels(['%s' % t if t % 8 == 0 else '' for t in d[2] if t > 1])
        else:
            ax.set_xticklabels(['%s' % t if t % 4 == 0 else '' for t in d[2] if t > 1])

        ax.plot(d[2], d[2], color='k', linestyle='--', label='ideal Speedup')
        g = 0
        for ys in plot_data:
            gran = float(granularities[g].split('/')[1]) / 1000.
            ax.plot(d[2], ys, label='%s ms' % gran)
            g = g + 1
    axes[i][-1].legend()

for d in data:
    i = data_map[d[0]]
    fig = figs[i]
    fig.tight_layout()
    fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.89, bottom=0.06)
    fig.text(0.5, 0.95, 'Scheduling Speedup for different task granularities (%s)' % d[0],
             horizontalalignment='center', color='black', weight='bold',
             fontsize=11)

    fname = '%s/scheduling_heat_%s.pgf' % (os.path.join(results_base, '../figures/'), d[0])
    plt.figure(fig.number)
    plt.savefig(fname)

#plt.show()

