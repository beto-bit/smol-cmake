cmake_minimum_required(VERSION 3.21)

project(Smol)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# I hate CMake
include(vcpkg/scripts/buildsystems/vcpkg.cmake)

add_executable(main src/main.cpp src/add.hpp)
target_include_directories(main PRIVATE include)

find_package(fmt CONFIG REQUIRED)
target_link_libraries(main PRIVATE fmt::fmt)

