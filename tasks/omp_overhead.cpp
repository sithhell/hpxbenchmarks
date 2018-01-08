// Copyright (c) 2017-2018 Thomas Heller
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

#include <benchmark/benchmark.h>
#include <omp.h>

#include <support/dummy.hpp>

static void function_call_overhead(benchmark::State& state)
{
    for (auto _: state)
    {
        dummy();
    }
}
BENCHMARK(function_call_overhead)->UseRealTime();

static void omp_overhead(benchmark::State& state)
{
    for (auto _: state)
    {
#pragma omp task
        {
            dummy();
        }
    }
}
BENCHMARK(omp_overhead)->UseRealTime();

int main(int argc, char **argv)
{
    const char *env = std::getenv("NUM_THREADS");
    std::string thread_env = env == nullptr ? "1": std::string(env);

    omp_set_num_threads(std::atoi(thread_env.c_str()));

    benchmark::Initialize(&argc, argv);
    benchmark::RunSpecifiedBenchmarks();

    return 0;
}
