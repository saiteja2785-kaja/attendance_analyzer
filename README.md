# Student Attendance Analyzer

A Python + Pandas tool that reads student attendance from a CSV file, calculates
attendance percentages, finds students below the target, and shows how many
classes they need to attend to reach it.

## Features
- Validates the input CSV with clear error messages
- Attendance percentage and shortage status (default target 75%)
- Consecutive classes needed to reach the target
- Projections: attend all, miss all, or a custom number of upcoming classes
- Exports `attendance_report.csv`

## Setup
```
python -m pip install -r requirements.txt
```

## Run
```
python main.py
```

## Input format (attendance.csv)
```
student_id,name,total_classes,attended_classes
101,Rahul,100,90
```

## Tests
```
python -m pytest
```
## Dashboard
```
python -m streamlit run app.py
```