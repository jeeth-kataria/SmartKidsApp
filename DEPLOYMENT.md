# Vercel Deployment Guide

## Prerequisites
1. Vercel account
2. Git repository
3. All required files present

## Deployment Steps

### 1. Prepare Repository
```bash
python deploy.py
```

### 2. Install Vercel CLI
```bash
npm i -g vercel
```

### 3. Login to Vercel
```bash
vercel login
```

### 4. Deploy
```bash
vercel
```

### 5. Set Environment Variables
Go to Vercel dashboard and set:
- GOOGLE_CALENDAR_CREDENTIALS (if using Google Calendar)
- TIMEZONE
- Any other custom variables

### 6. Test Deployment
Visit the deployed URL and test all features

## Troubleshooting

### Common Issues
1. **Import errors**: Check requirements.txt
2. **Memory issues**: Optimize image processing
3. **Timeout errors**: Reduce processing complexity
4. **File not found**: Check file paths and permissions

### Performance Tips
1. Use opencv-python-headless for smaller size
2. Optimize face encoding storage
3. Implement caching for better performance
4. Monitor memory usage

## Support
Check the main README.md for detailed troubleshooting steps.