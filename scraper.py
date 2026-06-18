import re
import browser_cookie3
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, field

BASE_URL = "https://www.tecnoempleo.com/ofertas-trabajo/"

PROVINCIAS = {
    "madrid": "263",
}

EXPERIENCIA = {
    "sin_exp": "1",
    "menos_1": "2",
    "1_anio": "3",
    "2_anios": "4",
}


@dataclass
class Oferta:
    titulo: str
    url: str
    empresa: str
    fecha: str
    ubicacion: str
    modalidad: str
    descripcion: str
    tecnologias: list[str] = field(default_factory=list)


def build_url(query: str = "", provincia: str = "", experiencias: list[str] = [], pagina: int = 1) -> str:
    params = {}
    if query:
        params["te"] = query
    if provincia:
        params["pr"] = f",{provincia},"
    if experiencias:
        params["ex"] = "," + ",".join(experiencias) + ","
    if pagina > 1:
        params["pagina"] = pagina
    return requests.Request("GET", BASE_URL, params=params).prepare().url


def parse_modalidad(texto: str) -> str:
    match = re.search(r"\(([^)]+)\)", texto)
    return match.group(1) if match else ""


def parse_card(card) -> Oferta | None:
    titulo_tag = card.select_one("a.font-weight-bold.text-cyan-700")
    if not titulo_tag:
        return None

    empresa_tag = card.select_one("a.text-primary.link-muted")
    fecha_tag = card.select_one("div.col-12.col-lg-3.text-gray-700")
    descripcion_tag = card.select_one("span.hidden-md-down")
    ubicacion_tag = card.select_one("div.col-12.col-lg-3.text-gray-700 b")
    tech_tags = card.select("span.badge.bg-gray-500, span.badge.bg-danger")

    # print(card.prettify())

    fecha = ""
    if fecha_tag:
        nodos = [t.strip() for t in fecha_tag.strings if "/" in t.strip()]
        fecha = nodos[0] if nodos else ""

    modalidad = ""
    if fecha_tag:
        texto_completo = fecha_tag.get_text(" ", strip=True)
        modalidad = parse_modalidad(texto_completo)

    descripcion = ""
    if descripcion_tag:
        nodos = [t.strip() for t in descripcion_tag.find_all(string=True, recursive=False)]
        descripcion = " ".join(t for t in nodos if t).strip()

    return Oferta(
        titulo=titulo_tag.text.strip(),
        url=titulo_tag["href"],
        empresa=empresa_tag.text.strip() if empresa_tag else "",
        fecha=fecha,
        ubicacion=ubicacion_tag.text.strip() if ubicacion_tag else "",
        modalidad=modalidad,
        descripcion=descripcion,
        tecnologias=[t.text.strip() for t in tech_tags],
    )


def create_session() -> requests.Session:
    cookies = browser_cookie3.firefox(domain_name="tecnoempleo.com")
    session = requests.Session()
    session.cookies.update(cookies)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    })
    return session


def get_ofertas(session: requests.Session, pagina: int = 1) -> list[Oferta]:
    url = build_url(
        query="python",
        provincia=PROVINCIAS["madrid"],
        experiencias=list(EXPERIENCIA.values()),
        pagina=pagina,
    )
    response = session.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.select("div.p-3.border.rounded.mb-3.bg-white")
    return [o for card in cards if (o := parse_card(card))]


def scrape_todas(max_paginas: int = 100) -> list[Oferta]:
    session = create_session()
    todas = []
    for pagina in range(1, max_paginas + 1):
        ofertas = get_ofertas(session, pagina)
        if not ofertas:
            break
        todas.extend(ofertas)
        print(f"Pagina {pagina}: {len(ofertas)} ofertas")
    return todas


if __name__ == "__main__":
    ofertas = scrape_todas(max_paginas=1)
    for o in ofertas:
        print(f"\n{o.fecha} | {o.titulo}")
        print(f"  {o.empresa} — {o.ubicacion} ({o.modalidad})")
        print(f"  {o.descripcion[:120]}...")
        print(f"  Tecnologias: {', '.join(o.tecnologias)}")
        print(f"  {o.url}")
        print("-" * 80)