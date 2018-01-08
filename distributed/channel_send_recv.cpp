// Copyright (c) 2017-2018 Thomas Heller
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

#include <benchmark/benchmark.h>
#include <hpx/hpx_init.hpp>
#include <hpx/runtime/serialization/detail/preprocess.hpp>
#include <hpx/include/serialization.hpp>
#include <hpx/include/async.hpp>
#include <hpx/include/actions.hpp>
#include <hpx/include/lcos.hpp>
#include <hpx/lcos/broadcast.hpp>

#include <support/dummy.hpp>
#include <support/null_reporter.hpp>

HPX_REGISTER_CHANNEL(double)
typedef std::vector<double> double_vector;
HPX_REGISTER_CHANNEL(double_vector)

std::size_t generation = 0;
hpx::lcos::channel<double> timer_channel_0;
hpx::lcos::channel<double> timer_channel_1;
hpx::lcos::channel<std::vector<double>> send_channel;
hpx::lcos::channel<std::vector<double>> recv_channel;

static void hpx_channel_send_recv(benchmark::State& state)
{
    std::size_t size = state.range(0);
    std::size_t window = state.range(1);
    std::size_t rank = hpx::get_locality_id();
    std::size_t dst_rank = 0;
    if (rank == 0)
        dst_rank = 1;

    for (auto _: state)
    {
        hpx::util::high_resolution_timer timer;
        std::vector<double> src(size);
        std::vector<hpx::future<void>> futures(window);
        for (std::size_t i = 0; i != window; ++i)
        {
            hpx::future<void> send_fut = send_channel.set(hpx::launch::async, std::move(src), generation);
            hpx::future<void> recv_fut = recv_channel.get(generation);
            futures[i] = hpx::when_all(send_fut, recv_fut);
            ++generation;
        }
        for (auto & f: futures)
        {
            f.get();
        }
        double elapsed = timer.elapsed();

        hpx::future<double> f;
        if (rank == 0)
        {
            f = timer_channel_1.get(generation);
            timer_channel_0.set(hpx::launch::sync, elapsed, generation);
        }
        else
        {
            f = timer_channel_0.get(generation);
            timer_channel_1.set(hpx::launch::sync, elapsed, generation);
        }
        double iteration_time = std::max(elapsed, f.get());
        state.SetIterationTime(iteration_time);
        ++generation;
    }
    hpx::lcos::barrier::synchronize();
    state.SetBytesProcessed(int64_t(state.iterations()) * int64_t(size * sizeof(double)) * window * 2);
}
BENCHMARK(hpx_channel_send_recv)
    ->UseRealTime()
    ->RangeMultiplier(2)->Ranges({{1, 1024*1024}, {1, 128}})
    ->UseManualTime()
    ;

int hpx_main(int argc, char **argv)
{
    std::size_t rank = hpx::get_locality_id();
    if (rank == 0)
    {
        timer_channel_0 = hpx::lcos::channel<double>(hpx::find_here());
        timer_channel_0.register_as("benchmark/timer/0");
        timer_channel_1.connect_to("benchmark/timer/1");
        send_channel = hpx::lcos::channel<std::vector<double>>(hpx::find_here());
        send_channel.register_as("benchmark/send");
        recv_channel.connect_to("benchmark/recv");
        benchmark::RunSpecifiedBenchmarks();
    }
    else
    {
        timer_channel_0.connect_to("benchmark/timer/0");
        timer_channel_1 = hpx::lcos::channel<double>(hpx::find_here());
        timer_channel_1.register_as("benchmark/timer/1");
        send_channel = hpx::lcos::channel<std::vector<double>>(hpx::find_here());
        send_channel.register_as("benchmark/recv");
        recv_channel.connect_to("benchmark/send");
        null_reporter reporter;
        benchmark::RunSpecifiedBenchmarks(&reporter);
    }

    return hpx::finalize();
}

int main(int argc, char **argv)
{
    benchmark::Initialize(&argc, argv);
    std::vector<std::string> const cfg = {
        "hpx.run_hpx_main!=1"
    };
    return hpx::init(argc, argv, cfg);
}

