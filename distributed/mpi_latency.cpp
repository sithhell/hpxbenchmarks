// Copyright (c) 2017-2018 Thomas Heller
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

#include <benchmark/benchmark.h>

#include <mpi.h>

#include <support/dummy.hpp>
#include <support/null_reporter.hpp>

#include <iostream>

static void mpi_isend_irecv(benchmark::State& state)
{
    std::size_t size = state.range(0);
    std::size_t window = state.range(1);
    int rank = 0;
    int dst_rank = 0;
    int comm_size = 0;

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &comm_size);
    if(rank == 0)
    {
        dst_rank = 1;
    }
    else
    {
        dst_rank = 0;
    }
    MPI_Barrier(MPI_COMM_WORLD);

    for (auto _: state)
    {
        MPI_Barrier(MPI_COMM_WORLD);
        double start = MPI_Wtime();
        std::vector<double> src(size);
        std::vector<double> dst(size);
        std::vector<MPI_Request> send_requests(window);
        std::vector<MPI_Request> recv_requests(window);
        for (std::size_t i = 0; i != window; ++i)
        {
            MPI_Isend(src.data(), size, MPI_DOUBLE, dst_rank, i,
                MPI_COMM_WORLD, &send_requests[i]);
            MPI_Irecv(dst.data(), size, MPI_DOUBLE, dst_rank, i,
                MPI_COMM_WORLD, &recv_requests[i]);
        }
        {
            std::vector<MPI_Status> status(window);
            MPI_Waitall(window, send_requests.data(), status.data());
        }
        {
            std::vector<MPI_Status> status(window);
            MPI_Waitall(window, recv_requests.data(), status.data());
        }
        double elapsed = MPI_Wtime() - start;

        double times[2];
        MPI_Allgather(&elapsed, 1, MPI_DOUBLE, &times, 2, MPI_DOUBLE, MPI_COMM_WORLD);

        state.SetIterationTime(std::max(times[0], times[1]));
    }
    MPI_Barrier(MPI_COMM_WORLD);

    state.SetBytesProcessed(int64_t(state.iterations()) * int64_t(size * sizeof(double)) * window * 2);
}
BENCHMARK(mpi_isend_irecv)
    ->UseRealTime()
    ->RangeMultiplier(2)->Ranges({{1, 1024*1024}, {1, 128}})
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
