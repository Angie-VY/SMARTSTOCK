from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from app.database import get_db
from app.models import Product, User
from app.dependencies import get_current_user, require_role

router = APIRouter(prefix="/products", tags=["products"])

class ProductSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    stock: int = Field(0, ge=0)
    price: float = Field(0.0, ge=0.0)
    min_stock: int = Field(10, ge=0)
    supplier: str = Field("Proveedor General", max_length=255)

class ProductResponse(ProductSchema):
    id: int

    class Config:
        from_attributes = True

@router.get("/", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Product).all()

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado."
        )
    return product

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(req: ProductSchema, db: Session = Depends(get_db), current_user: User = Depends(require_role(["admin", "supervisor"]))):
    # Validar duplicados por nombre
    existing = db.query(Product).filter(Product.name == req.name.strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un producto con este nombre."
        )

    product = Product(
        name=req.name.strip(),
        category=req.category.strip(),
        stock=req.stock,
        price=req.price,
        min_stock=req.min_stock,
        supplier=req.supplier.strip()
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, req: ProductSchema, db: Session = Depends(get_db), current_user: User = Depends(require_role(["admin", "supervisor"]))):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado."
        )

    # Validar duplicados de nombre en otros productos
    existing = db.query(Product).filter(Product.name == req.name.strip(), Product.id != product_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe otro producto con este nombre."
        )

    product.name = req.name.strip()
    product.category = req.category.strip()
    product.stock = req.stock
    product.price = req.price
    product.min_stock = req.min_stock
    product.supplier = req.supplier.strip()

    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role(["admin", "supervisor"]))):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado."
        )

    db.delete(product)
    db.commit()
    return {"status": "success", "message": f"Producto '{product.name}' eliminado correctamente."}
