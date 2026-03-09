# PythonAutomatizaciónIA — Web Scraping y Análisis con IA Local

Este proyecto implementa un sistema completo de automatización con Python y Selenium para extraer información de productos desde webscraper.io, procesarla, generar análisis estadísticos y complementarlo con un análisis adicional mediante un modelo de IA local ejecutado con Ollama.
El objetivo es generar la Automatización con IA, integrando scraping robusto, configuración mínima, análisis clásico y análisis con un modelo de lenguaje ejecutado localmente.


---

## Características principales

### Scraper robusto
- Navegación estable entre categorías y subcategorías.
- Normalización y resolución de URLs relativas y absolutas.
- Mecanismo de navegación tolerante a fallos (click, reintento, fallback a navegación directa).
- Extracción de productos con manejo de paginación automática o por rango.
- Limpieza y deduplicación de datos.
Análisis clásico
- Cálculo de total de productos.
- Precio promedio.
- Selección de los tres productos más destacados.
- Exportación del análisis a analysis.txt.
### Análisis con IA local
- Lectura del archivo CSV generado por el scraper.
- Ejecución de dos consultas al modelo local (resumen general y detección de anomalías).
- Exportación del análisis a ai_summary.md.
- Modelo configurable por parámetro.
### Configuración mínima
El usuario puede definir:
- Categoría a scrapear.
- Páginas a procesar.
- Modelo de IA a utilizar. 

---
## Estructura del proyecto

PythonAutomatizaciónIA/
│
├── main.py                # Flujo principal del scraper
├── analysis.py            # Análisis clásico e integración con IA local
├── navigation.py          # Funciones de navegación y normalización de URLs
├── scraping.py            # Extracción de enlaces y productos
├── utils.py               # Limpieza de datos y funciones auxiliares
│
├── products.csv           # Resultados del scraping
├── analysis.txt           # Análisis clásico
├── ai_summary.md          # Análisis generado por IA local
│
├── requirements.txt       # Dependencias del proyecto
└── README.md              # Documentación del proyecto

---

## Requisitos

- Python 3.10 o superior.
- Google Chrome y ChromeDriver compatibles.
- Librerías Python incluidas en requirements.txt.
- Ollama instalado en el sistema.
- Descarga: https://ollama.com/download
- Modelo IA local descargado, por ejemplo:
```bash
    ollama pull llama3
```

---

## Instalación

1. Clonar el repositorio
```bash
git clone https://github.com/jusermer/PythonAutomatizaci-nIA
cd PythonAutomatizaci-nIA
```
2. Crear y activar un entorno virtual
```bash
python -m venv venv
source venv/Scripts/activate
```
3. Instalar dependencias
```bash
pip install -r requirements.txt
```

4. Instalar Ollama (si no está instalado)
Descargar desde:
https://ollama.com/download

5. Descargar el modelo IA
```bash
  ollama pull llama3
```
---

## Configuración mínim

El proyecto permite configurar:
- Categoría (--categoria)
- Páginas a scrapear (--paginas)
- Modelo IA (--modelo)
Ejemplo:
```bash
python main.py --categoria phones --paginas 1-3 --modelo llama3
```
Parámetros disponibles
| Parámetro   | Descripción                | Ejemplo                  |
|-------------|----------------------------|---------------------------|
| --categoria | Categoría del menú lateral | phones                    |
| --paginas   | Rango o lista de páginas   | 1-3 , 1,4,7               |
| --modelo    | Modelo IA local            | llama3 , mistral , phi3   |
---

## Ejecución

Ejecutar el scraper con valores por defecto:  
```bash
python main.py
```

Ejecutar con configuración personalizada

```bash
python main.py --categoria laptops --paginas 2-4 --modelo llama3
```

### Resultados generados

Después de la ejecución, el proyecto genera:
### products.csv
Archivo con los productos extraídos, incluyendo:
- nombre
- precio
- rating
- reviews
### analysis.txt
Análisis clásico con:
- total de productos
- precio promedio
- top 3 productos
### ai_summary.md
Análisis generado por IA local con:
- resumen general
- anomalías detectadas
- observaciones relevantes 

---

## Arquitectura técnica

### Navegación robusta
El sistema implementa:
- Normalización de URLs.
- Resolución de rutas relativas y absolutas.
- Búsqueda inteligente de enlaces en el DOM.
- Mecanismo de recuperación ante fallos:
- intento de click
- reintento tras reset
- navegación directa por URL
### Extracción de productos
- Esperas explícitas para garantizar estabilidad.
- Manejo de paginación automática o manual.
- Limpieza y conversión de datos numéricos.
- Eliminación de duplicados.
### Integración con IA local
- Uso de ollama.generate() para ejecutar modelos locales.
- Modelo configurable desde la línea de comandos.
- Dos consultas obligatorias para cumplir la Kata.
- Exportación del análisis en formato Markdown.

---

## Pruebas recomendadas

- Ejecutar scraping completo sin parámetros.
- Probar diferentes categorías.
- Probar rangos de páginas.
- Cambiar el modelo IA.
- Verificar los archivos generados.
- Validar que el análisis IA se genera correctamente.

---

## Conclusión

Este proyecto integra scraping avanzado, análisis de datos y modelos de lenguaje locales en un flujo completo, robusto y documentado.

---

## Licencia

Uso libre para fines educativos y de práctica.





