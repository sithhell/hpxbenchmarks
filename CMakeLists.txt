# Copyright (c) 2018 Thomas Heller

cmake_minimum_required(VERSION 3.5)

project(hpxbenchmarks CXX)

find_package(HPX REQUIRED)
find_package(TBB)
find_package(OpenMP REQUIRED)
find_package(MPI)

set(BENCHMARK_ENABLE_TESTING OFF CACHE BOOL "")
add_subdirectory(google_benchmark)
add_subdirectory(support)
add_subdirectory(tasks)
add_subdirectory(scheduling)
add_subdirectory(distributed)

