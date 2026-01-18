import os

# Function to remove a directory
def remove_directory():
    dir_to_remove = input("Enter the name of the directory you want to remove: ")
    if os.path.exists(dir_to_remove) and os.path.isdir(dir_to_remove):
        os.rmdir(dir_to_remove)
        print(f"Directory '{dir_to_remove}' removed successfully!")
    else:
        print(f"Directory '{dir_to_remove}' does not exist or is not a directory.")

# Main loop for removing a directory
while True:
    remove_directory_choice = input("\nDo you want to remove a directory? (yes/no): ").strip().lower()
    
    if remove_directory_choice == 'yes':
        remove_directory()
    elif remove_directory_choice == 'no':
        print("Exiting the program.")
        break
    else:
        print("Invalid input, please answer with 'yes' or 'no'.")
