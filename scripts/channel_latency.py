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
    name = os.path.split(results_dir)[-1]
    print(name)
    async_data = json.load(open('%s/distributed/channel_send_recv.json' % results_dir))

    benchmarks = async_data['benchmarks']

    for benchmark in benchmarks:
        (name, sent_bytes, window_size, _) = benchmark['name'].split('/')

        if window_size in ['2', '4', '8', '16', '32', '64']:
            continue

        window_size = int(window_size)
        time = float(benchmark['bytes_per_second']) / 1e9
        if not name in data:
            data[name] = collections.OrderedDict()
        if not window_size in data[name]:
            data[name][window_size] = collections.OrderedDict()

        data[name][window_size][sent_bytes] = time# / window_size

    async_data = json.load(open('%s/distributed/mpi_latency.json' % results_dir))
    benchmarks = async_data['benchmarks']

    name = 'mpi'
    data[name] = collections.OrderedDict()
    for benchmark in benchmarks:
        (__, sent_bytes, window_size, _) = benchmark['name'].split('/')
        if window_size in ['2', '4', '8', '16', '32', '64']:
            continue

        window_size = int(window_size)
        time = float(benchmark['bytes_per_second']) / 1e9
        if not window_size in data[name]:
            data[name][window_size] = collections.OrderedDict()

        data[name][window_size][sent_bytes] = time# / window_size

fig, ax = plt.subplots(figsize=(5.78851, 5.78851 * (9./16.)))

sent_bytes = data['mpi'][1].keys()

line_styles = { 'hpx_channel_send_recv': '-', 'mpi': ':'}

for name in data:
    for window_size in data[name]:
        label = '%s, window size = %s' % (' '.join(name.split('_')), window_size)
        ax.plot(sent_bytes, data[name][window_size].values(), label = label, linestyle=line_styles[name])

ax.set_yscale('log')
#ax.set_xscale('log')
ax.set_xticklabels(sent_bytes, rotation=80, ha='left')

ax.legend()

ax.set_ylabel('Bandwidth [GB/s]')
ax.set_xlabel('Processed bytes')
ax.set_title('HPX channel throughput', fontsize=11, weight='bold')
plt.tight_layout(.5)

fname = '%s/channel_throughput.pgf' % os.path.join(results_base, '../figures/')
plt.savefig(fname)
#plt.show()
