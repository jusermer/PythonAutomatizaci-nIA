from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scraper.navegador import TIEMPO_ESPERA

from typing import List, Any
def selenium_wait_and_read(driver, selector: str, by: Any = By.CSS_SELECTOR, timeout: int = TIEMPO_ESPERA) -> List[Any]:
    """
    Espera a que los elementos estén presentes y luego los lee.
    Args:
        driver: Selenium WebDriver
        selector: Selector CSS o By
        by: Tipo de selector (por defecto By.CSS_SELECTOR)
        timeout: Tiempo de espera
    Returns:
        Lista de elementos encontrados
    """
    wait = WebDriverWait(driver, timeout)
    wait.until(EC.presence_of_all_elements_located((by, selector)))
    return driver.find_elements(by, selector)
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from scraper.navegador import TIEMPO_ESPERA, BASE_URL
import logging
logger = logging.getLogger(__name__)

from typing import Optional, Set, Union
def parse_paginas(paginas: Union[str, list, None]) -> Optional[Set[int]]:
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
    txt = str(paginas).strip()
    paginas_set = set()
    for chunk in txt.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            try:
                start, end = chunk.split("-", 1)
                start_n = int(start.strip())
                end_n = int(end.strip())
                paginas_set.update(range(start_n, end_n + 1))
            except ValueError:
                continue
        else:
            try:
                paginas_set.add(int(chunk))
            except ValueError:
                continue
    return paginas_set

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
    def scrape_actual():
        try:
            items = selenium_wait_and_read(driver, "thumbnail", By.CLASS_NAME, TIEMPO_ESPERA)
        except TimeoutException:
            logger.warning("No se encontraron productos en la página")
            return []
        logger.info(f"URL actual: {driver.current_url}")
        logger.info(f"Cantidad de productos en la página: {len(items)}")
        pagina_productos = []
        for item in items:
            nombre = item.find_element(By.CLASS_NAME, "title").text.strip()
            precio = item.find_element(By.CLASS_NAME, "price").text.strip()
            try:
                rating_raw = item.find_element(By.CSS_SELECTOR, "p[data-rating]").get_attribute("data-rating")
            except NoSuchElementException:
                rating_raw = "0"
            rating = int(rating_raw) if rating_raw else 0
            reviews = item.find_element(By.CLASS_NAME, "review-count").text.strip()
            pagina_productos.append({
                "nombre": nombre,
                "precio": precio,
                "rating": rating,
                "reviews": reviews
            })
        return pagina_productos
    # Detectar paginación
    paginacion_links = driver.find_elements(By.CSS_SELECTOR, "ul.pagination a")
    logger.info(f"Links de paginación encontrados: {[link.get_attribute('href') for link in paginacion_links]}")
    paginas_disponibles = set()
    for link in paginacion_links:
        texto = link.text.strip()
        if texto.isdigit():
            paginas_disponibles.add(int(texto))
    if not paginas_disponibles:
        productos.extend(scrape_actual())
        return productos

    # Si se pasan páginas específicas, solo recorre esas
    if paginas:
        paginas_a_visitar = parse_paginas(paginas)
        paginas_validas = set()
        if 1 in paginas_a_visitar:
            paginas_validas.add(1)
        paginas_validas.update(paginas_a_visitar & paginas_disponibles)
        paginas_validas = sorted(paginas_validas)
        if not paginas_validas:
            logger.warning("Ninguna de las páginas seleccionadas existe en la paginación.")
            return productos
        base_url = driver.current_url
        for pagina in paginas_validas:
            logger.info(f"Procesando página: {pagina}")
            target_url = paginacion_url(base_url, pagina)
            # Para la página 1, no es necesario cambiar de URL si ya estamos en la base
            if pagina == 1:
                logger.info(f"Extrayendo información de la página {pagina}")
                page_products = scrape_actual()
            else:
                if driver.current_url != target_url:
                    try:
                        driver.get(target_url)
                    except WebDriverException as e:
                        logger.warning(f"No se pudo cargar la página {pagina} ({target_url}): {e}")
                        break
                logger.info(f"Extrayendo información de la página {pagina}")
                page_products = scrape_actual()
            if not page_products:
                logger.warning(f"No se encontraron productos en la página {pagina}. Se detiene la extracción de páginas.")
                break
            productos.extend(page_products)
        return productos

    # Si no se pasan páginas, recorre toda la paginación automática
    while True:
        productos.extend(scrape_actual())
        next_links = driver.find_elements(By.CSS_SELECTOR, "a.page-link.next")
        if not next_links:
            break
        next_link = next_links[0]
        if "disabled" in next_link.get_attribute("class"):
            break
        href = next_link.get_attribute("href")
        if not href:
            break
        prev_url = driver.current_url
        wait = WebDriverWait(driver, TIEMPO_ESPERA)
        try:
            next_link.click()
            wait.until(EC.url_changes(prev_url))
        except WebDriverException:
            logger.warning("No se pudo hacer click en 'Siguiente', navegando por href en su lugar")
            driver.get(href)
            wait.until(EC.url_changes(prev_url))
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

def navigate_to_href(driver, href, reset_fn=None, prefer_click=True):
    if not href:
        return False
    normalizado = _normalizar_href(href)
    if not normalizado:
        return False
    def _normalizar_url(u):
        parsed = urlparse(u)
        return parsed.path + ("?" + parsed.query if parsed.query else "")
    target_abs = _resolver_href(driver.current_url, normalizado)
    if target_abs:
        current_norm = _normalizar_url(driver.current_url)
        target_norm = _normalizar_url(target_abs)
        if current_norm == target_norm:
            return True
    el = _encontrar_link_elemento(driver, normalizado)
    if el and prefer_click:
        try:
            el.click()
            return True
        except WebDriverException:
            logger.debug("Click falló, se intentará navegar por href")
    if reset_fn:
        reset_fn()
        el = _encontrar_link_elemento(driver, normalizado)
        if el and prefer_click:
            try:
                el.click()
                return True
            except WebDriverException:
                logger.debug("Click falló tras reset, se intentará navegar por href")
    abs_url = _resolver_href(driver.current_url, normalizado)
    if abs_url:
        try:
            driver.get(abs_url)
            return True
        except WebDriverException:
            logger.warning(f"No se pudo navegar a {abs_url}")
    return False
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse

from .navegador import TIEMPO_ESPERA

def obtener_hrefs(driver, css_selector, wait_selector=None):
    wait_selector = wait_selector or css_selector
    elementos = selenium_wait_and_read(driver, wait_selector, By.CSS_SELECTOR, TIEMPO_ESPERA)
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
            if sub_href and "allinone" in sub_href:
                # Solo agregar subcategorías si pertenecen a la categoría principal
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
