// Copyright (c) 2017-2018 Thomas Heller
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

#include <benchmark/benchmark.h>
#include <hpx/hpx_main.hpp>
#include <hpx/runtime/serialization/detail/preprocess.hpp>
#include <hpx/include/serialization.hpp>
#include <hpx/include/async.hpp>
#include <hpx/include/actions.hpp>
#include <hpx/include/components.hpp>

#include <support/dummy.hpp>

struct simple_component
  : hpx::components::component_base<simple_component>
{
    int foo()
    {
        return dummy();
    }
    HPX_DEFINE_COMPONENT_ACTION(simple_component, foo, foo_action);
    HPX_DEFINE_COMPONENT_DIRECT_ACTION(simple_component, foo, foo_direct_action);
};

struct managed_component
  : hpx::components::managed_component_base<managed_component>
{
    int foo()
    {
        return dummy();
    }
    HPX_DEFINE_COMPONENT_ACTION(managed_component, foo, foo_action);
    HPX_DEFINE_COMPONENT_DIRECT_ACTION(managed_component, foo, foo_direct_action);
};


typedef
  hpx::components::component<simple_component>
  simple_component_server;
HPX_REGISTER_COMPONENT(simple_component_server, component_server);

typedef
  hpx::components::managed_component<managed_component>
  managed_component_server;
HPX_REGISTER_COMPONENT(managed_component_server, managed_component_server);

static void simple_component_local(benchmark::State& state)
{
    hpx::id_type dest = hpx::find_here();
    for (auto _: state)
    {
        hpx::id_type id = hpx::new_<simple_component>(dest).get();
    }
}
BENCHMARK(simple_component_local)
    ->UseRealTime()
    ;

static void simple_component_remote(benchmark::State& state)
{
    hpx::id_type dest = hpx::find_all_localities()[1];
    for (auto _: state)
    {
        hpx::id_type id = hpx::new_<simple_component>(dest).get();
    }
}
BENCHMARK(simple_component_remote)
    ->UseRealTime()
    ;

static void simple_component_action_ptr(benchmark::State& state)
{
    hpx::id_type dest = hpx::find_here();
    hpx::id_type id = hpx::new_<simple_component>(dest).get();
    auto ptr = hpx::get_ptr<simple_component>(id).get();
    for (auto _: state)
    {
        benchmark::DoNotOptimize(ptr->foo());
    }
}
BENCHMARK(simple_component_action_ptr)
    ->UseRealTime()
    ;

static void simple_component_action_id(benchmark::State& state)
{
    hpx::id_type dest = hpx::find_here();
    hpx::id_type id = hpx::new_<simple_component>(dest).get();
    for (auto _: state)
    {
        simple_component::foo_action act;
        benchmark::DoNotOptimize(act(id));
    }
}
BENCHMARK(simple_component_action_id)
    ->UseRealTime()
    ;

static void simple_component_direct_action_id(benchmark::State& state)
{
    hpx::id_type dest = hpx::find_here();
    hpx::id_type id = hpx::new_<simple_component>(dest).get();
    for (auto _: state)
    {
        simple_component::foo_direct_action act;
        benchmark::DoNotOptimize(act(id));
    }
}
BENCHMARK(simple_component_action_id)
    ->UseRealTime()
    ;

static void simple_component_action_id_remote(benchmark::State& state)
{
    hpx::id_type dest = hpx::find_all_localities()[1];
    hpx::id_type id = hpx::new_<simple_component>(dest).get();
    for (auto _: state)
    {
        simple_component::foo_action act;
        benchmark::DoNotOptimize(act(id));
    }
}
BENCHMARK(simple_component_action_id_remote)
    ->UseRealTime()
    ;

static void simple_component_direct_action_id_remote(benchmark::State& state)
{
    hpx::id_type dest = hpx::find_all_localities()[1];
    hpx::id_type id = hpx::new_<simple_component>(dest).get();
    for (auto _: state)
    {
        simple_component::foo_direct_action act;
        benchmark::DoNotOptimize(act(id));
    }
}
BENCHMARK(simple_component_action_id_remote)
    ->UseRealTime()
    ;

static void managed_component_local(benchmark::State& state)
{
    hpx::id_type dest = hpx::find_here();
    for (auto _: state)
    {
        hpx::id_type id = hpx::new_<managed_component>(dest).get();
    }
}
BENCHMARK(managed_component_local)
    ->UseRealTime()
    ;

static void managed_component_remote(benchmark::State& state)
{
    hpx::id_type dest = hpx::find_all_localities()[1];
    for (auto _: state)
    {
        hpx::id_type id = hpx::new_<managed_component>(dest).get();
    }
}
BENCHMARK(managed_component_remote)
    ->UseRealTime()
    ;

static void managed_component_action_ptr(benchmark::State& state)
{
    hpx::id_type dest = hpx::find_here();
    hpx::id_type id = hpx::new_<managed_component>(dest).get();
    auto ptr = hpx::get_ptr<managed_component>(id).get();
    for (auto _: state)
    {
        benchmark::DoNotOptimize(ptr->foo());
    }
}
BENCHMARK(managed_component_action_ptr)
    ->UseRealTime()
    ;

static void managed_component_action_id(benchmark::State& state)
{
    hpx::id_type dest = hpx::find_here();
    hpx::id_type id = hpx::new_<managed_component>(dest).get();
    for (auto _: state)
    {
        managed_component::foo_action act;
        benchmark::DoNotOptimize(act(id));
    }
}
BENCHMARK(managed_component_action_id)
    ->UseRealTime()
    ;

static void managed_component_direct_action_id(benchmark::State& state)
{
    hpx::id_type dest = hpx::find_here();
    hpx::id_type id = hpx::new_<managed_component>(dest).get();
    for (auto _: state)
    {
        managed_component::foo_direct_action act;
        benchmark::DoNotOptimize(act(id));
    }
}
BENCHMARK(managed_component_action_id)
    ->UseRealTime()
    ;

static void managed_component_action_id_remote(benchmark::State& state)
{
    hpx::id_type dest = hpx::find_all_localities()[1];
    hpx::id_type id = hpx::new_<managed_component>(dest).get();
    for (auto _: state)
    {
        managed_component::foo_action act;
        benchmark::DoNotOptimize(act(id));
    }
}
BENCHMARK(managed_component_action_id_remote)
    ->UseRealTime()
    ;

static void managed_component_direct_action_id_remote(benchmark::State& state)
{
    hpx::id_type dest = hpx::find_all_localities()[1];
    hpx::id_type id = hpx::new_<managed_component>(dest).get();
    for (auto _: state)
    {
        managed_component::foo_direct_action act;
        benchmark::DoNotOptimize(act(id));
    }
}
BENCHMARK(managed_component_action_id_remote)
    ->UseRealTime()
    ;

int main(int argc, char **argv)
{
    benchmark::Initialize(&argc, argv);
    benchmark::RunSpecifiedBenchmarks();

    return 0;
}
