import datetime
from datetime import date, timedelta

def count_specific_days(start, end, day_name, holidays):
    """Count specific days (Mon, Tue, etc.) between dates excluding holidays"""
    day_mapping = {
        'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6
    }
    
    target_weekday = day_mapping[day_name]
    holiday_dates = set()
    
    # Convert holiday strings to date objects
    for holiday in holidays:
        try:
            holiday_date = datetime.date.fromisoformat(holiday.strip())
            holiday_dates.add(holiday_date)
        except ValueError:
            continue
    
    count = 0
    current = start + timedelta(days=1)  # Start from tomorrow
    
    while current <= end:
        if current.weekday() == target_weekday and current not in holiday_dates:
            count += 1
        current += timedelta(days=1)
    
    return count