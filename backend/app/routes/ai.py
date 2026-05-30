from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Anomaly, Product, User
from app.services import ai_service
from app.dependencies import require_role
import os
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])

@router.get("/health")
def ai_health_check(current_user: User = Depends(require_role(["admin", "supervisor"]))):
    """
    Verifica el estado de Gemini API y retorna información sobre disponibilidad.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    health_status = {
        "api_key_configured": bool(gemini_key),
        "gemini_available": False,
        "error": None,
        "message": "ℹ️ API de Gemini disponible" if gemini_key else "⚠️ API de Gemini no configurada"
    }
    
    if not gemini_key:
        health_status["message"] = "⚠️ GEMINI_API_KEY no está configurada. El sistema usará simulaciones."
        return health_status
    
    try:
        # Intentar contactar Gemini con un prompt mínimo
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Di solo '✅ OK'")
        
        if response and response.text:
            health_status["gemini_available"] = True
            health_status["message"] = "✅ Gemini API funcionando correctamente"
            logger.info("✅ Gemini API Health Check: OK")
        else:
            health_status["error"] = "Sin respuesta de Gemini"
            health_status["message"] = "⚠️ Gemini respondió pero sin contenido"
            logger.warning("⚠️ Gemini respondió vacío")
            
    except Exception as e:
        error_str = str(e)
        health_status["error"] = error_str
        health_status["message"] = f"❌ Error: {error_str}"
        logger.error(f"❌ Gemini API Health Check falló: {error_str}")
        
        # Detectar tipo de error
        if "401" in error_str or "authentication" in error_str.lower():
            health_status["message"] = "❌ Error de autenticación: API Key inválida o expirada"
        elif "quota" in error_str.lower():
            health_status["message"] = "❌ Cuota de API excedida"
        elif "429" in error_str:
            health_status["message"] = "❌ Rate limit excedido"
        elif "timeout" in error_str.lower():
            health_status["message"] = "❌ Timeout: Sin conexión o Gemini no responde"
    
    return health_status

@router.get("/patterns/{product_id}")
def get_product_patterns(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role(["admin", "supervisor"]))):
    # Validar que exista el producto
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado."
        )

    # Analizar patrones en tiempo real (simulación / real-time AI)
    analysis = ai_service.analyze_patterns(product_id, db)
    return analysis

@router.get("/anomalies")
def get_realtime_anomalies(db: Session = Depends(get_db), current_user: User = Depends(require_role(["admin", "supervisor"]))):
    # Ejecuta el análisis en tiempo real para encontrar/guardar nuevas anomalías
    anomalies = ai_service.detect_anomalies(db)
    
    # Formatear respuesta con nombres de producto para mejor visualización
    formatted_anomalies = []
    for a in anomalies:
        prod_name = "General"
        if a.product_id:
            prod = db.query(Product).filter(Product.id == a.product_id).first()
            if prod:
                prod_name = prod.name
                
        formatted_anomalies.append({
            "id": a.id,
            "product_id": a.product_id,
            "product_name": prod_name,
            "description": a.description,
            "gravity": a.gravity,
            "value": a.value,
            "date": a.date.isoformat(),
            "resolved": a.resolved
        })
        
    return formatted_anomalies

@router.post("/anomalies/{anomaly_id}/resolve")
def resolve_anomaly(anomaly_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role(["admin", "supervisor"]))):
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if not anomaly:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anomalía no encontrada."
        )
        
    anomaly.resolved = True
    db.commit()
    return {"status": "success", "message": "Anomalía marcada como resuelta."}
