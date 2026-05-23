from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

class RecoverRequest(BaseModel):
    username: str
    new_password: str

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    username = req.username.strip()
    password = req.password

    # Auto-creación de admin si la tabla está vacía o el usuario no existe y es 'admin'
    user = db.query(User).filter(User.username == username).first()
    if not user and username == "admin":
        user = User(username="admin", password=password if password else "admin123", role="admin")
        db.add(user)
        db.commit()
        db.refresh(user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no registrado en el sistema."
        )

    # Verificación de contraseña simple (para fines académicos y facilidad de prueba)
    if user.password != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta."
        )

    return {
        "status": "success",
        "username": user.username,
        "role": user.role,
        "message": "Autenticación exitosa 🚀"
    }

@router.post("/recover")
def recover_password(req: RecoverRequest, db: Session = Depends(get_db)):
    username = req.username.strip()
    new_password = req.new_password

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario ingresado no existe."
        )

    user.password = new_password
    db.commit()

    return {
        "status": "success",
        "message": f"Contraseña restablecida con éxito para el usuario '{username}'."
    }
