import base64
from PIL import Image

def load_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def load_pil_image(path):
    return Image.open(path)