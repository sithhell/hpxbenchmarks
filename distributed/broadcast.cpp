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
#include <hpx/include/lcos.hpp>
#include <hpx/lcos/broadcast.hpp>

#include <support/dummy.hpp>

void test(std::vector<double> v)
{
}

HPX_PLAIN_ACTION(test, test_action)
HPX_PLAIN_DIRECT_ACTION(test, test_direct_action)

static void hpx_broadcast_direct(benchmark::State& state)
{
    std::size_t size = state.range(0);
    std::size_t window = state.range(1);
    std::vector<hpx::id_type> locs = hpx::find_all_localities();
    for (auto _: state)
    {
        std::vector<double> src(size);
        std::vector<hpx::future<void>> futures(window);
        for (std::size_t i = 0; i != window; ++i)
        {
            futures[i] = hpx::lcos::broadcast<test_action>(locs, std::move(src));
        }
        for (auto & f: futures)
        {
            f.get();
        }
    }
    state.SetBytesProcessed(int64_t(state.iterations()) * int64_t(size * sizeof(double)) * window);
}
BENCHMARK(hpx_broadcast_direct)
    ->UseRealTime()
    ->RangeMultiplier(2)->Ranges({{1, 1024*1024}, {1, 128}})
    ;

static void hpx_broadcast(benchmark::State& state)
{
    std::size_t size = state.range(0);
    std::size_t window = state.range(1);
    std::vector<hpx::id_type> locs = hpx::find_all_localities();
    for (auto _: state)
    {
        std::vector<double> src(size);
        std::vector<hpx::future<void>> futures(window);
        for (std::size_t i = 0; i != window; ++i)
        {
            futures[i] = hpx::lcos::broadcast<test_direct_action>(locs, std::move(src));
        }
        for (auto & f: futures)
        {
            f.get();
        }
    }
    state.SetBytesProcessed(int64_t(state.iterations()) * int64_t(size * sizeof(double)) * window);
}
BENCHMARK(hpx_broadcast)
    ->UseRealTime()
    ->RangeMultiplier(2)->Ranges({{1, 1024*1024}, {1, 128}})
    ;

int main(int argc, char **argv)
{
    benchmark::Initialize(&argc, argv);
    benchmark::RunSpecifiedBenchmarks();

    return 0;
}
