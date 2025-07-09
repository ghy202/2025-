#include "gesture.h"
#include "oled.h"
#include "bsp/adc.h"
#include "bsp/neural_network.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <math.h>

#define SAMPLE_COUNT 5
#define SAMPLE_DELAY_MS 50
#define FILTER_FACTOR 0.3

const char* GESTURE_NAMES[12] = {
    "OK", "厉害", "你", "抗议", "谢谢", 
    "无语", "疑问", "明天见", "好", "对不起", 
    "没关系", "喜欢"
};

static float filtered_values[5] = {0};

void gesture_init(void) {
    if (adc_init() < 0) {
        fprintf(stderr, "ADC init failed\n");
        exit(1);
    }
    
    if (i2c_init(1, 0x3C) < 0) {
        fprintf(stderr, "I2C init failed\n");
        exit(1);
    }
    
    OLED_Init();
    
    nn_init();
    
    OLED_ShowString(0, 0, "Gesture System", 16);
    OLED_ShowString(0, 2, "Initializing...", 16);
    sleep(1);
    OLED_Clear();
    
    for (int ch = 0; ch < 5; ch++) {
        filtered_values[ch] = adc_read(ch);
    }
}

void gesture_process(void) {
    float averages[5] = {0};
    char displayBuffer[50];
    
    for (int i = 0; i < SAMPLE_COUNT; i++) {
        for (int ch = 0; ch < 5; ch++) {
            uint16_t raw_value = adc_read(ch);
            filtered_values[ch] = FILTER_FACTOR * raw_value + 
                                  (1 - FILTER_FACTOR) * filtered_values[ch];
            averages[ch] += filtered_values[ch];
        }
        usleep(SAMPLE_DELAY_MS * 1000);
    }
    
    for (int ch = 0; ch < 5; ch++) {
        averages[ch] /= SAMPLE_COUNT;
    }

    float input[5];
    for (int i = 0; i < 5; i++) {
        input[i] = averages[i] / 1024.0f; 
    }


    float output[12];
    nn_inference(input, output);

    int best_match = nn_get_best_match(output);

    OLED_Clear();
    
    sprintf(displayBuffer, "ID:%d Prob:%.2f", best_match + 1, output[best_match]);
    OLED_ShowString(0, 0, displayBuffer, 16);
    
    sprintf(displayBuffer, "A0:%.0f A1:%.0f", averages[0], averages[1]);
    OLED_ShowString(0, 2, displayBuffer, 16);
    
    switch(best_match) {
        case 0: // OK
            OLED_ShowString(40, 4, "OK", 16);
            break;
        case 1: // 厉害
            OLED_ShowChinese(40, 4, 0, 16); // 厉
            OLED_ShowChinese(56, 4, 1, 16); // 害
            break;
        case 2: // 你
            OLED_ShowChinese(56, 4, 2, 16);
            break;
        case 3: // 抗议
            OLED_ShowChinese(32, 4, 3, 16); // 抗
            OLED_ShowChinese(48, 4, 4, 16); // 议
            break;
        case 4: // 谢谢
            OLED_ShowChinese(40, 4, 5, 16); // 谢
            OLED_ShowChinese(56, 4, 5, 16); // 谢
            break;
        case 5: // 无语
            OLED_ShowChinese(40, 4, 6, 16); // 无
            OLED_ShowChinese(56, 4, 7, 16); // 语
            break;
        case 6: // 疑问
            OLED_ShowChinese(32, 4, 8, 16); // 疑
            OLED_ShowChinese(48, 4, 9, 16); // 问
            break;
        case 7: // 明天见
            OLED_ShowChinese(20, 4, 10, 16); // 明
            OLED_ShowChinese(36, 4, 11, 16); // 天
            OLED_ShowChinese(52, 4, 12, 16); // 见
            break;
        case 8: // 好
            OLED_ShowChinese(56, 4, 13, 16);
            break;
        case 9: // 对不起
            OLED_ShowChinese(20, 4, 14, 16); // 对
            OLED_ShowChinese(36, 4, 15, 16); // 不
            OLED_ShowChinese(52, 4, 16, 16); // 起
            break;
        case 10: // 没关系
            OLED_ShowChinese(20, 4, 17, 16); // 没
            OLED_ShowChinese(36, 4, 18, 16); // 关
            OLED_ShowChinese(52, 4, 19, 16); // 系
            break;
        case 11: // 喜欢
            OLED_ShowChinese(40, 4, 20, 16); // 喜
            OLED_ShowChinese(56, 4, 21, 16); // 欢
            break;
    }
    
    sprintf(displayBuffer, "Confidence: %.0f%%", output[best_match] * 100);
    OLED_ShowString(0, 6, displayBuffer, 16);
    
    usleep(500000); 
}