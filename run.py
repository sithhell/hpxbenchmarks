#!/usr/bin/env python

import subprocess, os, sys, socket
import multiprocessing

if len(sys.argv) >= 2:
    max_cores = int(sys.argv[1])
    run=sys.argv[2:]
else:
    max_cores = multiprocessing.cpu_count()
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
    ]

    my_env['NUM_THREADS'] = '1'
    my_env['OMP_NUM_THREADS'] = '1'
    for benchmark in benchmarks:
        print('  %s' % benchmark)
        result = os.path.join(result_dir, benchmark + '.json')
        if not os.path.exists(os.path.dirname(result)):
            os.makedirs(os.path.dirname(result))
        bench = [
                os.path.join(os.getcwd(), benchmark), '--hpx:ini=hpx.parcel.enable=0', '--hpx:threads=1', '--benchmark_out_format=json', '--benchmark_out=' + result]
        print(bench)
        p = subprocess.Popen(bench, env = my_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(p.stdout.readline, b''):
            print(line.rstrip())
        p.wait()

if 'scheduling' in run or run == 'all':

    benchmarks=[
        'scheduling/hpx_scheduling',
        'scheduling/omp_scheduling',
        'scheduling/seq_scheduling',
        'scheduling/std_scheduling',
    ]

    r = range(0, max_cores + 1, 2)
    r[0] = 1
    for threads in r:

        my_env['NUM_THREADS'] = str(threads)

        for benchmark in benchmarks:
            if benchmark == 'scheduling/seq_scheduling' and threads > 1:
                continue

            print('  %s' % benchmark)
            result = os.path.join(result_dir, benchmark + ('_t%s' % threads) + '.json')
            if not os.path.exists(os.path.dirname(result)):
                os.makedirs(os.path.dirname(result))
            bench = [
                    os.path.join(os.getcwd(), benchmark), '--hpx:ini=hpx.parcel.enable=0', '-Ihpx.stacks.use_guard_pages=0', '--benchmark_out_format=json', '--benchmark_out=' + result]
            p = subprocess.Popen(bench, env = my_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in iter(p.stdout.readline, b''):
                print(line.rstrip())
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
                os.path.join(os.getcwd(), benchmark), '--hpx:ini=hpx.parcel.enable=0', '--hpx:threads=1', '--benchmark_out_format=json', '--benchmark_out=' + result]
        p = subprocess.Popen(bench, env = my_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(p.stdout.readline, b''):
            print(line.rstrip())
        p.wait()

if 'distributed' in run or run == 'all':
    benchmarks=[
        'distributed/async_latency',
        'distributed/channel_send_recv',
        'distributed/components',
    ]
    my_env['NUM_THREADS'] = '%s' % max_cores
    my_env['OMP_NUM_THREADS'] = '1'
    for benchmark in benchmarks:
        print('  %s' % benchmark)
        result = os.path.join(result_dir, benchmark + '.json')
        if not os.path.exists(os.path.dirname(result)):
            os.makedirs(os.path.dirname(result))
        bench = ['srun',
                os.path.join(os.getcwd(), benchmark), '--hpx:threads=%s' % max_cores, '--benchmark_out_format=json', '--benchmark_out=' + result]
        p = subprocess.Popen(bench, env = my_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(p.stdout.readline, b''):
            print(line.rstrip())
        p.wait()

    benchmarks=[
        'distributed/mpi_latency',
    ]
    my_env['NUM_THREADS'] = '%s' % max_cores
    my_env['OMP_NUM_THREADS'] = '1'
    for benchmark in benchmarks:
        print('  %s' % benchmark)
        result = os.path.join(result_dir, benchmark + '.json')
        if not os.path.exists(os.path.dirname(result)):
            os.makedirs(os.path.dirname(result))
        bench = ['srun',
                os.path.join(os.getcwd(), benchmark), '--benchmark_out_format=json', '--benchmark_out=' + result]
        p = subprocess.Popen(bench, env = my_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(p.stdout.readline, b''):
            print(line.rstrip())
        p.wait()

if 'broadcast' in run or run == 'all':
    benchmarks=[
        'distributed/broadcast',
    ]
    my_env['NUM_THREADS'] = '%s' % max_cores
    my_env['OMP_NUM_THREADS'] = '1'
    nodes = my_env['SLURM_NNODES']
    for benchmark in benchmarks:
        print('  %s' % benchmark)
        result = os.path.join(result_dir, "%s_%s" % (benchmark, nodes) + '.json')
        if not os.path.exists(os.path.dirname(result)):
            os.makedirs(os.path.dirname(result))
        bench = ['srun',
                os.path.join(os.getcwd(), benchmark), '--hpx:threads=%s' % max_cores, '--benchmark_out_format=json', '--benchmark_out=' + result]
        p = subprocess.Popen(bench, env = my_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(p.stdout.readline, b''):
            print(line.rstrip())
        p.wait()

    benchmarks=[
        'distributed/mpi_broadcast',
    ]
    my_env['NUM_THREADS'] = '%s' % max_cores
    my_env['OMP_NUM_THREADS'] = '1'
    for benchmark in benchmarks:
        print('  %s' % benchmark)
        result = os.path.join(result_dir, "%s_%s" % (benchmark, nodes) + '.json')
        if not os.path.exists(os.path.dirname(result)):
            os.makedirs(os.path.dirname(result))
        bench = ['srun',
                os.path.join(os.getcwd(), benchmark), '--benchmark_out_format=json', '--benchmark_out=' + result]
        p = subprocess.Popen(bench, env = my_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(p.stdout.readline, b''):
            print(line.rstrip())
            p.wait()
