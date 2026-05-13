import os
import queue
import threading
from typing import Dict, Optional

try:
    import pygame
except Exception:  # pragma: no cover - optional dependency
    pygame = None


class AudioManager:
    """Controlador de audio Asincrono usando eventos en vez de nombres de archivos."""

    def __init__(self, silent: bool = False):
        self.base_path = os.path.join(os.path.dirname(__file__), "sounds")
        self.silent = silent
        self.sounds: Dict[str, str] = {
            "startup": "startup.wav",
            "success": "success.wav",
            "error": "error.wav",
            "click": "click.wav",
            "register": "register.wav",
        }
        self._queue: "queue.Queue[str]" = queue.Queue()
        self._sound_cache: Dict[str, "pygame.mixer.Sound"] = {}
        self._worker_started = False
        self._worker_lock = threading.Lock()
        self._stop_event = threading.Event()

    def set_silent(self, silent: bool) -> None:
        self.silent = silent

    def play(self, event_name: str) -> None:
        if self.silent:
            return
        if event_name not in self.sounds:
            print(f"AudioManager: evento desconocido '{event_name}'")
            return
        if pygame is None:
            print("AudioManager: pygame no esta disponible")
            return
        self._ensure_worker()
        self._queue.put(event_name)

    def shutdown(self) -> None:
        self._stop_event.set()

    def _ensure_worker(self) -> None:
        if self._worker_started:
            return
        with self._worker_lock:
            if self._worker_started:
                return
            thread = threading.Thread(target=self._worker_loop, daemon=True)
            thread.start()
            self._worker_started = True

    def _worker_loop(self) -> None:
        if pygame is None:
            return
        try:
            pygame.mixer.init()
        except Exception as exc:
            print(f"AudioManager: error inicializando mixer: {exc}")
            return
        while not self._stop_event.is_set():
            try:
                event_name = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue
            try:
                sound = self._get_sound(event_name)
                if sound is not None:
                    sound.play()
            except Exception as exc:
                print(f"AudioManager: error reproduciendo sonido: {exc}")
            finally:
                self._queue.task_done()

    def _get_sound(self, event_name: str) -> Optional["pygame.mixer.Sound"]:
        if event_name in self._sound_cache:
            return self._sound_cache[event_name]
        filename = self.sounds[event_name]
        file_path = os.path.join(self.base_path, filename)
        if not os.path.exists(file_path):
            print(f"AudioManager: archivo no encontrado: {file_path}")
            return None
        try:
            sound = pygame.mixer.Sound(file_path)
        except Exception as exc:
            print(f"AudioManager: error cargando sonido: {exc}")
            return None
        self._sound_cache[event_name] = sound
        return sound
