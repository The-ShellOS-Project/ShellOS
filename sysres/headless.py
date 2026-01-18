import os
import sys
import subprocess
import threading
import importlib.util

class bcolors:
    PURPLE = '\033[95m'
    ENDC = '\033[0m'

class TerminalCLI:
    def __init__(self):
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        self.shellos_root = os.path.dirname(current_script_dir)
        self.cwd = current_script_dir

        # --- New code to get the version ---
        self.shell_version = self.get_shellos_ver()
        # --- End of new code ---

        # --- New code to get the version ---
        self.shell_version = self.get_shellos_ver()
        # --- End of new code ---

        # Check if a file was passed as argument to execute
        if len(sys.argv) > 1:
            file_to_execute = sys.argv[1]
            self.execute_file_on_load(file_to_execute)

        self.display_banner()
        self.run_terminal()

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
            try:
                result = subprocess.run(
                    [sys.executable, file_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=300,
                    env=os.environ,
                    cwd=self.cwd
                )

                if result.stdout:
                    for line in result.stdout.splitlines():
                        self.insert_colored_line(line + "\n")
                if result.stderr:
                    print(f"{result.stderr}\n")

            except subprocess.TimeoutExpired:
                print("Error: Process timed out.\n")
            except Exception as e:
                print(f"Error: {str(e)}\n")
        else:
            print(f"Error: File not found: {file_path}\n")

    def display_banner(self):
        banner_text = f"ShellOS {self.shell_version}\nHeadless Mode\n"
        print(banner_text)

    def resolve_path(self, relative_path):
        if hasattr(self, 'shellos_root') and self.shellos_root:
            if relative_path.startswith("ShellOS/sysres/"):
                relative_path = relative_path[len("ShellOS/sysres/"):]
            return os.path.join(self.shellos_root, *relative_path.split("/"))
        else:
            print(f"Error: ShellOS root not set. Cannot resolve {relative_path}.")
            return relative_path

    def run_terminal(self):
        while True:
            try:
                command_text = input(f"{self.cwd}> ")
                self.process_command(command_text)
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except EOFError:
                break

    def process_command(self, command_text):
        parts = command_text.split()
        command = parts[0].lower() if parts else ""
        args = parts[1:]

        if command == "exit":
            print("Exiting...")
            sys.exit(0)
        elif command == "cd":
            self.change_directory(args)
            return
        elif command == "clear":
            self.clear_screen()
            return
        else:
            command_found_and_executed = False

            # --- MODIFIED CODE START ---
            shellos_executable_dirs = [
                os.path.join(self.cwd, "System64"),
                os.path.join(self.cwd, "System64", "Programs"),
                os.path.join(self.cwd, "System64", "Programs", "games"), # Added this line
                os.path.join(self.cwd, "System64", "Cmdlets")
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

            if not command_found_and_executed:
                print(f"Command '{command}' not found in recovery system.\n")

    def change_directory(self, args):
        if not args:
            self.cwd = os.path.expanduser("~")
        else:
            new_path = os.path.abspath(os.path.join(self.cwd, " ".join(args)))
            if os.path.isdir(new_path):
                self.cwd = new_path
            else:
                print(f"cd: no such directory: {new_path}\n")

    def clear_screen(self):
        if os.name == 'nt':  # Windows
            os.system('cls')
        else:  # Unix/Linux/Mac
            os.system('clear')

    def insert_colored_line(self, line):
        if line.startswith(">>"):
            parts = line[2:].split(":", 1)
            if len(parts) == 2:
                label, value = parts
                print(f"{bcolors.PURPLE}{label.strip()}:", end="")
                print(f"{value}{bcolors.ENDC}")
                return
        print(line, end="")

    def run_file(self, file_path, args):
        if not os.path.isfile(file_path):
            print(f"Error: File '{file_path}' not found.\n")
            return

        try:
            if file_path.endswith(".py"):
                cmd = [sys.executable, file_path] + args
            elif file_path.endswith(".ssl"):
                ssl_path = os.path.join(self.cwd, "System64", "ShellOS-Scripting-Language", "ssl.py")
                cmd = [sys.executable, ssl_path, file_path] + args
            elif sys.platform == "win32" and file_path.endswith(".bat"):
                cmd = [file_path] + args
            elif not sys.platform == "win32" and file_path.endswith(".sh"):
                cmd = ["bash", file_path] + args
            else:
                print("Error: Unsupported file type or platform mismatch.\n")
                return

            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, cwd=self.cwd, shell=False, timeout=60,
                env=os.environ
            )

            if result.stdout:
                for line in result.stdout.splitlines():
                    self.insert_colored_line(line + "\n")
            if result.stderr:
                print(f"Error: {result.stderr}\n")

        except subprocess.TimeoutExpired:
            print("Error: Process timed out.\n")
        except Exception as e:
            print(f"Error: {str(e)}\n")

if __name__ == "__main__":
    app = TerminalCLI()