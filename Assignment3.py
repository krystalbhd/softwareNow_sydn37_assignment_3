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

    
# GAME STATE CLASS - Tracks the player's score, mistakes, and round progress

class GameState:
    def __init__(self):
        # Cumulative score across all rounds
        self.total_found = 0
        self.reset_round()

    # Resets only the current round's stats (not total score)
    def reset_round(self):
        self.found_count = 0
        self.mistakes = 0
        self.game_over = False

    # Returns how many differences are still unfound
    def remaining(self):
        return 5 - self.found_count

    # Returns True if all 5 differences have been found
    def win(self):
        return self.found_count == 5

    # Returns True if the player has exceeded mistake limit
    def lose(self):
        return self.game_over
    
# =========================================================
# MAIN APPLICATION — GUI SETUP
# Builds the GUI and connects all components together
# =========================================================
class SpotTheDifferenceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spot the Difference")
        self.root.configure(bg="#eef4f7")
        # Handles image loading and effect generation
        self.processor = ImageProcessor()
        # Tracks game progress and player stats
        self.state = GameState()
        # Scale factors to map canvas clicks to image coordinates
        self.scale_x = 1
        self.scale_y = 1

        # Title label at the top of the window
        tk.Label(
            root,
            text="Spot the Difference",
            bg="#eef4f7",
            fg="black",
            font=("Comic Sans MS", 22, "bold")
        ).pack(pady=12)

        # Frame containing the Load and Reveal buttons
        button_frame = tk.Frame(root, bg="#eef4f7")
        button_frame.pack(pady=5)

        # Button to load a new image from file
        tk.Button(
            button_frame,
            text="Load Image",
            command=self.load_image,
            bg="white",
            fg="black",
            font=("Arial", 11, "bold"),
            width=14
        ).pack(side=tk.LEFT, padx=10)

        # Button to reveal all differences
        tk.Button(
            button_frame,
            text="Reveal",
            command=self.reveal_differences,
            bg="white",
            fg="black",
            font=("Arial", 11, "bold"),
            width=14
        ).pack(side=tk.LEFT, padx=10)

        # Label showing how many differences are remaining
        self.remaining_label = tk.Label(
            root,
            text="Remaining: 0",
            bg="#eef4f7",
            fg="green",
            font=("Arial", 12, "bold")
        )
        self.remaining_label.pack(pady=2)

        # Label showing how many mistakes the player has made
        self.mistake_label = tk.Label(
            root,
            text="Mistakes: 0/3",
            bg="#eef4f7",
            fg="red",
            font=("Arial", 12, "bold")
        )
        self.mistake_label.pack(pady=2)

        # Label showing the total score across all rounds
        self.total_score_label = tk.Label(
            root,
            text="Total Score: 0",
            bg="#eef4f7",
            fg="blue",
            font=("Arial", 12, "bold")
        )
        self.total_score_label.pack(pady=2)

        # Frame for the Original / Modified image labels
        label_frame = tk.Frame(root, bg="#eef4f7")
        label_frame.pack(fill="x", pady=(5, 0))
        label_frame.columnconfigure(0, weight=1)
        label_frame.columnconfigure(1, weight=1)

        # Label above the original image canvas
        self.ori_label = tk.Label(
            label_frame,
            text="Original Image",
            bg="#eef4f7",
            fg="black",
            font=("Arial", 12, "bold"),
            width=30
        )
        self.ori_label.grid(row=0, column=0)

        # Label above the modified image canvas
        self.mod_label = tk.Label(
            label_frame,
            text="Modified Image",
            bg="#eef4f7",
            fg="black",
            font=("Arial", 12, "bold"),
            width=30
        )
        self.mod_label.grid(row=0, column=1)

        # Frame that holds both image canvases side by side
        image_frame = tk.Frame(root, bg="#eef4f7")
        image_frame.pack(pady=10)

        # Left canvas displays the original image (not clickable)
        self.left_canvas = tk.Canvas(
            image_frame,
            width=450,
            height=450,
            bg="white",
            highlightthickness=2,
            highlightbackground="#cccccc"
        )
        self.left_canvas.grid(row=0, column=0, padx=12)

        # Right canvas displays the modified image (clickable)
        self.right_canvas = tk.Canvas(
            image_frame,
            width=450,
            height=450,
            bg="white",
            highlightthickness=2,
            highlightbackground="#cccccc"
        )
        self.right_canvas.grid(row=0, column=1, padx=12)

        # Only the right (modified) image responds to player clicks
        self.right_canvas.bind("<Button-1>", self.check_click)

    

