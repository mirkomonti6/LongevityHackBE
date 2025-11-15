"""
Script to convert an image or PDF file to base64 encoding.

Usage:
    python convert_to_base64.py <file_path>
    
Example:
    python convert_to_base64.py sample_lab_results.png
"""

import base64
import sys
import os
import json


def file_to_base64(file_path):
    """
    Convert a file to base64 encoding.
    
    Args:
        file_path: Path to the file to convert
        
    Returns:
        Base64 encoded string
    """
    with open(file_path, 'rb') as file:
        file_data = file.read()
        base64_encoded = base64.b64encode(file_data).decode('utf-8')
    return base64_encoded


def get_mime_type(file_path):
    """
    Determine the MIME type based on file extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        MIME type string
    """
    extension = os.path.splitext(file_path)[1].lower()
    mime_types = {
        '.pdf': 'application/pdf',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
    }
    return mime_types.get(extension, 'application/octet-stream')


def create_api_request(file_path, base64_string):
    """
    Create a sample API request with the base64 data.
    
    Args:
        file_path: Original file path
        base64_string: Base64 encoded file data
        
    Returns:
        Dictionary formatted as API request
    """
    filename = os.path.basename(file_path)
    mime_type = get_mime_type(file_path)
    
    api_request = {
        "age": 36,
        "sex": "male",
        "height_cm": 180,
        "weight_kg": 78,
        "sleep_hours_per_night": 7.5,
        "movement_days_per_week": 3,
        "work_activity_level": "moderate",
        "stress_level_1_to_10": 6,
        "lab_pdf": {
            "filename": filename,
            "mime_type": mime_type,
            "base64": base64_string
        }
    }
    
    return api_request


def main():
    """Main function to handle command line arguments and conversion."""
    if len(sys.argv) < 2:
        print("Error: No file path provided")
        print("\nUsage:")
        print("  python convert_to_base64.py <file_path>")
        print("\nExample:")
        print("  python convert_to_base64.py sample_lab_results.png")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    print(f"Converting file: {file_path}")
    print(f"File size: {os.path.getsize(file_path)} bytes")
    
    # Convert to base64
    try:
        base64_string = file_to_base64(file_path)
        print(f"Base64 length: {len(base64_string)} characters")
        print()
        
        # Get mime type
        mime_type = get_mime_type(file_path)
        filename = os.path.basename(file_path)
        
        print("=" * 70)
        print("FILE INFORMATION")
        print("=" * 70)
        print(f"Filename: {filename}")
        print(f"MIME Type: {mime_type}")
        print(f"Base64 String (first 100 chars): {base64_string[:100]}...")
        print()
        
        # Save to output file
        output_file = "base64_output.txt"
        with open(output_file, 'w') as f:
            f.write(base64_string)
        print(f"✓ Full base64 string saved to: {output_file}")
        
        # Create and save sample API request
        api_request = create_api_request(file_path, base64_string)
        api_request_file = "api_request_sample.json"
        
        # For display purposes, truncate the base64 in the JSON
        display_request = api_request.copy()
        display_request["lab_pdf"]["base64"] = base64_string[:50] + "..."
        
        with open(api_request_file, 'w') as f:
            # Save with full base64
            json.dump(api_request, f, indent=2)
        
        print(f"✓ Sample API request saved to: {api_request_file}")
        print()
        
        print("=" * 70)
        print("SAMPLE API REQUEST FORMAT (base64 truncated for display)")
        print("=" * 70)
        print(json.dumps(display_request, indent=2))
        print()
        
        print("=" * 70)
        print("USAGE WITH CURL")
        print("=" * 70)
        print(f"curl -X POST http://localhost:8000/execute \\")
        print(f"  -H 'Content-Type: application/json' \\")
        print(f"  -d @{api_request_file}")
        print()
        
    except Exception as e:
        print(f"Error converting file: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

