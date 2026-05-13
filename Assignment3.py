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

# ||IMAGE PROCESSOR||

class ImageProcessor:
    def __init__(self):
        # Stores the original unmodified image
        self.original_image = None
        # Stores the image with effects applied
        self.modified_image = None
        # List of Difference objects placed on the image
        self.differences = []
        # Available effects to randomly assign to differences
        self.effects = [
            ColorShiftEffect(),
            BlurEffect(),
            InvertEffect()
        ]

    # To load an image from the given file path
    def load_image(self, path):
        image = cv2.imread(path)
        if image is None:
            return
        # Keep the original image unchanged
        self.original_image = image.copy()
        # Modified image will receive the applied effects
        self.modified_image = image.copy()
        # Clear any previous differences
        self.differences = []

    # To randomly generate 5 non-overlapping difference regions
    def generate_differences(self):
        height, width = self.original_image.shape[:2]
        while len(self.differences) < 5:
            # Random size between 40 and 80 pixels
            size = random.randint(40, 80)
            # Random position within image bounds
            x = random.randint(0, width - size)
            y = random.randint(0, height - size)
            # Randomly select an effect to apply
            effect = random.choice(self.effects)
            difference = Difference(x, y, size, size, effect)
            # Skip this region if it overlaps with an existing one
            if self.overlaps(difference):
                continue
            self.differences.append(difference)
            # Apply the effect only to the modified image
            effect.apply(self.modified_image, x, y, size, size)

    # To check if a new difference overlaps with any existing ones
    def overlaps(self, new_difference):
        nx, ny, nw, nh = new_difference.rect()
        for difference in self.differences:
            x, y, w, h = difference.rect()
            overlap = not (
                nx + nw < x or
                nx > x + w or
                ny + nh < y or
                ny > y + h
            )
            if overlap:
                return True
        return False
    

