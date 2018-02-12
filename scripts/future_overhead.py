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
    future_data = json.load(open('%s/tasks/future_overhead.json' % results_dir))
    mhz = float(future_data['context']['mhz_per_cpu'])

    hpx_make_ready_void = float((x for x in future_data['benchmarks']
        if x['name'] == 'hpx_make_ready_void_overhead/real_time').next()['real_time'])

    hpx_make_ready_int = float((x for x in future_data['benchmarks']
        if x['name'] == 'hpx_make_ready_overhead/real_time').next()['real_time'])

    hpx_promise_void = float((x for x in future_data['benchmarks']
        if x['name'] == 'hpx_promise_void_overhead/real_time').next()['real_time'])

    hpx_promise_int = float((x for x in future_data['benchmarks']
        if x['name'] == 'hpx_promise_overhead/real_time').next()['real_time'])

    hpx_async_void = float((x for x in future_data['benchmarks']
        if x['name'] == 'hpx_async_void_overhead/real_time').next()['real_time'])

    hpx_async_int = float((x for x in future_data['benchmarks']
        if x['name'] == 'hpx_async_int_overhead/real_time').next()['real_time'])

    std_promise_void = float((x for x in future_data['benchmarks']
        if x['name'] == 'std_promise_void_overhead/real_time').next()['real_time'])

    std_promise_int = float((x for x in future_data['benchmarks']
        if x['name'] == 'std_promise_overhead/real_time').next()['real_time'])

    std_async_void = float((x for x in future_data['benchmarks']
        if x['name'] == 'std_async_void_overhead/real_time').next()['real_time'])

    std_async_int = float((x for x in future_data['benchmarks']
        if x['name'] == 'std_async_int_overhead/real_time').next()['real_time'])

    times = np.array([
        hpx_make_ready_void,
        hpx_make_ready_int,
        hpx_promise_void,
        hpx_promise_int,
        hpx_async_void,
        hpx_async_int,
        std_promise_void,
        std_promise_int,
        std_async_void,
        std_async_int
    ])
    cycles = (times * mhz) / 1000
    data.append((name, cycles))

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
ax.set_xticklabels((
    'HPX make_ready (void)',
    'HPX make_ready (int)',
    'HPX promise (void)',
    'HPX promise (int)',
    'HPX async (void)',
    'HPX async (int)',
    'std promise (void)',
    'std promise (int)',
    'std async (void)',
    'std async (int)'))
for tick in ax.get_xticklabels():
    tick.set_rotation(-90)

ax.legend((r for r in rects), (d[0] for d in data))

plt.show()
