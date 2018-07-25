// Copyright (c) 2017-2018 Thomas Heller
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

#include <benchmark/benchmark.h>
#include <hpx/hpx_init.hpp>
#include <hpx/runtime/threads/thread_data.hpp>
#include <hpx/runtime/threads/thread_init_data.hpp>

#include <support/dummy.hpp>

static void function_call_overhead(benchmark::State& state)
{
    for (auto _: state)
    {
        dummy();
    }
}
BENCHMARK(function_call_overhead)->UseRealTime();

static void coroutines_create_overhead(benchmark::State& state)
{
    for (auto _: state)
    {
        using hpx::threads::thread_init_data;

        thread_init_data data(
            [](hpx::threads::thread_state_ex_enum)
            {
                dummy();
                return hpx::threads::thread_result_type(hpx::threads::terminated, hpx::threads::invalid_thread_id);
            },
            hpx::util::thread_description()
        );
        hpx::threads::thread_data thrd(data, nullptr, hpx::threads::pending);
    }
}
BENCHMARK(coroutines_create_overhead)->UseRealTime();

static void coroutines_create_reuse_overhead(benchmark::State& state)
{
    hpx::threads::thread_init_data data(
        [](hpx::threads::thread_state_ex_enum)
        {
            dummy();
            return hpx::threads::thread_result_type(hpx::threads::terminated, hpx::threads::invalid_thread_id);
        },
        hpx::util::thread_description()
    );
    hpx::threads::thread_data thrd(data, nullptr, hpx::threads::pending);
    thrd();

    for (auto _: state)
    {
        hpx::threads::thread_init_data data(
            [](hpx::threads::thread_state_ex_enum)
            {
                dummy();
                return hpx::threads::thread_result_type(hpx::threads::terminated, hpx::threads::invalid_thread_id);
            },
            hpx::util::thread_description()
        );
        thrd.rebind(data, hpx::threads::pending);
    }
}
BENCHMARK(coroutines_create_reuse_overhead)->UseRealTime();

static void coroutines_call_overhead(benchmark::State& state)
{
    hpx::threads::thread_init_data data(
        [](hpx::threads::thread_state_ex_enum)
        {
            dummy();
            return hpx::threads::thread_result_type(hpx::threads::terminated, hpx::threads::invalid_thread_id);
        },
        hpx::util::thread_description()
    );
    hpx::threads::thread_data thrd(data, nullptr, hpx::threads::pending);
    thrd();

    for (auto _: state)
    {
        hpx::threads::thread_init_data data(
            [](hpx::threads::thread_state_ex_enum)
            {
                dummy();
                return hpx::threads::thread_result_type(hpx::threads::terminated, hpx::threads::invalid_thread_id);
            },
            hpx::util::thread_description()
        );
        thrd.rebind(data, hpx::threads::pending);
        thrd();
    }
}
BENCHMARK(coroutines_call_overhead)->UseRealTime();

static void coroutines_overhead(benchmark::State& state)
{
    for (auto _: state)
    {
        using hpx::threads::thread_init_data;

        thread_init_data data(
            [](hpx::threads::thread_state_ex_enum)
            {
                dummy();
                return hpx::threads::thread_result_type(hpx::threads::terminated, hpx::threads::invalid_thread_id);
            },
            hpx::util::thread_description()
        );
        hpx::threads::thread_data thrd(data, nullptr, hpx::threads::pending);

        thrd();
    }
}
BENCHMARK(coroutines_overhead)->UseRealTime();

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
        "hpx.os_threads!=" + thread_env,
    };
    return hpx::init(argc, argv, cfg);
}
