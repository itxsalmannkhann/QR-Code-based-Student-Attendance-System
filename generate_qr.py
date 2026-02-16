"""
Student QR Code Generator
==========================
Generates unique QR codes for each student from students.csv file.

QR Data Format: StudentID|Name|Class
Filename Format: {StudentID}_{Name}.png

Author: Student Attendance System
License: MIT
"""

import qrcode
import csv
import os
from pathlib import Path


def read_students_csv(csv_file="students.csv"):
    """
    Read student data from CSV file.
    
    Args:
        csv_file (str): Path to students CSV file
    
    Returns:
        list: List of dictionaries containing student data
    
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV is empty or malformed
    """
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Students CSV file not found: {csv_file}")
    
    students = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Validate headers
            required_headers = ['StudentID', 'Name', 'Class']
            if not all(header in reader.fieldnames for header in required_headers):
                raise ValueError(f"CSV must contain headers: {', '.join(required_headers)}")
            
            for row in reader:
                # Validate row data
                if not all(row.get(key, '').strip() for key in required_headers):
                    print(f"⚠️  Skipping incomplete row: {row}")
                    continue
                
                students.append({
                    'StudentID': row['StudentID'].strip(),
                    'Name': row['Name'].strip(),
                    'Class': row['Class'].strip()
                })
        
        if not students:
            raise ValueError("No valid student records found in CSV")
        
        return students
    
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")


def generate_qr_code(data, filename, output_dir="qr_codes"):
    """
    Generate a QR code with high error correction.
    
    Args:
        data (str): Data to encode in QR code
        filename (str): Output filename (without extension)
        output_dir (str): Directory to save QR codes
    
    Returns:
        str: Path to saved QR code image
    
    How QR Code Generation Works:
    1. Data is converted to binary format
    2. Error correction codes are added (Reed-Solomon)
    3. Data is arranged in a 2D matrix pattern
    4. Finder patterns (corners) help scanners locate the code
    5. Version and format information is embedded
    
    Error Correction Levels:
    - L (Low): 7% recovery capability
    - M (Medium): 15% recovery capability
    - Q (Quartile): 25% recovery capability
    - H (High): 30% recovery capability - BEST for scanning reliability
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Configure QR code with optimal settings for scanning
    qr = qrcode.QRCode(
        version=1,  # Auto-size (1 = smallest, 40 = largest)
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Highest reliability
        box_size=10,  # Size of each module (pixel)
        border=4,  # Minimum border (QR spec requires 4)
    )
    
    # Add data and optimize size
    qr.add_data(data)
    qr.make(fit=True)
    
    # Generate image with high contrast for better scanning
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Construct output path
    output_path = os.path.join(output_dir, f"{filename}.png")
    
    # Save QR code
    qr_image.save(output_path)
    
    return output_path


def format_qr_data(student):
    """
    Format student data for QR code encoding.
    
    Format: StudentID|Name|Class
    Example: 101|John Doe|10A
    
    Args:
        student (dict): Student information
    
    Returns:
        str: Formatted data string for QR encoding
    """
    return f"{student['StudentID']}|{student['Name']}|{student['Class']}"


def format_filename(student):
    """
    Generate filename for student QR code.
    
    Format: {StudentID}_{Name}
    Example: 101_John_Doe
    
    Args:
        student (dict): Student information
    
    Returns:
        str: Formatted filename (without extension)
    """
    # Replace spaces with underscores and remove special characters
    safe_name = student['Name'].replace(' ', '_')
    safe_name = ''.join(c for c in safe_name if c.isalnum() or c == '_')
    
    return f"{student['StudentID']}_{safe_name}"


def generate_all_qr_codes(students, output_dir="qr_codes"):
    """
    Generate QR codes for all students.
    
    Args:
        students (list): List of student dictionaries
        output_dir (str): Directory to save QR codes
    
    Returns:
        int: Number of QR codes successfully generated
    """
    success_count = 0
    failed_students = []
    
    print(f"\n{'='*60}")
    print(f"Generating QR Codes for {len(students)} students...")
    print(f"{'='*60}\n")
    
    for i, student in enumerate(students, 1):
        try:
            # Format data and filename
            qr_data = format_qr_data(student)
            filename = format_filename(student)
            
            # Generate QR code
            output_path = generate_qr_code(qr_data, filename, output_dir)
            
            # Success message
            print(f"[{i}/{len(students)}] ✓ Generated: {student['Name']} ({student['StudentID']})")
            print(f"           → {output_path}")
            
            success_count += 1
            
        except Exception as e:
            print(f"[{i}/{len(students)}] ✗ Failed: {student['Name']} - {e}")
            failed_students.append(student['Name'])
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Generation Complete!")
    print(f"{'='*60}")
    print(f"✓ Success: {success_count}/{len(students)}")
    
    if failed_students:
        print(f"✗ Failed: {len(failed_students)}")
        print(f"  Students: {', '.join(failed_students)}")
    
    print(f"📁 QR codes saved in: {os.path.abspath(output_dir)}")
    print(f"{'='*60}\n")
    
    return success_count


def main():
    """
    Main function to generate QR codes for all students.
    """
    try:
        # Read student data from CSV
        print("📖 Reading students.csv...")
        students = read_students_csv("students.csv")
        print(f"✓ Found {len(students)} students")
        
        # Generate QR codes
        generated = generate_all_qr_codes(students)
        
        if generated > 0:
            print("🎉 QR codes generated successfully!")
            print("\n💡 Next Step: Run 'python scanner.py' to start attendance scanning")
        else:
            print("❌ No QR codes were generated. Please check errors above.")
    
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure 'students.csv' exists in the current directory.")
        print("   Format: StudentID,Name,Class")
    
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Check that your CSV file has the correct format:")
        print("   - Headers: StudentID,Name,Class")
        print("   - All rows have complete data")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("   Please check your setup and try again.")


if __name__ == "__main__":
    main()
