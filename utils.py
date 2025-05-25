from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import re

def parse_natural_date(text: str) -> str:
    today = datetime.today()

    if "오늘" in text:
        return today.strftime("%Y-%m-%d")
    elif "어제" in text:
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")
    elif "그제" in text:
        return (today - timedelta(days=2)).strftime("%Y-%m-%d")
    elif "이번 주" in text or "이번주" in text:
        start = today - timedelta(days=today.weekday())
        return start.strftime("%Y-%m-%d")
    elif "지난 주" in text or "지난주" in text:
        last_week = today - timedelta(days=today.weekday() + 7)
        return last_week.strftime("%Y-%m-%d")
    elif match := re.search(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일", text):
        y, m, d = map(int, match.groups())
        return datetime(y, m, d).strftime("%Y-%m-%d")
    else:
        return None