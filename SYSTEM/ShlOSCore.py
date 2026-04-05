import os
import subprocess

script_dir = os.path.dirname(os.path.abspath(__file__))
login_script = os.path.join(script_dir, "shloslogon.py")

def run_shellos():
    # runs shit that lets you log into your user account to actually access shellos
    if os.path.exists(login_script):
        subprocess.run(["python", login_script])
    else:
        print(f"Error: {login_script} not found.")
        return

if __name__ == "__main__":
    run_shellos()
