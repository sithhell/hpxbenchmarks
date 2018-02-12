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


rects = []
for d in data:
    name = d[0]
    fig, ax = plt.subplots()
    coroutine_creation = d[1][1]
    context_switch = d[1][2] - coroutine_creation
    scheduler_overhead = d[1][-1] - d[1][2]

    total = d[1][-1]

    labels = 'Stack Creation', 'Context Switch', 'Scheduler Overhead'
    sizes = (np.array([coroutine_creation, context_switch, scheduler_overhead]) / total) * 100
    explode = (0, 0, 0.1)

    ax.pie(sizes, labels = labels, autopct='%1.1f%%', startangle=10)
    ax.axis('equal')

    ax.set_title('HPX Scheduling Overhead, %s' % name)

plt.show()
