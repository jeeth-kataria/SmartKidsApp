# Smart Kids Attendance - Teacher Face Recognition System

A comprehensive face recognition attendance system for teachers built with Streamlit, featuring time-restricted capture, Excel database integration, and Google Calendar holiday detection.

## 🌟 Features

### Core Functionality
- **Face Recognition**: Real-time teacher identification using OpenCV and face_recognition
- **Time-Restricted Access**: Automatic system activation during 9:00 AM - 9:20 AM window
- **Excel Database**: Stores teacher data and attendance records in Excel format
- **Holiday Integration**: Google Calendar API integration with manual holiday override
- **Multi-Teacher Support**: Optimized for small teams (4 teachers)

### Advanced Features
- **Confidence Threshold**: Adjustable recognition sensitivity
- **Multiple Face Detection**: Handles multiple faces simultaneously
- **Data Backup**: Automatic daily backups of all data
- **Analytics Dashboard**: Comprehensive reporting and statistics
- **Mobile Responsive**: Works on desktop and mobile devices

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Webcam or camera device
- Google Cloud Console account (optional, for calendar integration)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Smart_Kids_Attendance
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Access the application**
   Open your browser and navigate to `http://localhost:8501`

## 📁 Project Structure

```
Smart_Kids_Attendance/
├── app.py                      # Main Streamlit application
├── database_manager.py         # Excel database operations
├── face_recognition_utils.py   # Face detection and recognition
├── time_manager.py            # Time window and holiday management
├── calendar_integration.py    # Google Calendar API integration
├── requirements.txt           # Python dependencies
├── vercel.json               # Vercel deployment configuration
├── README.md                 # This file
├── data/                     # Data storage directory
│   ├── teachers.xlsx         # Teacher database
│   ├── attendance.xlsx       # Attendance records
│   ├── manual_holidays.json  # Manual holiday entries
│   ├── time_settings.json    # Time configuration
│   └── backups/             # Automatic backups
├── face_encodings/           # Face encoding storage
├── temp_images/             # Temporary image processing
└── static/                  # Static assets
```

## 🔧 Configuration

### Time Settings
- Default attendance window: 9:00 AM - 9:20 AM
- Configurable through Settings page
- Automatic timezone detection

### Face Recognition
- Default confidence threshold: 0.6
- Adjustable from 0.3 to 0.9
- Requires 2-5 photos per teacher for optimal accuracy

### Database
- Excel format for easy data management
- Automatic backup creation
- Data validation and error handling

## 👥 Teacher Management

### Adding Teachers
1. Navigate to "Teacher Management" → "Add Teacher"
2. Fill in teacher details (ID, Name, Department, Email)
3. Upload 2-5 clear photos of the teacher
4. System will process and store face encodings

### Managing Teachers
- View all registered teachers
- Delete/deactivate teachers
- Update teacher information
- Export teacher data

## 📊 Attendance Process

### Daily Workflow
1. System automatically activates at 8:50 AM
2. Teachers stand in front of camera during active window
3. System recognizes faces and logs attendance
4. Attendance window closes at 9:10 AM
5. Reports and analytics available immediately

### Holiday Management
- Automatic holiday detection via Google Calendar
- Manual holiday addition/removal
- Weekend detection and skipping
- Holiday notifications on dashboard

## 📈 Reports & Analytics

### Available Reports
- Daily attendance summary
- Teacher-wise attendance tracking
- Monthly/weekly statistics
- Recognition confidence metrics
- Export to Excel/CSV formats

### Dashboard Metrics
- Total teachers registered
- Today's attendance count
- Monthly attendance summary
- System status indicators

## 🔗 Google Calendar Integration

### Setup Instructions
1. Create a Google Cloud Console project
2. Enable Google Calendar API
3. Create service account credentials
4. Download credentials.json file
5. Upload through Settings → Google Calendar tab

### Features
- Automatic holiday detection
- Indian holiday calendar integration
- Custom calendar support
- Offline fallback with cached data

## 🚀 Deployment

### Vercel Deployment
1. **Prepare for deployment**
   ```bash
   # Ensure all files are committed
   git add .
   git commit -m "Ready for deployment"
   ```

2. **Deploy to Vercel**
   ```bash
   # Install Vercel CLI
   npm i -g vercel
   
   # Deploy
   vercel
   ```

3. **Configure environment variables**
   - Set up Google Calendar credentials as environment variables
   - Configure timezone settings
   - Set up any custom configurations

### Environment Variables
```
GOOGLE_CALENDAR_CREDENTIALS=<base64-encoded-credentials>
TIMEZONE=Asia/Kolkata
STREAMLIT_SERVER_PORT=8501
```

## 🔒 Security Considerations

### Data Protection
- Face encodings stored securely
- No raw images stored permanently
- Excel files with access controls
- Backup encryption recommended

### Privacy Compliance
- Minimal data collection
- Secure face encoding storage
- Data retention policies
- User consent mechanisms

## 🛠️ Troubleshooting

### Common Issues

1. **Camera not working**
   - Check browser permissions
   - Ensure HTTPS for production
   - Verify camera device availability

2. **Face recognition accuracy**
   - Upload more photos per teacher
   - Adjust confidence threshold
   - Ensure good lighting conditions

3. **Google Calendar not working**
   - Verify credentials.json format
   - Check API quotas and limits
   - Ensure proper permissions

4. **Database errors**
   - Check file permissions
   - Verify Excel file format
   - Ensure sufficient disk space

### Performance Optimization
- Limit concurrent users
- Regular database cleanup
- Monitor memory usage
- Optimize image processing

## 📞 Support

### Getting Help
- Check troubleshooting section
- Review error logs in System Status
- Verify all dependencies installed
- Ensure proper file permissions

### Feature Requests
- Submit through issue tracker
- Provide detailed requirements
- Include use case scenarios

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request
5. Follow code review process

## 📋 Changelog

### Version 1.0.0
- Initial release
- Core face recognition functionality
- Time-based attendance system
- Excel database integration
- Google Calendar support
- Vercel deployment ready

## 🔮 Future Enhancements

### Planned Features
- SMS/Email notifications
- Advanced analytics dashboard
- Multi-school support
- Mobile app integration
- API endpoints for external systems

### Technical Improvements
- Database migration to PostgreSQL
- Real-time synchronization
- Enhanced security features
- Performance optimizations
- Automated testing suite
