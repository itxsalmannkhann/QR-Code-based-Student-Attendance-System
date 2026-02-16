"""
Attendance Report Generator
============================
Generate daily, weekly, and custom attendance reports.

Features:
- Daily attendance summary
- Class-wise analysis
- Export to Excel
- Absentee list generation
- Attendance statistics

Usage:
    python report_generator.py
    python report_generator.py --date 2024-02-16
    python report_generator.py --export excel
"""

import pandas as pd
import csv
import os
from datetime import datetime, timedelta
from collections import defaultdict
import argparse


class ReportGenerator:
    """
    Generate and analyze attendance reports.
    """
    
    def __init__(self, attendance_file="attendance.csv", students_file="students.csv"):
        """
        Initialize report generator.
        
        Args:
            attendance_file (str): Path to attendance records
            students_file (str): Path to students database
        """
        self.attendance_file = attendance_file
        self.students_file = students_file
        self.students_df = None
        self.attendance_df = None
        
        self._load_data()
    
    def _load_data(self):
        """Load student and attendance data."""
        try:
            # Load students
            if os.path.exists(self.students_file):
                self.students_df = pd.read_csv(self.students_file)
                print(f"✓ Loaded {len(self.students_df)} students")
            else:
                print(f"⚠️  Students file not found: {self.students_file}")
            
            # Load attendance
            if os.path.exists(self.attendance_file):
                self.attendance_df = pd.read_csv(self.attendance_file)
                
                if not self.attendance_df.empty:
                    print(f"✓ Loaded {len(self.attendance_df)} attendance records")
                else:
                    print("⚠️  No attendance records found")
            else:
                print(f"⚠️  Attendance file not found: {self.attendance_file}")
        
        except Exception as e:
            print(f"❌ Error loading data: {e}")
    
    def get_daily_report(self, date_str=None):
        """
        Generate daily attendance report.
        
        Args:
            date_str (str): Date in YYYY-MM-DD format (None = today)
        
        Returns:
            dict: Daily report data
        """
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        if self.attendance_df is None or self.attendance_df.empty:
            return {
                'date': date_str,
                'present': 0,
                'absent': 0,
                'percentage': 0.0,
                'present_students': [],
                'absent_students': []
            }
        
        # Filter today's attendance
        daily_attendance = self.attendance_df[self.attendance_df['Date'] == date_str]
        
        # Get present students
        present_ids = set(daily_attendance['StudentID'].astype(str).tolist())
        present_students = daily_attendance[['StudentID', 'Name', 'Class', 'Time']].to_dict('records')
        
        # Get absent students
        if self.students_df is not None:
            all_student_ids = set(self.students_df['StudentID'].astype(str).tolist())
            absent_ids = all_student_ids - present_ids
            
            absent_students = []
            for sid in absent_ids:
                student = self.students_df[self.students_df['StudentID'].astype(str) == sid]
                if not student.empty:
                    absent_students.append({
                        'StudentID': sid,
                        'Name': student.iloc[0]['Name'],
                        'Class': student.iloc[0]['Class']
                    })
            
            total_students = len(all_student_ids)
            attendance_percentage = (len(present_ids) / total_students * 100) if total_students > 0 else 0
        else:
            absent_students = []
            total_students = len(present_ids)
            attendance_percentage = 100.0
        
        return {
            'date': date_str,
            'present': len(present_ids),
            'absent': len(absent_students),
            'total': total_students,
            'percentage': round(attendance_percentage, 2),
            'present_students': present_students,
            'absent_students': absent_students
        }
    
    def get_class_wise_report(self, date_str=None):
        """
        Generate class-wise attendance report.
        
        Args:
            date_str (str): Date in YYYY-MM-DD format (None = today)
        
        Returns:
            dict: Class-wise statistics
        """
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        daily_report = self.get_daily_report(date_str)
        
        # Group by class
        class_stats = defaultdict(lambda: {'present': 0, 'absent': 0, 'total': 0})
        
        for student in daily_report['present_students']:
            class_name = student['Class']
            class_stats[class_name]['present'] += 1
            class_stats[class_name]['total'] += 1
        
        for student in daily_report['absent_students']:
            class_name = student['Class']
            class_stats[class_name]['absent'] += 1
            class_stats[class_name]['total'] += 1
        
        # Calculate percentages
        for class_name in class_stats:
            total = class_stats[class_name]['total']
            present = class_stats[class_name]['present']
            class_stats[class_name]['percentage'] = round((present / total * 100), 2) if total > 0 else 0
        
        return dict(class_stats)
    
    def print_daily_report(self, date_str=None):
        """Print formatted daily report."""
        report = self.get_daily_report(date_str)
        
        print("\n" + "="*70)
        print(f"DAILY ATTENDANCE REPORT - {report['date']}")
        print("="*70)
        print(f"\n📊 Summary:")
        print(f"   Total Students: {report['total']}")
        print(f"   Present: {report['present']} ({report['percentage']}%)")
        print(f"   Absent: {report['absent']} ({100 - report['percentage']:.2f}%)")
        
        print(f"\n✓ Present Students ({len(report['present_students'])}):")
        print(f"{'─'*70}")
        print(f"{'ID':<10} {'Name':<25} {'Class':<10} {'Time':<15}")
        print(f"{'─'*70}")
        
        for student in report['present_students']:
            print(f"{student['StudentID']:<10} {student['Name']:<25} {student['Class']:<10} {student['Time']:<15}")
        
        if report['absent_students']:
            print(f"\n✗ Absent Students ({len(report['absent_students'])}):")
            print(f"{'─'*70}")
            print(f"{'ID':<10} {'Name':<25} {'Class':<10}")
            print(f"{'─'*70}")
            
            for student in report['absent_students']:
                print(f"{student['StudentID']:<10} {student['Name']:<25} {student['Class']:<10}")
        
        print("\n" + "="*70)
    
    def print_class_wise_report(self, date_str=None):
        """Print formatted class-wise report."""
        class_stats = self.get_class_wise_report(date_str)
        
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        print("\n" + "="*70)
        print(f"CLASS-WISE ATTENDANCE REPORT - {date_str}")
        print("="*70)
        print(f"\n{'Class':<10} {'Total':<10} {'Present':<10} {'Absent':<10} {'Percentage':<15}")
        print("─"*70)
        
        for class_name, stats in sorted(class_stats.items()):
            print(f"{class_name:<10} {stats['total']:<10} {stats['present']:<10} {stats['absent']:<10} {stats['percentage']:<15.2f}%")
        
        print("="*70 + "\n")
    
    def export_to_excel(self, output_file="attendance_report.xlsx", date_str=None):
        """
        Export daily report to Excel file.
        
        Args:
            output_file (str): Output Excel filename
            date_str (str): Date to export (None = today)
        
        Returns:
            str: Path to exported file
        """
        try:
            report = self.get_daily_report(date_str)
            
            # Create Excel writer
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = {
                    'Metric': ['Date', 'Total Students', 'Present', 'Absent', 'Attendance %'],
                    'Value': [
                        report['date'],
                        report['total'],
                        report['present'],
                        report['absent'],
                        f"{report['percentage']}%"
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                # Present students sheet
                if report['present_students']:
                    present_df = pd.DataFrame(report['present_students'])
                    present_df.to_excel(writer, sheet_name='Present', index=False)
                
                # Absent students sheet
                if report['absent_students']:
                    absent_df = pd.DataFrame(report['absent_students'])
                    absent_df.to_excel(writer, sheet_name='Absent', index=False)
                
                # Class-wise sheet
                class_stats = self.get_class_wise_report(date_str)
                class_df = pd.DataFrame([
                    {
                        'Class': class_name,
                        'Total': stats['total'],
                        'Present': stats['present'],
                        'Absent': stats['absent'],
                        'Percentage': f"{stats['percentage']}%"
                    }
                    for class_name, stats in sorted(class_stats.items())
                ])
                class_df.to_excel(writer, sheet_name='Class-wise', index=False)
            
            output_path = os.path.abspath(output_file)
            print(f"✓ Report exported to: {output_path}")
            return output_path
        
        except Exception as e:
            print(f"❌ Error exporting to Excel: {e}")
            return None


def main():
    """Main function with CLI support."""
    parser = argparse.ArgumentParser(description='Generate attendance reports')
    parser.add_argument('--date', help='Date in YYYY-MM-DD format (default: today)')
    parser.add_argument('--export', choices=['excel'], help='Export format')
    parser.add_argument('--class-wise', action='store_true', help='Show class-wise report')
    
    args = parser.parse_args()
    
    # Initialize report generator
    generator = ReportGenerator()
    
    # Generate reports
    if args.class_wise:
        generator.print_class_wise_report(args.date)
    else:
        generator.print_daily_report(args.date)
    
    # Export if requested
    if args.export == 'excel':
        date_suffix = args.date.replace('-', '_') if args.date else datetime.now().strftime("%Y_%m_%d")
        filename = f"attendance_report_{date_suffix}.xlsx"
        generator.export_to_excel(filename, args.date)


if __name__ == "__main__":
    main()
