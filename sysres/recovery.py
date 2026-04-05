import os
import sys
import subprocess

def main():
    print("ShellOS Recovery Environment")
    print("1. Start ShellOS Headless")
    print("2. Start ShellOS Normally")
    print("3. Shutdown")

    while True:
        choice = input("Select an option: ").strip()
        if choice == "1":
            # Start ShellOS Headless
            headless_path = os.path.join(os.path.dirname(__file__), "headless.py")
            if os.path.isfile(headless_path):
                subprocess.run([sys.executable, headless_path])
            else:
                print("headless.py not found.")
        elif choice == "2":
            # Start ShellOS Normally
            shellos_path = os.path.join(os.path.dirname(__file__), "..", "ShellOS.py")
            if os.path.isfile(shellos_path):
                subprocess.run([sys.executable, shellos_path])
            else:
                print("ShellOS.py not found.")
        elif choice == "3":
            print("Shutting down...")
            sys.exit(0)
        else:
            print("Invalid option. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()
