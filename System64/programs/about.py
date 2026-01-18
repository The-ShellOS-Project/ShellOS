import tkinter as tk
from tkinter import Label, Toplevel
from PIL import Image, ImageTk
import os
import sys
import platform
import pip
import webbrowser

# Determine the correct path to system version module
system_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'SYSTEM'))
sys.path.append(system_path)

try:
    from registry import __version__
except ImportError as e:
    # Fallback if registry.py is not found, to allow the program to run
    # (though in a real scenario, this would indicate a setup issue)
    __version__ = "UNKNOWN"
    print(f"Warning: Failed to import __version__. Using 'UNKNOWN'. Details: {e}", file=sys.stderr)


def open_link(event):
    """Opens the specified GitHub link in a web browser."""
    webbrowser.open_new("https://github.com/The-ShellOS-Project")

def about_program(parent):
    """
    Creates and displays the 'About ShellOS' Toplevel window with dark mode styling.
    """
    # Define dark mode colors
    bg_color = "#191919"  # Dark background
    text_color = "white"  # White text for general info
    link_color = "#488FF8" # Light sky blue for links (better contrast on dark)

    # Create the about window
    about_win = Toplevel(parent)
    about_win.title("About ShellOS")
    about_win.geometry("400x320")
    about_win.resizable(False, False)
    about_win.config(bg=bg_color) # Apply dark mode background to the window

    # Load and display the ShellOS logo
    logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'System64', 'resources', 'images', 'shellosverlogo.png'))
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path)
            aspect_ratio = 15.12 / 4.25
            new_width = 150
            new_height = int(new_width / aspect_ratio)
            img = img.resize((new_width, new_height), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
            logo_label = Label(about_win, image=img, bg=bg_color) # Apply dark mode background
            logo_label.image = img  # Keep a reference
            logo_label.pack(pady=10)
        except Exception as e:
            error_label = Label(
                about_win,
                text=f"Error loading image: {e}",
                font=("Arial", 12),
                fg="red", # Keep red for errors
                bg=bg_color # Apply dark mode background
            )
            error_label.pack(pady=10)
    else:
        error_label = Label(
            about_win,
            text="Image not found at path:\n" + logo_path,
            font=("Arial", 12),
            fg="red", # Keep red for errors
            bg=bg_color # Apply dark mode background
        )
        error_label.pack(pady=10)

    # Get dynamic version info
    python_version = platform.python_version()
    pip_version = pip.__version__

    # Display version information
    info_text = f"""ShellOS
Version: {__version__}
Python {python_version}
Pip {pip_version}
© Copyright 2024-2026 
TDot Technologies 
ATGF Technologies Co.
"""
    info_label = Label(
        about_win,
        text=info_text,
        font=("Arial", 12),
        justify="center",
        fg=text_color, # Apply white text color
        bg=bg_color # Apply dark mode background
    )
    info_label.pack(pady=(10, 2))

    # Add clickable GitHub link
    link_label = Label(
        about_win,
        text="https://github.com/The-ShellOS-Project/ShellOS",
        font=("Arial", 10, "underline"),
        fg=link_color, # Apply light blue link color
        cursor="hand2",
        bg=bg_color # Apply dark mode background
    )
    link_label.pack()
    link_label.bind("<Button-1>", open_link)

def main():
    """Main function to initialize and run the Tkinter application."""
    root = tk.Tk()
    root.withdraw()  # Hide the main root window
    about_program(root)
    root.mainloop()

if __name__ == "__main__":
    main()
