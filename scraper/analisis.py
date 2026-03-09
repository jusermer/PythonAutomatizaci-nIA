import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generar_analysis(productos, filename):
    """
    Genera un reporte de análisis de productos y lo guarda en un archivo de texto.
    """
    if not productos:
        logger.warning("No hay productos para analizar")
        return
    total = len(productos)
    precios = [p["precio"] for p in productos]
    promedio = sum(precios) / total
    top3 = sorted(
        productos,
        key=lambda x: (x["rating"], x["reviews"], x["precio"]),
        reverse=True
    )[:3]
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Total de productos: {total}\n")
        f.write(f"Precio promedio: ${promedio:.2f}\n")
        f.write("Top 3 productos destacados:\n")
        for p in top3:
            f.write(f"- {p['nombre']} | {p['rating']} | {p['reviews']} reviews | ${p['precio']:.2f}\n")
    logger.info(f"Análisis generado en {filename}")

def analizar_con_ollama_csv(ruta_csv, modelo_ia="llama3"):
    """
    Realiza un análisis avanzado de productos usando Ollama.
    Lee el archivo CSV indicado, construye prompts y preguntas, envía la consulta a Ollama,
    y almacena la respuesta en ai_summary.md.
    Args:
        ruta_csv (str): Ruta al archivo CSV de productos.
    """
    try:
        from ollama import Client
    except ImportError as e:
        logger.warning(f"Ollama no está instalado. Instálalo con 'pip install ollama' para análisis avanzado. Detalle: {e}")
        return
    except Exception as e:
        logger.error(f"Error inesperado al importar Ollama: {e}")
        return
    import csv
    cliente_ollama = Client()
    try:
        with open(ruta_csv, encoding="utf-8") as archivo:
            lector = csv.reader(archivo)
            filas = list(lector)
            contenido_csv = "\n".join([",".join(fila) for fila in filas])
            prompt_categoriza = f"Categoriza los productos en tipo de tecnología en la lista de productos:\n{contenido_csv}"
            pregunta_anomalias = "¿Qué anomalías encuentras en este CSV de productos?"
            mensajes = [
                {"role": "user", "content": prompt_categoriza},
                {"role": "user", "content": pregunta_anomalias}
            ]
        try:
            respuesta = cliente_ollama.chat(model=modelo_ia, messages=mensajes)
            logger.info("Respuesta de Ollama almacenada en ai_summary.md")
            with open("ai_summary.md", "a", encoding="utf-8") as archivo_md:
                archivo_md.write("\n---\n\n")
                archivo_md.write(f"Fecha: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                archivo_md.write(f"Prompts:\n{prompt_categoriza}\n{pregunta_anomalias}\n\nRespuesta:\n{respuesta}\n")
        except Exception as ollama_error:
            logger.error(f"Error en Ollama: {ollama_error}")
    except Exception as e:
        logger.error(f"Error al procesar el CSV: {e}")
