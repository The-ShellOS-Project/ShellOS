import customtkinter as ctk
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
import math
import os

# App settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Updated Color Scheme
PRIMARY_COLOR = "#0D3772"
BUTTON_HOVER = "#0A2C5A" # Slightly darker for hover effect
FONT = ("Segoe UI", 14)

class CalculatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("316x489")
        self.title("ShellOS Calculator")

        # Set the window icon
        icon_path = os.path.join("System64", "resources", "icons", "calc.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        self.scientific_mode = False
        self.current_view = "calculator"

        # Main Layout
        self.create_menu()
        
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.create_calculator_view()

    def create_menu(self):
        """Creates a hamburger-style menu at the top"""
        self.menu_frame = ctk.CTkFrame(self, height=40, fg_color="transparent")
        self.menu_frame.pack(fill="x", padx=10, pady=5)

        self.menu_dropdown = ctk.CTkOptionMenu(
            self.menu_frame,
            values=["Standard", "Scientific", "Date Calculator"],
            command=self.menu_callback,
            fg_color=PRIMARY_COLOR,
            button_color=PRIMARY_COLOR,
            button_hover_color=BUTTON_HOVER,
            dynamic_resizing=False,
            width=140
        )
        self.menu_dropdown.set("Menu ≡")
        self.menu_dropdown.pack(side="left")

    def menu_callback(self, choice):
        if choice == "Standard":
            self.scientific_mode = False
            self.create_calculator_view()
        elif choice == "Scientific":
            self.scientific_mode = True
            self.create_calculator_view()
        elif choice == "Date Calculator":
            self.create_date_calculator_view()
        
        self.menu_dropdown.set("Menu ≡") # Reset text after selection

    def create_calculator_view(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.current_view = "calculator"

        # Display Entry
        self.entry = ctk.CTkEntry(
            self.main_frame, 
            font=("Segoe UI", 24), 
            justify="right", 
            corner_radius=10, 
            fg_color="#F0F0F0", 
            text_color="black", 
            height=50
        )
        self.entry.grid(row=0, column=0, columnspan=4, padx=5, pady=10, sticky="ew")

        buttons = [
            ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("/", 1, 3),
            ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("*", 2, 3),
            ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("-", 3, 3),
            ("0", 4, 0), (".", 4, 1), ("=", 4, 2), ("+", 4, 3),
        ]

        for (text, row, col) in buttons:
            ctk.CTkButton(
                self.main_frame, 
                text=text, 
                command=lambda t=text: self.on_button_click(t), 
                fg_color=PRIMARY_COLOR, 
                hover_color=BUTTON_HOVER,
                text_color="white", 
                font=FONT, 
                height=50
            ).grid(row=row, column=col, padx=3, pady=3, sticky="nsew")

        if self.scientific_mode:
            sci_buttons = [
                ("sin", 5, 0), ("cos", 5, 1), ("tan", 5, 2), ("sqrt", 5, 3),
            ]
            for (text, row, col) in sci_buttons:
                ctk.CTkButton(
                    self.main_frame, 
                    text=text, 
                    command=lambda t=text: self.on_scientific_click(t), 
                    fg_color="#1a4a8d", # Slightly lighter blue for sci buttons
                    text_color="white", 
                    font=FONT, 
                    height=40
                ).grid(row=row, column=col, padx=3, pady=3, sticky="nsew")

        # Configure grid weighting
        for i in range(6): self.main_frame.grid_rowconfigure(i, weight=1)
        for i in range(4): self.main_frame.grid_columnconfigure(i, weight=1)

    def on_button_click(self, char):
        if char == "=":
            try:
                # Basic safety check for eval
                result = eval(self.entry.get())
                self.entry.delete(0, tk.END)
                self.entry.insert(0, str(result))
            except Exception:
                messagebox.showerror("Error", "Invalid expression")
        else:
            self.entry.insert(tk.END, char)

    def on_scientific_click(self, func):
        try:
            val = float(self.entry.get())
            if func == "sin": result = math.sin(math.radians(val))
            elif func == "cos": result = math.cos(math.radians(val))
            elif func == "tan": result = math.tan(math.radians(val))
            elif func == "sqrt": result = math.sqrt(val)

            self.entry.delete(0, tk.END)
            self.entry.insert(0, str(round(result, 4)))
        except Exception:
            messagebox.showerror("Error", "Invalid input")

    def create_date_calculator_view(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.current_view = "date_calculator"

        ctk.CTkLabel(self.main_frame, text="Calculate days from today", font=("Segoe UI", 16, "bold")).pack(pady=20)
        ctk.CTkLabel(self.main_frame, text="Enter Date (YYYY-MM-DD):", font=FONT).pack(pady=5)
        
        date_entry = ctk.CTkEntry(self.main_frame, font=FONT, width=200)
        date_entry.pack(pady=10)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        def calculate_days():
            try:
                input_date = datetime.strptime(date_entry.get(), "%Y-%m-%d")
                today = datetime.combine(datetime.today(), datetime.min.time())
                delta = today - input_date
                messagebox.showinfo("Result", f"The difference is {abs(delta.days)} days.")
            except:
                messagebox.showerror("Error", "Use format YYYY-MM-DD")

        ctk.CTkButton(self.main_frame, text="Calculate Difference", command=calculate_days, fg_color=PRIMARY_COLOR, font=FONT).pack(pady=20)
        ctk.CTkButton(self.main_frame, text="← Back", command=self.create_calculator_view, fg_color="transparent", border_width=1, font=FONT).pack(pady=10)

if __name__ == "__main__":
    app = CalculatorApp()
    app.mainloop()