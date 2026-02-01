#!/usr/bin/env python3
"""Graficzny interfejs (tkinter) dla kalkulatora dni roboczych."""

import calendar
import datetime
import tkinter as tk
from tkinter import ttk

from dni_robocze import (
    DAY_NAMES_PL,
    SUPPORTED_YEARS,
    add_workdays,
    count_workdays,
    get_holidays,
    get_holidays_with_names,
)

# --- Color constants ---
COLOR_BG = "#ffffff"
COLOR_HEADER_BG = "#ebebeb"
COLOR_HOLIDAY = "#c62828"
COLOR_WEEKEND = "#757575"
COLOR_TODAY_BG = "#fff3e0"
COLOR_TODAY_FG = "#e65100"
COLOR_TODAY_BORDER = "#ffb300"
COLOR_SELECTED_BG = "#1565c0"
COLOR_SELECTED_FG = "#ffffff"
COLOR_NORMAL = "#212121"
COLOR_EMPTY = "#fafafa"
COLOR_HOVER_BG = "#e3f2fd"
COLOR_DAY_BG = "#ffffff"
COLOR_POPUP_BORDER = "#bdbdbd"
COLOR_RESULT_OK = "#1b5e20"
COLOR_RESULT_ERR = "#c62828"

DAY_HEADERS = ["Pn", "Wt", "Śr", "Cz", "Pt", "So", "Nd"]

MIN_YEAR = SUPPORTED_YEARS[0]
MAX_YEAR = SUPPORTED_YEARS[-1]

FONT_DAY = ("Helvetica", 12)
FONT_DAY_HEADER = ("Helvetica", 10, "bold")
FONT_NAV_TITLE = ("Helvetica", 12, "bold")
FONT_LABEL = ("Helvetica", 12)
FONT_HEADING = ("Helvetica", 14, "bold")
FONT_RESULT = ("Helvetica", 12)
FONT_SMALL = ("Helvetica", 10)

CELL_W = 40
CELL_H = 30


