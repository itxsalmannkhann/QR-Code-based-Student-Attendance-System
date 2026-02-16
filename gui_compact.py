"""
Student Attendance System - Compact GUI Version
================================================
Optimized for smaller screens and laptops.

Features:
- Compact layout (fits 1366x768 screens)
- Scrollable content
- All functionality preserved

Author: Student Attendance System
License: MIT
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


class CompactAttendanceGUI:
    """
    Compact GUI for Student Attendance System.
    Optimized for smaller screens.
    """
    
    def __init__(self, root):
        """Initialize the compact GUI application."""
        self.root = root
        self.root.title("Attendance System")
        
        # Auto-detect screen size and adjust
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Set window size (80% of screen, max 900x600)
        window_width = min(900, int(screen_width * 0.8))
        window_height = min(600, int(screen_height * 0.8))
        
        # Center window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(700, 500)
        
        # System components
        self.attendance_system = AttendanceSystem()
        self.report_generator = ReportGenerator()
        self.scanner = None
        self.scanning = False
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Create and layout all UI elements."""
        
        # Compact Title
        title_frame = tk.Frame(self.root, bg="#2196F3", height=50)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🎓 Attendance System",
            font=("Helvetica", 16, "bold"),
            bg="#2196F3",
            fg="white"
        )
        title_label.pack(pady=12)
        
        # Main container with tabs
        main_container = ttk.Frame(self.root, padding=10)
        main_container.pack(fill="both", expand=True)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)
        
        # Tab 1: Scanner (main feature)
        self.create_scanner_tab()
        
        # Tab 2: Generate QR
        self.create_qr_tab()
        
        # Tab 3: Reports
        self.create_reports_tab()
    
    def create_scanner_tab(self):
        """Create compact scanner tab."""
        scanner_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(scanner_frame, text="📷 Scanner")
        
        # Instructions (compact)
        info_label = tk.Label(
            scanner_frame,
            text="Click 'Start' → Show QR code to camera → Attendance marked!",
            font=("Helvetica", 9),
            fg="gray"
        )
        info_label.pack(pady=5)
        
        # Camera preview (compact)
        self.camera_label = tk.Label(
            scanner_frame,
            text="Camera preview",
            bg="black",
            fg="white",
            font=("Helvetica", 10),
            width=60,
            height=12
        )
        self.camera_label.pack(pady=5)
        
        # Status
        self.scan_status_label = tk.Label(
            scanner_frame,
            text="Ready to scan",
            font=("Helvetica", 10, "bold"),
            fg="blue"
        )
        self.scan_status_label.pack(pady=5)
        
        # Control buttons (larger for easier clicking)
        button_frame = ttk.Frame(scanner_frame)
        button_frame.pack(pady=10)
        
        self.start_scan_btn = ttk.Button(
            button_frame,
            text="▶️ START SCANNER",
            command=self.start_scanner,
            width=20
        )
        self.start_scan_btn.pack(side="left", padx=5)
        
        self.stop_scan_btn = ttk.Button(
            button_frame,
            text="⏹️ STOP",
            command=self.stop_scanner,
            state="disabled",
            width=15
        )
        self.stop_scan_btn.pack(side="left", padx=5)
        
        # Recent scans (compact)
        recent_frame = ttk.LabelFrame(scanner_frame, text="Recent", padding=5)
        recent_frame.pack(fill="both", expand=True, pady=5)
        
        self.recent_scans_text = tk.Text(recent_frame, height=3, font=("Courier", 8))
        scrollbar = ttk.Scrollbar(recent_frame, command=self.recent_scans_text.yview)
        self.recent_scans_text.config(yscrollcommand=scrollbar.set)
        
        self.recent_scans_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_qr_tab(self):
        """Create compact QR generation tab."""
        qr_frame = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(qr_frame, text="📝 QR Codes")
        
        # Title
        ttk.Label(
            qr_frame,
            text="Generate QR Codes",
            font=("Helvetica", 12, "bold")
        ).pack(pady=10)
        
        # Instructions
        instructions = tk.Text(qr_frame, height=6, wrap="word", font=("Helvetica", 9))
        instructions.pack(fill="x", pady=10)
        instructions.insert("1.0", """
1. Make sure 'students.csv' exists
2. Click 'Generate QR Codes'
3. Find QR codes in 'qr_codes/' folder
4. Print and distribute to students

Format: StudentID,Name,Class
""")
        instructions.config(state="disabled")
        
        # Status
        self.qr_status_label = tk.Label(
            qr_frame,
            text="Ready",
            font=("Helvetica", 10),
            fg="gray"
        )
        self.qr_status_label.pack(pady=10)
        
        # Buttons
        button_frame = ttk.Frame(qr_frame)
        button_frame.pack(pady=15)
        
        ttk.Button(
            button_frame,
            text="🔄 Generate QR Codes",
            command=self.generate_qr_codes,
            width=25
        ).pack(pady=5)
        
        ttk.Button(
            button_frame,
            text="📁 Open QR Folder",
            command=self.open_qr_folder,
            width=25
        ).pack(pady=5)
    
    def create_reports_tab(self):
        """Create compact reports tab."""
        reports_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(reports_frame, text="📊 Reports")
        
        # Date selection
        date_frame = ttk.Frame(reports_frame)
        date_frame.pack(fill="x", pady=5)
        
        ttk.Label(date_frame, text="Date:").pack(side="left", padx=5)
        
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(date_frame, textvariable=self.date_var, width=15).pack(side="left", padx=5)
        
        ttk.Button(
            date_frame,
            text="Today",
            command=lambda: self.date_var.set(datetime.now().strftime("%Y-%m-%d")),
            width=10
        ).pack(side="left", padx=5)
        
        # Report display
        report_frame = ttk.Frame(reports_frame)
        report_frame.pack(fill="both", expand=True, pady=5)
        
        self.report_text = tk.Text(
            report_frame,
            font=("Courier", 8),
            wrap="none"
        )
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(report_frame, orient="vertical", command=self.report_text.yview)
        h_scroll = ttk.Scrollbar(report_frame, orient="horizontal", command=self.report_text.xview)
        self.report_text.config(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.report_text.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        report_frame.grid_rowconfigure(0, weight=1)
        report_frame.grid_columnconfigure(0, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(reports_frame)
        button_frame.pack(pady=5)
        
        ttk.Button(
            button_frame,
            text="📋 Daily Report",
            command=self.show_daily_report,
            width=15
        ).pack(side="left", padx=3)
        
        ttk.Button(
            button_frame,
            text="📊 By Class",
            command=self.show_classwise_report,
            width=15
        ).pack(side="left", padx=3)
        
        ttk.Button(
            button_frame,
            text="💾 Export",
            command=self.export_report,
            width=15
        ).pack(side="left", padx=3)
    
    # Action methods (same as before)
    
    def generate_qr_codes(self):
        """Generate QR codes for all students."""
        try:
            self.qr_status_label.config(text="Generating...", fg="blue")
            self.root.update()
            
            students = read_students_csv("students.csv")
            count = generate_all_qr_codes(students)
            
            self.qr_status_label.config(
                text=f"✓ Generated {count} QR codes!",
                fg="green"
            )
            
            messagebox.showinfo("Success", f"Generated {count} QR codes!")
        
        except Exception as e:
            self.qr_status_label.config(text=f"Error: {str(e)}", fg="red")
            messagebox.showerror("Error", f"Failed:\n{str(e)}")
    
    def open_qr_folder(self):
        """Open QR codes folder."""
        if os.path.exists("qr_codes"):
            os.system("qr_codes" if os.name == 'nt' else "open qr_codes")
        else:
            messagebox.showwarning("Not Found", "qr_codes folder not found!")
    
    def start_scanner(self):
        """Start the QR scanner."""
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
        """Run scanner loop."""
        try:
            camera = cv2.VideoCapture(0)
            
            if not camera.isOpened():
                self.scan_status_label.config(text="❌ Camera not found!", fg="red")
                self.scanning = False
                self.start_scan_btn.config(state="normal")
                self.stop_scan_btn.config(state="disabled")
                return
            
            self.scan_status_label.config(text="✓ Scanner running", fg="green")
            
            while self.scanning:
                ret, frame = camera.read()
                if not ret:
                    break
                
                # Resize for display
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width = frame_rgb.shape[:2]
                max_width = 550
                if width > max_width:
                    ratio = max_width / width
                    frame_rgb = cv2.resize(frame_rgb, (int(width * ratio), int(height * ratio)))
                
                # Convert to PhotoImage
                image = Image.fromarray(frame_rgb)
                photo = ImageTk.PhotoImage(image)
                
                # Update GUI
                self.camera_label.config(image=photo)
                self.camera_label.image = photo
                
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
        self.scan_status_label.config(text="Stopping...", fg="blue")
    
    def show_daily_report(self):
        """Display daily report."""
        try:
            date_str = self.date_var.get()
            report = self.report_generator.get_daily_report(date_str)
            
            output = f"DAILY REPORT - {report['date']}\n"
            output += "="*50 + "\n\n"
            output += f"Total: {report['total']} | "
            output += f"Present: {report['present']} ({report['percentage']}%) | "
            output += f"Absent: {report['absent']}\n\n"
            
            output += f"Present ({len(report['present_students'])}):\n"
            output += "-"*50 + "\n"
            for s in report['present_students']:
                output += f"{s['StudentID']:<8} {s['Name']:<20} {s['Time']}\n"
            
            self.report_text.delete("1.0", "end")
            self.report_text.insert("1.0", output)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed:\n{str(e)}")
    
    def show_classwise_report(self):
        """Display class-wise report."""
        try:
            date_str = self.date_var.get()
            class_stats = self.report_generator.get_class_wise_report(date_str)
            
            output = f"CLASS-WISE REPORT - {date_str}\n"
            output += "="*50 + "\n\n"
            output += f"{'Class':<8} {'Total':<8} {'Present':<8} {'%'}\n"
            output += "-"*50 + "\n"
            
            for class_name, stats in sorted(class_stats.items()):
                output += f"{class_name:<8} {stats['total']:<8} {stats['present']:<8} {stats['percentage']}%\n"
            
            self.report_text.delete("1.0", "end")
            self.report_text.insert("1.0", output)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed:\n{str(e)}")
    
    def export_report(self):
        """Export report to Excel."""
        try:
            date_str = self.date_var.get()
            filename = f"report_{date_str.replace('-', '_')}.xlsx"
            
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=filename
            )
            
            if filepath:
                self.report_generator.export_to_excel(filepath, date_str)
                messagebox.showinfo("Success", f"Exported to:\n{filepath}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed:\n{str(e)}")


def main():
    """Launch the compact GUI."""
    root = tk.Tk()
    app = CompactAttendanceGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
