import datetime
from utils import count_specific_days

def calculate_summary(subjects_data, last_date, holidays):
    """Calculate class summary with day-specific scheduling"""
    try:
        today = datetime.date.today()
        
        if last_date <= today:
            raise ValueError("Last date must be in the future")
        
        summary_lines = []
        total_required = 0
        total_conducted = 0
        total_extra_needed = 0
        
        for subject, data in subjects_data.items():
            conducted = data['conducted']
            weekly_slots = data['weekly_slots']
            days_schedule = data['days_schedule']
            
            # Parse days schedule: "Mon-2,Tue-1,Thu-2"
            schedule_dict = {}
            for part in days_schedule.split(','):
                day, count = part.strip().split('-')
                schedule_dict[day] = int(count)
            
            # Calculate total required (15 weeks)
            required = weekly_slots * 15
            
            # Calculate remaining classes based on specific days
            remaining_regular = 0
            missed_in_holidays = 0
            
            for day, classes_per_day in schedule_dict.items():
                # Count remaining days of this type
                remaining_days = count_specific_days(today, last_date, day, holidays)
                total_days_possible = count_specific_days(today, last_date, day, [])
                
                remaining_regular += remaining_days * classes_per_day
                missed_in_holidays += (total_days_possible - remaining_days) * classes_per_day
            
            # Calculate extra needed
            extra_needed = max(0, required - conducted - remaining_regular)
            
            total_required += required
            total_conducted += conducted
            total_extra_needed += extra_needed
            
            status = "✅" if extra_needed == 0 else "⚠️" if extra_needed <= 2 else "❌"
            
            summary_lines.append(
                f"{status} {subject}:\n"
                f"  Total Required: {required}\n"
                f"  Conducted Till Now: {conducted}\n"
                f"  Remaining: {required - conducted}\n"
                f"  Will be conducted regularly: {remaining_regular}\n"
                f"  Missed due to holidays: {missed_in_holidays}\n"
                f"  Extra classes needed: {extra_needed}\n"
            )
        
        header = [
            "📊 CLASS SUMMARY (Day-wise Calculation)",
            f"Generated: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}",
            f"Semester End: {last_date.strftime('%d/%m/%Y')}",
            f"Holidays: {len(holidays)}",
            ""
        ]
        
        footer = [
            "📈 TOTALS:",
            f"Total Required: {total_required}",
            f"Total Conducted: {total_conducted}",
            f"Total Extra Needed: {total_extra_needed}"
        ]
        
        return "\n".join(header + summary_lines + footer)
        
    except Exception as e:
        return f"Error: {str(e)}"