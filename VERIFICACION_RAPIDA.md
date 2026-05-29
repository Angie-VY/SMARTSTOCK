# ✅ VERIFICACIÓN RÁPIDA DE CORRECCIONES

**Instrucciones paso a paso para comprobar que los problemas están resueltos**

---

## 🚀 PASO 1: Reiniciar el Servidor

```bash
# En la terminal actual:
# 1. Presionar Ctrl+C para detener (si está corriendo)
# 2. Esperar 2 segundos
# 3. Ejecutar:
python run.py
```

**Qué debe ver en la consola (NUEVO - antes no estaba):**
```
============================================================
🚀 SmartStock IA - Iniciando validación de configuración...
============================================================
✅ DATABASE_URL: sqlite:///./smartstock.db...
✅ GEMINI_API_KEY configurada (primeros 10 chars: AIzaSyCLg9_...)
============================================================
✅ Tablas de BD creadas o verificadas correctamente
🟢 Servidor SmartStock IA iniciado correctamente
📚 Documentación API disponible en: /docs
```

**Si ve esto, ✅ la validación de startup funciona correctamente.**

---

## 🧪 PASO 2: Verificar Health Check de Gemini

**URL en navegador:**
```
http://localhost:8000/docs
```

**En la interfaz Swagger UI:**

1. Buscar `GET /api/ai/health`
2. Hacer clic en "Try it out"
3. Hacer clic en "Execute"

**Respuesta esperada (OK):**
```json
{
  "api_key_configured": true,
  "gemini_available": true,
  "error": null,
  "message": "✅ Gemini API funcionando correctamente"
}
```

**Si Gemini falla (pero es OK, el sistema funciona igual):**
```json
{
  "api_key_configured": true,
  "gemini_available": false,
  "error": "Error de autenticación...",
  "message": "❌ Error de autenticación: API Key inválida o expirada"
}
```

**En ambos casos es NORMAL. Lo importante es que la respuesta es clara.**

---

## 🎯 PASO 3: Probar Predicciones Dinámicas (BOTÓN POBLAR IA)

Este es el CAMBIO más importante que pidió.

**En Swagger UI:**

1. Buscar `GET /api/ai/patterns/{product_id}`
2. En `product_id` ingrese: `1`
3. Hacer clic en "Try it out"
4. Hacer clic en "Execute"

**Nota el valor de:** `predictions[0].cantidad_predicha`
```json
{
  "predictions": [
    {
      "fecha": "2026-05-29",
      "dia_semana": "Jueves",
      "cantidad_predicha": 8     // ← ANOTE ESTE NÚMERO
    },
    ...
  ]
}
```

**AHORA, repita el paso 3-4 otra vez (con el mismo product_id=1):**

**Resultado esperado (ANTES era IGUAL, AHORA es DIFERENTE):**
```json
{
  "predictions": [
    {
      "fecha": "2026-05-30",
      "dia_semana": "Viernes",
      "cantidad_predicha": 9     // ← NÚMERO DIFERENTE (ej: 7, 8, 9, 10, etc)
    },
    ...
  ]
}
```

**Si el número cambió → ✅ PROBLEMA RESUELTO**
**Si sigue igual → ⚠️ El cambio no se aplicó (reinicie servidor)**

---

## 📊 PASO 4: Verificar Indicador de Fuente de IA

**En la misma respuesta de Step 3, buscar estos campos (NUEVOS):**

```json
{
  "ai_report": "...",
  "ai_report_source": "gemini",    // ← NUEVO: dice si es real o simulación
  "ai_report_error": null           // ← NUEVO: error details si los hay
}
```

**Valores posibles:**
- `"ai_report_source": "gemini"` → Respuesta real de Gemini ✅
- `"ai_report_source": "fallback"` → Usando simulación (normal si Gemini falla)
- `"ai_report_error": "Invalid API Key"` → Error específico

**Si ve estos campos → ✅ INDICADOR DE FUENTE IMPLEMENTADO**

---

## 📝 PASO 5: Probar Inserción de Datos (Opcional)

Para verificar que BD real funciona:

**En Swagger UI:**

1. Buscar `POST /movements/in`
2. Ingrese JSON:
```json
{
  "product_id": 1,
  "quantity": 5,
  "supplier": "Proveedor Test",
  "price": 100
}
```
3. Hacer clic en "Execute"

