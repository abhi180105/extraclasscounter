from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton,
                             QLabel, QFileDialog, QTableWidget, QTableWidgetItem,
                             QHBoxLayout, QDateEdit, QMessageBox, QLineEdit, QHeaderView, 
                             QCalendarWidget, QListWidget, QListWidgetItem, QTextEdit, QMenuBar, QMenu,
                             QProgressBar, QStatusBar, QSplitter, QDialog, QFormLayout, QCheckBox,
                             QSpinBox, QComboBox, QDialogButtonBox)
from PyQt6.QtCore import QDate, Qt, QSettings, QTimer
from PyQt6.QtGui import QFont, QAction, QPalette, QKeySequence
import json
import sqlite3
import os
from calculator import calculate_summary
from data_manager import DataManager
import datetime
import json

class ExtraClassApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        self.setWindowTitle("Extra Class Counter")
        self.resize(1200, 800)
        
        # Initialize settings
        self.settings = QSettings('ExtraClassCounter', 'Settings')
        self.is_dark_theme = self.settings.value('dark_theme', False, type=bool)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar with progress
        self.create_status_bar()
        
        # Initialize database
        self.init_database()
        
        # Load recent files
        self.recent_files = self.settings.value('recent_files', [], type=list)[:5]

        # Create main splitter (horizontal for sidebar)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left widget for main interface
        left_widget = QWidget()
        layout = QVBoxLayout(left_widget)
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
        
        self.table = QTableWidget(0, 10)
        self.table.setHorizontalHeaderLabels(["Subject", "Conducted", "Weekly", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        
        # Set column widths and resize modes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)  # Subject - resizable
        for i in range(1, 10):  # All other columns fixed width
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
        
        # Set specific column widths
        self.table.setColumnWidth(0, 120)  # Subject
        self.table.setColumnWidth(1, 80)   # Conducted
        self.table.setColumnWidth(2, 60)   # Weekly
        for i in range(3, 10):  # Day columns
            self.table.setColumnWidth(i, 80)
        
        self.table.setStyleSheet("QTableWidget { gridline-color: #d0d0d0; }")
        self.table.setMinimumHeight(300)
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
        
        # Note for day counters
        edit_note = QLabel("Excel format: Days as rows, time slots as columns | Manual: Use day counters (Mon, Tue, etc.)")
        edit_note.setStyleSheet("color: #666; font-style: italic; font-size: 10px;")
        layout.addWidget(edit_note)
        
        # Connect table changes to update weekly slots
        self.table.itemChanged.connect(self.update_weekly_slots)

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
        
        # Add left widget to splitter
        main_splitter.addWidget(left_widget)
        
        # Right widget (results sidebar)
        result_widget = QWidget()
        result_layout = QVBoxLayout(result_widget)
        result_layout.setContentsMargins(10, 5, 10, 10)
        
        result_label = QLabel("Results:")
        result_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        result_layout.addWidget(result_label)
        
        self.result_label = QTextEdit("Upload Excel file or manually add subjects to start calculating extra classes needed.")
        self.result_label.setStyleSheet("background-color: #2b2b2b; color: white; padding: 15px; border: 2px solid #555; border-radius: 5px; font-family: monospace;")
        self.result_label.setReadOnly(True)
        result_layout.addWidget(self.result_label)
        
        main_splitter.addWidget(result_widget)
        
        # Set splitter proportions and behavior (left panel wider)
        main_splitter.setSizes([800, 400])
        main_splitter.setCollapsible(0, False)
        main_splitter.setCollapsible(1, False)
        
        # Container
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.addWidget(main_splitter)

        self.setCentralWidget(main_splitter)

        self.subjects = {}
        self.current_summary = ""
        self.selected_holidays = set()
        
        # Calculate button enabled when data is available
        self.calc_btn.setEnabled(True)
        
        # Apply saved theme
        if self.is_dark_theme:
            self.toggle_theme()
        
        # Setup keyboard shortcuts
        self.setup_shortcuts()
        
        # Add tooltips
        self.add_tooltips()
        
        # Make panels resizable
        self.make_resizable()
    
    def create_menu_bar(self):
        """Create menu bar with File and View menus"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        save_action = QAction('Save Project', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        open_action = QAction('Open Project', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        new_action = QAction('New Project', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        theme_action = QAction('Toggle Dark/Light Theme', self)
        theme_action.setShortcut('Ctrl+T')
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)
        
        view_menu.addSeparator()
        
        fullscreen_action = QAction('Toggle Fullscreen', self)
        fullscreen_action.setShortcut('F11')
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # Recent files menu
        if hasattr(self, 'recent_files') and self.recent_files:
            file_menu.addSeparator()
            recent_menu = file_menu.addMenu('Recent Files')
            for i, file_path in enumerate(self.recent_files):
                action = QAction(f"{i+1}. {os.path.basename(file_path)}", self)
                action.triggered.connect(lambda checked, path=file_path: self.open_recent_file(path))
                recent_menu.addAction(action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        settings_action = QAction('Preferences...', self)
        settings_action.setShortcut('Ctrl+,')
        settings_action.triggered.connect(self.show_preferences)
        tools_menu.addAction(settings_action)
    
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
    
    def update_weekly_slots_for_row(self, row):
        """Update weekly slots for a specific row"""
        total = 0
        
        # Sum all day counters from widgets
        for col in range(3, 10):  # Mon to Sun columns
            widget = self.table.cellWidget(row, col)
            if widget:
                # Find the counter label in the widget
                counter_label = widget.findChild(QLabel)
                if counter_label:
                    total += int(counter_label.text())
        
        # Update weekly slots column
        weekly_item = self.table.item(row, 2)
        if weekly_item:
            weekly_item.setText(str(total))
            self.update_weekly_background(row)
    
    def update_weekly_background(self, row):
        """Update weekly column background based on current theme"""
        weekly_item = self.table.item(row, 2)
        if weekly_item:
            weekly_item.setBackground(Qt.GlobalColor.transparent)
    
    def update_weekly_slots(self, item):
        """Auto-update weekly slots when day counters change (for text editing)"""
        if item and item.column() >= 3 and item.column() <= 9:  # Day columns
            self.update_weekly_slots_for_row(item.row())
    
    def create_day_counter_widget(self, row, col, initial_count):
        """Create a widget with counter and +/- buttons for day cells"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Minus button
        minus_btn = QPushButton("-")
        minus_btn.setFixedSize(20, 25)
        minus_btn.setStyleSheet("QPushButton { font-size: 12px; font-weight: bold; }")
        
        # Counter label
        counter_label = QLabel(str(initial_count))
        counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        counter_label.setFixedWidth(30)
        counter_label.setStyleSheet("QLabel { font-size: 12px; }")
        
        # Plus button
        plus_btn = QPushButton("+")
        plus_btn.setFixedSize(20, 25)
        plus_btn.setStyleSheet("QPushButton { font-size: 12px; font-weight: bold; }")
        
        # Connect buttons
        minus_btn.clicked.connect(lambda: self.adjust_counter(row, col, counter_label, -1))
        plus_btn.clicked.connect(lambda: self.adjust_counter(row, col, counter_label, 1))
        
        layout.addWidget(minus_btn)
        layout.addWidget(counter_label)
        layout.addWidget(plus_btn)
        
        return widget
    
    def adjust_counter(self, row, col, label, change):
        """Adjust counter value and update weekly total"""
        current_count = int(label.text())
        new_count = max(0, current_count + change)
        label.setText(str(new_count))
        
        # Update weekly slots
        self.update_weekly_slots_for_row(row)
    
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
                    df = pd.read_csv(file, header=0)
                else:
                    df = pd.read_excel(file, header=0)
                
                # If columns are unnamed, try using first row as headers
                if any('Unnamed:' in str(col) for col in df.columns):
                    if file.endswith('.csv'):
                        df = pd.read_csv(file, header=1)  # Try second row as header
                    else:
                        df = pd.read_excel(file, header=1)  # Try second row as header
                    
                    # If still unnamed, use first data row as column names
                    if any('Unnamed:' in str(col) for col in df.columns):
                        if file.endswith('.csv'):
                            df = pd.read_csv(file, header=None)
                        else:
                            df = pd.read_excel(file, header=None)
                        
                        # Use first row as column names
                        df.columns = df.iloc[0]
                        df = df.drop(df.index[0]).reset_index(drop=True)
                
                # Find DAY column (flexible naming)
                day_col = None
                for col in df.columns:
                    col_str = str(col).upper().strip()
                    if col_str in ['DAY', 'DAYS', 'DAY OF WEEK', 'WEEKDAY'] or any(day in col_str for day in ['MON', 'TUE', 'WED']):
                        day_col = col
                        break
                
                # If no DAY column found, check if first column contains day names
                if not day_col and len(df.columns) > 0:
                    first_col = df.columns[0]
                    first_col_values = df[first_col].astype(str).str.upper()
                    if any(day in ' '.join(first_col_values.values) for day in ['MON', 'TUE', 'WED', 'THU', 'FRI']):
                        day_col = first_col
                
                if not day_col:
                    QMessageBox.warning(self, "Invalid Format", 
                                      f"Excel file must have a DAY column or days in first column. Found columns: {list(df.columns)}\nFirst few rows: {df.head(3).to_string()}")
                    return
                
                # Clear existing data
                self.table.setRowCount(0)
                
                # Extract subjects from timetable
                subjects_count = {}
                
                # Skip header row and process each day
                for _, row in df.iterrows():
                    day = str(row[day_col]).strip().upper()
                    if day not in ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']:
                        continue
                    
                    # Get time slot columns
                    time_cols = [col for col in df.columns if col not in [day_col, 'BATCH']]
                    
                    # Check each time slot for subjects
                    for col in time_cols:
                        cell_value = str(row[col]).strip() if pd.notna(row[col]) else ''
                        if not cell_value or cell_value == 'nan':
                            continue
                        
                        subject = self.extract_subject_name(cell_value)
                        if subject:
                            # Check if it's a lab class
                            lab_keywords = ['lab', 'practical', 'prac', 'laboratory', 'workshop']
                            is_lab = any(keyword in cell_value.lower() for keyword in lab_keywords)
                            
                            # Check for -P suffix (Practical)
                            has_p_suffix = '-p' in cell_value.lower()
                            
                            # Also check if subject name itself indicates lab
                            subject_lab = 'lab' in subject.lower() if subject else False
                            
                            class_count = 2 if (is_lab or subject_lab or has_p_suffix) else 1
                            
                            if subject not in subjects_count:
                                subjects_count[subject] = {}
                            if day not in subjects_count[subject]:
                                subjects_count[subject][day] = 0
                            subjects_count[subject][day] += class_count
                
                # Add subjects to table
                for subject, day_counts in subjects_count.items():
                    days_schedule = []
                    weekly_total = 0
                    
                    for day, count in day_counts.items():
                        days_schedule.append(f"{day.title()}-{count}")
                        weekly_total += count
                    
                    if weekly_total > 0:
                        # Convert to day_counts dictionary
                        day_counts = {}
                        for day_schedule in days_schedule:
                            if '-' in day_schedule:
                                day, count = day_schedule.split('-', 1)
                                day_counts[day] = int(count)
                            else:
                                # Handle case where there's no '-' separator
                                day_counts[day_schedule] = 1
                        
                        self.add_subject_to_table(subject, 0, weekly_total, day_counts)
                
                self.file_label.setText(f"Loaded: {file.split('/')[-1]} ({len(df)} subjects)")
                self.result_label.setText("Excel timetable loaded. Enter conducted classes and calculate.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load Excel file: {str(e)}")
    
    def add_subject(self):
        """Add new subject row"""
        self.add_subject_to_table("New Subject", 0, 3)
    
    def remove_subject(self):
        """Remove selected subject"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
    
    def add_subject_to_table(self, subject, conducted, weekly_slots, day_counts=None):
        """Add subject to table with day counters"""
        if day_counts is None:
            day_counts = {'Mon': 1, 'Wed': 1, 'Fri': 1}  # Default schedule
        
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
        
        # Weekly slots (read-only, auto-calculated)
        weekly_item = QTableWidgetItem(str(weekly_slots))
        weekly_item.setFlags(weekly_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 2, weekly_item)
        self.update_weekly_background(row)
        
        # Day counters with +/- buttons
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            count = day_counts.get(day, 0)
            day_widget = self.create_day_counter_widget(row, 3 + i, count)
            self.table.setCellWidget(row, 3 + i, day_widget)



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
                # Build days schedule from day counter widgets
                days_schedule_parts = []
                days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                for j, day in enumerate(days):
                    widget = self.table.cellWidget(i, 3 + j)
                    if widget:
                        counter_label = widget.findChild(QLabel)
                        if counter_label and int(counter_label.text()) > 0:
                            days_schedule_parts.append(f"{day}-{counter_label.text()}")
                days_schedule = ','.join(days_schedule_parts)
                
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
                
                # Validate that at least one day has classes
                if not days_schedule_parts:
                    QMessageBox.warning(self, "Invalid Input", f"Subject {subject} must have at least one day with classes.")
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
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            self.status_bar.showMessage("Calculating extra classes...")

            # Use QTimer to defer calculation to avoid blocking
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
                
                # Build days schedule from widgets
                days_schedule_parts = []
                days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                for j, day in enumerate(days):
                    widget = self.table.cellWidget(i, 3 + j)
                    if widget:
                        counter_label = widget.findChild(QLabel)
                        if counter_label and int(counter_label.text()) > 0:
                            days_schedule_parts.append(f"{day}-{counter_label.text()}")
                days_schedule = ','.join(days_schedule_parts)
                
                subjects_data[subject] = {
                    'conducted': int(self.table.item(i, 1).text()),
                    'weekly_slots': int(self.table.item(i, 2).text()),
                    'days_schedule': days_schedule
                }

            last_date = self.date_input.date().toPyDate()
            holidays = list(self.selected_holidays)

            summary = calculate_summary(subjects_data, last_date, holidays)
            self.current_summary = summary
            
            # Display results as plain text
            self.result_label.setText(summary)
            self.export_btn.setEnabled(True)
            self.calc_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
            self.status_bar.showMessage("Calculation completed", 3000)
            
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
    
    def save_project(self):
        """Save current project data to JSON file"""
        try:
            file, _ = QFileDialog.getSaveFileName(
                self,
                "Save Project",
                f"class_project_{datetime.date.today()}.json",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file:
                # Collect all data
                project_data = {
                    'subjects': [],
                    'semester_end': self.date_input.date().toString('yyyy-MM-dd'),
                    'holidays': list(self.selected_holidays)
                }
                
                # Save table data
                for row in range(self.table.rowCount()):
                    subject_data = {
                        'name': self.table.item(row, 0).text(),
                        'conducted': int(self.table.item(row, 1).text()),
                        'weekly': int(self.table.item(row, 2).text()),
                        'days': {}
                    }
                    
                    # Get day counts from widgets
                    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                    for i, day in enumerate(days):
                        widget = self.table.cellWidget(row, 3 + i)
                        if widget:
                            counter_label = widget.findChild(QLabel)
                            if counter_label:
                                subject_data['days'][day] = int(counter_label.text())
                    
                    project_data['subjects'].append(subject_data)
                
                # Save to file
                with open(file, 'w') as f:
                    json.dump(project_data, f, indent=2)
                
                QMessageBox.information(self, "Success", f"Project saved to {file}")
                
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save project: {str(e)}")
    
    def open_project(self):
        """Open saved project from JSON file"""
        try:
            file, _ = QFileDialog.getOpenFileName(
                self,
                "Open Project",
                "",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file:
                with open(file, 'r') as f:
                    project_data = json.load(f)
                
                # Clear existing data
                self.table.setRowCount(0)
                self.holiday_list.clear()
                self.selected_holidays.clear()
                
                # Load semester end date
                date_obj = QDate.fromString(project_data['semester_end'], 'yyyy-MM-dd')
                self.date_input.setDate(date_obj)
                
                # Load holidays
                for holiday in project_data['holidays']:
                    self.selected_holidays.add(holiday)
                    date_obj = QDate.fromString(holiday, 'yyyy-MM-dd')
                    item = QListWidgetItem(date_obj.toString("dd/MM/yyyy"))
                    item.setData(Qt.ItemDataRole.UserRole, holiday)
                    self.holiday_list.addItem(item)
                
                # Load subjects
                for subject_data in project_data['subjects']:
                    self.add_subject_to_table(
                        subject_data['name'],
                        subject_data['conducted'],
                        subject_data['weekly'],
                        subject_data['days']
                    )
                
                self.file_label.setText(f"Loaded: {file.split('/')[-1]}")
                QMessageBox.information(self, "Success", f"Project loaded from {file}")
                
        except Exception as e:
            QMessageBox.critical(self, "Open Error", f"Failed to open project: {str(e)}")
    
    def new_project(self):
        """Create new project (reset all)"""
        reply = QMessageBox.question(self, "New Project", 
                                   "Create new project? This will clear all current data.",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.reset_all()
    
    def toggle_theme(self):
        """Toggle between dark and light theme"""
        self.is_dark_theme = not self.is_dark_theme
        
        if self.is_dark_theme:
            # Dark theme
            self.setStyleSheet("""
                QMainWindow { background-color: #2b2b2b; color: white; }
                QWidget { background-color: #2b2b2b; color: white; }
                QTableWidget { background-color: #3c3c3c; color: white; gridline-color: #555; }
                QTableWidget::item { background-color: #3c3c3c; }
                QTableWidget::item:selected { background-color: #4a4a4a; }
                QPushButton { background-color: #4a4a4a; color: white; border: 1px solid #666; padding: 5px; }
                QPushButton:hover { background-color: #5a5a5a; }
                QLabel { color: white; }
                QDateEdit { background-color: #4a4a4a; color: white; border: 1px solid #666; }
                QCalendarWidget { background-color: #3c3c3c; color: white; }
                QListWidget { background-color: #3c3c3c; color: white; border: 1px solid #666; }
                QTextEdit { background-color: #2b2b2b; color: white; }
            """)
        else:
            # Light theme (default)
            self.setStyleSheet("")
        
        # Update result label style
        if self.is_dark_theme:
            self.result_label.setStyleSheet("background-color: #1a1a1a; color: white; padding: 15px; border: 2px solid #555; border-radius: 5px; font-family: monospace;")
        else:
            self.result_label.setStyleSheet("background-color: #2b2b2b; color: white; padding: 15px; border: 2px solid #555; border-radius: 5px; font-family: monospace;")
        

    
    def create_status_bar(self):
        """Create status bar with progress indicator"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
    
    def init_database(self):
        """Initialize SQLite database for better data storage"""
        db_path = os.path.join(os.path.expanduser('~'), '.extraclasscounter', 'data.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_conn = sqlite3.connect(db_path)
        cursor = self.db_conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY,
                name TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.db_conn.commit()
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.table.setTabKeyNavigation(True)
        
        # Calculate shortcut
        calc_shortcut = QAction(self)
        calc_shortcut.setShortcut('Ctrl+Return')
        calc_shortcut.triggered.connect(self.compute)
        self.addAction(calc_shortcut)
    
    def add_tooltips(self):
        """Add helpful tooltips to UI elements"""
        self.upload_btn.setToolTip("Upload Excel timetable with days as rows and time slots as columns")
        self.table.setToolTip("Edit subject data. Use +/- buttons to adjust daily class counts")
        self.date_input.setToolTip("Set the last day of your semester")
        self.calendar.setToolTip("Click dates to add festival holidays")
        self.calc_btn.setToolTip("Calculate extra classes needed (Ctrl+Enter)")
    
    def make_resizable(self):
        """Make panels resizable"""
        self.result_label.setMaximumHeight(16777215)
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def show_preferences(self):
        """Show preferences dialog"""
        dialog = PreferencesDialog(self)
        dialog.exec()
    
    def add_recent_file(self, file_path):
        """Add file to recent files list"""
        if hasattr(self, 'recent_files'):
            if file_path in self.recent_files:
                self.recent_files.remove(file_path)
            self.recent_files.insert(0, file_path)
            self.recent_files = self.recent_files[:5]
            self.settings.setValue('recent_files', self.recent_files)
    
    def open_recent_file(self, file_path):
        """Open a recent file"""
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    project_data = json.load(f)
                self.load_project_data(project_data)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open recent file: {str(e)}")
    
    def load_project_data(self, project_data):
        """Load project data"""
        self.table.setRowCount(0)
        self.holiday_list.clear()
        self.selected_holidays.clear()
        
        date_obj = QDate.fromString(project_data['semester_end'], 'yyyy-MM-dd')
        self.date_input.setDate(date_obj)
        
        for holiday in project_data['holidays']:
            self.selected_holidays.add(holiday)
            date_obj = QDate.fromString(holiday, 'yyyy-MM-dd')
            item = QListWidgetItem(date_obj.toString("dd/MM/yyyy"))
            item.setData(Qt.ItemDataRole.UserRole, holiday)
            self.holiday_list.addItem(item)
        
        for subject_data in project_data['subjects']:
            self.add_subject_to_table(
                subject_data['name'],
                subject_data['conducted'],
                subject_data['weekly'],
                subject_data['days']
            )

class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setModal(True)
        self.resize(400, 200)
        
        layout = QFormLayout()
        
        self.auto_save_cb = QCheckBox("Enable auto-save")
        layout.addRow("Auto-save:", self.auto_save_cb)
        
        self.weeks_spin = QSpinBox()
        self.weeks_spin.setRange(10, 30)
        self.weeks_spin.setValue(15)
        layout.addRow("Default weeks:", self.weeks_spin)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)


