import datetime
from datetime import time, date, timedelta
import pytz
from typing import Tuple, List, Dict, Optional
import streamlit as st
import json
import os

class TimeManager:
    def __init__(self, timezone: str = 'Asia/Kolkata'):
        self.timezone = pytz.timezone(timezone)
        self.start_time = time(9, 0)   # 9:00 AM
        self.end_time = time(9, 30)    # 9:30 AM (updated from 9:20)
        self.manual_holidays_file = "data/manual_holidays.json"
        self.settings_file = "data/time_settings.json"
        
        # Load settings
        self._load_settings()
        
        # Create manual holidays file if it doesn't exist
        if not os.path.exists(self.manual_holidays_file):
            self._save_manual_holidays([])
    
    def _load_settings(self):
        """Load time settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.start_time = time.fromisoformat(settings.get('start_time', '09:00:00'))
                    self.end_time = time.fromisoformat(settings.get('end_time', '09:30:00'))  # Updated default
                    self.timezone = pytz.timezone(settings.get('timezone', 'Asia/Kolkata'))
        except Exception as e:
            st.warning(f"Could not load time settings: {str(e)}")
    
    def _save_settings(self):
        """Save time settings to file"""
        try:
            os.makedirs("data", exist_ok=True)
            settings = {
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat(),
                'timezone': str(self.timezone)
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            st.error(f"Could not save time settings: {str(e)}")
    
    def get_current_time(self) -> datetime.datetime:
        """Get current time in configured timezone"""
        return datetime.datetime.now(self.timezone)
    
    def is_within_time_window(self) -> Tuple[bool, str]:
        """Check if current time is within the allowed attendance window"""
        try:
            current_time = self.get_current_time().time()
            
            if self.start_time <= current_time <= self.end_time:
                return True, "Within attendance window"
            elif current_time < self.start_time:
                time_until_start = datetime.datetime.combine(date.today(), self.start_time) - \
                                 datetime.datetime.combine(date.today(), current_time)
                return False, f"Attendance starts in {time_until_start}"
            else:
                return False, "Attendance window has closed"
                
        except Exception as e:
            return False, f"Error checking time window: {str(e)}"
    
    def is_weekend(self, check_date: date = None) -> bool:
        """Check if given date (or today) is weekend"""
        if check_date is None:
            check_date = self.get_current_time().date()
        
        # Monday = 0, Sunday = 6
        return check_date.weekday() >= 5  # Saturday = 5, Sunday = 6
    
    def is_manual_holiday(self, check_date: date = None) -> Tuple[bool, str]:
        """Check if given date is a manually added holiday"""
        if check_date is None:
            check_date = self.get_current_time().date()
        
        try:
            manual_holidays = self._load_manual_holidays()
            date_str = check_date.strftime('%Y-%m-%d')
            
            for holiday in manual_holidays:
                if holiday['date'] == date_str:
                    return True, holiday['name']
            
            return False, ""
            
        except Exception as e:
            st.error(f"Error checking manual holidays: {str(e)}")
            return False, ""
    
    def _load_manual_holidays(self) -> List[Dict]:
        """Load manual holidays from file"""
        try:
            if os.path.exists(self.manual_holidays_file):
                with open(self.manual_holidays_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            st.error(f"Error loading manual holidays: {str(e)}")
            return []
    
    def _save_manual_holidays(self, holidays: List[Dict]):
        """Save manual holidays to file"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.manual_holidays_file, 'w') as f:
                json.dump(holidays, f, indent=2)
        except Exception as e:
            st.error(f"Error saving manual holidays: {str(e)}")
    
    def add_manual_holiday(self, holiday_date: date, holiday_name: str) -> Tuple[bool, str]:
        """Add a manual holiday"""
        try:
            holidays = self._load_manual_holidays()
            date_str = holiday_date.strftime('%Y-%m-%d')
            
            # Check if holiday already exists
            for holiday in holidays:
                if holiday['date'] == date_str:
                    return False, "Holiday already exists for this date"
            
            # Add new holiday
            holidays.append({
                'date': date_str,
                'name': holiday_name,
                'added_on': datetime.datetime.now().isoformat()
            })
            
            self._save_manual_holidays(holidays)
            return True, "Holiday added successfully"
            
        except Exception as e:
            return False, f"Error adding holiday: {str(e)}"
    
    def remove_manual_holiday(self, holiday_date: date) -> Tuple[bool, str]:
        """Remove a manual holiday"""
        try:
            holidays = self._load_manual_holidays()
            date_str = holiday_date.strftime('%Y-%m-%d')
            
            # Find and remove holiday
            holidays = [h for h in holidays if h['date'] != date_str]
            
            self._save_manual_holidays(holidays)
            return True, "Holiday removed successfully"
            
        except Exception as e:
            return False, f"Error removing holiday: {str(e)}"
    
    def get_upcoming_manual_holidays(self, days_ahead: int = 30) -> List[Dict]:
        """Get upcoming manual holidays"""
        try:
            holidays = self._load_manual_holidays()
            current_date = self.get_current_time().date()
            end_date = current_date + timedelta(days=days_ahead)
            
            upcoming = []
            for holiday in holidays:
                holiday_date = datetime.datetime.strptime(holiday['date'], '%Y-%m-%d').date()
                if current_date <= holiday_date <= end_date:
                    upcoming.append(holiday)
            
            # Sort by date
            upcoming.sort(key=lambda x: x['date'])
            return upcoming
            
        except Exception as e:
            st.error(f"Error getting upcoming holidays: {str(e)}")
            return []
    
    def is_attendance_day(self, check_date: date = None) -> Tuple[bool, str]:
        """Check if given date is a valid attendance day"""
        if check_date is None:
            check_date = self.get_current_time().date()
        
        # Check weekend
        if self.is_weekend(check_date):
            return False, "Weekend"
        
        # Check manual holidays
        is_holiday, holiday_name = self.is_manual_holiday(check_date)
        if is_holiday:
            return False, f"Holiday: {holiday_name}"
        
        return True, "Regular working day"
    
    def get_time_until_window(self) -> Optional[timedelta]:
        """Get time remaining until attendance window starts"""
        try:
            current_time = self.get_current_time()
            current_date = current_time.date()
            
            # Create datetime for start of attendance window today
            window_start = datetime.datetime.combine(current_date, self.start_time)
            window_start = self.timezone.localize(window_start)
            
            if current_time < window_start:
                return window_start - current_time
            else:
                return None
                
        except Exception as e:
            st.error(f"Error calculating time until window: {str(e)}")
            return None
    
    def get_time_remaining_in_window(self) -> Optional[timedelta]:
        """Get time remaining in attendance window"""
        try:
            current_time = self.get_current_time()
            current_date = current_time.date()
            
            # Create datetime for end of attendance window today
            window_end = datetime.datetime.combine(current_date, self.end_time)
            window_end = self.timezone.localize(window_end)
            
            if current_time < window_end:
                return window_end - current_time
            else:
                return None
                
        except Exception as e:
            st.error(f"Error calculating time remaining: {str(e)}")
            return None
    
    def update_time_window(self, start_time: time, end_time: time) -> Tuple[bool, str]:
        """Update attendance time window"""
        try:
            self.start_time = start_time
            self.end_time = end_time
            self._save_settings()
            return True, "Time window updated successfully"
        except Exception as e:
            return False, f"Error updating time window: {str(e)}"
    
    def get_attendance_status(self) -> Dict:
        """Get comprehensive attendance status"""
        try:
            current_time = self.get_current_time()
            is_valid_day, day_reason = self.is_attendance_day()
            can_mark_attendance, window_reason = self.is_within_time_window()
            
            status = {
                'current_time': current_time,
                'is_valid_day': is_valid_day,
                'day_reason': day_reason,
                'can_mark_attendance': can_mark_attendance and is_valid_day,
                'window_reason': window_reason,
                'start_time': self.start_time,
                'end_time': self.end_time,
                'timezone': str(self.timezone)
            }
            
            # Add time information
            time_until_start = self.get_time_until_window()
            if time_until_start:
                status['time_until_start'] = str(time_until_start)
            
            time_remaining = self.get_time_remaining_in_window()
            if time_remaining:
                status['time_remaining'] = str(time_remaining)
            
            return status
            
        except Exception as e:
            st.error(f"Error getting attendance status: {str(e)}")
            return {}
