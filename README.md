# Docházkový systém pro kroužek

Mobile-first Flask app pro správu docházky v kroužku. Optimalizovaná pro mobil, podpora PWA (instalace na plochu telefonu). Export do HTML (tisk → PDF) a XML.

## Home Assistant add-on

Přidej repo v **Supervisor → Add-on Store → tři tečky → Repositories**:

```
https://github.com/czechtechgeek/dochazka-krouzek
```

HA automaticky najde add-on v `addon/` adresáři. Po instalaci se v sidebaru objeví **📋 Docházka**.

**Výhody:**
- **Ingress** — funguje lokálně i vzdáleně (HA proxy)
- **Auth** — přes HA účet, nic extra
- **Data** — SQLite v `/config/dochazka.db` (přes restart)

## Samostatné spuštění (bez HA)

```bash
cd addon
pip install Flask Flask-SQLAlchemy
python3 src/app.py
# → http://localhost:9120
```

## Použití

1. **⚙️ Nastavení** → vytvoř skupinu (např. "12:30 — 26 dětí")
2. **➕ Přidat děti** → hromadně vložit jména, každé na nový řádek
3. **📝 Docházka** → vyber skupinu → datum (default dnes) → odklepávej stavy
4. **🖨️ Export** → HTML (Print → PDF) nebo XML

### Stavy

✅ **Přítomen** — dítě je přítomno  
📝 **Omluven** — omluveno předem  
❌ **Nepřítomen** — nepřišlo bez omluvy

### PWA

Appku jde nainstalovat na plochu mobilu (Android i iOS). Stačí v prohlížeči "Přidat na plochu".

## Struktura

```
├── addon/
│   ├── config.yaml       # HA add-on metadata
│   ├── Dockerfile        # HA add-on image
│   ├── run.sh            # start script
│   └── src/
│       ├── app.py        # Flask server
│       ├── models.py     # DB modely
│       ├── static/       # CSS + PWA
│       ├── templates/    # Jinja2 šablony
│       └── requirements.txt
├── .gitignore
└── README.md
```

## Licence

MIT