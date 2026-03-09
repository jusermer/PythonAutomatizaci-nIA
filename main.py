import argparse
from scraper.navegador import inicializar_driver, BASE_URL, TIEMPO_ESPERA, esperar_menu
from scraper.extraccion import obtener_links, obtener_sublinks, navegar_a_enlace, obtener_productos
from scraper.limpieza import refinar_data
from scraper.almacenamiento import guardar_csv
from scraper.analisis import generar_analysis, analizar_con_ollama_csv

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main() -> None:
    """
    Orquesta el proceso completo de scraping, limpieza, almacenamiento y análisis de productos.

    El flujo incluye:
        - Inicialización del navegador y espera del menú principal.
        - Filtrado de categorías según los argumentos recibidos.
        - Navegación por categorías y subcategorías, extracción de productos.
        - Refinamiento y guardado de datos en formato CSV.
        - Generación de análisis estadístico básico y, si se solicita, análisis avanzado con IA.
        - Registro de logs detallados en cada etapa.
        - Manejo robusto de errores y cierre seguro del navegador.

    Argumentos:
        --categoria: Filtra la categoría principal a analizar (por nombre en el href).
        --paginas: Expresión de páginas a extraer (rango o lista).
        --modeloIA: Modelo de IA para análisis avanzado (opcional).

    El diseño busca modularidad, claridad y trazabilidad, facilitando la depuración y el mantenimiento.
    """
    # Configuración de argumentos para el scraper
    parser = argparse.ArgumentParser(description="Scraper de productos modular")
    parser.add_argument("--categoria", type=str, default="", help="computers, phones, etc. (filtra por nombre en el href de la categoría)")
    parser.add_argument("--paginas", type=str, default="", help="Expresión de páginas a extraer (ejemplo: '1-10' o '2,3,4')")
    parser.add_argument("--modeloIA", type=str, default="llama3", help="Modelo de IA a utilizar para el análisis avanzado (por defecto: 'llama3')")
    args = parser.parse_args()

    # Inicialización del navegador y espera del menú principal
    driver = inicializar_driver()
    esperar_menu(driver)

    productos_totales = []
    try:
        esperar_menu(driver)
        # Filtrado de categorías según argumento
        if not args.categoria.strip():
            categorias = obtener_links(driver)
            logger.info("Categorías encontradas:")
            for cat in categorias:
                logger.info(cat)
        else:
            categorias = obtener_links(driver, categorias=[args.categoria])

        # Navegación por cada categoría/subcategoría
        for cat_href in categorias:
            def regresar_al_inicio():
                driver.get(BASE_URL)

            # Intento de navegación; log de error si falla
            if not navegar_a_enlace(driver, cat_href, reset_fn=regresar_al_inicio):
                logger.warning(f"No se pudo acceder a la categoría o subcategoría: {cat_href}")
                continue

            # Extracción de productos con paginación
            productos = obtener_productos(driver, paginacion=True, paginas=args.paginas)
            logger.info(f"URL: {cat_href} | Páginas: {args.paginas} | Productos extraídos: {len(productos)}")
            productos_totales.extend(productos)

        # Refinamiento, almacenamiento y análisis de datos
        if productos_totales:
            datos_limpios = refinar_data(productos_totales)
            guardar_csv(datos_limpios, "products.csv")
            generar_analysis(datos_limpios, "analysis.txt")
            if args.modeloIA:
                analizar_con_ollama_csv("products.csv", modelo_ia=args.modeloIA)
            logger.info("Scraping completado exitosamente")
        else:
            logger.warning("No se extrajeron productos")

    except Exception as e:
        # Manejo robusto de errores
        logger.error(f"Error durante scraping: {str(e)}", exc_info=True)
    finally:
        # Cierre seguro del navegador
        driver.quit()

        # Manejo de errores: log detallado y cierre seguro
if __name__ == "__main__":
    # Punto de entrada principal
    main()
