import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os
from excel_automation import ExcelAutomationManager
from database_manager import DatabaseManager
import io

def excel_automation_interface():
    """Streamlit interface for Excel automation features"""
    
    st.title("📊 Excel Automation System")
    st.markdown("---")
    
    # Initialize managers
    excel_manager = ExcelAutomationManager()
    db_manager = DatabaseManager()
    
    # Sidebar for navigation
    st.sidebar.title("Excel Operations")
    operation = st.sidebar.selectbox(
        "Choose Operation",
        [
            "📋 Create Templates",
            "📤 Export Reports", 
            "📥 Import Data",
            "📊 Generate Summary",
            "💾 Backup Files",
            "🔍 Validate Data",
            "📈 Statistics"
        ]
    )
    
    if operation == "📋 Create Templates":
        create_templates_section(excel_manager)
    elif operation == "📤 Export Reports":
        export_reports_section(excel_manager)
    elif operation == "📥 Import Data":
        import_data_section(excel_manager, db_manager)
    elif operation == "📊 Generate Summary":
        generate_summary_section(excel_manager)
    elif operation == "💾 Backup Files":
        backup_files_section(excel_manager)
    elif operation == "🔍 Validate Data":
        validate_data_section(excel_manager)
    elif operation == "📈 Statistics":
        statistics_section(excel_manager)

def create_templates_section(excel_manager):
    """Create Excel templates section"""
    st.header("📋 Create Excel Templates")
    st.markdown("Generate pre-formatted Excel templates for different purposes.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Available Templates")
        
        template_options = {
            "teachers": "👥 Teachers Template",
            "attendance": "📅 Attendance Template", 
            "bulk_import": "📦 Bulk Import Template",
            "report": "📊 Report Template"
        }
        
        selected_template = st.selectbox(
            "Select Template Type",
            list(template_options.keys()),
            format_func=lambda x: template_options[x]
        )
        
        if st.button("🔨 Create Template", type="primary"):
            with st.spinner("Creating template..."):
                success, message = excel_manager.create_excel_template(selected_template)
                
                if success:
                    st.success(message)
                    st.balloons()
                else:
                    st.error(message)
    
    with col2:
        st.subheader("Template Descriptions")
        
        descriptions = {
            "teachers": "📝 Pre-formatted template for adding teacher information with proper columns and sample data.",
            "attendance": "⏰ Template for attendance records with date, time, and status columns.",
            "bulk_import": "📋 Simplified template for importing multiple teachers at once.",
            "report": "📊 Comprehensive report template with multiple sheets for analysis."
        }
        
        st.info(descriptions.get(selected_template, "Select a template to see description."))
        
        # Show template preview
        if selected_template == "teachers":
            st.markdown("**Template Columns:**")
            st.code("ID | Name | Department | Registration_Date | Face_Encoding_Path | Status | Email")
        elif selected_template == "attendance":
            st.markdown("**Template Columns:**")
            st.code("Date | Teacher_ID | Name | Time_In | Status | Is_Holiday | Holiday_Name | Recognition_Confidence")
        elif selected_template == "bulk_import":
            st.markdown("**Template Columns:**")
            st.code("ID | Name | Department | Email | Notes")

