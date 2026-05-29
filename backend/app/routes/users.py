from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from app.database import get_db
from app.models import User
from app.auth_utils import get_password_hash
from app.dependencies import require_role

router = APIRouter(prefix="/users", tags=["users"])

class UserSchema(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=4, max_length=255)
    role: str = Field("employee", description="admin, supervisor, employee")

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Listar todos los usuarios del sistema"""
    return db.query(User).all()

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Obtener detalles de un usuario específico"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )
    return user

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    req: UserSchema, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Crear un nuevo usuario en el sistema"""
    existing_user = db.query(User).filter(User.username == req.username.strip()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya existe en el sistema."
        )
    
    if req.role not in ["admin", "supervisor", "employee"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rol no válido. Debe ser: admin, supervisor, employee"
        )

    new_user = User(
        username=req.username.strip(),
        password=get_password_hash(req.password),
        role=req.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, 
    req: UserSchema, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Actualizar datos de un usuario existente"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )
    
    if req.role not in ["admin", "supervisor", "employee"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rol no válido. Debe ser: admin, supervisor, employee"
        )
    
    existing_user = db.query(User).filter(
        User.username == req.username.strip(),
        User.id != user_id
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe otro usuario con ese nombre."
        )

    user.username = req.username.strip()
    if req.password and req.password != user.password:
        user.password = get_password_hash(req.password)
    user.role = req.role
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Eliminar un usuario del sistema"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )
    
    admin_count = db.query(User).filter(User.role == "admin").count()
    if user.role == "admin" and admin_count <= 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se puede eliminar el último administrador del sistema."
        )

    db.delete(user)
    db.commit()
    return {"status": "success", "message": f"Usuario '{user.username}' eliminado correctamente."}

@router.post("/change-password")
def change_password(
    user_id: int, 
    new_password: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Cambiar contraseña de un usuario"""
    if len(new_password) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 4 caracteres."
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )
    
    user.password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    
    return {
        "status": "success",
        "message": f"Contraseña de '{user.username}' actualizada correctamente.",
        "user": UserResponse.from_orm(user)
    }
