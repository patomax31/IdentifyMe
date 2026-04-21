import os


class CameraSettings:
    def __init__(self) -> None:
        self.index = int(os.getenv("CAMERA_INDEX", "0"))
        self.profile = os.getenv("CAMERA_PROFILE", "AUTO").strip().upper()
        self.width = int(os.getenv("CAMERA_WIDTH", "640"))
        self.height = int(os.getenv("CAMERA_HEIGHT", "480"))
        self.fps = int(os.getenv("CAMERA_FPS", "20"))


def get_camera_settings() -> CameraSettings:
    return CameraSettings()
