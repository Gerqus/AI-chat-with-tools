from datetime import datetime

def get_current_time() -> str:
    return f"Current date and time on user computer in format YYYY-MM-DD HH:MM:SS is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
