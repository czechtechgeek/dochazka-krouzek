# Docházkový systém pro kroužek

Mobile-first Flask app pro správu docházky. Optimalizovaná pro mobil, podpora PWA (instalace na plochu). Možnost exportu do HTML (PDF) a XML.

## Home Assistant add-on

Repo je zároveň HA add-on — přidej ho v Supervisor → Add-on Store → Repositories:

```
https://github.com/czechtechgeek/dochazka-krouzek
```

Po instalaci se v sidebaru objeví položka "Docházka". HA řeší auth i remote přístup.

### Architektura add-onu

- **Ingress** — HA proxy, funguje lokálně i vzdáleně
- **Auth** — přes HA účet, žádná extra přihlášení
- **Data** — SQLite v `/config/dochazka.db` (persistentní)

## Samostatné spuštění (bez HA)

```bash
pip install Flask Flask-SQLAlchemy
python3 src/app.py
# → http://localhost:9120
```

## Použití

1. **Nastavení** → vytvoř skupinu (např. "12:30 — 26 dětí")
2. **Přidat děti** → hromadně vložit jména, každé na nový řádek
3. **Docházka** → vyber skupinu → datum (default dnes) → odklepávej stavy
4. **Export** → HTML (Print → PDF) nebo XML

## Stavy

| Stav | Tlačítko | Význam |
|------|----------|--------|
| ✅ | Přítomen | Dítě je přítomno |
| 📝 | Omluven | Dítě se omluvilo předem |
| ❌ | Nepřítomen | Dítě nepřišlo bez omluvy |

## Struktura

```
├── config.yaml          # HA add-on metadata
├── Dockerfile           # HA add-on image
├── run.sh               # HA add-on start script
├── src/
│   ├── app.py           # Flask server
│   ├── models.py        # DB modely (Group, Child, Attendance)
│   ├── static/          # CSS + PWA
│   ├── templates/       # Jinja2 šablony
│   └── requirements.txt
└── README.md
```

## Licence

MIT