class CalendarWidget(tk.Frame):
    """Custom month-view calendar drawn on a Canvas for clean rendering."""

    def __init__(self, master, on_date_select=None, **kwargs):
        super().__init__(master, bg=COLOR_BG, **kwargs)
        self._on_date_select = on_date_select
        today = datetime.date.today()
        # Clamp initial year/month to supported range
        if today.year < MIN_YEAR:
            self._year = MIN_YEAR
            self._month = 1
        elif today.year > MAX_YEAR:
            self._year = MAX_YEAR
            self._month = 12
        else:
            self._year = today.year
            self._month = today.month
        self._selected_date = None
        self._today = today
        self._cal = calendar.Calendar(firstweekday=0)
        self._hover_cell = None
        self._cells = []  # list of (row, col, day, x0, y0, x1, y1) for hit testing

        self._build_nav()
        self._build_canvas()
        self._refresh()

    def _build_nav(self):
        nav = tk.Frame(self, bg=COLOR_HEADER_BG)
        nav.pack(fill=tk.X)

        self._btn_prev = ttk.Button(nav, text="\u25c0", width=3, command=self._prev_month)
        self._btn_prev.pack(side=tk.LEFT, padx=4, pady=4)

        self._lbl_title = tk.Label(
            nav, text="", font=FONT_NAV_TITLE,
            bg=COLOR_HEADER_BG, anchor=tk.CENTER,
        )
        self._lbl_title.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self._btn_next = ttk.Button(nav, text="\u25b6", width=3, command=self._next_month)
        self._btn_next.pack(side=tk.RIGHT, padx=4, pady=4)

    def _build_canvas(self):
        width = 7 * CELL_W
        height = 7 * CELL_H  # 1 header row + 6 week rows
        self._canvas = tk.Canvas(
            self, width=width, height=height,
            bg=COLOR_BG, highlightthickness=0,
        )
        self._canvas.pack()
        self._canvas.bind("<Button-1>", self._on_canvas_click)
        self._canvas.bind("<Motion>", self._on_canvas_motion)
        self._canvas.bind("<Leave>", self._on_canvas_leave)

    def _refresh(self):
        month_name = self._polish_month(self._month)
        self._lbl_title.configure(text=f"{month_name} {self._year}")

        at_min = (self._year, self._month) <= (MIN_YEAR, 1)
        at_max = (self._year, self._month) >= (MAX_YEAR, 12)
        self._btn_prev.configure(state="disabled" if at_min else "normal")
        self._btn_next.configure(state="disabled" if at_max else "normal")

        self._draw_calendar()

    def _draw_calendar(self):
        c = self._canvas
        c.delete("all")
        self._cells = []

        # Draw day-of-week headers
        for col, name in enumerate(DAY_HEADERS):
            x = col * CELL_W + CELL_W // 2
            y = CELL_H // 2
            fg = COLOR_WEEKEND if col >= 5 else COLOR_NORMAL
            c.create_text(x, y, text=name, font=FONT_DAY_HEADER, fill=fg)

        weeks = self._cal.monthdayscalendar(self._year, self._month)
        try:
            holidays = get_holidays(self._year)
        except ValueError:
            holidays = set()

        for r, week in enumerate(weeks):
            for col, day in enumerate(week):
                x0 = col * CELL_W
                y0 = (r + 1) * CELL_H
                x1 = x0 + CELL_W
                y1 = y0 + CELL_H
                cx = x0 + CELL_W // 2
                cy = y0 + CELL_H // 2

                if day == 0:
                    c.create_rectangle(x0, y0, x1, y1, fill=COLOR_EMPTY, outline="")
                    continue

                dt = datetime.date(self._year, self._month, day)
                bg = COLOR_DAY_BG
                fg = COLOR_NORMAL
                outline = ""
                outline_w = 0

                if col >= 5:
                    fg = COLOR_WEEKEND
                if dt in holidays:
                    fg = COLOR_HOLIDAY
                if dt == self._today:
                    bg = COLOR_TODAY_BG
                    fg = COLOR_TODAY_FG
                    outline = COLOR_TODAY_BORDER
                    outline_w = 2
                if dt == self._selected_date:
                    bg = COLOR_SELECTED_BG
                    fg = COLOR_SELECTED_FG
                    outline = ""
                    outline_w = 0

                # Hover highlight
                if self._hover_cell == (r, col):
                    if dt != self._selected_date:
                        bg = COLOR_HOVER_BG

                c.create_rectangle(
                    x0 + 1, y0 + 1, x1 - 1, y1 - 1,
                    fill=bg, outline=outline, width=outline_w,
                )
                c.create_text(cx, cy, text=str(day), font=FONT_DAY, fill=fg)

                self._cells.append((r, col, day, x0, y0, x1, y1))

    def _hit_test(self, mx, my):
        """Return (row, col, day) for the cell at canvas coords, or None."""
        for r, col, day, x0, y0, x1, y1 in self._cells:
            if x0 <= mx < x1 and y0 <= my < y1:
                return r, col, day
        return None

    def _on_canvas_click(self, event):
        hit = self._hit_test(event.x, event.y)
        if hit:
            _, _, day = hit
            try:
                dt = datetime.date(self._year, self._month, day)
                self._selected_date = dt
                self._refresh()
                if self._on_date_select:
                    self._on_date_select(dt)
            except (ValueError, OverflowError):
                # Invalid date construction, ignore click
                pass

    def _on_canvas_motion(self, event):
        hit = self._hit_test(event.x, event.y)
        new_hover = (hit[0], hit[1]) if hit else None
        if new_hover != self._hover_cell:
            self._hover_cell = new_hover
            self._draw_calendar()

    def _on_canvas_leave(self, _event):
        if self._hover_cell is not None:
            self._hover_cell = None
            self._draw_calendar()

    def _prev_month(self):
        if self._month == 1:
            if self._year > MIN_YEAR:
                self._year -= 1
                self._month = 12
        else:
            self._month -= 1
        self._refresh()

    def _next_month(self):
        if self._month == 12:
            if self._year < MAX_YEAR:
                self._year += 1
                self._month = 1
        else:
            self._month += 1
        self._refresh()

    def set_date(self, dt):
        # Validate date is within supported range
        if dt.year < MIN_YEAR or dt.year > MAX_YEAR:
            return
        self._selected_date = dt
        self._year = dt.year
        self._month = dt.month
        self._refresh()

    def get_date(self):
        return self._selected_date

    @staticmethod
    def _polish_month(m):
        names = [
            "", "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec",
            "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień",
        ]
        return names[m]


