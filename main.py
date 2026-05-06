import tkinter as tk

from state_manager import StateManager


class MainWindow:
    """Compatibilidad con integraciones antiguas que esperan MainWindow.

    La implementación real vive en `StateManager`.
    """

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.app = StateManager(self.root)

    def start(self) -> None:
        self.app.start()

    def run(self) -> None:
        self.start()
        self.root.mainloop()


def main() -> None:
    window = MainWindow()
    window.run()


__all__ = ["MainWindow", "main"]


if __name__ == "__main__":
    main()