import tkinter as tk

from state_manager import StateManager


def main() -> None:
    root = tk.Tk()
    app = StateManager(root)
    app.start()
    root.mainloop()


if __name__ == "__main__":
    main()