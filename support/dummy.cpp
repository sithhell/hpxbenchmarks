// Copyright (c) 2017-2018 Thomas Heller
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

#include <benchmark/benchmark.h>
#include <chrono>

int dummy()
{
    int i = 0;
    benchmark::DoNotOptimize(i = 42);
    return i;
}

#include <iostream>

int dummy_timed(double delay)
{
    auto start = std::chrono::high_resolution_clock::now();
    int i = 0;
    while (true)
    {
        ++i;
        benchmark::DoNotOptimize(i);
		auto now = std::chrono::high_resolution_clock::now();
		double s = std::chrono::duration_cast<std::chrono::nanoseconds>(now-start).count();
        if (s >= delay)
            break;
    }

    return i;
}
