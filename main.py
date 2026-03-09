import argparse
from scraper.navegador import inicializar_driver, BASE_URL, TIEMPO_ESPERA, esperar_menu
from scraper.extraccion import obtener_links, obtener_sublinks, navigate_to_href, obtener_productos
from scraper.limpieza import refinar_data
from scraper.almacenamiento import guardar_csv
from scraper.analisis import generar_analysis, analizar_con_ollama_csv

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main() -> None:
    parser = argparse.ArgumentParser(description="Scraper de productos modular")
    parser.add_argument("--categoria", type=str, default="", help="computers, phones, etc. (filtra por nombre en el href de la categoría)")
    parser.add_argument("--paginas", type=str, default="", help="Expresión de páginas a extraer (ejemplo: '1-10' o '2,3,4')")
    parser.add_argument("--modeloIA", type=str, default="", help="Modelo de IA a utilizar para el análisis avanzado (ejemplo: 'llama3')")
    args = parser.parse_args()

    driver = inicializar_driver()
    esperar_menu(driver)
    
    productos_totales = []
    try:
        esperar_menu(driver)
        if not args.categoria.strip():
                categorias = obtener_links(driver)
                logger.info("Categorías encontradas:")
                for cat in categorias:
                    logger.info(cat)
        else:
            categorias = obtener_links(driver, categorias=[args.categoria])
            logger.info("Categorías filtradas:")

        for cat_href in categorias:
            def _reset_to_base():
                driver.get(BASE_URL)

            if not navigate_to_href(driver, cat_href, reset_fn=_reset_to_base):
                logger.warning(f"No se pudo acceder a la categoría: {cat_href}")
                continue

            subenlaces = obtener_sublinks(driver)
            if not subenlaces:
                # Si no hay subcategorías, extrae productos de la categoría
                productos = obtener_productos(driver, paginacion=True, paginas=args.paginas)
                logger.info(f"URL: {cat_href} | Páginas: {args.paginas} | Productos extraídos: {len(productos)}")
                productos_totales.extend(productos)
            else:
                for sub_href in subenlaces:
                    def _reset_to_category():
                        navigate_to_href(driver, cat_href, reset_fn=_reset_to_base, prefer_click=False)

                    if not navigate_to_href(driver, sub_href, reset_fn=_reset_to_category):
                        logger.warning(f"No se pudo acceder a la subcategoría: {sub_href}")
                        continue

                    productos = obtener_productos(driver, paginacion=True, paginas=args.paginas)
                    logger.info(f"URL: {sub_href} | Páginas: {args.paginas} | Productos extraídos: {len(productos)}")
                    productos_totales.extend(productos)

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
        logger.error(f"Error durante scraping: {str(e)}", exc_info=True)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
