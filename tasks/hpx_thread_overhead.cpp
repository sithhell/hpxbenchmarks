// Copyright (c) 2017-2018 Thomas Heller
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

#include <benchmark/benchmark.h>

#include <hpx/hpx_init.hpp>
#include <hpx/include/threads.hpp>

#include <support/dummy.hpp>

static void function_call_overhead(benchmark::State& state)
{
    for (auto _: state)
    {
        dummy();
    }
}
BENCHMARK(function_call_overhead)->UseRealTime();

static void hpx_thread_overhead(benchmark::State& state)
{
    for (auto _: state)
    {
        hpx::thread t(dummy);
        t.join();
    }
}
BENCHMARK(hpx_thread_overhead)->UseRealTime();

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
