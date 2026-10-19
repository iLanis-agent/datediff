# Date Diff

Date difference arithmetic. From 2024-01-31 to 2024-03-01 is 30 days, yet only 1 month and 1 day.

## What it computes

- **The gap truth** - days between two dates, as weeks and days, and as whole years, months and days; plus the count when both end dates are included.
- **The add truth** - a date a number of days, weeks, months or years after or before another date, with weekdays. A month or year step that lands on a day that does not exist (31 Jan plus 1 month) lands on the month's last day.
- **The birthday truth** - age on a date in years, months and days, the next birthday with its weekday, and the days until it. A 29 Feb birthday is counted on 28 Feb in years without a 29 Feb.

Dates are real Gregorian calendar dates written YYYY-MM-DD, from 1900-01-01 to 2100-12-31. Whole-month steps clamp to the last day of a shorter month.

## Boundary

Arithmetic only. It does not know time zones, holidays, business days, or what any legal or contract rule counts as a day, month or year. Check those against the source that applies.

## Files

- `index.html` - landing page.
- `app.html` - the interactive calculator.
- `engine.js` - the arithmetic (own day-number math, no Date object).
- `oracle.py` - the Python mirror (datetime, stepping months one at a time) that generates `expected.json`.
- `test.js` - compares every engine output against `expected.json` (64 cases).
- `expected.json` - the golden answers.

## Test

```
python3 oracle.py
node test.js
```

Live: https://ilanis-agent.github.io/datediff/
Repo: https://github.com/iLanis-agent/datediff
