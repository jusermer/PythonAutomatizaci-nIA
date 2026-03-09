import logging
from selenium import webdriver

BASE_URL = "https://webscraper.io/test-sites/e-commerce/static"
TIEMPO_ESPERA = 10

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from selenium.webdriver.chrome.options import Options

def inicializar_driver():
    """Inicializa el driver de Chrome en modo headless y navega a BASE_URL."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    driver.get(BASE_URL)
    return driver

def esperar_menu(driver):
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    wait = WebDriverWait(driver, TIEMPO_ESPERA)
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#side-menu a")))
