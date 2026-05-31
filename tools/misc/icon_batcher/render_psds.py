from pathlib import Path
from psd_tools import PSDImage

# --- SETUP ---
# Replace this string with the actual path to your folder.
# The 'r' before the string handles Windows backslashes automatically.
DIRECTORY_PATH = r"E:\PROJECTS\HOI4_LOTR\out_batch 1\out_batch" 

def batch_convert_psds(folder_path):
    target_dir = Path(folder_path)
    
    # Check if the folder actually exists
    if not target_dir.is_dir():
        print(f"Error: The directory '{folder_path}' cannot be found.")
        return

    # Find all files ending in .psd (case-insensitive search)
    # Note: .rglob() searches subfolders too. Use .glob() to only search the top folder.
    psd_files = list(target_dir.glob("*.[pP][sS][dD]"))
    
    if not psd_files:
        print(f"No PSD files found in {target_dir}.")
        return

    print(f"Found {len(psd_files)} PSD file(s). Starting conversion...\n")
    print("-" * 40)

    for psd_path in psd_files:
        print(f"Opening: {psd_path.name}...")
        
        try:
            # Load the PSD
            psd = PSDImage.open(psd_path)
            
            # Check for the perfect embedded render
            if psd.has_preview():
                image = psd.topil()
                method_used = "Extracted embedded preview"
            else:
                # Fallback to psd-tools rendering if no preview is baked in
                image = psd.composite()
                method_used = "Rendered via psd-tools (Fallback)"
            
            # Create the new filename by replacing .psd with .png
            png_path = psd_path.with_suffix('.png')
            
            # Save the file
            image.save(png_path)
            print(f"  -> Saved: {png_path.name} [{method_used}]")
            
        except Exception as e:
            print(f"  -> Error processing {psd_path.name}: {e}")

    print("-" * 40)
    print("Batch conversion complete!")

# Run the script
if __name__ == "__main__":
    batch_convert_psds(DIRECTORY_PATH)