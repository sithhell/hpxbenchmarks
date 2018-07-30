#!/usr/bin/env python

import subprocess, os, sys, socket

if len(sys.argv) >= 2:
    run=sys.argv[1:]
else:
    run='all'

my_env = os.environ.copy()

result_dir = os.path.join('runs', socket.gethostname())

if 'tasks' in run or run == 'all':
    benchmarks=[
        'tasks/coroutines_overhead',
        'tasks/future_overhead',
        'tasks/hpx_thread_overhead',
        'tasks/std_thread_overhead',
        'tasks/omp_overhead',
        'tasks/tbb_overhead',
    ]

    my_env['NUM_THREADS'] = '1'
    my_env['OMP_NUM_THREADS'] = '1'
    for benchmark in benchmarks:
        print('  %s' % benchmark)
        result = os.path.join(result_dir, benchmark + '.json')
        if not os.path.exists(os.path.dirname(result)):
            os.makedirs(os.path.dirname(result))
        bench = [
            benchmark + ' --benchmark_out_format=json --benchmark_out=' + result]
        p = subprocess.Popen(bench, env = my_env, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(p.stdout.read())
        p.wait()

if 'scheduling' in run or run == 'all':
    import multiprocessing

    benchmarks=[
        'scheduling/hpx_scheduling',
        'scheduling/omp_scheduling',
        'scheduling/seq_scheduling',
        'scheduling/std_scheduling',
        'scheduling/tbb_scheduling',
    ]

    for threads in range(1, multiprocessing.cpu_count() + 1):

        my_env['NUM_THREADS'] = str(threads)

        for benchmark in benchmarks:
            if benchmark == 'scheduling/seq_scheduling' and threads > 1:
                continue

            print('  %s' % benchmark)
            result = os.path.join(result_dir, benchmark + ('_t%s' % threads) + '.json')
            if not os.path.exists(os.path.dirname(result)):
                os.makedirs(os.path.dirname(result))
            bench = [
                benchmark + ' --benchmark_out_format=json --benchmark_out=' + result + ' -Ihpx.stacks.use_guard_pages=0']
            p = subprocess.Popen(bench, env = my_env, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(p.stdout.read())
            p.wait()

if 'serialization' in run or run == 'all':
    benchmarks=[
        'distributed/serialization_overhead',
    ]
    my_env['NUM_THREADS'] = '1'
    my_env['OMP_NUM_THREADS'] = '1'
    for benchmark in benchmarks:
        print('  %s' % benchmark)
        result = os.path.join(result_dir, benchmark + '.json')
        if not os.path.exists(os.path.dirname(result)):
            os.makedirs(os.path.dirname(result))
        bench = [
                benchmark + ' --hpx:threads=1 --benchmark_out_format=json --benchmark_out=' + result]
        p = subprocess.Popen(bench, env = my_env, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(p.stdout.read())
        p.wait()
