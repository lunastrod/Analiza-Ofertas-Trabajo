import json
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Validar API key
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_API_KEY no encontrada en .env")

print(f"API Key cargada: {api_key[:20]}...{api_key[-10:]}")  # Debug
print(f"Longitud: {len(api_key)}")  # Debug

# Campos a extraer
CAMPOS = [
    'titulo',
    'url',
    'empresa',
    'fecha',
    'ubicacion',
    'modalidad',
    'categoria',
    'descripcion_completa',
    'tecnologias',
    'salario',
]

def cargar_ofertas(ruta: str) -> list:
    """Carga las ofertas desde el JSON"""
    with open(ruta, 'r', encoding='utf-8') as f:
        return json.load(f)

def cargar_perfil(ruta: str) -> str:
    """Carga el perfil profesional desde el markdown"""
    with open(ruta, 'r', encoding='utf-8') as f:
        return f.read()

def formatear_oferta(oferta: dict) -> str:
    """Formatea una oferta para pasarla a Gemini"""
    lineas = []
    for campo in CAMPOS:
        valor = oferta.get(campo, '')
        if campo == 'tecnologias' and isinstance(valor, list):
            valor = ', '.join(valor)
        lineas.append(f"{campo.upper()}: {valor}")
    return '\n'.join(lineas)

def formatear_todas_ofertas(ofertas: list) -> str:
    """Formatea todas las ofertas"""
    ofertas_formateadas = []
    for i, oferta in enumerate(ofertas, 1):
        ofertas_formateadas.append(f"--- OFERTA {i} ---\n{formatear_oferta(oferta)}")
    return '\n\n'.join(ofertas_formateadas)

# Cargar datos
print("Cargando ofertas...")
ofertas = cargar_ofertas('ofertas_completas.json')
print(f"✓ {len(ofertas)} ofertas cargadas")

print("Cargando perfil profesional...")
perfil = cargar_perfil('PerfilProfesional.md')
print("✓ Perfil cargado")

# Formatear ofertas
ofertas_texto = formatear_todas_ofertas(ofertas)

# Crear prompt
prompt = f"""He recopilado {len(ofertas)} ofertas de empleo. Aquí están los detalles:

{ofertas_texto}

---

PERFIL PROFESIONAL:

{perfil}
"""

print("\nEnviando a Gemini...")
client = genai.Client(api_key=api_key)
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
)

print("\n" + "="*80)
print(response.text)
print("="*80)

with open('analisis_gemini.txt', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("\n✓ Análisis guardado en analisis_gemini.txt")