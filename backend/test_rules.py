from app.database import SessionLocal
from app.services.rules_engine import evaluate_rules

db = SessionLocal()
try:
    logs = evaluate_rules(db)
    print("SUCCESS", logs)
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
