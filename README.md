# Proyecto de Pruebas Automatizadas: Urban Routes
 
## Descripción del Proyecto
Este proyecto contiene una suite de pruebas automatizadas de extremo a extremo (E2E) para la aplicación **Urban Routes**. La suite valida el flujo completo de reservación de viajes, selección de tarifas (como la tarifa Comfort), configuración de opciones adicionales (manta, pañuelos, helados), ingreso de número telefónico y asignación de métodos de pago.
 
## Tecnologías y Técnicas Utilizadas
- **Lenguaje:** Python 3
- **Framework de Pruebas:** Pytest
- **Herramienta de Automatización Web:** Selenium WebDriver
- **Patrón de Diseño:** Page Object Model (POM) para la separación de la lógica de la página y las pruebas.
- **Estrategias de Localización:** Uso de XPaths avanzados, IDs y clases CSS.
- **Manejo de Asincronía:** Esperas explícitas (`WebDriverWait`) para interactuar con elementos dinámicos del DOM.
 
## Instrucciones para Ejecutar las Pruebas
 
1. **Clonar el repositorio o situarse en la carpeta del proyecto:**
   ```bash
   cd qa-project-Urban-Routes-es
