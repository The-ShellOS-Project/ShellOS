def extract_zip(zip_path, output_folder):
    """Extract a zip archive to a specified folder."""
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(output_folder)
    print(f"Extracted '{zip_path}' to '{output_folder}'")

def main():
    parser = argparse.ArgumentParser(description="Zip compiler and extractor")
    parser.add_argument("mode", choices=["zip", "unzip"], help="Choose mode: 'zip' to compress, 'unzip' to extract")
    parser.add_argument("input", help="Input file or directory (for zip) or zip file (for unzip)")
    parser.add_argument("output", help="Output zip file (for zip) or extraction folder (for unzip)")
    
    args = parser.parse_args()
    
    if args.mode == "zip":
        zip_folder(args.input, args.output)
    elif args.mode == "unzip":
        extract_zip(args.input, args.output)

if __name__ == "__main__":
    main()
