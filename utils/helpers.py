"""
توابع کمکی برنامه
"""

from datetime import datetime, timedelta


# ===== تبدیل اعداد به فارسی =====
_FA_DIGITS = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')

def to_persian_num(n):
    return str(n).translate(_FA_DIGITS)


# ===== تبدیل تاریخ =====
WEEKDAYS_FA = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یکشنبه']
MONTHS_FA   = ['', 'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
               'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']

def format_date_fa(dt: datetime) -> str:
    """نمایش تاریخ میلادی به صورت فارسی خوانا"""
    weekday = WEEKDAYS_FA[dt.weekday()]
    return f"{weekday} {to_persian_num(dt.day)} / {to_persian_num(dt.month)} / {to_persian_num(dt.year)}"


def days_until(iso_str: str) -> int:
    """تعداد روز تا تاریخ داده‌شده"""
    try:
        target = datetime.fromisoformat(iso_str)
        delta = (target - datetime.now()).days
        return delta
    except Exception:
        return 0


def relative_time_fa(iso_str: str) -> str:
    """نمایش زمان نسبی فارسی"""
    days = days_until(iso_str)
    if days < 0:
        return f'{to_persian_num(abs(days))} روز گذشته'
    if days == 0:
        return 'امروز!'
    if days == 1:
        return 'فردا'
    return f'{to_persian_num(days)} روز دیگر'


# ===== مدیریت تایمر =====
def next_due_date(interval_days: int) -> str:
    return (datetime.now() + timedelta(days=interval_days)).isoformat()


def is_overdue(iso_str: str) -> bool:
    try:
        return datetime.fromisoformat(iso_str) < datetime.now()
    except Exception:
        return False


# ===== رنگ سطح مراقبت =====
CARE_COLOR = {
    'بسیار آسان': '#43A047',
    'آسان':        '#66BB6A',
    'متوسط':       '#FFA726',
    'سخت':         '#EF5350',
}

def care_color(level: str) -> str:
    for k, v in CARE_COLOR.items():
        if k in level:
            return v
    return '#757575'


# ===== اعتبارسنجی فیلدها =====
def validate_plant_form(data: dict) -> tuple:
    """
    Returns (is_valid: bool, error_message: str)
    """
    name = data.get('name', '').strip()
    if not name:
        return False, 'نام گیاه نمی‌تواند خالی باشد.'
    if len(name) < 2:
        return False, 'نام گیاه باید حداقل ۲ حرف داشته باشد.'
    return True, ''


def validate_timer_form(data: dict) -> tuple:
    name = data.get('name', '').strip()
    if not name:
        return False, 'نام تایمر نمی‌تواند خالی باشد.'
    interval = data.get('interval_days', 0)
    try:
        interval = int(interval)
    except Exception:
        return False, 'فاصله زمانی باید عدد باشد.'
    if interval < 1:
        return False, 'فاصله زمانی باید حداقل ۱ روز باشد.'
    return True, ''


# ===== آیکون دسته‌بندی =====
CATEGORY_ICON = {
    'آپارتمانی': '🌿',
    'گلدار':      '🌸',
    'دارویی':     '🌱',
    'درخت میوه': '🍎',
}

def category_icon(cat: str) -> str:
    return CATEGORY_ICON.get(cat, '🌿')


# ===== ساخت متن خلاصه گیاه =====
def plant_summary(plant: dict) -> str:
    parts = []
    if plant.get('care_level'):
        parts.append(f"نگهداری: {plant['care_level']}")
    if plant.get('watering'):
        parts.append(f"آبیاری: {plant['watering']}")
    if plant.get('light'):
        parts.append(f"نور: {plant['light']}")
    return '  •  '.join(parts)
