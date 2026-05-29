from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import engine
from app.models import Base
from app.routes import auth, products, movements, ai, rules, seed, users
import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===== VALIDAR CONFIGURACIÓN AL STARTUP =====
logger.info("=" * 60)
logger.info("🚀 SmartStock IA - Iniciando validación de configuración...")
logger.info("=" * 60)

# Validar DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("❌ CRÍTICO: DATABASE_URL no está configurada en .env")
    raise RuntimeError("DATABASE_URL no configurada")
else:
    logger.info(f"✅ DATABASE_URL: {DATABASE_URL[:50]}...")

# Validar GEMINI_API_KEY
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    logger.warning("⚠️ GEMINI_API_KEY no está configurada. Se usarán simulaciones.")
else:
    logger.info(f"✅ GEMINI_API_KEY configurada (primeros 10 chars: {GEMINI_KEY[:10]}...)")

logger.info("=" * 60)

# Crear todas las tablas en la BD si no existen
try:
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Tablas de BD creadas o verificadas correctamente")
except Exception as e:
    logger.error(f"❌ Error creando tablas en BD: {e}")
    raise

app = FastAPI(
    title="SmartStock IA",
    description="Sistema de Inventario Avanzado Automatizado con IA",
    version="1.0.0"
)

# Configurar middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir enrutadores de la API
app.include_router(auth.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(movements.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(rules.router, prefix="/api")
app.include_router(seed.router, prefix="/api")
app.include_router(users.router, prefix="/api")

# Asegurar la existencia del directorio estático
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
    logger.info(f"📁 Directorio de archivos estáticos creado: {static_dir}")

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Servir el Frontend SPA en el Root '/'
@app.get("/")
def read_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "status": "online",
        "message": "Servidor SmartStock IA funcionando 🚀. Cargando frontend...",
        "api_docs": "/docs"
    }

@app.on_event("startup")
def startup_event():
    logger.info("🟢 Servidor SmartStock IA iniciado correctamente")
    logger.info("📚 Documentación API disponible en: /docs")

@app.on_event("shutdown")
def shutdown_event():
    logger.info("🔴 Servidor SmartStock IA cerrado")