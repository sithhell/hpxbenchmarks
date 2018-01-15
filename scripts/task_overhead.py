#!/usr/bin/env python

import sys
import json
from pprint import pprint

import numpy as np
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
    coroutines_data = json.load(open('%s/tasks/coroutines_overhead.json' % results_dir))
    mhz = float(coroutines_data['context']['mhz_per_cpu'])
    baseline_str = 'function_call_overhead/real_time'
    baseline = float((x for x in coroutines_data['benchmarks']
        if x['name'] == baseline_str).next()['real_time'])
    coroutines = float((x for x in coroutines_data['benchmarks']
        if x['name'] == 'coroutines_call_overhead/real_time').next()['real_time'])

    hpx_threads_data = json.load(open('%s/tasks/hpx_thread_overhead.json' % results_dir))
    hpx_threads = float((x for x in hpx_threads_data['benchmarks']
        if x['name'] == 'hpx_thread_overhead/real_time').next()['real_time'])

    omp_data = json.load(open('%s/tasks/omp_overhead.json' % results_dir))
    omp = float((x for x in omp_data['benchmarks']
        if x['name'] == 'omp_overhead/real_time').next()['real_time'])

    tbb_data = json.load(open('%s/tasks/tbb_overhead.json' % results_dir))
    tbb = float((x for x in tbb_data['benchmarks']
        if x['name'] == 'tbb_overhead/real_time').next()['real_time'])

    std_threads_data = json.load(open('%s/tasks/std_thread_overhead.json' % results_dir))
    std_threads = float((x for x in std_threads_data['benchmarks']
        if x['name'] == 'std_thread_overhead/real_time').next()['real_time'])
    std_threads=0

    #times = np.array([coroutines, hpx_threads, std_threads])
    #data.append((name, times / baseline))
    times = np.array([baseline, coroutines, omp, tbb])
    cycles = (times * mhz) / 1000
    data.append((name, cycles))

if len(data) == 0:
    print('no results found')
    sys.exit(1)

# Number of data points:
#  - coroutines (plain)
#  - hpx threads
#  - std threads
N = len(data[0][1])

N_experiments = len(data)

ind = np.arange(N)
width = 1.0 / (N_experiments + 1.0)

fig, ax = plt.subplots()

rects = []
for d, i in zip(data, range(0, len(data))):
    rect = ax.bar(ind + i * width, d[1], width)
    rects.append(rect)

ax.set_ylabel('Cycles')
ax.set_title('Task creation overhead')
ax.set_xticks(ind + ((N_experiments - 1) * width) / 2.0)
ax.set_xticklabels(('Function Call', 'HPX Coroutines', 'OpenMP', 'TBB'))

ax.legend((r for r in rects), (d[0] for d in data))

plt.show()
