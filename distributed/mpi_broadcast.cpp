// Copyright (c) 2017-2018 Thomas Heller
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

#include <benchmark/benchmark.h>

#include <mpi.h>

#include <support/dummy.hpp>
#include <support/null_reporter.hpp>

#include <iostream>
#include <algorithm>

static void mpi_broadcast(benchmark::State& state)
{
    std::size_t size = state.range(0);
    int rank = 0;
    int comm_size = 0;

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &comm_size);
    MPI_Barrier(MPI_COMM_WORLD);

    for (auto _: state)
    {
        MPI_Barrier(MPI_COMM_WORLD);
        double start = MPI_Wtime();
        std::vector<double> src(size);

        MPI_Bcast(src.data(), size, MPI_DOUBLE, 0, MPI_COMM_WORLD);

        double elapsed = MPI_Wtime() - start;

        double result = 0.0;

        MPI_Allreduce(&elapsed, &result, 1, MPI_DOUBLE, MPI_MAX, MPI_COMM_WORLD);

        state.SetIterationTime(result);
    }
    MPI_Barrier(MPI_COMM_WORLD);

    state.SetBytesProcessed(int64_t(state.iterations()) * int64_t(size * sizeof(double)));
}
BENCHMARK(mpi_broadcast)
    ->UseRealTime()
    ->RangeMultiplier(2)->Range(1, 1024*1024)
    ->UseManualTime()
    ;

int main(int argc, char **argv)
{
    MPI_Init(&argc, &argv);
    benchmark::Initialize(&argc, argv);
    int rank = 0;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    if (rank == 0)
    {
        benchmark::RunSpecifiedBenchmarks();
    }
    else
    {
        null_reporter reporter;
        benchmark::RunSpecifiedBenchmarks(&reporter);
    }

    MPI_Finalize();

    return 0;
}
