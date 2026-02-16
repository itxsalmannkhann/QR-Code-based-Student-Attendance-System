"""
Abdul Wali Khan University Mardan Student Attendance System - GUI Version
========================================
User-friendly graphical interface for attendance management.

Features:
- Generate QR codes
- Scan attendance
- View reports
- Export data

"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import cv2
from PIL import Image, ImageTk
from datetime import datetime
import os

# Import our modules
from generate_qr import read_students_csv, generate_all_qr_codes
from scanner import AttendanceSystem, QRScanner
from report_generator import ReportGenerator


class AttendanceGUI:

    
    def __init__(self, root):
        self.root = root
        self.root.title("Student Attendance System")
        self.root.geometry("900x650")  # Reduced height
        self.root.minsize(800, 500)  # Set minimum size
        
        # System components
        self.attendance_system = AttendanceSystem()
        self.report_generator = ReportGenerator()
        self.scanner = None
        self.scanning = False
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Create and layout all UI elements."""
        
        # Title
        title_frame = tk.Frame(self.root, bg="#5F0A0A", height=60)  # Reduced from 80
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="Awkum Student Attendance System",
            font=("Helvetica", 20, "bold"),  # Reduced from 24
            bg="#5F0A0A",
            fg="white"
        )
        title_label.pack(pady=15)  # Reduced from 20
        
        # Main container
        main_container = ttk.Frame(self.root, padding=20)
        main_container.pack(fill="both", expand=True)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)
        
        # Tab 1: QR Generation
        self.create_qr_generation_tab()
        
        # Tab 2: Scanner
        self.create_scanner_tab()
        
        # Tab 3: Reports
        self.create_reports_tab()
        
        # Tab 4: Settings
        self.create_settings_tab()
    
    def create_qr_generation_tab(self):
        """Create QR code generation tab."""
        qr_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(qr_frame, text="Generate QR Codes")
        
        # Instructions
        instructions = tk.Text(qr_frame, height=8, wrap="word", font=("Helvetica", 10))
        instructions.pack(fill="x", pady=10)
        instructions.insert("1.0", """
How to Generate QR Codes:

1. Make sure 'students.csv' exists with format: StudentID,Name,Class
2. Click 'Generate QR Codes' button below
3. QR codes will be saved in 'qr_codes/' folder
4. Print and distribute QR codes to students

Example students.csv:
101,John Doe,10A
102,Jane Smith,10A
        """)
        instructions.config(state="disabled")
        
        # Status
        self.qr_status_label = tk.Label(
            qr_frame,
            text="Ready to generate QR codes",
            font=("Helvetica", 11),
            fg="gray"
        )
        self.qr_status_label.pack(pady=10)
        
        # Buttons
        button_frame = ttk.Frame(qr_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(
            button_frame,
            text="Open students.csv",
            command=self.open_students_csv
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Generate QR Codes",
            command=self.generate_qr_codes
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Open QR Folder",
            command=self.open_qr_folder
        ).pack(side="left", padx=5)
    
    def create_scanner_tab(self):
        """Create attendance scanner tab."""
        scanner_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(scanner_frame, text="📷 Scan Attendance")
        
        # Camera preview (reduced size)
        self.camera_label = tk.Label(
            scanner_frame,
            text="Camera feed will appear here",
            bg="black",
            fg="white",
            font=("Helvetica", 12),
            width=70,
            height=15  # Reduced from 20
        )
        self.camera_label.pack(pady=5)
        
        # Status
        self.scan_status_label = tk.Label(
            scanner_frame,
            text="Click 'Start Scanner' to begin",
            font=("Helvetica", 11, "bold"),
            fg="blue"
        )
        self.scan_status_label.pack(pady=5)
        
        # Recent scans (reduced size)
        recent_frame = ttk.LabelFrame(scanner_frame, text="Recent Scans", padding=10)
        recent_frame.pack(fill="both", expand=True, pady=5)
        
        self.recent_scans_text = tk.Text(recent_frame, height=4, font=("Courier", 9))  # Reduced height
        self.recent_scans_text.pack(fill="both", expand=True)
        
        # Control buttons
        button_frame = ttk.Frame(scanner_frame)
        button_frame.pack(pady=10)
        
        self.start_scan_btn = ttk.Button(
            button_frame,
            text="▶️ Start Scanner",
            command=self.start_scanner
        )
        self.start_scan_btn.pack(side="left", padx=5)
        
        self.stop_scan_btn = ttk.Button(
            button_frame,
            text="⏹️ Stop Scanner",
            command=self.stop_scanner,
            state="disabled"
        )
        self.stop_scan_btn.pack(side="left", padx=5)
    
    def create_reports_tab(self):
        """Create reports tab."""
        reports_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(reports_frame, text="Reports")
        
        # Date selection
        date_frame = ttk.LabelFrame(reports_frame, text="Select Date", padding=10)
        date_frame.pack(fill="x", pady=10)
        
        ttk.Label(date_frame, text="Date (YYYY-MM-DD):").pack(side="left", padx=5)
        
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(date_frame, textvariable=self.date_var, width=20).pack(side="left", padx=5)
        
        ttk.Button(
            date_frame,
            text="Today",
            command=lambda: self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        ).pack(side="left", padx=5)
        
        # Report display
        report_display_frame = ttk.LabelFrame(reports_frame, text="Report", padding=10)
        report_display_frame.pack(fill="both", expand=True, pady=10)
        
        self.report_text = tk.Text(
            report_display_frame,
            font=("Courier", 10),
            wrap="none"
        )
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(report_display_frame, orient="vertical", command=self.report_text.yview)
        h_scroll = ttk.Scrollbar(report_display_frame, orient="horizontal", command=self.report_text.xview)
        self.report_text.config(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.report_text.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        report_display_frame.grid_rowconfigure(0, weight=1)
        report_display_frame.grid_columnconfigure(0, weight=1)
        
        # Report buttons
        button_frame = ttk.Frame(reports_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(
            button_frame,
            text="Daily Report",
            command=self.show_daily_report
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Class-wise Report",
            command=self.show_classwise_report
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Export to Excel",
            command=self.export_report
        ).pack(side="left", padx=5)
    
    def create_settings_tab(self):
        """Create settings tab."""
        settings_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(settings_frame, text="Settings")
        
        # File locations
        files_frame = ttk.LabelFrame(settings_frame, text="File Locations", padding=10)
        files_frame.pack(fill="x", pady=10)
        
        ttk.Label(files_frame, text="Students CSV:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Label(files_frame, text="students.csv").grid(row=0, column=1, sticky="w", padx=10)
        
        ttk.Label(files_frame, text="Attendance CSV:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Label(files_frame, text="attendance.csv").grid(row=1, column=1, sticky="w", padx=10)
        
        ttk.Label(files_frame, text="QR Codes Folder:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Label(files_frame, text="qr_codes/").grid(row=2, column=1, sticky="w", padx=10)
        
        # System info
        info_frame = ttk.LabelFrame(settings_frame, text="System Information", padding=10)
        info_frame.pack(fill="x", pady=10)
        
        # Count records
        student_count = len(self.report_generator.students_df) if self.report_generator.students_df is not None else 0
        attendance_count = len(self.report_generator.attendance_df) if self.report_generator.attendance_df is not None else 0
        
        ttk.Label(info_frame, text=f"Total Students: {student_count}").pack(anchor="w", pady=5)
        ttk.Label(info_frame, text=f"Total Attendance Records: {attendance_count}").pack(anchor="w", pady=5)
    
    # Action methods
    
    def open_students_csv(self):
        """Open students.csv in default editor."""
        if os.path.exists("students.csv"):
            os.system("students.csv" if os.name == 'nt' else "open students.csv")
        else:
            messagebox.showwarning("File Not Found", "students.csv not found!")
    
    def generate_qr_codes(self):
        """Generate QR codes for all students."""
        try:
            self.qr_status_label.config(text="Generating QR codes...", fg="blue")
            self.root.update()
            
            students = read_students_csv("students.csv")
            count = generate_all_qr_codes(students)
            
            self.qr_status_label.config(
                text=f"✓ Generated {count} QR codes successfully!",
                fg="green"
            )
            
            messagebox.showinfo(
                "Success",
                f"Generated {count} QR codes!\n\nCheck 'qr_codes/' folder."
            )
        
        except Exception as e:
            self.qr_status_label.config(text=f"Error: {str(e)}", fg="red")
            messagebox.showerror("Error", f"Failed to generate QR codes:\n{str(e)}")
    
    def open_qr_folder(self):
        """Open QR codes folder."""
        if os.path.exists("qr_codes"):
            os.system("qr_codes" if os.name == 'nt' else "open qr_codes")
        else:
            messagebox.showwarning("Folder Not Found", "qr_codes folder not found!")
    
    def start_scanner(self):
        """Start the QR scanner in a separate thread."""
        if self.scanning:
            return
        
        self.scanning = True
        self.start_scan_btn.config(state="disabled")
        self.stop_scan_btn.config(state="normal")
        self.scan_status_label.config(text="🔄 Starting camera...", fg="blue")
        
        # Start scanner thread
        scan_thread = threading.Thread(target=self.run_scanner, daemon=True)
        scan_thread.start()
    
    def run_scanner(self):
        """Run scanner loop (in separate thread)."""
        try:
            camera = cv2.VideoCapture(0)
            
            if not camera.isOpened():
                self.scan_status_label.config(text="❌ Camera not found!", fg="red")
                self.scanning = False
                return
            
            self.scan_status_label.config(text="✓ Scanner running - show QR code", fg="green")
            
            while self.scanning:
                ret, frame = camera.read()
                if not ret:
                    break
                
                # Process frame (simplified for GUI)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Resize for display
                height, width = frame_rgb.shape[:2]
                max_width = 700
                if width > max_width:
                    ratio = max_width / width
                    frame_rgb = cv2.resize(frame_rgb, (int(width * ratio), int(height * ratio)))
                
                # Convert to PhotoImage
                image = Image.fromarray(frame_rgb)
                photo = ImageTk.PhotoImage(image)
                
                # Update GUI
                self.camera_label.config(image=photo)
                self.camera_label.image = photo
                
                # Small delay
                self.root.update()
                
            camera.release()
            self.scan_status_label.config(text="Scanner stopped", fg="gray")
        
        except Exception as e:
            self.scan_status_label.config(text=f"Error: {str(e)}", fg="red")
        
        finally:
            self.scanning = False
            self.start_scan_btn.config(state="normal")
            self.stop_scan_btn.config(state="disabled")
    
    def stop_scanner(self):
        """Stop the scanner."""
        self.scanning = False
        self.scan_status_label.config(text="Stopping scanner...", fg="blue")
    
    def show_daily_report(self):
        """Display daily attendance report."""
        try:
            date_str = self.date_var.get()
            report = self.report_generator.get_daily_report(date_str)
            
            # Format report
            output = f"DAILY ATTENDANCE REPORT - {report['date']}\n"
            output += "="*70 + "\n\n"
            output += f"Total Students: {report['total']}\n"
            output += f"Present: {report['present']} ({report['percentage']}%)\n"
            output += f"Absent: {report['absent']} ({100 - report['percentage']:.2f}%)\n\n"
            
            output += f"Present Students ({len(report['present_students'])}):\n"
            output += "-"*70 + "\n"
            for s in report['present_students']:
                output += f"{s['StudentID']:<10} {s['Name']:<25} {s['Class']:<10} {s['Time']}\n"
            
            if report['absent_students']:
                output += f"\nAbsent Students ({len(report['absent_students'])}):\n"
                output += "-"*70 + "\n"
                for s in report['absent_students']:
                    output += f"{s['StudentID']:<10} {s['Name']:<25} {s['Class']}\n"
            
            self.report_text.delete("1.0", "end")
            self.report_text.insert("1.0", output)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report:\n{str(e)}")
    
    def show_classwise_report(self):
        """Display class-wise report."""
        try:
            date_str = self.date_var.get()
            class_stats = self.report_generator.get_class_wise_report(date_str)
            
            output = f"CLASS-WISE ATTENDANCE REPORT - {date_str}\n"
            output += "="*70 + "\n\n"
            output += f"{'Class':<10} {'Total':<10} {'Present':<10} {'Absent':<10} {'Percentage'}\n"
            output += "-"*70 + "\n"
            
            for class_name, stats in sorted(class_stats.items()):
                output += f"{class_name:<10} {stats['total']:<10} {stats['present']:<10} {stats['absent']:<10} {stats['percentage']}%\n"
            
            self.report_text.delete("1.0", "end")
            self.report_text.insert("1.0", output)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report:\n{str(e)}")
    
    def export_report(self):
        """Export report to Excel."""
        try:
            date_str = self.date_var.get()
            filename = f"attendance_report_{date_str.replace('-', '_')}.xlsx"
            
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=filename
            )
            
            if filepath:
                self.report_generator.export_to_excel(filepath, date_str)
                messagebox.showinfo("Success", f"Report exported to:\n{filepath}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export:\n{str(e)}")


def main():
    """Launch the GUI application."""
    root = tk.Tk()
    app = AttendanceGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
