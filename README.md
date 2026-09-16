# Docházkový systém pro kroužek

Mobile-first Flask app pro správu docházky s PWA podporou.

## Rychlý start

```bash
pip install Flask Flask-SQLAlchemy
python app.py
```

Otevři http://localhost:9120

## Cloudflare Tunnel

Na RPi už máš tunel. Přidej hostname:

```yaml
# ~/.cloudflared/config.yaml
ingress:
  - hostname: dochazka.czechtechgeek.cz
    service: http://localhost:9120
  - hostname: herm.czechtechgeek.cz
    service: http://localhost:9119
```

Nastav Zero Trust Access policy (Email OTP) → jen ty.

## Použití

1. **Nastavení** → vytvoř skupinu (např. "12:30 - 26 dětí", "13:30 - zbytek")
2. **Přidat děti** → hromadně vložit jména, každé na nový řádek
3. **Docházka** → vyber skupinu → datum (default dnes) → označuj stavy
4. **Export** → HTML (Print → PDF) nebo XML

## Struktura

```
dochazka/
├── app.py              # Flask server
├── models.py           # DB modely (Group, Child, Attendance)
├── static/style.css    # Mobile-first CSS
├── templates/          # Jinja2 šablony
└── dochazka.db         # SQLite (auto-vytvoří se)
```