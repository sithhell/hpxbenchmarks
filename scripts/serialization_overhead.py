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

def to_mbyte(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])

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
    serialization_data = json.load(open('%s/distributed/serialization_overhead.json' % results_dir))

    benchmarks = serialization_data['benchmarks']

    for benchmark in benchmarks:
        (name, serialized_bytes, _) = benchmark['name'].split('/')
        serialized_bytes = int(serialized_bytes)
        time = benchmark['real_time'] / 1e9
        if not name in data:
            data[name] = collections.OrderedDict()

        data[name][serialized_bytes] = time

    #mhz = float(coroutines_data['context']['mhz_per_cpu'])
    #baseline_str = 'function_call_overhead/real_time'
    #baseline = float((x for x in coroutines_data['benchmarks']
    #    if x['name'] == baseline_str).next()['real_time'])
    #coroutines = float((x for x in coroutines_data['benchmarks']
    #    if x['name'] == 'coroutines_call_overhead/real_time').next()['real_time'])

    #hpx_threads_data = json.load(open('%s/tasks/hpx_thread_overhead.json' % results_dir))
    #hpx_threads = float((x for x in hpx_threads_data['benchmarks']
    #    if x['name'] == 'hpx_thread_overhead/real_time').next()['real_time'])

    #omp_data = json.load(open('%s/tasks/omp_overhead.json' % results_dir))
    #omp = float((x for x in omp_data['benchmarks']
    #    if x['name'] == 'omp_overhead/real_time').next()['real_time'])

    #std_threads_data = json.load(open('%s/tasks/std_thread_overhead.json' % results_dir))
    #std_threads = float((x for x in std_threads_data['benchmarks']
    #    if x['name'] == 'std_thread_overhead/real_time').next()['real_time'])

    #times = np.array([coroutines, hpx_threads - baseline, omp - baseline])

    #print(hpx_threads/omp)
    #print(omp/hpx_threads)

    #cycles = (times * mhz) / 1000
    #data.append((name, cycles))

if len(data) == 0:
    print('no results found')
    sys.exit(1)

# Number of data points:
#  - coroutines (plain)
#  - hpx threads
#  - std threads
N = len(data['memcpy_double'])

N_experiments = 3

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

ax.set_xticks(ind + ((N_experiments - 1) * width) / 2.0)
ax.set_xticklabels([size for size in data['memcpy_double'].keys()], rotation=80, ha='right')

serialized_bytes = (np.array(data['memcpy_double'].keys()) * 8) / 1e9

# plot memcpy...
rect = ax.bar(ind, serialized_bytes / np.array(data['memcpy_double'].values()) , width)
rects.append(rect)

hpx_ind = ind + width

hpx_parcel_total = np.array(data['hpx_double_input'].values())
hpx_parcel_total = hpx_parcel_total + np.array(data['hpx_double_output'].values())

rect = ax.bar(hpx_ind, serialized_bytes / hpx_parcel_total , width)
rects.append(rect)

hpx_ind = ind + 2* width

hpx_parcel_total = np.array(data['hpx_parcel_double_input'].values())
hpx_parcel_total = hpx_parcel_total + np.array(data['hpx_parcel_double_output'].values())

rect = ax.bar(hpx_ind, serialized_bytes / hpx_parcel_total , width)
rects.append(rect)


#for name in data:
#    print(data[name].keys(), data[name].values())
#    label = ' '.join(name.split('_'))
#    ax.plot(data[name].keys(), data[name].values(), label = label)

ax.legend(rects, ['memcpy', 'plain serialization', 'parcel serialization'])

#data[37] = 35;
#data[23] = 25;
#ax.plot(data.keys(), data.values())

#rects = []
#for d, i in zip(data, range(0, len(data))):
#    print('%s %s' % (d[0], d[1][2]))
#    rect = ax.bar(ind + i * width, d[1], width)
#    rects.append(rect)
#
ax.set_ylabel('Bandwidth [GB/s]')
ax.set_xlabel('Processed bytes')
ax.set_title('HPX Serialization throughput (%s)' % result_name, fontsize=11, weight='bold')
plt.tight_layout(.5)

print(result_name)
fname = '%s/serialization_overhead_%s.pgf' % (os.path.join(results_base, '../figures/'), result_name)
plt.savefig(fname)
#plt.show()
