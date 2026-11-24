cmake_minimum_required(VERSION 3.20)

if(CMAKE_VERSION VERSION_GREATER_EQUAL 3.27)
    cmake_policy(SET CMP0148 NEW)
endif()

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD 20)

project(${SKBUILD_PROJECT_NAME}
    VERSION ${SKBUILD_PROJECT_VERSION}
    LANGUAGES CXX
)

set(PYBIND11_NEWPYTHON ON)
find_package(pybind11 REQUIRED)
find_package(uproot-custom REQUIRED)

# ==============================
#    Declare the C++ module
# ==============================
pybind11_add_module(_kernel
    my_reader.cc
)
target_include_directories(_kernel PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(_kernel PRIVATE uproot-custom)

# Install the module to the package directory
if(DEFINED SKBUILD_PROJECT_NAME)
    install(
        TARGETS _kernel
        LIBRARY DESTINATION ${SKBUILD_PROJECT_NAME}
    )
endif()
