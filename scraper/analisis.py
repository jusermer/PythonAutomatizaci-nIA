import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generar_analysis(productos, filename):
    """
    Genera un reporte de análisis de productos y lo guarda en un archivo de texto.

    Uso:
        Esta función calcula estadísticas básicas (total, promedio de precios) y destaca los tres mejores productos,
        guardando el análisis en un archivo de texto.

    Parámetros:
        productos (list[dict]): Lista de productos refinados.
        filename (str): Nombre del archivo de salida.

    Retorno:
        None

    Ejemplo:
        generar_analysis(productos_limpios, "analysis.txt")
    """
    # Validación inicial: lista vacía
    if not productos:
        logger.warning("No hay productos para analizar")
        return
    total = len(productos)
    precios = [p["precio"] for p in productos]
    promedio = sum(precios) / total
    # Ordena productos por rating, reviews y precio, selecciona los 3 mejores
    top3 = sorted(
        productos,
        key=lambda x: (x["rating"], x["reviews"], x["precio"]),
        reverse=True
    )[:3]
    # Escribe el análisis en el archivo
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

    Uso:
        Esta función lee el archivo CSV de productos, construye prompts para IA, envía la consulta a Ollama
        y almacena la respuesta en ai_summary.md. Permite categorizar productos y detectar anomalías.

    Parámetros:
        ruta_csv (str): Ruta al archivo CSV de productos.
        modelo_ia (str): Modelo de IA a utilizar (por defecto 'llama3').

    Retorno:
        None

    Ejemplo:
        analizar_con_ollama_csv("products.csv", modelo_ia="llama3")
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
            prompt_categoriza = f"Categoriza los productos en tipo de tecnología en la lista de productos (responde en español):\n{contenido_csv}"
            pregunta_anomalias = "¿Qué anomalías encuentras en este CSV de productos? Responde en español."
            mensajes = [
                {"role": "user", "content": prompt_categoriza},
                {"role": "user", "content": pregunta_anomalias}
            ]
        try:
            respuesta = cliente_ollama.chat(model=modelo_ia, messages=mensajes)
            logger.info("Respuesta de Ollama almacenada en ai_summary.md")
            fecha_guardado = __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"Guardando ai_summary.md a las {fecha_guardado}")
            categoria_text = ''
            anomalias_text = ''
            # Extraer solo el contenido limpio del modelo
            if isinstance(respuesta, dict):
                if 'messages' in respuesta and isinstance(respuesta['messages'], list):
                    if len(respuesta['messages']) > 0 and 'content' in respuesta['messages'][0]:
                        categoria_text = respuesta['messages'][0]['content'].strip()
                    if len(respuesta['messages']) > 1 and 'content' in respuesta['messages'][1]:
                        anomalias_text = respuesta['messages'][1]['content'].strip()
                elif 'message' in respuesta and 'content' in respuesta['message']:
                    categoria_text = respuesta['message']['content'].strip()
            elif isinstance(respuesta, str):
                categoria_text = respuesta.strip()
            else:
                categoria_text = str(respuesta).strip()

            # Si no hay respuesta de anomalías, hacer una consulta aparte
            if not anomalias_text:
                logger.info("No se obtuvo respuesta de anomalías, realizando consulta separada...")
                respuesta_anomalias = cliente_ollama.chat(model=modelo_ia, messages=[{"role": "user", "content": pregunta_anomalias}])
                if isinstance(respuesta_anomalias, dict):
                    if 'messages' in respuesta_anomalias and isinstance(respuesta_anomalias['messages'], list):
                        if len(respuesta_anomalias['messages']) > 0 and 'content' in respuesta_anomalias['messages'][0]:
                            anomalias_text = respuesta_anomalias['messages'][0]['content'].strip()
                    elif 'message' in respuesta_anomalias and 'content' in respuesta_anomalias['message']:
                        anomalias_text = respuesta_anomalias['message']['content'].strip()
                elif isinstance(respuesta_anomalias, str):
                    anomalias_text = respuesta_anomalias.strip()
                else:
                    anomalias_text = str(respuesta_anomalias).strip()

            with open("ai_summary.md", "w", encoding="utf-8") as archivo_md:
                archivo_md.write("\n---\n")
                archivo_md.write(f"Fecha de guardado: {fecha_guardado}\n")
                archivo_md.write("\n# Análisis de Categoría\n")
                archivo_md.write(f"Prompt:\n{prompt_categoriza}\n")
                archivo_md.write("Respuesta:\n\n")
                archivo_md.write("# Respuesta de Categoría\n")
                archivo_md.write(categoria_text + "\n\n")
                archivo_md.write("# Análisis de Anomalías\n")
                archivo_md.write(anomalias_text + "\n")
            logger.info(f"ai_summary.md guardado correctamente a las {fecha_guardado}")
        except Exception as ollama_error:
            logger.error(f"Error en Ollama: {ollama_error}")
    except Exception as e:
        logger.error(f"Error al procesar el CSV: {e}")
