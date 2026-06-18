import json
import re
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

import browser_cookie3
import requests
from bs4 import BeautifulSoup


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
    logo_url: str
    fecha: date | None
    ubicacion: str
    modalidad: str
    categoria: str
    descripcion: str
    tecnologias: list[str] = field(default_factory=list)
    salario: str = ""
    urgente: bool = False
    inscrito: bool = False
    match_pct: int | None = None

    def __str__(self) -> str:
        flags = []
        if self.urgente:
            flags.append("URGENTE")
        if self.inscrito:
            flags.append("INSCRITO")
        if self.match_pct is not None:
            flags.append(f"{self.match_pct}% match")

        lineas = [
            f"[{self.fecha}] {self.titulo}" + (f"  {' '.join(flags)}" if flags else ""),
            f"  {self.empresa} — {self.ubicacion} ({self.modalidad}) | {self.categoria}",
        ]
        if self.salario:
            lineas.append(f"  {self.salario}")
        lineas.append(f"  {self.descripcion[:120]}...")
        if self.tecnologias:
            lineas.append(f"  {', '.join(self.tecnologias)}")
        lineas.append(f"  {self.url}")
        return "\n".join(lineas)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["fecha"] = self.fecha.isoformat() if self.fecha else None
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Oferta":
        d = d.copy()
        d["fecha"] = date.fromisoformat(d["fecha"]) if d.get("fecha") else None
        return cls(**d)


def guardar_ofertas(ofertas: list[Oferta], path: str | Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump([o.to_dict() for o in ofertas], f, ensure_ascii=False, indent=2)
    print(f"Guardadas {len(ofertas)} ofertas en {path}")


def cargar_ofertas(path: str | Path) -> list[Oferta]:
    with open(path, encoding="utf-8") as f:
        return [Oferta.from_dict(d) for d in json.load(f)]


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


def parse_fecha(texto: str) -> date | None:
    match = re.search(r"(\d{2})/(\d{2})/(\d{4})", texto)
    if not match:
        return None
    try:
        return date(int(match.group(3)), int(match.group(2)), int(match.group(1)))
    except ValueError:
        return None


def parse_modalidad(texto: str) -> str:
    match = re.search(r"\(([^)]+)\)", texto)
    return match.group(1) if match else ""


def parse_match(tag) -> int | None:
    match_tag = tag.select_one("span.text-success.fw-semibold") or tag.select_one("span.small.fw-semibold.text-success")
    if not match_tag:
        return None
    match = re.search(r"(\d+)%", match_tag.text)
    return int(match.group(1)) if match else None


def parse_card(card) -> Oferta | None:
    titulo_tag = card.select_one("a.font-weight-bold.text-cyan-700")
    if not titulo_tag:
        return None

    empresa_tag = card.select_one("a.text-primary.link-muted")
    fecha_col = card.select_one("div.col-12.col-lg-3.text-gray-700")
    descripcion_tag = card.select_one("span.hidden-md-down")
    ubicacion_tag = card.select_one("div.col-12.col-lg-3.text-gray-700 b")
    tech_tags = card.select("span.badge.bg-gray-500, span.badge.bg-danger")
    logo_tag = card.select_one("div.d-none.d-md-block img") or card.select_one("figure img")

    # print(card.prettify())

    fecha_texto = fecha_col.get_text(" ", strip=True) if fecha_col else ""

    categoria = ""
    salario = ""
    if fecha_col:
        lineas = [t.strip() for t in fecha_col.strings if t.strip()]
        for linea in lineas:
            if "€" in linea:
                salario = linea
            elif "/" not in linea and "(" not in linea and linea not in ("Nueva", "Actualizada"):
                categoria = linea

    descripcion = ""
    if descripcion_tag:
        nodos = [t.strip() for t in descripcion_tag.find_all(string=True, recursive=False)]
        descripcion = " ".join(t for t in nodos if t).strip()

    logo_url = ""
    if logo_tag:
        logo_url = logo_tag.get("src") or logo_tag.get("data-src") or ""
        if logo_url.startswith("data:"):
            logo_url = logo_tag.get("data-src") or ""

    return Oferta(
        titulo=titulo_tag.text.strip(),
        url=titulo_tag["href"],
        empresa=empresa_tag.text.strip() if empresa_tag else "",
        logo_url=logo_url,
        fecha=parse_fecha(fecha_texto),
        ubicacion=ubicacion_tag.text.strip() if ubicacion_tag else "",
        modalidad=parse_modalidad(fecha_texto),
        categoria=categoria,
        descripcion=descripcion,
        tecnologias=[t.text.strip() for t in tech_tags],
        salario=salario,
        urgente=bool(card.select_one("span.badge.badge-success.mr-1")),
        inscrito=bool(card.find(string=re.compile("Ya estás inscrito"))),
        match_pct=parse_match(card),
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
    FICHERO = Path("ofertas.json")

    if FICHERO.exists():
        print(f"Cargando desde {FICHERO}...")
        ofertas = cargar_ofertas(FICHERO)
    else:
        ofertas = scrape_todas(max_paginas=2)
        guardar_ofertas(ofertas, FICHERO)

    for o in ofertas:
        print(o)
        print()