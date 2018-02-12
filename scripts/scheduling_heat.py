#!/usr/bin/env python

import sys
import json
from pprint import pprint

import numpy as np
from matplotlib import cm
import matplotlib.pyplot as plt
import matplotlib.colors as colors
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

thread_nums = []
max_speedup=0.0

for results_dir in results:
    name = os.path.split(results_dir)[-1]
    times = {}
    for runtime in ('seq', 'hpx', 'hpx_base', 'omp_for', 'omp_task', 'tbb', 'std'):
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
                    thread_nums.append(int(threads))

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
    data.append((name, times))


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

for runtime in ('hpx', 'hpx_base', 'omp_for', 'omp_task', 'tbb', 'std'):
    #normalize data
    plot_data =  np.transpose(data[0][1][runtime])

    fig, ax = plt.subplots()

    ax.set_title('Scheduling with different granularities, %s' % runtime)
    ax.set_yticks(np.arange(len(granularities)))
    ax.set_yticklabels([ float(g.split('/')[1])/1000 for g in granularities])
    ax.set_xticks(np.arange(len(thread_nums)))
    ax.set_xticklabels(thread_nums)
    ax.set_xlabel('#Cores')
    ax.set_ylabel('Granularity [microseconds]')

    upper_bound = round(max_speedup)
    if (upper_bound % 4) != 0:
        upper_bound = upper_bound  + 4 - (upper_bound % 4)
    bounds = np.linspace(0, upper_bound, 1000)
    norm = colors.BoundaryNorm(boundaries=bounds, ncolors=256)
    #norm = MidpointNormalize(1.0)

    #cax = ax.pcolormesh(
    #    np.arange(len(thread_nums)),
    #    np.arange(len(granularities)), plot_data, norm=norm, cmap='RdBu_r'
    #)

    cax = ax.imshow(plot_data, cmap=cm.coolwarm, norm=norm)

    cbar = fig.colorbar(cax, ticks=np.arange(upper_bound + 1, step=4), orientation='horizontal')
    cbar.ax.set_xlabel('Speedup')

pprint(np.transpose(data[0][1]['hpx']))
pprint(np.transpose(data[0][1]['hpx_base']))
try:
    pprint(np.transpose(data[0][1]['hpx']) / np.transpose(data[0][1]['hpx_base']))
except:
    pass

plt.show()
