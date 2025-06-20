# ⏰ Timeslot Changer Guide

## 🎯 Overview

The **Timeslot Changer** feature allows you to easily adjust the attendance window timing for different scenarios like late school starts, early sessions, or extended attendance periods.

---

## 🚀 Quick Presets

### **🕘 Standard (9:00-9:30)**
- **Use when:** Regular school timing
- **Duration:** 30 minutes
- **Best for:** Normal school days

### **🕙 Late Start (10:00-10:30)**
- **Use when:** School starts late due to weather, events, etc.
- **Duration:** 30 minutes
- **Best for:** Delayed school openings

### **🕗 Early (8:00-8:30)**
- **Use when:** Early morning sessions or activities
- **Duration:** 30 minutes
- **Best for:** Morning programs, early classes

### **🕚 Extended (9:00-10:00)**
- **Use when:** Need longer attendance window
- **Duration:** 60 minutes
- **Best for:** Flexible attendance periods

---

## ⚙️ Custom Time Settings

### **How to Set Custom Times:**
1. Go to **Settings** → **Time Settings**
2. Use the time input fields to set your desired start and end times
3. Click **"Update Time Window"** to save changes
4. Changes take effect immediately

### **Time Validation:**
- ✅ **Start time must be before end time**
- ✅ **Minimum 5 minutes duration recommended**
- ✅ **Maximum 4 hours duration allowed**
- ✅ **24-hour format (HH:MM)**

### **Late Policy:**
- Teachers marked as **"Late"** if attendance is 10+ minutes after start time
- Late threshold is automatically calculated
- Late attendance is still recorded but flagged

---

## 📊 Dashboard Integration

### **Timeslot Indicator:**
- Shows current attendance window on dashboard
- Displays start and end times clearly
- Updates automatically when times are changed

### **Quick Access:**
- **"Change Attendance Time"** button on dashboard
- Direct link to time settings
- No need to navigate through menus

### **Status Display:**
- Shows if attendance window is currently open/closed
- Displays time remaining in current window
- Shows next attendance window timing

---

## 🎛️ Advanced Features

### **Real-time Updates:**
- Time changes take effect immediately
- No system restart required
- All users see updated times instantly

### **Time Zone Support:**
- Uses Asia/Kolkata (IST) timezone
- Current time display on dashboard
- Automatic time calculations

### **Validation & Safety:**
- Prevents invalid time ranges
- Shows preview before saving
- Error messages for invalid inputs

---

## 📱 User Interface

### **Settings Page Layout:**
```
┌─────────────────────────────────────┐
│ ⏰ Attendance Time Window            │
├─────────────────────────────────────┤
│ Current Settings                    │
│ [Start Time] [End Time] [Duration]  │
├─────────────────────────────────────┤
│ Quick Presets                       │
│ [Standard] [Late Start] [Early]     │
│ [Extended]                          │
├─────────────────────────────────────┤
│ Custom Time Settings                │
│ [Start Time Input] [End Time Input] │
│ [Update Button]                     │
├─────────────────────────────────────┤
│ Preview & Status                    │
│ [Current Status] [Time Zone Info]   │
└─────────────────────────────────────┘
```

### **Dashboard Integration:**
```
┌─────────────────────────────────────┐
│ 📊 Dashboard                        │
├─────────────────────────────────────┤
│ [System Status] [Current Time]      │
│ [Attendance Window] [Working Day]   │
│ [Change Attendance Time Button]     │
└─────────────────────────────────────┘
```

---

## 🔧 Common Use Cases

### **1. Regular School Day**
- **Preset:** Standard (9:00-9:30)
- **When:** Normal school operations
- **Duration:** 30 minutes

### **2. Late School Start**
- **Preset:** Late Start (10:00-10:30)
- **When:** Weather delays, events, etc.
- **Duration:** 30 minutes

### **3. Early Morning Program**
- **Preset:** Early (8:00-8:30)
- **When:** Morning activities, early classes
- **Duration:** 30 minutes

### **4. Flexible Attendance**
- **Preset:** Extended (9:00-10:00)
- **When:** Need longer window for attendance
- **Duration:** 60 minutes

### **5. Custom Timing**
- **Method:** Custom time settings
- **When:** Specific school requirements
- **Duration:** Any valid time range

---

## 📋 Step-by-Step Instructions

### **Changing to Late Start:**
1. Go to **Settings** → **Time Settings**
2. Click **"🕙 Late Start (10:00-10:30)"** button
3. Confirm the change
4. System updates immediately

### **Setting Custom Times:**
1. Go to **Settings** → **Time Settings**
2. Use time inputs to set desired times
3. Review the preview
4. Click **"Update Time Window"**
5. Confirm the change

### **Quick Access from Dashboard:**
1. On dashboard, click **"⚙️ Change Attendance Time"**
2. Automatically goes to time settings
3. Make your changes
4. Return to dashboard

---

## ⚠️ Important Notes

### **Immediate Effect:**
- Time changes take effect immediately
- No restart or refresh required
- All users see updated times instantly

### **Data Persistence:**
- Changes are saved permanently
- Survives app restarts
- Stored in `data/time_settings.json`

### **Validation:**
- System prevents invalid time ranges
- Shows clear error messages
- Validates before saving

### **Backup:**
- Time settings included in backups
- Can be restored if needed
- Part of system configuration

---

## 🆘 Troubleshooting

### **Common Issues:**

#### 1. "Start time must be before end time"
**Solution:**
- Check your time inputs
- Ensure start time is earlier than end time
- Use 24-hour format (HH:MM)

#### 2. "Time window not updating"
**Solution:**
- Click the update button
- Check for error messages
- Refresh the page if needed

#### 3. "Preset not working"
**Solution:**
- Try clicking the preset button again
- Check if there are any error messages
- Use custom time settings as alternative

### **Getting Help:**
1. **Check error messages** - Look for specific error details
2. **Use custom settings** - If presets don't work
3. **Refresh page** - If changes don't appear
4. **Check time format** - Use HH:MM format

---

## 💡 Best Practices

### **1. Plan Ahead:**
- Set times before school day starts
- Consider weather and events
- Plan for different scenarios

### **2. Communicate Changes:**
- Inform teachers of time changes
- Update school announcements
- Keep everyone informed

### **3. Use Presets:**
- Use presets for common scenarios
- Save custom times for special cases
- Keep it simple when possible

### **4. Monitor Usage:**
- Check attendance patterns
- Adjust times based on usage
- Optimize for your school's needs

---

## 🎉 Benefits Summary

### **For Administrators:**
- ✅ **Quick adjustments** - Change times instantly
- ✅ **Flexible scheduling** - Adapt to any scenario
- ✅ **Easy management** - Simple interface
- ✅ **Real-time updates** - Immediate effect

### **For Teachers:**
- ✅ **Clear timing** - Know exactly when to mark attendance
- ✅ **Flexible window** - Adequate time for attendance
- ✅ **Consistent system** - Reliable timing
- ✅ **Easy access** - Quick time checks

### **For IT Support:**
- ✅ **No technical setup** - Simple configuration
- ✅ **Immediate changes** - No system restart
- ✅ **Safe updates** - Validation prevents errors
- ✅ **Easy troubleshooting** - Clear error messages

---

## 🚀 Ready to Use!

Your Smart Kids Attendance System now includes:

✅ **Flexible timeslot management**  
✅ **Quick preset options**  
✅ **Custom time settings**  
✅ **Real-time updates**  
✅ **Dashboard integration**  
✅ **Easy access controls**  

**The timeslot changer is ready to help you adapt to any school timing scenario!** 