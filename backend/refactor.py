import re

with open('app/static/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace auth login parsing
content = content.replace("this.user = { username: data.username, role: data.role };", "this.user = { username: data.username, role: data.role, token: data.token };")

# Substitute fetch calls manually
def replace_fetch(url, fetch_args=""):
    old_code = f"""                const res = await fetch({url}{fetch_args});
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail ||"""
    
    new_code = f"""                const data = await this.fetchAPI({url}{fetch_args});"""
    return old_code, new_code

substitutions = [
    # recover
    (
"""                const res = await fetch('/api/auth/recover', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: this.recoverForm.username,
                        new_password: this.recoverForm.new_password
                    })
                });
                
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Error al recuperar contraseña');""",
"""                const data = await this.fetchAPI('/api/auth/recover', {
                    method: 'POST',
                    body: JSON.stringify({
                        username: this.recoverForm.username,
                        new_password: this.recoverForm.new_password
                    })
                });"""
    ),
    # seed
    (
"""                const res = await fetch('/api/seed/', { method: 'POST' });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Error al sembrar base de datos');""",
"""                const data = await this.fetchAPI('/api/seed/', { method: 'POST' });"""
    ),
    # get products
    (
"""                const res = await fetch('/api/products/');
                if (!res.ok) throw new Error('No se pudieron obtener los productos');
                this.products = await res.json();""",
"""                this.products = await this.fetchAPI('/api/products/');"""
    ),
    # get movements
    (
"""                const res = await fetch('/api/movements/');
                if (!res.ok) throw new Error('No se pudo obtener el historial de movimientos');
                this.movements = await res.json();""",
"""                this.movements = await this.fetchAPI('/api/movements/');"""
    ),
    # get anomalies
    (
"""                const res = await fetch('/api/ai/anomalies');
                if (!res.ok) throw new Error('No se pudieron obtener las anomalías de inventario');
                this.anomalies = await res.json();""",
"""                this.anomalies = await this.fetchAPI('/api/ai/anomalies');"""
    ),
    # get rules
    (
"""                const res = await fetch('/api/rules/');
                if (!res.ok) throw new Error('No se pudieron obtener las reglas de negocio');
                this.rules = await res.json();""",
"""                this.rules = await this.fetchAPI('/api/rules/');"""
    ),
    # save product
    (
"""                const res = await fetch(url, {
                    method: method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.productForm)
                });
                
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Error al guardar el producto');""",
"""                const data = await this.fetchAPI(url, {
                    method: method,
                    body: JSON.stringify(this.productForm)
                });"""
    ),
    # delete product
    (
"""                const res = await fetch(`/api/products/${id}`, { method: 'DELETE' });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Error al eliminar producto');""",
"""                const data = await this.fetchAPI(`/api/products/${id}`, { method: 'DELETE' });"""
    ),
    # register movement
    (
"""                const res = await fetch(path, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body)
                });

                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Error al registrar el movimiento');""",
"""                const data = await this.fetchAPI(path, {
                    method: 'POST',
                    body: JSON.stringify(body)
                });"""
    ),
    # resolve anomaly
    (
"""                const res = await fetch(`/api/ai/anomalies/${anomalyId}/resolve`, { method: 'POST' });
                const data = await res.json();
                if (!res.ok) throw new Error('No se pudo resolver la anomalía');""",
"""                const data = await this.fetchAPI(`/api/ai/anomalies/${anomalyId}/resolve`, { method: 'POST' });"""
    ),
    # toggle rule
    (
"""                const res = await fetch(`/api/rules/${rule.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(updated)
                });
                
                const data = await res.json();
                if (!res.ok) throw new Error('No se pudo actualizar la regla');""",
"""                const data = await this.fetchAPI(`/api/rules/${rule.id}`, {
                    method: 'PUT',
                    body: JSON.stringify(updated)
                });"""
    ),
    # run rules
    (
"""                const res = await fetch('/api/rules/evaluate', { method: 'POST' });
                const data = await res.json();
                if (!res.ok) throw new Error('Error ejecutando el motor de reglas');""",
"""                const data = await this.fetchAPI('/api/rules/evaluate', { method: 'POST' });"""
    ),
    # ai patterns
    (
"""                const res = await fetch(`/api/ai/patterns/${this.selectedProductIdPatterns}`);
                if (!res.ok) throw new Error('No se pudo completar el análisis de la IA');
                
                this.aiPatternsData = await res.json();""",
"""                this.aiPatternsData = await this.fetchAPI(`/api/ai/patterns/${this.selectedProductIdPatterns}`);"""
    )
]

for old_s, new_s in substitutions:
    # Use exact string replacement where possible, but replace backticks for exact matching if variables are evaluated
    # For now simply replace exact blocks:
    content = content.replace(old_s, new_s)

# Also replace user module state
content = content.replace("rules: [],", "rules: [],\n        systemUsers: [],\n        userForm: { id: null, username: '', password: '', role: 'employee' },\n        isUserModalOpen: false,")

with open('app/static/app.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("refactored app.js")
