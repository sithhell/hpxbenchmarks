// Copyright (c) 2017-2018 Thomas Heller
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

#include <benchmark/benchmark.h>
#include <hpx/hpx_init.hpp>
#include <hpx/lcos/future.hpp>
#include <hpx/lcos/local/promise.hpp>
#include <hpx/async.hpp>

#include <support/dummy.hpp>

static void hpx_homogeneous_seq(benchmark::State& state)
{
    std::size_t num_tasks = state.range(0);
    double delay = state.range(1);
    for (auto _: state)
    {
        std::vector<hpx::future<int>> futures(num_tasks);
        for (auto &f: futures)
        {
            f = hpx::async(dummy_timed, delay);
        }

        for (auto &f: futures)
        {
            f.get();
        }
    }
}
BENCHMARK(hpx_homogeneous_seq)
    ->UseRealTime()
    ->RangeMultiplier(10)->Ranges({{1, 1000}, {0, 100000}})
    ;

int hpx_main(int argc, char **argv)
{
    benchmark::RunSpecifiedBenchmarks();

    return hpx::finalize();
}

int main(int argc, char **argv)
{
    benchmark::Initialize(&argc, argv);

    const char *env = std::getenv("NUM_THREADS");
    std::string thread_env = env == nullptr ? "1": std::string(env);

    std::vector<std::string> const cfg = {
        "hpx.os_threads!=" + thread_env
    };
    return hpx::init(argc, argv, cfg);
}
