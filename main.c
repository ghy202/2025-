#include "gesture.h"
#include <signal.h>

volatile sig_atomic_t stop = 0;
void handle_signal(int sig) {
    stop = 1;
}

int main() {
    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);
    
    gesture_init();
    
    while (!stop) {
        gesture_process();
    }
    
    adc_close();
    i2c_close();
    
    return 0;
}