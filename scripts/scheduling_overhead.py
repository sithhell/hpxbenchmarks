#!/usr/bin/env python

import sys
import json
from pprint import pprint

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
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

for results_dir in results:
    name = os.path.split(results_dir)[-1]

    coroutines_data = json.load(open('%s/tasks/coroutines_overhead.json' % results_dir))
    hpx_threads_data = json.load(open('%s/tasks/hpx_thread_overhead.json' % results_dir))

    mhz = float(coroutines_data['context']['mhz_per_cpu'])

    coroutines_call = float((x for x in coroutines_data['benchmarks']
        if x['name'] == 'coroutines_call_overhead/real_time').next()['real_time'])

    coroutines_overhead = float((x for x in coroutines_data['benchmarks']
        if x['name'] == 'coroutines_overhead/real_time').next()['real_time'])

    coroutines_creation = float((x for x in coroutines_data['benchmarks']
        if x['name'] == 'coroutines_create_overhead/real_time').next()['real_time'])

    coroutines_creation_reuse = float((x for x in coroutines_data['benchmarks']
        if x['name'] == 'coroutines_create_reuse_overhead/real_time').next()['real_time'])

    hpx_threads = float((x for x in hpx_threads_data['benchmarks']
        if x['name'] == 'hpx_thread_overhead/real_time').next()['real_time'])

    times = np.array([coroutines_creation, coroutines_creation_reuse, coroutines_call, coroutines_overhead, hpx_threads])
    cycles = (times * mhz) / 1000
    data.append((name, cycles))

if len(data) == 0:
    print('no results found')
    sys.exit(1)

N = len(data[0][1])

N_experiments = len(data)

ind = np.arange(N)
width = 0.5

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

fig, axes = plt.subplots(nrows=1, ncols=len(data), figsize=(5.78851, 5.78851 * (9./16.)))
fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)
rects = []
for d, ax in zip(data, axes.flatten()):
    name = d[0]
    coroutine_creation = d[1][1]
    context_switch = d[1][2] - coroutine_creation
    scheduler_overhead = d[1][-1] - d[1][2]

    total = d[1][-1]

    sizes = (np.array([coroutine_creation, context_switch, scheduler_overhead]) / total) * 100
    explode = (0, 0, 0.1)

    ax.pie(sizes, autopct='%1.1f\%%', startangle=10)
    ax.axis('equal')

    ax.set_title(name, position=(0.5, .8), fontsize=11)



fig.text(0.5, 0.9, 'HPX Scheduling Overhead',
             horizontalalignment='center', color='black', weight='bold',
             fontsize=11)

plt.tight_layout(.5)

ax = axes[1]
labels = 'Stack Creation', 'Context Switch', 'Scheduler Overhead'
legend = ax.legend(labels, ncol=3, loc='lower center')

fname = '%s/scheduling_overhead.pgf' % os.path.join(results_base, '../figures/')
plt.savefig(fname)
