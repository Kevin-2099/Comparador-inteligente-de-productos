# 🧠 Comparador Inteligente de Productos

Comparador automático de productos basado en procesamiento de lenguaje natural (NLP), diseñado para analizar descripciones de hasta **5 productos** en **español** o **inglés**.

La aplicación identifica categorías relevantes, extrae especificaciones técnicas, analiza el sentimiento del texto y genera comparaciones automáticas con gráficos, ranking ponderado e informes exportables mediante una interfaz desarrollada con **Gradio**.

---

# ✨ Características principales

## 🔍 Análisis automático

El sistema procesa automáticamente los textos para:

- Detectar el idioma (Español/Inglés).
- Dividir el contenido en oraciones.
- Clasificar las frases por categorías mediante palabras clave.
- Extraer especificaciones técnicas.
- Analizar el sentimiento de cada oración.
- Comparar entre **2 y 5 productos**.

---

## 📌 Categorías soportadas

### Español

- Pantalla
- Cámara
- Batería
- Rendimiento
- Almacenamiento
- Conectividad
- Precio / Calidad
- Diseño
- Software
- Audio
- Durabilidad

### English

- Screen
- Camera
- Battery
- Performance
- Storage
- Connectivity
- Price / Quality
- Design
- Software
- Audio
- Durability

---

## 🧮 Sistema inteligente de puntuación

Cada categoría utiliza un sistema de evaluación específico.

### Categorías numéricas

Se extraen automáticamente valores como:

- Tamaño de pantalla
- Resolución
- Megapíxeles
- Capacidad de batería (mAh)
- Potencia de carga (W)
- Memoria RAM
- Almacenamiento
- Tecnologías de conectividad

Los valores obtenidos se convierten en una puntuación comparable entre productos.

### Categorías cualitativas

Las categorías como:

- Precio / Calidad
- Diseño
- Software
- Audio
- Durabilidad

se evalúan mediante análisis de sentimiento de las evidencias encontradas.

---

## 💬 Análisis de sentimiento

El comparador clasifica automáticamente cada oración como:

- ✅ Positiva
- ❌ Negativa
- ➖ Neutra

Además, detecta negaciones para interpretar correctamente expresiones como:

- "No es rápido"
- "Not good"

---

## 📊 Comparación inteligente

Para cada categoría el sistema calcula:

- Score obtenido
- Score normalizado
- Nivel de confianza
- Evidencias encontradas
- Producto ganador

Los empates se detectan mediante un margen de tolerancia, evitando diferencias insignificantes entre puntuaciones.

Los niveles de confianza son:

- 🟢 Alta
- 🟠 Media
- 🔴 Baja

---

## 🏆 Resultado final

Tras analizar todas las categorías, la aplicación genera:

- Ganador por categoría
- Conteo de victorias
- Resultado general
- Ranking ponderado configurable
- Resumen automático en lenguaje natural

---

# 📈 Visualización

La aplicación muestra los resultados mediante:

- 📝 Resumen en Markdown
- 📋 Tabla HTML
- 📊 Gráfico Radar
- 📊 Gráfico de Barras
- 📦 JSON estructurado

---

# 📂 Entrada de datos

Cada producto puede introducirse mediante:

- Texto escrito manualmente.
- Archivo **TXT**.
- Archivo **PDF**.

---

# 📤 Exportación

Los resultados pueden descargarse en:

- 📥 CSV
- 📄 Word (.docx)

---

# ⚙️ Funcionalidades avanzadas

- Ranking ponderado mediante pesos personalizados.
- Categorías personalizadas mediante JSON.
- Caché automática para acelerar comparaciones repetidas.
- Limpieza manual de la caché.
- Historial de comparaciones durante la sesión.
- Detección automática del idioma.
- Extracción de múltiples especificaciones por producto.
- Normalización automática de puntuaciones.

---

# 📄 Licencia

Este proyecto se distribuye bajo una **licencia propietaria con acceso al código (source-available)**.

El código fuente se pone a disposición únicamente para fines de **visualización, evaluación y aprendizaje**.

❌ No está permitido copiar, modificar, redistribuir, sublicenciar, ni crear obras derivadas del software o de su código fuente sin autorización escrita expresa del titular de los derechos.

❌ El uso comercial del software, incluyendo su oferta como servicio (SaaS), su integración en productos comerciales o su uso en entornos de producción, requiere un **acuerdo de licencia comercial independiente**.

📌 El texto **legalmente vinculante** de la licencia es la versión en inglés incluida en el archivo `LICENSE`. 

Se proporciona una traducción al español en `LICENSE_ES.md` únicamente con fines informativos. En caso de discrepancia, prevalece la versión en inglés.

---

# Autor
Kevin-2099
