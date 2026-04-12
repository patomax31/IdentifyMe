import os
import cv2

from src.core.config import get_camera_settings


def open_camera():
    """OpenCV camera bootstrap with dual profile support (Windows / Raspberry Pi)."""
    settings = get_camera_settings()
    profile = settings.profile
    if profile == "AUTO":
        profile = "WINDOWS_STABLE" if os.name == "nt" else "RASPBERRY_PI"

    camera_index = settings.index
    if profile == "WINDOWS_STABLE":
        attempts = [
            (camera_index, cv2.CAP_DSHOW),
            (1 - camera_index, cv2.CAP_DSHOW),
        ]
    else:
        attempts = [
            (camera_index, cv2.CAP_V4L2),
            (1 - camera_index, cv2.CAP_V4L2),
            (camera_index, None),
        ]

    for index, backend in attempts:
        cap = cv2.VideoCapture(index) if backend is None else cv2.VideoCapture(index, backend)
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.height)
            cap.set(cv2.CAP_PROP_FPS, settings.fps)
            return cap
        cap.release()

    return None
