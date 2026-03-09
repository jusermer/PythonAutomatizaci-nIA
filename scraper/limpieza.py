import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from typing import List, Dict
def refinar_data(productos: List[Dict]) -> List[Dict]:
    """
    Limpia y transforma la lista de productos extraídos del scraping.

    Propósito:
        - Convierte los valores de precio a float, rating y reviews a int.
        - Elimina productos duplicados (por nombre, precio, rating y reviews).
    
    Parámetros:
        productos (list[dict]): Lista de productos, cada uno con las claves 'nombre', 'precio', 'rating', 'reviews'.

    Retorno:
        list[dict]: Lista de productos refinados, sin duplicados y con tipos correctos.
    """
    if not productos:
        logger.warning("Lista de productos vacía")
        return []
    datos_limpios = []
    vistos = set()
    for p in productos:
        try:
            precio = float(p["precio"].replace("$", "").replace(",", ""))
        except (ValueError, AttributeError):
            logger.warning(f"No se pudo parsear precio: {p['precio']}")
            precio = 0.0
        try:
            rating = int(p["rating"])
        except (ValueError, AttributeError):
            logger.warning(f"No se pudo parsear rating: {p['rating']}")
            rating = 0
        try:
            reviews = int(str(p["reviews"]).replace(" reviews", "").replace(",", "").strip())
        except (ValueError, AttributeError):
            logger.warning(f"No se pudo parsear reviews: {p['reviews']}")
            reviews = 0
        key = (p.get("nombre"), precio, rating, reviews)
        if key in vistos:
            continue
        vistos.add(key)
        datos_limpios.append({
            "nombre": p["nombre"],
            "precio": precio,
            "rating": rating,
            "reviews": reviews
        })
    return datos_limpios
