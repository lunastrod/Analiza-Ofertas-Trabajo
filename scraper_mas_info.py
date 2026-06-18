import json
import re
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
import browser_cookie3
import requests
from bs4 import BeautifulSoup

def create_session() -> requests.Session:
    cookies = browser_cookie3.firefox(domain_name="tecnoempleo.com")
    session = requests.Session()
    session.cookies.update(cookies)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    })
    return session

def extraer_descripcion(session: requests.Session, oferta: dict) -> dict:
    url = oferta['url']
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    descripcion_div = soup.find('div', itemprop='description')
    descripcion_completa = descripcion_div.get_text(separator='\n', strip=True) if descripcion_div else ''

    return {**oferta, 'descripcion_completa': descripcion_completa}

# Cargar ofertas filtradas
with open('ofertas_filtradas.json', 'r', encoding='utf-8') as f:
    ofertas = json.load(f)

# Bucle sobre todas las ofertas
session = create_session()
ofertas_completas = []

for i, oferta in enumerate(ofertas):
    print(f"[{i+1}/{len(ofertas)}] Scraping: {oferta['titulo']} ({oferta['empresa']})")
    oferta_completa = extraer_descripcion(session, oferta)
    ofertas_completas.append(oferta_completa)

# Guardar en ofertas_completas.json
with open('ofertas_completas.json', 'w', encoding='utf-8') as f:
    json.dump(ofertas_completas, f, ensure_ascii=False, indent=2)

print(f"\n✓ Guardado en ofertas_completas.json ({len(ofertas_completas)} ofertas)")