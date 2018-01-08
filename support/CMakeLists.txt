
add_library(dummy dummy.cpp)
target_link_libraries(dummy benchmark)
target_include_directories(dummy PUBLIC ${CMAKE_SOURCE_DIR})
