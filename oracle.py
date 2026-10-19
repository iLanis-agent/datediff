#!/usr/bin/env python3
# Date Diff oracle - mirrors engine.js using datetime.date, with whole-month gaps found by stepping up one month at a time.
import json, re, calendar
from datetime import date, timedelta

DATE_ERR = "date must be a real calendar date written YYYY-MM-DD, from 1900-01-01 to 2100-12-31"

def _date(text):
    t = text.strip() if isinstance(text, str) else ""
    m = re.fullmatch(r"([0-9]{4})-([0-9]{2})-([0-9]{2})", t)
    if not m:
        raise ValueError(DATE_ERR)
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if y < 1900 or y > 2100 or mo < 1 or mo > 12 or d < 1 or d > calendar.monthrange(y, mo)[1]:
        raise ValueError(DATE_ERR)
    return date(y, mo, d)

def pl(n, w): return f"{n} {w}" + ("" if n == 1 else "s")

def add_months(dt, k):
    total = dt.year * 12 + (dt.month - 1) + k
    ny, nm = divmod(total, 12)
    nm += 1
    nd = min(dt.day, calendar.monthrange(ny, nm)[1])
    return date(ny, nm, nd), nd != dt.day

def lst(parts):
    if not parts: return "0 days"
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]

def ymd(a, b):
    m = 0
    while add_months(a, m + 1)[0] <= b:  # step up month by month
        m += 1
    days = (b - add_months(a, m)[0]).days
    years, months = divmod(m, 12)
    parts = []
    if years: parts.append(pl(years, "year"))
    if months: parts.append(pl(months, "month"))
    if days: parts.append(pl(days, "day"))
    return lst(parts)

def wd(dt): return dt.strftime("%A")
def iso(dt): return f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d}"

def gap_truth(frm, to):
    a = _date(frm); b = _date(to)
    if b < a:
        raise ValueError("the end date must be on or after the start date")
    n = (b - a).days
    return (f"From {iso(a)} to {iso(b)} is {pl(n, 'day')} ({pl(n // 7, 'week')} and {pl(n % 7, 'day')}), or {ymd(a, b)} "
            f"in whole years, months and days. Counting both end dates it is {pl(n + 1, 'day')}.")

def add_truth(dt, count, unit, direction):
    a = _date(dt)
    t = count.strip() if isinstance(count, str) else ""
    if not re.fullmatch(r"[0-9]{1,6}", t) or int(t) > 100000:
        raise ValueError("count must be a whole number from 0 to 100000")
    k = int(t)
    if unit not in ("day", "week", "month", "year"):
        raise ValueError("unit must be one of day, week, month, year")
    if direction not in ("after", "before"):
        raise ValueError("direction must be after or before")
    s = 1 if direction == "after" else -1
    clamped = False
    try:
        if unit in ("day", "week"):
            r = a + timedelta(days=s * k * (7 if unit == "week" else 1))
        else:
            r, clamped = add_months(a, s * k * (12 if unit == "year" else 1))
    except (OverflowError, ValueError):
        raise ValueError("that lands outside 1900 to 2100")
    if r.year < 1900 or r.year > 2100:
        raise ValueError("that lands outside 1900 to 2100")
    tail = f" (day {a.day} does not exist in that month, so it lands on the month's last day)." if clamped else "."
    return f"{pl(k, unit)} {direction} {iso(a)} (a {wd(a)}) is {iso(r)}, a {wd(r)}{tail}"

def birthday_truth(birth, on):
    b = _date(birth); o = _date(on)
    if o < b:
        raise ValueError("the birth date must be on or before the other date")
    def bday(y):
        if b.month == 2 and b.day == 29 and not calendar.isleap(y):
            return date(y, 2, 28)
        return date(y, b.month, b.day)
    nb = bday(o.year)
    if nb < o:
        nb = bday(o.year + 1)
    age = nb.year - b.year
    s = f"Born {iso(b)}, the age on {iso(o)} is {ymd(b, o)}. "
    if nb == o:
        s += f"The birthday is today, {iso(nb)}, a {wd(nb)}, and the age is {age}."
    else:
        s += f"The next birthday is {iso(nb)}, a {wd(nb)}, in {pl((nb - o).days, 'day')}, when the age is {age}."
    if b.month == 2 and b.day == 29:
        s += " A 29 Feb birthday is counted on 28 Feb in years without a 29 Feb."
    return s

