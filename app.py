import streamlit as st
import numpy as np
from PIL import Image
from glitch_engine import GlitchEngine
from image_validation import ImageValidator, ImageValidationError
import io
import base64

# Page Config
st.set_page_config(
    page_title="Glitch Art // Memory Corruptor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS FOR URBAN/STREETWEAR AESTHETIC ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Permanent+Marker&display=swap');

    /* Global Reset & Background */
    .stApp {
        background-color: #b0b0b0; /* Darker grey background for the 'desktop' feel */
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Container - The "Card" */
    .main .block-container {
        background-color: #f4f4f4; /* Light grey card background */
        border-radius: 20px;
        padding: 3rem !important;
        max_width: 1400px;
        margin: 2rem auto;
        box-shadow: 0 20px 50px rgba(0,0,0,0.3);
        color: #1a1a1a;
    }

    /* Typography */
    h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 900;
        font-size: 5rem !important;
        letter-spacing: -2px;
        color: #111;
        margin-bottom: 0;
        line-height: 0.9;
    }
    
    .accent-text {
        font-family: 'Permanent Marker', cursive;
        color: #ff3333;
        font-size: 4rem;
        position: relative;
        top: -10px;
        margin-left: 10px;
    }

    h3 {
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.9rem !important;
        color: #666;
        margin-top: 2rem;
        border-bottom: 2px solid #ff3333;
        display: inline-block;
        padding-bottom: 5px;
    }

    p {
        color: #444;
        line-height: 1.6;
        font-size: 0.95rem;
    }

    /* Custom Input Styling */
    .stSelectbox label, .stSlider label, .stCheckbox label {
        color: #111 !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.8rem;
    }
    
    div[data-baseweb="select"] > div {
        background-color: #e0e0e0;
        border: none;
        border-radius: 0;
        color: #111;
    }

    /* Buttons */
    .stButton > button {
        background-color: #111;
        color: #fff;
        border: none;
        border-radius: 0;
        padding: 15px 30px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #ff3333;
        color: #fff;
        transform: translateY(-2px);
        box-shadow: 5px 5px 0px rgba(0,0,0,0.2);
    }

    /* Image Container */
    .img-container {
        position: relative;
        border: 1px solid #ccc;
        padding: 10px;
        background: white;
    }
    
    /* Decorative Elements */
    .deco-line {
        height: 2px;
        background: #ccc;
        width: 50px;
        margin: 20px 0;
    }
    
    .big-number {
        font-size: 6rem;
        font-weight: 900;
        color: #e0e0e0;
        line-height: 1;
        position: absolute;
        bottom: 0;
        right: 0;
        z-index: 0;
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- LAYOUT ---

# Top Nav (Visual Only)
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; border-bottom: 1px solid #ddd; padding-bottom: 20px;">
    <div style="font-weight: 700; font-size: 1.2rem;">GLITCH.CREATOR</div>
    <div style="font-family: monospace; color: #888;">DDCO // SIMULATION // V1.0</div>
    <div style="font-weight: 700;">EN | RUS</div>
</div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1.5], gap="large")

