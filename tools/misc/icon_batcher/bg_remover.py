import os
from pathlib import Path
from rembg import remove, new_session

# --- CONFIGURATION ---
INPUT_FOLDER = r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\retrievals\2026-01-19_10-38-33'
OUTPUT_FOLDER = r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\retrievals\2026-01-19_10-38-33_no_bg'

# 1. CHOOSE A MODEL
# Options: 'u2net' (default), 'u2netp' (fast/light), 'u2net_human_seg' (people), 
# 'isnet-general-use' (very accurate), 'bria-rmbg' (good for products)
MODEL_NAME = 'isnet-general-use' 

def remove_backgrounds_gpu():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # --- GPU SETTINGS ---
    # We define the execution providers. CUDA is for NVIDIA GPUs.
    # The order matters: it will try CUDA first, then CPU as a fallback.
    providers = [
        'CUDAExecutionProvider', 
        'CPUExecutionProvider'
    ]

    try:
        session = new_session(MODEL_NAME, providers=providers)
        print(f"Session started with model: {MODEL_NAME}")
        # Check if it actually picked up the GPU
        print(f"Active providers: {session.inner_session.get_providers()}")
    except Exception as e:
        print(f"Could not initialize GPU session: {e}")
        return

    for file_path in Path(INPUT_FOLDER).iterdir():
        if file_path.suffix.lower() in ('.jpg', '.jpeg', '.png'):
            print(f"Processing (GPU): {file_path.name}")
            output_path = Path(OUTPUT_FOLDER) / (file_path.stem + ".png")
            
            with open(file_path, 'rb') as i:
                input_data = i.read()
                output_data = remove(
                    input_data, 
                    session=session,
                    alpha_matting=True # Keeping high quality enabled
                )
                
                with open(output_path, 'wb') as o:
                    o.write(output_data)

if __name__ == "__main__":
    remove_backgrounds_gpu()