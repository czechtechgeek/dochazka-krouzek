# Changelog

## 1.0.10 (2025-09-18)

- Poznámky u dětí (manage + 📌 indikátor v docházce)
- Oprava 302 redirectů v HA ingress (konec 404 po všech akcích)

## 1.0.9 (2025-09-18)

- after_request: přepis Location hlavičky u redirectů pro HA ingress

## 1.0.8 (2025-09-17)

- DB migrace: automatické přidání chybějícího subgroup sloupce

## 1.0.7 (2025-09-17)

- Server-side HTML rewriting pro HA ingress (href/action)
- INGRESS_BASE env var v Dockerfile

## 1.0.6 (2025-09-16)

- JS oprava absolutních cest a formulářů pro HA ingress

## 1.0.5 (2025-09-16)

- CSS inlinován do base.html (žádný externí soubor)
- JS base path detekce pro HA ingress

## 1.0.4 (2025-09-16)

- SCRIPT_NAME z HA ingress headers (before_request)
- ProxyFix middleware

## 1.0.3 (2025-09-16)

- IngressFix middleware: X-Ingress-Path → X-Forwarded-Prefix

## 1.0.2 (2025-09-16)

- url_for všude místo hardcoded cest
- ProxyFix middleware

## 1.0.1 (2025-09-16)

- Dockerfile: vytvoření /config adresáře

## 1.0.0 (2025-09-16)

- První release
- Základní docházkový systém: skupiny, děti, zápis docházky
- Hromadné akce (vše přítomno/omluveno/nepřítomno)
- Podskupiny (třídy) v rámci skupiny
- PWA podpora (instalace na plochu)
- Export HTML (PDF) a XML
- Statistiky jednotlivců
- Home Assistant add-on (ingress)