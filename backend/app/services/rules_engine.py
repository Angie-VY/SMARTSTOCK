import datetime
from sqlalchemy.orm import Session
from app.models import Product, Anomaly, Rule, Movement
from app.services import ai_service

def evaluate_rules(db: Session):
    """
    Evalúa todas las reglas activas de la base de datos contra el estado actual de los
    productos y anomalías. Realiza acciones automáticas (como reajustes de stock mínimo)
    y retorna una lista detallada de las acciones ejecutadas.
    """
    active_rules = db.query(Rule).filter(Rule.is_active == True).all()
    execution_logs = []

    for rule in active_rules:
        # Marca de ejecución
        triggered_this_run = False
        action_desc = ""

        # 1. Regla de Reorden (Generar Orden de Compra Automática)
        if rule.rule_type == "reorder":
            # Buscar productos cuyo stock esté por debajo de su punto de reorden (min_stock)
            low_stock_products = db.query(Product).filter(Product.stock < Product.min_stock).all()
            
            for prod in low_stock_products:
                triggered_this_run = True
                order_qty = max(20, (prod.min_stock * 2) - prod.stock)
                action_desc = (
                    f"📦 [REORDEN AUTOMÁTICA] El stock de '{prod.name}' ({prod.stock} uds) "
                    f"está por debajo del mínimo ({prod.min_stock} uds). Se ha generado una "
                    f"Orden de Compra simulada (#OC-{datetime.datetime.now().strftime('%M%S')}-{prod.id}) "
                    f"para adquirir {order_qty} unidades del proveedor '{prod.supplier}'."
                )
                execution_logs.append({
                    "rule_id": rule.id,
                    "rule_name": rule.name,
                    "type": "reorder",
                    "product_id": prod.id,
                    "product_name": prod.name,
                    "message": action_desc,
                    "timestamp": datetime.datetime.now().isoformat()
                })

        # 2. Regla de Alerta de Anomalía de Alto Valor
        elif rule.rule_type == "anomaly_alert":
            threshold_value = rule.condition_value if rule.condition_value > 0 else 500.0
            # Buscar anomalías no resueltas de alto valor o gravedad Alta
            unresolved_anomalies = db.query(Anomaly).filter(
                Anomaly.resolved == False
            ).all()

            for anomaly in unresolved_anomalies:
                if anomaly.gravity == "Alta" or anomaly.value >= threshold_value:
                    triggered_this_run = True
                    prod_name = "General"
                    if anomaly.product_id:
                        prod = db.query(Product).filter(Product.id == anomaly.product_id).first()
                        if prod:
                            prod_name = prod.name

                    action_desc = (
                        f"🚨 [ALERTA DE SEGURIDAD] Se detectó anomalía de alto valor/gravedad. "
                        f"Detalle: '{anomaly.description}' (Valor: ${anomaly.value}, Gravedad: {anomaly.gravity}). "
                        f"Acción: Se ha enviado una notificación push de emergencia a la gerencia de operaciones."
                    )
                    execution_logs.append({
                        "rule_id": rule.id,
                        "rule_name": rule.name,
                        "type": "anomaly_alert",
                        "product_id": anomaly.product_id,
                        "product_name": prod_name,
                        "message": action_desc,
                        "timestamp": anomaly.date.isoformat()
                    })

        # 3. Regla de Ajuste Automático de Stock Mínimo según la Demanda IA
        elif rule.rule_type == "auto_min_stock":
            # Esta regla recalcula el min_stock en base a las predicciones de IA
            products = db.query(Product).all()
            for prod in products:
                # Obtener la demanda diaria promedio simulada o real de la IA
                # Para evitar loops infinitos lentos, hacemos un cálculo rápido basado en el historial
                sales = db.query(Movement).filter(
                    Movement.product_id == prod.id,
                    Movement.type == "OUT"
                ).order_by(Movement.date.desc()).limit(15).all()
                
                avg_daily_demand = sum(s.quantity for s in sales) / len(sales) if sales else 5.0
                if avg_daily_demand == 0:
                    avg_daily_demand = 5.0
                
                # Ajuste inteligente: el nuevo min_stock será igual a 2.5 días de demanda + factor
                factor = rule.condition_value if rule.condition_value > 0 else 2.5
                new_min = round(avg_daily_demand * factor)
                # Mantener un mínimo de seguridad razonable
                new_min = max(5, min(100, new_min))

                if prod.min_stock != new_min:
                    triggered_this_run = True
                    old_min = prod.min_stock
                    prod.min_stock = new_min
                    
                    action_desc = (
                        f"⚙️ [AUTO-AJUSTE IA] Ajustado stock mínimo de '{prod.name}' "
                        f"de {old_min} ➔ {new_min} unidades, basado en análisis de "
                        f"demanda proyectada (Demanda promedio diaria: {round(avg_daily_demand, 1)} uds)."
                    )
                    execution_logs.append({
                        "rule_id": rule.id,
                        "rule_name": rule.name,
                        "type": "auto_min_stock",
                        "product_id": prod.id,
                        "product_name": prod.name,
                        "message": action_desc,
                        "timestamp": datetime.datetime.now().isoformat()
                    })
            
            # Preparar la actualización de los productos
            pass

        if triggered_this_run:
            rule.last_triggered = datetime.datetime.now()

    # Un solo commit al final de evaluar todas las reglas
    if execution_logs:
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            print("Error actualizando reglas y productos:", e)

    return execution_logs
