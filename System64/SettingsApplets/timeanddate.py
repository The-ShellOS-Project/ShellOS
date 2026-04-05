import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import json

SETTINGS_FILE = "time_settings.json"

def set_time():
    selected_date = cal.get_date()
    selected_time = f"{hour_var.get()}:{minute_var.get()}:{second_var.get()}"
    new_datetime = f"{selected_date} {selected_time}"
    
    settings = {"date": str(selected_date), "time": selected_time}
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file)
    
    status_label.config(text=f"Date and Time set to: {new_datetime}")

root = tk.Tk()
root.title("Time and Date Settings")
root.geometry("300x250")

ttk.Label(root, text="Select Date:").pack(pady=5)
cal = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
cal.pack(pady=5)

ttk.Label(root, text="Select Time:").pack(pady=5)
time_frame = ttk.Frame(root)
time_frame.pack(pady=5)

hour_var = tk.StringVar(value='12')
minute_var = tk.StringVar(value='00')
second_var = tk.StringVar(value='00')

hour_box = ttk.Combobox(time_frame, textvariable=hour_var, values=[f"{i:02d}" for i in range(24)], width=3)
minute_box = ttk.Combobox(time_frame, textvariable=minute_var, values=[f"{i:02d}" for i in range(60)], width=3)
second_box = ttk.Combobox(time_frame, textvariable=second_var, values=[f"{i:02d}" for i in range(60)], width=3)

hour_box.pack(side=tk.LEFT, padx=2)
ttk.Label(time_frame, text=":").pack(side=tk.LEFT)
minute_box.pack(side=tk.LEFT, padx=2)
ttk.Label(time_frame, text=":").pack(side=tk.LEFT)
second_box.pack(side=tk.LEFT, padx=2)

apply_button = ttk.Button(root, text="Apply", command=set_time)
apply_button.pack(pady=10)

status_label = ttk.Label(root, text="", foreground="green")
status_label.pack(pady=5)

root.mainloop()
