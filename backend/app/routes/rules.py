from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
import datetime
from app.database import get_db
from app.models import Rule
from app.services import rules_engine

router = APIRouter(prefix="/rules", tags=["rules"])

class RuleSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    rule_type: str = Field(..., description="reorder, anomaly_alert, auto_min_stock")
    is_active: bool = Field(True)
    condition_value: float = Field(0.0)

class RuleResponse(RuleSchema):
    id: int
    last_triggered: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

@router.get("/", response_model=List[RuleResponse])
def get_rules(db: Session = Depends(get_db)):
    return db.query(Rule).all()

@router.post("/", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule(req: RuleSchema, db: Session = Depends(get_db)):
    # Validar tipo de regla
    if req.rule_type not in ["reorder", "anomaly_alert", "auto_min_stock"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de regla no soportado. Debe ser: reorder, anomaly_alert o auto_min_stock."
        )

    rule = Rule(
        name=req.name.strip(),
        rule_type=req.rule_type,
        is_active=req.is_active,
        condition_value=req.condition_value
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

@router.put("/{rule_id}", response_model=RuleResponse)
def update_rule(rule_id: int, req: RuleSchema, db: Session = Depends(get_db)):
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regla no encontrada."
        )

    if req.rule_type not in ["reorder", "anomaly_alert", "auto_min_stock"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de regla no soportado."
        )

    rule.name = req.name.strip()
    rule.rule_type = req.rule_type
    rule.is_active = req.is_active
    rule.condition_value = req.condition_value

    db.commit()
    db.refresh(rule)
    return rule

@router.delete("/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regla no encontrada."
        )

    db.delete(rule)
    db.commit()
    return {"status": "success", "message": f"Regla '{rule.name}' eliminada correctamente."}

@router.post("/evaluate")
def force_evaluate_rules(db: Session = Depends(get_db)):
    # Ejecuta manualmente el motor de reglas y retorna el log
    logs = rules_engine.evaluate_rules(db)
    return {
        "status": "success",
        "message": f"Motor de reglas ejecutado. Se dispararon {len(logs)} acciones.",
        "actions_triggered": logs
    }