def export_reports_section(excel_manager):
    """Export reports section"""
    st.header("📤 Export Attendance Reports")
    st.markdown("Generate comprehensive attendance reports in Excel format.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Report Parameters")
        
        # Date range selection
        start_date = st.date_input(
            "Start Date",
            value=date.today() - timedelta(days=30),
            max_value=date.today()
        )
        
        end_date = st.date_input(
            "End Date", 
            value=date.today(),
            max_value=date.today()
        )
        
        # Teacher selection
        try:
            teachers_df = pd.read_excel("data/teachers.xlsx")
            if not teachers_df.empty:
                teacher_options = teachers_df[teachers_df['Status'] == 'Active']['ID'].tolist()
                selected_teachers = st.multiselect(
                    "Select Teachers (leave empty for all)",
                    teacher_options,
                    help="Select specific teachers or leave empty to include all"
                )
            else:
                selected_teachers = []
                st.warning("No teachers found in database.")
        except:
            selected_teachers = []
            st.warning("Could not load teachers data.")
    
    with col2:
        st.subheader("Report Options")
        
        report_type = st.selectbox(
            "Report Type",
            ["Comprehensive", "Summary Only", "Raw Data Only"]
        )
        
        include_charts = st.checkbox("Include Charts", value=True)
        include_statistics = st.checkbox("Include Statistics", value=True)
        
        st.info(f"📅 Report Period: {start_date} to {end_date}")
        st.info(f"👥 Teachers: {'All' if not selected_teachers else len(selected_teachers)}")
    
    if st.button("📊 Generate Report", type="primary"):
        if start_date > end_date:
            st.error("Start date must be before end date.")
        else:
            with st.spinner("Generating report..."):
                success, message = excel_manager.export_attendance_report(
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d'),
                    selected_teachers if selected_teachers else None
                )
                
                if success:
                    st.success(message)
                    st.balloons()
                    
                    # Provide download link
                    report_path = message.split("to ")[-1]
                    if os.path.exists(report_path):
                        with open(report_path, "rb") as file:
                            st.download_button(
                                label="📥 Download Report",
                                data=file.read(),
                                file_name=os.path.basename(report_path),
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                else:
                    st.error(message)

def import_data_section(excel_manager, db_manager):
    """Import data section"""
    st.header("📥 Import Data from Excel")
    st.markdown("Import teachers or attendance data from Excel files.")
    
    tab1, tab2 = st.tabs(["👥 Import Teachers", "📅 Import Attendance"])
    
    with tab1:
        st.subheader("Import Teachers from Excel")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose Excel file",
            type=['xlsx', 'xls'],
            help="Upload an Excel file with teacher data"
        )
        
        if uploaded_file is not None:
            try:
                # Preview data
                df = pd.read_excel(uploaded_file)
                st.subheader("📋 Data Preview")
                st.dataframe(df.head())
                
                # Validate data
                with st.spinner("Validating data..."):
                    is_valid, validation_message, warnings = excel_manager.validate_excel_data(
                        uploaded_file, "teachers"
                    )
                
                if warnings:
                    st.warning(f"Warnings: {'; '.join(warnings)}")
                
                if is_valid:
                    st.success("✅ Data validation passed!")
                    
                    if st.button("📥 Import Teachers", type="primary"):
                        with st.spinner("Importing teachers..."):
                            # Save uploaded file temporarily
                            temp_path = f"temp_{uploaded_file.name}"
                            with open(temp_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            
                            try:
                                success, message, teachers_data = excel_manager.import_teachers_from_excel(temp_path)
                                
                                if success:
                                    # Add teachers to database
                                    imported_count = 0
                                    errors = []
                                    
                                    for teacher_data in teachers_data:
                                        # Note: Face encoding will be added later when photos are uploaded
                                        dummy_encoding = [0] * 128  # Placeholder
                                        
                                        db_success, db_message = db_manager.add_teacher(
                                            teacher_data['ID'],
                                            teacher_data['Name'],
                                            teacher_data['Department'],
                                            dummy_encoding,
                                            teacher_data['Email']
                                        )
                                        
                                        if db_success:
                                            imported_count += 1
                                        else:
                                            errors.append(f"{teacher_data['ID']}: {db_message}")
                                    
                                    if imported_count > 0:
                                        st.success(f"✅ Successfully imported {imported_count} teachers!")
                                        if errors:
                                            st.warning(f"Some errors occurred: {'; '.join(errors[:3])}")
                                    else:
                                        st.error("No teachers were imported.")
                                else:
                                    st.error(message)
                                    
                            finally:
                                # Clean up temp file
                                if os.path.exists(temp_path):
                                    os.remove(temp_path)
                else:
                    st.error(f"❌ Data validation failed: {validation_message}")
                    
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    
    with tab2:
        st.subheader("Import Attendance Data")
        st.info("📝 This feature allows importing historical attendance data.")
        
        # File upload for attendance
        attendance_file = st.file_uploader(
            "Choose Attendance Excel file",
            type=['xlsx', 'xls'],
            key="attendance_upload"
        )
        
        if attendance_file is not None:
            try:
                df = pd.read_excel(attendance_file)
                st.subheader("📋 Attendance Data Preview")
                st.dataframe(df.head())
                
                st.warning("⚠️ Attendance import functionality is under development.")
                
            except Exception as e:
                st.error(f"Error processing attendance file: {str(e)}")

def generate_summary_section(excel_manager):
    """Generate summary section"""
    st.header("📊 Generate Monthly Summary")
    st.markdown("Create comprehensive monthly attendance summaries.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Summary Parameters")
        
        # Month and year selection
        current_date = datetime.now()
        
        year = st.selectbox(
            "Year",
            range(current_date.year - 2, current_date.year + 1),
            index=2  # Current year
        )
        
        month = st.selectbox(
            "Month",
            range(1, 13),
            index=current_date.month - 1,
            format_func=lambda x: datetime(2024, x, 1).strftime('%B')
        )
        
        # Summary options
        include_charts = st.checkbox("Include Charts", value=True)
        include_statistics = st.checkbox("Include Detailed Statistics", value=True)
    
    with col2:
        st.subheader("Summary Preview")
        
        try:
            # Load data for preview
            attendance_df = pd.read_excel("data/attendance.xlsx")
            month_str = f"{year}-{month:02d}"
            monthly_data = attendance_df[attendance_df['Date'].str.startswith(month_str)]
            
            if not monthly_data.empty:
                st.metric("📅 Records Found", len(monthly_data))
                st.metric("👥 Unique Teachers", monthly_data['Teacher_ID'].nunique())
                st.metric("📆 Days Covered", monthly_data['Date'].nunique())
            else:
                st.warning("No data found for selected month.")
                
        except Exception as e:
            st.warning("Could not load preview data.")
    
    if st.button("📊 Generate Monthly Summary", type="primary"):
        with st.spinner("Generating monthly summary..."):
            success, message = excel_manager.create_monthly_summary(year, month)
            
            if success:
                st.success(message)
                st.balloons()
                
                # Provide download link
                summary_path = message.split("at ")[-1]
                if os.path.exists(summary_path):
                    with open(summary_path, "rb") as file:
                        st.download_button(
                            label="📥 Download Summary",
                            data=file.read(),
                            file_name=os.path.basename(summary_path),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
            else:
                st.error(message)

def backup_files_section(excel_manager):
    """Backup files section"""
    st.header("💾 Backup Excel Files")
    st.markdown("Create backups of all Excel files and data.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Backup Options")
        
        backup_type = st.selectbox(
            "Backup Type",
            ["Full Backup", "Excel Files Only", "Data Files Only"]
        )
        
        include_reports = st.checkbox("Include Generated Reports", value=True)
        compress_backup = st.checkbox("Compress Backup", value=False)
        
        st.info("💡 Backups are stored in the data/backups directory with timestamps.")
    
    with col2:
        st.subheader("Backup Status")
        
        try:
            # Show existing backups
            backup_dir = "data/backups"
            if os.path.exists(backup_dir):
                backups = [d for d in os.listdir(backup_dir) if d.startswith('excel_backup_')]
                backups.sort(reverse=True)
                
                if backups:
                    st.write("📁 Recent Backups:")
                    for backup in backups[:5]:  # Show last 5 backups
                        backup_path = os.path.join(backup_dir, backup)
                        backup_time = backup.replace('excel_backup_', '').replace('_', ' ')
                        backup_size = sum(os.path.getsize(os.path.join(backup_path, f)) 
                                        for f in os.listdir(backup_path) if os.path.isfile(os.path.join(backup_path, f)))
                        st.text(f"📦 {backup_time} ({backup_size/1024:.1f} KB)")
                else:
                    st.info("No previous backups found.")
            else:
                st.info("Backup directory not found.")
                
        except Exception as e:
            st.warning("Could not load backup information.")
    
    if st.button("💾 Create Backup", type="primary"):
        with st.spinner("Creating backup..."):
            success, message = excel_manager.backup_excel_files()
            
            if success:
                st.success(message)
                st.balloons()
            else:
                st.error(message)

def validate_data_section(excel_manager):
    """Validate data section"""
    st.header("🔍 Validate Excel Data")
    st.markdown("Validate Excel files before importing to ensure data quality.")
    
    uploaded_file = st.file_uploader(
        "Choose Excel file to validate",
        type=['xlsx', 'xls']
    )
    
    if uploaded_file is not None:
        data_type = st.selectbox(
            "Data Type",
            ["teachers", "attendance"],
            help="Select the type of data in the Excel file"
        )
        
        if st.button("🔍 Validate Data", type="primary"):
            with st.spinner("Validating data..."):
                try:
                    # Save file temporarily for validation
                    temp_path = f"temp_validate_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    try:
                        is_valid, message, warnings = excel_manager.validate_excel_data(temp_path, data_type)
                        
                        if is_valid:
                            st.success(f"✅ Validation Passed: {message}")
                            
                            if warnings:
                                st.warning("⚠️ Warnings found:")
                                for warning in warnings:
                                    st.warning(f"• {warning}")
                        else:
                            st.error(f"❌ Validation Failed: {message}")
                            
                        # Show data preview
                        df = pd.read_excel(temp_path)
                        st.subheader("📋 Data Preview")
                        st.dataframe(df.head(10))
                        
                        # Show data info
                        st.subheader("📊 Data Information")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Rows", len(df))
                        with col2:
                            st.metric("Columns", len(df.columns))
                        with col3:
                            st.metric("Empty Cells", df.isnull().sum().sum())
                            
                    finally:
                        # Clean up temp file
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                            
                except Exception as e:
                    st.error(f"Error during validation: {str(e)}")

def statistics_section(excel_manager):
    """Statistics section"""
    st.header("📈 Excel File Statistics")
    st.markdown("View statistics and information about your Excel files.")
    
    with st.spinner("Loading statistics..."):
        stats = excel_manager.get_excel_statistics()
    
    if stats:
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Teachers", stats.get('teachers_count', 0))
        with col2:
            st.metric("📅 Attendance Records", stats.get('attendance_records', 0))
        with col3:
            if 'data_range' in stats and stats['data_range']:
                date_range = f"{stats['data_range']['start_date']} to {stats['data_range']['end_date']}"
                st.metric("📆 Date Range", "Available")
                st.caption(date_range)
            else:
                st.metric("📆 Date Range", "No Data")
        with col4:
            total_size = sum(stats.get('file_sizes', {}).values())
            st.metric("💾 Total Size", f"{total_size/1024:.1f} KB")
        
        # File details
        st.subheader("📁 File Details")
        
        file_data = []
        for file_type in ['teachers', 'attendance']:
            if file_type in stats.get('file_sizes', {}):
                file_data.append({
                    'File': file_type.title(),
                    'Size (KB)': f"{stats['file_sizes'][file_type]/1024:.1f}",
                    'Last Modified': stats.get('last_modified', {}).get(file_type, 'Unknown')
                })
        
        if file_data:
            st.table(pd.DataFrame(file_data))
        
        # Data quality indicators
        st.subheader("🎯 Data Quality")
        
        try:
            # Check teachers data quality
            teachers_df = pd.read_excel("data/teachers.xlsx")
            attendance_df = pd.read_excel("data/attendance.xlsx")
            
            quality_metrics = []
            
            # Teachers quality
            if not teachers_df.empty:
                active_teachers = len(teachers_df[teachers_df['Status'] == 'Active'])
                teachers_with_email = len(teachers_df[teachers_df['Email'].notna() & (teachers_df['Email'] != '')])
                
                quality_metrics.append({
                    'Metric': 'Active Teachers',
                    'Value': f"{active_teachers}/{len(teachers_df)}",
                    'Percentage': f"{(active_teachers/len(teachers_df)*100):.1f}%"
                })
                
                quality_metrics.append({
                    'Metric': 'Teachers with Email',
                    'Value': f"{teachers_with_email}/{len(teachers_df)}",
                    'Percentage': f"{(teachers_with_email/len(teachers_df)*100):.1f}%"
                })
            
            # Attendance quality
            if not attendance_df.empty:
                high_confidence = len(attendance_df[attendance_df['Recognition_Confidence'] >= 0.8])
                
                quality_metrics.append({
                    'Metric': 'High Confidence Records',
                    'Value': f"{high_confidence}/{len(attendance_df)}",
                    'Percentage': f"{(high_confidence/len(attendance_df)*100):.1f}%"
                })
            
            if quality_metrics:
                st.table(pd.DataFrame(quality_metrics))
            
        except Exception as e:
            st.warning("Could not calculate data quality metrics.")
    
    else:
        st.warning("Could not load statistics. Please check if Excel files exist.")

if __name__ == "__main__":
    excel_automation_interface()