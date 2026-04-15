import os


class CameraSettings:
    def __init__(self) -> None:
        self.index = int(os.getenv("CAMERA_INDEX", "0"))
        self.profile = os.getenv("CAMERA_PROFILE", "AUTO").strip().upper()
        self.width = int(os.getenv("CAMERA_WIDTH", "640"))
        self.height = int(os.getenv("CAMERA_HEIGHT", "480"))
        self.fps = int(os.getenv("CAMERA_FPS", "20"))


class RecognitionSettings:
    def __init__(self) -> None:
        self.scale = float(os.getenv("RECOGNITION_SCALE", "0.25"))
        self.tolerance = float(os.getenv("RECOGNITION_TOLERANCE", "0.5"))
        self.access_cooldown_seconds = float(os.getenv("ACCESS_COOLDOWN_SECONDS", "8.0"))


def get_camera_settings() -> CameraSettings:
    return CameraSettings()


def get_recognition_settings() -> RecognitionSettings:
    return RecognitionSettings()
