import browser_cookie3
import requests
from bs4 import BeautifulSoup

URL = "https://www.tecnoempleo.com/ofertas-trabajo/?te="

cookies = browser_cookie3.firefox(domain_name="tecnoempleo.com")
session = requests.Session()
session.cookies.update(cookies)
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
})

response = session.get(URL, timeout=10)
soup = BeautifulSoup(response.text, "html.parser")

cards = soup.select("div.p-3.border.rounded.mb-3.bg-white")
for card in cards:
    titulo_tag = card.select_one("a.font-weight-bold.text-cyan-700")
    if titulo_tag:
        titulo = titulo_tag.text.strip()
        url = titulo_tag["href"]
        print(f"{titulo}\n{url}\n")