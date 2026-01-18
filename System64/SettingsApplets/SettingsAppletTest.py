import tkinter as tk
from tkinter import ttk

class AppletTest:
    def __init__(self, master):
        self.master = master
        self.master.title("Applet Test")
        self.master.geometry("400x200")

        ttk.Label(
            master,
            text="Welcome to Applet Test!",
            font=("Arial", 16, "bold")
        ).pack(pady=20)

        ttk.Label(
            master,
            text="This is a test applet.",
            font=("Arial", 12)
        ).pack(pady=10)

# Run the applet
if __name__ == "__main__":
    root = tk.Tk()
    app = AppletTest(root)
    root.mainloop()
