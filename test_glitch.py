from glitch_engine import GlitchEngine
from PIL import Image
import numpy as np
import os

def create_dummy_image():
    # Create a 100x100 gradient image
    data = np.zeros((100, 100, 3), dtype=np.uint8)
    for i in range(100):
        data[i, :, 0] = i * 2.5  # Red gradient
        data[:, i, 1] = i * 2.5  # Green gradient
    
    img = Image.fromarray(data)
    img.save("test_input.png")
    print("Created test_input.png")
    return "test_input.png"

def main():
    print("Running Glitch Engine Test...")
    
    # 1. Create Input
    input_path = create_dummy_image()
    
    # 2. Initialize Engine
    engine = GlitchEngine(input_path)
    
    # 3. Apply Stuck-at-0 on Bit 7 (MSB) - Should be very visible
    print("Applying Stuck-at-0 on MSB...")
    result = engine.corrupt(fault_type='stuck_at_0', target_bit=7, probability=1.0)
    result.save("test_output_stuck0.png")
    print("Saved test_output_stuck0.png")
    
    # 4. Apply Bit Flip
    print("Applying Bit Flip...")
    result = engine.corrupt(fault_type='bit_flip', probability=0.1)
    result.save("test_output_flip.png")
    print("Saved test_output_flip.png")
    
    print("Test Complete. Check the output images.")

if __name__ == "__main__":
    main()
