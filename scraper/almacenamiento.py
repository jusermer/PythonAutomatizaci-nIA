import csv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def guardar_csv(productos, filename):
    """
    Guarda la lista de productos en un archivo CSV.

    Uso:
        Esta función serializa y almacena los productos en formato CSV, manejando posibles errores de acceso al archivo.

    Parámetros:
        productos (list[dict]): Lista de productos a guardar.
        filename (str): Nombre del archivo CSV destino.

    Retorno:
        None

    Ejemplo:
        guardar_csv(productos_limpios, "productos.csv")
    """
    # Definición de las columnas del CSV
    fieldnames = ["nombre", "precio", "rating", "reviews"]
    try:
        # Intento de guardar el archivo CSV
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(productos)
        logger.info(f"CSV guardado en: {filename}")
    except PermissionError:
        # Manejo de error: archivo en uso, se guarda con nombre alternativo
        logger.warning(f"{filename} está en uso. Usando nombre alternativo...")
        filename = "products_output.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(productos)
        logger.info(f"CSV guardado en: {filename}")
