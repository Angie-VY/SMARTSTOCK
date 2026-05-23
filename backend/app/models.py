from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    password = Column(String(255))
    role = Column(String(50), default="admin")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    category = Column(String(100), index=True)
    stock = Column(Integer, default=0)
    price = Column(Float, default=0.0)
    min_stock = Column(Integer, default=10)  # Punto de reorden
    supplier = Column(String(255), default="Proveedor General")

    movements = relationship("Movement", back_populates="product", cascade="all, delete-orphan")
    anomalies = relationship("Anomaly", back_populates="product", cascade="all, delete-orphan")


class Movement(Base):
    __tablename__ = "movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    type = Column(String(10))  # 'IN' o 'OUT'
    quantity = Column(Integer)
    price = Column(Float)  # Precio unitario al momento del movimiento
    date = Column(DateTime, default=datetime.datetime.utcnow)
    supplier = Column(String(255), nullable=True)  # Para entradas (IN)
    reason = Column(String(255), nullable=True)  # Para salidas (OUT)

    product = relationship("Product", back_populates="movements")


class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    description = Column(String(500))
    gravity = Column(String(50))  # 'Alta', 'Media', 'Baja'
    value = Column(Float, default=0.0)  # Valor implicado
    date = Column(DateTime, default=datetime.datetime.utcnow)
    resolved = Column(Boolean, default=False)

    product = relationship("Product", back_populates="anomalies")


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    rule_type = Column(String(100))  # 'reorder', 'anomaly_alert', 'auto_min_stock'
    is_active = Column(Boolean, default=True)
    condition_value = Column(Float, default=0.0)  # Valor umbral o parámetro
    last_triggered = Column(DateTime, nullable=True)