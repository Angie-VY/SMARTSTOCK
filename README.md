# SmartStock - Sistema de Gestión de Inventario con Inteligencia Artificial

SmartStock es una aplicación web moderna diseñada para la gestión inteligente de inventarios. Va más allá de las operaciones tradicionales (entradas y salidas de stock) al integrar Inteligencia Artificial para predecir la demanda y detectar anomalías en tiempo real.

## ¿Qué hace el proyecto?

1. **Gestión de Inventario Tradicional**: Permite administrar productos (crear, editar, eliminar), controlar el stock mínimo, registrar entradas (abastecimiento) y salidas (ventas o retiros), y ver el historial completo de movimientos.
2. **Sistema de Usuarios y Roles (RBAC)**: Cuenta con un sistema de seguridad avanzado mediante autenticación por tokens (JWT) y contraseñas encriptadas (Bcrypt). Los roles definidos son:
   - **Admin**: Control total, incluyendo la gestión de cuentas de usuario.
   - **Supervisor**: Gestión de productos y acceso a los módulos de Inteligencia Artificial.
   - **Empleado**: Acceso limitado únicamente a visualizar productos y registrar movimientos (entradas y salidas).
3. **Módulos de Inteligencia Artificial (Gemini AI)**:
   - **Detección de Patrones y Proyección**: Analiza el historial de movimientos de un producto y utiliza Google Gemini 1.5-Flash para predecir la demanda futura a 7 días.
   - **Detección de Anomalías**: Escanea la base de datos en busca de transacciones inusuales (ej. ventas masivas o en horarios extraños) y alerta a los supervisores.
   - **Motor de Reglas**: Permite configurar alertas automáticas basadas en IA o condiciones de stock (por ejemplo, reabastecer cuando el stock baje del límite).

## ¿Cómo está hecho? (Tecnologías utilizadas)

El proyecto utiliza una arquitectura monolítica moderna donde el backend y el frontend conviven en el mismo servidor para facilitar su despliegue y desarrollo:

### Backend
- **Python con FastAPI**: Framework web ultrarrápido y asíncrono para construir la API REST.
- **SQLAlchemy & SQLite**: Sistema de base de datos relacional (ORM) para almacenar productos, movimientos, usuarios y reglas sin necesidad de un servidor de base de datos complejo.
- **PyJWT & Passlib**: Para la seguridad, generación de tokens (JSON Web Tokens) y el hash seguro de las contraseñas (`bcrypt`).
- **Google Generative AI SDK**: Integración directa con la API de Google Gemini para realizar los análisis predictivos y lógicos basándose en los datos de la base de datos.

### Frontend
- **Alpine.js**: Un framework de JavaScript muy ligero (similar a Vue o React pero mucho más sencillo) que maneja toda la lógica de la interfaz (SPA - Single Page Application) directamente en el HTML.
- **Tailwind CSS**: Framework de estilos para crear un diseño moderno, oscuro y con efectos avanzados (glassmorphism, gradientes, animaciones) sin escribir CSS tradicional.
- **ApexCharts**: Librería de gráficos interactivos utilizada para mostrar las proyecciones de demanda de la IA.
- **Lucide Icons**: Conjunto de íconos vectoriales modernos.

---

## ¿Cómo se corre el proyecto?

Sigue estos pasos para iniciar la aplicación en tu computadora local:

### 1. Preparar el entorno
Abre una terminal (Símbolo del sistema o PowerShell) y navega hasta la carpeta `backend` de tu proyecto:
```bash
cd "C:\Users\migue\Documents\Universidad\Universidad 1er Semestre 2026\IA\SMARTSTOCK\backend"
```

Si aún no has instalado las dependencias (o es tu primera vez), ejecuta:
```bash
python -m pip install -r requirements.txt
```

### 2. Iniciar el Servidor
Para arrancar el sistema, ejecuta el script principal:
```bash
python run.py
```
El script intentará iniciar en el puerto `8000` y, si ese puerto está ocupado, usará automáticamente `8001`.

*Verás un mensaje en la terminal indicando la URL activa del servidor.*

### 3. Acceder a la Aplicación
Abre tu navegador web favorito (Chrome, Edge, Firefox) e ingresa a la siguiente dirección:
**[http://localhost:8000](http://localhost:8000)**

### 4. Primer Inicio de Sesión
- Si es la primera vez que levantas el sistema y la base de datos está vacía, simplemente ingresa el usuario `admin` y la contraseña que desees (ej. `admin123`) en la pantalla de Login.
- El sistema creará esa cuenta como Administrador automáticamente.
- Una vez dentro, ve a la pestaña de **Gestión Usuarios** en la parte inferior del menú izquierdo para crear las cuentas de tus supervisores y empleados.

> **Tip:** También puedes ir a "Configuración" (o usar el endpoint oculto) para *Sembrar Base de Datos* y rellenarla con datos de prueba si necesitas hacer una presentación.
>
> **Solución rápida si el puerto 8000 está ocupado:** cierra otros procesos Python/uvicorn que estén usando el puerto o reinicia la máquina. El script `run.py` ahora ofrece un puerto alternativo automáticamente.
