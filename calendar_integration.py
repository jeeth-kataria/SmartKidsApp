import os
import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple, Optional
import streamlit as st

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    GOOGLE_CALENDAR_AVAILABLE = False
    # Don't show warning in production - just use fallback

class CalendarIntegration:
    def __init__(self):
        self.credentials_file = "data/google_credentials.json"
        self.token_file = "data/google_token.json"
        self.calendar_cache_file = "data/calendar_cache.json"
        self.scopes = ['https://www.googleapis.com/auth/calendar.readonly']
        self.service = None
        
        # Create data directory
        os.makedirs("data", exist_ok=True)
        
        if GOOGLE_CALENDAR_AVAILABLE:
            self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Calendar service"""
        try:
            creds = None
            
            # Load existing token
            if os.path.exists(self.token_file):
                creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
            
            # If there are no valid credentials, request authorization
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except Exception as e:
                        st.warning(f"Could not refresh Google Calendar credentials: {str(e)}")
                        return
                else:
                    # Check if credentials file exists
                    if not os.path.exists(self.credentials_file):
                        st.warning("Google Calendar credentials not found. Please upload credentials.json file.")
                        return
                    
                    # This would require user interaction in a web flow
                    # For now, we'll use cached data or manual holidays
                    st.info("Google Calendar authentication required. Using cached data.")
                    return
            
            # Save credentials for next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
            
            # Build service
            self.service = build('calendar', 'v3', credentials=creds)
            
        except Exception as e:
            st.warning(f"Could not initialize Google Calendar service: {str(e)}")
    
    def setup_credentials(self, credentials_content: str) -> Tuple[bool, str]:
        """Setup Google Calendar credentials from uploaded file"""
        try:
            # Parse and validate credentials
            creds_data = json.loads(credentials_content)
            
            # Save credentials file
            with open(self.credentials_file, 'w') as f:
                json.dump(creds_data, f, indent=2)
            
            return True, "Credentials saved successfully. Please restart the app to enable Google Calendar integration."
            
        except json.JSONDecodeError:
            return False, "Invalid JSON format in credentials file"
        except Exception as e:
            return False, f"Error saving credentials: {str(e)}"
    
    def get_holidays_from_calendar(self, calendar_id: str = 'en.indian#holiday@group.v.calendar.google.com',
                                 days_ahead: int = 365) -> List[Dict]:
        """Get holidays from Google Calendar"""
        if not GOOGLE_CALENDAR_AVAILABLE or not self.service:
            return self._get_cached_holidays()
        
        try:
            # Calculate date range
            now = datetime.utcnow()
            end_date = now + timedelta(days=days_ahead)
            
            # Call the Calendar API
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=now.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            holidays = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                
                # Parse date
                if 'T' in start:
                    event_date = datetime.fromisoformat(start.replace('Z', '+00:00')).date()
                else:
                    event_date = datetime.fromisoformat(start).date()
                
                holidays.append({
                    'date': event_date.strftime('%Y-%m-%d'),
                    'name': event['summary'],
                    'source': 'google_calendar'
                })
            
            # Cache the results
            self._cache_holidays(holidays)
            
            return holidays
            
        except Exception as e:
            st.warning(f"Could not fetch holidays from Google Calendar: {str(e)}")
            return self._get_cached_holidays()
    
    def _cache_holidays(self, holidays: List[Dict]):
        """Cache holidays to local file"""
        try:
            cache_data = {
                'holidays': holidays,
                'last_updated': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
            }
            
            with open(self.calendar_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
        except Exception as e:
            st.warning(f"Could not cache holidays: {str(e)}")
    
    def _get_cached_holidays(self) -> List[Dict]:
        """Get holidays from cache"""
        try:
            if not os.path.exists(self.calendar_cache_file):
                return self._get_default_holidays()
            
            with open(self.calendar_cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is expired
            expires_at = datetime.fromisoformat(cache_data['expires_at'])
            if datetime.now() > expires_at:
                st.info("Holiday cache expired. Using default holidays.")
                return self._get_default_holidays()
            
            return cache_data.get('holidays', [])
            
        except Exception as e:
            st.warning(f"Could not load cached holidays: {str(e)}")
            return self._get_default_holidays()
    
    def _get_default_holidays(self) -> List[Dict]:
        """Get default Indian holidays for current year"""
        current_year = datetime.now().year
        
        # Common Indian holidays (approximate dates)
        default_holidays = [
            {'date': f'{current_year}-01-26', 'name': 'Republic Day', 'source': 'default'},
            {'date': f'{current_year}-08-15', 'name': 'Independence Day', 'source': 'default'},
            {'date': f'{current_year}-10-02', 'name': 'Gandhi Jayanti', 'source': 'default'},
            {'date': f'{current_year}-12-25', 'name': 'Christmas Day', 'source': 'default'},
        ]
        
        return default_holidays
    
    def is_holiday_today(self, check_date: date = None) -> Tuple[bool, str]:
        """Check if today (or given date) is a holiday according to Google Calendar"""
        if check_date is None:
            check_date = date.today()
        
        holidays = self.get_holidays_from_calendar()
        date_str = check_date.strftime('%Y-%m-%d')
        
        for holiday in holidays:
            if holiday['date'] == date_str:
                return True, holiday['name']
        
        return False, ""
    
    def get_upcoming_holidays(self, days_ahead: int = 30) -> List[Dict]:
        """Get upcoming holidays"""
        holidays = self.get_holidays_from_calendar(days_ahead=days_ahead)
        current_date = date.today()
        end_date = current_date + timedelta(days=days_ahead)
        
        upcoming = []
        for holiday in holidays:
            holiday_date = datetime.strptime(holiday['date'], '%Y-%m-%d').date()
            if current_date <= holiday_date <= end_date:
                upcoming.append(holiday)
        
        # Sort by date
        upcoming.sort(key=lambda x: x['date'])
        return upcoming
    
    def get_next_holiday(self) -> Optional[Dict]:
        """Get the next upcoming holiday"""
        upcoming = self.get_upcoming_holidays(days_ahead=365)
        return upcoming[0] if upcoming else None
    
    def refresh_holiday_cache(self) -> Tuple[bool, str]:
        """Manually refresh holiday cache"""
        try:
            if not GOOGLE_CALENDAR_AVAILABLE or not self.service:
                return False, "Google Calendar service not available"
            
            holidays = self.get_holidays_from_calendar()
            return True, f"Holiday cache refreshed. Found {len(holidays)} holidays."
            
        except Exception as e:
            return False, f"Error refreshing cache: {str(e)}"
    
    def get_calendar_status(self) -> Dict:
        """Get status of calendar integration"""
        status = {
            'google_calendar_available': GOOGLE_CALENDAR_AVAILABLE,
            'service_initialized': self.service is not None,
            'credentials_exist': os.path.exists(self.credentials_file),
            'token_exists': os.path.exists(self.token_file),
            'cache_exists': os.path.exists(self.calendar_cache_file)
        }
        
        if status['cache_exists']:
            try:
                with open(self.calendar_cache_file, 'r') as f:
                    cache_data = json.load(f)
                status['cache_last_updated'] = cache_data.get('last_updated', 'Unknown')
                status['cache_expires_at'] = cache_data.get('expires_at', 'Unknown')
                status['cached_holidays_count'] = len(cache_data.get('holidays', []))
            except:
                status['cache_status'] = 'Error reading cache'
        
        return status
    
    def test_calendar_connection(self) -> Tuple[bool, str]:
        """Test Google Calendar connection"""
        try:
            if not GOOGLE_CALENDAR_AVAILABLE:
                return False, "Google Calendar libraries not installed"
            
            if not self.service:
                return False, "Google Calendar service not initialized"
            
            # Try to fetch a small number of events
            now = datetime.utcnow()
            end_date = now + timedelta(days=7)
            
            events_result = self.service.events().list(
                calendarId='en.indian#holiday@group.v.calendar.google.com',
                timeMin=now.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                maxResults=1,
                singleEvents=True
            ).execute()
            
            return True, "Google Calendar connection successful"
            
        except Exception as e:
            return False, f"Google Calendar connection failed: {str(e)}"
