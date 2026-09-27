// ====================PREDICTION====================
using Sample = std::array<float, 3>; // x, y, z values

#include "gesture_queue.h"
#include "data_processing.h" 
#include "ai_impl.h"

#define ALPHA 0.2

#define SAMPLES_IN_BUFFER 50 
#define WINDOW_SIZE 20
#define STRIDE 10
#define NUM_STATS 14

#define X_PIN 4
#define Y_PIN 5
#define Z_PIN 6
#define BUTTON_PIN 7

Queue queue;
int last_pred = -1;

void setup() {
    Serial.begin(115200);
    pinMode(BUTTON_PIN, INPUT_PULLUP);
  
    // while (!Serial) delay(10); 

    Serial.println("Finished setup. ");
}

void loop() {
    int button_state = digitalRead(BUTTON_PIN);

    // if (button_state == LOW) {
    //     delay(50); // debounce
    float x_raw = analogRead(X_PIN);
    float y_raw = analogRead(Y_PIN);
    float z_raw = analogRead(Z_PIN);

    float overall_stats[4*NUM_STATS];
    bool res = queue.on_new_sample(x_raw, y_raw, z_raw, overall_stats);

    if (res) { 
        int pred = predict_consensus_gesture(overall_stats);

        if (pred != -1 && pred != last_pred) {
        //     const char* stat_names[] = {
        //         "x_mean", "y_mean", "z_mean", "dvm_mean",
        //         "x_min", "y_min", "z_min",
        //         "x_max", "y_max", "z_max", "dvm_max",
        //         "cov_xy", "cov_yz", "cov_xz"
        //     };

        //     Serial.println("Statistics: ");
        //     for (int i = 0; i < 14; i++) {
        //         Serial.printf("%s: %.4f\n", stat_names[i], overall_stats[i]);
        //     }
            Serial.printf("Predicted Gesture: %d\n", pred); 
            last_pred = pred;
        }
    }

    //     while (digitalRead(BUTTON_PIN) == LOW) {
    //         delay(10); // wait for button release
    //     }
    // }

    delay(20);
}










// //====================Recording====================
// #include <array>

// #define SAMPLES_IN_BUFFER 50 
// #define X_PIN 4
// #define Y_PIN 5
// #define Z_PIN 6
// #define BUTTON_PIN 7

// // Change this number depending on which gesture you are recording (0, 1, 2, or 3)
// const int CURRENT_GESTURE_ID = 2; 

// using Sample = std::array<float, 3>; // x, y, z values

// Sample buffer[SAMPLES_IN_BUFFER];

// void setup() {
//     Serial.begin(115200);
//     while (!Serial) {
//         delay(10);
//     }
//     pinMode(BUTTON_PIN, INPUT_PULLUP);

//     // Print CSV Header once on boot so get_data.py recognizes it
//     for (int i = 0; i < SAMPLES_IN_BUFFER; ++i) {
//         Serial.printf("X_%d,Y_%d,Z_%d,", i, i, i);
//     }
//     Serial.println("gesture_id");

//     Serial.println("Setup finished. Press the button and perform a gesture!");
// }

// void loop() {
//     // Wait for button press (Active Low with INPUT_PULLUP)
//     // if (digitalRead(BUTTON_PIN) == LOW) {
//     //     delay(50); // Debounce delay
        
//     //     if (digitalRead(BUTTON_PIN) == LOW) {
//             // Record 50 samples at 50Hz (20ms interval)
//     for (int i = 0; i < SAMPLES_IN_BUFFER; ++i) {
//         buffer[i][0] = static_cast<float>(analogRead(X_PIN));
//         buffer[i][1] = static_cast<float>(analogRead(Y_PIN));
//         buffer[i][2] = static_cast<float>(analogRead(Z_PIN));
//         delay(20); // 20ms delay for 50Hz sampling rate
//     }

//     // Output all 50 samples in a single comma-separated row
//     for (int i = 0; i < SAMPLES_IN_BUFFER; ++i) {
//         Serial.printf("%.1f,%.1f,%.1f,", buffer[i][0], buffer[i][1], buffer[i][2]);
//     }
//     // Append the gesture ID at the very end of the row
//     Serial.println(CURRENT_GESTURE_ID);
//     //         // Wait until button is released to prevent immediate re-triggering
//     //         while (digitalRead(BUTTON_PIN) == LOW) {
//     //             delay(10);
//     //         }
//     //         delay(50); // Post-release debounce
//     //     }
//     // }

//     delay(10);
// }