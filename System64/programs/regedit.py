import tkinter as tk
from tkinter import messagebox, ttk
import ast
import os

# --- Path Configuration ---
# Get the directory where THIS script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Navigate up two levels to /ShellOS/ and then into /SYSTEM/
REGISTRY_PATH = os.path.join(BASE_DIR, "..", "..", "SYSTEM", "Registry.py")

class RegistryEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("ShellOS Registry Editor")
        self.root.geometry("600x450")
        self.registry_data = {}

        self.setup_ui()
        self.load_registry()

    def setup_ui(self):
        # Top Label showing path
        path_label = tk.Label(self.root, text=f"Path: {REGISTRY_PATH}", fg="gray")
        path_label.pack(pady=2)

        # Table to display keys and values
        self.tree = ttk.Treeview(self.root, columns=("Key", "Value"), show='headings')
        self.tree.heading("Key", text="Registry Key")
        self.tree.heading("Value", text="Current Value")
        self.tree.column("Key", width=200)
        self.tree.column("Value", width=350)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Input Area
        input_frame = tk.LabelFrame(self.root, text="Edit / Create Entry", padx=10, pady=10)
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(input_frame, text="Key:").grid(row=0, column=0, sticky="w")
        self.key_entry = tk.Entry(input_frame)
        self.key_entry.grid(row=0, column=1, sticky="ew", padx=5)

        tk.Label(input_frame, text="Value:").grid(row=1, column=0, sticky="w")
        self.val_entry = tk.Entry(input_frame)
        self.val_entry.grid(row=1, column=1, sticky="ew", padx=5)

        input_frame.columnconfigure(1, weight=1)

        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(btn_frame, text="Update/Add", command=self.save_entry, bg="#e1e1e1").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_entry).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Refresh", command=self.load_registry).pack(side=tk.RIGHT, padx=5)

    def load_registry(self):
        if not os.path.exists(REGISTRY_PATH):
            messagebox.showerror("Error", f"Registry file not found at:\n{REGISTRY_PATH}")
            return

        try:
            with open(REGISTRY_PATH, "r") as f:
                content = f.read()
                tree = ast.parse(content)
            
            self.registry_data = {}
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            val = ast.literal_eval(node.value)
                            self.registry_data[target.id] = val
            
            self.refresh_tree()
        except Exception as e:
            messagebox.showerror("Parse Error", f"Failed to parse Registry.py:\n{e}")

    def refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for key, val in self.registry_data.items():
            self.tree.insert("", tk.END, values=(key, val))

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            key, val = item['values']
            self.key_entry.delete(0, tk.END)
            self.key_entry.insert(0, key)
            self.val_entry.delete(0, tk.END)
            self.val_entry.insert(0, val)

    def save_entry(self):
        key = self.key_entry.get().strip().replace(" ", "_")
        val_raw = self.val_entry.get().strip()

        if not key:
            return

        # Simple logic to handle strings vs numbers
        if (val_raw.startswith("'") and val_raw.endswith("'")) or \
           (val_raw.startswith('"') and val_raw.endswith('"')):
            val = val_raw.strip("'\"")
        elif val_raw.replace('.','',1).isdigit():
            val = float(val_raw) if '.' in val_raw else int(val_raw)
        else:
            val = val_raw # Default to string

        self.registry_data[key] = val
        self.write_to_file()
        self.refresh_tree()

    def delete_entry(self):
        key = self.key_entry.get().strip()
        if key in self.registry_data:
            if messagebox.askyesno("Confirm", f"Delete registry key '{key}'?"):
                del self.registry_data[key]
                self.write_to_file()
                self.refresh_tree()

    def write_to_file(self):
        try:
            with open(REGISTRY_PATH, "w") as f:
                f.write("# ShellOS Registry Keys\n\n")
                for key, val in self.registry_data.items():
                    if isinstance(val, str):
                        f.write(f'{key} = "{val}"\n')
                    else:
                        f.write(f'{key} = {val}\n')
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not write to file:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RegistryEditor(root)
    root.mainloop()