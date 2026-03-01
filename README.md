# 💈 BarberPOS - Sistema de Gestión Ligero

Una solución completa de Punto de Venta (POS) y gestión de negocios diseñada específicamente para barberías locales. Construido para facilitar la transición de pequeños negocios del lápiz y papel a un flujo de trabajo totalmente digital, este sistema maneja ventas, inventario, gastos y cálculos de nómina automatizados.

Actualmente implementado y gestionando las operaciones diarias para un cliente real en Banderilla, Veracruz, procesando ventas en tiempo real y generando reportes mensuales precisos.

## 🚀 Características Principales

* **Punto de Venta (POS):** Proceso de cobro rápido y optimizado para barberías. Separa "Servicios" (cortes, arreglos de barba) de "Productos" (ceras, aceites).
* **Gestión de Inventario:** Rastreo de stock en tiempo real. Previene la venta de artículos agotados y proporciona alertas visuales para bajo inventario.
* **Nómina y Comisiones Automatizadas:** Calcula dinámicamente las comisiones individuales de cada barbero basándose en los servicios diarios realizados, eliminando las matemáticas manuales de fin de mes.
* **Dashboard Financiero:** Genera reportes mensuales que muestran los ingresos brutos, gastos fijos (renta, luz, insumos), costos de nómina y la ganancia neta, acompañados de gráficas interactivas.
* **Ejecutable Independiente:** Empaquetado como un archivo `.exe` utilizando PyInstaller para un despliegue sin fricciones en computadoras Windows de usuarios finales, sin necesidad de instalar entornos de Python.
* **Protocolo de Apagado Seguro:** "Kill Switch" integrado para terminar de forma segura el servidor Flask en segundo plano y prevenir conflictos de puertos en la máquina local.

## 💻 Stack Tecnológico

* **Backend:** Python, Flask
* **Base de Datos:** SQLite (Ligera, sin servidor, perfecta para despliegues locales de escritorio)
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
* **Despliegue/Empaquetado:** PyInstaller, Waitress (Para WSGI en producción)


## ⚙️ Instalación y Configuración Local (Para Desarrolladores)

Si deseas ejecutar este proyecto de manera local o contribuir al código:

1. **Clona el repositorio:**
   ```bash
   git clone [https://github.com/TuUsuario/BarberPOS.git](https://github.com/TuUsuario/BarberPOS.git)
   cd BarberPOS