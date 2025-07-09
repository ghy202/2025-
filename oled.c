#include "oled.h"
#include "bsp/i2c.h"
#include <string.h>

#define OLED_CMD   0x00
#define OLED_DATA  0x40

void OLED_Set_Pos(uint8_t x, uint8_t y) {
    uint8_t cmd[3];
    cmd[0] = 0xB0 | (y & 0x07);
    cmd[1] = ((x & 0xF0) >> 4) | 0x10;
    cmd[2] = x & 0x0F;
    i2c_write(OLED_CMD, cmd, 3);
}

void OLED_Init(void) {
    uint8_t init_seq[] = {
        0xAE, 0x00, 0x10, 0x40, 0x81, 0xCF, 0xA1, 0xC8, 
        0xA6, 0xA8, 0x3F, 0xD3, 0x00, 0xD5, 0x80, 0xD9, 
        0xF1, 0xDA, 0x12, 0xDB, 0x40, 0x20, 0x02, 0x8D, 
        0x14, 0xA4, 0xA6, 0xAF
    };
    
    i2c_write(OLED_CMD, init_seq, sizeof(init_seq));
    OLED_Clear();
}

void OLED_Clear(void) {
    for (uint8_t i = 0; i < 8; i++) {
        OLED_Set_Pos(0, i);
        uint8_t zeros[128] = {0};
        i2c_write(OLED_DATA, zeros, sizeof(zeros));
    }
}

void OLED_ShowChar(uint8_t x, uint8_t y, char chr, uint8_t sizey) {
    if (sizey == 8) {
        uint8_t char_data[6] = {0}; // 6x8字符
        OLED_Set_Pos(x, y);
        i2c_write(OLED_DATA, char_data, 6);
    } else if (sizey == 16) {
        uint8_t char_data[16] = {0}; // 8x16字符
        OLED_Set_Pos(x, y);
        i2c_write(OLED_DATA, char_data, 16);
    }
}

void OLED_ShowString(uint8_t x, uint8_t y, const char *str, uint8_t sizey) {
    while (*str) {
        OLED_ShowChar(x, y, *str, sizey);
        if (sizey == 8) x += 6;
        else x += 8;
        str++;
    }
}

void OLED_ShowChinese(uint8_t x, uint8_t y, uint8_t no, uint8_t sizey) {

    if (sizey == 16) {
        uint8_t char_data[32] = {0}; // 16x16汉字
        OLED_Set_Pos(x, y);
        i2c_write(OLED_DATA, char_data, 16);
        OLED_Set_Pos(x, y + 1);
        i2c_write(OLED_DATA, char_data + 16, 16);
    }
}