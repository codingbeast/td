import base64
import json
import sys
import argparse

def encode_file_to_base64(file_path):
    """Encode a file to Base64"""
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
        return base64.b64encode(file_content).decode('utf-8')
    except Exception as e:
        print(f"Error encoding file: {e}")
        return None

def validate_json(file_path):
    """Validate the JSON file"""
    try:
        with open(file_path) as f:
            json.load(f)
        return True
    except ValueError as e:
        print(f"Invalid JSON file: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Encode Google Service Account JSON to Base64 for GitHub Secrets')
    parser.add_argument('file', help='Path to service account JSON file')
    parser.add_argument('--validate', action='store_true', help='Validate JSON before encoding')
    args = parser.parse_args()

    if args.validate and not validate_json(args.file):
        sys.exit(1)

    encoded = encode_file_to_base64(args.file)
    if encoded:
        print("\nCopy the following output to your GitHub secret (GOOGLE_SERVICE_ACCOUNT):\n")
        print(encoded)
        print("\nImportant:")
        print("- Never commit your service account JSON file to version control")
        print("- Only use this encoded value in GitHub Secrets")
        print("- The encoded value contains newlines - copy ALL of it")

if __name__ == "__main__":
    main()