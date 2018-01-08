// Copyright (c) 2017-2018 Thomas Heller
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

#include <benchmark/benchmark.h>

#include <tbb/tbb.h>

#include <support/dummy.hpp>

static void function_call_overhead(benchmark::State& state)
{
    for (auto _: state)
    {
        dummy();
    }
}
BENCHMARK(function_call_overhead)->UseRealTime();

struct dummy_task : tbb::task
{
    tbb::task *execute()
    {
        dummy();

        return nullptr;
    }
};

static void tbb_overhead(benchmark::State& state)
{
    for (auto _: state)
    {
        dummy_task &d = *new (tbb::task::allocate_root()) dummy_task();
        tbb::task::spawn_root_and_wait(d);
    }
}
BENCHMARK(tbb_overhead)->UseRealTime();

#include <cstdlib>

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
