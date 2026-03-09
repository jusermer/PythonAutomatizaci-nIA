from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scraper.navegador import TIEMPO_ESPERA

from typing import List, Any
def esperar_y_leer_elementos(driver, selector: str, por: Any = By.CSS_SELECTOR, tiempo_espera: int = TIEMPO_ESPERA) -> List[Any]:
    """
    Espera a que los elementos estén presentes en el DOM y luego los devuelve.

    Uso:
        Esta función es útil para garantizar que los elementos requeridos por el scraper
        estén disponibles antes de interactuar con ellos, evitando errores de sincronización.

    Parámetros:
        driver (Selenium WebDriver): Instancia del navegador.
        selector (str): Selector CSS o tipo By para localizar los elementos.
        por (Any): Tipo de selector (por defecto By.CSS_SELECTOR).
        tiempo_espera (int): Tiempo máximo de espera en segundos.

    Retorno:
        List[Any]: Lista de elementos encontrados.

    Ejemplo:
        elementos = esperar_y_leer_elementos(driver, "div.producto", By.CSS_SELECTOR, 10)
    """
    # Espera explícita hasta que los elementos estén presentes en el DOM
    espera = WebDriverWait(driver, tiempo_espera)
    espera.until(EC.presence_of_all_elements_located((por, selector)))
    # Devuelve la lista de elementos encontrados
    return driver.find_elements(por, selector)
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from scraper.navegador import TIEMPO_ESPERA, BASE_URL
import logging
logger = logging.getLogger(__name__)

from typing import Optional, Set, Union
def interpretar_paginas(paginas: Union[str, list, None]) -> Optional[Set[int]]:
    """
    Convierte expresiones de páginas a un conjunto de enteros.

    Propósito:
        - Permite seleccionar páginas específicas para scraping.

    Parámetros:
        paginas (str | list | None): Expresión de páginas ('2-5', '2,3,5', lista de enteros).

    Retorno:
        set[int] | None: Conjunto de números de página o None si no hay selección.
    """
    if paginas is None:
        return None
    if isinstance(paginas, (list, tuple, set)):
        return set(int(p) for p in paginas)
    texto = str(paginas).strip()
    conjunto_paginas = set()
    for fragmento in texto.split(","):
        fragmento = fragmento.strip()
        if not fragmento:
            continue
        if "-" in fragmento:
            try:
                inicio, fin = fragmento.split("-", 1)
                inicio_n = int(inicio.strip())
                fin_n = int(fin.strip())
                conjunto_paginas.update(range(inicio_n, fin_n + 1))
            except ValueError:
                continue
        else:
            try:
                conjunto_paginas.add(int(fragmento))
            except ValueError:
                continue
    return conjunto_paginas

def paginacion_url(base_url: str, page_number: int) -> str:
    """
    Construye la URL de una página determinada usando el parámetro 'page'.

    Propósito:
        - Genera la URL para navegar a una página específica.

    Parámetros:
        base_url (str): URL base de la categoría.
        page_number (int): Número de página.

    Retorno:
        str: URL de la página solicitada.
    """
    parsed = urlparse(base_url)
    query = parsed.query
    query_parts = []
    if query:
        for part in query.split("&"):
            if not part.startswith("page="):
                query_parts.append(part)
    if page_number > 1:
        query_parts.append(f"page={page_number}")
    query_str = "&".join(query_parts)
    return parsed._replace(query=query_str).geturl()

