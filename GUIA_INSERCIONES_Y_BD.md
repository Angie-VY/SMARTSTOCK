# 📝 REVISIÓN: Inserciones de Datos y Base de Datos

**Fecha:** 28 de Mayo de 2026

---

## ❓ Pregunta del Usuario

> "Podría revisar el proyecto porque al momento de insertar algunos datos da un error en la solicitud?"
> "¿Está usando los datos de la Base de Datos real o son datos quemados?"

---

## ✅ RESPUESTA COMPLETA

### 1. ¿Está usando datos reales o quemados?

**La BD está usando datos REALES:**
- ✅ Base de Datos: **SQLite local** (`backend/smartstock.db`)
- ✅ Tipo: Datos REALES en BD, NO hardcoded en código
- ✅ Tabla: `products` - Datos guardados persistentemente
- ✅ Tabla: `movements` - Historial de inserciones/salidas

**¿Dónde están los datos "quemados"?**
- Solo en `seed.py` - Para INICIALIZAR la BD con datos de ejemplo
- NO en el código de negocio, solo para primera carga

**Flujo de datos:**
```
Usuario inserta movimiento → FastAPI → SQLAlchemy → SQLite BD → Persiste en archivo .db
```

---

### 2. Errores Potenciales en Inserciones

He revisado [backend/app/routes/movements.py](backend/app/routes/movements.py) y encontré los siguientes escenarios que podrían causar errores:

#### ❌ Escenario A: Stock Insuficiente (Error 400)

```python
# LÍNEA ~120 en movements.py
if product.stock < req.quantity:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Stock insuficiente. Stock actual de '{product.name}': {product.stock} unidades."
    )
```

**Síntoma:**
- Error: `400 Bad Request`
- Mensaje: `"Stock insuficiente. Stock actual de 'Producto X': 5 unidades."`

**Causa:** Intentar sacar (OUT) más unidades de las disponibles

**Solución:** 
- Verificar stock disponible ANTES de intentar salida
- Usar endpoint `GET /api/products/{id}` para ver stock

#### ❌ Escenario B: Producto No Encontrado (Error 404)

```python
# LÍNEA ~115 en movements.py
product = db.query(Product).filter(Product.id == req.product_id).first()
if not product:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Producto no encontrado."
    )
```

**Síntoma:**
- Error: `404 Not Found`
- Mensaje: `"Producto no encontrado."`

**Causa:** `product_id` no existe en BD

**Solución:**
- Usar `GET /api/products` para listar productos disponibles
- Verificar el ID del producto

#### ❌ Escenario C: Datos Inválidos en JSON (Error 422)

```python
# En la definición del schema (MovementInputSchema)
class MovementInputSchema(BaseModel):
    product_id: int                          # Debe ser número entero
    quantity: int = Field(..., gt=0)         # Debe ser > 0
    supplier: str = Field(..., min_length=1) # Debe ser string no vacío
    price: Optional[float] = Field(None, ge=0.0) # Si está, debe ser ≥ 0
```

**Síntoma:**
- Error: `422 Unprocessable Entity`
- Mensaje: `"validation error for MovementInputSchema..."`

**Causas comunes:**
- `quantity: 0` o negativo (debe ser `gt=0`)
- `product_id: "texto"` (debe ser número)
- `supplier: ""` (debe tener al menos 1 carácter)

**Ejemplo de solicitud MALA:**
```json
{
  "product_id": "1",        // ❌ String en lugar de número
  "quantity": 0,            // ❌ Cero no es válido (gt=0)
  "supplier": "",           // ❌ String vacío
  "price": -5              // ❌ Negativo no permitido
}
```

**Ejemplo de solicitud BUENA:**
```json
{
  "product_id": 1,          // ✅ Número entero
  "quantity": 5,            // ✅ Entero > 0
  "supplier": "Proveedor ABC",  // ✅ String no vacío
  "price": 25.50            // ✅ Número positivo
}
```

#### ❌ Escenario D: Error de Autorización (Error 401/403)

```python
# En las rutas de movements.py - Línea 48, 82, 115
def register_input(
    req: MovementInputSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ← Requiere autenticación
):
```

**Síntoma:**
- Error: `401 Unauthorized` o `403 Forbidden`
- Mensaje: `"Not authenticated"` o `"Not authorized"`

**Causa:** 
- No hay token JWT en header
- Token expirado
- Usuario sin permisos

**Solución:**
- Enviar header: `Authorization: Bearer <TOKEN>`
- Obtener token en `/api/auth/login`

---

### 3. Validación de Inserciones - Checklist

Use esta tabla para verificar cada inserción:

| Campo | Validación | Ejemplo Correcto |
|-------|-----------|-----------------|
| `product_id` | Entero, debe existir | `1`, `2`, `5` |
| `quantity` | Entero > 0 | `5`, `10`, `100` |
| `supplier` (IN) | String, min 1 char | `"Coca-Cola"`, `"Proveedor X"` |
| `price` | Float ≥ 0, opcional | `25.50`, `100.00` |
| `reason` (OUT) | String, min 1 char | `"Venta cliente"`, `"Descuento"` |
| `type` | Solo "IN" o "OUT" | (`auto` en endpoint) |
| `date` | ISO 8601 | (Auto: ahora mismo) |

