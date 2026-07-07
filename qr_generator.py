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