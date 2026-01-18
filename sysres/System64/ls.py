import os
import sys

def list_directory_contents(path="."):
    """
    Lists the contents of a specified directory.

    Args:
        path (str): The path to the directory to list. Defaults to the current directory.

    Returns:
        None: Prints the directory contents to the console.
    """
    try:
        # Check if the path exists
        if not os.path.exists(path):
            print(f"Error: Path '{path}' does not exist.")
            return

        # Check if the path is a directory
        if not os.path.isdir(path):
            print(f"Error: '{path}' is not a directory.")
            # If it's a file, we can optionally just print its name
            print(f"It is a file: {os.path.basename(path)}")
            return

        print(f"Contents of '{path}':")
        # Get all entries (files and directories) in the specified path
        entries = os.listdir(path)

        if not entries:
            print("(Directory is empty)")
        else:
            # Sort the entries alphabetically for a consistent output
            entries.sort(key=str.lower) # Case-insensitive sort

            # Iterate through the entries and print them
            for entry in entries:
                full_path = os.path.join(path, entry)
                if os.path.isdir(full_path):
                    # Mark directories with a trailing slash, similar to 'ls -F'
                    print(f"{entry}/")
                else:
                    print(entry)

    except PermissionError:
        print(f"Error: Permission denied to access '{path}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Check if a path argument was provided
    if len(sys.argv) > 1:
        # If yes, use the first argument as the path
        target_path = sys.argv[1]
    else:
        # If no argument, default to the current directory
        target_path = "."

    list_directory_contents(target_path)
