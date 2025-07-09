#!/bin/bash

# 创建构建目录
mkdir -p build
cd build

# 配置CMake
cmake -DCMAKE_TOOLCHAIN_FILE=../toolchain-loongarch64.cmake ..

# 编译
make -j$(nproc)

# 复制到目标设备
scp gesture_recognition user@loongson-device:/home/user/