import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from typing import List, Dict
def refinar_data(productos: List[Dict]) -> List[Dict]:
    """
    Refina y transforma la lista de productos extraídos del scraping.

    Uso:
        Esta función convierte los valores de precio a float, rating y reviews a int,
        y elimina productos duplicados para asegurar datos limpios y consistentes.

    Parámetros:
        productos (list[dict]): Lista de productos, cada uno con las claves 'nombre', 'precio', 'rating', 'reviews'.

    Retorno:
        list[dict]: Lista de productos refinados, sin duplicados y con tipos correctos.

    Ejemplo:
        productos_limpios = refinar_data(productos_extraidos)
    """
    # Validación inicial: lista vacía
    if not productos:
        logger.warning("Lista de productos vacía")
        return []
    datos_limpios = []
    vistos = set()
    # Procesamiento de cada producto
    for p in productos:
        # Conversión de precio a float
        try:
            precio = float(p["precio"].replace("$", "").replace(",", ""))
        except (ValueError, AttributeError):
            logger.warning(f"No se pudo parsear precio: {p['precio']}")
            precio = 0.0
        # Conversión de rating a int
        try:
            rating = int(p["rating"])
        except (ValueError, AttributeError):
            logger.warning(f"No se pudo parsear rating: {p['rating']}")
            rating = 0
        # Conversión de reviews a int
        try:
            reviews = int(str(p["reviews"]).replace(" reviews", "").replace(",", "").strip())
        except (ValueError, AttributeError):
            logger.warning(f"No se pudo parsear reviews: {p['reviews']}")
            reviews = 0
        # Eliminar duplicados por nombre, precio, rating y reviews
        clave = (p.get("nombre"), precio, rating, reviews)
        if clave in vistos:
            continue
        vistos.add(clave)
        datos_limpios.append({
            "nombre": p["nombre"],
            "precio": precio,
            "rating": rating,
            "reviews": reviews
        })
    # Retorna la lista refinada
    return datos_limpios
