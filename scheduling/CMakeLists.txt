
add_executable(seq_scheduling seq_scheduling.cpp)
target_link_libraries(seq_scheduling benchmark dummy)
hpx_setup_target(seq_scheduling)

add_executable(std_scheduling std_scheduling.cpp)
target_link_libraries(std_scheduling benchmark dummy)
hpx_setup_target(std_scheduling)

add_executable(hpx_scheduling hpx_scheduling.cpp)
target_link_libraries(hpx_scheduling benchmark dummy)
hpx_setup_target(hpx_scheduling)

add_executable(omp_scheduling omp_scheduling.cpp)
target_link_libraries(omp_scheduling benchmark dummy)
target_compile_options(omp_scheduling PUBLIC ${OpenMP_CXX_FLAGS})
hpx_setup_target(omp_scheduling)
set_target_properties(omp_scheduling PROPERTIES LINK_FLAGS ${OpenMP_CXX_FLAGS})

add_executable(tbb_scheduling tbb_scheduling.cpp)
target_link_libraries(tbb_scheduling benchmark dummy ${TBB_PROXY_LIBRARY})
target_include_directories(tbb_scheduling PUBLIC ${TBB_INCLUDE_DIR})
hpx_setup_target(tbb_scheduling)
