#ifndef __ADC_H__
#define __ADC_H__

#include <stdint.h>

// ADC初始化
int adc_init();

// 读取指定通道的ADC值
uint16_t adc_read(uint8_t channel);

// 关闭ADC
void adc_close();

#endif