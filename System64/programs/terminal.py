import os
import sys
import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading
import importlib.util

class TerminalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ShellOS Terminal")

        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        shellos_index = current_script_dir.find("ShellOS")
        if shellos_index != -1:
            self.shellos_root = current_script_dir[:shellos_index + len("ShellOS")]
        else:
            print("Warning: 'ShellOS' directory not found in current path. Some paths might not resolve correctly.")
            self.shellos_root = os.getcwd()

        self.cwd = self.shellos_root

        # --- New code to get the version ---
        self.shell_version = self.get_shellos_ver()
        # --- End of new code ---

        icon_path = self.resolve_path("ShellOS/SYSTEM/Graphical_Shell/icons/terminal.png")
        if os.path.exists(icon_path):
            icon_image = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(False, icon_image)
        else:
            print(f"Warning: Icon file not found at {icon_path}")

        self.terminal = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, bg="black", fg="white",
            insertbackground="white", font=("Consolas", 12),
            undo=True
        )
        self.terminal.pack(expand=True, fill=tk.BOTH)

        self.terminal.bind("<Return>", self.process_command)
        self.terminal.bind("<BackSpace>", self.prevent_backspace)
        self.terminal.bind("<Key>", self.prevent_edit_before_prompt)

        self.terminal.tag_config("prompt", foreground="white")

        self.display_banner()
        self.insert_prompt()
        
        # Check if a file was passed as argument to execute
        if len(sys.argv) > 1:
            file_to_execute = sys.argv[1]
            self.execute_file_on_load(file_to_execute)

    def get_shellos_ver(self):
        version_file_path = os.path.join(self.shellos_root, "SYSTEM", "registry.py")
        if os.path.exists(version_file_path):
            spec = importlib.util.spec_from_file_location("version_module", version_file_path)
            version_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(version_module)
            return getattr(version_module, '__version__', 'Unknown Version')
        return 'Unknown Version'

    def execute_file_on_load(self, file_path):
        """Execute a Python file passed as argument on terminal load."""
        if os.path.isfile(file_path):
            def execute():
                try:
                    result = subprocess.run(
                        [sys.executable, file_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=300,
                        env=os.environ
                    )
                    
                    if result.stdout:
                        for line in result.stdout.splitlines():
                            self.root.after(0, lambda line=line: self.insert_colored_line(line + "\n"))
                    if result.stderr:
                        self.root.after(0, lambda: self.terminal.insert(tk.END, f"{result.stderr}\n"))
                
                except subprocess.TimeoutExpired:
                    self.root.after(0, lambda: self.terminal.insert(tk.END, "Error: Process timed out.\n"))
                except Exception as e:
                    self.root.after(0, lambda: self.terminal.insert(tk.END, f"Error: {str(e)}\n"))
                
                self.root.after(0, self.insert_prompt)
                self.root.after(0, lambda: self.terminal.see(tk.END))
            
            threading.Thread(target=execute, daemon=True).start()
        else:
            self.terminal.insert(tk.END, f"Error: File not found: {file_path}\n")
            self.insert_prompt()

    def display_banner(self):
        banner_text = f"ShellOS: Python Edition {self.shell_version}\n"
        self.terminal.insert(tk.END, banner_text)
        self.terminal.insert(tk.END, "\n")

    def resolve_path(self, relative_path):
        if hasattr(self, 'shellos_root') and self.shellos_root:
            if relative_path.startswith("ShellOS/"):
                relative_path = relative_path[len("ShellOS/"):]
            return os.path.join(self.shellos_root, *relative_path.split("/"))
        else:
            print(f"Error: ShellOS root not set. Cannot resolve {relative_path}.")
            return relative_path

    def insert_prompt(self):
        prompt = f"{self.cwd}>"
        self.terminal.insert(tk.END, prompt, "prompt")
        self.terminal.mark_set("insert", tk.END)
        self.prompt_index = self.terminal.index("insert")

    def process_command(self, event):
        line_start = self.terminal.index("insert linestart")
        line_end = self.terminal.index("insert lineend")
        line_text = self.terminal.get(line_start, line_end).strip()

        if ">" in line_text:
            command_text = line_text.split(">", 1)[-1].strip()
        else:
            command_text = line_text.strip()

        self.terminal.insert(tk.END, "\n")
        threading.Thread(target=self.execute_command, args=(command_text,), daemon=True).start()
        return "break"

    def prevent_backspace(self, event):
        if self.terminal.compare("insert", "<=", self.prompt_index):
            return "break"
        return None

    def prevent_edit_before_prompt(self, event):
        if event.keysym in ("Left", "BackSpace") and self.terminal.compare("insert", "<=", self.prompt_index):
            return "break"
        return None

    def execute_command(self, command_text):
        parts = command_text.split()
        command = parts[0].lower() if parts else ""
        args = parts[1:]

        if command == "cd":
            self.root.after(0, lambda: self.change_directory(args))
            self.root.after(0, self.insert_prompt)
            return
        elif command == "clear":
            self.root.after(0, lambda: self.terminal.delete("1.0", tk.END))
            self.root.after(0, self.insert_prompt)
            return
        else:
            command_found_and_executed = False

            # --- MODIFIED CODE START ---
            shellos_executable_dirs = [
                os.path.join(self.shellos_root, "System64"),
                os.path.join(self.shellos_root, "System64", "Programs"),
                os.path.join(self.shellos_root, "System64", "Programs", "games"), # Added this line
                os.path.join(self.shellos_root, "System64", "Cmdlets")
            ]
            # --- MODIFIED CODE END ---

            for directory in shellos_executable_dirs:
                possible_py_file = os.path.join(directory, command + ".py")
                if os.path.isfile(possible_py_file):
                    self.run_file(possible_py_file, args)
                    command_found_and_executed = True
                    break

            if not command_found_and_executed:
                possible_ssl_file = os.path.join(self.cwd, command)
                if os.path.isfile(possible_ssl_file) and possible_ssl_file.endswith('.ssl'):
                    self.run_file(possible_ssl_file, args)
                    command_found_and_executed = True

            if command_found_and_executed:
                return

            try:
                process = subprocess.Popen(
                    command_text, shell=True, cwd=self.cwd,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                    env=os.environ
                )
                for line in process.stdout:
                    self.root.after(0, lambda line=line: self.insert_colored_line(line))
                process.wait()
            except Exception as e:
                self.root.after(0, lambda: self.terminal.insert(tk.END, f"Shell error: {str(e)}\n"))
            finally:
                self.root.after(0, self.insert_prompt)
                self.root.after(0, lambda: self.terminal.see(tk.END))

    def change_directory(self, args):
        if not args:
            self.cwd = os.path.expanduser("~")
        else:
            new_path = os.path.abspath(os.path.join(self.cwd, " ".join(args)))
            if os.path.isdir(new_path):
                self.cwd = new_path
            else:
                self.terminal.insert(tk.END, f"cd: no such directory: {new_path}\n")

    def insert_colored_line(self, line):
        if line.startswith(">>"):
            parts = line[2:].split(":", 1)
            if len(parts) == 2:
                label, value = parts
                self.terminal.insert(tk.END, f"{label.strip()}:", "shlos_purple")
                self.terminal.insert(tk.END, f"{value}\n")
                return
        self.terminal.insert(tk.END, line)

    def run_file(self, file_path, args):
        if not os.path.isfile(file_path):
            self.root.after(0, lambda: self.terminal.insert(tk.END, f"Error: File '{file_path}' not found.\n"))
            self.root.after(0, self.insert_prompt)
            return

        def task():
            try:
                if file_path.endswith(".py"):
                    cmd = [sys.executable, file_path] + args
                elif file_path.endswith(".ssl"):
                    ssl_path = os.path.join(self.shellos_root, "System64", "ShellOS-Scripting-Language", "ssl.py")
                    cmd = [sys.executable, ssl_path, file_path] + args
                elif sys.platform == "win32" and file_path.endswith(".bat"):
                    cmd = [file_path] + args
                elif not sys.platform == "win32" and file_path.endswith(".sh"):
                    cmd = ["bash", file_path] + args
                else:
                    self.root.after(0, lambda: self.terminal.insert(tk.END, "Error: Unsupported file type or platform mismatch.\n"))
                    self.root.after(0, self.insert_prompt)
                    return

                result = subprocess.run(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, cwd=self.cwd, shell=False, timeout=60,
                    env=os.environ
                )

                if result.stdout:
                    for line in result.stdout.splitlines():
                        self.root.after(0, lambda line=line: self.insert_colored_line(line + "\n"))
                if result.stderr:
                    self.root.after(0, lambda: self.terminal.insert(tk.END, f"Error: {result.stderr}\n"))

            except subprocess.TimeoutExpired:
                self.root.after(0, lambda: self.terminal.insert(tk.END, "Error: Process timed out.\n"))
            except Exception as e:
                self.root.after(0, lambda: self.terminal.insert(tk.END, f"Error: {str(e)}\n"))

            self.root.after(0, self.insert_prompt)
            self.root.after(0, lambda: self.terminal.see(tk.END))

        threading.Thread(target=task, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = TerminalApp(root)
    root.geometry("640x440")
    root.mainloop()