#ifndef __OLED_H__
#define __OLED_H__

#include <stdint.h>

// OLED初始化
void OLED_Init(void);

// OLED控制函数
void OLED_Clear(void);
void OLED_ShowChar(uint8_t x, uint8_t y, char chr, uint8_t sizey);
void OLED_ShowString(uint8_t x, uint8_t y, const char *str, uint8_t sizey);
void OLED_ShowChinese(uint8_t x, uint8_t y, uint8_t no, uint8_t sizey);

#endif