import os
import requests

def load_api_key():
    """
    Locates and reads the API key from REMBG_KEY.txt in the current
    or parent directory.
    """
    paths_to_check = [
        "REMBG_KEY.txt",            # Current working directory
        "../REMBG_KEY.txt",         # One directory up
    ]
    
    for path in paths_to_check:
        if os.path.exists(path):
            with open(path, "r") as f:
                # .strip() removes any accidental spaces or newlines
                return f.read().strip()
    
    raise FileNotFoundError("REMBG_KEY.txt not found in current or parent directory.")

def process_image(image_bytes: bytes, use_preview: bool = True) -> bytes:
    """
    Sends raw image bytes to Remove.bg and returns the raw PNG bytes 
    of the background-removed image.

    Args:
        image_bytes (bytes): The raw binary data of the input image (JPG/PNG).
        use_preview (bool): If True, requests the 'preview' size (approx 0.25MP)
                            to cost only 0.25 credits. If False, requests 'auto'
                            (full resolution) for 1 credit.

    Returns:
        bytes: Raw PNG data of the processed image.
    """
    api_key = load_api_key()
    url = "https://api.remove.bg/v1.0/removebg"
    
    # 'preview' costs 0.25 credits. 'auto' costs 1 credit (for high res).
    size_param = "preview" if use_preview else "auto"
    
    payload = {
        'size': size_param,
    }
    
    # We send the raw bytes directly as a file named 'image.png' (the API handles handling types)
    files = {
        'image_file': ('image.png', image_bytes)
    }
    
    headers = {
        'X-Api-Key': api_key
    }

    response = requests.post(url, files=files, data=payload, headers=headers)

    if response.status_code == 200:
        return response.content
    else:
        # Raise an informative error if the API call fails
        raise RuntimeError(f"Remove.bg API Error {response.status_code}: {response.text}")