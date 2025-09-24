# Extra Class Counter

A PyQt6-based desktop application for calculating extra classes needed in educational institutions based on day-specific timetable scheduling.

## Features

- **Excel Timetable Import**: Upload timetables with days as rows and time slots as columns
- **Day-Specific Calculation**: Calculates remaining classes based on actual weekdays (Mon, Tue, Wed, etc.)
- **Holiday Management**: Visual calendar to select festival holidays that affect specific days
- **Manual Subject Management**: Add, edit, and remove subjects with custom schedules
- **Real-time Calculation**: Shows exactly how many extra classes are needed per subject
- **Export Results**: Save calculation summaries to text files
- **Scrollable Results**: Dark-themed result sidebar with copy functionality

## How It Works

The application calculates extra classes using day-specific logic:

1. **Subject Schedule**: Each subject has specific days (e.g., ADA: Mon-2, Thu-1, Fri-1)
2. **Remaining Days**: Counts actual remaining Mondays, Thursdays, Fridays till semester end
3. **Holiday Impact**: Subtracts holidays that fall on subject's specific days
4. **Extra Classes**: Calculates: Required - (Conducted + Will be conducted regularly)

### Example Calculation
```
ADA Subject:
- Schedule: Mon-2, Thu-1, Fri-1 (5 classes/week)
- Total Required: 5 × 15 weeks = 75 classes
- Conducted: 50 classes
- Remaining: 25 classes
- Will be conducted regularly: 22 classes (based on remaining Mon/Thu/Fri)
- Extra classes needed: 25 - 22 = 3 classes
```

## Installation

### Quick Start
```bash
git clone https://github.com/abhi180105/extraclasscounter.git
cd extraclasscounter
chmod +x run.sh
./run.sh
```

### Manual Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## Usage

1. **Upload Timetable**: Click "Upload Timetable Excel File" and select your Excel file
2. **Manual Entry**: Or use "Add Subject" to manually enter subjects
3. **Enter Data**: Fill in classes conducted for each subject
4. **Set Semester End**: Choose the last day of semester using date picker
5. **Add Holidays**: Click calendar dates to add festival holidays
6. **Calculate**: Click "Calculate Classes" to see results
7. **Export**: Save results using "Export Results" button

## Excel Format

Your timetable should have days as rows and time slots as columns:

```
DAY | BATCH | 9:15-10:10 | 10:15-11:10 | 11:15-12:10 | ...
MON | 5CSE  | ADA-L      | BS          | FBL         | ...
TUE | 5CSE  | EN-L       | SKE DS      | DBMS-L      | ...
WED | 5CSE  | EN-L       | BS          |             | ...
```

The application automatically:
- Extracts subject names (ADA, BS, EN, SKE, DBMS)
- Counts classes per day for each subject
- Builds day-wise schedules (Mon-2, Tue-1, Thu-2)

## Dependencies

- **PyQt6**: GUI framework
- **pandas**: Excel/CSV file processing
- **openpyxl**: Excel file reading

## File Structure

```
extraclasscounter/
├── main.py           # Application entry point
├── gui.py            # Main GUI interface
├── calculator.py     # Core calculation logic
├── utils.py          # Day counting utilities
├── data_manager.py   # Data saving and export
├── config.py         # Configuration management
├── requirements.txt  # Python dependencies
├── run.sh           # Startup script
└── README.md        # This file
```

## Screenshots

### Main Interface
- Clean, intuitive interface with table for subject management
- Visual calendar for holiday selection
- Dark-themed scrollable results sidebar

### Calculation Results
```
📊 CLASS SUMMARY (Day-wise Calculation)
Generated: 24/09/2025 14:30
Semester End: 30/10/2025
Holidays: 2

✅ ADA:
  Total Required: 75
  Conducted Till Now: 50
  Remaining: 25
  Will be conducted regularly: 22
  Missed due to holidays: 0
  Extra classes needed: 3

📈 TOTALS:
Total Required: 165
Total Conducted: 75
Total Extra Needed: 15
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/abhi180105/extraclasscounter/issues) page
2. Create a new issue with detailed description
3. Include your timetable format and error messages if applicable

---

**Made for educational institutions to efficiently manage and calculate extra classes needed based on day-specific timetable scheduling.**