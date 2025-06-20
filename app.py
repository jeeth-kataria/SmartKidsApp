import streamlit as st
import cv2
import numpy as np
from datetime import datetime, date, time, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import io
import base64
import os

# Import custom modules
from csv_manager import CSVManager
from face_recognition_utils import FaceRecognitionSystem
from time_manager import TimeManager
from calendar_integration import CalendarIntegration
from excel_interface import excel_automation_interface

# Page configuration
st.set_page_config(
    page_title="Smart Kids Attendance - Teacher Face Recognition",
    page_icon="👨‍🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'csv_manager' not in st.session_state:
    st.session_state.csv_manager = CSVManager()

if 'face_system' not in st.session_state:
    st.session_state.face_system = FaceRecognitionSystem()

if 'time_manager' not in st.session_state:
    st.session_state.time_manager = TimeManager()

if 'calendar_integration' not in st.session_state:
    st.session_state.calendar_integration = CalendarIntegration()

if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .status-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
    
    .success-card {
        background: #d4edda;
        border-left-color: #28a745;
    }
    
    .warning-card {
        background: #fff3cd;
        border-left-color: #ffc107;
    }
    
    .error-card {
        background: #f8d7da;
        border-left-color: #dc3545;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Utility function to ensure single date/time

def ensure_single_date(val, fallback):
    if isinstance(val, (tuple, list)):
        return val[0] if val else fallback
    return val

def ensure_single_time(val, fallback):
    if isinstance(val, (tuple, list)):
        return val[0] if val else fallback
    return val

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎓 Smart Kids Attendance System</h1>
        <h3>Teacher Face Recognition Portal</h3>
    </div>
    """, unsafe_allow_html=True)

    # Check if face recognition is available
    try:
        import face_recognition
        face_recognition_available = True
    except ImportError:
        face_recognition_available = False
        st.warning("⚠️ **Demo Mode**: Face recognition is disabled in this deployment. Download and run locally for full functionality.")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "Live Attendance", "Teacher Management", "Reports", "Excel Automation", "Settings", "System Status"]
    )
    
    # Load face encodings for recognition
    teachers_df = st.session_state.csv_manager.get_all_teachers()
    if not teachers_df.empty:
        face_encodings = st.session_state.csv_manager.get_teacher_face_encodings()
        teacher_names = dict(zip(teachers_df['ID'], teachers_df['Name']))
        st.session_state.face_system.load_known_faces(face_encodings, teacher_names)
    
    # Route to different pages
    if page == "Dashboard":
        show_dashboard()
    elif page == "Live Attendance":
        show_live_attendance()
    elif page == "Teacher Management":
        show_teacher_management()
    elif page == "Reports":
        show_reports()
    elif page == "Excel Automation":
        show_excel_automation()
    elif page == "Settings":
        show_settings()
    elif page == "System Status":
        show_system_status()

def show_dashboard():
    st.header("📊 Dashboard")
    
    # Get attendance status
    status = st.session_state.time_manager.get_attendance_status()
    
    # Status cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if status.get('can_mark_attendance', False):
            st.markdown("""
            <div class="status-card success-card">
                <h4>✅ System Active</h4>
                <p>Attendance window is open</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-card warning-card">
                <h4>⏰ System Inactive</h4>
                <p>Outside attendance window</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        current_time = status.get('current_time', datetime.now())
        st.markdown(f"""
        <div class="status-card">
            <h4>🕐 Current Time</h4>
            <p>{current_time.strftime('%H:%M:%S')}</p>
            <small>{current_time.strftime('%Y-%m-%d')}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Timeslot indicator
        current_start = st.session_state.time_manager.start_time
        current_end = st.session_state.time_manager.end_time
        st.markdown(f"""
        <div class="status-card">
            <h4>⏰ Attendance Window</h4>
            <p>{current_start.strftime('%H:%M')} - {current_end.strftime('%H:%M')}</p>
            <small>Daily timing</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        is_valid_day = status.get('is_valid_day', True)
        day_reason = status.get('day_reason', 'Regular day')
        
        if is_valid_day:
            st.markdown(f"""
            <div class="status-card success-card">
                <h4>📅 Working Day</h4>
                <p>{day_reason}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="status-card error-card">
                <h4>🏖️ Non-Working Day</h4>
                <p>{day_reason}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Quick timeslot change button
    if st.button("⚙️ Change Attendance Time", type="secondary"):
        st.switch_page("Settings")
    
    # Statistics
    st.subheader("📈 Statistics")
    stats = st.session_state.csv_manager.get_teacher_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Teachers", stats.get('total_teachers', 0))
    
    with col2:
        st.metric("Today's Attendance", stats.get('today_attendance', 0))
    
    with col3:
        st.metric("This Month", stats.get('this_month_attendance', 0))
    
    with col4:
        st.metric("Total Records", stats.get('total_attendance_records', 0))
    
    # Today's attendance
    st.subheader("📋 Today's Attendance")
    today_attendance = st.session_state.csv_manager.get_today_attendance()
    
    if not today_attendance.empty:
        st.dataframe(
            today_attendance[['Name', 'Time_In', 'Recognition_Confidence']],
            use_container_width=True
        )
    else:
        st.info("No attendance records for today")
    
    # Upcoming holidays
    st.subheader("🎉 Upcoming Holidays")
    upcoming_holidays = st.session_state.time_manager.get_upcoming_manual_holidays()
    calendar_holidays = st.session_state.calendar_integration.get_upcoming_holidays()
    
    all_holidays = upcoming_holidays + calendar_holidays
    
    if all_holidays:
        for holiday in all_holidays[:5]:  # Show next 5 holidays
            holiday_date = datetime.strptime(holiday['date'], '%Y-%m-%d').date()
            days_until = (holiday_date - date.today()).days
            
            if days_until >= 0:
                st.info(f"🎊 **{holiday['name']}** - {holiday_date.strftime('%B %d, %Y')} ({days_until} days)")
    else:
        st.info("No upcoming holidays found")

def show_live_attendance():
    st.header("📹 Live Attendance")
    
    # Check if system is active
    status = st.session_state.time_manager.get_attendance_status()
    
    if not status.get('can_mark_attendance', False):
        st.warning(f"⚠️ Attendance system is currently inactive: {status.get('window_reason', 'Unknown reason')}")
        
        if not status.get('is_valid_day', True):
            st.error(f"Today is not a working day: {status.get('day_reason', 'Unknown reason')}")
            return
        
        # Show time information
        if 'time_until_start' in status and status['time_until_start']:
            st.info(f"⏰ Attendance window opens in: {status['time_until_start']}")
        
        if 'time_remaining' in status and status['time_remaining']:
            st.info(f"⏱️ Time remaining in window: {status['time_remaining']}")
    
    # Camera controls
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("🎥 Start Camera", disabled=not status.get('can_mark_attendance', False)):
            st.session_state.camera_active = True
        
        if st.button("⏹️ Stop Camera"):
            st.session_state.camera_active = False
        
        # Confidence threshold
        confidence_threshold = st.slider(
            "Recognition Confidence",
            min_value=0.3,
            max_value=0.9,
            value=0.6,
            step=0.05
        )
        st.session_state.face_system.set_confidence_threshold(confidence_threshold)
    
    with col1:
        if st.session_state.camera_active and status.get('can_mark_attendance', False):
            # Camera placeholder
            camera_placeholder = st.empty()
            
            # This is a placeholder for camera integration
            # In a real implementation, you would use streamlit-webrtc or similar
            st.info("📷 Camera feed would appear here. Use streamlit-webrtc for real camera integration.")
            
            # Simulate face detection for demo
            if st.button("🔍 Simulate Face Detection"):
                st.success("Face detected! Processing...")
                # Here you would process the actual camera frame
        else:
            st.info("Camera is inactive. Start camera when attendance window is open.")
    
    # Recent attendance
    st.subheader("📝 Recent Attendance")
    recent_attendance = st.session_state.csv_manager.get_today_attendance()
    
    if not recent_attendance.empty:
        st.dataframe(recent_attendance, use_container_width=True)
    else:
        st.info("No attendance records today")

def show_teacher_management():
    st.header("👥 Teacher Management")
    
    tab1, tab2, tab3 = st.tabs(["Add Teacher", "View Teachers", "Manage Teachers"])
    
    with tab1:
        st.subheader("➕ Add New Teacher")
        
        with st.form("add_teacher_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                teacher_id = st.text_input("Teacher ID*", placeholder="T001")
                teacher_name = st.text_input("Full Name*", placeholder="John Doe")
            
            with col2:
                department = st.selectbox(
                    "Department*",
                    ["Mathematics", "Science", "English", "Social Studies", "Arts", "Physical Education", "Other"]
                )
                email = st.text_input("Email", placeholder="teacher@school.com")
            
            st.subheader("📸 Upload Photos")
            st.info("Upload 3-5 clear photos of the teacher for better recognition accuracy")
            
            uploaded_files = st.file_uploader(
                "Choose photos",
                type=['jpg', 'jpeg', 'png'],
                accept_multiple_files=True
            )
            
            submitted = st.form_submit_button("Add Teacher")
            
            if submitted:
                if not teacher_id or not teacher_name or not department:
                    st.error("Please fill all required fields")
                elif not uploaded_files:
                    st.error("Please upload at least one photo")
                elif len(uploaded_files) < 2:
                    st.error("Please upload at least 2 photos for better accuracy")
                else:
                    # Process images
                    with st.spinner("Processing images..."):
                        success, processed_images, message = st.session_state.face_system.process_uploaded_images(uploaded_files)
                    
                    if success:
                        # Generate average face encoding
                        face_encodings = []
                        for img in processed_images:
                            encoding = st.session_state.face_system.encode_face(img)
                            if encoding is not None:
                                face_encodings.append(encoding)
                        
                        if face_encodings:
                            average_encoding = np.mean(face_encodings, axis=0)
                            
                            # Add to database
                            success, db_message = st.session_state.csv_manager.add_teacher(
                                teacher_id, teacher_name, department, average_encoding, email
                            )
                            
                            if success:
                                st.success(f"✅ {db_message}")
                                st.balloons()
                            else:
                                st.error(f"❌ {db_message}")
                        else:
                            st.error("Could not generate face encodings from uploaded images")
                    else:
                        st.error(f"❌ {message}")
    
    with tab2:
        st.subheader("👀 View All Teachers")
        
        teachers_df = st.session_state.csv_manager.get_all_teachers()
        
        if not teachers_df.empty:
            # Filter active teachers
            active_teachers = teachers_df[teachers_df['Status'] == 'Active']
            
            if not active_teachers.empty:
                st.dataframe(
                    active_teachers[['ID', 'Name', 'Department', 'Registration_Date', 'Email']],
                    use_container_width=True
                )
                
                st.metric("Total Active Teachers", len(active_teachers))
            else:
                st.info("No active teachers found")
        else:
            st.info("No teachers registered yet")
    
    with tab3:
        st.subheader("⚙️ Manage Teachers")
        
        teachers_df = st.session_state.csv_manager.get_all_teachers()
        
        if not teachers_df.empty:
            active_teachers = teachers_df[teachers_df['Status'] == 'Active']
            
            if not active_teachers.empty:
                selected_teacher = st.selectbox(
                    "Select Teacher",
                    options=active_teachers['ID'].tolist(),
                    format_func=lambda x: f"{x} - {active_teachers[active_teachers['ID'] == x]['Name'].iloc[0]}"
                )
                
                if selected_teacher:
                    teacher_info = active_teachers[active_teachers['ID'] == selected_teacher].iloc[0]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.info(f"**Name:** {teacher_info['Name']}")
                        st.info(f"**Department:** {teacher_info['Department']}")
                        st.info(f"**Registration Date:** {teacher_info['Registration_Date']}")
                    
                    with col2:
                        if st.button("🗑️ Delete Teacher", type="secondary"):
                            if st.checkbox("I confirm deletion"):
                                success, message = st.session_state.csv_manager.delete_teacher(selected_teacher)
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
            else:
                st.info("No active teachers to manage")
        else:
            st.info("No teachers registered yet")

def show_reports():
    st.header("📊 Reports & Analytics")
    
    # Create tabs for different report types
    tab1, tab2, tab3 = st.tabs(["📈 Analytics", "📁 Daily Files", "📥 Export"])
    
    with tab1:
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
            start_date = ensure_single_date(start_date, date.today() - timedelta(days=30))
            if start_date is None:
                start_date = date.today() - timedelta(days=30)
        with col2:
            end_date = st.date_input("End Date", value=date.today())
            end_date = ensure_single_date(end_date, date.today())
            if end_date is None:
                end_date = date.today()
        
        if start_date > end_date:
            st.error("Start date must be before end date")
            return
        
        # Get attendance data
        attendance_df = st.session_state.csv_manager.get_attendance_by_date_range(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        if attendance_df.empty:
            st.info("No attendance data found for the selected date range")
            return
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", len(attendance_df))
        
        with col2:
            unique_teachers = attendance_df['Teacher_ID'].nunique()
            st.metric("Unique Teachers", unique_teachers)
        
        with col3:
            avg_confidence = attendance_df['Recognition_Confidence'].mean()
            st.metric("Avg Confidence", f"{avg_confidence:.2f}")
        
        with col4:
            working_days = len(attendance_df['Date'].unique())
            st.metric("Working Days", working_days)
        
        # Charts
        st.subheader("📈 Attendance Trends")
        
        # Daily attendance chart
        daily_counts = attendance_df.groupby('Date').size().reset_index(name='Count')
        daily_counts['Date'] = pd.to_datetime(daily_counts['Date'])
        
        fig_daily = px.line(
            daily_counts,
            x='Date',
            y='Count',
            title='Daily Attendance Count',
            markers=True
        )
        st.plotly_chart(fig_daily, use_container_width=True)
        
        # Teacher-wise attendance
        teacher_counts = attendance_df.groupby('Name').size().reset_index(name='Days_Present')
        
        fig_teachers = px.bar(
            teacher_counts,
            x='Name',
            y='Days_Present',
            title='Teacher-wise Attendance',
            color='Days_Present'
        )
        st.plotly_chart(fig_teachers, use_container_width=True)
    
    with tab2:
        st.subheader("📁 Daily Attendance Files")
        st.info("📝 Each day's attendance is stored in a separate CSV file (dd-mm-yyyy.csv)")
        
        # Get daily files information
        files_info = st.session_state.csv_manager.get_daily_files_info()
        
        if not files_info:
            st.info("No daily attendance files found")
        else:
            # Show files in a table
            st.write(f"**Found {len(files_info)} daily attendance files:**")
            
            # Create a DataFrame for display
            display_data = []
            for file_info in files_info:
                display_data.append({
                    'Date': file_info['date'],
                    'Filename': file_info['filename'],
                    'Records': file_info['record_count'],
                    'Size (KB)': round(file_info['file_size'] / 1024, 2),
                    'Modified': file_info['modified_time'].strftime('%Y-%m-%d %H:%M')
                })
            
            files_df = pd.DataFrame(display_data)
            st.dataframe(files_df, use_container_width=True)
            
            # Download individual files
            st.subheader("📥 Download Daily Files")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Select date for download
                available_dates = [file_info['date'] for file_info in files_info]
                selected_date = st.selectbox(
                    "Select date to download:",
                    available_dates,
                    format_func=lambda x: datetime.strptime(x, '%Y-%m-%d').strftime('%d %B %Y')
                )
                
                if selected_date:
                    # Convert to date object
                    target_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
                    
                    # Get file for download
                    success, file_path = st.session_state.csv_manager.download_daily_file(target_date)
                    
                    if success:
                        # Read file content
                        with open(file_path, 'r') as f:
                            file_content = f.read()
                        
                        # Create download button
                        filename = f"{target_date.strftime('%d-%m-%Y')}.csv"
                        st.download_button(
                            label=f"📥 Download {filename}",
                            data=file_content,
                            file_name=filename,
                            mime="text/csv"
                        )
                        
                        # Show file preview
                        st.write("**File Preview:**")
                        df_preview = pd.read_csv(file_path)
                        st.dataframe(df_preview.head(10), use_container_width=True)
                    else:
                        st.error(file_path)  # file_path contains error message
            
            with col2:
                # Bulk download options
                st.write("**Bulk Download Options:**")
                
                # Download all files as ZIP
                if st.button("📦 Download All Files (ZIP)"):
                    st.info("📝 ZIP download functionality coming soon...")
                
                # Download last 7 days
                if st.button("📅 Download Last 7 Days"):
                    st.info("📝 Batch download functionality coming soon...")
                
                # Download this month
                if st.button("📆 Download This Month"):
                    st.info("📝 Monthly download functionality coming soon...")
    
    with tab3:
        st.subheader("📥 Export Data")
        
        # Date range for export
        col1, col2 = st.columns(2)
        with col1:
            export_start = st.date_input("Export Start Date", value=date.today() - timedelta(days=30), key="export_start")
            export_start = ensure_single_date(export_start, date.today() - timedelta(days=30))
            if export_start is None:
                export_start = date.today() - timedelta(days=30)
        with col2:
            export_end = st.date_input("Export End Date", value=date.today(), key="export_end")
            export_end = ensure_single_date(export_end, date.today())
            if export_end is None:
                export_end = date.today()
        
        if export_start > export_end:
            st.error("Start date must be before end date")
            return
        
        # Get data for export
        export_df = st.session_state.csv_manager.get_attendance_by_date_range(
            export_start.strftime('%Y-%m-%d'),
            export_end.strftime('%Y-%m-%d')
        )
        
        if export_df.empty:
            st.info("No data found for export in the selected date range")
            return
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Download Excel Report"):
                # Create Excel file
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:  # type: ignore
                    export_df.to_excel(writer, sheet_name='Attendance', index=False)
                    
                    # Add summary sheets
                    daily_counts = export_df.groupby('Date').size().reset_index(name='Count')
                    daily_counts.to_excel(writer, sheet_name='Daily_Summary', index=False)
                    
                    teacher_counts = export_df.groupby('Name').size().reset_index(name='Days_Present')
                    teacher_counts.to_excel(writer, sheet_name='Teacher_Summary', index=False)
                
                st.download_button(
                    label="📥 Download Excel",
                    data=output.getvalue(),
                    file_name=f"attendance_report_{export_start}_{export_end}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        with col2:
            if st.button("📄 Download CSV"):
                csv = export_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"attendance_data_{export_start}_{export_end}.csv",
                    mime="text/csv"
                )
        
        # Show export summary
        st.write("**Export Summary:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Records to Export", len(export_df))
        
        with col2:
            st.metric("Date Range", f"{export_start} to {export_end}")
        
        with col3:
            st.metric("File Size (est.)", f"{len(export_df) * 100:.0f} bytes")

def show_settings():
    st.header("⚙️ Settings")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Time Settings", "Holiday Management", "System Config", "Google Calendar", "CSV Storage"])
    
    with tab1:
        st.subheader("⏰ Attendance Time Window")
        
        current_start = st.session_state.time_manager.start_time
        current_end = st.session_state.time_manager.end_time
        
        # Current status display
        st.write("**Current Settings**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Start Time", current_start.strftime('%H:%M'))
        
        with col2:
            st.metric("End Time", current_end.strftime('%H:%M'))
        
        with col3:
            duration = (current_end.hour * 60 + current_end.minute) - (current_start.hour * 60 + current_start.minute)
            st.metric("Duration", f"{duration} minutes")
        
        # Quick presets for common scenarios
        st.write("**Quick Presets**")
        st.info("💡 Use these presets for common school timing scenarios")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🕘 Standard (9:00-9:30)", type="secondary"):
                new_start = time(9, 0)
                new_end = time(9, 30)
                success, message = st.session_state.time_manager.update_time_window(new_start, new_end)
                if success:
                    st.success("✅ Updated to Standard timing")
                    st.rerun()
                else:
                    st.error(message)
        
        with col2:
            if st.button("🕙 Late Start (10:00-10:30)", type="secondary"):
                new_start = time(10, 0)
                new_end = time(10, 30)
                success, message = st.session_state.time_manager.update_time_window(new_start, new_end)
                if success:
                    st.success("✅ Updated to Late Start timing")
                    st.rerun()
                else:
                    st.error(message)
        
        with col3:
            if st.button("🕗 Early (8:00-8:30)", type="secondary"):
                new_start = time(8, 0)
                new_end = time(8, 30)
                success, message = st.session_state.time_manager.update_time_window(new_start, new_end)
                if success:
                    st.success("✅ Updated to Early timing")
                    st.rerun()
                else:
                    st.error(message)
        
        with col4:
            if st.button("🕚 Extended (9:00-10:00)", type="secondary"):
                new_start = time(9, 0)
                new_end = time(10, 0)
                success, message = st.session_state.time_manager.update_time_window(new_start, new_end)
                if success:
                    st.success("✅ Updated to Extended timing")
                    st.rerun()
                else:
                    st.error(message)
        
        # Custom time settings
        st.write("**Custom Time Settings**")
        st.info("🎛️ Set custom start and end times for your specific needs")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            new_start_time = st.time_input(
                "Start Time", 
                value=current_start,
                help="When teachers can start marking attendance"
            )
            new_start_time = ensure_single_time(new_start_time, current_start)
            if new_start_time is None:
                new_start_time = current_start
        
        with col2:
            new_end_time = st.time_input(
                "End Time", 
                value=current_end,
                help="When attendance window closes"
            )
            new_end_time = ensure_single_time(new_end_time, current_end)
            if new_end_time is None:
                new_end_time = current_end
        
        with col3:
            st.write("")  # Spacer
            st.write("")  # Spacer
            if st.button("🔄 Update Time Window", type="primary"):
                if new_start_time >= new_end_time:
                    st.error("❌ Start time must be before end time")
                else:
                    success, message = st.session_state.time_manager.update_time_window(new_start_time, new_end_time)
                    if success:
                        st.success("✅ Time window updated successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
        
        # Time window validation and info
        if new_start_time < new_end_time:
            duration_minutes = (new_end_time.hour * 60 + new_end_time.minute) - (new_start_time.hour * 60 + new_start_time.minute)
            
            st.write("**Preview**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.info(f"**Start:** {new_start_time.strftime('%H:%M')}")
            
            with col2:
                st.info(f"**End:** {new_end_time.strftime('%H:%M')}")
            
            with col3:
                st.info(f"**Duration:** {duration_minutes} minutes")
            
            # Late threshold calculation (10 minutes after start)
            late_threshold = time(
                new_start_time.hour,
                min(new_start_time.minute + 10, 59)
            )
            if new_start_time.minute + 10 >= 60:
                late_threshold = time(new_start_time.hour + 1, (new_start_time.minute + 10) % 60)
            
            st.info(f"📝 **Late threshold:** {late_threshold.strftime('%H:%M')} (10 minutes after start time)")
        
        # Current attendance status
        st.write("**Current Attendance Status**")
        status = st.session_state.time_manager.get_attendance_status()
        
        if status.get('can_mark_attendance', False):
            st.success("✅ **Attendance window is currently OPEN**")
            st.info(f"Teachers can mark attendance until {current_end.strftime('%H:%M')}")
        else:
            st.warning("⏰ **Attendance window is currently CLOSED**")
            if status.get('is_valid_day', True):
                st.info(f"Next attendance window: {current_start.strftime('%H:%M')} - {current_end.strftime('%H:%M')}")
            else:
                st.info(f"Today is a non-working day: {status.get('day_reason', 'Holiday')}")
        
        # Time zone information
        st.write("**Time Zone Information**")
        st.info("🌍 **Current time zone:** Asia/Kolkata (IST)")
        st.info("🕐 **Current time:** " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Help section
        with st.expander("📖 Time Window Help"):
            st.markdown("""
            ### ⏰ **Attendance Time Window Guide**
            
            **🎯 Purpose:**
            The attendance time window defines when teachers can mark their attendance using face recognition.
            
            **📅 How it works:**
            - Teachers can only mark attendance during the specified time window
            - Attendance is marked as "Late" if done 10+ minutes after start time
            - Outside the window, attendance marking is disabled
            
            **🕘 Common Scenarios:**
            - **Standard (9:00-9:30):** Regular school timing
            - **Late Start (10:00-10:30):** When school starts late
            - **Early (8:00-8:30):** Early morning sessions
            - **Extended (9:00-10:00):** Longer attendance window
            
            **⚙️ Custom Settings:**
            - Set any start and end time you need
            - Minimum 5 minutes duration recommended
            - Maximum 4 hours duration allowed
            
            **📝 Late Policy:**
            - Teachers marked as "Late" if attendance is 10+ minutes after start time
            - Late threshold is automatically calculated
            - Late attendance is still recorded but flagged
            
            **🔄 Updates:**
            - Time changes take effect immediately
            - No restart required
            - Changes are saved permanently
            """)
    
    with tab2:
        st.subheader("🎉 Manual Holiday Management")
        
        # Add holiday
        st.write("**Add New Holiday**")
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            holiday_date = st.date_input("Holiday Date", min_value=date.today())
            holiday_date = ensure_single_date(holiday_date, date.today())
        
        with col2:
            holiday_name = st.text_input("Holiday Name", placeholder="e.g., Diwali")
        
        with col3:
            if st.button("Add Holiday"):
                if holiday_name:
                    success, message = st.session_state.time_manager.add_manual_holiday(holiday_date, holiday_name)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter holiday name")
        
        # List existing holidays
        st.write("**Existing Manual Holidays**")
        manual_holidays = st.session_state.time_manager.get_upcoming_manual_holidays(days_ahead=365)
        
        if manual_holidays:
            for holiday in manual_holidays:
                col1, col2, col3 = st.columns([2, 3, 1])
                
                with col1:
                    st.write(holiday['date'])
                
                with col2:
                    st.write(holiday['name'])
                
                with col3:
                    if st.button("Remove", key=f"remove_{holiday['date']}"):
                        holiday_date_obj = datetime.strptime(holiday['date'], '%Y-%m-%d').date()
                        success, message = st.session_state.time_manager.remove_manual_holiday(holiday_date_obj)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
        else:
            st.info("No manual holidays added")
    
    with tab3:
        st.subheader("🔧 System Configuration")
        
        # Face recognition settings
        st.write("**Face Recognition Settings**")
        
        current_threshold = st.session_state.face_system.confidence_threshold
        new_threshold = st.slider(
            "Recognition Confidence Threshold",
            min_value=0.3,
            max_value=0.9,
            value=current_threshold,
            step=0.05,
            help="Higher values require more confident matches"
        )
        
        if new_threshold != current_threshold:
            st.session_state.face_system.set_confidence_threshold(new_threshold)
            st.success("Confidence threshold updated")
        
        # Backup settings
        st.write("**Data Backup**")
        
        if st.button("🔄 Create Backup"):
            with st.spinner("Creating backup..."):
                success = st.session_state.csv_manager.backup_data()
            
            if success:
                st.success("Backup created successfully")
            else:
                st.error("Backup failed")
    
    with tab4:
        st.subheader("📅 Google Calendar Integration")
        
        calendar_status = st.session_state.calendar_integration.get_calendar_status()
        
        # Status display
        st.write("**Integration Status**")
        
        status_items = [
            ("Google Calendar Libraries", calendar_status.get('google_calendar_available', False)),
            ("Service Initialized", calendar_status.get('service_initialized', False)),
            ("Credentials File", calendar_status.get('credentials_exist', False)),
            ("Token File", calendar_status.get('token_exists', False)),
            ("Holiday Cache", calendar_status.get('cache_exists', False))
        ]
        
        for item, status in status_items:
            icon = "✅" if status else "❌"
            st.write(f"{icon} {item}")
        
        # Upload credentials
        st.write("**Setup Google Calendar**")
        
        uploaded_creds = st.file_uploader(
            "Upload Google Calendar credentials.json",
            type=['json'],
            help="Download from Google Cloud Console"
        )
        
        if uploaded_creds:
            if st.button("Setup Credentials"):
                content = uploaded_creds.read().decode('utf-8')
                success, message = st.session_state.calendar_integration.setup_credentials(content)
                
                if success:
                    st.success(message)
                else:
                    st.error(message)
        
        # Test connection
        if st.button("🔍 Test Calendar Connection"):
            with st.spinner("Testing connection..."):
                success, message = st.session_state.calendar_integration.test_calendar_connection()
            
            if success:
                st.success(message)
            else:
                st.error(message)
        
        # Refresh cache
        if st.button("🔄 Refresh Holiday Cache"):
            with st.spinner("Refreshing holiday cache..."):
                success, message = st.session_state.calendar_integration.refresh_holiday_cache()
            
            if success:
                st.success(message)
            else:
                st.error(message)
    
    with tab5:
        st.subheader("📊 CSV Storage Management")
        
        # Storage status
        st.write("**Storage Status**")
        
        # Get storage info
        teachers_df = st.session_state.csv_manager.get_all_teachers()
        files_info = st.session_state.csv_manager.get_daily_files_info()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Teachers", len(teachers_df))
        
        with col2:
            st.metric("Daily Files", len(files_info))
        
        with col3:
            total_records = sum(file_info['record_count'] for file_info in files_info)
            st.metric("Total Records", total_records)
        
        # File structure info
        st.write("**File Structure**")
        st.info("""
        📁 **Data Organization:**
        - `data/teachers.csv` - All teacher information
        - `data/daily_attendance/` - Daily attendance files (dd-mm-yyyy.csv)
        - `face_encodings/` - Teacher face encoding files
        - `data/backups/` - Automatic backup files
        """)
        
        # Show recent files
        if files_info:
            st.write("**Recent Daily Files:**")
            recent_files = files_info[:5]  # Show last 5 files
            
            for file_info in recent_files:
                col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                
                with col1:
                    st.write(f"📄 {file_info['filename']}")
                
                with col2:
                    st.write(f"{file_info['record_count']} records")
                
                with col3:
                    st.write(f"{round(file_info['file_size'] / 1024, 1)} KB")
                
                with col4:
                    st.write(file_info['modified_time'].strftime('%Y-%m-%d %H:%M'))
        
        # Storage actions
        st.write("**Storage Actions**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Create Backup"):
                with st.spinner("Creating backup..."):
                    success = st.session_state.csv_manager.backup_data()
                
                if success:
                    st.success("✅ Backup created successfully")
                else:
                    st.error("❌ Backup failed")
            
            if st.button("📊 Download Teachers CSV"):
                if not teachers_df.empty:
                    csv = teachers_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Teachers CSV",
                        data=csv,
                        file_name="teachers.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No teachers data to download")
        
        with col2:
            if st.button("🗑️ Clear Old Files"):
                st.info("📝 File cleanup functionality coming soon...")
            
            if st.button("📈 Storage Statistics"):
                st.info("📝 Detailed statistics coming soon...")
        
        # Benefits section
        with st.expander("📖 CSV Storage Benefits"):
            st.markdown("""
            ### ✅ **Advantages of CSV Storage:**
            
            **🎯 Perfect for Streamlit Cloud:**
            - ✅ **No data loss** - Files are created fresh each day
            - ✅ **Organized by date** - Easy to find specific day's data
            - ✅ **Downloadable** - Users can save files locally
            - ✅ **Familiar format** - CSV is widely supported
            
            **📁 File Organization:**
            - Each day gets its own file: `20-12-2024.csv`
            - Teachers stored in: `teachers.csv`
            - Face encodings in: `face_encodings/` folder
            - Automatic backups in: `data/backups/`
            
            **💾 Storage Benefits:**
            - ✅ **Free storage** - No cloud costs
            - ✅ **Local control** - Users own their data
            - ✅ **Easy sharing** - Send CSV files via email
            - ✅ **Excel compatible** - Open in Excel/Google Sheets
            - ✅ **Backup friendly** - Simple file copying
            
            **🔒 Privacy & Security:**
            - ✅ **No cloud storage** - Data stays local
            - ✅ **No third-party access** - Complete privacy
            - ✅ **User control** - Download and manage files
            - ✅ **No data mining** - No analytics on your data
            """)

def show_system_status():
    st.header("🔍 System Status")
    
    # Overall system health
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Database status
        try:
            teachers_count = len(st.session_state.csv_manager.get_all_teachers())
            st.metric("Database", "✅ Healthy", f"{teachers_count} teachers")
        except Exception as e:
            st.metric("Database", "❌ Error", str(e))
    
    with col2:
        # Face recognition status
        try:
            encodings_count = len(st.session_state.csv_manager.get_teacher_face_encodings())
            st.metric("Face Recognition", "✅ Ready", f"{encodings_count} encodings")
        except Exception as e:
            st.metric("Face Recognition", "❌ Error", str(e))
    
    with col3:
        # Time management status
        status = st.session_state.time_manager.get_attendance_status()
        if status.get('can_mark_attendance', False):
            st.metric("Time System", "✅ Active", "In window")
        else:
            st.metric("Time System", "⏰ Inactive", "Outside window")
    
    # Detailed status
    st.subheader("📋 Detailed Status")
    
    # File system status
    st.write("**File System**")
    
    files_to_check = [
        ("Teachers Database", "data/teachers.xlsx"),
        ("Attendance Database", "data/attendance.xlsx"),
        ("Manual Holidays", "data/manual_holidays.json"),
        ("Time Settings", "data/time_settings.json")
    ]
    
    for name, path in files_to_check:
        exists = os.path.exists(path)
        icon = "✅" if exists else "❌"
        st.write(f"{icon} {name}: {path}")
    
    # Calendar integration status
    st.write("**Calendar Integration**")
    calendar_status = st.session_state.calendar_integration.get_calendar_status()
    
    for key, value in calendar_status.items():
        if isinstance(value, bool):
            icon = "✅" if value else "❌"
            st.write(f"{icon} {key.replace('_', ' ').title()}")
        else:
            st.write(f"ℹ️ {key.replace('_', ' ').title()}: {value}")
    
    # System logs (placeholder)
    st.subheader("📝 Recent Activity")
    st.info("System logging would appear here in a production environment")

def show_excel_automation():
    """Show Excel automation interface"""
    excel_automation_interface()

if __name__ == "__main__":
    main()
