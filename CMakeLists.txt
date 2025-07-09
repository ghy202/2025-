cmake_minimum_required(VERSION 3.10)
project(gesture_recognition)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -O2")

set(CMAKE_C_COMPILER "loongarch64-linux-gnu-gcc")
set(CMAKE_CXX_COMPILER "loongarch64-linux-gnu-g++")

include_directories(
    include
    include/bsp
)

add_executable(gesture_recognition
    src/main.c
    src/gesture.c
    src/oled.c
    src/bsp/adc.c
    src/bsp/i2c.c
    src/bsp/neural_network.c
)

target_link_libraries(gesture_recognition m)