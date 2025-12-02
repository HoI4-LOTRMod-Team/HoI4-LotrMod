import cv2
import numpy as np
from scipy.spatial import cKDTree

def relax_layer(image_rgb, mask=None, iterations=15, 
                distortion_scale=25, distortion_magnitude=8):
    
    # Create working copy
    output_rgb = image_rgb.copy()
    h, w = output_rgb.shape[:2]

    # Mask logic
    if mask is None:
        return output_rgb
    
    valid_mask = mask > 0
    y_coords, x_coords = np.where(valid_mask)
    
    if len(y_coords) == 0: return output_rgb

    valid_pixels = np.column_stack((x_coords, y_coords))
    
    # Extract Centroids
    pixel_colors = output_rgb[y_coords, x_coords]
    unique_colors, inverse_indices = np.unique(pixel_colors, axis=0, return_inverse=True)
    num_provinces = len(unique_colors)
    
    if num_provinces < 1: return output_rgb

    centroids = np.zeros((num_provinces, 2))
    for i in range(num_provinces):
        indices = np.where(inverse_indices == i)[0]
        if len(indices) > 0:
            centroids[i] = valid_pixels[indices].mean(axis=0)

    # Relaxation Loop
    for _ in range(iterations):
        tree = cKDTree(centroids)
        _, nearest_indices = tree.query(valid_pixels)
        
        new_centroids = np.zeros_like(centroids)
        counts = np.zeros(num_provinces)
        np.add.at(new_centroids, nearest_indices, valid_pixels)
        np.add.at(counts, nearest_indices, 1)
        
        mask_valid = counts > 0
        centroids[mask_valid] = new_centroids[mask_valid] / counts[mask_valid][:, None]

    # Distortion / Naturalization
    def get_noise(h, w, sc, mag):
        # Create small random grid
        sh, sw = int(h / sc) + 1, int(w / sc) + 1
        small = np.random.uniform(-1, 1, (sh, sw))
        # Upscale
        full = cv2.resize(small, (w, h), interpolation=cv2.INTER_CUBIC)
        return full * mag

    off_x = get_noise(h, w, distortion_scale, distortion_magnitude)
    off_y = get_noise(h, w, distortion_scale, distortion_magnitude)

    grid_y, grid_x = np.mgrid[0:h, 0:w]
    dist_x = grid_x.astype(np.float32) + off_x
    dist_y = grid_y.astype(np.float32) + off_y

    # We want to repaint the entire bounding box area based on the new centroids
    # But strictly speaking, we only want to repaint where the mask WAS 
    # OR where the new shapes extend to.
    # To keep it simple and avoid artifacts: we query the whole ROI grid.
    # Any pixel in the ROI gets assigned to the nearest centroid.
    
    # HOWEVER: This will fill the "White Space" between provinces with color.
    # If you want to preserve the whitespace gaps, we need to limit the query 
    # to pixels that are "close enough" to a centroid, or just query the valid_mask pixels.
    
    # OPTION A: Fill everything in the box (Blocky rectangle result) - Bad.
    # OPTION B: Only move pixels that were already colored (Preserves total area perfectly) - Good.
    
    # Let's do Option B (Warp the originally selected pixels):
    query_points = np.column_stack((
        dist_x[y_coords, x_coords], 
        dist_y[y_coords, x_coords]
    ))
    
    tree = cKDTree(centroids)
    _, final_indices = tree.query(query_points)
    final_colors = unique_colors[final_indices]
    
    output_rgb[y_coords, x_coords] = final_colors
    
    return output_rgb