---

### 4. Endpoints para Insertar Datos

#### 4a. Insertar ENTRADA (IN) - Compra/Reabastecimiento

```bash
POST /api/movements/in
Content-Type: application/json
Authorization: Bearer <TOKEN>

{
  "product_id": 1,
  "quantity": 50,
  "supplier": "Distribuidor Central ABC",
  "price": 12.99
}
```

**Respuesta exitosa (201):**
```json
{
  "status": "success",
  "message": "Ingreso registrado: +50 unidades de 'Laptop HP'.",
  "movement": {
    "id": 42,
    "product_name": "Laptop HP",
    "type": "IN",
    "quantity": 50,
    "stock_after": 150
  },
  "rule_triggers": []
}
```

#### 4b. Insertar SALIDA (OUT) - Venta/Descarte

```bash
POST /api/movements/out
Content-Type: application/json
Authorization: Bearer <TOKEN>

{
  "product_id": 1,
  "quantity": 5,
  "reason": "Venta cliente retail",
  "price": 12.99
}
```

**Respuesta exitosa (201):**
```json
{
  "status": "success",
  "message": "Salida registrada: -5 unidades de 'Laptop HP'.",
  "movement": {
    "id": 43,
    "product_name": "Laptop HP",
    "type": "OUT",
    "quantity": 5,
    "stock_after": 145
  },
  "rule_triggers": []
}
```

---

### 5. Solución de Errores - Árbol de Decisión

```
¿Error al insertar movimiento?
│
├─ ¿Error 401/403?
│  └─ Solución: Verificar token JWT en Authorization header
│
├─ ¿Error 404?
│  └─ Solución: El product_id no existe
│     ├─ GET /api/products (listar productos)
│     └─ Usar product_id válido
│
├─ ¿Error 422?
│  └─ Solución: Datos inválidos en JSON
│     ├─ Verificar tipos de datos (int, string, float)
│     ├─ Verificar restricciones (quantity > 0, supplier != "")
│     └─ Revisar mensaje de validación
│
├─ ¿Error 400 con "Stock insuficiente"?
│  └─ Solución: Intentar sacar más de lo disponible
│     ├─ GET /api/products/{id} (ver stock actual)
│     └─ Usar quantity ≤ stock disponible
│
└─ ¿Error 500?
   └─ Solución: Error del servidor
      ├─ Revisar consola de ejecución (python run.py)
      ├─ Verificar logs (nuevos logs implementados)
      └─ Contactar al desarrollador
```

---

### 6. Archivos Relevantes para Inserciones

| Archivo | Propósito | Líneas |
|---------|----------|--------|
| [backend/app/routes/movements.py](backend/app/routes/movements.py) | Lógica de inserciones IN/OUT | 1-145 |
| [backend/app/models.py](backend/app/models.py) | Definición de modelo Movement | Ver `Movement` class |
| [backend/app/routes/products.py](backend/app/routes/products.py#L50) | Crear/listar productos | 50-80 |
| [backend/app/database.py](backend/app/database.py) | Conexión BD SQLite | 1-25 |

---

### 7. Test de Inserciones - Paso a Paso

1. **Obtener lista de productos:**
   ```bash
   GET /api/products
   Authorization: Bearer <TOKEN>
   ```
   Nota el `id` del producto a usar

2. **Ver stock actual:**
   ```bash
   GET /api/products/{id}
   Authorization: Bearer <TOKEN>
   ```

3. **Insertar entrada (IN):**
   ```bash
   POST /api/movements/in
   Authorization: Bearer <TOKEN>
   Content-Type: application/json
   
   {
     "product_id": <el_id>,
     "quantity": 10,
     "supplier": "Proveedor Test",
     "price": 15.00
   }
   ```

4. **Insertar salida (OUT):**
   ```bash
   POST /api/movements/out
   Authorization: Bearer <TOKEN>
   Content-Type: application/json
   
   {
     "product_id": <el_id>,
     "quantity": 3,
     "reason": "Test de salida",
     "price": 15.00
   }
   ```

5. **Ver historial:**
   ```bash
   GET /api/movements
   Authorization: Bearer <TOKEN>
   ```

---

## 🎯 CONCLUSIÓN

| Pregunta | Respuesta |
|----------|-----------|
| ¿Usa BD real? | ✅ SÍ - SQLite local, persistente |
| ¿Tiene datos quemados? | ✅ SÍ en seed.py, pero no en inserciones reales |
| ¿Por qué errores en inserción? | Validación de datos (422), stock (400), auth (401) |
| ¿Cómo verificar? | Ver logs, revisar códigos de error HTTP, validar JSON |

**Recomendación:** 
1. Verificar tipo de error que recibe (401, 404, 422, 400)
2. Usar logs implementados para debugging
3. Validar datos JSON con los ejemplos anteriores

