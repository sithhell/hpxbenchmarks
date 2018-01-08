// Copyright (c) 2017-2018 Thomas Heller
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

#include <benchmark/benchmark.h>
#include <hpx/hpx_main.hpp>
#include <hpx/runtime/serialization/detail/preprocess.hpp>
#include <hpx/include/serialization.hpp>
#include <hpx/include/async.hpp>
#include <hpx/include/actions.hpp>

#include <support/dummy.hpp>

std::vector<double> test(std::vector<double> v)
{
    return v;
}

HPX_PLAIN_ACTION(test, test_action)
HPX_PLAIN_DIRECT_ACTION(test, test_direct_action)

static void hpx_async_direct(benchmark::State& state)
{
    std::size_t size = state.range(0);
    std::size_t window = state.range(1);
    hpx::id_type dest = hpx::find_all_localities()[1];
    for (auto _: state)
    {
        std::vector<double> src(size);
        std::vector<hpx::future<std::vector<double>>> futures(window);
        for (std::size_t i = 0; i != window; ++i)
        {
            test_direct_action act;
            futures[i] = hpx::async(act, dest, std::move(src));
        }
        for (auto & f: futures)
        {
            f.get();
        }

    }
    state.SetBytesProcessed(int64_t(state.iterations()) * int64_t(size * sizeof(double)) * window * 2);
}
BENCHMARK(hpx_async_direct)
    ->UseRealTime()
    ->RangeMultiplier(2)->Ranges({{1, 1024*1024}, {1, 128}})
    ;

static void hpx_async(benchmark::State& state)
{
    std::size_t size = state.range(0);
    std::size_t window = state.range(1);
    hpx::id_type dest = hpx::find_all_localities()[1];
    for (auto _: state)
    {
        std::vector<double> src(size);
        std::vector<hpx::future<std::vector<double>>> futures(window);
        for (std::size_t i = 0; i != window; ++i)
        {
            test_action act;
            futures[i] = hpx::async(act, dest, std::move(src));
        }
        for (auto & f: futures)
        {
            f.get();
        }

    }
    state.SetBytesProcessed(int64_t(state.iterations()) * int64_t(size * sizeof(double)) * window);
}
BENCHMARK(hpx_async)
    ->UseRealTime()
    ->RangeMultiplier(2)->Ranges({{1, 1024*1024}, {1, 128}})
    ;

int main(int argc, char **argv)
{
    benchmark::Initialize(&argc, argv);
    benchmark::RunSpecifiedBenchmarks();

    return 0;
}
