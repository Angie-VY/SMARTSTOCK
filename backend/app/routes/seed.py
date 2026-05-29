from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import datetime
import random
from app.database import get_db
from app.models import Product, Movement, Anomaly, Rule, User
from app.dependencies import require_role
from app.auth_utils import get_password_hash

router = APIRouter(prefix="/seed", tags=["seed"])

@router.post("/")
def seed_database(db: Session = Depends(get_db), current_user: User = Depends(require_role(["admin"]))):
    # 1. Limpiar base de datos
    db.query(Anomaly).delete()
    db.query(Movement).delete()
    db.query(Rule).delete()
    db.query(Product).delete()
    db.query(User).delete()
    db.commit()

    # 2. Agregar usuarios con diferentes roles
    users_data = [
        {"username": "admin", "password": "admin123", "role": "admin"},
        {"username": "supervisor", "password": "supervisor123", "role": "supervisor"},
        {"username": "gerente_almacen", "password": "pass123", "role": "supervisor"},
        {"username": "empleado1", "password": "emp123", "role": "employee"},
        {"username": "empleado2", "password": "emp123", "role": "employee"},
        {"username": "empleado3", "password": "emp123", "role": "employee"},
    ]
    
    created_users = []
    for u_data in users_data:
        u_data["password"] = get_password_hash(u_data["password"])
        user = User(**u_data)
        db.add(user)
        created_users.append(user)
    db.commit()

    # 3. Agregar productos base
    products_data = [
        # Categoría: Tecnología
        {"name": "Laptop HP Pavilion 15", "category": "Tecnología", "stock": 15, "price": 799.99, "min_stock": 12, "supplier": "HP Distribuidora"},
        {"name": "iPhone 15 Pro Max", "category": "Tecnología", "stock": 4, "price": 1199.99, "min_stock": 8, "supplier": "Apple Latam"},
        {"name": "Mouse Inalámbrico Logitech", "category": "Tecnología", "stock": 45, "price": 29.99, "min_stock": 15, "supplier": "Logitech Store"},
        # Categoría: Alimentos
        {"name": "Café Gourmet de Altura 1kg", "category": "Alimentos", "stock": 60, "price": 14.50, "min_stock": 20, "supplier": "Cafetales del Sur"},
        {"name": "Leche Entera Premium 1L", "category": "Alimentos", "stock": 120, "price": 1.80, "min_stock": 40, "supplier": "Lácteos de la Villa"},
        {"name": "Cereal Integral de Avena 500g", "category": "Alimentos", "stock": 3, "price": 4.20, "min_stock": 15, "supplier": "NutriSana SA"},
        # Categoría: Ropa
        {"name": "Camisa Formal Slim Fit", "category": "Ropa", "stock": 30, "price": 35.00, "min_stock": 10, "supplier": "Textiles del Norte"},
        {"name": "Zapatos Deportivos UltraLight", "category": "Ropa", "stock": 8, "price": 85.00, "min_stock": 12, "supplier": "Zapatos & Moda"}
    ]

    products = []
    for p_data in products_data:
        prod = Product(**p_data)
        db.add(prod)
        products.append(prod)
    
    db.commit()
    # Refrescar para obtener los IDs
    for prod in products:
        db.refresh(prod)

    # 4. Generar historial de 60 movimientos de inventario en los últimos 15 días
    # Esto creará tendencias hermosas para ApexCharts
    start_date = datetime.datetime.now() - datetime.timedelta(days=15)
    
    movements_to_add = []
    
    # Añadir algunas compras masivas iniciales hace 15 días para establecer stock
    for prod in products:
        mov = Movement(
            product_id=prod.id,
            type="IN",
            quantity=prod.stock + 20,
            price=prod.price,
            date=start_date,
            supplier=prod.supplier
        )
        movements_to_add.append(mov)

    # Generar ventas (OUT) e ingresos (IN) aleatorios consistentes en los días siguientes
    random.seed(42)  # Semilla fija para consistencia
    categories_weights = {"Tecnología": (1, 3), "Alimentos": (5, 15), "Ropa": (2, 6)}
    
    for day in range(1, 15):
        current_day_date = start_date + datetime.timedelta(days=day)
        
        # Simular ventas diarias
        for prod in products:
            # Determinamos cantidad de venta típica según categoría
            min_q, max_q = categories_weights[prod.category]
            
            # Incremento el viernes y sábado (Patrón semanal)
            weekday = current_day_date.weekday()
            if weekday in [4, 5]: # Viernes y Sábado
                min_q = int(min_q * 1.5)
                max_q = int(max_q * 1.8)

            qty = random.randint(min_q, max_q)
            
            # Crear venta (OUT)
            sale_mov = Movement(
                product_id=prod.id,
                type="OUT",
                quantity=qty,
                price=prod.price,
                date=current_day_date + datetime.timedelta(hours=random.randint(9, 18)), # Horario laboral
                reason="Venta de mostrador"
            )
            movements_to_add.append(sale_mov)
            
            # Ocasionalmente crear una reposición (IN)
            if random.random() > 0.65:
                refill_qty = random.randint(15, 30)
                refill_mov = Movement(
                    product_id=prod.id,
                    type="IN",
                    quantity=refill_qty,
                    price=prod.price,
                    date=current_day_date + datetime.timedelta(hours=random.randint(8, 12)),
                    supplier=prod.supplier
                )
                movements_to_add.append(refill_mov)

    db.add_all(movements_to_add)
    db.commit()

    # 5. Agregar reglas de negocio predeterminadas
    default_rules = [
        {"name": "Reorden de Inventario Bajo", "rule_type": "reorder", "is_active": True, "condition_value": 0.0},
        {"name": "Alerta de Anomalías Críticas", "rule_type": "anomaly_alert", "is_active": True, "condition_value": 500.0},
        {"name": "Optimización de Stock por IA", "rule_type": "auto_min_stock", "is_active": True, "condition_value": 2.5}
    ]

    for r_data in default_rules:
        rule = Rule(**r_data)
        db.add(rule)
    db.commit()

    # 6. Pre-registrar 2 anomalías realistas de ejemplo
    # Anomalía A: Venta nocturna a las 3:00 AM (Crítica)
    iphone = db.query(Product).filter(Product.name == "iPhone 15 Pro Max").first()
    anomaly_a = Anomaly(
        product_id=iphone.id if iphone else products[1].id,
        description=f"Transacción fuera de horario comercial detectada para {iphone.name if iphone else 'iPhone 15 Pro Max'} (OUT de 4 unidades a las 03:14 AM). Posible brecha de seguridad.",
        gravity="Alta",
        value=4799.96,
        date=datetime.datetime.now() - datetime.timedelta(days=2),
        resolved=False
    )
    db.add(anomaly_a)

    # Anomalía B: Compra excesiva de leche (Media, Resuelta)
    leche = db.query(Product).filter(Product.name == "Leche Entera Premium 1L").first()
    anomaly_b = Anomaly(
        product_id=leche.id if leche else products[4].id,
        description=f"Movimiento masivo inusual de {leche.name if leche else 'Leche Premium'}: IN de 180 unidades del proveedor 'Lácteos de la Villa'. Excede 3 veces la desviación estándar.",
        gravity="Media",
        value=324.00,
        date=datetime.datetime.now() - datetime.timedelta(days=4),
        resolved=True
    )
    db.add(anomaly_b)
    db.commit()

    return {
        "status": "success",
        "message": "¡Base de datos sembrada exitosamente! 🌱",
        "details": {
            "users": len(users_data),
            "products": len(products_data),
            "movements": len(movements_to_add),
            "rules": len(default_rules),
            "anomalies": 2
        }
    }
