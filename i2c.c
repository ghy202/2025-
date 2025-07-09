#include "bsp/i2c.h"
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <stdio.h>

static int i2c_fd = -1;

int i2c_init(uint8_t bus, uint8_t addr) {
    char filename[20];
    snprintf(filename, sizeof(filename), "/dev/i2c-%d", bus);
    
    i2c_fd = open(filename, O_RDWR);
    if (i2c_fd < 0) {
        perror("Failed to open I2C device");
        return -1;
    }
    
    if (ioctl(i2c_fd, I2C_SLAVE, addr) < 0) {
        perror("Failed to set I2C address");
        close(i2c_fd);
        i2c_fd = -1;
        return -1;
    }
    
    return 0;
}

int i2c_write(uint8_t reg, const uint8_t *data, uint32_t len) {
    uint8_t buffer[len + 1];
    buffer[0] = reg;
    
    for (uint32_t i = 0; i < len; i++) {
        buffer[i + 1] = data[i];
    }
    
    if (write(i2c_fd, buffer, len + 1) != (len + 1)) {
        perror("I2C write failed");
        return -1;
    }
    
    return 0;
}

int i2c_read(uint8_t reg, uint8_t *data, uint32_t len) {
    if (write(i2c_fd, &reg, 1) != 1) {
        perror("I2C register select failed");
        return -1;
    }
    
    if (read(i2c_fd, data, len) != (int)len) {
        perror("I2C read failed");
        return -1;
    }
    
    return 0;
}

void i2c_close() {
    if (i2c_fd >= 0) {
        close(i2c_fd);
        i2c_fd = -1;
    }
}