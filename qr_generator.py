import qrcode
import csv
import os
from pathlib import Path

def read_students_csv(csv_file = "./students_data/students.csv"):
    if not os.path.exists(csv_file):
        raise FileNotFoundError("Students CSV file not found: {}".format(csv_file))
    
    students = []

    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            required_headers = ['StudentID', 'Name', 'Class']
            if not all(header in reader.fieldnames for header in required_headers):
                raise ValueError("CSV must contain headers: {}".format(', '.join(required_headers)))
            
            for row in reader:

                if not all(row.get(key, '').strip() for key in required_headers):
                    print("⚠ Skipping incomplete row: {}".format(row))
                    continue

                students.append({
                    'StudentID': row['StudentID'].stip(),
                    'Name': row['Name'].strip(),
                    'Class': row['Class'].strip()
                })

        if not students:
            raise ValueError('No valid students record found in CSV')
        
        return students
    
    except Exception as e:
        raise ValueError('Error Reading CSV file: '.format(e))
    
    
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