from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Anomaly, Product
from app.services import ai_service

router = APIRouter(prefix="/ai", tags=["ai"])

@router.get("/patterns/{product_id}")
def get_product_patterns(product_id: int, db: Session = Depends(get_db)):
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
def get_realtime_anomalies(db: Session = Depends(get_db)):
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
def resolve_anomaly(anomaly_id: int, db: Session = Depends(get_db)):
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if not anomaly:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anomalía no encontrada."
        )
        
    anomaly.resolved = True
    db.commit()
    return {"status": "success", "message": "Anomalía marcada como resuelta."}
