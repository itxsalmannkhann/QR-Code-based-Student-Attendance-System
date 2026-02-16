# 🎓 Student Attendance System using QR Codes

A complete Python-based attendance management system using QR codes and real-time webcam scanning.

## 📋 Table of Contents

- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Usage Guide](#usage-guide)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)
- [Technical Documentation](#technical-documentation)

---

## ✨ Features

### Core Features
- ✅ **Unique QR Code Generation** - Generate individual QR codes for each student
- ✅ **Real-time Scanning** - Webcam-based QR code detection and decoding
- ✅ **Duplicate Prevention** - Automatically prevents multiple attendance entries per day
- ✅ **CSV Logging** - Attendance records saved in CSV format
- ✅ **Visual Feedback** - On-screen confirmation when attendance is marked
- ✅ **Error Handling** - Robust error checking and user-friendly messages

### Advanced Features
- 📊 **Report Generation** - Daily, class-wise, and custom date reports
- 📈 **Excel Export** - Export reports to Excel format
- 🖥️ **GUI Interface** - User-friendly graphical interface
- 📅 **Date-based Filtering** - View attendance for specific dates
- 📉 **Attendance Statistics** - Percentage calculations and analytics
- 🎯 **Absentee Tracking** - Automatic identification of absent students

---

## 🖥️ System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Webcam**: Required for attendance scanning
- **Dependencies**: See `requirements.txt`

---

## 📦 Installation

### Step 1: Clone or Download the Project

```bash
# Download the project
cd student_attendance
```

### Step 2: Install Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt
```

**Required packages:**
```
qrcode[pil]==7.4.2
opencv-python==4.9.0.80
pyzbar==0.1.9
pandas==2.2.0
Pillow==10.2.0
openpyxl==3.1.2  # For Excel export
```

### Step 3: Install Additional System Dependencies

**For pyzbar (QR code decoding):**

**Windows:**
```bash
# pyzbar should work out of the box
# If issues occur, install Visual C++ Redistributable
```

**macOS:**
```bash
brew install zbar
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install libzbar0
```

---

## 🚀 Quick Start

### 1. Prepare Student Data

Create or edit `students.csv` with your student information:

```csv
StudentID,Name,Class
101,Salman Khan,BCS AI
103,Ihsan Ullah Mohmand,BCS AI
```

### 2. Generate QR Codes

```bash
python generate_qr.py
```

This will:
- Read student data from `students.csv`
- Generate unique QR codes for each student
- Save QR images in `qr_codes/` folder
- Display progress and summary

### 3. Start Attendance Scanner

```bash
python scanner.py
```

Controls:
- Point webcam at student QR code
- Press **'q'** to quit
- Press **'r'** to reload today's attendance

### 4. View Reports

```bash
# Daily report for today
python report_generator.py

# Report for specific date
python report_generator.py --date 2024-02-16

# Class-wise report
python report_generator.py --class-wise

# Export to Excel
python report_generator.py --export excel
```

### 5. Use GUI (Optional)

```bash
python gui.py
```

---

## 📁 Project Structure

```
student_attendance/
│
├── generate_qr.py          # QR code generator
├── scanner.py               # Real-time attendance scanner
├── report_generator.py      # Report generation and analysis
├── gui.py                   # Graphical user interface
├── requirements.txt         # Python dependencies
├── README.md               # This file
│
├── students.csv            # Student database (input)
├── attendance.csv          # Attendance records (auto-created)
│
└── qr_codes/               # Generated QR codes (auto-created)
    ├── 101_Salman_Khan.png
    ├── 102_Ihsan_ullah_Mohmand.png
    └── ...
```

---

## 🔍 How It Works

### 1. QR Code Generation

**What happens:**
1. System reads student data from CSV
2. For each student, creates data string: `StudentID|Name|Class`
3. Encodes data into QR code matrix
4. Applies error correction (Reed-Solomon algorithm)
5. Saves as PNG image

**Why High Error Correction (Level H)?**
- Allows up to 30% of QR code to be damaged/covered
- Ensures reliable scanning even with:
  - Poor lighting conditions
  - Damaged or creased paper
  - Partially obscured codes
  - Low-quality cameras

**QR Code Structure:**
```
┌─────────────────────────┐
│ ▓▓▓▓▓▓▓     ▓▓▓▓▓▓▓     │  ← Finder patterns (3 corners)
│ ▓     ▓     ▓     ▓     │
│ ▓ ▓▓▓ ▓     ▓ ▓▓▓ ▓     │
│ ▓ ▓▓▓ ▓     ▓ ▓▓▓ ▓     │
│ ▓     ▓     ▓     ▓     │
│ ▓▓▓▓▓▓▓     ▓▓▓▓▓▓▓     │
│                         │
│   [Student Data Area]   │  ← Encoded information
│   101|Salman Khan|BCS   │
│                         │
│ ▓▓▓▓▓▓▓                 │
│ ▓     ▓                 │  ← Alignment pattern
│ ▓ ▓▓▓ ▓                 │
└─────────────────────────┘
```

### 2. QR Code Scanning Process

**How pyzbar Decodes QR Codes:**

```
Camera Frame → Image Processing → Pattern Detection → Data Extraction
      ↓              ↓                    ↓                  ↓
   640x480px    Grayscale        Find corners         Decode bits
   RGB Image    Conversion     & orientation        → "101|John|10A"
```

**Step-by-step:**

1. **Frame Capture**: OpenCV captures frames at ~30 FPS
   ```python
   ret, frame = camera.read()  # Returns 640x480x3 numpy array
   ```

2. **QR Detection**: pyzbar scans for QR patterns
   - Locates finder patterns (3 corners)
   - Determines orientation and size
   - Identifies data modules

3. **Data Decoding**: 
   - Reads binary data from modules
   - Applies error correction
   - Converts to text string

4. **Validation**: System checks format
   ```python
   data = "101|John Doe|10A"
   parts = data.split('|')
   # Validates: len(parts) == 3 and all parts non-empty
   ```

### 3. Duplicate Prevention

**Why is this important?**
- Prevents accidental double-scanning
- Ensures accurate attendance counts
- Eliminates fraudulent multiple entries
- Maintains data integrity

**How it works:**

```python
# At system startup
today_attendance = {101, 102, 105}  # Already marked today

# When QR is scanned
if student_id in today_attendance:
    return "Already Marked!"
else:
    mark_attendance(student)
    today_attendance.add(student_id)
```

**Implementation:**
1. **On startup**: Load all today's attendance into memory (Set data structure)
2. **On scan**: Check if StudentID exists in set (O(1) time complexity)
3. **On success**: Add StudentID to set and CSV file
4. **Result**: Fast duplicate checking without repeated file reads

### 4. Real-Time Detection Loop

```
┌─────────────────────────────────────┐
│  while True:                        │
│    1. Capture frame from webcam     │
│    2. Detect QR codes in frame      │
│    3. Decode QR data                │
│    4. Parse student information     │
│    5. Check for duplicates          │
│    6. Mark attendance if valid      │
│    7. Draw visual feedback          │
│    8. Display frame                 │
│    9. Check for user input (q/r)    │
│   10. Repeat (~30 times per second) │
└─────────────────────────────────────┘
```

**Performance Optimization:**
- **Cooldown timer**: 3-second delay prevents rapid re-scanning
- **In-memory checking**: Fast duplicate detection
- **Single pass processing**: Efficient frame processing

---

## 📖 Usage Guide

### Generating QR Codes

**Basic usage:**
```bash
python generate_qr.py
```

**Expected output:**
```
============================================================
Generating QR Codes for 10 students...
============================================================

[1/10] ✓ Generated: John Doe (101)
           → qr_codes/101_John_Doe.png
[2/10] ✓ Generated: Jane Smith (102)
           → qr_codes/102_Jane_Smith.png
...

============================================================
Generation Complete!
============================================================
✓ Success: 10/10
📁 QR codes saved in: /path/to/qr_codes
============================================================
```

### Scanning Attendance

**Start scanner:**
```bash
python scanner.py
```

**On-screen feedback:**
- **Green**: Attendance marked successfully ✅
- **Orange**: Already marked today ⚠️
- **Red**: Invalid QR code or error ❌

**Example successful scan:**
```
✓ Attendance Marked:
   Student ID: 101
   Name: Salman Khan
   Class: BCS AI
   Time: 09:15:23
```

### Generating Reports

**Daily report:**
```bash
python report_generator.py
```

**Class-wise report:**
```bash
python report_generator.py --class-wise
```

**Export to Excel:**
```bash
python report_generator.py --export excel
# Creates: attendance_report_2024_02_16.xlsx
```

**Custom date:**
```bash
python report_generator.py --date 2024-02-15
```

---

## 🎯 Advanced Features

### 1. Excel Export

Generate professional Excel reports with multiple sheets:

```bash
python report_generator.py --export excel
```

**Excel file contains:**
- **Summary Sheet**: Overall statistics
- **Present Sheet**: List of present students
- **Absent Sheet**: List of absent students
- **Class-wise Sheet**: Class-level breakdown

### 2. GUI Interface

Launch the graphical interface for non-technical users:

```bash
python gui.py
```

**Features:**
- 📝 Generate QR codes
- 📷 Scan attendance (with live camera preview)
- 📊 View and export reports
- ⚙️ System settings

### 3. Sound Confirmation (Bonus)

Add audio feedback when attendance is marked:

```python
# Install pygame for sound
pip install pygame

# Add to scanner.py
import pygame
pygame.mixer.init()
success_sound = pygame.mixer.Sound('success.wav')

# Play on successful scan
success_sound.play()
```

### 4. Database Version (SQLite)

Convert from CSV to SQLite database:

```python
import sqlite3

# Create database
conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
    CREATE TABLE students (
        id INTEGER PRIMARY KEY,
        student_id TEXT UNIQUE,
        name TEXT,
        class TEXT
    )
''')

cursor.execute('''
    CREATE TABLE attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        date TEXT,
        time TEXT,
        FOREIGN KEY (student_id) REFERENCES students (student_id)
    )
''')
```

---

## 🔧 Troubleshooting

### Camera Not Detected

**Error:** `❌ Error: Could not open camera 0`

**Solutions:**
1. Check if camera is connected and working
2. Close other applications using the camera (Zoom, Skype, etc.)
3. Try different camera index:
   ```python
   camera = cv2.VideoCapture(1)  # Try 1, 2, etc.
   ```
4. On Linux, check permissions:
   ```bash
   sudo chmod 666 /dev/video0
   ```

### QR Code Not Scanning

**Solutions:**
1. **Better lighting**: Ensure good, even lighting
2. **Distance**: Hold QR code 6-12 inches from camera
3. **Steady hold**: Keep QR code steady for 1-2 seconds
4. **Print quality**: Use high-quality printer
5. **No glare**: Avoid reflective surfaces

### pyzbar Installation Issues

**Windows:**
```bash
pip install pyzbar
# If fails, download wheel from:
# https://pypi.org/project/pyzbar/#files
```

**macOS:**
```bash
brew install zbar
pip install pyzbar
```

**Linux:**
```bash
sudo apt-get install libzbar0
pip install pyzbar
```

### CSV File Errors

**Error:** `students.csv not found`

**Solution:** Create the file with correct format:
```csv
StudentID,Name,Class
101,Salman Khan,BCS AI
102,Ihsan Ullah Mohmand,BCS AI
```

**Important:**
- First row must be headers
- No empty rows
- All fields must be filled

---

## 📚 Technical Documentation

### QR Code Data Format

```
Format: StudentID|Name|Class
Example: 101|John Doe|10A
```

**Why use pipe delimiter (|)?**
- Rarely used in names (unlike comma, space)
- Easy to split programmatically
- Compatible with all QR readers
- No escaping needed

### CSV File Formats

**students.csv:**
```csv
StudentID,Name,Class
101,Salman Khan,BCS AI
```

**attendance.csv (auto-created):**
```csv
StudentID,Name,Class,Date,Time
101,Salman Khan,BCS ,2024-02-16,09:15:23
```

### Error Correction Levels

| Level | Recovery Capability | Use Case |
|-------|-------------------|----------|
| L     | ~7%               | Clean environments |
| M     | ~15%              | Standard use |
| Q     | ~25%              | Moderate damage |
| **H** | **~30%**          | **Best for scanning** |

**Why we use Level H:**
- Maximum reliability
- Works with damaged codes
- Compensates for poor lighting
- Handles partial obstruction

### Camera Resolution Settings

```python
# Recommended settings
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
camera.set(cv2.CAP_PROP_FPS, 30)
```

**Balance between:**
- **Higher resolution**: Better QR detection
- **Lower resolution**: Faster processing
- **Sweet spot**: 720p @ 30 FPS

---

## 🎓 Educational Concepts

### How QR Codes Work

1. **Data Encoding**: Text → Binary → Matrix
2. **Error Correction**: Reed-Solomon algorithm adds redundancy
3. **Pattern Placement**: Finder, alignment, timing patterns
4. **Version Selection**: Size based on data amount (1-40)

### Reed-Solomon Error Correction

```
Original Data:    [1, 0, 1, 1, 0]
Error Correction: [1, 1, 0]  ← Generated codes
Final Code:       [1, 0, 1, 1, 0, 1, 1, 0]

If damaged:       [1, 0, X, 1, 0, 1, 1, 0]
                          ↑ Error
Recovered:        [1, 0, 1, 1, 0, 1, 1, 0]
                          ↑ Fixed!
```

### OpenCV Frame Processing

```python
# Frame is a NumPy array
frame.shape  # (720, 1280, 3) = Height × Width × Channels
frame.dtype  # uint8 (0-255)

# Each pixel: [Blue, Green, Red]
pixel = frame[360, 640]  # Center pixel
# pixel = [128, 200, 255]  # B, G, R values
```

---

## 📝 Best Practices

### For Administrators

1. **Backup**: Regularly backup `attendance.csv`
2. **Print Quality**: Use high-quality printer for QR codes
3. **Lamination**: Laminate QR codes for durability
4. **Testing**: Test system before first use
5. **Training**: Train students on proper scanning technique

### For Developers

1. **Error Handling**: Always validate input data
2. **Logging**: Log errors for debugging
3. **Testing**: Test with various QR code qualities
4. **Performance**: Profile code for bottlenecks
5. **Documentation**: Keep code comments updated

---

## 🚀 Future Enhancements

- [ ] Mobile app version (Android/iOS)
- [ ] Cloud database integration
- [ ] SMS/Email notifications to parents
- [ ] Facial recognition as backup
- [ ] Multi-camera support
- [ ] Analytics dashboard
- [ ] Integration with school management system

---

## 📄 License

MIT License - Feel free to use and modify for your institution!

---

## 🤝 Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

---

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review error messages carefully
3. Ensure all dependencies are installed
4. Verify camera and file permissions

---

**Made with ❤️ for Educational Institutions By Salman Khan**
