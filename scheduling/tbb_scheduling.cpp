// Copyright (c) 2017-2018 Thomas Heller
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

#include <benchmark/benchmark.h>

#include <tbb/tbb.h>

#include <support/dummy.hpp>

#include <iostream>

#include <cstdlib>

double delay;
std::size_t num_tasks;

struct dummy_task : tbb::task
{

    tbb::task *execute()
    {
        int j = dummy_timed(delay);
        benchmark::DoNotOptimize(j);

        return nullptr;
    }
};

struct root_task : tbb::task
{
    tbb::task *execute()
    {
        set_ref_count(num_tasks + 1);
        for (std::size_t i = 0; i != num_tasks-1; ++i)
        {
            dummy_task &d = *new (tbb::task::allocate_child()) dummy_task();
            spawn(d);
        }
        dummy_task &d = *new (tbb::task::allocate_child()) dummy_task();
        spawn_and_wait_for_all(d);

        return nullptr;
    }
};

static void tbb_homogeneous_seq(benchmark::State& state)
{
    num_tasks = state.range(0);
    delay = state.range(1);
    for (auto _: state)
    {
        root_task &r = *new (tbb::task::allocate_root()) root_task();
        tbb::task::spawn_root_and_wait(r);
    }
}
BENCHMARK(tbb_homogeneous_seq)
    ->UseRealTime()
    ->RangeMultiplier(10)->Ranges({{1, 1000}, {0, 100000}})
    ;

int main(int argc, char **argv)
{
    benchmark::Initialize(&argc, argv);

    int num_threads = 1;
    if (argc == 2)
    {
        num_threads = std::atoi(argv[1]);
    }


    tbb::task_scheduler_init init(num_threads);
    benchmark::RunSpecifiedBenchmarks();

    return 0;
}
