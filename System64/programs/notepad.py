import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import json
from datetime import datetime

class ShellOSNotepad(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ShellOS Notepad")
        self.geometry("800x600")
        self.current_file = None
        self.modified = False
        self.font_size = 11
        self.recent_files = self.load_recent_files()

        # Dark mode colors
        BACKGROUND_COLOR = "#191919"  # Very dark grey
        FOREGROUND_COLOR = "#FFFFFF"  # White
        TEXT_AREA_BG = "#2B2B2B"      # Slightly lighter dark grey for text area
        TEXT_AREA_FG = "#FFFFFF"      # White for text area text
        STATUS_BAR_BG = "#0D0D0D"     # Even darker grey for status bar
        STATUS_BAR_FG = "#00D4FF"     # Cyan text for status bar
        ACCENT_COLOR = "#00D4FF"      # Cyan accent

        # Store colors as instance variables
        self.BACKGROUND_COLOR = BACKGROUND_COLOR
        self.FOREGROUND_COLOR = FOREGROUND_COLOR
        self.TEXT_AREA_BG = TEXT_AREA_BG
        self.TEXT_AREA_FG = TEXT_AREA_FG
        self.STATUS_BAR_BG = STATUS_BAR_BG
        self.STATUS_BAR_FG = STATUS_BAR_FG
        self.ACCENT_COLOR = ACCENT_COLOR

        self.config(bg=BACKGROUND_COLOR)

        # Menu bar
        menubar = tk.Menu(self, bg=self.BACKGROUND_COLOR, fg=self.FOREGROUND_COLOR)
        
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.BACKGROUND_COLOR, fg=self.FOREGROUND_COLOR)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.view_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Recent Files", command=self.show_recent_files)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.BACKGROUND_COLOR, fg=self.FOREGROUND_COLOR)
        edit_menu.add_command(label="Undo", command=self.undo)
        edit_menu.add_command(label="Redo", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut_text)
        edit_menu.add_command(label="Copy", command=self.copy_text)
        edit_menu.add_command(label="Paste", command=self.paste_text)
        edit_menu.add_separator()
        edit_menu.add_command(label="Find & Replace", command=self.open_find_replace)
        edit_menu.add_command(label="Clear", command=self.clear_document)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        format_menu = tk.Menu(menubar, tearoff=0, bg=self.BACKGROUND_COLOR, fg=self.FOREGROUND_COLOR)
        format_menu.add_command(label="Increase Font Size", command=self.increase_font)
        format_menu.add_command(label="Decrease Font Size", command=self.decrease_font)
        format_menu.add_command(label="Reset Font Size", command=self.reset_font)
        menubar.add_cascade(label="Format", menu=format_menu)

        view_menu = tk.Menu(menubar, tearoff=0, bg=self.BACKGROUND_COLOR, fg=self.FOREGROUND_COLOR)
        view_menu.add_command(label="Word Count", command=self.show_word_count)
        menubar.add_cascade(label="View", menu=view_menu)

        self.config(menu=menubar)

        # Text area
        self.text = tk.Text(self, undo=True, wrap=tk.WORD, bg=self.TEXT_AREA_BG, fg=self.TEXT_AREA_FG, insertbackground=self.FOREGROUND_COLOR, font=("Consolas", self.font_size))
        self.text.pack(fill=tk.BOTH, expand=True)
        self.text.bind("<KeyRelease>", self.on_text_change)

        # Status bar frame for better organization
        self.status_frame = tk.Frame(self, bg=self.STATUS_BAR_BG, height=30)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Status bar with multiple sections
        self.status_label = tk.Label(self.status_frame, text="Ready", anchor="w", bg=self.STATUS_BAR_BG, fg=self.STATUS_BAR_FG, font=("Consolas", 9))
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)

        # Line and column counter
        self.line_col_label = tk.Label(self.status_frame, text="Line: 1 | Col: 1", anchor="e", bg=self.STATUS_BAR_BG, fg=self.STATUS_BAR_FG, font=("Consolas", 9))
        self.line_col_label.pack(side=tk.RIGHT, padx=5, pady=2)

    def on_text_change(self, event=None):
        """Update line and column information when text changes"""
        pos = self.text.index(tk.INSERT)
        line, col = pos.split('.')
        self.line_col_label.config(text=f"Line: {line} | Col: {int(col) + 1}")
        self.modified = True

    def new_file(self):
        """Create a new document"""
        if self.modified:
            response = messagebox.askyesnocancel("Unsaved Changes", "Save changes before creating a new document?")
            if response is None:
                return
            elif response:
                self.save_file()
        
        self.text.delete(1.0, tk.END)
        self.current_file = None
        self.modified = False
        self.title("ShellOS Notepad")
        self.status_label.config(text="New document created")

    def view_file(self):
        file_path = filedialog.askopenfilename(
            initialdir="System64/Documents",
            title="Open File",
            filetypes=(("Text files", "*.txt"), ("Python files", "*.py"), ("All files", "*.*"))
        )
        if file_path:
            self.open_file(file_path)

    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, 'w') as f:
                    f.write(self.text.get(1.0, tk.END).rstrip())
                self.modified = False
                self.status_label.config(text=f"Saved: {os.path.basename(self.current_file)} ✓")
                self.save_to_recent_files(self.current_file)
                self.title(f"ShellOS Notepad - {os.path.basename(self.current_file)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(
            initialdir="System64/Documents",
            title="Save File As",
            defaultextension=".txt",
            filetypes=(("Text files", "*.txt"), ("Python files", "*.py"), ("All files", "*.*"))
        )
        if file_path:
            self.current_file = file_path
            self.save_file()

    def open_file(self, path):
        try:
            with open(path, 'r') as f:
                content = f.read()
                self.text.delete(1.0, tk.END)
                self.text.insert(tk.END, content)
            self.current_file = path
            self.modified = False
            self.status_label.config(text=f"Opened: {os.path.basename(path)}")
            self.title(f"ShellOS Notepad - {os.path.basename(path)}")
            self.save_to_recent_files(path)
        except FileNotFoundError:
            self.text.delete(1.0, tk.END)
            self.status_label.config(text="File not found.")

    def cut_text(self):
        """Cut selected text"""
        try:
            self.text.event_generate("<<Cut>>")
        except tk.TclError:
            pass

    def copy_text(self):
        """Copy selected text"""
        try:
            self.text.event_generate("<<Copy>>")
        except tk.TclError:
            pass

    def paste_text(self):
        """Paste text from clipboard"""
        try:
            self.text.event_generate("<<Paste>>")
        except tk.TclError:
            pass

    def undo(self):
        try:
            self.text.edit_undo()
        except tk.TclError:
            pass

    def redo(self):
        try:
            self.text.edit_redo()
        except tk.TclError:
            pass

    def clear_document(self):
        """Clear all text from document"""
        response = messagebox.askyesno("Clear Document", "Are you sure you want to clear all text?")
        if response:
            self.text.delete(1.0, tk.END)
            self.status_label.config(text="Document cleared")
            self.modified = True

    def increase_font(self):
        """Increase font size"""
        self.font_size = min(self.font_size + 1, 24)
        self.text.config(font=("Consolas", self.font_size))
        self.status_label.config(text=f"Font size: {self.font_size}")

    def decrease_font(self):
        """Decrease font size"""
        self.font_size = max(self.font_size - 1, 8)
        self.text.config(font=("Consolas", self.font_size))
        self.status_label.config(text=f"Font size: {self.font_size}")

    def reset_font(self):
        """Reset font size to default"""
        self.font_size = 11
        self.text.config(font=("Consolas", self.font_size))
        self.status_label.config(text="Font size reset to default")

    def show_word_count(self):
        """Display word count statistics"""
        text_content = self.text.get(1.0, tk.END).strip()
        words = len(text_content.split())
        characters = len(text_content)
        lines = len(text_content.split('\n'))
        
        messagebox.showinfo("Word Count", f"Words: {words}\nCharacters: {characters}\nLines: {lines}")

    def open_find_replace(self):
        """Open Find and Replace dialog"""
        find_window = tk.Toplevel(self)
        find_window.title("Find and Replace")
        find_window.geometry("400x200")
        find_window.config(bg=self.BACKGROUND_COLOR)

        # Find section
        tk.Label(find_window, text="Find:", bg=self.BACKGROUND_COLOR, fg=self.FOREGROUND_COLOR).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        find_entry = tk.Entry(find_window, bg=self.TEXT_AREA_BG, fg=self.TEXT_AREA_FG, insertbackground=self.FOREGROUND_COLOR)
        find_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Replace section
        tk.Label(find_window, text="Replace:", bg=self.BACKGROUND_COLOR, fg=self.FOREGROUND_COLOR).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        replace_entry = tk.Entry(find_window, bg=self.TEXT_AREA_BG, fg=self.TEXT_AREA_FG, insertbackground=self.FOREGROUND_COLOR)
        replace_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        def find_text():
            search_term = find_entry.get()
            if not search_term:
                messagebox.showwarning("Find", "Please enter text to find")
                return
            
            self.text.tag_remove("found", "1.0", tk.END)
            start_pos = "1.0"
            count = 0
            
            while True:
                start_pos = self.text.search(search_term, start_pos, nocase=True)
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(search_term)}c"
                self.text.tag_add("found", start_pos, end_pos)
                count += 1
                start_pos = end_pos
            
            self.text.tag_config("found", background=self.ACCENT_COLOR, foreground=self.BACKGROUND_COLOR)
            self.status_label.config(text=f"Found {count} match(es)")

        def replace_all():
            search_term = find_entry.get()
            replace_term = replace_entry.get()
            
            if not search_term:
                messagebox.showwarning("Replace", "Please enter text to find")
                return
            
            content = self.text.get(1.0, tk.END)
            count = content.count(search_term)
            new_content = content.replace(search_term, replace_term)
            
            self.text.delete(1.0, tk.END)
            self.text.insert(tk.END, new_content)
            self.status_label.config(text=f"Replaced {count} occurrence(s)")
            self.modified = True

        # Buttons
        button_frame = tk.Frame(find_window, bg=self.BACKGROUND_COLOR)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        find_btn = tk.Button(button_frame, text="Find All", command=find_text, bg=self.ACCENT_COLOR, fg=self.BACKGROUND_COLOR)
        find_btn.pack(side=tk.LEFT, padx=5)

        replace_btn = tk.Button(button_frame, text="Replace All", command=replace_all, bg=self.ACCENT_COLOR, fg=self.BACKGROUND_COLOR)
        replace_btn.pack(side=tk.LEFT, padx=5)

        find_window.columnconfigure(1, weight=1)

    def load_recent_files(self):
        """Load recent files list from config file"""
        config_path = "System64/programs/notepad_config.json"
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    return data.get('recent_files', [])
        except:
            pass
        return []

    def save_to_recent_files(self, file_path):
        """Save file to recent files list"""
        config_path = "System64/programs/notepad_config.json"
        
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]  # Keep only 10 most recent
        
        try:
            with open(config_path, 'w') as f:
                json.dump({'recent_files': self.recent_files}, f)
        except:
            pass

    def show_recent_files(self):
        """Show recent files submenu"""
        if not self.recent_files:
            messagebox.showinfo("Recent Files", "No recent files")
            return
        
        recent_window = tk.Toplevel(self)
        recent_window.title("Recent Files")
        recent_window.geometry("300x300")
        recent_window.config(bg=self.BACKGROUND_COLOR)

        listbox = tk.Listbox(recent_window, bg=self.TEXT_AREA_BG, fg=self.TEXT_AREA_FG)
        listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        for file_path in self.recent_files:
            listbox.insert(tk.END, os.path.basename(file_path))

        def open_selected():
            selection = listbox.curselection()
            if selection:
                self.open_file(self.recent_files[selection[0]])
                recent_window.destroy()

        open_btn = tk.Button(recent_window, text="Open", command=open_selected, bg=self.ACCENT_COLOR, fg=self.BACKGROUND_COLOR)
        open_btn.pack(pady=5)

if __name__ == "__main__":
    app = ShellOSNotepad()
    if len(sys.argv) > 1:
        app.open_file(sys.argv[1])
    app.mainloop()