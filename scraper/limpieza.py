import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def refinar_data(productos):
    """
    Limpia y transforma la lista de productos, convirtiendo precios a float, ratings y reviews a int.
    Elimina duplicados y retorna una lista de productos refinados.
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
