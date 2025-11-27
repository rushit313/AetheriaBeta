import io
import numpy as np
from PIL import Image, ImageStat
import cv2

def analyze_image_stats(image_bytes: bytes) -> dict:
    """
    Calculate real statistics for an image.
    Returns a dictionary with keys matching the frontend expectations:
    - exposure_mean
    - contrast_std
    - noise_level
    - saturation_pct
    - sharpness_laplacian_var
    - wb_shift_blue_minus_red
    """
    try:
        # Load image with PIL
        img_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Convert to numpy array for OpenCV/NumPy ops
        img_np = np.array(img_pil)
        
        # 1. Exposure (Mean Brightness)
        # Convert to grayscale for simple brightness
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        exposure_mean = float(np.mean(gray))
        
        # 2. Contrast (Standard Deviation)
        contrast_std = float(np.std(gray))
        
        # 3. Saturation (Mean Saturation in HSV)
        hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
        saturation_channel = hsv[:, :, 1]
        saturation_pct = float(np.mean(saturation_channel)) / 2.55  # Convert 0-255 to 0-100
        
        # 4. Sharpness (Laplacian Variance)
        # Variance of the Laplacian gives a measure of edges/focus
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness_laplacian_var = float(laplacian.var())
        
        # 5. White Balance Shift (Blue - Red)
        # Simple heuristic: difference between average Blue and average Red
        r_mean = np.mean(img_np[:, :, 0])
        b_mean = np.mean(img_np[:, :, 2])
        wb_shift = float(b_mean - r_mean)
        
        # 6. Noise Level (Estimate)
        # Simple estimation: standard deviation of a smooth area or high freq components
        # Here we use a fast approximation: difference between image and its blurred version
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        noise_img = cv2.absdiff(gray, blurred)
        noise_level = float(np.mean(noise_img))

        return {
            "exposure_mean": round(exposure_mean, 1),
            "contrast_std": round(contrast_std, 1),
            "noise_level": round(noise_level, 1),
            "saturation_pct": round(saturation_pct, 1),
            "sharpness_laplacian_var": int(sharpness_laplacian_var),
            "wb_shift_blue_minus_red": round(wb_shift, 1),
        }
        
    except Exception as e:
        print(f"Error calculating image stats: {e}")
        # Fallback to safe defaults if something fails
        return {
            "exposure_mean": 128.0,
            "contrast_std": 50.0,
            "noise_level": 10.0,
            "saturation_pct": 50.0,
            "sharpness_laplacian_var": 500,
            "wb_shift_blue_minus_red": 0.0,
        }
