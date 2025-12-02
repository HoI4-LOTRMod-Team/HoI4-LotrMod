import cv2
import numpy as np
from scipy.spatial import cKDTree

def relax_layer(image_rgb, mask=None, iterations=15, 
                distortion_scale=40, distortion_magnitude=6,
                smoothness=3): # <--- New Parameter
    
    output_rgb = image_rgb.copy()
    h, w = output_rgb.shape[:2]

    # --- 1. Mask Logic ---
    if mask is None:
        # If no mask, assume whole image
        valid_mask = np.ones((h, w), dtype=bool)
    else:
        valid_mask = mask > 0
        
    y_coords, x_coords = np.where(valid_mask)
    if len(y_coords) == 0: return output_rgb

    valid_pixels = np.column_stack((x_coords, y_coords))
    
    # --- 2. Extract Centroids ---
    pixel_colors = output_rgb[y_coords, x_coords]
    
    # We need to map colors to unique IDs to filter them later
    unique_colors, inverse_indices = np.unique(pixel_colors, axis=0, return_inverse=True)
    num_provinces = len(unique_colors)
    
    if num_provinces < 1: return output_rgb

    centroids = np.zeros((num_provinces, 2))
    for i in range(num_provinces):
        indices = np.where(inverse_indices == i)[0]
        if len(indices) > 0:
            centroids[i] = valid_pixels[indices].mean(axis=0)

    # --- 3. Relaxation Loop ---
    for _ in range(iterations):
        tree = cKDTree(centroids)
        _, nearest_indices = tree.query(valid_pixels)
        
        new_centroids = np.zeros_like(centroids)
        counts = np.zeros(num_provinces)
        np.add.at(new_centroids, nearest_indices, valid_pixels)
        np.add.at(counts, nearest_indices, 1)
        
        mask_valid = counts > 0
        centroids[mask_valid] = new_centroids[mask_valid] / counts[mask_valid][:, None]

    # --- 4. Fractal Distortion ---
    def get_fractal_noise(h, w, base_scale, magnitude, octaves=3):
        noise = np.zeros((h, w), dtype=np.float32)
        current_scale = base_scale
        current_mag = magnitude
        for _ in range(octaves):
            if current_scale < 2: current_scale = 2
            sh, sw = int(h / current_scale) + 1, int(w / current_scale) + 1
            small = np.random.uniform(-1, 1, (sh, sw))
            layer = cv2.resize(small, (w, h), interpolation=cv2.INTER_CUBIC)
            noise += layer * current_mag
            current_scale /= 2.0
            current_mag /= 2.0
        return noise

    off_x = get_fractal_noise(h, w, distortion_scale, distortion_magnitude)
    off_y = get_fractal_noise(h, w, distortion_scale, distortion_magnitude)

    grid_y, grid_x = np.mgrid[0:h, 0:w]
    dist_x = grid_x.astype(np.float32) + off_x
    dist_y = grid_y.astype(np.float32) + off_y

    # --- 5. Reconstruction ---
    # Get the raw province indices for every pixel in the mask
    query_points = np.column_stack((
        dist_x[y_coords, x_coords], 
        dist_y[y_coords, x_coords]
    ))
    
    tree = cKDTree(centroids)
    _, raw_indices = tree.query(query_points)

    # --- 6. Coherence / Denoising Pass (New Step) ---
    if smoothness > 0:
        # We must reconstruct the full 2D map of IDs to check neighbors
        # Use -1 for "out of bounds/mask"
        id_map = np.full((h, w), -1, dtype=np.float32)
        
        # Place our calculated province IDs onto the map
        id_map[y_coords, x_coords] = raw_indices.astype(np.float32)
        
        # Apply Median Blur to IDs
        # The median of integers is always an integer from the set.
        # It removes outliers (stray pixels) effectively.
        # Kernel size must be odd (3, 5, 7...)
        ksize = smoothness if smoothness % 2 == 1 else smoothness + 1
        cleaned_map = cv2.medianBlur(id_map, ksize)
        
        # Read the cleaned IDs back out
        final_indices = cleaned_map[y_coords, x_coords].astype(int)
        
        # Edge case: If the blur pulled in a -1 (background), revert to raw
        # This prevents black artifacts at the very edge of the mask
        mask_errors = final_indices == -1
        final_indices[mask_errors] = raw_indices[mask_errors]
    else:
        final_indices = raw_indices

    # Map indices back to RGB colors
    final_colors = unique_colors[final_indices]
    output_rgb[y_coords, x_coords] = final_colors
    
    return output_rgb