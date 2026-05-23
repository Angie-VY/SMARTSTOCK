from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
import datetime
from app.database import get_db
from app.models import Product, Movement
from app.services import rules_engine

router = APIRouter(prefix="/movements", tags=["movements"])

class MovementInputSchema(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    supplier: str = Field(..., min_length=1)
    price: Optional[float] = Field(None, ge=0.0)

class MovementOutputSchema(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    reason: str = Field(..., min_length=1)
    price: Optional[float] = Field(None, ge=0.0)

@router.get("/")
def get_movements_history(db: Session = Depends(get_db)):
    # Retorna el historial ordenado por fecha descendente con detalles de producto
    results = db.query(Movement, Product.name, Product.category)\
        .join(Product, Movement.product_id == Product.id)\
        .order_by(Movement.date.desc()).all()
    
    history = []
    for mov, prod_name, prod_cat in results:
        history.append({
            "id": mov.id,
            "product_id": mov.product_id,
            "product_name": prod_name,
            "product_category": prod_cat,
            "type": mov.type,
            "quantity": mov.quantity,
            "price": mov.price,
            "date": mov.date.isoformat(),
            "supplier": mov.supplier,
            "reason": mov.reason,
            "total_value": round(mov.quantity * mov.price, 2)
        })
    return history

@router.post("/in")
def register_input(req: MovementInputSchema, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == req.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado."
        )

    # Si no se provee precio, tomamos el del producto
    price = req.price if req.price is not None else product.price

    # 1. Registrar movimiento
    movement = Movement(
        product_id=req.product_id,
        type="IN",
        quantity=req.quantity,
        price=price,
        date=datetime.datetime.now(),
        supplier=req.supplier.strip()
    )
    db.add(movement)

    # 2. Actualizar Stock
    product.stock += req.quantity

    # Guardar para poder correr el motor de reglas con el nuevo stock
    db.commit()
    db.refresh(product)
    db.refresh(movement)

    # 3. Evaluar Motor de Reglas en tiempo real
    rule_logs = rules_engine.evaluate_rules(db)

    return {
        "status": "success",
        "message": f"Ingreso registrado: +{req.quantity} unidades de '{product.name}'.",
        "movement": {
            "id": movement.id,
            "product_name": product.name,
            "type": "IN",
            "quantity": movement.quantity,
            "stock_after": product.stock
        },
        "rule_triggers": rule_logs
    }

@router.post("/out")
def register_output(req: MovementOutputSchema, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == req.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado."
        )

    # Validar stock suficiente
    if product.stock < req.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock insuficiente. Stock actual de '{product.name}': {product.stock} unidades."
        )

    # Si no se provee precio, tomamos el del producto
    price = req.price if req.price is not None else product.price

    # 1. Registrar movimiento
    movement = Movement(
        product_id=req.product_id,
        type="OUT",
        quantity=req.quantity,
        price=price,
        date=datetime.datetime.now(),
        reason=req.reason.strip()
    )
    db.add(movement)

    # 2. Actualizar Stock
    product.stock -= req.quantity

    db.commit()
    db.refresh(product)
    db.refresh(movement)

    # 3. Evaluar Motor de Reglas en tiempo real
    rule_logs = rules_engine.evaluate_rules(db)

    return {
        "status": "success",
        "message": f"Salida registrada: -{req.quantity} unidades de '{product.name}'.",
        "movement": {
            "id": movement.id,
            "product_name": product.name,
            "type": "OUT",
            "quantity": movement.quantity,
            "stock_after": product.stock
        },
        "rule_triggers": rule_logs
    }
