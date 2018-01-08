// Copyright (c) 2017-2018 Thomas Heller
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

#include <benchmark/benchmark.h>

#include <thread>

#include <support/dummy.hpp>

static void function_call_overhead(benchmark::State& state)
{
    for (auto _: state)
    {
        dummy();
    }
}
BENCHMARK(function_call_overhead)->UseRealTime();

static void std_thread_overhead(benchmark::State& state)
{
    for (auto _: state)
    {
        std::thread t(dummy);
        t.join();
    }
}
BENCHMARK(std_thread_overhead)->UseRealTime();

BENCHMARK_MAIN();
