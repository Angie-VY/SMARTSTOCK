# 🚀 GUÍA RÁPIDA DE PUESTA EN MARCHA - SmartStock IA

## ⚡ Requisitos Previos
- Python 3.8+
- pip (gestor de paquetes de Python)

---

## 📋 PASOS PARA EJECUTAR EL PROYECTO

### 1️⃣ **Crear archivo `.env`** (CRÍTICO)

Copia el contenido de `backend/.env.example` a `backend/.env`:

```bash
cd backend
cp .env.example .env
```

**O crea manualmente** `backend/.env` con:
```env
DATABASE_URL=sqlite:///./smartstock.db
```

---

### 2️⃣ **Instalar dependencias** (CRÍTICO)

```bash
cd backend
pip install -r requirements.txt
```

**Dependencias que se instalan:**
- FastAPI - Framework web moderno
- Uvicorn - Servidor ASGI
- SQLAlchemy - ORM para base de datos
- python-dotenv - Carga variables de entorno
- google-generativeai - API de Google Gemini (opcional)

---

### 3️⃣ **Iniciar el servidor**

**Opción A: Desde `backend/`**
```bash
cd backend
python -m uvicorn app.main:app --reload
```

**Opción B: Desde la raíz del proyecto**
```bash
python run.py
```

**Salida esperada:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

---

### 4️⃣ **Acceder a la aplicación**

- **Frontend SPA**: http://127.0.0.1:8000/
- **Swagger UI (API Docs)**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

---

### 5️⃣ **Login inicial**

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `admin123`

> ℹ️ Si la tabla de usuarios está vacía, el sistema crea automáticamente el usuario admin.

---

### 6️⃣ **Llenar base de datos con datos de prueba** (Opcional)

1. Una vez loguedo en http://127.0.0.1:8000/
2. Haz clic en el botón **"Sembrar Base de Datos"**
3. Se crearán automáticamente:
   - 8 productos de demostración
   - 70 movimientos de inventario
   - 3 reglas de negocio
   - 2 anomalías de ejemplo

---

## 🔧 ESTRUCTURA DE CARPETAS

```
SmartStock-IA/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 ← Punto de entrada FastAPI
│   │   ├── database.py             ← Configuración BD
│   │   ├── models.py               ← Modelos SQLAlchemy
│   │   ├── routes/                 ← Endpoints API
│   │   │   ├── auth.py             (Login/Recover)
│   │   │   ├── products.py         (CRUD Productos)
│   │   │   ├── movements.py        (Registro de Stock)
│   │   │   ├── ai.py               (Análisis IA)
│   │   │   ├── rules.py            (Motor de Reglas)
│   │   │   └── seed.py             (Siembra de BD)
│   │   ├── services/               ← Lógica de negocio
│   │   │   ├── ai_service.py       (Análisis patrones, detección anomalías)
│   │   │   └── rules_engine.py     (Evaluación de reglas)
│   │   └── static/                 ← Frontend
│   │       ├── index.html          (SPA HTML)
│   │       ├── app.js              (Lógica Alpine.js)
│   │       └── style.css           (Estilos)
│   ├── .env                        (⚠️ CREAR: Variables de entorno)
│   ├── .env.example                (Plantilla .env)
│   ├── requirements.txt            (Dependencias Python)
│   └── venv/                       (Entorno virtual - se crea al instalar)
│
├── run.py                          (Script para ejecutar)
└── REPORTE_ANALISIS_COMPLETO.md   (Análisis detallado)
```

---

## 🐛 TROUBLESHOOTING

### ❌ Error: "ModuleNotFoundError: No module named 'fastapi'"

**Solución:**
```bash
pip install -r requirements.txt
```

---

### ❌ Error: "DATABASE_URL not found"

**Solución:**
1. Verifica que exista `backend/.env`
2. Verifica que contenga: `DATABASE_URL=sqlite:///./smartstock.db`

---

### ❌ Error: "Address already in use"

**Solución:**
```bash
# Cambiar puerto
python -m uvicorn app.main:app --port 8001
```

---

### ❌ El servidor inicia pero no se ve el frontend

**Solución:**
1. Verifica que exista `backend/app/static/index.html`
2. Recarga la página (Ctrl+F5)

---

## 📝 VARIABLES DE ENTORNO (.env)

| Variable | Requerida | Ejemplo | Descripción |
|----------|-----------|---------|-------------|
| `DATABASE_URL` | ✅ SÍ | `sqlite:///./smartstock.db` | Conexión a BD |
| `GEMINI_API_KEY` | ❌ NO | `AIzaSy...` | API Key de Gemini (opcional) |

---

## 🔐 Seguridad

⚠️ **Para producción**, se recomienda:

1. **Habilitar HTTPS** (usar certificados SSL)
2. **Usar autenticación JWT** (en lugar de plain text)
3. **Hash de contraseñas** con bcrypt
4. **CORS restringido** a dominios específicos
5. **Rate limiting** para APIs
6. **Usar base de datos robusta** (PostgreSQL en lugar de SQLite)

---

## 📚 DOCUMENTACIÓN ADICIONAL

- Reporte completo: `REPORTE_ANALISIS_COMPLETO.md`
- FastAPI docs: https://fastapi.tiangolo.com/
- SQLAlchemy docs: https://docs.sqlalchemy.org/
- Gemini API: https://ai.google.dev/

---

## 🆘 ¿Problemas?

Si encuentras problemas, verifica:

1. ✅ Python 3.8+ instalado: `python --version`
2. ✅ `.env` existe con `DATABASE_URL`
3. ✅ Dependencias instaladas: `pip list | grep fastapi`
4. ✅ Carpeta `backend/app/static/` existe

---

**¡Listo! El sistema está configurado y funcionando.** 🚀
