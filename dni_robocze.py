#!/usr/bin/env python3
"""Polski kalkulator dni roboczych / Polish Work Days Calculator.

Calculates work days in Poland accounting for weekends and all 13 Polish
public holidays. Easter dates are hardcoded for years 2020-2030.
"""

import argparse
import datetime
import sys

# Hardcoded Easter Sunday dates for 2020-2030
EASTER_DATES = {
    2020: datetime.date(2020, 4, 12),
    2021: datetime.date(2021, 4, 4),
    2022: datetime.date(2022, 4, 17),
    2023: datetime.date(2023, 4, 9),
    2024: datetime.date(2024, 3, 31),
    2025: datetime.date(2025, 4, 20),
    2026: datetime.date(2026, 4, 5),
    2027: datetime.date(2027, 3, 28),
    2028: datetime.date(2028, 4, 16),
    2029: datetime.date(2029, 4, 1),
    2030: datetime.date(2030, 4, 21),
}

SUPPORTED_YEARS = sorted(EASTER_DATES.keys())


def get_holidays(year):
    """Return a set of datetime.date for all 13 Polish public holidays in a given year."""
    if year not in EASTER_DATES:
        raise ValueError(
            f"Rok {year} nie jest obsługiwany. "
            f"Obsługiwane lata: {SUPPORTED_YEARS[0]}-{SUPPORTED_YEARS[-1]}."
        )

    easter = EASTER_DATES[year]

    holidays = {
        # Fixed-date holidays
        datetime.date(year, 1, 1),    # Nowy Rok
        datetime.date(year, 1, 6),    # Trzech Króli
        datetime.date(year, 5, 1),    # Święto Pracy
        datetime.date(year, 5, 3),    # Święto Konstytucji 3 Maja
        datetime.date(year, 8, 15),   # Wniebowzięcie NMP
        datetime.date(year, 11, 1),   # Wszystkich Świętych
        datetime.date(year, 11, 11),  # Święto Niepodległości
        datetime.date(year, 12, 25),  # Boże Narodzenie (pierwszy dzień)
        datetime.date(year, 12, 26),  # Boże Narodzenie (drugi dzień)
        # Moveable holidays (Easter-dependent)
        easter,                                          # Wielkanoc
        easter + datetime.timedelta(days=1),             # Poniedziałek Wielkanocny
        easter + datetime.timedelta(days=49),            # Zielone Świątki
        easter + datetime.timedelta(days=60),            # Boże Ciało
    }

    return holidays


HOLIDAY_NAMES = [
    (1, 1, "Nowy Rok"),
    (1, 6, "Trzech Króli"),
    (5, 1, "Święto Pracy"),
    (5, 3, "Święto Konstytucji 3 Maja"),
    (8, 15, "Wniebowzięcie NMP"),
    (11, 1, "Wszystkich Świętych"),
    (11, 11, "Święto Niepodległości"),
    (12, 25, "Boże Narodzenie (pierwszy dzień)"),
    (12, 26, "Boże Narodzenie (drugi dzień)"),
]


def get_holidays_with_names(year):
    """Return a sorted list of (date, name) tuples for all holidays in a year."""
    if year not in EASTER_DATES:
        raise ValueError(
            f"Rok {year} nie jest obsługiwany. "
            f"Obsługiwane lata: {SUPPORTED_YEARS[0]}-{SUPPORTED_YEARS[-1]}."
        )

    easter = EASTER_DATES[year]

    result = []
    for month, day, name in HOLIDAY_NAMES:
        result.append((datetime.date(year, month, day), name))

    result.append((easter, "Wielkanoc"))
    result.append((easter + datetime.timedelta(days=1), "Poniedziałek Wielkanocny"))
    result.append((easter + datetime.timedelta(days=49), "Zielone Świątki"))
    result.append((easter + datetime.timedelta(days=60), "Boże Ciało"))

    result.sort(key=lambda x: x[0])
    return result


def is_workday(date):
    """Return True if the given date is a work day (not weekend, not holiday)."""
    if date.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    try:
        holidays = get_holidays(date.year)
    except ValueError:
        raise
    return date not in holidays


