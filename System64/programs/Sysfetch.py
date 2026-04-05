import os
import platform
import time
import subprocess
import psutil

def get_versions():
    """
    Retrieves the __version__ (OS version) and core_version from SYSTEM/registry.py.
    """
    os_version = "Unknown"
    core_version = "Unknown"
    try:
        # Assuming the current script is in System64/programs
        # and registry.py is in SYSTEM/registry.py relative to the root.
        # So, we need to go up two directories from System64/programs to get to the root,
        # then down into SYSTEM.
        script_dir = os.path.dirname(__file__)
        system_dir = os.path.abspath(os.path.join(script_dir, os.pardir, os.pardir, "SYSTEM"))
        version_path = os.path.join(system_dir, "registry.py")

        spec = {}
        with open(version_path, "r") as f:
            exec(f.read(), spec)
        os_version = spec.get("__version__", "Unknown")
        core_version = spec.get("core_version", "Unknown")
    except Exception as e:
        print(f"Error reading registry.py: {e}")
    return os_version, core_version

def get_uptime():
    uptime_seconds = time.time() - psutil.boot_time()
    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def get_pip_version():
    try:
        output = subprocess.check_output(["pip", "--version"], text=True)
        return output.split()[1]
    except Exception:
        return "Unknown"

def get_cpu_info():
    try:
        cpu = platform.processor()
        freq = psutil.cpu_freq()
        if freq:
            freq_str = f"{freq.current:.2f} GHz"
        else:
            freq_str = "Unknown"
        return f"{cpu} @ {freq_str}"
    except Exception:
        return "Unknown"

def get_memory_usage():
    try:
        mem = psutil.virtual_memory()
        used_gb = mem.used / (1024 ** 3)
        total_gb = mem.total / (1024 ** 3)
        return f"{used_gb:.2f} GB / {total_gb:.2f} GB"
    except Exception:
        return "Unknown"

def main():
    os_version, core_version = get_versions()
    print(f"OS: ShellOS: Python Edition {os_version}")
    print(f"Core: {core_version}") # Changed to use the retrieved core_version
    print(f"Uptime: {get_uptime()}")
    print(f"Python: {platform.python_version()}")
    print(f"Pip: {get_pip_version()}")
    print("Shell: ShellOS Terminal")
    print(f"CPU: {get_cpu_info()}")
    print(f"Memory: {get_memory_usage()}")

if __name__ == "__main__":
    main()