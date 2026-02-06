import cv2
import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import distance_transform_edt

def relax_layer(image_rgb, mask=None, iterations=15, 
                distortion_scale=40, distortion_magnitude=6,
                smoothness=3):
    
    output_rgb = image_rgb.copy()
    h, w = output_rgb.shape[:2]

    # --- 1. Mask Logic ---
    if mask is None:
        valid_mask = np.ones((h, w), dtype=bool)
    else:
        valid_mask = mask > 0
        
    y_coords, x_coords = np.where(valid_mask)
    if len(y_coords) == 0: return output_rgb

    valid_pixels = np.column_stack((x_coords, y_coords))
    
    # --- 2. Extract Centroids ---
    pixel_colors = output_rgb[y_coords, x_coords]
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
    query_points = np.column_stack((
        dist_x[y_coords, x_coords], 
        dist_y[y_coords, x_coords]
    ))
    
    tree = cKDTree(centroids)
    _, raw_indices = tree.query(query_points)

    # --- 6a. Smoothing Pass ---
    # We construct the map to apply median blur
    id_map = np.full((h, w), -1, dtype=np.int32)
    id_map[y_coords, x_coords] = raw_indices.astype(np.int32)
    
    if smoothness > 0:
        ksize = smoothness if smoothness % 2 == 1 else smoothness + 1
        # Convert to float32 for medianBlur (or cast back and forth with uint8/int16 if needed)
        # OpenCV medianBlur works on uint8, float32, or int16. 
        # Using float32 to stay safe with negative IDs (-1)
        cleaned_map = cv2.medianBlur(id_map.astype(np.float32), ksize).astype(np.int32)
        
        # Restore boundary errors caused by blur
        mask_errors = cleaned_map == -1
        # Only fix errors where we actually have a valid mask
        valid_mask_flat = np.zeros_like(cleaned_map, dtype=bool)
        valid_mask_flat[y_coords, x_coords] = True
        
        to_fix = mask_errors & valid_mask_flat
        cleaned_map[to_fix] = id_map[to_fix]
        final_indices_map = cleaned_map
    else:
        final_indices_map = id_map

    # --- 6b. Enforce Connectivity (The Fix) ---
    # We create a map of "Pruned" IDs, where islands are removed (set to -1)
    pruned_map = np.full((h, w), -1, dtype=np.int32)
    
    # We process each province to find its "Main Body"
    # (Iterating 50-100 provinces is very fast. 
    # If you have 5000+, this might take a second)
    for i in range(num_provinces):
        # Create binary mask for this province
        # Using uint8 for connectedComponents
        p_mask = (final_indices_map == i).astype(np.uint8)
        
        # Fast check: skip if province empty
        if not np.any(p_mask): continue

        # Find all blobs of this province
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(p_mask, connectivity=8)
        
        if num_labels <= 2: 
            # 1 background + 1 component = Perfect. Keep as is.
            pruned_map[p_mask == 1] = i
        else:
            # Multiple blobs found. We need to keep the "correct" one.
            # Strategy: Keep the component closest to the province's centroid.
            cx, cy = centroids[i]
            cx, cy = int(cx), int(cy)
            
            # Clamp coordinates to image bounds just in case
            cx = np.clip(cx, 0, w - 1)
            cy = np.clip(cy, 0, h - 1)
            
            # Check which label is at the centroid
            target_label = labels[cy, cx]
            
            # If centroid landed on background (0) or another province (due to distortion),
            # fall back to the largest component by area.
            if target_label == 0:
                # stats shape: [label, x, y, w, h, area]
                # stats[1:, 4] extracts areas of all foreground components
                # +1 because argmax gives index relative to the slice, and we skipped bg (0)
                target_label = np.argmax(stats[1:, 4]) + 1
            
            # Write only the chosen component to the pruned map
            pruned_map[labels == target_label] = i

    # Now 'pruned_map' has -1 holes where the stray islands used to be.
    # We fill these holes using nearest-neighbor based on Euclidean distance.
    
    # invalid_mask is True where we need to fill holes (inside the valid area)
    # We must ensure we only fill holes that are inside our original Valid Mask
    global_valid_mask = np.zeros((h, w), dtype=bool)
    global_valid_mask[y_coords, x_coords] = True
    
    holes_mask = (pruned_map == -1) & global_valid_mask
    
    if np.any(holes_mask):
        # distance_transform_edt computes distance to the nearest ZERO pixel.
        # So we invert: 0 = Valid Province, 1 = Hole.
        # return_indices=True gives us the index of the nearest Valid Province pixel.
        _, indices = distance_transform_edt(holes_mask, return_distances=True, return_indices=True)
        
        # 'indices' is a tuple of arrays (y_indices, x_indices) pointing to nearest valid pixel
        # We use these to sample from pruned_map
        fill_values = pruned_map[tuple(indices)]
        
        # Apply the fill
        pruned_map[holes_mask] = fill_values[holes_mask]

    # --- 7. Final Assignment ---
    # Extract the final IDs only for the valid pixels
    final_indices = pruned_map[y_coords, x_coords]
    
    # Map back to colors
    final_colors = unique_colors[final_indices]
    output_rgb[y_coords, x_coords] = final_colors
    
    return output_rgb