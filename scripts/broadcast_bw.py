#!/usr/bin/env python

import sys
import json
from pprint import pprint

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os
import math
import collections
import re

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

data = {}

for results_dir in results:
    result_name = os.path.split(results_dir)[-1]

    file_list = os.listdir('%s/distributed' % results_dir)

    data['hpx_broadcast_direct'] = collections.OrderedDict()
    data['hpx_broadcast'] = collections.OrderedDict()

    tresults = [ f for f in file_list if f.startswith('broadcast_') ]
    for result in tresults:
        broadcast_data = json.load(open('%s/distributed/%s' % (results_dir, result)))
        m = re.search('broadcast_([0-9]+).json', result)
        nodes = m.groups()[0]
        print(result, nodes)
        benchmarks = broadcast_data['benchmarks']
        for benchmark in benchmarks:
            print(benchmark['name'])
            (name, sent_bytes, window_size, _) = benchmark['name'].split('/')
            print(name, sent_bytes, window_size)

            time = float(benchmark['bytes_per_second']) / 1e9
            print(nodes, time)
            sent_bytes = int(sent_bytes)
            window_size = int(window_size)
            if not window_size in data[name]:
                data[name][window_size] = collections.OrderedDict()

            if not sent_bytes in data[name][window_size]:
                data[name][window_size][sent_bytes] = collections.OrderedDict()

            data[name][window_size][sent_bytes][int(nodes)] = time

    #benchmarks = async_data['benchmarks']

    #for benchmark in benchmarks:
    #    (name, sent_bytes, window_size, _) = benchmark['name'].split('/')

    #    if window_size in ['2', '4', '8', '16', '32', '64']:
    #        continue

    #    window_size = int(window_size)
    #    time = float(benchmark['bytes_per_second']) / 1e9
    #    if not name in data:
    #        data[name] = collections.OrderedDict()
    #    if not window_size in data[name]:
    #        data[name][window_size] = collections.OrderedDict()

    #    data[name][window_size][sent_bytes] = time# / window_size

    tresults = [ f for f in file_list if 'mpi_broadcast_' in f ]
    name = 'mpi'
    data[name] = collections.OrderedDict()

    for result in tresults:
        broadcast_data = json.load(open('%s/distributed/%s' % (results_dir, result)))
        m = re.search('mpi_broadcast_([0-9]+).json', result)
        nodes = m.groups()[0]
        print(result, nodes)
        benchmarks = broadcast_data['benchmarks']
        for benchmark in benchmarks:
            (__, sent_bytes, _) = benchmark['name'].split('/')
            print(sent_bytes)

            time = float(benchmark['bytes_per_second']) / 1e9
            print(nodes, time)
            sent_bytes = int(sent_bytes)
            if not sent_bytes in data[name]:
                data[name][sent_bytes] = collections.OrderedDict()

            data[name][sent_bytes][int(nodes)] = time
        #    if not window_size in data[name]:
        #        data[name][window_size] = collections.OrderedDict()
        #
        #    data[name][window_size][sent_bytes] = time# / window_size

fig, axes = plt.subplots(ncols=3, figsize=(5.78851, 5.78851 * (9./16.)), sharey=True)

nodes = sorted(data['mpi'][1].keys())

print(nodes)

line_styles = { 'hpx_async_direct': '-', 'hpx_async': '--', 'mpi': ':'}

ax = axes[0]

sizes = [1, 4096, 1048576]

mpi_colors = {1: 'C1', 4096: 'C2', 1048576: 'C3'}
direct_colors = {1: 'C4', 4096: 'C5', 1048576: 'C6'}
async_colors = {1: 'C7', 4096: 'C8', 1048576: 'C9'}

rects = []


def to_mbyte(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


for sent_bytes in sizes:
    label = 'MPI, size=%s' % to_mbyte(sent_bytes)
    d = [ data['mpi'][sent_bytes][n] for n in nodes ]
    print(sent_bytes, d)
    rect, = ax.plot(nodes, d, label = label, linestyle='-', color=mpi_colors[sent_bytes])
    rects.append(rect)

ax.set_ylabel('Bandwidth [GB/s]')
ax.set_xlabel('Number of Nodes')
ax.set_title('MPI', fontsize=11, weight='bold')
#ax.legend()

ax = axes[1]

for sent_bytes in sizes:
    label = 'HPX direct, size=%s' % to_mbyte(sent_bytes)
    d = [ data['hpx_broadcast_direct'][1][sent_bytes][n] for n in nodes ]
    print(sent_bytes, d)
    rect, = ax.plot(nodes, d, label = label, linestyle='-', color=direct_colors[sent_bytes])
    rects.append(rect)

for sent_bytes in sizes:
    label = 'HPX async, size=%s' % to_mbyte(sent_bytes)
    d = [ data['hpx_broadcast'][1][sent_bytes][n] for n in nodes ]
    print(sent_bytes, d)
    rect, = ax.plot(nodes, d, label = label, linestyle='-', color=async_colors[sent_bytes])
    rects.append(rect)

ax.set_xlabel('Number of Nodes')
ax.set_title('HPX window size = 1', fontsize=11, weight='bold')
#ax.legend()

ax = axes[2]

for sent_bytes in sizes:
    label = 'HPX direct, size=%s' % to_mbyte(sent_bytes)
    d = [ data['hpx_broadcast_direct'][8][sent_bytes][n] for n in nodes ]
    print(sent_bytes, d)
    rect, = ax.plot(nodes, d, label = label, linestyle='-', color=direct_colors[sent_bytes])

for sent_bytes in sizes:
    label = 'HPX async, size=%s' % to_mbyte(sent_bytes)
    d = [ data['hpx_broadcast'][8][sent_bytes][n] for n in nodes ]
    print(sent_bytes, d)
    rect, = ax.plot(nodes, d, label = label, linestyle='-', color=async_colors[sent_bytes])


#for name in data:
#    for window_size in data[name]:
#        label = '%s, window size = %s' % (' '.join(name.split('_')), window_size)
#        ax.plot(sent_bytes, data[name][window_size].values(), label = label, linestyle=line_styles[name])

ax.set_yscale('log')
#ax.set_xticks(nodes)
#ax.set_xscale('log')
#ax.set_xticklabels(nodes, rotation=80, ha='left')


ax.set_xlabel('Number of Nodes')
ax.set_title('HPX window size = 8', fontsize=11, weight='bold')
#ax.legend()
plt.tight_layout()


#fig.legend((r for r in rects), ('MPI', 'HPX direct', 'HPX async'))
fig.legend(handlelength=0.9, loc='lower center', ncol=3, handles=rects, fontsize=11, handletextpad=0.1)#(r for r in rects), ('MPI', 'HPX direct', 'HPX async'))

fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.39)
fig.text(0.5, 0.95, 'Broadcast Throughput (%s)' % result_name,
     horizontalalignment='center', color='black', weight='bold',
     fontsize=11)

#ax.legend()
import matplotlib.ticker
ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())


fname = '%s/broadcast_bw_%s.pgf' % (os.path.join(results_base, '../figures/'), result_name)
plt.savefig(fname)
