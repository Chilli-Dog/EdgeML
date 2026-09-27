import serial
import time

PORT = 'COM8'  # Update to your current port
BAUD_RATE = 115200
OUTPUT_FILE = 'gesture_dataset.csv'

def is_valid_csv_line(line):
    # Ignore bootloader output strings
    if any(boot_str in line for boot_str in ['Build:', 'rst:', 'SPIWP:', 'mode:', 'load:', 'entry']):
        return False
    # Ensure line starts with the header or a numeric raw sample reading
    if line.startswith("X_0") or line[0].isdigit() or line[0] == '-':
        return True
    return False

def record_serial_to_csv():
    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
        ser.dtr = True  # <--- Add this line
        print(f"Connected to {PORT} at {BAUD_RATE} baud.")
        time.sleep(2)
        
        gesture_count = 0
        
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as file:
            print(f"Recording data to {OUTPUT_FILE}... Press Ctrl+C to stop.\n")
            
            while True:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    
                    # Filter out empty strings and ESP32 boot log messages
                    if line and is_valid_csv_line(line):
                        file.write(line + '\n')
                        file.flush()
                        
                        if line.startswith("X_0"):
                            print("Received CSV Header.")
                        else:
                            gesture_count += 1
                            label = line.split(',')[-1]
                            print(f"Captured gesture #{gesture_count} (Label: {label})")

    except serial.SerialException as e:
        print(f"Serial Port Error: {e}")
    except KeyboardInterrupt:
        print("\nData collection stopped by user.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial connection closed.")

if __name__ == "__main__":
    record_serial_to_csv()