from selenium.webdriver.chrome.webdriver import WebDriver
from typing import List, Dict, Union
def obtener_productos(driver: WebDriver, paginacion: bool = True, paginas: Union[str, list, None] = None) -> List[Dict]:
    """
    Extrae los productos de la categoría actual.

    Propósito:
        - Realiza scraping de productos en la categoría/subcategoría actual.
        - Soporta paginación automática y selección manual de páginas.

    Parámetros:
        driver (selenium.webdriver.Chrome): Driver de Selenium.
        paginacion (bool): Si True, recorre toda la paginación automáticamente.
        paginas (str | list | None): Expresión de páginas a extraer.

    Retorno:
        list[dict]: Lista de productos extraídos.
    """
    productos = []
    def extraer_actual():
        try:
            elementos = esperar_y_leer_elementos(driver, "thumbnail", By.CLASS_NAME, TIEMPO_ESPERA)
        except TimeoutException:
            logger.warning("No se encontraron productos en la página")
            return []
        logger.info(f"URL actual: {driver.current_url}")
        logger.info(f"Cantidad de productos en la página: {len(elementos)}")
        productos_pagina = []
        for elemento in elementos:
            nombre = elemento.find_element(By.CLASS_NAME, "title").text.strip()
            precio = elemento.find_element(By.CLASS_NAME, "price").text.strip()
            try:
                calificacion_raw = elemento.find_element(By.CSS_SELECTOR, "p[data-rating]").get_attribute("data-rating")
            except NoSuchElementException:
                calificacion_raw = "0"
            calificacion = int(calificacion_raw) if calificacion_raw else 0
            opiniones = elemento.find_element(By.CLASS_NAME, "review-count").text.strip()
            productos_pagina.append({
                "nombre": nombre,
                "precio": precio,
                "calificacion": calificacion,
                "opiniones": opiniones
            })
        return productos_pagina
    # Detectar paginación
    enlaces_paginacion = driver.find_elements(By.CSS_SELECTOR, "ul.pagination a")
    logger.info(f"Enlaces de paginación encontrados: {[enlace.get_attribute('href') for enlace in enlaces_paginacion]}")
    paginas_disponibles = set()
    for enlace in enlaces_paginacion:
        texto = enlace.text.strip()
        if texto.isdigit():
            paginas_disponibles.add(int(texto))
    if not paginas_disponibles:
        productos.extend(extraer_actual())
        return productos

    # Si se pasan páginas específicas, solo recorre esas
    if paginas:
        paginas_a_visitar = interpretar_paginas(paginas)
        paginas_validas = set()
        if 1 in paginas_a_visitar:
            paginas_validas.add(1)
        paginas_validas.update(paginas_a_visitar & paginas_disponibles)
        paginas_validas = sorted(paginas_validas)
        if not paginas_validas:
            logger.warning("Ninguna de las páginas seleccionadas existe en la paginación.")
            return productos
        url_base = driver.current_url
        for pagina in paginas_validas:
            logger.info(f"Procesando página: {pagina}")
            url_destino = paginacion_url(url_base, pagina)
            # Para la página 1, no es necesario cambiar de URL si ya estamos en la base
            if pagina == 1:
                logger.info(f"Extrayendo información de la página {pagina}")
                productos_pagina = extraer_actual()
            else:
                if driver.current_url != url_destino:
                    try:
                        driver.get(url_destino)
                    except WebDriverException as e:
                        logger.warning(f"No se pudo cargar la página {pagina} ({url_destino}): {e}")
                        break
                logger.info(f"Extrayendo información de la página {pagina}")
                productos_pagina = extraer_actual()
            if not productos_pagina:
                logger.warning(f"No se encontraron productos en la página {pagina}. Se detiene la extracción de páginas.")
                break
            productos.extend(productos_pagina)
        return productos

    # Si no se pasan páginas, recorre toda la paginación automática
    while True:
        productos.extend(extraer_actual())
        enlaces_siguiente = driver.find_elements(By.CSS_SELECTOR, "a.page-link.next")
        if not enlaces_siguiente:
            break
        enlace_siguiente = enlaces_siguiente[0]
        if "disabled" in enlace_siguiente.get_attribute("class"):
            break
        href = enlace_siguiente.get_attribute("href")
        if not href:
            break
        url_anterior = driver.current_url
        espera = WebDriverWait(driver, TIEMPO_ESPERA)
        try:
            enlace_siguiente.click()
            espera.until(EC.url_changes(url_anterior))
        except WebDriverException:
            logger.warning("No se pudo hacer clic en 'Siguiente', navegando por href en su lugar")
            driver.get(href)
            espera.until(EC.url_changes(url_anterior))
    return productos
# Dependencias para navegación
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from urllib.parse import urlparse
from scraper.navegador import BASE_URL
import logging
logger = logging.getLogger(__name__)

def _normalizar_href(href):
    """
    Normaliza un href a ruta relativa (path + query).
    Útil para comparar enlaces en el DOM.
    """
    if not href:
        return None
    parsed = urlparse(href)
    return parsed.path + ("?" + parsed.query if parsed.query else "")

def _resolver_href(base_url, href):
    """
    Resuelve un href relativo (o absoluto) a una URL absoluta.
    Útil para navegación programática.
    """
    if not href:
        return None
    from urllib.parse import urljoin
    return urljoin(base_url, href)