class DatePicker(tk.Frame):
    """Date entry with an inline calendar overlay for selection."""

    def __init__(self, master, label_text="Data:", **kwargs):
        super().__init__(master, bg=COLOR_BG, **kwargs)
        self._cal_frame = None
        self._escape_id = None
        today = datetime.date.today()
        # Ensure today is within supported range, or use first/last supported year
        if today.year < MIN_YEAR:
            self._selected_date = datetime.date(MIN_YEAR, 1, 1)
        elif today.year > MAX_YEAR:
            self._selected_date = datetime.date(MAX_YEAR, 12, 31)
        else:
            self._selected_date = today

        tk.Label(
            self, text=label_text, font=FONT_LABEL, bg=COLOR_BG, width=6, anchor=tk.W,
        ).pack(side=tk.LEFT)

        self._entry_var = tk.StringVar(value=self._selected_date.isoformat())
        self._entry = ttk.Entry(self, textvariable=self._entry_var, font=FONT_LABEL, width=12)
        self._entry.pack(side=tk.LEFT)
        self._entry.bind("<Return>", self._on_entry_commit)
        self._entry.bind("<FocusOut>", self._on_entry_commit)

        self._day_label = tk.Label(
            self, text=f"({DAY_NAMES_PL[self._selected_date.weekday()]})",
            font=FONT_SMALL, bg=COLOR_BG, fg=COLOR_WEEKEND,
            width=14, anchor=tk.W,
        )
        self._day_label.pack(side=tk.LEFT, padx=(6, 0))

        self._btn = ttk.Button(
            self, text="\u25bc", width=3, command=self._toggle_calendar,
        )
        self._btn.pack(side=tk.LEFT, padx=(4, 0))

    def _on_entry_commit(self, _event=None):
        text = self._entry_var.get().strip()
        try:
            normalized = text.replace(".", "-").replace(" ", "-")
            dt = datetime.date.fromisoformat(normalized)
            # Validate date is within supported year range
            if dt.year < MIN_YEAR or dt.year > MAX_YEAR:
                # Restore previous valid date
                self._entry_var.set(self._selected_date.isoformat())
                return
            self._selected_date = dt
            self._entry_var.set(dt.isoformat())
            self._day_label.configure(text=f"({DAY_NAMES_PL[dt.weekday()]})")
        except (ValueError, OverflowError):
            # Restore previous valid date on any error
            self._entry_var.set(self._selected_date.isoformat())

    def _toggle_calendar(self):
        if self._cal_frame and self._cal_frame.winfo_exists():
            self._close_calendar()
        else:
            self._open_calendar()

    def _open_calendar(self):
        self._on_entry_commit()

        try:
            root = self.winfo_toplevel()
            self._cal_frame = tk.Frame(root, bg=COLOR_POPUP_BORDER, relief=tk.RAISED, bd=1)

            inner = tk.Frame(self._cal_frame, bg=COLOR_BG)
            inner.pack(padx=1, pady=1)

            cal = CalendarWidget(inner, on_date_select=self._on_pick)
            cal.set_date(self._selected_date)
            cal.pack(padx=2, pady=2)

            # Position the overlay relative to the root window
            self.update_idletasks()
            rx = self._entry.winfo_rootx() - root.winfo_rootx()
            ry = self._entry.winfo_rooty() - root.winfo_rooty() + self._entry.winfo_height() + 2
            self._cal_frame.place(x=rx, y=ry)
            self._cal_frame.lift()

            # Escape closes the calendar
            self._escape_id = root.bind("<Escape>", lambda _e: self._close_calendar(), add="+")
        except (tk.TclError, AttributeError):
            # If calendar creation fails, clean up and fail silently
            if self._cal_frame and self._cal_frame.winfo_exists():
                self._cal_frame.destroy()
            self._cal_frame = None

    def _on_pick(self, dt):
        self._selected_date = dt
        self._entry_var.set(dt.isoformat())
        self._day_label.configure(text=f"({DAY_NAMES_PL[dt.weekday()]})")
        self._close_calendar()

    def _close_calendar(self):
        if self._cal_frame and self._cal_frame.winfo_exists():
            self._cal_frame.destroy()
        self._cal_frame = None
        try:
            root = self.winfo_toplevel()
            if hasattr(self, '_escape_id') and self._escape_id:
                root.unbind("<Escape>", self._escape_id)
                self._escape_id = None
        except (tk.TclError, ValueError, AttributeError):
            pass

    def get_date(self):
        self._on_entry_commit()
        return self._selected_date

    def set_date(self, dt):
        # Validate date is within supported range
        if dt.year < MIN_YEAR or dt.year > MAX_YEAR:
            return
        self._selected_date = dt
        self._entry_var.set(dt.isoformat())
        self._day_label.configure(text=f"({DAY_NAMES_PL[dt.weekday()]})")


