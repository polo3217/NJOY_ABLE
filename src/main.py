from gui_app import NJOYInputGUI
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    # The application class handles theme setup and geometry
    app = NJOYInputGUI(root)
    root.mainloop()