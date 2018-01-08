// Copyright (c) 2017-2018 Thomas Heller
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

#include <benchmark/benchmark.h>
#include <hpx/hpx_main.hpp>
#include <hpx/async.hpp>
#include <hpx/runtime/serialization/detail/preprocess.hpp>
#include <hpx/include/serialization.hpp>

#include <support/dummy.hpp>

static void memcpy_double(benchmark::State& state)
{
    std::size_t size = state.range(0);
    std::vector<double> src(size);
    for (auto _: state)
    {
        std::vector<double> dst(size);
        memcpy(dst.data(), src.data(), size * sizeof(double));
    }
    state.SetBytesProcessed(int64_t(state.iterations()) * int64_t(size * sizeof(double)));
}
BENCHMARK(memcpy_double)
    ->UseRealTime()
    ->RangeMultiplier(2)->Range(1, 1024*1024)
    ;

template <typename T>
std::size_t get_archive_size(T const& p,
    std::uint32_t flags,
    std::vector<hpx::serialization::serialization_chunk>& chunks)
{
    // gather the required size for the archive
    hpx::serialization::detail::preprocess gather_size;
    hpx::serialization::output_archive archive(
        gather_size, flags, &chunks);
    archive << p;
    return gather_size.size();
}

static void hpx_double_output(benchmark::State& state)
{
    std::size_t size = state.range(0);
    std::vector<double> src(size);
    unsigned int flags = 0U;
    for (auto _: state)
    {
        std::vector<hpx::serialization::serialization_chunk> chunks;
        std::size_t buf_size = get_archive_size(src, flags, chunks);
        std::vector<char> buffer(buf_size);

        hpx::serialization::output_archive archive(
            buffer, flags, &chunks);
        archive << src;
    }
    state.SetBytesProcessed(int64_t(state.iterations()) * int64_t(size * sizeof(double)));
}
BENCHMARK(hpx_double_output)
    ->UseRealTime()
    ->RangeMultiplier(2)->Range(1, 1024*1024)
    ;

static void hpx_double_input(benchmark::State& state)
{
    std::size_t size = state.range(0);
    std::vector<double> src(size);
    std::vector<hpx::serialization::serialization_chunk> chunks;
    unsigned int flags = 0U;
    std::size_t buf_size = get_archive_size(src, flags, chunks);
    std::vector<char> buffer(buf_size);
    hpx::serialization::output_archive oarchive(
        buffer, flags, &chunks);
    oarchive << src;
    for (auto _: state)
    {
        std::vector<double> dst;
        hpx::serialization::input_archive archive(
            buffer, buf_size, &chunks);

        archive >> dst;
    }
    state.SetBytesProcessed(int64_t(state.iterations()) * int64_t(size * sizeof(double)));
}
BENCHMARK(hpx_double_input)
    ->UseRealTime()
    ->RangeMultiplier(2)->Range(1, 1024*1024)
    ;

void test_function(std::vector<double> const& v)
{}
HPX_PLAIN_ACTION(test_function, test_action)

static void hpx_parcel_double_output(benchmark::State& state)
{
    std::size_t size = state.range(0);
    unsigned int flags = 0U;
    hpx::naming::id_type const here = hpx::find_here();
    hpx::naming::address addr(hpx::get_locality(),
        hpx::components::component_invalid,
        reinterpret_cast<std::uint64_t>(&test_function));
    hpx::naming::gid_type dest = here.get_gid();
    std::vector<double> src(size);
    std::vector<hpx::serialization::serialization_chunk> chunks;
    hpx::parcelset::parcel outp(
        hpx::parcelset::detail::create_parcel::call(
            std::false_type(),
            std::move(dest), std::move(addr),
            test_action(), hpx::threads::thread_priority_normal, std::move(src)
        )
    );
    outp.set_source_id(here);

    for (auto _: state)
    {
        std::size_t buf_size = get_archive_size(outp, flags, chunks);
        std::vector<char> buffer(buf_size);

        hpx::serialization::output_archive archive(
            buffer, flags, &chunks);
        archive << outp;
    }
    state.SetBytesProcessed(int64_t(state.iterations()) * int64_t(size * sizeof(double)));
}
BENCHMARK(hpx_parcel_double_output)
    ->UseRealTime()
    ->RangeMultiplier(2)->Range(1, 1024*1024)
    ;

static void hpx_parcel_double_input(benchmark::State& state)
{
    std::size_t size = state.range(0);
    unsigned int flags = 0U;
    hpx::naming::id_type const here = hpx::find_here();
    hpx::naming::address addr(hpx::get_locality(),
        hpx::components::component_invalid,
        reinterpret_cast<std::uint64_t>(&test_function));
    hpx::naming::gid_type dest = here.get_gid();
    std::vector<double> src(size);
    std::vector<hpx::serialization::serialization_chunk> chunks;
    hpx::parcelset::parcel outp(
        hpx::parcelset::detail::create_parcel::call(
            std::false_type(),
            std::move(dest), std::move(addr),
            test_action(), hpx::threads::thread_priority_normal, std::move(src)
        )
    );
    outp.set_source_id(here);
    std::size_t buf_size = get_archive_size(outp, flags, chunks);
    std::vector<char> buffer(buf_size);

    hpx::serialization::output_archive oarchive(
        buffer, flags, &chunks);
    oarchive << outp;
    for (auto _: state)
    {
        hpx::parcelset::parcel inp;

        hpx::serialization::input_archive archive(
            buffer, buf_size, &chunks);

        archive >> inp;
    }
    state.SetBytesProcessed(int64_t(state.iterations()) * int64_t(size * sizeof(double)));
}
BENCHMARK(hpx_parcel_double_input)
    ->UseRealTime()
    ->RangeMultiplier(2)->Range(1, 1024*1024)
    ;

int main(int argc, char **argv)
{
    benchmark::Initialize(&argc, argv);
    benchmark::RunSpecifiedBenchmarks();

    return 0;
}
