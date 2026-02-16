"""
Student Attendance Scanner
===========================
Real-time QR code scanner using webcam for attendance tracking.

Features:
- Real-time webcam QR detection
- Duplicate attendance prevention
- Automatic CSV logging
- Visual feedback on screen

Controls:
- Press 'q' to quit
- Press 'r' to reload attendance records

Author: Student Attendance System
License: MIT
"""

import cv2
from pyzbar import pyzbar
import csv
import os
from datetime import datetime
import pandas as pd


class AttendanceSystem:
    """
    Complete attendance system with QR scanning and logging.
    """
    
    def __init__(self, attendance_file="attendance.csv"):
        """
        Initialize the attendance system.
        
        Args:
            attendance_file (str): Path to attendance CSV file
        """
        self.attendance_file = attendance_file
        self.attendance_records = []
        self.today_attendance = set()  # Track today's attendance in memory
        
        # Initialize attendance file
        self._initialize_attendance_file()
        
        # Load today's attendance
        self._load_today_attendance()
    
    def _initialize_attendance_file(self):
        """
        Create attendance CSV file if it doesn't exist.
        
        CSV Format: StudentID,Name,Class,Date,Time
        """
        if not os.path.exists(self.attendance_file):
            with open(self.attendance_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['StudentID', 'Name', 'Class', 'Date', 'Time'])
            print(f"✓ Created new attendance file: {self.attendance_file}")
        else:
            print(f"✓ Using existing attendance file: {self.attendance_file}")
    
    def _load_today_attendance(self):
        """
        Load today's attendance records into memory for quick duplicate checking.
        
        Why this is important:
        - Prevents students from scanning multiple times
        - Faster than reading entire CSV for each scan
        - Memory-efficient (only today's records)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        try:
            if os.path.exists(self.attendance_file):
                df = pd.read_csv(self.attendance_file)
                
                # Filter today's records
                if not df.empty and 'Date' in df.columns:
                    today_records = df[df['Date'] == today]
                    self.today_attendance = set(today_records['StudentID'].astype(str).tolist())
                    
                    if self.today_attendance:
                        print(f"✓ Loaded {len(self.today_attendance)} attendance records for today")
                    else:
                        print(f"✓ No attendance records found for today")
        
        except Exception as e:
            print(f"⚠️  Warning: Could not load today's attendance: {e}")
            self.today_attendance = set()
    
    def parse_qr_data(self, qr_data):
        """
        Parse QR code data into student information.
        
        Expected Format: StudentID|Name|Class
        Example: 101|John Doe|10A
        
        Args:
            qr_data (str): Raw QR code data
        
        Returns:
            dict or None: Parsed student data or None if invalid
        """
        try:
            parts = qr_data.split('|')
            
            if len(parts) != 3:
                print(f"⚠️  Invalid QR format: {qr_data}")
                return None
            
            student = {
                'StudentID': parts[0].strip(),
                'Name': parts[1].strip(),
                'Class': parts[2].strip()
            }
            
            # Validate data
            if not all(student.values()):
                print(f"⚠️  Incomplete student data: {qr_data}")
                return None
            
            return student
        
        except Exception as e:
            print(f"⚠️  Error parsing QR data: {e}")
            return None
    
    def is_already_marked(self, student_id):
        """
        Check if student has already marked attendance today.
        
        Args:
            student_id (str): Student ID to check
        
        Returns:
            bool: True if already marked, False otherwise
        """
        return str(student_id) in self.today_attendance
    
    def mark_attendance(self, student):
        """
        Mark attendance for a student.
        
        Args:
            student (dict): Student information (StudentID, Name, Class)
        
        Returns:
            bool: True if marked successfully, False if already marked
        """
        student_id = str(student['StudentID'])
        
        # Check duplicate
        if self.is_already_marked(student_id):
            return False
        
        # Get current timestamp
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        # Append to CSV file
        try:
            with open(self.attendance_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    student['StudentID'],
                    student['Name'],
                    student['Class'],
                    date_str,
                    time_str
                ])
            
            # Add to today's attendance set
            self.today_attendance.add(student_id)
            
            return True
        
        except Exception as e:
            print(f"❌ Error writing to attendance file: {e}")
            return False


class QRScanner:
    """
    Real-time QR code scanner using webcam.
    """
    
    def __init__(self, attendance_system):
        """
        Initialize the QR scanner.
        
        Args:
            attendance_system (AttendanceSystem): Attendance system instance
        """
        self.attendance_system = attendance_system
        self.camera = None
        self.last_scanned = None  # Prevent rapid re-scanning
        self.scan_cooldown = 3  # seconds
        self.last_scan_time = 0
    
    def initialize_camera(self, camera_index=0):
        """
        Initialize webcam for video capture.
        
        Args:
            camera_index (int): Camera device index (0 = default)
        
        Returns:
            bool: True if successful, False otherwise
        
        How OpenCV Camera Capture Works:
        1. cv2.VideoCapture() opens connection to camera
        2. cap.read() captures frames continuously
        3. Frame is a NumPy array (height x width x 3 channels)
        4. We process each frame to detect QR codes
        5. Results are displayed in real-time window
        """
        self.camera = cv2.VideoCapture(camera_index)
        
        if not self.camera.isOpened():
            print(f"❌ Error: Could not open camera {camera_index}")
            print("\n💡 Troubleshooting:")
            print("   1. Check if camera is connected")
            print("   2. Close other apps using the camera")
            print("   3. Try a different camera index (1, 2, etc.)")
            return False
        
        # Set camera properties for better performance
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        print("✓ Camera initialized successfully")
        return True
    
    def detect_and_decode_qr(self, frame):
        """
        Detect and decode QR codes in a frame.
        
        Args:
            frame: OpenCV frame (NumPy array)
        
        Returns:
            list: List of detected QR codes with data and location
        
        How pyzbar QR Detection Works:
        1. Image is analyzed for QR patterns
        2. Finder patterns (3 corners) are located
        3. Alignment patterns help determine orientation
        4. Timing patterns define module size
        5. Data area is read and error-corrected
        6. Binary data is converted to text
        """
        # Decode QR codes in the frame
        decoded_objects = pyzbar.decode(frame)
        return decoded_objects
    
    def draw_qr_overlay(self, frame, decoded_obj, status_message, status_color):
        """
        Draw visual overlay on detected QR code.
        
        Args:
            frame: OpenCV frame
            decoded_obj: Detected QR code object
            status_message (str): Message to display
            status_color (tuple): BGR color for rectangle
        """
        # Get QR code bounding box coordinates
        points = decoded_obj.polygon
        
        # Draw rectangle around QR code
        if len(points) == 4:
            pts = [(point.x, point.y) for point in points]
            cv2.polylines(frame, [np.array(pts, dtype=np.int32)], True, status_color, 3)
        
        # Draw filled rectangle for text background
        rect_start = (decoded_obj.rect.left, decoded_obj.rect.top - 60)
        rect_end = (decoded_obj.rect.left + 400, decoded_obj.rect.top)
        cv2.rectangle(frame, rect_start, rect_end, status_color, -1)
        
        # Draw status message
        text_position = (decoded_obj.rect.left + 10, decoded_obj.rect.top - 15)
        cv2.putText(
            frame,
            status_message,
            text_position,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
    
    def process_qr_code(self, qr_data):
        """
        Process detected QR code and mark attendance.
        
        Args:
            qr_data (str): Decoded QR code data
        
        Returns:
            tuple: (success, message, color)
        """
        # Parse student data
        student = self.attendance_system.parse_qr_data(qr_data)
        
        if not student:
            return False, "Invalid QR Code", (0, 0, 255)  # Red
        
        # Check if already marked
        if self.attendance_system.is_already_marked(student['StudentID']):
            message = f"{student['Name']} - Already Marked Today!"
            return False, message, (0, 165, 255)  # Orange
        
        # Mark attendance
        success = self.attendance_system.mark_attendance(student)
        
        if success:
            message = f"{student['Name']} - Attendance Marked!"
            print(f"\n✓ Attendance Marked:")
            print(f"   Student ID: {student['StudentID']}")
            print(f"   Name: {student['Name']}")
            print(f"   Class: {student['Class']}")
            print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
            return True, message, (0, 255, 0)  # Green
        else:
            return False, "Error marking attendance", (0, 0, 255)  # Red
    
    def run(self):
        """
        Run the real-time QR scanner loop.
        
        The Real-Time Detection Loop:
        1. Capture frame from camera
        2. Decode QR codes in frame
        3. Process each detected QR
        4. Draw visual feedback
        5. Display frame
        6. Check for user input (quit, etc.)
        7. Repeat at ~30 FPS
        """
        if not self.initialize_camera():
            return
        
        print("\n" + "="*60)
        print("QR Code Attendance Scanner Running")
        print("="*60)
        print("📷 Point camera at student QR code")
        print("⌨️  Press 'q' to quit")
        print("⌨️  Press 'r' to reload today's attendance")
        print("="*60 + "\n")
        
        try:
            while True:
                # Capture frame from camera
                ret, frame = self.camera.read()
                
                if not ret:
                    print("❌ Error: Failed to capture frame")
                    break
                
                # Detect QR codes in frame
                decoded_objects = self.detect_and_decode_qr(frame)
                
                # Process each detected QR code
                for obj in decoded_objects:
                    qr_data = obj.data.decode('utf-8')
                    
                    # Prevent rapid re-scanning (cooldown)
                    current_time = datetime.now().timestamp()
                    if qr_data == self.last_scanned and (current_time - self.last_scan_time) < self.scan_cooldown:
                        continue
                    
                    # Process QR code
                    success, message, color = self.process_qr_code(qr_data)
                    
                    # Update scan tracking
                    self.last_scanned = qr_data
                    self.last_scan_time = current_time
                    
                    # Draw overlay
                    self.draw_qr_overlay(frame, obj, message, color)
                
                # Draw instructions on frame
                cv2.putText(
                    frame,
                    "Press 'q' to quit | Press 'r' to reload",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )
                
                # Display frame
                cv2.imshow('Student Attendance Scanner', frame)
                
                # Check for key press
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    print("\n👋 Quitting scanner...")
                    break
                elif key == ord('r'):
                    print("\n🔄 Reloading today's attendance...")
                    self.attendance_system._load_today_attendance()
        
        finally:
            # Clean up
            if self.camera:
                self.camera.release()
            cv2.destroyAllWindows()
            print("✓ Camera released")
            print("✓ Scanner closed\n")


import numpy as np  # Required for drawing


def main():
    """
    Main function to run the attendance scanner.
    """
    try:
        # Initialize attendance system
        print("🚀 Starting Student Attendance System...\n")
        attendance_system = AttendanceSystem()
        
        # Initialize and run scanner
        scanner = QRScanner(attendance_system)
        scanner.run()
        
        print("✓ Attendance system closed successfully")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("✓ System closed")
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print("   Please check your setup and try again")


if __name__ == "__main__":
    main()
