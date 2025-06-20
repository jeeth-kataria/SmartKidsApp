import pandas as pd
import numpy as np
import os
from datetime import datetime, date
import pickle
import shutil
from typing import Dict, List, Optional, Tuple
import streamlit as st
import json

class CSVManager:
    """
    CSV-based storage manager for Smart Kids Attendance System
    Saves daily attendance records in date-named CSV files
    """
    
    def __init__(self):
        # Directory structure
        self.data_dir = "data"
        self.teachers_file = "data/teachers.csv"
        self.face_encodings_dir = "face_encodings"
        self.backup_dir = "data/backups"
        self.daily_attendance_dir = "data/daily_attendance"
        
        # Create directories
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.face_encodings_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(self.daily_attendance_dir, exist_ok=True)
        
        # Initialize teachers file if it doesn't exist
        self._initialize_teachers_file()
    
    def _initialize_teachers_file(self):
        """Initialize teachers CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.teachers_file):
            teachers_df = pd.DataFrame(columns=[
                'ID', 'Name', 'Department', 'Registration_Date', 
                'Face_Encoding_Path', 'Status', 'Email'
            ])
            teachers_df.to_csv(self.teachers_file, index=False)
            st.success("✅ Created teachers CSV file")
    
    def _get_daily_attendance_file(self, target_date: date = None) -> str:
        """Get the CSV file path for a specific date"""
        if target_date is None:
            target_date = date.today()
        
        filename = f"{target_date.strftime('%d-%m-%Y')}.csv"
        return os.path.join(self.daily_attendance_dir, filename)
    
    def add_teacher(self, teacher_id: str, name: str, department: str, 
                   face_encoding: np.ndarray, email: str = "") -> Tuple[bool, str]:
        """Add a new teacher to CSV storage"""
        try:
            # Save face encoding
            encoding_path = f"{self.face_encodings_dir}/{teacher_id}.pkl"
            with open(encoding_path, 'wb') as f:
                pickle.dump(face_encoding, f)
            
            # Load existing teachers
            if os.path.exists(self.teachers_file):
                teachers_df = pd.read_csv(self.teachers_file)
            else:
                teachers_df = pd.DataFrame(columns=[
                    'ID', 'Name', 'Department', 'Registration_Date', 
                    'Face_Encoding_Path', 'Status', 'Email'
                ])
            
            # Check if teacher already exists
            if teacher_id in teachers_df['ID'].values:
                return False, "Teacher ID already exists"
            
            # Add new teacher
            new_teacher = {
                'ID': teacher_id,
                'Name': name,
                'Department': department,
                'Registration_Date': datetime.now().strftime('%Y-%m-%d'),
                'Face_Encoding_Path': encoding_path,
                'Status': 'Active',
                'Email': email
            }
            
            teachers_df = pd.concat([teachers_df, pd.DataFrame([new_teacher])], ignore_index=True)
            teachers_df.to_csv(self.teachers_file, index=False)
            
            return True, f"Teacher {name} added successfully to CSV"
            
        except Exception as e:
            return False, f"Error adding teacher: {str(e)}"
    
    def get_all_teachers(self) -> pd.DataFrame:
        """Get all teachers from CSV"""
        try:
            if os.path.exists(self.teachers_file):
                return pd.read_csv(self.teachers_file)
            else:
                return pd.DataFrame()
        except Exception as e:
            st.error(f"Error loading teachers: {str(e)}")
            return pd.DataFrame()
    
    def get_teacher_face_encodings(self) -> Dict[str, np.ndarray]:
        """Load all teacher face encodings"""
        encodings = {}
        teachers_df = self.get_all_teachers()
        
        for _, teacher in teachers_df.iterrows():
            if teacher['Status'] == 'Active':
                try:
                    encoding_path = teacher['Face_Encoding_Path']
                    if os.path.exists(encoding_path):
                        with open(encoding_path, 'rb') as f:
                            encodings[teacher['ID']] = pickle.load(f)
                except Exception as e:
                    st.warning(f"Could not load encoding for {teacher['Name']}: {str(e)}")
        
        return encodings
    
    def log_attendance(self, teacher_id: str, confidence: float, 
                      is_holiday: bool = False, holiday_name: str = "") -> Tuple[bool, str]:
        """Log attendance to daily CSV file"""
        try:
            today = date.today()
            current_time = datetime.now().strftime('%H:%M:%S')
            
            # Get teacher name
            teachers_df = self.get_all_teachers()
            teacher_row = teachers_df[teachers_df['ID'] == teacher_id]
            
            if teacher_row.empty:
                return False, "Teacher not found"
            
            teacher_name = teacher_row['Name'].iloc[0]
            
            # Get today's attendance file
            attendance_file = self._get_daily_attendance_file(today)
            
            # Load or create today's attendance
            if os.path.exists(attendance_file):
                attendance_df = pd.read_csv(attendance_file)
            else:
                attendance_df = pd.DataFrame(columns=[
                    'Date', 'Teacher_ID', 'Name', 'Time_In', 'Status', 
                    'Is_Holiday', 'Holiday_Name', 'Recognition_Confidence'
                ])
            
            # Check if already marked today
            existing_record = attendance_df[
                (attendance_df['Teacher_ID'] == teacher_id) & 
                (attendance_df['Date'] == today.strftime('%Y-%m-%d'))
            ]
            
            if not existing_record.empty:
                return False, "Attendance already marked for today"
            
            # Add attendance record
            attendance_record = {
                'Date': today.strftime('%Y-%m-%d'),
                'Teacher_ID': teacher_id,
                'Name': teacher_name,
                'Time_In': current_time,
                'Status': 'Present',
                'Is_Holiday': is_holiday,
                'Holiday_Name': holiday_name,
                'Recognition_Confidence': confidence
            }
            
            attendance_df = pd.concat([attendance_df, pd.DataFrame([attendance_record])], ignore_index=True)
            attendance_df.to_csv(attendance_file, index=False)
            
            return True, f"Attendance marked for {teacher_name} in {today.strftime('%d-%m-%Y')}.csv"
            
        except Exception as e:
            return False, f"Error logging attendance: {str(e)}"
    
    def get_today_attendance(self) -> pd.DataFrame:
        """Get today's attendance records"""
        try:
            today = date.today()
            attendance_file = self._get_daily_attendance_file(today)
            
            if os.path.exists(attendance_file):
                return pd.read_csv(attendance_file)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            st.error(f"Error loading today's attendance: {str(e)}")
            return pd.DataFrame()
    
    def get_attendance_by_date(self, target_date: date) -> pd.DataFrame:
        """Get attendance records for a specific date"""
        try:
            attendance_file = self._get_daily_attendance_file(target_date)
            
            if os.path.exists(attendance_file):
                return pd.read_csv(attendance_file)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            st.error(f"Error loading attendance for {target_date}: {str(e)}")
            return pd.DataFrame()
    
    def get_attendance_by_date_range(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get attendance records for a date range"""
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            all_attendance = []
            
            current_date = start
            while current_date <= end:
                daily_attendance = self.get_attendance_by_date(current_date)
                if not daily_attendance.empty:
                    all_attendance.append(daily_attendance)
                current_date += pd.Timedelta(days=1)
            
            if all_attendance:
                return pd.concat(all_attendance, ignore_index=True)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            st.error(f"Error loading attendance data: {str(e)}")
            return pd.DataFrame()
    
    def get_available_dates(self) -> List[str]:
        """Get list of dates with attendance records"""
        try:
            available_dates = []
            
            if os.path.exists(self.daily_attendance_dir):
                for filename in os.listdir(self.daily_attendance_dir):
                    if filename.endswith('.csv'):
                        # Extract date from filename (dd-mm-yyyy.csv)
                        date_str = filename.replace('.csv', '')
                        try:
                            # Convert to standard format
                            date_obj = datetime.strptime(date_str, '%d-%m-%Y')
                            available_dates.append(date_obj.strftime('%Y-%m-%d'))
                        except ValueError:
                            continue
            
            return sorted(available_dates)
            
        except Exception as e:
            st.error(f"Error getting available dates: {str(e)}")
            return []
    
    def export_to_excel(self, start_date: str, end_date: str) -> str:
        """Export attendance data to Excel file"""
        try:
            attendance_df = self.get_attendance_by_date_range(start_date, end_date)
            
            if attendance_df.empty:
                return "No attendance data found for the specified date range"
            
            # Create report filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = f"excel_reports/attendance_report_{start_date}_to_{end_date}_{timestamp}.xlsx"
            
            # Ensure directory exists
            os.makedirs("excel_reports", exist_ok=True)
            
            # Export to Excel
            attendance_df.to_excel(report_file, index=False)
            
            return f"Report exported successfully: {report_file}"
            
        except Exception as e:
            return f"Error exporting report: {str(e)}"
    
    def get_teacher_stats(self) -> Dict:
        """Get statistics about teachers and attendance"""
        try:
            teachers_df = self.get_all_teachers()
            
            # Get attendance for last 365 days
            end_date = date.today()
            start_date = (end_date - pd.Timedelta(days=365)).strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            attendance_df = self.get_attendance_by_date_range(start_date, end_date_str)
            
            # Calculate this month's attendance
            this_month_start = date.today().replace(day=1)
            this_month_attendance = self.get_attendance_by_date_range(
                this_month_start.strftime('%Y-%m-%d'),
                end_date_str
            )
            
            stats = {
                'total_teachers': len(teachers_df[teachers_df['Status'] == 'Active']) if not teachers_df.empty else 0,
                'total_attendance_records': len(attendance_df),
                'today_attendance': len(self.get_today_attendance()),
                'this_month_attendance': len(this_month_attendance)
            }
            
            return stats
        except Exception as e:
            st.error(f"Error calculating stats: {str(e)}")
            return {}
    
    def backup_data(self) -> bool:
        """Create backup of all data"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}")
            os.makedirs(backup_path, exist_ok=True)
            
            # Backup teachers file
            if os.path.exists(self.teachers_file):
                shutil.copy2(self.teachers_file, os.path.join(backup_path, 'teachers.csv'))
            
            # Backup daily attendance files
            attendance_backup_dir = os.path.join(backup_path, 'daily_attendance')
            os.makedirs(attendance_backup_dir, exist_ok=True)
            
            if os.path.exists(self.daily_attendance_dir):
                for filename in os.listdir(self.daily_attendance_dir):
                    if filename.endswith('.csv'):
                        src = os.path.join(self.daily_attendance_dir, filename)
                        dst = os.path.join(attendance_backup_dir, filename)
                        shutil.copy2(src, dst)
            
            # Backup face encodings
            encodings_backup_dir = os.path.join(backup_path, 'face_encodings')
            os.makedirs(encodings_backup_dir, exist_ok=True)
            
            if os.path.exists(self.face_encodings_dir):
                for filename in os.listdir(self.face_encodings_dir):
                    if filename.endswith('.pkl'):
                        src = os.path.join(self.face_encodings_dir, filename)
                        dst = os.path.join(encodings_backup_dir, filename)
                        shutil.copy2(src, dst)
            
            st.success(f"✅ Backup created: {backup_path}")
            return True
            
        except Exception as e:
            st.error(f"Backup failed: {str(e)}")
            return False
    
    def get_daily_files_info(self) -> List[Dict]:
        """Get information about all daily attendance files"""
        try:
            files_info = []
            
            if os.path.exists(self.daily_attendance_dir):
                for filename in os.listdir(self.daily_attendance_dir):
                    if filename.endswith('.csv'):
                        file_path = os.path.join(self.daily_attendance_dir, filename)
                        
                        # Get file stats
                        stat = os.stat(file_path)
                        file_size = stat.st_size
                        modified_time = datetime.fromtimestamp(stat.st_mtime)
                        
                        # Get record count
                        try:
                            df = pd.read_csv(file_path)
                            record_count = len(df)
                        except:
                            record_count = 0
                        
                        # Extract date from filename
                        date_str = filename.replace('.csv', '')
                        try:
                            date_obj = datetime.strptime(date_str, '%d-%m-%Y')
                            formatted_date = date_obj.strftime('%Y-%m-%d')
                        except ValueError:
                            formatted_date = date_str
                        
                        files_info.append({
                            'filename': filename,
                            'date': formatted_date,
                            'record_count': record_count,
                            'file_size': file_size,
                            'modified_time': modified_time,
                            'file_path': file_path
                        })
            
            # Sort by date (newest first)
            files_info.sort(key=lambda x: x['date'], reverse=True)
            return files_info
            
        except Exception as e:
            st.error(f"Error getting files info: {str(e)}")
            return []
    
    def download_daily_file(self, target_date: date) -> Tuple[bool, str]:
        """Prepare a daily attendance file for download"""
        try:
            attendance_file = self._get_daily_attendance_file(target_date)
            
            if os.path.exists(attendance_file):
                return True, attendance_file
            else:
                return False, f"No attendance file found for {target_date.strftime('%d-%m-%Y')}"
                
        except Exception as e:
            return False, f"Error preparing file: {str(e)}"
    
    def delete_teacher(self, teacher_id: str) -> Tuple[bool, str]:
        """Delete a teacher from the system"""
        try:
            teachers_df = self.get_all_teachers()
            
            if teacher_id not in teachers_df['ID'].values:
                return False, "Teacher not found"
            
            # Get teacher info
            teacher_row = teachers_df[teachers_df['ID'] == teacher_id]
            teacher_name = teacher_row['Name'].iloc[0]
            encoding_path = teacher_row['Face_Encoding_Path'].iloc[0]
            
            # Remove from teachers CSV
            teachers_df = teachers_df[teachers_df['ID'] != teacher_id]
            teachers_df.to_csv(self.teachers_file, index=False)
            
            # Delete face encoding file
            if os.path.exists(encoding_path):
                os.remove(encoding_path)
            
            return True, f"Teacher {teacher_name} deleted successfully"
            
        except Exception as e:
            return False, f"Error deleting teacher: {str(e)}" 