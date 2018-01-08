// Copyright (c) 2017-2018 Thomas Heller
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

#include <benchmark/benchmark.h>
#include <hpx/hpx_main.hpp>
#include <hpx/lcos/future.hpp>
#include <hpx/lcos/local/promise.hpp>
#include <hpx/async.hpp>

#include <future>
#include <thread>

#include <support/dummy.hpp>

static void int_overhead(benchmark::State& state)
{
    for (auto _: state)
    {
        int i = 0;
        benchmark::DoNotOptimize(i);
    }
}
BENCHMARK(int_overhead)->UseRealTime();

static void hpx_make_ready_void_overhead(benchmark::State& state)
{
    for (auto _: state)
    {
        hpx::make_ready_future().get();
    }
}
BENCHMARK(hpx_make_ready_void_overhead)->UseRealTime();

static void hpx_make_ready_overhead(benchmark::State& state)
{
    for (auto _: state)
    {
        int i = hpx::make_ready_future(0).get();
        benchmark::DoNotOptimize(i);
    }
}
BENCHMARK(hpx_make_ready_overhead)->UseRealTime();

static void hpx_promise_void_overhead(benchmark::State& state)
{
    for (auto _: state)
    {
        hpx::lcos::local::promise<void> p;
        p.set_value();
        p.get_future().get();
    }
}
BENCHMARK(hpx_promise_void_overhead)->UseRealTime();

static void hpx_promise_overhead(benchmark::State& state)
{
    for (auto _: state)
    {
        hpx::lcos::local::promise<int> p;
        p.set_value(0);
        int i = p.get_future().get();
        benchmark::DoNotOptimize(i);
    }
}
BENCHMARK(hpx_promise_overhead)->UseRealTime();

static void hpx_async_void_overhead(benchmark::State& state)
{
    for (auto _: state)
    {
        hpx::async([](){}).get();
    }
}
BENCHMARK(hpx_async_void_overhead)->UseRealTime();

static void hpx_async_int_overhead(benchmark::State& state)
{
    for (auto _: state)
    {
        int i = hpx::async(dummy).get();
        benchmark::DoNotOptimize(i);
    }
}
BENCHMARK(hpx_async_int_overhead)->UseRealTime();

static void std_promise_void_overhead(benchmark::State& state)
{
    for (auto _: state)
    {
        std::promise<void> p;
        p.set_value();
        p.get_future().get();
    }
}
BENCHMARK(std_promise_void_overhead)->UseRealTime();

static void std_promise_overhead(benchmark::State& state)
{
    for (auto _: state)
    {
        std::promise<int> p;
        p.set_value(0);
        int i = p.get_future().get();
        benchmark::DoNotOptimize(i);
    }
}
BENCHMARK(std_promise_overhead)->UseRealTime();

static void std_async_void_overhead(benchmark::State& state)
{
    for (auto _: state)
    {
        std::async([](){}).get();
    }
}
BENCHMARK(std_async_void_overhead)->UseRealTime();

static void std_async_int_overhead(benchmark::State& state)
{
    for (auto _: state)
    {
        int i = std::async(dummy).get();
        benchmark::DoNotOptimize(i);
    }
}
BENCHMARK(std_async_int_overhead)->UseRealTime();


int main(int argc, char **argv)
{
    benchmark::Initialize(&argc, argv);
    benchmark::RunSpecifiedBenchmarks();

    return 0;
}
