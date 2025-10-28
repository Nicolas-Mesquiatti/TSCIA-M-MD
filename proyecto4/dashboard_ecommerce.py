# dashboard_ecommerce.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import time
import os

# Configuración de la página
st.set_page_config(
    page_title="Dashboard E-commerce en Tiempo Real",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .section-header {
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    .real-time-graph {
        border: 2px solid #1f77b4;
        border-radius: 10px;
        padding: 10px;
        background-color: #f9f9f9;
    }
</style>
""", unsafe_allow_html=True)

class DashboardEcommerce:
    def __init__(self):
        self.datos_cargados = False
        self.ventas_simuladas = []  # Lista para ventas en tiempo real
        self.tiempo_inicio = datetime.now()
        self.cargar_datos()
        if self.datos_cargados:
            self.procesar_datos()
            self.inicializar_datos_tiempo_real()
        
    def inicializar_datos_tiempo_real(self):
        """Inicializar datos para el gráfico en tiempo real"""
        # Crear datos iniciales para las últimas 24 horas
        self.tiempos_reales = []
        self.ventas_reales = []
        
        hora_actual = datetime.now()
        for i in range(10):  # Menos puntos iniciales para mejor visualización
            tiempo = hora_actual - timedelta(minutes=(9-i)*5)  # Cada 5 minutos
            self.tiempos_reales.append(tiempo)
            self.ventas_reales.append(np.random.randint(10, 100))  # Datos iniciales aleatorios
        
    def cargar_datos(self):
        """Cargar y preparar los datos"""
        try:
            # Obtener el directorio actual
            directorio_actual = os.path.dirname(os.path.abspath(__file__))
            
            # Cargar todos los datasets
            self.clientes = pd.read_csv(os.path.join(directorio_actual, "clientes_ecommerce.csv"))
            self.productos = pd.read_csv(os.path.join(directorio_actual, "productos_ecommerce.csv"))
            self.ventas = pd.read_csv(os.path.join(directorio_actual, "ventas_ecommerce.csv"))
            self.categorias = pd.read_csv(os.path.join(directorio_actual, "categorias_ecommerce.csv"))
            self.metodos_pago = pd.read_csv(os.path.join(directorio_actual, "metodos_pago.csv"))
            
            # Verificar que todos los datasets se cargaron correctamente
            if all([hasattr(self, attr) for attr in ['clientes', 'productos', 'ventas', 'categorias', 'metodos_pago']]):
                self.datos_cargados = True
                st.success("✅ Todos los datasets cargados correctamente")
                
                # Simular datos en tiempo real
                self.simular_datos_tiempo_real()
            else:
                st.error("❌ No se pudieron cargar todos los datasets")
            
        except Exception as e:
            st.error(f"❌ Error al cargar datos: {e}")
            st.info("Asegúrate de que estos archivos estén en la misma carpeta:")
            st.code("""
            - clientes_ecommerce.csv
            - productos_ecommerce.csv
            - ventas_ecommerce.csv
            - categorias_ecommerce.csv
            - metodos_pago.csv
            """)
            
            # Mostrar archivos disponibles
            st.info("📂 Archivos disponibles en el directorio:")
            try:
                archivos = os.listdir(directorio_actual)
                for archivo in archivos:
                    if archivo.endswith('.csv'):
                        st.write(f"   - {archivo}")
            except:
                st.write("No se pudieron listar los archivos")
    
    def simular_datos_tiempo_real(self):
        """Simular datos en tiempo real para demostración"""
        try:
            # Agregar timestamps para simular tiempo real
            base_date = datetime.now() - timedelta(days=30)
            self.ventas['fecha_hora'] = [
                base_date + timedelta(hours=i*2) for i in range(len(self.ventas))
            ]
            
            # Simular ventas en tiempo real
            self.ultima_venta_id = self.ventas['venta_id'].max()
        except Exception as e:
            st.warning(f"⚠️ No se pudieron simular datos en tiempo real: {e}")
    
    def procesar_datos(self):
        """Procesar y unir todos los datos"""
        try:
            # Unir datos
            self.datos_completos = pd.merge(self.ventas, self.clientes, on='cliente_id')
            self.datos_completos = pd.merge(self.datos_completos, self.productos, on='producto_id')
            self.datos_completos = pd.merge(self.datos_completos, self.categorias, left_on='categoria', right_on='nombre_categoria')
            
            # Transformaciones
            self.datos_completos['genero'] = self.datos_completos['genero'].map({'F': 'Femenino', 'M': 'Masculino'})
            self.datos_completos['cliente_premium'] = self.datos_completos['cliente_premium'].map({'Sí': 'Premium', 'No': 'Regular'})
            self.datos_completos['realizo_review'] = self.datos_completos['realizo_review'].map({'Sí': 'Sí', 'No': 'No'})
            
            # Agregar datos por cliente
            self.compras_por_cliente = self.datos_completos.groupby('cliente_id').agg({
                'total': 'sum',
                'venta_id': 'count',
                'realizo_review': lambda x: (x == 'Sí').mean(),
                'rating': 'mean'
            }).rename(columns={'venta_id': 'total_compras', 'total': 'gasto_total'}).reset_index()
            
            self.compras_por_cliente = pd.merge(self.compras_por_cliente, self.clientes, on='cliente_id')
            
            # Segmentación de clientes
            if len(self.compras_por_cliente) > 0:
                self.compras_por_cliente['segmento'] = pd.qcut(
                    self.compras_por_cliente['gasto_total'], 
                    q=min(3, len(self.compras_por_cliente)),
                    labels=['Bajo', 'Medio', 'Alto'][:min(3, len(self.compras_por_cliente))]
                )
            
        except Exception as e:
            st.error(f"❌ Error al procesar datos: {e}")
            self.datos_cargados = False
    
    def generar_venta_aleatoria(self):
        """Generar una venta aleatoria para simular tiempo real"""
        try:
            nuevo_id = self.ultima_venta_id + 1
            cliente = np.random.choice(self.clientes['cliente_id'])
            producto = np.random.choice(self.productos['producto_id'])
            cantidad = np.random.randint(1, 4)
            
            precio_producto = self.productos[self.productos['producto_id'] == producto]['precio'].values[0]
            total = cantidad * precio_producto
            
            nueva_venta = {
                'venta_id': nuevo_id,
                'cliente_id': cliente,
                'producto_id': producto,
                'fecha_venta': datetime.now().strftime("%Y-%m-%d"),
                'fecha_hora': datetime.now(),
                'cantidad': cantidad,
                'total': total,
                'metodo_pago': np.random.choice(['Tarjeta', 'PayPal', 'Efectivo']),
                'realizo_review': np.random.choice(['Sí', 'No'])
            }
            
            # Agregar a ventas simuladas para el gráfico en tiempo real
            self.ventas_simuladas.append({
                'timestamp': datetime.now(),
                'monto': total,
                'producto_id': producto,
                'cliente_id': cliente
            })
            
            # Actualizar gráfico en tiempo real
            self.actualizar_grafico_tiempo_real(total)
            
            self.ultima_venta_id = nuevo_id
            return nueva_venta
            
        except Exception as e:
            st.warning(f"⚠️ No se pudo generar venta aleatoria: {e}")
            return None
    
    def actualizar_grafico_tiempo_real(self, monto_venta):
        """Actualizar el gráfico en tiempo real con nueva venta"""
        try:
            # Agregar nuevo punto de datos
            ahora = datetime.now()
            self.tiempos_reales.append(ahora)
            self.ventas_reales.append(monto_venta)
            
            # Mantener solo las últimas 30 puntos para mejor rendimiento
            if len(self.tiempos_reales) > 30:
                self.tiempos_reales = self.tiempos_reales[-30:]
                self.ventas_reales = self.ventas_reales[-30:]
                
        except Exception as e:
            st.error(f"Error actualizando gráfico tiempo real: {e}")
    
    def mostrar_grafico_tiempo_real(self):
        """Mostrar gráfico lineal en tiempo real"""
        st.markdown("---")
        st.markdown('<h2 class="section-header">📈 Evolución de Ventas en Tiempo Real</h2>', 
                   unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Crear gráfico en tiempo real
            if len(self.tiempos_reales) > 0:
                fig = go.Figure()
                
                # Línea principal de ventas
                fig.add_trace(go.Scatter(
                    x=self.tiempos_reales,
                    y=self.ventas_reales,
                    mode='lines+markers',
                    name='Ventas en Tiempo Real',
                    line=dict(color='#1f77b4', width=3),
                    marker=dict(size=8, color='#ff7f0e'),
                    fill='tozeroy',
                    fillcolor='rgba(31, 119, 180, 0.1)'
                ))
                
                # Promedio móvil (últimas 5 ventas)
                if len(self.ventas_reales) >= 5:
                    promedio_movil = pd.Series(self.ventas_reales).rolling(window=5).mean()
                    fig.add_trace(go.Scatter(
                        x=self.tiempos_reales,
                        y=promedio_movil,
                        mode='lines',
                        name='Promedio Móvil (5 ventas)',
                        line=dict(color='red', width=2, dash='dash')
                    ))
                
                fig.update_layout(
                    title='🔄 Evolución de Ventas en Tiempo Real',
                    xaxis_title='Tiempo',
                    yaxis_title='Monto de Venta ($)',
                    height=400,
                    showlegend=True,
                    template='plotly_white'
                )
                
                # Destacar el último punto
                if len(self.tiempos_reales) > 0:
                    fig.add_annotation(
                        x=self.tiempos_reales[-1],
                        y=self.ventas_reales[-1],
                        text="Última venta",
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1,
                        arrowwidth=2,
                        arrowcolor="red"
                    )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de ventas en tiempo real aún")
        
        with col2:
            st.markdown("### 📊 Estadísticas en Tiempo Real")
            if len(self.ventas_reales) > 0:
                st.metric(
                    "Ventas Totales (RT)",
                    f"${sum(self.ventas_reales):.2f}",
                    f"+${self.ventas_reales[-1] if self.ventas_reales else 0:.2f}"
                )
                
                st.metric(
                    "Número de Ventas (RT)",
                    len(self.ventas_reales),
                    "+1"
                )
                
                if len(self.ventas_reales) > 0:
                    st.metric(
                        "Ticket Promedio (RT)",
                        f"${np.mean(self.ventas_reales):.2f}",
                        f"${(self.ventas_reales[-1] - np.mean(self.ventas_reales[:-1])) if len(self.ventas_reales) > 1 else 0:.2f}"
                    )
                
                # Información de la última venta
                if self.ventas_simuladas:
                    ultima = self.ventas_simuladas[-1]
                    st.markdown("---")
                    st.markdown("**Última Venta:**")
                    st.write(f"🕒 {ultima['timestamp'].strftime('%H:%M:%S')}")
                    st.write(f"💰 ${ultima['monto']:.2f}")
                    st.write(f"👤 Cliente: {ultima['cliente_id']}")
                    st.write(f"📦 Producto: {ultima['producto_id']}")
    
    def mostrar_controles_simulacion(self):
        """Mostrar controles para la simulación en tiempo real"""
        st.markdown("---")
        st.markdown('<h3 class="section-header">🎮 Controles de Simulación</h3>', 
                   unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Botón para generar una venta
            if st.button('🔄 Generar Nueva Venta', key='gen_venta', use_container_width=True):
                with st.spinner('Generando venta...'):
                    time.sleep(0.5)
                    nueva_venta = self.generar_venta_aleatoria()
                    
                    if nueva_venta:
                        st.success(f"✅ Nueva venta generada: ${nueva_venta['total']:.2f}")
                    else:
                        st.error("❌ No se pudo generar la venta")
            
            # Botón para generar múltiples ventas
            if st.button('🚀 Generar 5 Ventas Rápidas', key='gen_5_ventas', use_container_width=True):
                progress_bar = st.progress(0)
                for i in range(5):
                    time.sleep(0.3)
                    self.generar_venta_aleatoria()
                    progress_bar.progress((i + 1) / 5)
                st.success("✅ 5 ventas generadas exitosamente!")
        
        with col2:
            # Selector de velocidad de simulación
            velocidad = st.slider("Velocidad de simulación", 1, 10, 3)
            if st.button('▶️ Iniciar Simulación Continua', key='sim_continua', use_container_width=True):
                st.info("🔄 Simulación en curso... (Presiona Stop en el navegador para detener)")
                placeholder = st.empty()
                for i in range(10):
                    time.sleep(2/velocidad)  # Más rápido con mayor velocidad
                    nueva_venta = self.generar_venta_aleatoria()
                    with placeholder.container():
                        if nueva_venta:
                            st.success(f"Venta #{i+1}: ${nueva_venta['total']:.2f}")

    def mostrar_header(self):
        """Mostrar el encabezado del dashboard"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<h1 class="main-header">🛒 Dashboard E-commerce en Tiempo Real</h1>', 
                       unsafe_allow_html=True)
            st.markdown("### Monitoreo en vivo del comportamiento de clientes y ventas")
    
    def mostrar_metricas_principales(self):
        """Mostrar métricas principales en tiempo real"""
        if not self.datos_cargados:
            st.warning("⚠️ No hay datos disponibles para mostrar métricas")
            return
            
        st.markdown("---")
        st.markdown('<h2 class="section-header">📊 Métricas Principales</h2>', 
                   unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total_ventas = len(self.ventas)
            st.metric(
                label="Total Ventas", 
                value=f"{total_ventas:,}",
                delta="+2 hoy"
            )
        
        with col2:
            ingresos_totales = self.ventas['total'].sum()
            st.metric(
                label="Ingresos Totales", 
                value=f"${ingresos_totales:,.2f}",
                delta=f"+${ingresos_totales * 0.05:,.2f}"
            )
        
        with col3:
            ticket_promedio = self.ventas['total'].mean()
            st.metric(
                label="Ticket Promedio", 
                value=f"${ticket_promedio:.2f}",
                delta="+$5.20"
            )
        
        with col4:
            clientes_unicos = self.clientes['cliente_id'].nunique()
            st.metric(
                label="Clientes Únicos", 
                value=f"{clientes_unicos}",
                delta="+3"
            )
        
        with col5:
            try:
                tasa_reviews = (self.datos_completos['realizo_review'] == 'Sí').mean() * 100
                st.metric(
                    label="Tasa de Reviews", 
                    value=f"{tasa_reviews:.1f}%",
                    delta="+2.5%"
                )
            except:
                st.metric(
                    label="Tasa de Reviews", 
                    value="N/A",
                    delta="0%"
                )
    
    def mostrar_analisis_ventas(self):
        """Mostrar análisis de ventas"""
        if not self.datos_cargados:
            st.warning("⚠️ No hay datos disponibles para análisis de ventas")
            return
            
        st.markdown("---")
        st.markdown('<h2 class="section-header">💰 Análisis de Ventas</h2>', 
                   unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Ventas por categoría
            try:
                ventas_categoria = self.datos_completos.groupby('categoria')['total'].sum().reset_index()
                fig = px.bar(
                    ventas_categoria, 
                    x='total', 
                    y='categoria',
                    orientation='h',
                    title='Ventas Totales por Categoría',
                    color='total',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error en gráfico de ventas por categoría: {e}")
        
        with col2:
            # Ventas por método de pago
            try:
                ventas_metodo = self.datos_completos['metodo_pago'].value_counts()
                fig = px.pie(
                    values=ventas_metodo.values,
                    names=ventas_metodo.index,
                    title='Distribución por Método de Pago',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error en gráfico de métodos de pago: {e}")
        
        col3, col4 = st.columns(2)
        
        with col3:
            # Evolución temporal de ventas (simulada)
            try:
                ventas_diarias = self.datos_completos.groupby(
                    pd.to_datetime(self.datos_completos['fecha_venta'])
                )['total'].sum().reset_index()
                
                fig = px.line(
                    ventas_diarias,
                    x='fecha_venta',
                    y='total',
                    title='Evolución de Ventas Diarias',
                    markers=True
                )
                fig.update_traces(line=dict(color='#1f77b4', width=3))
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error en gráfico de evolución: {e}")
        
        with col4:
            # Productos más vendidos
            try:
                productos_vendidos = self.datos_completos.groupby('producto_id').agg({
                    'cantidad': 'sum',
                    'total': 'sum',
                    'categoria': 'first'
                }).reset_index()
                
                fig = px.treemap(
                    productos_vendidos,
                    path=['categoria', 'producto_id'],
                    values='cantidad',
                    title='Productos Más Vendidos por Categoría',
                    color='total',
                    color_continuous_scale='RdYlBu'
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error en treemap de productos: {e}")
    
    def mostrar_analisis_clientes(self):
        """Mostrar análisis de clientes"""
        if not self.datos_cargados:
            st.warning("⚠️ No hay datos disponibles para análisis de clientes")
            return
            
        st.markdown("---")
        st.markdown('<h2 class="section-header">👥 Análisis de Clientes</h2>', 
                   unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribución demográfica
            try:
                fig = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=('Distribución por Edad', 'Distribución por Género', 
                                  'Clientes Premium vs Regular', 'Distribución de Ingresos'),
                    specs=[[{"type": "histogram"}, {"type": "pie"}],
                           [{"type": "pie"}, {"type": "histogram"}]]
                )
                
                # Edad
                fig.add_trace(go.Histogram(x=self.clientes['edad'], name='Edad'), row=1, col=1)
                
                # Género
                genero_counts = self.clientes['genero'].value_counts()
                fig.add_trace(go.Pie(labels=genero_counts.index, values=genero_counts.values, 
                                   name='Género'), row=1, col=2)
                
                # Premium vs Regular
                premium_counts = self.clientes['cliente_premium'].value_counts()
                fig.add_trace(go.Pie(labels=premium_counts.index, values=premium_counts.values,
                                   name='Tipo Cliente'), row=2, col=1)
                
                # Ingresos
                fig.add_trace(go.Histogram(x=self.clientes['ingreso_mensual'], name='Ingresos'), 
                             row=2, col=2)
                
                fig.update_layout(height=600, showlegend=False, title_text="Análisis Demográfico de Clientes")
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error en análisis demográfico: {e}")
        
        with col2:
            # Segmentación de clientes por valor
            try:
                if len(self.compras_por_cliente) > 0:
                    fig = px.scatter(
                        self.compras_por_cliente,
                        x='frecuencia_compra',
                        y='gasto_total',
                        size='gasto_total',
                        color='segmento' if 'segmento' in self.compras_por_cliente.columns else None,
                        hover_data=['cliente_id', 'edad', 'ingreso_mensual'],
                        title='Segmentación de Clientes por Valor',
                        size_max=50,
                        color_discrete_sequence=['#ff9999', '#66b3ff', '#99ff99']
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No hay suficientes datos para segmentación de clientes")
            except Exception as e:
                st.error(f"Error en segmentación de clientes: {e}")
            
            # Comportamiento de compra por grupo de edad
            try:
                if len(self.compras_por_cliente) > 0:
                    self.compras_por_cliente['grupo_edad'] = pd.cut(
                        self.compras_por_cliente['edad'],
                        bins=[20, 30, 40, 50, 60],
                        labels=['20-30', '31-40', '41-50', '51-60']
                    )
                    
                    gasto_edad = self.compras_por_cliente.groupby('grupo_edad').agg({
                        'gasto_total': 'mean',
                        'frecuencia_compra': 'mean'
                    }).reset_index()
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=gasto_edad['grupo_edad'],
                        y=gasto_edad['gasto_total'],
                        name='Gasto Promedio',
                        marker_color='#1f77b4'
                    ))
                    fig.add_trace(go.Scatter(
                        x=gasto_edad['grupo_edad'],
                        y=gasto_edad['frecuencia_compra'] * 100,  # Escalar para mejor visualización
                        name='Frecuencia (x100)',
                        yaxis='y2',
                        line=dict(color='red', width=3)
                    ))
                    
                    fig.update_layout(
                        title='Gasto y Frecuencia por Grupo de Edad',
                        xaxis_title='Grupo de Edad',
                        yaxis_title='Gasto Promedio ($)',
                        yaxis2=dict(
                            title='Frecuencia de Compra',
                            overlaying='y',
                            side='right'
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error en análisis por edad: {e}")
    
    def mostrar_analisis_productos(self):
        """Mostrar análisis de productos"""
        if not self.datos_cargados:
            st.warning("⚠️ No hay datos disponibles para análisis de productos")
            return
            
        st.markdown("---")
        st.markdown('<h2 class="section-header">📦 Análisis de Productos</h2>', 
                   unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Rating vs Ventas
            try:
                fig = px.scatter(
                    self.productos,
                    x='rating',
                    y='vendidos_mes',
                    size='precio',
                    color='categoria',
                    hover_data=['producto_id', 'precio'],
                    title='Rating vs Ventas Mensuales',
                    size_max=30
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error en gráfico rating vs ventas: {e}")
        
        with col2:
            # Precio vs Rating
            try:
                fig = px.scatter(
                    self.productos,
                    x='precio',
                    y='rating',
                    size='vendidos_mes',
                    color='categoria',
                    hover_data=['producto_id', 'stock'],
                    title='Precio vs Rating de Productos',
                    size_max=30
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error en gráfico precio vs rating: {e}")
        
        # Performance por categoría
        try:
            performance_categoria = self.datos_completos.groupby('categoria').agg({
                'total': 'sum',
                'venta_id': 'count',
                'rating': 'mean',
                'margen_ganancia': 'mean'
            }).reset_index()
            
            fig = go.Figure(data=[
                go.Bar(name='Ventas Totales', x=performance_categoria['categoria'], 
                      y=performance_categoria['total'], yaxis='y', offsetgroup=1),
                go.Bar(name='Número de Ventas', x=performance_categoria['categoria'], 
                      y=performance_categoria['venta_id'], yaxis='y2', offsetgroup=2),
                go.Scatter(name='Rating Promedio', x=performance_categoria['categoria'], 
                         y=performance_categoria['rating'] * 100, yaxis='y3', 
                         line=dict(color='red', width=3))
            ])
            
            fig.update_layout(
                title='Performance por Categoría - Múltiples Métricas',
                xaxis_title='Categoría',
                yaxis=dict(title='Ventas Totales ($)', side='left'),
                yaxis2=dict(title='Número de Ventas', side='right', overlaying='y'),
                yaxis3=dict(title='Rating (%)', side='right', overlaying='y', position=0.15),
                barmode='group'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error en performance por categoría: {e}")
    
    def mostrar_tendencias_tiempo_real(self):
        """Mostrar tendencias en tiempo real"""
        if not self.datos_cargados:
            st.warning("⚠️ No hay datos disponibles para tendencias en tiempo real")
            return
            
        st.markdown("---")
        st.markdown('<h2 class="section-header">⏰ Tendencias en Tiempo Real</h2>', 
                   unsafe_allow_html=True)
        
        # Simular actualización en tiempo real
        if st.button('🔄 Actualizar Datos en Tiempo Real'):
            with st.spinner('Simulando nueva data...'):
                time.sleep(2)
                
                # Generar venta simulada
                nueva_venta = self.generar_venta_aleatoria()
                
                if nueva_venta:
                    # Mostrar la nueva venta
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.info(f"**Nueva Venta:** #{nueva_venta['venta_id']}")
                    with col2:
                        st.info(f"**Cliente:** {nueva_venta['cliente_id']}")
                    with col3:
                        st.info(f"**Total:** ${nueva_venta['total']:.2f}")
                    with col4:
                        st.info(f"**Método:** {nueva_venta['metodo_pago']}")
                    
                    # Actualizar métricas
                    st.success("✅ Datos actualizados exitosamente!")
                else:
                    st.warning("No se pudo generar nueva venta")
        
        # Heatmap de ventas por hora del día (simulado)
        st.subheader("Patrón de Ventas por Hora")
        
        try:
            # Simular datos de horas
            horas = list(range(24))
            ventas_por_hora = [np.random.randint(10, 100) for _ in horas]
            
            fig = go.Figure(data=go.Heatmap(
                z=[ventas_por_hora],
                x=horas,
                y=['Ventas'],
                colorscale='Viridis',
                showscale=True
            ))
            
            fig.update_layout(
                title='Distribución de Ventas por Hora del Día',
                xaxis_title='Hora del Día',
                yaxis_title=''
            )
            
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error en heatmap: {e}")
    
    def mostrar_recomendaciones(self):
        """Mostrar recomendaciones basadas en el análisis"""
        st.markdown("---")
        st.markdown('<h2 class="section-header">💡 Recomendaciones Estratégicas</h2>', 
                   unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 🎯 Marketing
            - **Segmentar** por grupo de edad 31-50 años
            - **Incentivar** reviews con programas de recompensa
            - **Crear** campañas para clientes premium
            - **Optimizar** métodos de pago preferidos
            """)
        
        with col2:
            st.markdown("""
            ### 📊 Inventario
            - **Aumentar** stock en categorías populares
            - **Revisar** precios en bajo performance
            - **Crear** bundles de productos
            - **Monitorear** rotación de stock
            """)
        
        with col3:
            st.markdown("""
            ### 💡 Experiencia
            - **Mejorar** proceso de checkout
            - **Implementar** recomendaciones
            - **Crear** programa de fidelización
            - **Optimizar** mobile experience
            """)
    
    def ejecutar(self):
        """Ejecutar el dashboard completo"""
        self.mostrar_header()
        
        if not self.datos_cargados:
            st.error("❌ No se pudieron cargar los datos necesarios para el dashboard.")
            st.info("Por favor, verifica que todos los archivos CSV estén en la misma carpeta y tengan el formato correcto.")
            return
        
        # Todas las secciones originales del dashboard
        self.mostrar_metricas_principales()
        self.mostrar_analisis_ventas()
        self.mostrar_analisis_clientes()
        self.mostrar_analisis_productos()
        self.mostrar_tendencias_tiempo_real()
        self.mostrar_recomendaciones()
        
        # NUEVA SECCIÓN: Gráfico en tiempo real al final
        self.mostrar_grafico_tiempo_real()
        self.mostrar_controles_simulacion()
        
        # Footer
        st.markdown("---")
        st.markdown(
            "🛒 **Dashboard E-commerce** | "
            "Desarrollado con Streamlit | "
            f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

# Ejecutar la aplicación
if __name__ == "__main__":
    dashboard = DashboardEcommerce()
    dashboard.ejecutar()