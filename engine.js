// Date Diff engine - gaps between dates, dates plus or minus a span, and birthdays.
// Mirrored by oracle.py; keep the op order identical.
// Dates are YYYY-MM-DD, real Gregorian calendar dates from 1900-01-01 to 2100-12-31.
// Whole months from a start date clamp to the last day of a shorter month (31 Jan plus 1 month is 29 Feb 2024).

var DATE_ERR = "date must be a real calendar date written YYYY-MM-DD, from 1900-01-01 to 2100-12-31";
var WEEKDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

function _leap(y) { return (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0; }
function _dim(y, m) { return [31, _leap(y) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]; }

// Days since 1970-01-01 for a civil date.
function _days(y, m, d) {
  var yy = m <= 2 ? y - 1 : y;
  var era = Math.floor(yy / 400);
  var yoe = yy - era * 400;
  var doy = Math.floor((153 * (m + (m > 2 ? -3 : 9)) + 2) / 5) + d - 1;
  var doe = yoe * 365 + Math.floor(yoe / 4) - Math.floor(yoe / 100) + doy;
  return era * 146097 + doe - 719468;
}
function _civil(z) {
  z += 719468;
  var era = Math.floor(z / 146097);
  var doe = z - era * 146097;
  var yoe = Math.floor((doe - Math.floor(doe / 1460) + Math.floor(doe / 36524) - Math.floor(doe / 146096)) / 365);
  var y = yoe + era * 400;
  var doy = doe - (365 * yoe + Math.floor(yoe / 4) - Math.floor(yoe / 100));
  var mp = Math.floor((5 * doy + 2) / 153);
  var d = doy - Math.floor((153 * mp + 2) / 5) + 1;
  var m = mp + (mp < 10 ? 3 : -9);
  return { y: m <= 2 ? y + 1 : y, m: m, d: d };
}

function _date(text) {
  var t = typeof text === "string" ? text.trim() : "";
  var m = /^([0-9]{4})-([0-9]{2})-([0-9]{2})$/.exec(t);
  if (!m) throw new Error(DATE_ERR);
  var y = +m[1], mo = +m[2], d = +m[3];
  if (y < 1900 || y > 2100 || mo < 1 || mo > 12 || d < 1 || d > _dim(y, mo)) throw new Error(DATE_ERR);
  return { y: y, m: mo, d: d, n: _days(y, mo, d) };
}

function _pad(n, w) { var s = String(n); while (s.length < w) s = "0" + s; return s; }
function _iso(c) { return _pad(c.y, 4) + "-" + _pad(c.m, 2) + "-" + _pad(c.d, 2); }
function _wd(n) { return WEEKDAYS[(((n + 4) % 7) + 7) % 7]; }
function _pl(n, w) { return n + " " + w + (n === 1 ? "" : "s"); }

// A date plus k whole months, clamped to the month's last day.
function _addMonths(c, k) {
  var total = c.y * 12 + (c.m - 1) + k;
  var ny = Math.floor(total / 12), nm = total - ny * 12 + 1;
  var nd = Math.min(c.d, _dim(ny, nm));
  return { y: ny, m: nm, d: nd, n: _days(ny, nm, nd), clamped: nd !== c.d };
}

function _list(parts) {
  if (parts.length === 0) return "0 days";
  if (parts.length === 1) return parts[0];
  return parts.slice(0, -1).join(", ") + " and " + parts[parts.length - 1];
}
function _ymd(from, to) {
  var m0 = (to.y * 12 + to.m) - (from.y * 12 + from.m);
  if (_addMonths(from, m0).n > to.n) m0 -= 1;
  var days = to.n - _addMonths(from, m0).n;
  var years = Math.floor(m0 / 12), months = m0 - years * 12;
  var parts = [];
  if (years) parts.push(_pl(years, "year"));
  if (months) parts.push(_pl(months, "month"));
  if (days) parts.push(_pl(days, "day"));
  return _list(parts);
}

// The gap truth: days between two dates, and the same gap in whole years, months and days.
function gapTruth(from, to) {
  var a = _date(from), b = _date(to);
  if (b.n < a.n) throw new Error("the end date must be on or after the start date");
  var n = b.n - a.n;
  return "From " + _iso(a) + " to " + _iso(b) + " is " + _pl(n, "day") + " (" + _pl(Math.floor(n / 7), "week") + " and " + _pl(n % 7, "day") +
    "), or " + _ymd(a, b) + " in whole years, months and days. Counting both end dates it is " + _pl(n + 1, "day") + ".";
}

// The add truth: a date a span after or before another date.
function addTruth(date, count, unit, dir) {
  var a = _date(date);
  var t = typeof count === "string" ? count.trim() : "";
  if (!/^[0-9]{1,6}$/.test(t)) throw new Error("count must be a whole number from 0 to 100000");
  var k = +t;
  if (k > 100000) throw new Error("count must be a whole number from 0 to 100000");
  if (["day", "week", "month", "year"].indexOf(unit) < 0) throw new Error("unit must be one of day, week, month, year");
  if (dir !== "after" && dir !== "before") throw new Error("direction must be after or before");
  var s = dir === "after" ? 1 : -1, r, clamped = false;
  if (unit === "day" || unit === "week") {
    var cv = _civil(a.n + s * k * (unit === "week" ? 7 : 1));
    r = { y: cv.y, m: cv.m, d: cv.d, n: _days(cv.y, cv.m, cv.d) };
  } else {
    r = _addMonths(a, s * k * (unit === "year" ? 12 : 1));
    clamped = r.clamped;
  }
  if (r.y < 1900 || r.y > 2100) throw new Error("that lands outside 1900 to 2100");
  return _pl(k, unit) + " " + dir + " " + _iso(a) + " (a " + _wd(a.n) + ") is " + _iso(r) + ", a " + _wd(r.n) +
    (clamped ? " (day " + a.d + " does not exist in that month, so it lands on the month's last day)." : ".");
}

// The birthday truth: age on a date and the next birthday.
function birthdayTruth(birth, on) {
  var b = _date(birth), o = _date(on);
  if (o.n < b.n) throw new Error("the birth date must be on or before the other date");
  var bday = function (y) { return { y: y, m: b.m, d: b.m === 2 && b.d === 29 && !_leap(y) ? 28 : b.d }; };
  var nb = bday(o.y);
  nb.n = _days(nb.y, nb.m, nb.d);
  if (nb.n < o.n) { nb = bday(o.y + 1); nb.n = _days(nb.y, nb.m, nb.d); }
  var age = nb.y - b.y;
  var s = "Born " + _iso(b) + ", the age on " + _iso(o) + " is " + _ymd(b, o) + ". ";
  if (nb.n === o.n) s += "The birthday is today, " + _iso(nb) + ", a " + _wd(nb.n) + ", and the age is " + age + ".";
  else s += "The next birthday is " + _iso(nb) + ", a " + _wd(nb.n) + ", in " + _pl(nb.n - o.n, "day") + ", when the age is " + age + ".";
  if (b.m === 2 && b.d === 29) s += " A 29 Feb birthday is counted on 28 Feb in years without a 29 Feb.";
  return s;
}