def count_workdays(start, end):
    """Count work days in the inclusive range [start, end]."""
    if start > end:
        raise ValueError("Data początkowa nie może być późniejsza niż data końcowa.")

    years_needed = set(range(start.year, end.year + 1))
    all_holidays = set()
    for y in years_needed:
        all_holidays.update(get_holidays(y))

    count = 0
    current = start
    one_day = datetime.timedelta(days=1)
    while current <= end:
        if current.weekday() < 5 and current not in all_holidays:
            count += 1
        current += one_day
    return count


def add_workdays(start, n):
    """Add (or subtract if negative) n work days to start date.

    Returns the resulting date. The start date itself is NOT counted —
    we move forward/backward n work days from the start.
    """
    if n == 0:
        return start

    direction = 1 if n > 0 else -1
    remaining = abs(n)
    current = start
    one_day = datetime.timedelta(days=direction)

    while remaining > 0:
        current += one_day
        try:
            if is_workday(current):
                remaining -= 1
        except ValueError:
            raise ValueError(
                f"Wyszliśmy poza obsługiwany zakres lat "
                f"({SUPPORTED_YEARS[0]}-{SUPPORTED_YEARS[-1]})."
            )

    return current


DAY_NAMES_PL = {
    0: "poniedziałek",
    1: "wtorek",
    2: "środa",
    3: "czwartek",
    4: "piątek",
    5: "sobota",
    6: "niedziela",
}


def parse_date(date_str):
    """Parse a date string in YYYY-MM-DD format."""
    try:
        return datetime.date.fromisoformat(date_str)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Nieprawidłowy format daty: '{date_str}'. Użyj formatu YYYY-MM-DD."
        )


def cmd_count(args):
    """Handle the 'count' subcommand."""
    start = args.start
    end = args.end
    try:
        result = count_workdays(start, end)
    except ValueError as e:
        print(f"Błąd: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"Dni robocze od {start} do {end}: {result}")


def cmd_holidays(args):
    """Handle the 'holidays' subcommand."""
    year = args.year
    try:
        holidays = get_holidays_with_names(year)
    except ValueError as e:
        print(f"Błąd: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Święta ustawowe w {year} roku:")
    print(f"{'Data':<14} {'Dzień tygodnia':<16} Nazwa")
    print("-" * 56)
    for date, name in holidays:
        day_name = DAY_NAMES_PL[date.weekday()]
        print(f"{date}     {day_name:<16} {name}")


def cmd_add(args):
    """Handle the 'add' subcommand."""
    start = args.start
    n = args.days
    try:
        result = add_workdays(start, n)
    except ValueError as e:
        print(f"Błąd: {e}", file=sys.stderr)
        sys.exit(1)

    direction = "dodaniu" if n >= 0 else "odjęciu"
    day_name = DAY_NAMES_PL[result.weekday()]
    print(f"Po {direction} {abs(n)} dni roboczych od {start}: {result} ({day_name})")


def main():
    parser = argparse.ArgumentParser(
        description="Kalkulator dni roboczych w Polsce (uwzględnia weekendy i święta)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # count
    p_count = subparsers.add_parser(
        "count", help="Policz dni robocze między dwiema datami (włącznie)."
    )
    p_count.add_argument("start", type=parse_date, help="Data początkowa (YYYY-MM-DD)")
    p_count.add_argument("end", type=parse_date, help="Data końcowa (YYYY-MM-DD)")
    p_count.set_defaults(func=cmd_count)

    # holidays
    p_holidays = subparsers.add_parser(
        "holidays", help="Wyświetl święta ustawowe w danym roku."
    )
    p_holidays.add_argument("year", type=int, help="Rok (2020-2030)")
    p_holidays.set_defaults(func=cmd_holidays)

    # add
    p_add = subparsers.add_parser(
        "add", help="Dodaj/odejmij dni robocze od daty."
    )
    p_add.add_argument("start", type=parse_date, help="Data początkowa (YYYY-MM-DD)")
    p_add.add_argument("days", type=int, help="Liczba dni roboczych (ujemna = odejmij)")
    p_add.set_defaults(func=cmd_add)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