**Respuesta esperada:**
```json
{
  "status": "success",
  "message": "Ingreso registrado: +5 unidades de 'Laptop HP'.",
  "movement": {
    "id": 999,
    "product_name": "Laptop HP",
    "type": "IN",
    "quantity": 5,
    "stock_after": 155
  },
  "rule_triggers": []
}
```

**En la consola verá (NUEVO - antes no estaba):**
```
✅ Se registraron 0 anomalías nuevas en la BD.
```

**Si ve esto → ✅ LOGGING IMPLEMENTADO Y BD FUNCIONA**

---

## 🔍 PASO 6: Ver Logs en Consola (Debugging)

**En la ventana terminal donde corre `python run.py`, busque líneas como:**

```
✅ Gemini API configurada correctamente
✅ Se registraron 2 anomalías nuevas en la BD.
✅ Respuesta recibida de Gemini API
❌ Error llamando a Gemini API: Invalid API Key (usando fallback simulado)
```

**Antes solo se veían `print()` genéricos. Ahora es logging estructurado.**

---

## ✅ CHECKLIST DE VERIFICACIÓN

Marque cada uno después de completar:

- [ ] **Startup:** Ver logs de validación al iniciar (DATABASE_URL, GEMINI_API_KEY)
- [ ] **Health Check:** `/api/ai/health` responde con estado claro
- [ ] **Predicciones Dinámicas:** Llamar 2 veces, valores DIFERENTES
- [ ] **Indicador Fuente:** Ver `ai_report_source` en respuesta
- [ ] **Inserción Datos:** Insertar movimiento, ver `stock_after` actualizado
- [ ] **Logging:** Ver mensajes en consola (✅, ❌, ⚠️)

---

## ❌ PROBLEMAS COMUNES

### Problema: No veo cambios, igual al antes

**Solución:**
```bash
# 1. Detener servidor (Ctrl+C)
# 2. Esperar 3 segundos
# 3. Ejecutar nuevamente:
python run.py
```

### Problema: Error 401 en Health Check

**Solución:**
1. Ir a `/api/auth/login`
2. Usar credenciales:
   - Username: `admin`
   - Password: `admin123`
3. Copiar el token
4. En Health Check, ir a "Authorize" (arriba a la derecha)
5. Pegar token

### Problema: Health Check dice "GEMINI API no configurada"

**Solución (NORMAL - es fallback):**
- Esto significa que GEMINI_API_KEY no está en `.env` o es inválida
- El sistema usará simulaciones automáticamente
- Ver archivo `.env`:
  ```
  GEMINI_API_KEY=AIzaSyCLg9_WFcuGC4gRxPyQqWX_QdMej19rYuk
  ```

### Problema: Predictions siempre iguales aún después de restart

**Solución:**
1. Verificar que el cambio se aplicó:
   ```bash
   # Abrir: backend/app/services/ai_service.py
   # Línea ~43, debe ver:
   # random.seed(42)     # ← DEBE ESTAR
   # random.seed()       # ← DEBE ESTAR
   ```
2. Si no está, actualizar manualmente
3. Reiniciar servidor

---

## 📞 AYUDA ADICIONAL

Si algún paso no funciona:

1. **Revisar documentos generados:**
   - `DIAGNOSTICO_PROBLEMAS.md` - análisis detallado
   - `CORRECCIONES_IMPLEMENTADAS.md` - cómo funciona cada cambio
   - `GUIA_INSERCIONES_Y_BD.md` - para errores de inserción

2. **Verificar logs en consola:**
   - Los errores ahora son visibles con ✅, ❌, ⚠️

3. **Usar endpoint /api/ai/health:**
   - Indicará exactamente qué está pasando con Gemini

---

## 🎉 RESUMEN

**Si completó los 6 pasos y todo funciona → ✅ LISTO PARA USAR**

Los 3 problemas principales fueron resueltos:
1. ✅ **Predicciones ahora son dinámicas** (no siempre igual)
2. ✅ **Errores de Gemini son reportados** (no silenciosos)
3. ✅ **Sistema tiene logging profesional** (debugging fácil)

¡El proyecto está mejorando! 🚀

