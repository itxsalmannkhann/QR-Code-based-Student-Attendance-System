"""
Quick Start Demo
================
Automated demonstration of the Student Attendance System.

This script will:
1. Generate sample QR codes
2. Show you how to use the system
3. Create sample reports

Run: python demo.py
"""

import os
import sys
from generate_qr import read_students_csv, generate_all_qr_codes
from report_generator import ReportGenerator


def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def main():
    """Run the demonstration."""
    
    print_header("🎓 Student Attendance System - Quick Start Demo")
    
    print("This demo will:")
    print("  1. Generate QR codes for all students")
    print("  2. Show you the files created")
    print("  3. Explain next steps")
    print()
    
    input("Press Enter to continue...")
    
    # Step 1: Generate QR codes
    print_header("Step 1: Generating QR Codes")
    
    try:
        students = read_students_csv("students.csv")
        print(f"✓ Found {len(students)} students in students.csv")
        print()
        
        count = generate_all_qr_codes(students, "qr_codes")
        
        if count > 0:
            print("\n🎉 Success! QR codes have been generated.")
            print(f"📁 Check the 'qr_codes' folder to see {count} QR code images.")
        
    except FileNotFoundError:
        print("❌ Error: students.csv not found!")
        print("\n💡 Create students.csv with format:")
        print("   StudentID,Name,Class")
        print("   101,John Doe,10A")
        return
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Step 2: Explain next steps
    print_header("Step 2: Next Steps")
    
    print("✅ QR codes generated successfully!")
    print()
    print("📋 What to do next:")
    print()
    print("1️⃣  PRINT QR CODES")
    print("   • Open the 'qr_codes' folder")
    print("   • Print each student's QR code")
    print("   • Distribute to students")
    print()
    print("2️⃣  START ATTENDANCE SCANNER")
    print("   • Run: python scanner.py")
    print("   • Point webcam at QR codes")
    print("   • Press 'q' to quit")
    print()
    print("3️⃣  VIEW REPORTS")
    print("   • Run: python report_generator.py")
    print("   • See daily attendance summary")
    print("   • Export to Excel if needed")
    print()
    print("4️⃣  USE GUI (OPTIONAL)")
    print("   • Run: python gui.py")
    print("   • User-friendly interface")
    print("   • All features in one place")
    print()
    
    # Step 3: System check
    print_header("Step 3: System Check")
    
    print("Checking system components...")
    print()
    
    # Check files
    files_to_check = [
        ("students.csv", "Student database"),
        ("generate_qr.py", "QR generator"),
        ("scanner.py", "Attendance scanner"),
        ("report_generator.py", "Report generator"),
        ("gui.py", "GUI interface"),
    ]
    
    for filename, description in files_to_check:
        if os.path.exists(filename):
            print(f"✓ {description:<30} ({filename})")
        else:
            print(f"✗ {description:<30} ({filename}) - MISSING")
    
    print()
    
    # Check QR codes
    if os.path.exists("qr_codes"):
        qr_count = len([f for f in os.listdir("qr_codes") if f.endswith(".png")])
        print(f"✓ QR codes folder: {qr_count} images generated")
    else:
        print("✗ QR codes folder not found")
    
    print()
    
    # Final message
    print_header("🎉 Demo Complete!")
    
    print("Your Student Attendance System is ready to use!")
    print()
    print("Quick commands:")
    print("  python scanner.py          → Start scanning attendance")
    print("  python report_generator.py → View reports")
    print("  python gui.py              → Launch GUI")
    print()
    print("📚 For detailed documentation, see README.md")
    print()
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        print("Run 'python demo.py' again anytime!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check the README.md for troubleshooting.")
