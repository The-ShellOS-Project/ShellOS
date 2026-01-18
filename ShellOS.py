import subprocess
import sys
import os

def check_critical_files():
    """Checks for critical system files and directories."""
    critical_dirs = ['SYSTEM', 'System64', 'sysres']
    critical_files = [os.path.join('SYSTEM', 'registry.py'), 'requirements.txt']
    for d in critical_dirs:
        if not os.path.isdir(d):
            return False
    for f in critical_files:
        if not os.path.isfile(f):
            return False
    return True

def start_recovery():
    """Starts the recovery environment."""
    recovery_path = os.path.join(os.getcwd(), 'sysres', 'recovery.py')
    if os.path.isfile(recovery_path):
        subprocess.run([sys.executable, recovery_path])
    else:
        print("Recovery system not found. System cannot boot.")
        sys.exit(1)

def install_requirements(run_start=True):
    """Installs required packages from requirements.txt."""
    requirements_file = os.path.join(os.getcwd(), 'requirements.txt')
    if os.path.isfile(requirements_file):
        try:
            print("Installing required packages...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
            print("All required packages installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install required packages: {e}")
            return False
    else:
        print("requirements.txt file not found.")
        return False

    if run_start:
        try:
            print("Running ShlOSStart.py...")
            shlos_start_path = os.path.join(os.getcwd(), 'SYSTEM', 'ShlOSStart.py')
            if os.path.isfile(shlos_start_path):
                subprocess.check_call([sys.executable, shlos_start_path])
                print("ShlOSStart.py ran successfully.")
            else:
                print("ShlOSStart.py not found.")
                return False
        except subprocess.CalledProcessError as e:
            print(f"Failed to run ShlOSStart.py: {e}")
            return False
    return True

if __name__ == "__main__":
    headless = "--headless" in sys.argv or "-headless" in sys.argv
    if headless:
        headless_path = os.path.join(os.getcwd(), 'sysres', 'headless.py')
        if os.path.isfile(headless_path):
            subprocess.check_call([sys.executable, headless_path])
        else:
            print("sysres/headless.py not found.")
            sys.exit(1)
    else:
        if not check_critical_files():
            print("Critical system files missing. Booting to recovery...")
            start_recovery()
            sys.exit(0)
        if not install_requirements(True):
            print("Failed to install requirements or start system. Booting to recovery...")
            start_recovery()
            sys.exit(0)
