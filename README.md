# 🧠 Comparador Inteligente de Productos
Comparador automático de descripciones de productos basado en categorías clave: pantalla, cámara, batería, rendimiento, almacenamiento y conectividad.

Funciona en español (ES) e inglés (EN), con opción de detección automática de idioma.

Este proyecto utiliza Gradio para ofrecer una interfaz intuitiva que permite comparar 2 hasta 5 productos a partir de sus textos descriptivos y generar:

- 🏆 Ganador general
- 📊 Ganadores por categoría
- 🔍 Evidencias textuales por categoría
- 💬 Análisis de sentimiento (positivo, negativo, neutro)
- 🧩 Salida en JSON estructurado
- 📝 Resumen en Markdown
- 🧱 Tabla HTML con scores y confianza
- 📥 Exportación CSV

## ✨ Características Principales
- 🔍 Detección por categorías

  El sistema analiza los textos y clasifica oraciones según palabras clave por idioma.
  
  Categorías soportadas:

  - ES
    - Pantalla
    - Cámara
    - Batería
    - Rendimiento
    - Almacenamiento
    - Conectividad
  - EN
    - Screen
    - Camera
    - Battery
    - Performance
    - Storage
    - Connectivity
- 🧮 Sistema inteligente de puntuación

  Cada categoría se evalúa numéricamente según los valores detectados y patrones de texto:
  
    - Pantalla: pulgadas + resolución
    - Batería: mAh y potencia de carga (W)
    - Rendimiento: CPU, RAM, velocidad de juego
    - Cámara: MP / sensores
    - Almacenamiento: GB / TB
    - Conectividad: 4G, 5G, WiFi, Bluetooth, NFC
  
  También calcula confianza de la evidencia por categoría (alta / baja) y gestiona empates explícitos.

- 🏆 Resultado general

  El comparador determina:
  
    - Ganador por categoría
    - Conteo de victorias
    - Ganador final entre todos los productos comparados (A, B, C… hasta E)
- 📤 Salidas detalladas
  - 📝 Markdown: Resumen legible con evidencias y análisis de sentimiento por oración.
  - 📊 HTML: Tabla compacta con ganadores, colores y nivel de confianza.
  - 🧩 JSON: Datos estructurados para integraciones con otros sistemas.
  - 📥 CSV: Archivo descargable con scores y confianza por categoría.
- 🎨 Sistema de colores
  - 🟢 Mejor: verde
  - 🟠 Intermedio (cuando hay más de 2 productos)
  - 🔴 Peor: rojo
  - ⚪ Empate real: gris + texto explícito
## 📄 Licencia

Este proyecto se distribuye bajo una **licencia propietaria con acceso al código (source-available)**.

El código fuente se pone a disposición únicamente para fines de **visualización, evaluación y aprendizaje**.

❌ No está permitido copiar, modificar, redistribuir, sublicenciar, ni crear obras derivadas del software o de su código fuente sin autorización escrita expresa del titular de los derechos.

❌ El uso comercial del software, incluyendo su oferta como servicio (SaaS), su integración en productos comerciales o su uso en entornos de producción, requiere un **acuerdo de licencia comercial independiente**.

📌 El texto **legalmente vinculante** de la licencia es la versión en inglés incluida en el archivo `LICENSE`. 

Se proporciona una traducción al español en `LICENSE_ES.md` únicamente con fines informativos. En caso de discrepancia, prevalece la versión en inglés.

## Autor
Kevin-2099
