import numpy as np
from PIL import Image
import io

class GlitchEngine:
    def __init__(self, image_source):
        """
        Initialize with an image source (file path or bytes).
        """
        self.original_image = Image.open(image_source).convert('RGB')
        self.width, self.height = self.original_image.size
        # Convert to numpy array
        self.original_array = np.array(self.original_image)
        
    def get_memory_view(self):
        """
        Returns a flat byte array representing the image in RAM.
        """
        return self.original_array.flatten()

    def bytes_to_image(self, byte_data):
        """
        Converts the flat byte array back to an image.
        """
        # Ensure correct size
        expected_size = self.width * self.height * 3
        if len(byte_data) != expected_size:
            # Handle case where endianness swap might have padded/truncated? 
            # Usually shouldn't happen if we are careful.
            # Truncate or pad if necessary to prevent crash
            if len(byte_data) > expected_size:
                byte_data = byte_data[:expected_size]
            else:
                byte_data = np.pad(byte_data, (0, expected_size - len(byte_data)), 'constant')
                
        reshaped = byte_data.reshape((self.height, self.width, 3))
        return Image.fromarray(reshaped.astype('uint8'), 'RGB')

    def corrupt(self, 
                fault_type='none', 
                target_bit=0, 
                probability=0.01, 
                channels={'R': True, 'G': True, 'B': True},
                endian_swap=False,
                mask=None):
        """
        Main corruption logic.
        
        Args:
            fault_type: 'stuck_at_0', 'stuck_at_1', 'bit_flip', 'none'
            target_bit: 0-7 (which bit to target for stuck faults)
            probability: 0.0 to 1.0 (chance of fault occurring per byte)
            channels: Dict selecting which channels to affect
            endian_swap: Boolean, whether to simulate wrong endianness
            mask: Optional boolean numpy array (H, W). If provided, only corrupt True areas.
        """
        # Work on a copy of the flat memory
        data = self.original_array.copy()
        
        # 1. Memory Mapping / Channel Selection
        # We can use a mask to protect certain channels
        # Data is (Height, Width, 3)
        # We create a boolean mask of shape (H, W, 3)
        channel_mask = np.zeros_like(data, dtype=bool)
        if channels['R']: channel_mask[:, :, 0] = True
        if channels['G']: channel_mask[:, :, 1] = True
        if channels['B']: channel_mask[:, :, 2] = True
        
        # Apply Spatial Mask (T-Shirt Detection) if provided
        if mask is not None:
            # mask is (H, W), we need to broadcast to (H, W, 3)
            # Expand dims to (H, W, 1) so it broadcasts against (H, W, 3)
            spatial_mask = mask[:, :, np.newaxis]
            # Combine with channel mask
            channel_mask = channel_mask & spatial_mask
        
        # Flatten for bitwise operations
        flat_data = data.flatten()
        flat_mask = channel_mask.flatten()
        
        # Only apply operations where flat_mask is True
        # To do this efficiently, we'll generate noise/faults for everything 
        # but only apply them where the mask allows.
        
        # 2. Endianness Swap (Simulating reading data with wrong word alignment)
        if endian_swap:
            # Simulate 32-bit word swap (4 bytes)
            # Pad if not divisible by 4
            remainder = len(flat_data) % 4
            if remainder != 0:
                padding = 4 - remainder
                flat_data = np.pad(flat_data, (0, padding), 'constant')
                flat_mask = np.pad(flat_mask, (0, padding), 'constant', constant_values=False)
            
            # Reshape to N x 4
            view_32 = flat_data.reshape(-1, 4)
            # Swap bytes: e.g., [0, 1, 2, 3] -> [3, 2, 1, 0]
            view_32[:] = view_32[:, ::-1]
            flat_data = view_32.flatten()
            
            # Note: We swap back at the end? Or is the "glitch" that we display it swapped?
            # Usually endianness glitch means we interpret the bytes in wrong order.
            # If we just swap and display, the colors/pixels will be scrambled.
            # Let's keep it scrambled.
            
            # If we padded, we need to handle that when reshaping back, 
            # but bytes_to_image handles truncation.

        # 3. Apply Faults
        if fault_type != 'none':
            # Generate a random mask for probability
            # We want to affect 'probability' percent of the *selected* bytes
            # random_mask is True where we SHOULD apply the fault
            random_vals = np.random.random(flat_data.shape)
            active_faults = (random_vals < probability) & flat_mask
            
            if fault_type == 'stuck_at_0':
                # Bitwise AND with NOT(1 << target_bit)
                # e.g. target 5 (32): 11011111
                bit_mask = ~(1 << target_bit) & 0xFF
                # Apply only where active_faults is True
                # We use np.where: if active, apply AND, else keep original
                flat_data = np.where(active_faults, flat_data & bit_mask, flat_data)
                
            elif fault_type == 'stuck_at_1':
                # Bitwise OR with (1 << target_bit)
                bit_mask = (1 << target_bit)
                flat_data = np.where(active_faults, flat_data | bit_mask, flat_data)
                
            elif fault_type == 'bit_flip':
                bit_mask = (1 << target_bit)
                flat_data = np.where(active_faults, flat_data ^ bit_mask, flat_data)
            
            elif fault_type == 'burst_error':
                # Simulates a block of memory failing completely
                num_chunks = int(probability * 100)
                if num_chunks < 1: num_chunks = 1
                
                for _ in range(num_chunks):
                    start_idx = np.random.randint(0, len(flat_data))
                    length = np.random.randint(100, len(flat_data) // 100)
                    end_idx = min(start_idx + length, len(flat_data))
                    
                    # Check if this block overlaps with the mask
                    # If mask is provided, we only want to burst where mask is True
                    # We can just AND the burst with the mask
                    if np.any(flat_mask[start_idx:end_idx]):
                        # Generate noise
                        noise = np.random.randint(0, 255, size=(end_idx-start_idx))
                        # Apply noise only where mask is True in this block
                        block_mask = flat_mask[start_idx:end_idx]
                        flat_data[start_idx:end_idx] = np.where(block_mask, noise, flat_data[start_idx:end_idx])

            elif fault_type == 'sync_loss':
                # Simulates H-Sync/V-Sync loss by rolling the data
                # Probability determines the shift amount
                shift_amount = int(probability * len(flat_data) * 0.1)
                flat_data = np.roll(flat_data, shift_amount)
                
            elif fault_type == 'color_drift':
                # Multiplies values to cause overflow/wrapping
                # We'll multiply by a factor derived from target_bit (1 to 8)
                factor = target_bit + 1
                # We need to do this carefully to wrap around 255
                # Cast to uint16 to prevent early clipping, multiply, then mod 256
                temp_data = flat_data.astype(np.uint16)
                temp_data = np.where(active_faults, (temp_data * factor) % 256, temp_data)
                flat_data = temp_data.astype(np.uint8)

        # Convert back to image first
        glitched_image = self.bytes_to_image(flat_data)
        
        # 4. Apply Visual Outline (if mask provided)
        if mask is not None:
            # Convert to numpy to manipulate
            img_arr = np.array(glitched_image)
            
            # Calculate Edge of the mask
            # Edge = Mask AND (NOT Eroded_Mask)
            # We simulate erosion by checking neighbors
            p = np.pad(mask, 1, mode='constant', constant_values=False)
            
            # Check 4 neighbors (Up, Down, Left, Right)
            # If a pixel is True but any neighbor is False, it's an edge
            n_up = p[0:-2, 1:-1]
            n_down = p[2:, 1:-1]
            n_left = p[1:-1, 0:-2]
            n_right = p[1:-1, 2:]
            
            # Eroded is where pixel AND all neighbors are True
            eroded = mask & n_up & n_down & n_left & n_right
            
            # Edge is where Mask is True but Eroded is False
            edge_mask = mask & (~eroded)
            
            # Dilate the edge slightly for visibility (optional, making it 2px wide)
            # shift edge mask
            p_edge = np.pad(edge_mask, 1, mode='constant', constant_values=False)
            edge_dilated = edge_mask | p_edge[0:-2, 1:-1] | p_edge[2:, 1:-1] | p_edge[1:-1, 0:-2] | p_edge[1:-1, 2:]
            
            # Apply Outline: Darken the edge pixels
            # "Not too dark black line" -> Multiply by 0.3 (70% darker)
            # We apply this to all 3 channels where edge_dilated is True
            # Expand edge mask to (H, W, 3)
            edge_3ch = edge_dilated[:, :, np.newaxis]
            
            # Apply darkening
            img_arr = np.where(edge_3ch, (img_arr * 0.3).astype(np.uint8), img_arr)
            
            return Image.fromarray(img_arr)

        return glitched_image