FNS = {"gapTruth": gap_truth, "addTruth": add_truth, "birthdayTruth": birthday_truth}
CASES = [
    ("gapTruth", ["2024-01-31", "2024-03-01"]), ("gapTruth", ["2024-02-28", "2024-03-01"]), ("gapTruth", ["2023-02-28", "2023-03-01"]), ("gapTruth", ["2024-05-15", "2024-05-15"]),
    ("gapTruth", ["2024-05-15", "2024-05-16"]), ("gapTruth", ["2000-01-01", "2024-12-31"]), ("gapTruth", ["1900-01-01", "2100-12-31"]), ("gapTruth", ["2024-12-31", "2025-01-01"]),
    ("gapTruth", ["2023-01-31", "2023-02-28"]), ("gapTruth", ["2023-01-31", "2023-03-31"]), ("gapTruth", ["2024-02-29", "2025-02-28"]), ("gapTruth", ["2024-02-29", "2028-02-29"]),
    ("gapTruth", ["2020-01-01", "2021-01-01"]), ("gapTruth", ["2024-03-10", "2024-03-17"]), ("gapTruth", [" 2024-03-10 ", "2024-03-24"]), ("gapTruth", ["2024-03-31", "2024-04-30"]),
    ("gapTruth", ["2024-03-02", "2024-03-01"]), ("gapTruth", ["2023-02-30", "2023-03-01"]), ("gapTruth", ["2024-1-5", "2024-03-01"]), ("gapTruth", ["1899-12-31", "2024-03-01"]),
    ("gapTruth", ["2024-03-01", "2101-01-01"]), ("gapTruth", ["abc", "2024-03-01"]), ("gapTruth", ["2024-13-01", "2024-03-01"]), ("gapTruth", ["1900-02-29", "2024-03-01"]),
    ("addTruth", ["2024-01-31", "1", "month", "after"]), ("addTruth", ["2024-01-31", "30", "day", "after"]), ("addTruth", ["2024-03-01", "1", "day", "before"]), ("addTruth", ["2024-02-29", "1", "year", "after"]),
    ("addTruth", ["2024-02-29", "4", "year", "after"]), ("addTruth", ["2024-05-15", "2", "week", "after"]), ("addTruth", ["2024-05-15", "0", "day", "after"]), ("addTruth", ["2024-05-31", "3", "month", "before"]),
    ("addTruth", ["2024-12-31", "1", "day", "after"]), ("addTruth", ["2024-01-01", "1", "day", "before"]), ("addTruth", ["2024-03-31", "1", "month", "before"]), ("addTruth", ["2000-01-01", "100000", "day", "after"]),
    ("addTruth", ["2000-01-01", "1200", "month", "after"]), ("addTruth", ["2100-12-31", "1", "day", "after"]), ("addTruth", ["1900-01-01", "1", "day", "before"]), ("addTruth", ["2024-05-15", "100", "year", "after"]),
    ("addTruth", ["2024-05-15", "1.5", "day", "after"]), ("addTruth", ["2024-05-15", "-1", "day", "after"]), ("addTruth", ["2024-05-15", "100001", "day", "after"]), ("addTruth", ["2024-05-15", "5", "fortnight", "after"]),
    ("addTruth", ["2024-05-15", "5", "day", "around"]), ("addTruth", ["nope", "5", "day", "after"]), ("addTruth", ["2024-05-15", "1", "day", "after"]), ("addTruth", ["2023-01-29", "1", "month", "after"]),
    ("birthdayTruth", ["1990-05-15", "2024-05-14"]), ("birthdayTruth", ["1990-05-15", "2024-05-15"]), ("birthdayTruth", ["1990-05-15", "2024-05-16"]), ("birthdayTruth", ["2000-02-29", "2023-03-01"]),
    ("birthdayTruth", ["2000-02-29", "2024-02-29"]), ("birthdayTruth", ["2000-02-29", "2024-02-28"]), ("birthdayTruth", ["2024-05-15", "2024-05-15"]), ("birthdayTruth", ["2024-05-15", "2024-05-16"]),
    ("birthdayTruth", ["1900-01-01", "2100-12-31"]), ("birthdayTruth", ["1990-12-31", "2024-12-31"]), ("birthdayTruth", ["1990-12-31", "2024-12-30"]), ("birthdayTruth", ["1990-01-01", "2024-12-31"]),
    ("birthdayTruth", ["2000-02-29", "2100-12-31"]), ("birthdayTruth", ["2024-05-16", "2024-05-15"]), ("birthdayTruth", ["x", "2024-05-15"]), ("birthdayTruth", ["1990-05-15", "2101-01-01"]),
]

out = []
for fn, args in CASES:
    try:
        exp = FNS[fn](*args)
    except ValueError as e:
        exp = "ERR:" + str(e)
    out.append({"fn": fn, "args": args, "expected": exp})
with open("expected.json", "w") as f:
    json.dump(out, f, indent=1)
    f.write("\n")
print(len(out), "cases")
