add_executable(coroutines_overhead coroutines_overhead.cpp)
target_link_libraries(coroutines_overhead benchmark dummy)
hpx_setup_target(coroutines_overhead)

add_executable(omp_overhead omp_overhead.cpp)
target_link_libraries(omp_overhead benchmark dummy )
target_compile_options(omp_overhead PUBLIC ${OpenMP_CXX_FLAGS})
set_target_properties(omp_overhead PROPERTIES LINK_FLAGS ${OpenMP_CXX_FLAGS})
hpx_setup_target(omp_overhead)

add_executable(tbb_overhead tbb_overhead.cpp)
target_link_libraries(tbb_overhead benchmark dummy ${TBB_PROXY_LIBRARY})
target_include_directories(tbb_overhead PUBLIC ${TBB_INCLUDE_DIR})
hpx_setup_target(tbb_overhead)

add_executable(std_thread_overhead std_thread_overhead.cpp)
target_link_libraries(std_thread_overhead benchmark dummy)
hpx_setup_target(std_thread_overhead)

add_executable(hpx_thread_overhead hpx_thread_overhead.cpp)
target_link_libraries(hpx_thread_overhead benchmark dummy)
hpx_setup_target(hpx_thread_overhead)

add_executable(future_overhead future_overhead.cpp)
target_link_libraries(future_overhead benchmark dummy)
hpx_setup_target(future_overhead)
