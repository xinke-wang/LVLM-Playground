import base64
import random
from io import BytesIO

import numpy as np
import torch
from PIL import Image


def set_random_seed():
    """Set the random seed for reproducibility."""
    seed = random.randint(0, 2**32 - 1)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.random.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    return seed


def encode_image(image_path, size=None):
    """Encode an image to a base64 string. Optionally resize the image before
    encoding.
    """
    with open(image_path, 'rb') as image_file:
        image = Image.open(image_file)

        if size:
            image = image.resize(size, Image.Resampling.LANCZOS)

        buffered = BytesIO()
        image.save(buffered, format='PNG')
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
