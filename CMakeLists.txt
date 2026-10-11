cmake_minimum_required(VERSION 3.16)

project(BOFProcessModel)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(include)

add_executable(
    bof_model
    src/main.cpp
    src/MaterialBalance.cpp
    src/ReactionModel.cpp
    src/ProcessModel.cpp
    src/EnergyBalance.cpp
    src/ScrapModel.cpp
    src/SimulationLogger.cpp
    src/DatasetGenerator.cpp
)