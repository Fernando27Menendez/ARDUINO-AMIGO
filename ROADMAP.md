# 🚀 Hoja de Ruta (Roadmap): Proyecto Arduino Amigo

Este documento detalla la evolución del proyecto, desde su estado actual hasta las metas futuras planificadas para convertirlo en una herramienta de aprendizaje y prototipado líder.

---

## 🟢 Fase 1: Cimientos y Core (Completado)
*   **Pipeline de Compilación**: Implementación de Lexer, Parser, generador de Código Intermedio (TAC) y Generador de C++.
*   **Análisis Semántico**: Verificación de declaración de variables antes de su uso.
*   **Soporte de Hardware Básico**: Funciones para Digital I/O, Analog Input, PWM, Delay y Servomotores.
*   **IDE Web Premium**: Interfaz oscura, editor Ace integrado, panel de terminal con múltiples pestañas y visor de lógica interna.
*   **Sistema de Exportación**: Descarga de proyectos en formato nativo `.aa` y compatible `.ino`.

---

## 🟡 Fase 2: Potencia del Lenguaje (Corto Plazo)
*   **Estructuras de Control Iterativas**:
    *   Implementación de bucles `mientras (condicion): ... fin`.
    *   Implementación de ciclos `repetir (n): ... fin`.
*   **Tipos de Datos Avanzados**:
    *   Soporte para cadenas de texto (`texto`).
    *   Soporte para arreglos/listas de números.
*   **Funciones de Usuario**:
    *   Permitir definir bloques de código reutilizables: `funcion mi_accion(parametro): ... fin`.
*   **Gestión de Ámbito (Scope)**: Distinción clara entre variables globales y locales dentro de funciones.

---

## 🟠 Fase 3: Experiencia de Usuario Pro (Medio Plazo)
*   **Resaltado de Sintaxis Nativo**: Crear un modo de Ace Editor específico para el lenguaje `.aa` para colorear palabras clave propias.
*   **Autocompletado Inteligente**: Sugerencias de variables declaradas y comandos en tiempo real.
*   **Depurador Visual**: Resaltado de la línea exacta en el editor de entrada cuando ocurre un error en el terminal.
*   **Multibillingüe**: Soporte para cambio de idioma en la interfaz.

---

## 🔴 Fase 4: Ecosistema y Hardware (Largo Plazo)
*   **Simulación Integrada**: Integración con motores tipo Wokwi para visualizar el circuito virtualmente antes de programar.
*   **Carga Directa (WebUSB)**: Permitir subir el código directamente a la placa Arduino desde el navegador sin necesidad del IDE oficial.
*   **Gestor de Librerías**: Un sistema para incluir sensores complejos (I2C, LCD, Motores paso a paso) seleccionándolos desde una interfaz visual.
*   **Colaboración**: Guardado de proyectos en la nube y compartición mediante enlaces únicos.

---

## 🔵 Próximos Pasos Inmediatos
1. Implementar el bucle `mientras` en el Parser.
2. Añadir soporte para el operador `!` (NOT) en condiciones.
3. Crear el archivo de configuración para estilos de resaltado de sintaxis nativo.

---
*Ultima actualización: 5 de enero de 2026*
