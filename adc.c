#include "bsp/adc.h"
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define ADC_BASE_PATH "/sys/bus/iio/devices/iio:device0/in_voltage"
#define ADC_PATH_LEN 64

static int adc_fds[5] = {-1, -1, -1, -1, -1};

int adc_init() {
    char path[ADC_PATH_LEN];
    
    for (int i = 0; i < 5; i++) {
        snprintf(path, ADC_PATH_LEN, "%s%d_raw", ADC_BASE_PATH, i);
        adc_fds[i] = open(path, O_RDONLY);
        if (adc_fds[i] < 0) {
            perror("Failed to open ADC channel");
            return -1;
        }
    }
    return 0;
}

uint16_t adc_read(uint8_t channel) {
    if (channel >= 5) return 0;
    
    char buffer[16];
    lseek(adc_fds[channel], 0, SEEK_SET);
    ssize_t bytes_read = read(adc_fds[channel], buffer, sizeof(buffer)-1);
    
    if (bytes_read <= 0) {
        return 0;
    }
    
    buffer[bytes_read] = '\0';
    return (uint16_t)atoi(buffer);
}

void adc_close() {
    for (int i = 0; i < 5; i++) {
        if (adc_fds[i] >= 0) {
            close(adc_fds[i]);
            adc_fds[i] = -1;
        }
    }
}