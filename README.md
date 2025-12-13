# 🧠 Comparador Inteligente de Productos
Comparador automático de descripciones de productos basado en categorías clave como pantalla, cámara, batería, rendimiento, almacenamiento y conectividad.

Funciona en español (ES) e inglés (EN).

Este proyecto utiliza Gradio para ofrecer una interfaz intuitiva que permite comparar dos o tres productos a partir de sus textos descriptivos y generar:
- 🏆 Ganador general

- 📊 Ganadores por categoría

- 🔍 Evidencias textuales

- 🧩 Salida en JSON estructurado

- 📝 Resumen en Markdown

- 🧱 Tabla HTML

# ✨ Características Principales
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

  Cada categoría se evalúa numéricamente según los valores detectados:
  
  - Pantalla: pulgadas + resolución
  
  - Batería: mAh / potencia
  
  - Rendimiento: CPU, RAM, velocidades
  
  - Cámara: MP / sensores
  
  - Almacenamiento: GB
  
  - Conectividad: 4G, 5G, WiFi, Bluetooth

- 🏆 Resultado general

  El comparador determina:
  
  - Ganador por categoría
  
  - Conteo de victorias
  
  - Ganador final entre A y B( o C opcional)

- 📤 Salidas detalladas
  
  📝 Markdown
  
  Resumen legible con evidencias de cada categoría.
  
  📊 HTML
  
  Tabla compacta de ganadores categoría por categoría.
  
  🧩 JSON
  
  Útil para integraciones con otros sistemas.

# 🎨 Sistema de colores
🟢 Mejor: verde

🔴 Peor: rojo

🟠 Intermedio (cuando hay 3 productos)

⚪ Empate: gris + texto explícito
# 📄 Licencia
MIT License
# Autor
Kevin
