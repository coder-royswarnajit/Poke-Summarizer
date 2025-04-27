import numpy as np
from PIL import Image

def get_placeholder_image(width, height, color=(100, 100, 100)):
    """Generate a placeholder image of specified dimensions"""
    # Create a solid color image
    image_array = np.ones((height, width, 3), dtype=np.uint8) * np.array(color, dtype=np.uint8)
    return Image.fromarray(image_array)