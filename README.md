# dni_robocze

Kalkulator dni roboczych w Polsce. Uwzglednia weekendy i wszystkie 13 polskich swiat ustawowych (w tym ruchome, zalezne od Wielkanocy).

Obsługiwane lata: 2020-2030.

## Wymagania

Python 3 (bez zewnetrznych zaleznosci).

## Instalacja

### Linux / macOS

```bash
ln -s $(pwd)/dni_robocze.py ~/.local/bin/dni_robocze
```

Po tym komenda `dni_robocze` będzie dostępna globalnie (wymaga `~/.local/bin` w `PATH`).

### Windows

Utwórz plik `dni_robocze.cmd` w katalogu dostępnym w `PATH` (np. `%USERPROFILE%\.local\bin\`):

```cmd
@python "%USERPROFILE%\Documents\kodowanie\dni_robocze\dni_robocze.py" %*
```

Alternatywnie dodaj katalog ze skryptem do zmiennej środowiskowej `PATH` i uruchamiaj przez `python dni_robocze.py`.

## Użycie

### Policz dni robocze między datami

```
./dni_robocze.py count 2026-01-01 2026-12-31
# Dni robocze od 2026-01-01 do 2026-12-31: 254
```

### Wyświetl święta w danym roku

```
./dni_robocze.py holidays 2026
```

### Dodaj/odejmij dni robocze od daty

```
./dni_robocze.py add 2026-01-29 10
# Po dodaniu 10 dni roboczych od 2026-01-29: 2026-02-12 (czwartek)

./dni_robocze.py add 2026-01-29 -5
# Po odjęciu 5 dni roboczych od 2026-01-29: 2026-01-22 (czwartek)
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
- 25 grudnia — Boże Narodzenie (pierwszy dzień)
- 26 grudnia — Boże Narodzenie (drugi dzień)

Ruchome (zależne od Wielkanocy):
- Wielkanoc (Niedziela Wielkanocna)
- Poniedziałek Wielkanocny
- Zielone Świątki (49 dni po Wielkanocy)
- Boże Ciało (60 dni po Wielkanocy)
