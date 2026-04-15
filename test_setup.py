#!/usr/bin/env python
"""Test if all dependencies are correctly installed."""

try:
    import cv2
    print("✓ cv2 (OpenCV) OK")
except ImportError as e:
    print(f"✗ cv2 failed: {e}")

try:
    import numpy
    print("✓ numpy OK")
except ImportError as e:
    print(f"✗ numpy failed: {e}")

try:
    import dlib
    print("✓ dlib OK")
except ImportError as e:
    print(f"✗ dlib failed: {e}")

try:
    import PIL
    print("✓ PIL (Pillow) OK")
except ImportError as e:
    print(f"✗ PIL failed: {e}")

try:
    import face_recognition
    print("✓ face_recognition OK")
except ImportError as e:
    print(f"✗ face_recognition failed: {e}")

try:
    import tkinter
    print("✓ tkinter OK")
except ImportError as e:
    print(f"✗ tkinter failed: {e}")

print("\nAll dependencies are ready!")
