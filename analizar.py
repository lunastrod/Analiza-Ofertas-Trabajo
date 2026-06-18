import json
from datetime import datetime, timedelta

# Cargar el JSON
with open('ofertas.json', 'r', encoding='utf-8') as f:
    ofertas = json.load(f)

def filtrar_por_fecha(ofertas, fecha_inicio=None, fecha_fin=None):
    """
    Filtra ofertas por rango de fechas
    fecha_inicio y fecha_fin en formato 'YYYY-MM-DD'
    """
    resultado = ofertas
    
    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        resultado = [o for o in resultado if datetime.strptime(o['fecha'], '%Y-%m-%d') >= fecha_inicio]
    
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
        resultado = [o for o in resultado if datetime.strptime(o['fecha'], '%Y-%m-%d') <= fecha_fin]
    
    return resultado

def filtrar_por_inscrito(ofertas, inscrito=True):
    """
    Filtra ofertas por estado de inscripción
    inscrito=True: solo inscritos
    inscrito=False: solo no inscritos
    """
    return [o for o in ofertas if o['inscrito'] == inscrito]

def ofertas_ultima_semana_no_inscritas(ofertas):
    """
    Filtra ofertas de la última semana (desde hoy hasta hace 7 días) que no estén inscritas
    Usa las funciones filtrar_por_fecha() y filtrar_por_inscrito()
    """
    hoy = datetime.now().strftime('%Y-%m-%d')
    hace_una_semana = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    # Primero filtra por fecha
    resultado = filtrar_por_fecha(ofertas, fecha_inicio=hace_una_semana, fecha_fin=hoy)
    
    # Luego filtra por no inscritos
    resultado = filtrar_por_inscrito(resultado, inscrito=False)
    
    return resultado

if __name__ == "__main__":
    ultimas_semana = ofertas_ultima_semana_no_inscritas(ofertas)
    print(f"Ofertas de la última semana NO inscritas: {len(ultimas_semana)}")
    for oferta in ultimas_semana:
        print(f"  - {oferta['titulo']} ({oferta['empresa']}) - {oferta['fecha']}")
    
    with open('ofertas_filtradas.json', 'w', encoding='utf-8') as f:
        json.dump(ultimas_semana, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Guardado en ofertas_filtradas.json")