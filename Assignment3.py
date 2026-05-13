import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import random
# =========================================================
# BASE EFFECT CLASS (POLYMORPHISM)
# Each effect class inherits from this and overrides apply()
# =========================================================
class ImageEffect:
    def apply(self, image, x, y, w, h):
        # To be implemented by each child effect class
        raise NotImplementedError

# =========================================================
# EFFECT 0 - Tint Effect
# Adds a blue tint to the selected region of the image
# =========================================================
class TintEffect(ImageEffect):
    def apply(self, image, x, y, w, h):
        # Extract the region of interest from the image
        region = image[y:y + h, x:x + w]
        # Increase the blue channel value by 60 (clipped to max 255)
        region[:, :, 0] = np.clip(region[:, :, 0] + 60, 0, 255)
        # Write the modified region back to the image
        image[y:y + h, x:x + w] = region

# =========================================================
# EFFECT 1 - COLOUR SHIFT
# Adds a subtle green tint to the selected region
# =========================================================
class ColorShiftEffect(ImageEffect):
    def apply(self, image, x, y, w, h):
        # Extract the region of interest from the image
        region = image[y:y + h, x:x + w]
        # Increase the green channel value by 50 (clipped to max 255)
        region[:, :, 1] = np.clip(region[:, :, 1] + 50, 0, 255)
        # Write the modified region back to the image
        image[y:y + h, x:x + w] = region

# =========================================================
# EFFECT 2 - BLUR
# Applies Gaussian blur to the selected region
# =========================================================
class BlurEffect(ImageEffect):
    def apply(self, image, x, y, w, h):
        # Extract the region of interest from the image
        region = image[y:y + h, x:x + w]
        # Apply Gaussian blur with a 9x9 kernel
        blurred = cv2.GaussianBlur(region, (9, 9), 0)
        # Write the blurred region back to the image
        image[y:y + h, x:x + w] = blurred

# =========================================================
# EFFECT 3- INVERT Effect
# Inverts all pixel colours in the selected region
# =========================================================
class InvertEffect(ImageEffect):
    def apply(self, image, x, y, w, h):
        # Extract the region of interest from the image
        region = image[y:y + h, x:x + w]
        # Invert colours by subtracting each pixel value from 255
        region = 255 - region
        # Write the inverted region back to the image
        image[y:y + h, x:x + w] = region


# =========================================================
# DIFFERENCE CLASS (ENCAPSULATION)
# Represents a single difference region on the image
# Stores position, size, effect, and whether it was found
# =========================================================
class Difference:
    def __init__(self, x, y, w, h, effect):
        # Position and size of the difference region
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        # The effect applied to this difference region
        self._effect = effect
        # Whether the player has found this difference
        self._found = False

    # Returns the position and size as a tuple
    def rect(self):
        return self._x, self._y, self._w, self._h

    # Returns True if the player has already found this difference
    def found(self):
        return self._found

    # Marks this difference as found by the player
    def mark_found(self):
        self._found = True

    # Checks if a player's click falls within this difference region
    # Uses a tolerance to make clicking easier
    def contains(self, click_x, click_y, tolerance=20):
        x, y, w, h = self.rect()
        return (
            x - tolerance <= click_x <= x + w + tolerance
            and
            y - tolerance <= click_y <= y + h + tolerance
        )