class WorkDaysApp(tk.Tk):
    """Main application window with three tabs."""

    def __init__(self):
        super().__init__()
        self.title("Dni Robocze — Kalkulator")
        self.geometry("560x500")
        self.minsize(520, 460)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background=COLOR_BG)
        style.configure("TNotebook.Tab", font=("Helvetica", 11), padding=[12, 4])
        style.configure("Heading.TLabel", font=FONT_HEADING, background=COLOR_BG)
        style.configure("Result.TLabel", font=FONT_RESULT, background=COLOR_BG)
        style.configure(
            "Accent.TButton", font=("Helvetica", 11, "bold"),
            padding=[16, 6],
        )
        style.configure("Treeview", font=FONT_SMALL, rowheight=24)
        style.configure("Treeview.Heading", font=FONT_DAY_HEADER)

        self.configure(bg=COLOR_BG)

        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self._build_count_tab(self._notebook)
        self._build_add_tab(self._notebook)
        self._build_holidays_tab(self._notebook)

        self.bind("<Return>", self._on_return)

    def _on_return(self, _event=None):
        idx = self._notebook.index(self._notebook.select())
        if idx == 0:
            self._do_count()
        elif idx == 1:
            self._do_add()

    # =====================
    # Tab 1: Policz dni
    # =====================

    def _build_count_tab(self, notebook):
        tab = tk.Frame(notebook, bg=COLOR_BG)
        notebook.add(tab, text="Policz dni")

        pad = tk.Frame(tab, bg=COLOR_BG)
        pad.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        ttk.Label(
            pad, text="Policz dni robocze między datami", style="Heading.TLabel",
        ).pack(anchor=tk.W, pady=(0, 16))

        self._count_start = DatePicker(pad, label_text="Od:")
        self._count_start.pack(anchor=tk.W, pady=6)

        self._count_end = DatePicker(pad, label_text="Do:")
        self._count_end.pack(anchor=tk.W, pady=6)

        ttk.Button(
            pad, text="Oblicz", style="Accent.TButton", command=self._do_count,
        ).pack(pady=(16, 0))

        self._count_result = tk.Label(
            pad, text="", font=FONT_RESULT, bg=COLOR_BG, fg=COLOR_RESULT_OK,
            wraplength=480, justify=tk.LEFT, anchor=tk.W,
        )
        self._count_result.pack(anchor=tk.W, fill=tk.X, pady=(16, 0))


    def _do_count(self):
        start = self._count_start.get_date()
        end = self._count_end.get_date()
        # Validate dates are within supported range
        if start.year < MIN_YEAR or start.year > MAX_YEAR:
            self._count_result.configure(
                text=f"Błąd: Data początkowa musi być w zakresie {MIN_YEAR}-{MAX_YEAR}.",
                fg=COLOR_RESULT_ERR,
            )
            return
        if end.year < MIN_YEAR or end.year > MAX_YEAR:
            self._count_result.configure(
                text=f"Błąd: Data końcowa musi być w zakresie {MIN_YEAR}-{MAX_YEAR}.",
                fg=COLOR_RESULT_ERR,
            )
            return
        try:
            result = count_workdays(start, end)
            self._count_result.configure(
                text=f"Dni robocze od {start} do {end}:  {result}",
                fg=COLOR_RESULT_OK,
            )
        except ValueError as e:
            self._count_result.configure(text=f"Błąd: {e}", fg=COLOR_RESULT_ERR)

    # =====================
    # Tab 2: Dodaj dni
    # =====================

    def _build_add_tab(self, notebook):
        tab = tk.Frame(notebook, bg=COLOR_BG)
        notebook.add(tab, text="Dodaj dni")

        pad = tk.Frame(tab, bg=COLOR_BG)
        pad.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        ttk.Label(
            pad, text="Dodaj/odejmij dni robocze od daty", style="Heading.TLabel",
        ).pack(anchor=tk.W, pady=(0, 16))

        self._add_start = DatePicker(pad, label_text="Data:")
        self._add_start.pack(anchor=tk.W, pady=6)

        spin_frame = tk.Frame(pad, bg=COLOR_BG)
        spin_frame.pack(anchor=tk.W, pady=6)

        tk.Label(
            spin_frame, text="Liczba dni:", font=FONT_LABEL, bg=COLOR_BG, width=6, anchor=tk.W,
        ).pack(side=tk.LEFT)

        self._add_days_var = tk.IntVar(value=5)
        spinbox = ttk.Spinbox(
            spin_frame, from_=-9999, to=9999, width=8,
            textvariable=self._add_days_var, font=FONT_LABEL,
        )
        spinbox.pack(side=tk.LEFT)

        tk.Label(
            spin_frame, text="(ujemne = cofnij)", font=FONT_SMALL,
            bg=COLOR_BG, fg=COLOR_WEEKEND,
        ).pack(side=tk.LEFT, padx=(10, 0))

        ttk.Button(
            pad, text="Oblicz", style="Accent.TButton", command=self._do_add,
        ).pack(pady=(16, 0))

        self._add_result = tk.Label(
            pad, text="", font=FONT_RESULT, bg=COLOR_BG, fg=COLOR_RESULT_OK,
            wraplength=480, justify=tk.LEFT, anchor=tk.W,
        )
        self._add_result.pack(anchor=tk.W, fill=tk.X, pady=(16, 0))

    def _do_add(self):
        start = self._add_start.get_date()
        # Validate start date is within supported range
        if start.year < MIN_YEAR or start.year > MAX_YEAR:
            self._add_result.configure(
                text=f"Błąd: Data musi być w zakresie {MIN_YEAR}-{MAX_YEAR}.",
                fg=COLOR_RESULT_ERR,
            )
            return
        try:
            n = self._add_days_var.get()
            # Validate bounds to prevent extreme values
            if abs(n) > 9999:
                self._add_result.configure(
                    text="Błąd: liczba dni musi być w zakresie -9999 do 9999.",
                    fg=COLOR_RESULT_ERR,
                )
                return
        except (tk.TclError, ValueError):
            self._add_result.configure(
                text="Błąd: wpisz poprawną liczbę dni.", fg=COLOR_RESULT_ERR,
            )
            return
        try:
            result = add_workdays(start, n)
            day_name = DAY_NAMES_PL[result.weekday()]
            direction = "dodaniu" if n >= 0 else "odjęciu"
            self._add_result.configure(
                text=(
                    f"Po {direction} {abs(n)} dni roboczych od {start}:\n"
                    f"{result}  ({day_name})"
                ),
                fg=COLOR_RESULT_OK,
            )
        except ValueError as e:
            self._add_result.configure(text=f"Błąd: {e}", fg=COLOR_RESULT_ERR)

    # =====================
    # Tab 3: Święta
    # =====================

    def _build_holidays_tab(self, notebook):
        tab = tk.Frame(notebook, bg=COLOR_BG)
        notebook.add(tab, text="Święta")

        top = tk.Frame(tab, bg=COLOR_BG)
        top.pack(fill=tk.X, padx=20, pady=(16, 10))

        tk.Label(
            top, text="Rok:", font=FONT_LABEL, bg=COLOR_BG,
        ).pack(side=tk.LEFT, padx=(0, 6))

        self._holiday_year_var = tk.StringVar(value=str(datetime.date.today().year))
        combo = ttk.Combobox(
            top, textvariable=self._holiday_year_var,
            values=[str(y) for y in SUPPORTED_YEARS],
            state="readonly", width=8, font=FONT_LABEL,
        )
        combo.pack(side=tk.LEFT)
        combo.bind("<<ComboboxSelected>>", lambda _e: self._load_holidays())

        ttk.Button(top, text="Pokaż", command=self._load_holidays).pack(
            side=tk.LEFT, padx=(10, 0),
        )

        tree_frame = tk.Frame(tab)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 16))

        cols = ("date", "day", "name")
        self._tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=14)
        self._tree.heading("date", text="Data")
        self._tree.heading("day", text="Dzień tygodnia")
        self._tree.heading("name", text="Nazwa")
        self._tree.column("date", width=100, anchor=tk.CENTER)
        self._tree.column("day", width=130, anchor=tk.W)
        self._tree.column("name", width=260, anchor=tk.W)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._load_holidays()

    def _load_holidays(self):
        for item in self._tree.get_children():
            self._tree.delete(item)
        try:
            year = int(self._holiday_year_var.get().strip())
            # Validate year is within supported range
            if year < MIN_YEAR or year > MAX_YEAR:
                self._tree.insert(
                    "", tk.END,
                    values=(
                        "Błąd",
                        f"Obsługiwane lata: {MIN_YEAR}-{MAX_YEAR}",
                        ""
                    )
                )
                return
            holidays = get_holidays_with_names(year)
        except (ValueError, KeyError) as e:
            self._tree.insert("", tk.END, values=("Błąd", str(e), ""))
            return
        for dt, name in holidays:
            day_name = DAY_NAMES_PL[dt.weekday()]
            self._tree.insert("", tk.END, values=(dt.isoformat(), day_name, name))


def run_gui():
    app = WorkDaysApp()
    app.mainloop()


if __name__ == "__main__":
    run_gui()
