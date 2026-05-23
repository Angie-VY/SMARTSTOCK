from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import engine
from app.models import Base
from app.routes import auth, products, movements, ai, rules, seed, users
import os

# Crear todas las tablas en Clever Cloud MySQL si no existen
Base.metadata.create_all(bind=engine)

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