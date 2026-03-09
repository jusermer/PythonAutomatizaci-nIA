# PythonAutomatizaciónIA — Web Scraping y Análisis con IA Local

Este proyecto implementa un sistema completo de automatización con Python y Selenium para extraer información de productos desde webscraper.io, procesarla, generar análisis estadísticos y complementarlo con un análisis adicional mediante un modelo de IA local ejecutado con Ollama.

---

## Características principales

- Navegación robusta entre categorías y subcategorías.
- Extracción de productos con paginación automática o por rango.
- Limpieza y deduplicación de datos.
- Análisis clásico: total, promedio, top 3 productos.
- Análisis avanzado con IA local (Ollama).
- Configuración mínima por argumentos.

---

## Estructura del proyecto

```
bogota/
│
├── main.py                # Flujo principal del scraper
├── scraper/               # Módulos: navegador.py, extraccion.py, limpieza.py, almacenamiento.py, analisis.py
│
├── products.csv           # Resultados del scraping
├── analysis.txt           # Análisis clásico
├── ai_summary.md          # Análisis generado por IA local
│
├── requirements.txt       # Dependencias del proyecto
└── README.md              # Documentación del proyecto
```

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
git clone https://github.com/jusermer/PythonAutomatizacionIA
cd bogota
```
2. Crear y activar un entorno virtual
```bash
python -m venv venv
venv\Scripts\activate
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

## Configuración mínima

El proyecto permite configurar:
- Categoría (--categoria)
- Páginas a scrapear (--paginas)
- Modelo IA (--modeloIA)

Ejemplo:
```bash
python main.py --categoria phones --paginas 1-3 --modeloIA llama3
```

| Parámetro   | Descripción                | Ejemplo                  |
|-------------|----------------------------|--------------------------|
| --categoria | Categoría del menú lateral | phones                   |
| --paginas   | Rango o lista de páginas   | 1-3 , 1,4,7              |
| --modeloIA  | Modelo IA local            | llama3 , mistral , phi3  |

---

## Ejecución

Ejecutar el scraper con valores por defecto:
```bash
python main.py
```

Ejecutar con configuración personalizada:
```bash
python main.py --categoria laptops --paginas 2-4 --modeloIA llama3
```

### Resultados generados

Después de la ejecución, el proyecto genera:

#### products.csv (ejemplo)
| nombre         | precio | rating | reviews |
|---------------|--------|--------|---------|
| Laptop X      | 1200   | 5      | 23      |
| Phone Y       | 800    | 4      | 15      |

#### analysis.txt (ejemplo)
Total de productos: 20
Precio promedio: $950.00
Top 3 productos destacados:
- Laptop X | 5 | 23 reviews | $1200.00
- Phone Y  | 4 | 15 reviews | $800.00

#### ai_summary.md (ejemplo)
# Análisis de Categoría
...respuesta IA...
# Análisis de Anomalías
...respuesta IA...

---

## Arquitectura técnica

- Normalización de URLs.
- Resolución de rutas relativas y absolutas.
- Búsqueda inteligente de enlaces en el DOM.
- Mecanismo de recuperación ante fallos: click, reintento, navegación directa.
- Esperas explícitas para garantizar estabilidad.
- Manejo de paginación automática o manual.
- Limpieza y conversión de datos numéricos.
- Eliminación de duplicados.
- Uso de Ollama para ejecutar modelos locales.
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

## Contribución

¿Quieres mejorar el proyecto? Abre un issue o pull request en GitHub.

---

## Licencia

Uso libre para fines educativos y de práctica.





