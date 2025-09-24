import json
import csv
from datetime import datetime, date
from pathlib import Path
from config import Config

class DataManager:
    def __init__(self):
        self.config = Config()
        self.data_dir = Path(self.config.get("paths.data_dir", "data"))
        self.data_dir.mkdir(exist_ok=True)
        
        self.history_file = self.data_dir / "calculations_history.json"
        self.subjects_file = self.data_dir / "subjects_database.json"
        
        self.initialize_files()
    
    def initialize_files(self):
        """Initialize data files with empty structures if they don't exist"""
        if not self.history_file.exists():
            with open(self.history_file, 'w') as f:
                json.dump([], f, indent=2)
        
        if not self.subjects_file.exists():
            with open(self.subjects_file, 'w') as f:
                json.dump({}, f, indent=2)
    
    def save_calculation(self, subjects, conducted, last_date, holidays, summary):
        """Save a calculation to history"""
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
            
            calculation = {
                "timestamp": datetime.now().isoformat(),
                "subjects": subjects,
                "conducted": conducted,
                "last_date": last_date.isoformat(),
                "holidays": holidays,
                "summary": summary,
                "metadata": {
                    "total_subjects": len(subjects),
                    "total_conducted": sum(conducted.values()),
                    "total_required": sum(subjects.values()) * self.config.semester_weeks
                }
            }
            
            history.append(calculation)
            
            # Keep only last 100 calculations
            if len(history) > 100:
                history = history[-100:]
            
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            # Update subjects database
            self.update_subjects_database(subjects)
            
        except Exception as e:
            print(f"Error saving calculation: {e}")
    
    def update_subjects_database(self, subjects):
        """Update the subjects database with new subjects"""
        try:
            with open(self.subjects_file, 'r') as f:
                subjects_db = json.load(f)
            
            for subject, weekly_slots in subjects.items():
                if subject in subjects_db:
                    subjects_db[subject]["count"] += 1
                    subjects_db[subject]["last_seen"] = date.today().isoformat()
                    # Update weekly slots average
                    current_avg = subjects_db[subject].get("avg_weekly_slots", 0)
                    new_avg = (current_avg * (subjects_db[subject]["count"] - 1) + weekly_slots) / subjects_db[subject]["count"]
                    subjects_db[subject]["avg_weekly_slots"] = round(new_avg, 1)
                else:
                    subjects_db[subject] = {
                        "count": 1,
                        "first_seen": date.today().isoformat(),
                        "last_seen": date.today().isoformat(),
                        "avg_weekly_slots": weekly_slots
                    }
            
            with open(self.subjects_file, 'w') as f:
                json.dump(subjects_db, f, indent=2)
                
        except Exception as e:
            print(f"Error updating subjects database: {e}")
    
    def get_calculation_history(self, limit=10):
        """Get recent calculation history"""
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
            
            return history[-limit:]
        except Exception as e:
            print(f"Error reading history: {e}")
            return []
    
    def export_to_csv(self, filepath, calculations=None):
        """Export calculations to CSV format"""
        try:
            if calculations is None:
                calculations = self.get_calculation_history(limit=100)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    'Timestamp', 'Subject', 'Weekly Slots', 'Conducted', 
                    'Last Date', 'Holidays', 'Summary'
                ])
                
                # Write data
                for calc in calculations:
                    for subject, weekly in calc['subjects'].items():
                        writer.writerow([
                            calc['timestamp'],
                            subject,
                            weekly,
                            calc['conducted'].get(subject, 0),
                            calc['last_date'],
                            ', '.join(calc['holidays']),
                            calc['summary'].replace('\n', '; ')
                        ])
            
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def get_subject_statistics(self):
        """Get statistics about detected subjects"""
        try:
            with open(self.subjects_file, 'r') as f:
                subjects_db = json.load(f)
            
            return {
                "total_subjects": len(subjects_db),
                "most_common": sorted(
                    [(sub, data["count"]) for sub, data in subjects_db.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:10],
                "recently_added": [
                    sub for sub, data in sorted(
                        subjects_db.items(),
                        key=lambda x: x[1]["last_seen"],
                        reverse=True
                    )[:5]
                ]
            }
        except Exception as e:
            print(f"Error getting subject statistics: {e}")
            return {}
