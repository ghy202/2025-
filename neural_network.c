#include "bsp/neural_network.h"
#define INPUT_NODES 5
#define HIDDEN_NODES 8
#define OUTPUT_NODES 12

const float weights_input_hidden[INPUT_NODES][HIDDEN_NODES] = {0,
};

const float weights_hidden_output[HIDDEN_NODES][OUTPUT_NODES] = {0
};

float sigmoid(float x) {
    return 1.0f / (1.0f + expf(-x));
}

void nn_init() {
}

int nn_inference(const float *input, float *output) {
    float hidden[HIDDEN_NODES] = {0};
    
    for (int j = 0; j < HIDDEN_NODES; j++) {
        for (int i = 0; i < INPUT_NODES; i++) {
            hidden[j] += input[i] * weights_input_hidden[i][j];
        }
        hidden[j] = sigmoid(hidden[j]);
    }
    
    for (int k = 0; k < OUTPUT_NODES; k++) {
        output[k] = 0;
        for (int j = 0; j < HIDDEN_NODES; j++) {
            output[k] += hidden[j] * weights_hidden_output[j][k];
        }
        output[k] = sigmoid(output[k]);
    }
    
    return 0;
}

int nn_get_best_match(const float *output) {
    int best_index = 0;
    float best_value = output[0];
    
    for (int i = 1; i < OUTPUT_NODES; i++) {
        if (output[i] > best_value) {
            best_value = output[i];
            best_index = i;
        }
    }
    
    return best_index;
}