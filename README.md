# dni_robocze

Kalkulator dni roboczych w Polsce. Uwzglednia weekendy i polskie swieta ustawowe (13 do 2024, 14 od 2025 — Wigilia), w tym ruchome zalezne od Wielkanocy.

Obsługiwane lata: 2020-2030.

## Wymagania

Python 3 (bez zewnetrznych zaleznosci).

Wersja GUI wymaga dodatkowo modułu `tkinter` (wbudowany w większość instalacji Pythona; na macOS/Homebrew: `brew install python-tk@3.XX`).

## Instalacja

```bash
pip install dni-robocze-pl
```

Po instalacji dostępne są dwie komendy:
- `dni-robocze` — kalkulator w wierszu poleceń
- `dni-robocze-gui` — wersja graficzna (wymaga `tkinter`)

## Wersja GUI

```bash
dni-robocze-gui
```

Graficzny interfejs z trzema zakładkami:
- **Policz dni** — oblicz dni robocze między dwiema datami
- **Dodaj dni** — dodaj/odejmij dni robocze od daty
- **Święta** — lista świąt ustawowych w wybranym roku

Kalendarz z podglądem świąt (czerwone), weekendów (szare) i dnia dzisiejszego (pomarańczowy). Daty można wpisywać ręcznie lub wybierać z kalendarza.

## Użycie (wiersz poleceń)

Daty można podawać w formacie `YYYY-MM-DD`, `YYYY.MM.DD`, `"YYYY MM DD"` oraz pomocniczo: `today`, `+N`/`+Nd`, `-N`/`-Nd` (liczone od dnia dzisiejszego). Obsługiwane lata: 2020-2030.

### Policz dni robocze między datami

```
dni-robocze count 2026-01-01 2026-12-31
dni-robocze count --from 2026.01.01 --to 2026.12.31
dni-robocze count --from today --to +10 --quiet
# Dni robocze od 2026-01-01 do 2026-12-31: 253
```

### Wyświetl święta w danym roku

```
dni-robocze holidays 2026
```

### Dodaj/odejmij dni robocze od daty

```
dni-robocze add 2026-01-29 10
dni-robocze add 2026-01-29 -5 --quiet
# Po dodaniu 10 dni roboczych od 2026-01-29: 2026-02-12 (czwartek)
# Po odjęciu 5 dni roboczych od 2026-01-29: 2026-01-22 (czwartek)
```

### Wyświetl tylko daty świąt (quiet)

```
dni-robocze holidays 2026 --quiet
```

### Wersja

```
dni-robocze --version
```

## Święta ustawowe

Stałe:
- 1 stycznia — Nowy Rok
- 6 stycznia — Trzech Króli
- 1 maja — Święto Pracy
- 3 maja — Święto Konstytucji 3 Maja
- 15 sierpnia — Wniebowzięcie NMP
- 1 listopada — Wszystkich Świętych
- 11 listopada — Święto Niepodległości
- 24 grudnia — Wigilia Bożego Narodzenia (od 2025)
- 25 grudnia — Boże Narodzenie (pierwszy dzień)
- 26 grudnia — Boże Narodzenie (drugi dzień)

Ruchome (zależne od Wielkanocy):
- Wielkanoc (Niedziela Wielkanocna)
- Poniedziałek Wielkanocny
- Zielone Świątki (49 dni po Wielkanocy)
- Boże Ciało (60 dni po Wielkanocy)
