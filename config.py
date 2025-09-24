import json
from pathlib import Path
from datetime import date

class Config:
    def __init__(self):
        self.config_path = Path("config.json")
        self.default_config = {
            "app": {
                "name": "Extra Class Counter",
                "version": "1.0.0",
                "semester_weeks": 15,
                "lab_duration": 2
            },
            "paths": {
                "model_path": "models/timetable_reader.pt",
                "export_dir": "exports",
                "data_dir": "data"
            },
            "defaults": {
                "holidays": [
                    "2024-10-02",  # Gandhi Jayanti
                    "2024-12-25"   # Christmas
                ],
                "working_days": [0, 1, 2, 3, 4],  # Monday to Friday
                "weekly_hours": 40
            },
            "ocr": {
                "confidence_threshold": 0.7,
                "lab_width_threshold": 150,
                "fallback_ocr": True
            }
        }
        self.data = self.default_config.copy()
        self.load()
    
    def load(self):
        """Load configuration from file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self._deep_update(self.data, saved_config)
            else:
                self.save()  # Create default config file
        except Exception as e:
            print(f"Error loading config: {e}, using defaults")
    
    def save(self):
        """Save configuration to file"""
        try:
            # Create directory if it doesn't exist
            self.config_path.parent.mkdir(exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def _deep_update(self, original, update):
        """Recursively update nested dictionaries"""
        for key, value in update.items():
            if isinstance(value, dict) and key in original:
                self._deep_update(original[key], value)
            else:
                original[key] = value
    
    def get(self, key_path, default=None):
        """Get configuration value by dot-separated path"""
        keys = key_path.split('.')
        value = self.data
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path, value):
        """Set configuration value by dot-separated path"""
        keys = key_path.split('.')
        current = self.data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
        self.save()
    
    @property
    def semester_weeks(self):
        return self.get("app.semester_weeks", 15)
    
    @property
    def lab_duration(self):
        return self.get("app.lab_duration", 2)
    
    @property
    def default_holidays(self):
        return self.get("defaults.holidays", [])
    
    def add_default_holiday(self, date_str):
        """Add a holiday to default list"""
        holidays = self.default_holidays
        if date_str not in holidays:
            holidays.append(date_str)
            self.set("defaults.holidays", holidays)
