# Glitch Art Memory Corruptor

**A Software Simulation of Hardware Failures**

This project bridges the gap between Digital Design, Computer Organization (DDCO), and visual creativity. It simulates how hardware faults—like "stuck-at" bits or cosmic ray bit flips—affect data stored in RAM.

##  Quick Start

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Simulation**:
    ```bash
    streamlit run app.py
    ```
    This will open the "Chaos Engine" interface in your web browser.

##  Core Concepts

### 1. The Logic: Bitwise Operations
The core engine treats the image as a raw byte array (simulated RAM) and applies bitwise operators:

*   **Stuck-at-0 (Broken Gate)**: Forces a bit to 0 using Bitwise AND (`&`).
    *   `byte = byte & 11101111` (Forces 5th bit to 0)
*   **Stuck-at-1 (Broken Gate)**: Forces a bit to 1 using Bitwise OR (`|`).
    *   `byte = byte | 00010000` (Forces 5th bit to 1)
*   **Bit Flips (Cosmic Rays)**: Randomly flips a bit using Bitwise XOR (`^`).
    *   `byte = byte ^ 00000001` (Flips LSB)

### 2. DDCO Demonstrations
*   **Bit Significance**: Use the "Target Bit" slider. Notice how flipping Bit 7 (MSB) destroys the image, while Bit 0 (LSB) just adds noise.
*   **Endianness**: The "Swap Endianness" toggle simulates reading 32-bit words in the wrong byte order (Little vs Big Endian), scrambling the color channels.
*   **Memory Mapping**: Use the Channel Isolation checkboxes to apply corruption only to specific memory blocks (Red, Green, or Blue channels).

## Tech Stack
*   **Python**: Core logic.
*   **NumPy**: Efficient array manipulation and bitwise operations.
*   **Pillow (PIL)**: Image processing.
*   **Streamlit**: Interactive web interface.

## Project Structure
*   `app.py`: The interactive frontend.
*   `glitch_engine.py`: The backend logic handling byte manipulation.
*   `requirements.txt`: Project dependencies.

