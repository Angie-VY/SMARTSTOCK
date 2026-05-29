# 🔍 DIAGNÓSTICO COMPLETO DE PROBLEMAS - SmartStock IA

**Fecha:** 28 de Mayo de 2026  
**Revisión:** Análisis Completo de Errores

---

## 📌 RESUMEN EJECUTIVO

Se identificaron **4 problemas críticos** que causan comportamientos inesperados:
1. ❌ Botón "Poblar con IA" siempre retorna la misma cantidad
2. ❌ Peticiones de IA fallan silenciosamente sin reporte
3. ❌ Datos quemados (hardcoded) en el seed
4. ❌ Sin logging adecuado para debugging

---

## 🔴 PROBLEMA #1: Botón Poblar con IA - Siempre Retorna la Misma Cantidad

### 📍 Ubicación
[backend/app/services/ai_service.py](backend/app/services/ai_service.py#L43)

### 🐛 Root Cause
```python
# LÍNEA 43 - PROBLEMA
if len(base_sales) < 5:
    random.seed(product_id)  # ← AQUÍ está el problema
    base_sales = [random.randint(2, 12) for _ in range(14)]
```

**¿Por qué ocurre?**
- Cuando un producto no tiene suficientes ventas históricas (< 5), se generan datos simulados
- `random.seed(product_id)` **fija la semilla aleatoria** a un número determinístico (el ID del producto)
- Esto significa que **para el mismo producto, SIEMPRE genera los mismos 14 números**
- Por ejemplo, si es producto_id=2, SIEMPRE genera: `[7, 4, 11, 8, 9, 2, 12, 5, 10, 3, 6, 8, 11, 7]`

### 📊 Impacto
- El usuario ve siempre las mismas predicciones para el mismo producto
- Las predicciones de 7 días también son determinísticas
- No hay variabilidad realista en las proyecciones

### ✅ SOLUCIÓN
**Remover `random.seed()` para predicciones dinámicas:**
```python
# CORRECCIÓN
if len(base_sales) < 5:
    # Solo usar seed para datos históricos simulados (para reproducibilidad)
    random.seed(42)  # Semilla global, no basada en product_id
    base_sales = [random.randint(2, 12) for _ in range(14)]
    random.seed()  # Resetear seed para predicciones futuras
```

---

## 🔴 PROBLEMA #2: Peticiones de Gemini Fallan Silenciosamente

### 📍 Ubicación
[backend/app/services/ai_service.py](backend/app/services/ai_service.py#L13-24)

### 🐛 Root Cause
```python
def call_gemini_or_mock(prompt: str, fallback_response: str) -> str:
    if GEMINI_KEY:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print("Error llamando a la API de Gemini (usando fallback simulado):", e)
            # ← El error solo se imprime en consola, NO se reporta al usuario
    
    return fallback_response  # ← Siempre retorna fallback sin indicar error
```

### 🔍 Diagnóstico
El archivo `.env` contiene: `GEMINI_API_KEY=AIzaSyCLg9_WFcuGC4gRxPyQqWX_QdMej19rYuk`

**Estados Posibles:**
1. ✅ API Key válida → Gemini funciona correctamente
2. ❌ API Key expirada/inválida → Fallback sin notificación
3. ❌ Rate limit excedido → Fallback silencioso
4. ❌ Sin conexión de red → Fallback sin reporte
5. ❌ Modelo no disponible → Fallback silencioso

### 📊 Impacto
- El usuario **no sabe si Gemini funcionó o si está en fallback**
- No hay forma de debugging desde el frontend
- Los errores solo aparecen en logs del servidor
- Frontend muestra texto genérico sin contexto

### ✅ SOLUCIÓN
**Mejorar respuesta para indicar estado de Gemini:**
```python
def call_gemini_or_mock(prompt: str, fallback_response: str) -> dict:
    response_obj = {
        "text": fallback_response,
        "source": "mock",  # ← Indicar si es real o simulado
        "error": None
    }
    
    if GEMINI_KEY:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            response_obj["text"] = response.text
            response_obj["source"] = "gemini"
            response_obj["error"] = None
        except Exception as e:
            response_obj["error"] = str(e)
            response_obj["source"] = "fallback"
            logging.error(f"Gemini API Error: {e}")
    
    return response_obj
```

---

## 🔴 PROBLEMA #3: Datos Quemados (Hardcoded)

### 📍 Ubicación
[backend/app/routes/seed.py](backend/app/routes/seed.py)

### 📊 Qué hay hardcoded
```
✔️ 8 Productos predefinidos
✔️ 6 Usuarios con credenciales fijas
✔️ 3 Reglas de negocio predeterminadas
✔️ 2 Anomalías de ejemplo
✔️ Semilla aleatoria fija: random.seed(42)
```

### 📋 Base de Datos
- **Tipo:** SQLite local (`sqlite:///./smartstock.db`)
- **Ubicación:** `backend/smartstock.db`
- **NO es una BD real de producción** (es local)
- **Está usando la BD local, NO datos quemados** en inserciones normales

### ✅ ESTADO
✅ Los datos de INSERCIÓN (movimientos, productos) **SÍ usan la BD real**
✅ Solo el SEED usa datos hardcoded para inicializar

---

## 🔴 PROBLEMA #4: Sin Logging Adecuado

### 📍 Ubicación
`backend/app/` - Múltiples archivos

### 🐛 Root Cause
Solo hay `print()` statements que van a consola:
```python
print("Error llamando a la API de Gemini (usando fallback simulado):", e)
print(f"Se registraron {len(anomalies_to_add)} anomalías nuevas en la BD.")
```

### 📊 Impacto
- Difícil debugging en producción
- Logs se pierden cuando se reinicia
- No hay trazabilidad de errores
- Sin información sobre fuente de Gemini (real vs mock)

### ✅ SOLUCIÓN
Implementar logging con módulo `logging` de Python

---

## 📊 TABLA DE ESTADO

| Componente | Estado | Problema | Crítico |
|---|---|---|---|
| Base de Datos | ✅ OK | Usando SQLite local real | No |
| Inserción de Datos | ✅ OK | Insertan en BD correctamente | No |
| Seed de Datos | ✅ OK | Hardcoded pero necesario | No |
| Botón Poblar IA | ❌ BUG | Siempre misma cantidad | **SÍ** |
| Gemini API | ⚠️ WARN | Errores silenciosos | **SÍ** |
| Anomalías | ✅ OK | Funcionan correctamente | No |
| Logging | ⚠️ WARN | Solo prints a consola | Media |

---

## 🔧 PLAN DE CORRECCIONES

### Fase 1: Crítica (Hacer ahora)
- [ ] Fijar `random.seed()` en analyze_patterns
- [ ] Mejorar respuesta de Gemini con indicador de "source"
- [ ] Agregar logging básico

### Fase 2: Mejoras
- [ ] Validar API Key de Gemini al startup
- [ ] Crear endpoint para verificar estado de Gemini
- [ ] Dashboard de logs

### Fase 3: Futuro
- [ ] Migrar a BD real (MySQL/PostgreSQL)
- [ ] Caching de predicciones
- [ ] Sistema de alerts mejorado

