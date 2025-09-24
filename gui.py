from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton,
                             QLabel, QFileDialog, QTableWidget, QTableWidgetItem,
                             QHBoxLayout, QDateEdit, QMessageBox, QLineEdit, QHeaderView, 
                             QCalendarWidget, QListWidget, QListWidgetItem, QTextEdit)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QFont
from calculator import calculate_summary
from data_manager import DataManager
import datetime

class ExtraClassApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        self.setWindowTitle("Extra Class Counter")
        self.resize(900, 700)

        container = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Title
        title = QLabel("Extra Class Counter")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Upload button
        self.upload_btn = QPushButton("Upload Timetable Excel File")
        self.upload_btn.setStyleSheet("QPushButton { padding: 8px; font-weight: bold; }")
        self.upload_btn.clicked.connect(self.load_excel)
        layout.addWidget(self.upload_btn)

        # File label
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: gray;")
        layout.addWidget(self.file_label)

        # Table for subjects
        table_label = QLabel("Weekly Timetable:")
        table_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(table_label)
        
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Subject", "Classes Conducted", "Weekly Slots", "Days Schedule"])
        
        # Set column widths and resize modes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)  # Subject - resizable
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)        # Conducted - fixed
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)        # Weekly - fixed
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)      # Schedule - stretch
        
        # Set specific column widths
        self.table.setColumnWidth(0, 200)  # Subject
        self.table.setColumnWidth(1, 120)  # Conducted
        self.table.setColumnWidth(2, 100)  # Weekly
        
        self.table.setStyleSheet("QTableWidget { gridline-color: #d0d0d0; }")
        self.table.setMinimumHeight(200)
        layout.addWidget(self.table)
        
        # Add/Remove buttons
        table_btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Subject")
        add_btn.clicked.connect(self.add_subject)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_subject)
        table_btn_layout.addWidget(add_btn)
        table_btn_layout.addWidget(remove_btn)
        layout.addLayout(table_btn_layout)
        
        # Note for days schedule
        edit_note = QLabel("Excel format: Days as rows, time slots as columns | Manual format: Mon-2,Tue-1,Thu-2")
        edit_note.setStyleSheet("color: #666; font-style: italic; font-size: 10px;")
        layout.addWidget(edit_note)

        # Date and holiday section
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(5)

        # Semester last date
        date_layout = QHBoxLayout()
        self.date_label = QLabel("Last Day of Semester:")
        self.date_label.setFixedWidth(150)
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate().addDays(60))
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        self.date_input.setCalendarPopup(True)
        date_layout.addWidget(self.date_label)
        date_layout.addWidget(self.date_input)
        settings_layout.addLayout(date_layout)

        # Holidays
        holiday_label = QLabel("Festival Holidays:")
        holiday_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        settings_layout.addWidget(holiday_label)
        
        holiday_container = QHBoxLayout()
        
        # Calendar for date selection
        self.calendar = QCalendarWidget()
        self.calendar.setMaximumHeight(200)
        self.calendar.clicked.connect(self.add_holiday)
        
        # List of selected holidays
        self.holiday_list = QListWidget()
        self.holiday_list.setMaximumHeight(200)
        self.holiday_list.itemDoubleClicked.connect(self.remove_holiday)
        
        holiday_container.addWidget(self.calendar)
        holiday_container.addWidget(self.holiday_list)
        settings_layout.addLayout(holiday_container)
        
        # Holiday instructions
        holiday_note = QLabel("Click calendar to add holidays. Double-click list items to remove.")
        holiday_note.setStyleSheet("color: #666; font-style: italic; font-size: 10px;")
        settings_layout.addWidget(holiday_note)

        layout.addLayout(settings_layout)

        # Button layout
        button_layout = QHBoxLayout()
        
        # Calculate button
        self.calc_btn = QPushButton("Calculate Classes")
        self.calc_btn.setStyleSheet("QPushButton { padding: 10px; background-color: #4CAF50; color: white; font-weight: bold; }")
        self.calc_btn.clicked.connect(self.compute)
        self.calc_btn.setEnabled(False)
        
        # Export button
        self.export_btn = QPushButton("Export Results")
        self.export_btn.setStyleSheet("QPushButton { padding: 10px; background-color: #2196F3; color: white; }")
        self.export_btn.clicked.connect(self.export_results)
        self.export_btn.setEnabled(False)
        
        # Reset button
        self.reset_btn = QPushButton("Reset All")
        self.reset_btn.setStyleSheet("QPushButton { padding: 10px; background-color: #f44336; color: white; }")
        self.reset_btn.clicked.connect(self.reset_all)

        button_layout.addWidget(self.calc_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(self.reset_btn)
        layout.addLayout(button_layout)

        # Result
        result_label = QLabel("Results:")
        result_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(result_label)
        
        self.result_label = QTextEdit("Upload Excel file or manually add subjects to start calculating extra classes needed.")
        self.result_label.setStyleSheet("background-color: #2b2b2b; color: white; padding: 15px; border: 2px solid #555; border-radius: 5px; font-family: monospace;")
        self.result_label.setReadOnly(True)
        self.result_label.setMaximumHeight(300)
        layout.addWidget(self.result_label)

        container.setLayout(layout)
        self.setCentralWidget(container)

        self.subjects = {}
        self.current_summary = ""
        self.selected_holidays = set()
        
        # Calculate button enabled when data is available
        self.calc_btn.setEnabled(True)
    
    def add_holiday(self, date):
        """Add selected date to holiday list"""
        date_str = date.toString("yyyy-MM-dd")
        if date_str not in self.selected_holidays:
            self.selected_holidays.add(date_str)
            item = QListWidgetItem(date.toString("dd/MM/yyyy"))
            item.setData(Qt.ItemDataRole.UserRole, date_str)
            self.holiday_list.addItem(item)
    
    def remove_holiday(self, item):
        """Remove holiday from list"""
        date_str = item.data(Qt.ItemDataRole.UserRole)
        self.selected_holidays.discard(date_str)
        self.holiday_list.takeItem(self.holiday_list.row(item))
    
    def extract_subject_name(self, cell_value):
        """Extract subject name from timetable cell"""
        # Remove common suffixes and extract subject code
        cell_value = cell_value.replace('-L', '').replace('-P', '').replace(' Lab', '')
        
        # Split by space or hyphen and take first meaningful part
        parts = cell_value.replace('(', ' ').replace(')', ' ').split()
        if parts:
            subject = parts[0].strip()
            # Filter out common non-subject words
            if subject.upper() not in ['FBL', 'LUNCH', 'BREAK', '']:
                return subject.upper()
        return None
    
    def validate_days_schedule(self, schedule):
        """Validate days schedule format: Mon-2,Tue-1,Thu-2"""
        try:
            valid_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            parts = schedule.split(',')
            for part in parts:
                day, count = part.strip().split('-')
                if day not in valid_days or not count.isdigit() or int(count) <= 0:
                    return False
            return True
        except:
            return False

    def load_excel(self):
        try:
            file, _ = QFileDialog.getOpenFileName(
                self, 
                "Open Excel Timetable", 
                "", 
                "Excel Files (*.xlsx *.xls);;CSV Files (*.csv)"
            )
            if file:
                import pandas as pd
                
                # Read Excel/CSV file
                if file.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                # Expected format: DAY column with days as rows, time slots as columns
                if 'DAY' not in df.columns:
                    QMessageBox.warning(self, "Invalid Format", 
                                      "Excel file must have 'DAY' column with days as rows.")
                    return
                
                # Clear existing data
                self.table.setRowCount(0)
                
                # Extract subjects from timetable
                subjects_count = {}
                
                # Skip header row and process each day
                for _, row in df.iterrows():
                    day = str(row['DAY']).strip().upper()
                    if day not in ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']:
                        continue
                    
                    # Check each time slot for subjects
                    for col in df.columns:
                        if col in ['DAY', 'BATCH']:
                            continue
                        
                        cell_value = str(row[col]).strip() if pd.notna(row[col]) else ''
                        if not cell_value or cell_value == 'nan':
                            continue
                        
                        # Extract subject name (before first space or hyphen)
                        subject = self.extract_subject_name(cell_value)
                        if subject:
                            if subject not in subjects_count:
                                subjects_count[subject] = {}
                            if day not in subjects_count[subject]:
                                subjects_count[subject][day] = 0
                            subjects_count[subject][day] += 1
                
                # Add subjects to table
                for subject, day_counts in subjects_count.items():
                    days_schedule = []
                    weekly_total = 0
                    
                    for day, count in day_counts.items():
                        days_schedule.append(f"{day.title()}-{count}")
                        weekly_total += count
                    
                    if weekly_total > 0:
                        schedule_str = ','.join(days_schedule)
                        self.add_subject_to_table(subject, 0, weekly_total, schedule_str)
                
                self.file_label.setText(f"Loaded: {file.split('/')[-1]} ({len(df)} subjects)")
                self.result_label.setText("Excel timetable loaded. Enter conducted classes and calculate.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load Excel file: {str(e)}")
    
    def add_subject(self):
        """Add new subject row"""
        self.add_subject_to_table("New Subject", 0, 1)
    
    def remove_subject(self):
        """Remove selected subject"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
    
    def add_subject_to_table(self, subject, conducted, weekly_slots, days_schedule="Mon-1,Wed-1,Fri-1"):
        """Add subject to table"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Subject name (editable)
        subject_item = QTableWidgetItem(subject)
        subject_item.setFlags(subject_item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 0, subject_item)
        
        # Conducted classes (editable)
        conducted_item = QTableWidgetItem(str(conducted))
        conducted_item.setFlags(conducted_item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 1, conducted_item)
        
        # Weekly slots (editable)
        weekly_item = QTableWidgetItem(str(weekly_slots))
        weekly_item.setFlags(weekly_item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 2, weekly_item)
        
        # Days schedule (editable)
        days_item = QTableWidgetItem(days_schedule)
        days_item.setFlags(days_item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 3, days_item)



    def validate_inputs(self):
        """Validate all user inputs"""
        try:
            # Validate date
            last_date = self.date_input.date().toPyDate()
            if last_date <= datetime.date.today():
                QMessageBox.warning(self, "Invalid Date", "Semester end date must be in the future.")
                return False

            # Check if table has data
            if self.table.rowCount() == 0:
                QMessageBox.warning(self, "No Data", "Please add subjects or upload Excel file first.")
                return False
            
            # Validate holidays from calendar selection
            for date_str in self.selected_holidays:
                try:
                    holiday_date = datetime.date.fromisoformat(date_str)
                    if holiday_date < datetime.date.today():
                        QMessageBox.warning(self, "Invalid Holiday", f"Holiday date {date_str} is in the past.")
                        return False
                except ValueError:
                    QMessageBox.warning(self, "Invalid Date", f"Invalid holiday date: {date_str}")
                    return False

            # Validate table data
            for i in range(self.table.rowCount()):
                subject = self.table.item(i, 0).text().strip()
                conducted_text = self.table.item(i, 1).text().strip()
                weekly_text = self.table.item(i, 2).text().strip()
                days_schedule = self.table.item(i, 3).text().strip()
                
                if not subject:
                    QMessageBox.warning(self, "Invalid Input", f"Subject name cannot be empty in row {i+1}.")
                    return False
                
                if not conducted_text.isdigit():
                    QMessageBox.warning(self, "Invalid Input", f"Please enter a valid number for classes conducted in {subject}.")
                    return False
                
                if not weekly_text.isdigit():
                    QMessageBox.warning(self, "Invalid Input", f"Please enter a valid number for weekly slots in {subject}.")
                    return False
                
                if int(conducted_text) < 0:
                    QMessageBox.warning(self, "Invalid Input", f"Classes conducted cannot be negative for {subject}.")
                    return False
                
                if int(weekly_text) <= 0:
                    QMessageBox.warning(self, "Invalid Input", f"Weekly slots must be greater than 0 for {subject}.")
                    return False
                
                # Validate days schedule format
                if not self.validate_days_schedule(days_schedule):
                    QMessageBox.warning(self, "Invalid Input", f"Invalid days schedule format for {subject}. Use format: Mon-2,Tue-1,Thu-2")
                    return False

            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Validation Error", f"Input validation failed: {str(e)}")
            return False

    def compute(self):
        try:
            if not self.validate_inputs():
                return

            # Show calculating state
            self.calc_btn.setEnabled(False)
            self.result_label.setText("Calculating...")

            # Use QTimer to defer calculation to avoid blocking
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, self.perform_calculation)
            
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", f"Failed to calculate classes: {str(e)}")
            self.calc_btn.setEnabled(True)

    def perform_calculation(self):
        """Perform the actual calculation (called after a short delay)"""
        try:
            print("Starting calculation...")
            # Collect user edits
            subjects_data = {}
            for i in range(self.table.rowCount()):
                subject = self.table.item(i, 0).text()
                subjects_data[subject] = {
                    'conducted': int(self.table.item(i, 1).text()),
                    'weekly_slots': int(self.table.item(i, 2).text()),
                    'days_schedule': self.table.item(i, 3).text()
                }

            last_date = self.date_input.date().toPyDate()
            holidays = list(self.selected_holidays)

            summary = calculate_summary(subjects_data, last_date, holidays)
            self.current_summary = summary
            
            # Display results as plain text
            self.result_label.setText(summary)
            self.export_btn.setEnabled(True)
            self.calc_btn.setEnabled(True)
            
            # Save calculation
            try:
                conducted_dict = {subject: data['conducted'] for subject, data in subjects_data.items()}
                self.data_manager.save_calculation(
                    {subject: data['weekly_slots'] for subject, data in subjects_data.items()}, 
                    conducted_dict, last_date, holidays, summary
                )
            except Exception as e:
                print(f"Warning: Could not save calculation: {e}")
            
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", f"Failed to calculate classes: {str(e)}")
            self.calc_btn.setEnabled(True)

    def export_results(self):
        try:
            if not self.current_summary:
                QMessageBox.warning(self, "No Data", "Please calculate classes first.")
                return
                
            file, _ = QFileDialog.getSaveFileName(
                self,
                "Export Results",
                f"class_summary_{datetime.date.today()}.txt",
                "Text Files (*.txt);;All Files (*)"
            )
            
            if file:
                with open(file, 'w') as f:
                    f.write(f"Extra Class Counter Summary\n")
                    f.write(f"Generated on: {datetime.datetime.now()}\n")
                    f.write(f"Semester End Date: {self.date_input.date().toString()}\n")
                    f.write(f"Holidays: {', '.join(self.selected_holidays)}\n\n")
                    f.write(self.current_summary)
                
                QMessageBox.information(self, "Success", f"Results exported to {file}")
                
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export results: {str(e)}")
    
    def reset_all(self):
        """Reset all data and clear the interface"""
        reply = QMessageBox.question(self, "Reset All", 
                                   "Are you sure you want to clear all data?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # Clear table
            self.table.setRowCount(0)
            
            # Clear holidays
            self.holiday_list.clear()
            self.selected_holidays.clear()
            
            # Reset date to default
            self.date_input.setDate(QDate.currentDate().addDays(60))
            
            # Clear results
            self.result_label.setText("Upload Excel file or manually add subjects to start calculating extra classes needed.")
            self.current_summary = ""
            
            # Reset file label
            self.file_label.setText("No file selected")
            
            # Disable export button
            self.export_btn.setEnabled(False)


