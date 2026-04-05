import tkinter as tk
from tkinter import ttk
import os
import subprocess
import json

class SettingsPanel:
    def __init__(self, master):
        # Set up the main window
        self.master = master
        self.master.title("Settings Panel")
        self.master.geometry("600x400")
        self.master.configure(bg="#191919") # Set window background to dark mode

        # Header
        ttk.Label(
            master,
            text="Settings Panel",
            font=("Arial", 18, "bold"),
            background="#191919", # Dark mode background for label
            foreground="white" # White text for contrast
        ).pack(pady=10)

        # Frame for applet list
        self.settings_frame = tk.Frame(master, bg="#191919") # Dark mode background for frame
        self.settings_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # List of applets
        self.applets = []
        self.load_applets()

        # Add applets to UI
        self.display_applets()

    def load_applets(self):
        """Load applets dynamically from a predefined list."""
        # Define applets manually for now with the correct path for the background settings script
        self.applets = [
            ("Time and Date", "System64/SettingsApplets/timeanddate.py"),
        ]

    def display_applets(self):
        """Display the list of applets in the UI."""
        row = 0
        for applet_name, applet_path in self.applets:
            ttk.Label(
                self.settings_frame,
                text=applet_name,
                font=("Arial", 12),
                background="#191919", # Dark mode background for label
                foreground="white" # White text for contrast
            ).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            
            # Create a style for the dark mode button
            style = ttk.Style()
            style.theme_use('default') # Use a default theme to customize from
            style.configure(
                "Dark.TButton", 
                background="#333333", # Darker grey for button background
                foreground="white", # White text for button
                font=("Arial", 10, "bold")
            )
            style.map(
                "Dark.TButton", 
                background=[('active', '#555555')] # Even darker grey on hover
            )

            open_button = ttk.Button(
                self.settings_frame,
                text="Open",
                command=lambda path=applet_path: self.open_applet(path),
                style="Dark.TButton" # Apply the dark mode style
            )
            open_button.grid(row=row, column=1, padx=10, pady=5)
            row += 1

    def open_applet(self, path):
        """Open the applet by running the associated file."""
        try:
            # Use subprocess to run the applet
            subprocess.Popen(["python", path], shell=True)
            print(f"Opened applet: {path}")
        except Exception as e:
            print(f"Failed to open applet: {e}")

# Run the Settings Panel
if __name__ == "__main__":
    root = tk.Tk()
    app = SettingsPanel(root)
    root.mainloop()