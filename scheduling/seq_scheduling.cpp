// Copyright (c) 2017-2018 Thomas Heller
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

#include <benchmark/benchmark.h>

#include <support/dummy.hpp>

static void direct_homogeneous_seq(benchmark::State& state)
{
    std::size_t num_tasks = state.range(0);
    double delay = state.range(1);
    for (auto _: state)
    {
        for (std::size_t i = 0; i != num_tasks; ++i)
        {
            int j = dummy_timed(delay);
            benchmark::DoNotOptimize(j);
        }
    }
}
BENCHMARK(direct_homogeneous_seq)
    ->UseRealTime()
    ->RangeMultiplier(10)->Ranges({{1, 1000}, {0, 100000}})
    ;

int main(int argc, char **argv)
{
    benchmark::Initialize(&argc, argv);
    benchmark::RunSpecifiedBenchmarks();

    return 0;
}
