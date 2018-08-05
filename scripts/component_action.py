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
    print(name)
    components_data = json.load(open('%s/distributed/components.json' % results_dir))
    mhz = float(components_data['context']['mhz_per_cpu'])

    component_ptr = float((x for x in components_data['benchmarks']
        if x['name'] == 'simple_component_action_ptr/real_time').next()['real_time'])

    component_id = float((x for x in components_data['benchmarks']
        if x['name'] == 'simple_component_action_id/real_time').next()['real_time'])

    component_id_remote = float((x for x in components_data['benchmarks']
        if x['name'] == 'simple_component_action_id_remote/real_time').next()['real_time'])

    times = np.array([component_ptr, component_id, component_id_remote])

    cycles = (times * mhz) / 1000
    data.append((name, cycles))

if len(data) == 0:
    print('no results found')
    sys.exit(1)

# Number of data points:
#  - local
#  - remote
N = len(data[0][1])

N_experiments = len(data)

ind = np.arange(N)
width = 1.0 / (N_experiments + 1.0)

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


fig, ax = plt.subplots(figsize=(5.78851, 5.78851 * (9./16.)))

rects = []
for d, i in zip(data, range(0, len(data))):
    #print('%s %s' % (d[0], d[1][2]))
    rect = ax.bar(ind + i * width, d[1], width)
    rects.append(rect)

ax.set_ylabel('Cycles')
ax.set_title('Component Creation Costs', fontsize=11, weight='bold')
ax.set_xticks(ind + ((N_experiments - 1) * width) / 2.0)
ax.set_xticklabels(('Direct Call', 'Local AGAS Lookup', 'Remote AGAS Lookup'))
#ax.set_yscale('log')

ax.legend((r for r in rects), (d[0] for d in data))
plt.tight_layout(.5)

fname = '%s/component_action.pgf' % os.path.join(results_base, '../figures/')
plt.savefig(fname)
