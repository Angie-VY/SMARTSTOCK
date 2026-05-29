/* ==========================================
   SmartStock IA - SPA Alpine.js Controller
   ========================================== */

function smartStockApp() {
    return {
        // --- State Variables ---
        currentTab: 'login', // login, recover, dashboard, products, movements, stock, ai-patterns, ai-anomalies, rules-engine
        isAuthenticated: false,
        user: { username: '', role: '' },
        
        // --- Lists & Data ---
        products: [],
        movements: [],
        anomalies: [],
        rules: [],
        systemUsers: [],
        userForm: { id: null, username: '', password: '', role: 'employee' },
        isUserModalOpen: false,
        
        // --- Forms State ---
        loginForm: { username: '', password: '' },
        recoverForm: { username: '', new_password: '', confirm_password: '' },
        
        productForm: { id: null, name: '', category: '', stock: 0, price: 0.0, min_stock: 10, supplier: '' },
        isProductModalOpen: false,
        isEditMode: false,
        
        movementForm: { product_id: '', type: 'IN', quantity: 1, supplier: '', reason: '' },
        isMovementModalOpen: false,
        
        // --- AI Module State ---
        selectedProductIdPatterns: '',
        aiPatternsData: null,
        loadingAI: false,
        loadingAnomalies: false,
        ruleLogs: [],
        lastRuleEvaluationLogs: [],
        
        // --- Stats & Badges ---
        stats: {
            totalStock: 0,
            lowStockCount: 0,
            portfolioValue: 0.0,
            totalProducts: 0
        },
        unreadAnomaliesCount: 0,
        
        // --- UI Effects ---
        toasts: [], // { id, message, type }
        loadingSeed: false,
        confirmDeleteId: null,
        
        // --- ApexCharts Instances ---
        charts: {
            trendChart: null,
            categoryChart: null,
            forecastChart: null
        },

        // --- Init ---
        init() {
            // Cargar sesión del localStorage si existe
            const savedUser = localStorage.getItem('ss_user');
            if (savedUser) {
                this.user = JSON.parse(savedUser);
                this.isAuthenticated = true;
                this.currentTab = 'dashboard';
                this.loadAllData();
            }
            
            // Iniciar escucha para cerrar modales al presionar Escape
            window.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.isProductModalOpen = false;
                    this.isMovementModalOpen = false;
                    this.confirmDeleteId = null;
                }
            });
        },

        // --- Notifications Helper ---
        showToast(message, type = 'success') {
            const id = Date.now() + Math.random();
            this.toasts.push({ id, message, type });
            
            // Auto eliminar después de 4 segundos
            setTimeout(() => {
                this.toasts = this.toasts.filter(t => t.id !== id);
            }, 4000);
        },

        // Backwards-compatible notification alias used in some handlers
        showNotification(message, type = 'success') {
            this.showToast(message, type);
        },

        
        // --- API Helper ---
        async fetchAPI(url, options = {}) {
            const headers = { ...options.headers };
            if (this.user && this.user.token) {
                headers['Authorization'] = 'Bearer ' + this.user.token;
            }
            if (!headers['Content-Type']) {
                headers['Content-Type'] = 'application/json';
            }
            
            const res = await fetch(url, { ...options, headers });
            
            let data;
            try {
                data = await res.json();
            } catch (e) {
                data = null;
            }
            
            if (!res.ok) {
                if (res.status === 401 || res.status === 403) {
                    if (res.status === 401) this.logout();
                    throw new Error(data.detail || 'Sesión expirada o no autorizada.');
                }
                throw new Error((data && data.detail) || 'Error en la solicitud');
            }
            return data;
        },

        // --- Auth Operations ---
        async login() {
            try {
                const res = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.loginForm)
                });
                
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Error al iniciar sesión');
                
                this.user = { username: data.username, role: data.role, token: data.token };
                this.isAuthenticated = true;
                localStorage.setItem('ss_user', JSON.stringify(this.user));
                
                this.showToast(data.message, 'success');
                this.currentTab = 'dashboard';
                
                // Cargar datos
                await this.loadAllData();
                
            } catch (err) {
                this.showToast(err.message, 'error');
            }
        },

        logout() {
            this.isAuthenticated = false;
            this.user = { username: '', role: '' };
            localStorage.removeItem('ss_user');
            this.loginForm = { username: '', password: '' };
            this.currentTab = 'login';
            this.showToast('Sesión cerrada correctamente.', 'success');
            
            // Destruir gráficos
            this.destroyCharts();
        },

        async recoverPassword() {
            if (this.recoverForm.new_password !== this.recoverForm.confirm_password) {
                this.showToast('Las contraseñas no coinciden.', 'warning');
                return;
            }

            try {
                const data = await this.fetchAPI('/api/auth/recover', {
                    method: 'POST',
                    body: JSON.stringify({
                        username: this.recoverForm.username,
                        new_password: this.recoverForm.new_password
                    })
                });
                
                this.showToast(data.message, 'success');
                this.recoverForm = { username: '', new_password: '', confirm_password: '' };
                this.currentTab = 'login';
            } catch (err) {
                this.showToast(err.message, 'error');
            }
        },

        // --- Seeding Database Operations ---
        async seedDatabase() {
            // Requiere usuario autenticado con rol 'admin'
            if (!this.isAuthenticated || this.user.role !== 'admin') {
                this.showToast('Se requiere iniciar sesión como administrador para poblar la base de datos.', 'warning');
                return;
            }

            if (!confirm('Esto reemplazará los datos del sistema y creará usuarios y datos de prueba. ¿Deseas continuar?')) return;

            this.loadingSeed = true;
            this.showToast('Sembrando base de datos con Inteligencia Artificial...', 'info');
            try {
                const data = await this.fetchAPI('/api/seed/', { method: 'POST' });

                // Mostrar resultado y recargar datos
                this.showToast(data.message, 'success');
                this.loadingSeed = false;
                await this.loadAllData();
            } catch (err) {
                this.loadingSeed = false;
                this.showToast(err.message, 'error');
            }
        },

        // --- Load Data Operations ---
        async loadAllData() {
            this.isLoading = true;
            try {
                await Promise.all([
                    this.loadProducts(),
                    this.loadMovements(),
                    this.loadAnomalies(),
                    this.loadRules()
                ]);
                
                if (this.user && this.user.role === 'admin') {
                    await this.loadUsers();
                }
                
                // Actualizar contadores
                this.unreadAnomaliesCount = this.anomalies.filter(a => !a.resolved).length;
                
                // Dibujar gráficos de Dashboard después de cargar
                this.$nextTick(() => {
                    this.renderDashboardCharts();
                });
            } catch (err) {
                this.showToast(err.message, 'error');
            } finally {
                this.isLoading = false;
            }
        },

        async loadProducts() {
            try {
                this.products = await this.fetchAPI('/api/products/');
                
                // Calcular estadísticas
                this.stats.totalProducts = this.products.length;
                this.stats.totalStock = this.products.reduce((acc, p) => acc + p.stock, 0);
                this.stats.portfolioValue = this.products.reduce((acc, p) => acc + (p.stock * p.price), 0);
                this.stats.lowStockCount = this.products.filter(p => p.stock < p.min_stock).length;
                
            } catch (err) {
                this.showToast(err.message, 'error');
            }
        },

        async loadMovements() {
            try {
                this.movements = await this.fetchAPI('/api/movements/');
            } catch (err) {
                this.showToast(err.message, 'error');
            }
        },

        async loadAnomalies() {
            this.loadingAnomalies = true;
            try {
                this.anomalies = await this.fetchAPI('/api/ai/anomalies');
                
                // Contar anomalías activas
                this.unreadAnomaliesCount = this.anomalies.filter(a => !a.resolved).length;
            } catch (err) {
                console.error(err);
            } finally {
                this.loadingAnomalies = false;
            }
        },

        async loadRules() {
            try {
                this.rules = await this.fetchAPI('/api/rules/');
            } catch (err) {
                console.error(err);
            }
        },

        // --- Products CRUD Operations ---
        openAddProductModal() {
            this.isEditMode = false;
            this.productForm = { id: null, name: '', category: 'Tecnología', stock: 0, price: 10.0, min_stock: 5, supplier: 'Proveedor General' };
            this.isProductModalOpen = true;
        },

        openEditProductModal(product) {
            this.isEditMode = true;
            this.productForm = { ...product };
            this.isProductModalOpen = true;
        },

        async saveProduct() {
            const url = this.isEditMode ? `/api/products/${this.productForm.id}` : '/api/products/';
            const method = this.isEditMode ? 'PUT' : 'POST';
            
            try {
                const data = await this.fetchAPI(url, {
                    method: method,
                    body: JSON.stringify(this.productForm)
                });
                
                this.showToast(`Producto '${data.name}' guardado correctamente.`, 'success');
                this.isProductModalOpen = false;
                await this.loadAllData();
            } catch (err) {
                this.showToast(err.message, 'error');
            }
        },

        async deleteProduct(id) {
            try {
                const data = await this.fetchAPI(`/api/products/${id}`, { method: 'DELETE' });
                
                this.showToast(data.message, 'success');
                this.confirmDeleteId = null;
                await this.loadAllData();
            } catch (err) {
                this.showToast(err.message, 'error');
            }
        },

        // --- Movements Operations ---
        openMovementModal(type, productId = '') {
            this.movementForm = {
                product_id: productId,
                type: type,
                quantity: 1,
                supplier: type === 'IN' ? 'Proveedor de Confianza' : '',
                reason: type === 'OUT' ? 'Venta' : ''
            };
            this.isMovementModalOpen = true;
        },

        async registerMovement() {
            const path = this.movementForm.type === 'IN' ? '/api/movements/in' : '/api/movements/out';
            const body = this.movementForm.type === 'IN' ? 
                { product_id: parseInt(this.movementForm.product_id), quantity: this.movementForm.quantity, supplier: this.movementForm.supplier } :
                { product_id: parseInt(this.movementForm.product_id), quantity: this.movementForm.quantity, reason: this.movementForm.reason };

            try {
                const data = await this.fetchAPI(path, {
                    method: 'POST',
                    body: JSON.stringify(body)
                });

                this.showToast(data.message, 'success');
                this.isMovementModalOpen = false;
                
                // Guardar los disparadores de reglas para mostrarlos en consola
                if (data.rule_triggers && data.rule_triggers.length > 0) {
                    this.lastRuleEvaluationLogs = data.rule_triggers;
                    this.ruleLogs = [...data.rule_triggers, ...this.ruleLogs].slice(0, 30);
                    
                    // Mostrar alerta de que se dispararon reglas automatizadas
                    this.showToast(`🔥 IA activó ${data.rule_triggers.length} acción(es) automática(s).`, 'info');
                }
                
                await this.loadAllData();
            } catch (err) {
                this.showToast(err.message, 'error');
            }
        },

        // --- Anomaly Operations ---
        async resolveAnomaly(anomalyId) {
            try {
                const data = await this.fetchAPI(`/api/ai/anomalies/${anomalyId}/resolve`, { method: 'POST' });
                
                this.showToast(data.message, 'success');
                await this.loadAnomalies();
                
                // Disparar las reglas de nuevo
                await this.runRulesEngine(false);
            } catch (err) {
                this.showToast(err.message, 'error');
            }
        },

        // --- Rules Operations ---
        async toggleRule(rule) {
            const updated = {
                name: rule.name,
                rule_type: rule.rule_type,
                is_active: !rule.is_active,
                condition_value: rule.condition_value
            };
            
            try {
                const data = await this.fetchAPI(`/api/rules/${rule.id}`, {
                    method: 'PUT',
                    body: JSON.stringify(updated)
                });
                
                this.showToast(`Regla '${data.name}' ${data.is_active ? 'ACTIVADA' : 'DESACTIVADA'}.`, 'success');
                await this.loadRules();
            } catch (err) {
                this.showToast(err.message, 'error');
            }
        },

        async runRulesEngine(showSuccessToast = true) {
            try {
                const data = await this.fetchAPI('/api/rules/evaluate', { method: 'POST' });
                
                if (data.actions_triggered && data.actions_triggered.length > 0) {
                    this.lastRuleEvaluationLogs = data.actions_triggered;
                    this.ruleLogs = [...data.actions_triggered, ...this.ruleLogs].slice(0, 30);
                    if (showSuccessToast) {
                        this.showToast(`🤖 Reglas ejecutadas con éxito. Se dispararon ${data.actions_triggered.length} acciones automatizadas.`, 'success');
                    }
                } else {
                    this.lastRuleEvaluationLogs = [];
                    if (showSuccessToast) {
                        this.showToast('🤖 Reglas evaluadas. Ninguna acción requerida en este momento.', 'info');
                    }
                }
            } catch (err) {
                this.showToast(err.message, 'error');
            }
        },

        // --- AI Pattern Detection Module ---
        async selectProductForPatterns() {
            if (!this.selectedProductIdPatterns) {
                this.aiPatternsData = null;
                return;
            }
            
            this.loadingAI = true;
            try {
                this.aiPatternsData = await this.fetchAPI(`/api/ai/patterns/${this.selectedProductIdPatterns}`);
                this.showToast(`Análisis en tiempo real para '${this.aiPatternsData.product_name}' completado.`, 'success');
                
                // Dibujar gráfico de proyección
                this.$nextTick(() => {
                    this.renderForecastChart(this.aiPatternsData.predictions);
                });
                
            } catch (err) {
                this.showToast(err.message, 'error');
                this.aiPatternsData = null;
            } finally {
                this.loadingAI = false;
            }
        },

        // --- Navigation Controller ---
        switchTab(tab) {
            this.currentTab = tab;
            
            // Destruir gráficos anteriores para evitar fugas de memoria
            this.destroyCharts();
            
            if (tab === 'dashboard') {
                this.loadAllData();
            } else if (tab === 'products') {
                this.loadProducts();
            } else if (tab === 'movements') {
                this.loadMovements();
            } else if (tab === 'ai-patterns') {
                this.loadProducts();
                this.selectedProductIdPatterns = '';
                this.aiPatternsData = null;
            } else if (tab === 'ai-anomalies') {
                this.loadAnomalies();
            } else if (tab === 'rules-engine') {
                this.loadRules();
                // Ejecutar motor al entrar
                this.runRulesEngine(false);
            }
        },

        // --- ApexCharts Rendering ---
        destroyCharts() {
            if (this.charts.trendChart) { this.charts.trendChart.destroy(); this.charts.trendChart = null; }
            if (this.charts.categoryChart) { this.charts.categoryChart.destroy(); this.charts.categoryChart = null; }
            if (this.charts.forecastChart) { this.charts.forecastChart.destroy(); this.charts.forecastChart = null; }
        },

        renderDashboardCharts() {
            this.destroyCharts();
            
            const trendEl = document.getElementById('dashboard-trend-chart');
            const catEl = document.getElementById('dashboard-category-chart');
            
            if (!trendEl || !catEl) return;

            // --- 1. Gráfico de Historial de Movimientos (Área) ---
            // Agrupar movimientos por fecha para la serie
            const dailyData = {};
            this.movements.slice(0, 30).forEach(m => {
                const day = m.date.split('T')[0];
                if (!dailyData[day]) dailyData[day] = { in: 0, out: 0 };
                if (m.type === 'IN') dailyData[day].in += m.quantity;
                else dailyData[day].out += m.quantity;
            });
            
            const sortedDates = Object.keys(dailyData).sort();
            const ins = sortedDates.map(d => dailyData[d].in);
            const outs = sortedDates.map(d => dailyData[d].out);

            const trendOptions = {
                chart: {
                    type: 'area',
                    height: 250,
                    toolbar: { show: false },
                    background: 'transparent'
                },
                theme: { mode: 'dark' },
                colors: ['#10b981', '#6366f1'],
                dataLabels: { enabled: false },
                stroke: { curve: 'smooth', width: 2 },
                series: [
                    { name: 'Entradas (Stock IN)', data: ins.length ? ins : [] },
                    { name: 'Salidas (Ventas OUT)', data: outs.length ? outs : [] }
                ],
                xaxis: {
                    categories: sortedDates.length ? sortedDates.map(d => d.substring(5)) : [],
                    labels: { style: { colors: '#94a3b8' } }
                },
                yaxis: { labels: { style: { colors: '#94a3b8' } } },
                grid: { borderColor: '#1e293b' },
                fill: {
                    type: 'gradient',
                    gradient: { opacityFrom: 0.4, opacityTo: 0.05 }
                }
            };
            this.charts.trendChart = new ApexCharts(trendEl, trendOptions);
            this.charts.trendChart.render();

            // --- 2. Distribución de Categorías (Donut) ---
            const catMap = {};
            this.products.forEach(p => {
                catMap[p.category] = (catMap[p.category] || 0) + p.stock;
            });
            const categories = Object.keys(catMap);
            const stockValues = Object.values(catMap);

            const catOptions = {
                chart: {
                    type: 'donut',
                    height: 250,
                    background: 'transparent'
                },
                theme: { mode: 'dark' },
                colors: ['#6366f1', '#06b6d4', '#f43f5e', '#f59e0b', '#10b981'],
                series: stockValues.length ? stockValues : [],
                labels: categories.length ? categories : [],
                legend: { position: 'bottom', labels: { colors: '#94a3b8' } },
                stroke: { show: false },
                plotOptions: {
                    pie: {
                        donut: {
                            size: '75%',
                            labels: {
                                show: true,
                                name: { show: true, color: '#f8fafc' },
                                value: { show: true, color: '#94a3b8' }
                            }
                        }
                    }
                }
            };
            this.charts.categoryChart = new ApexCharts(catEl, catOptions);
            this.charts.categoryChart.render();
        },

        renderForecastChart(predictions) {
            if (this.charts.forecastChart) {
                this.charts.forecastChart.destroy();
            }

            const el = document.getElementById('ai-forecast-chart');
            if (!el) return;

            const dates = predictions.map(p => `${p.dia_semana} (${p.fecha.substring(5)})`);
            const values = predictions.map(p => p.cantidad_predicha);

            const options = {
                chart: {
                    type: 'area',
                    height: 260,
                    toolbar: { show: false },
                    background: 'transparent'
                },
                theme: { mode: 'dark' },
                colors: ['#06b6d4'],
                dataLabels: { enabled: true, style: { colors: ['#f8fafc'] } },
                stroke: { curve: 'stepline', width: 3 },
                series: [{ name: 'Demanda Predicha (Ud)', data: values }],
                xaxis: {
                    categories: dates,
                    labels: { style: { colors: '#94a3b8' } }
                },
                yaxis: { labels: { style: { colors: '#94a3b8' } } },
                grid: { borderColor: '#1e293b' },
                fill: {
                    type: 'gradient',
                    gradient: { opacityFrom: 0.5, opacityTo: 0.1 }
                },
                title: {
                    text: 'Predicción de Demanda Futura (7 Días)',
                    align: 'center',
                    style: { color: '#06b6d4', fontSize: '14px', fontFamily: 'Outfit' }
                }
            };

            this.charts.forecastChart = new ApexCharts(el, options);
            this.charts.forecastChart.render();
        },

        // --- Users Operations ---
        async loadUsers() {
            try {
                this.systemUsers = await this.fetchAPI('/api/users/');
            } catch (error) {
                console.error("Error cargando usuarios:", error);
            }
        },
        openUserModal(user = null) {
            if (user) {
                this.userForm = { id: user.id, username: user.username, password: '', role: user.role };
            } else {
                this.userForm = { id: null, username: '', password: '', role: 'employee' };
            }
            this.isUserModalOpen = true;
        },
        async saveUser() {
            try {
                const isUpdate = !!this.userForm.id;
                const url = isUpdate ? `/api/users/${this.userForm.id}` : '/api/users/';
                const method = isUpdate ? 'PUT' : 'POST';
                
                await this.fetchAPI(url, {
                    method: method,
                    body: JSON.stringify(this.userForm)
                });
                
                this.showNotification(`Usuario ${isUpdate ? 'actualizado' : 'creado'} correctamente`, 'success');
                this.isUserModalOpen = false;
                await this.loadUsers();
            } catch (error) {
                this.showNotification(error.message, 'error');
            }
        },
        async deleteUser(id) {
            if (!confirm('¿Estás seguro de eliminar este usuario?')) return;
            try {
                await this.fetchAPI(`/api/users/${id}`, { method: 'DELETE' });
                this.showNotification('Usuario eliminado', 'success');
                await this.loadUsers();
            } catch (error) {
                this.showNotification(error.message, 'error');
            }
        }
    };
}
