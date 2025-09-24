# Extra Class Counter

A PyQt6-based desktop application for tracking and calculating extra classes/teaching hours in educational institutions.

## Features

- **OCR Timetable Parsing**: Automatically reads timetable images using OCR and computer vision
- **Class Calculation**: Calculates required vs conducted classes and determines extra classes needed
- **Holiday Management**: Accounts for holidays and working days in calculations
- **Data Export**: Export results to text files for administrative use
- **History Tracking**: Maintains calculation history and subject database

## Quick Start

### Option 1: Using the startup script (Recommended)
```bash
./run.sh
```

### Option 2: Manual setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## Usage

1. **Upload Timetable**: Click "Upload Timetable Image" and select your timetable image
2. **Configure Settings**: 
   - Set semester end date
   - Add holidays (comma-separated, YYYY-MM-DD format)
3. **Edit Conducted Classes**: Update the "Conducted" column in the table
4. **Calculate**: Click "Calculate Classes" to get results
5. **Export**: Click "Export Results" to save the summary

## Dependencies

- PyQt6 (GUI framework)
- OpenCV (Image processing)
- Tesseract OCR (Text recognition)
- PyTorch + Ultralytics (Optional: Advanced timetable detection)
- Pandas, NumPy (Data processing)

## File Structure

- `main.py` - Application entry point
- `gui.py` - Main GUI interface
- `ocr_parser.py` - Timetable image processing
- `calculator.py` - Class calculation logic
- `data_manager.py` - Data storage and export
- `config.py` - Configuration management
- `utils.py` - Utility functions

## Configuration

Edit `config.json` to customize:
- Semester duration
- Default holidays
- Working days
- OCR settings

## Troubleshooting

- Ensure Tesseract OCR is installed on your system
- For better OCR results, use high-quality, clear timetable images
- Check that all dependencies are installed in the virtual environment