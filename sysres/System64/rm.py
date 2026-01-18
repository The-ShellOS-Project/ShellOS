import os
import shutil
import sys

def main():
    """
    Main function to execute the rm command.
    It determines the ShellOS root, validates paths, and performs deletions.
    """
    # Determine the absolute path of the current script.
    script_path = os.path.abspath(__file__)

    # Get the directory where this script resides (e.g., 'ShellOS/System64').
    system64_dir = os.path.dirname(script_path)

    # Go up one level from 'System64' to get the 'ShellOS' root directory.
    shellos_root = os.path.normpath(os.path.join(system64_dir, '..'))

    # --- Security Check: Ensure ShellOS root is a valid directory ---
    if not os.path.isdir(shellos_root):
        print(f"Error: ShellOS root directory not found at '{shellos_root}'.")
        print("Please ensure this script is located within 'ShellOS/System64'.")
        sys.exit(1)

    def is_within_shellos(path):
        """
        Checks if the given path is a subdirectory or file within the ShellOS root,
        but not the ShellOS root directory itself.

        Args:
            path (str): The path to check.

        Returns:
            bool: True if the path is within ShellOS (and not ShellOS itself), False otherwise.
        """
        # Get the absolute and normalized version of the target path.
        abs_path = os.path.abspath(path)
        # Get the absolute and normalized version of the ShellOS root path.
        abs_shellos_root = os.path.abspath(shellos_root)

        # Check if the ShellOS root is a common prefix of the target path.
        # This confirms the target path is inside ShellOS.
        is_subpath = os.path.commonpath([abs_shellos_root, abs_path]) == abs_shellos_root

        # Also ensure that the target path is not the ShellOS root directory itself.
        is_not_shellos_root = abs_path != abs_shellos_root

        return is_subpath and is_not_shellos_root

    def rm_command(target_path):
        """
        Simulates the 'rm' command to delete a file or directory.

        Args:
            target_path (str): The path to the file or directory to delete.
        """
        if not target_path:
            print("Usage: python rm_cmd.py <file_or_directory_path>")
            return

        # Convert the target path to its absolute form to handle relative paths correctly.
        full_target_path = os.path.abspath(target_path)

        # --- Security Check: Restrict deletion to within ShellOS ---
        if not is_within_shellos(target_path):
            print(f"Error: Cannot delete '{target_path}'.")
            print(f"Deletion is strictly limited to files and directories *inside* the '{os.path.basename(shellos_root)}' folder.")
            print(f"You cannot delete the '{os.path.basename(shellos_root)}' folder itself or anything outside it.")
            return

        # Check if the target exists before attempting to delete.
        if not os.path.exists(full_target_path):
            print(f"Error: '{target_path}' not found.")
            return

        try:
            if os.path.isfile(full_target_path):
                # If it's a file, use os.remove()
                os.remove(full_target_path)
                print(f"File '{target_path}' deleted successfully.")
            elif os.path.isdir(full_target_path):
                # --- Specific Security Check: Prevent deleting the System64 directory itself ---
                # This ensures the command doesn't delete the directory it resides in.
                if os.path.normpath(full_target_path) == os.path.normpath(system64_dir):
                    print(f"Error: Cannot delete the '{os.path.basename(system64_dir)}' directory itself.")
                    return
                # If it's a directory, use shutil.rmtree() to remove it and its contents.
                shutil.rmtree(full_target_path)
                print(f"Directory '{target_path}' and its contents deleted successfully.")
            else:
                # Handle cases where the target is neither a file nor a directory (e.g., a symbolic link).
                print(f"Error: '{target_path}' is neither a file nor a directory and cannot be deleted by this command.")
        except PermissionError:
            print(f"Error: Permission denied to delete '{target_path}'.")
            print("Please check your file permissions.")
        except OSError as e:
            # Catch other OS-related errors during deletion.
            print(f"Error deleting '{target_path}': {e}")
        except Exception as e:
            # Catch any unexpected errors.
            print(f"An unexpected error occurred: {e}")

    # --- Command Line Argument Parsing ---
    # sys.argv[0] is the script name itself, so we need at least sys.argv[1] for the target path.
    if len(sys.argv) < 2:
        print("Usage: python rm_cmd.py <file_or_directory_path>")
        print("\nExamples:")
        print(f"  python rm_cmd.py my_file.txt")
        print(f"  python rm_cmd.py my_directory/")
        print(f"  python rm_cmd.py ../ShellOS/another_folder/temp.log")
    else:
        # The first argument after the script name is the target path.
        target = sys.argv[1]
        rm_command(target)

if __name__ == "__main__":
    # Ensure the main function is called only when the script is executed directly.
    main()
