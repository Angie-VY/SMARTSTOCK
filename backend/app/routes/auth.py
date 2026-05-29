from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import User
from app.auth_utils import verify_password, get_password_hash, create_access_token

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
        hashed_pwd = get_password_hash(password if password else "admin123")
        user = User(username="admin", password=hashed_pwd, role="admin")
        db.add(user)
        db.commit()
        db.refresh(user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no registrado en el sistema."
        )

    # Verificación de contraseña usando el utilitario (soporta hash bcrypt o plano viejo)
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta."
        )

    # Generar Token JWT
    access_token = create_access_token(data={"sub": user.username, "role": user.role})

    return {
        "status": "success",
        "username": user.username,
        "role": user.role,
        "token": access_token,
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

    user.password = get_password_hash(new_password)
    db.commit()

    return {
        "status": "success",
        "message": f"Contraseña restablecida con éxito para el usuario '{username}'."
    }
