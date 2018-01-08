
add_executable(serialization_overhead serialization_overhead.cpp)
target_link_libraries(serialization_overhead benchmark dummy)
hpx_setup_target(serialization_overhead)

add_executable(async_latency async_latency.cpp)
target_link_libraries(async_latency benchmark dummy)
hpx_setup_target(async_latency)

add_executable(mpi_latency mpi_latency.cpp)
target_include_directories(mpi_latency PUBLIC ${MPI_CXX_INCLUDE_PATH})
target_link_libraries(mpi_latency benchmark dummy ${MPI_C_LIBRARIES} ${MPI_LIBRARY})
target_compile_options(mpi_latency PUBLIC ${MPI_CXX_COMPILE_FLAGS})
hpx_setup_target(mpi_latency)

find_package(OpenMP REQUIRED)
add_executable(components components.cpp)
target_link_libraries(components benchmark dummy)
hpx_setup_target(components)

add_executable(channel_send_recv channel_send_recv.cpp)
target_link_libraries(channel_send_recv benchmark dummy)
hpx_setup_target(channel_send_recv)

add_executable(broadcast broadcast.cpp)
target_link_libraries(broadcast benchmark dummy)
hpx_setup_target(broadcast)

add_executable(mpi_broadcast mpi_broadcast.cpp)
target_link_libraries(mpi_broadcast benchmark dummy)
target_include_directories(mpi_broadcast PUBLIC ${MPI_CXX_INCLUDE_PATH})
target_link_libraries(mpi_broadcast benchmark dummy ${MPI_C_LIBRARIES} ${MPI_LIBRARY})
target_compile_options(mpi_broadcast PUBLIC ${MPI_CXX_COMPILE_FLAGS})
hpx_setup_target(mpi_broadcast)
