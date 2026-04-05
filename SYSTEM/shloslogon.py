import json
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_FILE = os.path.join(script_dir, "accounts.json")

def get_password(prompt='Password: '):
    password = ''
    print(prompt, end='', flush=True)

    if os.name == 'nt':
        import msvcrt
        while True:
            ch = msvcrt.getch()
            if ch in (b'\r', b'\n'):
                print()
                break
            elif ch == b'\x08': 
                if len(password) > 0:
                    password = password[:-1]
                    print('\b \b', end='', flush=True)
            elif ch == b'\x03': 
                raise KeyboardInterrupt
            else:
                try:
                    char = ch.decode()
                except UnicodeDecodeError:
                    continue
                password += char
                print('*', end='', flush=True)
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch in ('\r', '\n'):
                    print()
                    break
                elif ch == '\x7f':  
                    if len(password) > 0:
                        password = password[:-1]
                        print('\b \b', end='', flush=True)
                elif ch == '\x03':
                    raise KeyboardInterrupt
                else:
                    password += ch
                    print('*', end='', flush=True)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return password

def load_accounts():
    if not os.path.exists(ACCOUNTS_FILE):
        return []
    with open(ACCOUNTS_FILE, "r") as f:
        return json.load(f)

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f, indent=4)

def list_visible_accounts(accounts):
    return [acct for acct in accounts if not acct.get("hidden", False)]

def create_account():
    print("\n--- Create New Account ---")
    name = input("Enter username: ").strip()
    password = get_password("Enter password: ").strip()
    new_account = {
        "name": name,
        "password": password,
        "hidden": False
    }
    accounts = load_accounts()
    accounts.append(new_account)
    save_accounts(accounts)
    print(f"Account '{name}' created successfully.\n")
    return new_account

def login_screen():
    while True:
        accounts = load_accounts()
        visible_accounts = list_visible_accounts(accounts)

        if not visible_accounts:
            print("No accounts found.")
            create_account()
            continue

        print("\nAccount List:")
        for idx, acct in enumerate(visible_accounts, start=1):
            print(f"{idx}. {acct['name']}")
        print(f"{len(visible_accounts)+1}. Create Account")

        choice = input("\nSelect an account by number: ").strip()

        if not choice.isdigit():
            print("Invalid input. Please enter a number.\n")
            continue

        choice = int(choice)
        if 1 <= choice <= len(visible_accounts):
            selected_account = visible_accounts[choice - 1]
            password = get_password(f"Enter password for {selected_account['name']}: ").strip()
            if password == selected_account["password"]:
                print(f"\nLogged in as {selected_account['name']}.\n")
                return
            else:
                print("Incorrect password. Try again.\n")
        elif choice == len(visible_accounts) + 1:
            create_account()
        else:
            print("Invalid choice. Try again.\n")

def run_shell():
    GUI = os.path.join(script_dir, "Graphical_Shell", "GraphicalShell.py")
    GUI = os.path.abspath(GUI)
    if os.path.exists(GUI):
        os.system(f'python "{GUI}"')
    else:
        print(f"Error: {GUI} not found.")

if __name__ == "__main__":
    login_screen()
    run_shell()