def _encontrar_link_elemento(driver, href):
    """
    Busca un <a href='...'> coincidente en el DOM actual.
    Útil para encontrar enlaces navegables.
    """
    if not href:
        return None
    candidatos = [href]
    abs_current = _resolver_href(driver.current_url, href)
    if abs_current and abs_current != href:
        candidatos.append(abs_current)
    abs_base = _resolver_href(BASE_URL, href)
    if abs_base and abs_base not in candidatos:
        candidatos.append(abs_base)
    for candidate in candidatos:
        try:
            return driver.find_element(By.XPATH, f"//a[@href='{candidate}']")
        except NoSuchElementException:
            continue
    return None

def navegar_a_enlace(driver, href, reset_fn=None, prefer_click=True):
    if not href:
        return False
    enlace_normalizado = _normalizar_href(href)
    if not enlace_normalizado:
        return False
    def _normalizar_url_actual(url):
        partes = urlparse(url)
        return partes.path + ("?" + partes.query if partes.query else "")
    enlace_absoluto = _resolver_href(driver.current_url, enlace_normalizado)
    if enlace_absoluto:
        actual_normalizado = _normalizar_url_actual(driver.current_url)
        destino_normalizado = _normalizar_url_actual(enlace_absoluto)
        if actual_normalizado == destino_normalizado:
            return True
    elemento = _encontrar_link_elemento(driver, enlace_normalizado)
    if elemento and prefer_click:
        try:
            elemento.click()
            return True
        except WebDriverException:
            logger.debug("El clic falló, se intentará navegar por el enlace directamente")
    if reset_fn:
        reset_fn()
        elemento = _encontrar_link_elemento(driver, enlace_normalizado)
        if elemento and prefer_click:
            try:
                elemento.click()
                return True
            except WebDriverException:
                logger.debug("El clic falló tras reinicio, se intentará navegar por el enlace directamente")
    enlace_absoluto_final = _resolver_href(driver.current_url, enlace_normalizado)
    if enlace_absoluto_final:
        try:
            driver.get(enlace_absoluto_final)
            return True
        except WebDriverException:
            logger.warning(f"No se pudo navegar a {enlace_absoluto_final}")
    return False
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse

from .navegador import TIEMPO_ESPERA

def obtener_hrefs(driver, css_selector, wait_selector=None):
    wait_selector = wait_selector or css_selector
    elementos = esperar_y_leer_elementos(driver, wait_selector, By.CSS_SELECTOR, TIEMPO_ESPERA)
    urls_finales = []
    for el in elementos:
        href = el.get_attribute("href")
        if not href:
            continue
        parsed = urlparse(href)
        href_rel = parsed.path + ("?" + parsed.query if parsed.query else "")
        urls_finales.append(href_rel)
    return list(dict.fromkeys(urls_finales))

def obtener_links(driver, categorias=None):
    """
    Recorre el menú lateral y obtiene todas las URLs de categorías y subcategorías.
    Usa los selectores validados en scraper.py.
    """
    wait = WebDriverWait(driver, TIEMPO_ESPERA)
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#side-menu a")))
    categorias_elems = driver.find_elements(By.CSS_SELECTOR, "#side-menu a")
    urls_principales = [c.get_attribute("href") for c in categorias_elems]
    urls_finales = []
    for url in urls_principales:
        if categorias:
            categorias_lower = [c.lower() for c in categorias]
            parsed = urlparse(url)
            # Extraer el último segmento del path
            path_segment = parsed.path.strip("/").split("/")[-1].lower()
            if path_segment not in categorias_lower:
                continue
        urls_finales.append(url)
        driver.get(url)
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "thumbnail")))
        subcategorias = driver.find_elements(By.CSS_SELECTOR, ".subcategory-link, .category-link")
        for sub in subcategorias:
            sub_href = sub.get_attribute("href")
            if not sub_href:
                continue
            # Si hay filtro de categorías, solo agregar subcategorías que pertenezcan a la principal
            if categorias:
                parsed_sub = urlparse(sub_href)
                parent_segment = parsed.path.strip("/").split("/")[-1].lower()
                sub_segments = parsed_sub.path.strip("/").split("/")
                if parent_segment not in sub_segments:
                    continue
            urls_finales.append(sub_href)
    return list(dict.fromkeys(urls_finales))

def obtener_sublinks(driver):
    """
    Obtiene subcategorías usando los selectores validados.
    """
    wait = WebDriverWait(driver, TIEMPO_ESPERA)
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "thumbnail")))
    subcategorias = driver.find_elements(By.CSS_SELECTOR, ".subcategory-link, .category-link")
    return [sub.get_attribute("href") for sub in subcategorias if sub.get_attribute("href")]
