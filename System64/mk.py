import os
import shutil
import sys

# --- Configuration ---
# Determine the absolute path to the directory where this script resides.
# This assumes the script is located at ShellOS/System64/mk_rm_cmd.py
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# The root directory that these commands are allowed to operate within.
# This is derived by going one level up from the SCRIPT_DIR.
# So if SCRIPT_DIR is /path/to/ShellOS/System64, SHELLOS_ROOT will be /path/to/ShellOS
SHELLOS_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir))

print(f"ShellOS Root Directory: {SHELLOS_ROOT}")
print(f"Script Directory: {SCRIPT_DIR}")

# --- Helper Function for Path Validation ---
def is_within_shellos(target_path: str) -> bool:
    """
    Checks if a given target path is strictly within the SHELLOS_ROOT directory.
    This prevents operations outside the controlled environment.
    """
    # Normalize and absolutize the target path to resolve any '..' or '.'
    # and get its full, canonical form.
    abs_target_path = os.path.abspath(target_path)
    print(f"Checking target path: {target_path} (Absolute: {abs_target_path})")

    # Ensure the target path starts with the SHELLOS_ROOT path.
    # The os.path.commonpath check adds robustness against trickier path manipulations
    # like symlinks or trying to navigate out and back in.
    return os.path.commonpath([SHELLOS_ROOT, abs_target_path]) == SHELLOS_ROOT

# --- Command Implementations ---

def mk_command(item_type: str, path: str):
    """
    Implements the 'mk' (make) command for files or directories.
    It respects the ShellOS directory boundary.
    """
    if not is_within_shellos(path):
        print(f"Error: Cannot create '{path}'. Operation is outside the ShellOS directory: {SHELLOS_ROOT}")
        return

    try:
        if item_type == 'dir':
            # Create directories recursively. exist_ok=True prevents an error
            # if the directory already exists.
            os.makedirs(path, exist_ok=True)
            print(f"Directory '{path}' created successfully.")
        elif item_type == 'file':
            # Create an empty file. 'w' mode truncates if it exists, creates if not.
            with open(path, 'w') as f:
                pass
            print(f"File '{path}' created successfully.")
        else:
            print(f"Error: Invalid item type '{item_type}'. Use 'file' or 'dir'.")
    except OSError as e:
        print(f"Error creating '{path}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def rm_command(item_type: str, path: str):
    """
    Implements the 'rm' (remove/delete) command for files or directories.
    It respects the ShellOS directory boundary.
    """
    if not is_within_shellos(path):
        print(f"Error: Cannot delete '{path}'. Operation is outside the ShellOS directory: {SHELLOS_ROOT}")
        return

    try:
        if not os.path.exists(path):
            print(f"Error: '{path}' does not exist.")
            return

        if item_type == 'dir':
            if not os.path.isdir(path):
                print(f"Error: '{path}' is not a directory.")
                return
            # Remove directory and its contents recursively.
            shutil.rmtree(path)
            print(f"Directory '{path}' removed successfully.")
        elif item_type == 'file':
            if not os.path.isfile(path):
                print(f"Error: '{path}' is not a file.")
                return
            # Remove a file.
            os.remove(path)
            print(f"File '{path}' removed successfully.")
        else:
            print(f"Error: Invalid item type '{item_type}'. Use 'file' or 'dir'.")
    except OSError as e:
        print(f"Error deleting '{path}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# --- Main Execution Block ---
def main():
    """
    Parses command-line arguments and dispatches to the appropriate command function.
    Usage: python mk_rm_cmd.py <command> <type> <path>
    Examples:
      python mk_rm_cmd.py mk dir my_new_folder
      python mk_rm_cmd.py mk file my_document.txt
      python mk_rm_cmd.py rm dir old_folder
      python mk_rm_cmd.py rm file old_document.txt
    """
    if len(sys.argv) < 4:
        print("Usage: python mk_rm_cmd.py <command> <type> <path>")
        print("Commands: mk (make), rm (remove)")
        print("Types: file, dir")
        print("Examples:")
        print("  python mk_rm_cmd.py mk dir my_new_folder")
        print("  python mk_rm_cmd.py mk file my_document.txt")
        print("  python mk_rm_cmd.py rm dir old_folder")
        print("  python mk_rm_cmd.py rm file old_document.txt")
        sys.exit(1)

    command = sys.argv[1].lower()
    item_type = sys.argv[2].lower()
    path = sys.argv[3]

    if command == 'mk':
        mk_command(item_type, path)
    elif command == 'rm':
        rm_command(item_type, path)
    else:
        print(f"Error: Unknown command '{command}'. Use 'mk' or 'rm'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