with col_left:
    # Title Section
    st.markdown("""
    <div>
        <h1>GLITCH.<span class="accent-text">ART</span></h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <p style="margin-top: 20px; font-size: 1.1rem;">
    The World's most advanced <b>Hardware Failure Simulator</b>. 
    Bridge the gap between Digital Design and Visual Creativity.
    Corrupt RAM. Destroy Data. Create Art.
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="deco-line"></div>', unsafe_allow_html=True)

    # Controls Section (Styled as "Project Specs")
    st.markdown("### // SYSTEM PARAMETERS")
    
    # Input Source: Static Image Files ONLY (No Live Camera Feed)
    uploaded_file = st.file_uploader("LOAD SOURCE DATA", type=['jpg', 'jpeg', 'png'])
    
    # Initialize session state for the engine to avoid reloading
    if 'engine' not in st.session_state:
        st.session_state.engine = None
    
    if uploaded_file:
        # Reset file pointer to be safe
        uploaded_file.seek(0)
        
        # Validate uploaded image for security
        try:
            validated_image = ImageValidator.validate(uploaded_file, filename=uploaded_file.name)
            # Reset file pointer after validation
            uploaded_file.seek(0)
            st.session_state.engine = GlitchEngine(uploaded_file)
        except ImageValidationError as e:
            st.error(f"⚠️ SECURITY VALIDATION FAILED: {str(e)}")
            st.info("Please upload a valid JPEG or PNG image file.")
            st.session_state.engine = None
            uploaded_file = None
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            # Default to index 1 (stuck_at_0)
            fault_type = st.selectbox(
                "FAULT TYPE",
                ('none', 'stuck_at_0', 'stuck_at_1', 'bit_flip', 'burst_error', 'color_drift'),
                index=1, 
                format_func=lambda x: x.upper()
            )
            
            # Dynamic Description based on selection
            descriptions = {
                'none': "System Integrity Normal.",
                'stuck_at_0': "HARDWARE FAILURE: A memory bit is physically broken and locked to 0. Causes vertical banding and dark artifacts.",
                'stuck_at_1': "HARDWARE FAILURE: A memory bit is physically broken and locked to 1. Causes vertical banding and bright artifacts.",
                'bit_flip': "COSMIC RAY INTERFERENCE: High-energy particles invert random bits. Creates 'salt and pepper' noise.",
                'burst_error': "DEAD SECTOR: Physical damage to the storage medium. Destroys contiguous blocks of data.",
                'color_drift': "INTEGER OVERFLOW: Processor math error causing color values to wrap around. Psychedelic shifts."
            }
            
            # Styled Info Box
            st.markdown(f"""
            <div style="background-color: #e0e0e0; padding: 10px; border-left: 3px solid #ff3333; font-size: 0.8rem; margin-bottom: 10px; color: #333;">
                <b>// DIAGNOSTIC:</b> {descriptions.get(fault_type, "")}
            </div>
            """, unsafe_allow_html=True)
            
            # Default to 7 (MSB) for maximum destruction
            target_bit = st.slider(
                "TARGET BIT (MSB-LSB)",
                0, 7, 7,
                help="Bit 7 (MSB) controls 50% of the color intensity. Bit 0 (LSB) controls <1%. Flipping MSB causes massive damage."
            )
            
        with col_c2:
            # Default to 0.5 (50%) for obvious effect
            probability = st.slider(
                "CHAOS LEVEL",
                0.0, 1.0, 0.5,
                help="Probability of a fault occurring. 0.5 means 50% of memory is corrupted."
            )
            
            endian_swap = st.checkbox("SWAP ENDIANNESS", help="Simulates reading data with the wrong byte order (Little vs Big Endian). Scrambles RGB channels.")

        st.markdown("### // MEMORY MAPPING")
        c1, c2, c3 = st.columns(3)
        r_active = c1.checkbox("RED CH", True)
        g_active = c2.checkbox("GRN CH", True)
        b_active = c3.checkbox("BLU CH", True)
        
        st.markdown("### // AI TARGETING")
        
        # Check for AI dependencies
        ai_available = False
        try:
            import torch
            import transformers
            ai_available = True
        except ImportError:
            ai_available = False
            
        if ai_available:
            use_mask = st.checkbox("TARGET T-SHIRT ONLY (AI)", help="Uses SegFormer to detect upper clothes.")
        else:
            st.warning("AI features unavailable. Please check console.")
            use_mask = False
        
        # Run Button
        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            run_glitch = st.button("EXECUTE SINGLE")
        with col_btn2:
            run_variations = st.button("GENERATE 4 VARIATIONS")
            
        # Interactive Guide (Collapsed to keep it simple)
        with st.expander("📚 HOW IT WORKS (DDCO CONCEPTS)"):
            st.markdown("""
            **1. The Byte Array (RAM)**
            Images are just numbers in RAM. We load the image as a flat array of bytes (0-255).
            
            **2. Bitwise Operations**
            We don't use Photoshop filters. We use raw logic gates:
            *   **AND (`&`)**: Used for `stuck_at_0`. Forces bits off.
            *   **OR (`|`)**: Used for `stuck_at_1`. Forces bits on.
            *   **XOR (`^`)**: Used for `bit_flip`. Inverts bits.
            
            **3. Significance**
            Try moving the **Target Bit** slider.
            *   **Bit 7 (128)**: The "Most Significant Bit". Changing this changes the color value by 128. Huge visual impact.
            *   **Bit 0 (1)**: The "Least Significant Bit". Changing this changes the color by 1. Invisible to the eye.
            """)

with col_right:
    # Image Display Area
    if uploaded_file and st.session_state.engine:
        engine = st.session_state.engine
        
        # Initialize Segmenter if needed
        mask = None
        if use_mask and ai_available:
            with st.spinner("🧠 AI Analyzing Image..."):
                try:
                    from segmentation import ClothingSegmenter
                    if 'segmenter' not in st.session_state:
                        st.session_state.segmenter = ClothingSegmenter()
                    
                    mask = st.session_state.segmenter.get_tshirt_mask(engine.original_image)
                    
                    # Check if mask is empty (no t-shirt found)
                    if not np.any(mask):
                        st.warning("⚠️ AI detected no T-Shirt/Upper-Clothes. The glitch effect will not be visible. Uncheck 'AI TARGETING' or try a different image.")
                        mask = None # Fallback to None? No, user asked for targeting. If None, it glitches everything. 
                        # If we leave it as all-False mask, it glitches nothing (which is what happens now).
                        # The warning explains it.
                        
                except Exception as e:
                    st.error(f"AI Model Error: {e}")
        
        if run_variations:
            st.markdown("### // RANDOMIZED CHAOS GENERATOR")
            v_col1, v_col2 = st.columns(2)
            
            # Available modes (Removed 'sync_loss' as requested/interpreted)
            # We focus on the ones that produce "Crazy" results
            modes = ['stuck_at_0', 'stuck_at_1', 'bit_flip', 'color_drift', 'burst_error']
            
            import random
            
            for i in range(4):
                # Randomize Parameters
                mode = random.choice(modes)
                
                # Force higher bits for visibility (3-7)
                t_bit = random.randint(3, 7)
                
                # Random probability (skewed towards chaos)
                prob = random.uniform(0.05, 0.4)
                if mode == 'burst_error': prob = random.uniform(0.01, 0.1) # Lower for burst
                
                # Random Endianness
                swap = random.choice([True, False])
                
                # Random Channels
                ch = {
                    'R': random.choice([True, False]), 
                    'G': random.choice([True, False]), 
                    'B': random.choice([True, False])
                }
                # Ensure at least one channel is active
                if not any(ch.values()): ch['G'] = True
                
                # Generate
                img = engine.corrupt(
                    fault_type=mode, 
                    target_bit=t_bit, 
                    probability=prob, 
                    channels=ch, 
                    endian_swap=swap,
                    mask=mask
                )
                
                caption = f"#{i+1} // {mode.upper()} // BIT {t_bit}"
                
                # Display in grid
                if i % 2 == 0:
                    with v_col1:
                        st.image(img, caption=caption, use_column_width=True)
                else:
                    with v_col2:
                        st.image(img, caption=caption, use_column_width=True)
                
        else:
            # Default Single Execution
            # Logic
            # We run this every time the script reruns (reactive)
            try:
                glitched_image = engine.corrupt(
                    fault_type=fault_type,
                    target_bit=target_bit,
                    probability=probability,
                    channels={'R': r_active, 'G': g_active, 'B': b_active},
                    endian_swap=endian_swap,
                    mask=mask
                )
                
                # Display
                st.image(glitched_image, use_column_width=True)
                
                # Metadata / Download
                st.markdown("""
                <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-top: 20px;">
                    <div style="font-family: monospace; color: #666; font-size: 0.8rem;">
                        D:\\MEMORY_DUMP\\OUTPUT.PNG<br>
                        SIZE: {}x{}<br>
                        STATUS: <span style="color: #ff3333;">CORRUPTED</span>
                    </div>
                    <div style="font-size: 4rem; font-weight: 900; color: #ddd; line-height: 1;">01</div>
                </div>
                """.format(glitched_image.width, glitched_image.height), unsafe_allow_html=True)
                
                # Download Button
                buf = io.BytesIO()
                glitched_image.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.download_button(
                    label="DOWNLOAD ARTIFACT",
                    data=byte_im,
                    file_name="glitch_art_urban.png",
                    mime="image/png"
                )
            except Exception as e:
                st.error(f"SYSTEM FAILURE: {e}")
        
    else:
        # Placeholder State
        st.markdown("""
        <div style="background: #e0e0e0; height: 500px; display: flex; align-items: center; justify-content: center; border-radius: 5px;">
            <div style="text-align: center; color: #999;">
                <div style="font-size: 3rem;">⊕</div>
                <p>WAITING FOR INPUT STREAM...</p>
            </div>
        </div>
        """, unsafe_allow_html=True)


# Footer / Technical Details
st.markdown("---")
st.markdown("""
<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; font-size: 0.8rem; color: #666;">
    <div>
        <b>BITWISE LOGIC</b><br>
        Using AND, OR, XOR to manipulate raw byte arrays directly in RAM.
    </div>
    <div>
        <b>STUCK-AT FAULTS</b><br>
        Simulating permanent hardware failures in memory cells.
    </div>
    <div>
        <b>ENDIANNESS</b><br>
        Demonstrating byte-order interpretation differences.
    </div>
</div>
""", unsafe_allow_html=True)
