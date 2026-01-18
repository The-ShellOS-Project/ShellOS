import os
import sys
import zipfile
import shutil
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROGRAMS_DIR = BASE_DIR

DEFAULT_REPO_BASE = "https://github.com/The-ShellOS-Project/ShellOS-Packages/raw/main/"

def find_package_file(name):
    file_extensions = ['.zip', '.py']
    for ext in file_extensions:
        filename = f"{name}{ext}"
        url = f"{DEFAULT_REPO_BASE}{filename}"
        try:
            # Use requests.get with stream=True and a small chunk size
            # to check if the file exists without downloading the whole thing
            with requests.get(url, stream=True) as response:
                if response.status_code == 200:
                    # File exists, immediately close the connection
                    # We don't need to read content here, just confirm 200 OK
                    for _ in response.iter_content(chunk_size=1):
                        break # Read just one byte to trigger potential errors if content is weird
                    return filename, url
                elif response.status_code == 404:
                    continue # File not found for this extension, try next
                else:
                    print(f"[WARN] Received status code {response.status_code} for {url}")
        except requests.exceptions.RequestException:
            pass # Ignore network errors for a specific file, try next
    return None, None

def install_package(arg):
    if not os.path.exists(PROGRAMS_DIR):
        os.makedirs(PROGRAMS_DIR)

    is_url = arg.startswith("http://") or arg.startswith("https://")

    if is_url:
        filename_with_ext = os.path.basename(arg)
        name = os.path.splitext(filename_with_ext)[0]
        url = arg
    else:
        filename_with_ext, url = find_package_file(arg)
        if not filename_with_ext:
            print(f"[ERROR] Package '{arg}' not found in the repository.")
            return
        name = os.path.splitext(filename_with_ext)[0]

    dest_path = os.path.join(PROGRAMS_DIR, filename_with_ext)
    extract_path = os.path.join(PROGRAMS_DIR, name)

    try:
        print(f"Downloading {url}...")
        # Re-download the file, as find_package_file only confirmed existence
        with requests.get(url, stream=True) as response:
            response.raise_for_status()

            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Downloaded '{filename_with_ext}' to '{dest_path}'")

        if dest_path.endswith(".zip"):
            if os.path.exists(extract_path):
                shutil.rmtree(extract_path)
            os.makedirs(extract_path)
            print(f"Extracting '{filename_with_ext}' to '{extract_path}'...")
            with zipfile.ZipFile(dest_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            os.remove(dest_path)
            print(f"Installed '{name}' from zip.")
        else:
            print(f"Installed '{filename_with_ext}' as standalone .py script.")

    except requests.exceptions.HTTPError as e:
        print(f"Failed to download '{filename_with_ext}'. HTTP Status code: {e.response.status_code}.")
    except requests.exceptions.RequestException as e:
        print(f"Network error during download of '{filename_with_ext}': {e}")
    except zipfile.BadZipFile:
        print(f"Downloaded file '{filename_with_ext}' is not a valid zip file.")
        if os.path.exists(dest_path):
            os.remove(dest_path)
    except Exception as e:
        print(f"An unexpected error occurred during installation: {e}")
        if os.path.exists(dest_path):
            os.remove(dest_path)
        if os.path.exists(extract_path) and os.path.isdir(extract_path):
            shutil.rmtree(extract_path)

def uninstall_package(input_name):
    name = input_name.lower()
    found = False
    items_to_check = [name, f"{name}.py"]

    for item in set(items_to_check):
        path = os.path.join(PROGRAMS_DIR, item)
        if os.path.exists(path):
            try:
                if os.path.isdir(path):
                    print(f"Removing package directory: '{path}'")
                    shutil.rmtree(path)
                else:
                    print(f"Removing package file: '{path}'")
                    os.remove(path)
                print(f"Uninstalled '{item}'")
                found = True
                break
            except OSError as e:
                print(f"Failed to remove '{path}': {e}")
        else:
            print(f"'{path}' does not exist, skipping.")

    if not found:
        print(f"Package '{input_name}' not found in installed programs.")

def print_help():
    print("""SPT Help:
  SPT Help                Show this help message
  SPT Install <name/url>  Install package by name from repo or direct URL
  SPT Uninstall <name>    Uninstall a locally installed package
""")

def main():
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1].lower()

    if command == "help":
        print_help()
    elif command == "install":
        if len(sys.argv) == 3:
            install_package(sys.argv[2])
        else:
            print("[ERROR] Usage: SPT Install <name/url>")
            print_help()
    elif command == "uninstall":
        if len(sys.argv) == 3:
            uninstall_package(sys.argv[2])
        else:
            print("[ERROR] Usage: SPT Uninstall <name>")
            print_help()
    else:
        print(f"[ERROR] Unknown command: '{sys.argv[1]}'")
        print_help()

if __name__ == "__main__":
    main()