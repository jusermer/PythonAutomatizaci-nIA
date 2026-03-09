import csv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def guardar_csv(productos, filename):
    """
    Guarda la lista de productos en un archivo CSV.

    Propósito:
        - Serializa y almacena los productos en formato CSV.

    Parámetros:
        productos (list[dict]): Lista de productos a guardar.
        filename (str): Nombre del archivo CSV destino.

    Retorno:
        None
    """
    fieldnames = ["nombre", "precio", "rating", "reviews"]
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(productos)
        logger.info(f"CSV guardado en: {filename}")
    except PermissionError:
        logger.warning(f"{filename} está en uso. Usando nombre alternativo...")
        filename = "products_output.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(productos)
        logger.info(f"CSV guardado en: {filename}")
