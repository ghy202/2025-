#ifndef __I2C_H__
#define __I2C_H__

#include <stdint.h>

// I2C初始化
int i2c_init(uint8_t bus, uint8_t addr);

// I2C写操作
int i2c_write(uint8_t reg, const uint8_t *data, uint32_t len);

// I2C读操作
int i2c_read(uint8_t reg, uint8_t *data, uint32_t len);

// I2C关闭
void i2c_close();

#endif