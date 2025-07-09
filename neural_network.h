#ifndef __NEURAL_NETWORK_H__
#define __NEURAL_NETWORK_H__

#include <stdint.h>

// 神经网络初始化
void nn_init();

// 执行神经网络推理
int nn_inference(const float *input, float *output);

// 获取最佳匹配手势ID
int nn_get_best_match(const float *output);

#endif