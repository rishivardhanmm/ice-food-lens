"""Image preprocessing for the internal model pipeline.

Placeholder implementation: resizes/normalizes images so later stages
(detection, classification, portion estimation) have a consistent input.
Not yet wired to a trained model.
"""
from PIL import Image as PILImage

TARGET_SIZE = (224, 224)


def load_image(filepath: str) -> PILImage.Image:
    return PILImage.open(filepath).convert("RGB")


def preprocess(filepath: str) -> PILImage.Image:
    img = load_image(filepath)
    img = img.resize(TARGET_SIZE)
    return img
