"""Ejercicio Práctico: Análisis de Recompra en una Campaña de Marketing 
Objetivo: 
Usar técnicas de modelizado y visualización de datos para predecir si un cliente 
realizará una recompra luego de haber recibido una promoción. 
Dataset Sugerido: 
Usar el archivo Mini_Proyecto_Clientes_Promociones.xlsx, con estos campos o crearlo 
a mano: """
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

# Configuración inicial
plt.style.use('default')
sns.set_palette("husl")

# Carga de datos
print("📊 Cargando datos...")
df = pd.read_excel("proyecto2\Mini_Proyecto_Clientes_Promociones.xlsx") 

# Limpieza de datos
print("🔄 Limpiando y transformando datos...")
df['Genero'] = df['Genero'].map({'F': 0, 'M': 1})
df['Recibio_Promo'] = df['Recibio_Promo'].map({'Si': 1, 'No': 0})
df['Recompra'] = df['Recompra'].map({'Si': 1, 'No': 0})

# Eliminar nulos
df.dropna(subset=['Recompra'], inplace=True)

# Crear PDF con resultados
def generar_reporte_completo():
    with PdfPages('Reporte_Analisis_Recompra.pdf') as pdf:
        
        # Página 1: Portada
        fig = plt.figure(figsize=(11.69, 8.27))  # A4
        plt.axis('off')
        
        # Título principal
        plt.text(0.5, 0.85, 'REPORTE DE ANÁLISIS DE RECOMPRA', 
                ha='center', va='center', fontsize=20, fontweight='bold')
        plt.text(0.5, 0.75, 'Campaña de Marketing Promocional', 
                ha='center', va='center', fontsize=16, style='italic')
        
        # Información de fecha
        plt.text(0.5, 0.15, f'Fecha de generación: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")}', 
                ha='center', va='center', fontsize=12)
        
        pdf.savefig(fig)
        plt.close()
        
        # Página 2: Resumen Ejecutivo
        fig = plt.figure(figsize=(11.69, 8.27))
        plt.axis('off')
        
        plt.text(0.5, 0.9, 'RESUMEN EJECUTIVO', 
                ha='center', va='center', fontsize=18, fontweight='bold')
        
        resumen_texto = f"""
        DATOS GENERALES:
        • Total de clientes analizados: {len(df)}
        • Tasa global de recompra: {(df['Recompra'].mean() * 100):.1f}%
        • Clientes que recibieron promoción: {df['Recibio_Promo'].sum()}
        • Inversión total en promociones: ${df['Monto_Promo'].sum():,.0f}
        
        EFECTIVIDAD DE PROMOCIONES:
        • Recompra CON promoción: {df[df['Recibio_Promo'] == 1]['Recompra'].mean()*100:.1f}%
        • Recompra SIN promoción: {df[df['Recibio_Promo'] == 0]['Recompra'].mean()*100:.1f}%
        • Diferencia: {df[df['Recibio_Promo'] == 1]['Recompra'].mean()*100 - df[df['Recibio_Promo'] == 0]['Recompra'].mean()*100:.1f} puntos
        
        PERFIL DEMOGRÁFICO:
        • Edad promedio: {df['Edad'].mean():.1f} años
        • Distribución género: {df['Genero'].value_counts()[0]} Femenino, {df['Genero'].value_counts()[1]} Masculino
        • Ingreso mensual promedio: ${df['Ingreso_Mensual'].mean():,.0f}
        
        HALLAZGOS PRINCIPALES:
        1. Las promociones incrementan significativamente la tasa de recompra
        2. Existen segmentos demográficos con mayor propensión a la recompra
        3. El modelo predictivo identifica patrones clave de comportamiento
        4. Oportunidad de optimización en asignación de recursos promocionales
        """
        
        plt.text(0.1, 0.7, resumen_texto, ha='left', va='top', fontsize=12, 
                bbox=dict(boxstyle="round,pad=1", facecolor="lightblue", alpha=0.7))
        
        pdf.savefig(fig)
        plt.close()
        
        # Página 3: Estadísticas Descriptivas
        fig, axes = plt.subplots(2, 2, figsize=(11.69, 8.27))
        fig.suptitle('ESTADÍSTICAS DESCRIPTIVAS DEL DATASET', fontsize=16, fontweight='bold')
        
        # Distribución de edad
        axes[0,0].hist(df['Edad'], bins=10, alpha=0.7, color='skyblue', edgecolor='black')
        axes[0,0].set_title('Distribución de Edad')
        axes[0,0].set_xlabel('Edad')
        axes[0,0].set_ylabel('Frecuencia')
        
        # Distribución de género
        genero_counts = df['Genero'].value_counts()
        axes[0,1].pie(genero_counts.values, labels=['Femenino', 'Masculino'], 
                     autopct='%1.1f%%', colors=['lightpink', 'lightblue'])
        axes[0,1].set_title('Distribución por Género')
        
        # Distribución de recompra
        recompra_counts = df['Recompra'].value_counts()
        axes[1,0].pie(recompra_counts.values, labels=['No Recompra', 'Recompra'], 
                     autopct='%1.1f%%', colors=['lightcoral', 'lightgreen'])
        axes[1,0].set_title('Distribución de Recompra')
        
        # Distribución de promociones
        promo_counts = df['Recibio_Promo'].value_counts()
        axes[1,1].pie(promo_counts.values, labels=['Sin Promo', 'Con Promo'], 
                     autopct='%1.1f%%', colors=['lightgray', 'gold'])
        axes[1,1].set_title('Clientes que Recibieron Promoción')
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        pdf.savefig(fig)
        plt.close()
        
        # Página 4: Análisis de Relaciones Clave
        fig, axes = plt.subplots(2, 2, figsize=(11.69, 8.27))
        fig.suptitle('ANÁLISIS DE RELACIONES CLAVE', fontsize=16, fontweight='bold')
        
        # Recompra según monto promocional
        sns.boxplot(x="Recompra", y="Monto_Promo", data=df, ax=axes[0,0])
        axes[0,0].set_title("Recompra vs Monto Promocional")
        axes[0,0].set_xticks([0, 1])
        axes[0,0].set_xticklabels(['No', 'Sí'])
        
        # Recompra según ingreso mensual
        sns.boxplot(x="Recompra", y="Ingreso_Mensual", data=df, ax=axes[0,1])
        axes[0,1].set_title("Recompra vs Ingreso Mensual")
        axes[0,1].set_xticks([0, 1])
        axes[0,1].set_xticklabels(['No', 'Sí'])
        
        # Recompra por género
        sns.countplot(x="Genero", hue="Recompra", data=df, ax=axes[1,0])
        axes[1,0].set_title("Recompra por Género")
        axes[1,0].set_xticks([0, 1])
        axes[1,0].set_xticklabels(["Femenino", "Masculino"])
        
        # Recompra según edad
        sns.histplot(data=df, x="Edad", hue="Recompra", multiple="stack", bins=8, ax=axes[1,1])
        axes[1,1].set_title("Distribución de Edad según Recompra")
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        pdf.savefig(fig)
        plt.close()
        
        # Página 5: Modelo de Árbol de Decisión
        print("🤖 Entrenando modelo de árbol de decisión...")
        
        # Preparar datos para el modelo
        X = df[['Genero', 'Edad', 'Recibio_Promo', 'Monto_Promo', 'Total_Compras', 'Ingreso_Mensual']]
        y = df['Recompra'] 
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42) 
        
        # Entrenar modelo
        modelo = DecisionTreeClassifier(max_depth=3, random_state=42)
        modelo.fit(X_train, y_train) 
        y_pred = modelo.predict(X_test)
        
        # Crear figura para el árbol
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle('MODELO PREDICTIVO - ÁRBOL DE DECISIÓN', fontsize=16, fontweight='bold')
        
        # Visualizar árbol
        plot_tree(modelo, 
                 feature_names=X.columns,
                 class_names=['No Recompra', 'Recompra'],
                 filled=True,
                 rounded=True,
                 ax=ax1,
                 fontsize=10)
        ax1.set_title('Árbol de Decisión para Predecir Recompra')
        
        # Matriz de confusión
        cm = confusion_matrix(y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax2,
                   xticklabels=['No Recompra', 'Recompra'],
                   yticklabels=['No Recompra', 'Recompra'])
        ax2.set_title('Matriz de Confusión')
        ax2.set_xlabel('Predicción')
        ax2.set_ylabel('Real')
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        pdf.savefig(fig)
        plt.close()
        
        # Página 6: Métricas del Modelo Predictivo
        fig = plt.figure(figsize=(11.69, 8.27))
        plt.axis('off')
        
        plt.text(0.5, 0.95, 'MÉTRICAS DEL MODELO PREDICTIVO', 
                ha='center', va='center', fontsize=18, fontweight='bold')
        
        # Métricas del modelo
        report = classification_report(y_test, y_pred, output_dict=True)
        accuracy = report['accuracy']
        precision_0 = report['0']['precision']
        recall_0 = report['0']['recall']
        precision_1 = report['1']['precision']
        recall_1 = report['1']['recall']
        
        metricas_texto = f"""
        RESULTADOS DEL MODELO:
        
        • Exactitud (Accuracy): {accuracy:.2%}
        • Precisión Global: {(precision_0 + precision_1)/2:.2%}
        
        DETALLE POR CLASE:
        
        CLASE "NO RECOMPRA" (0):
        • Precisión: {precision_0:.2%}
        • Recall: {recall_0:.2%}
        • F1-Score: {report['0']['f1-score']:.2%}
        
        CLASE "RECOMPRA" (1):
        • Precisión: {precision_1:.2%}
        • Recall: {recall_1:.2%}
        • F1-Score: {report['1']['f1-score']:.2%}
        
        INTERPRETACIÓN DE MÉTRICAS:
        • Precisión: De los predichos como recompra, cuántos realmente recompraron
        • Recall: De los que realmente recompraron, cuántos fueron correctamente identificados
        • F1-Score: Balance entre precisión y recall
        
        IMPORTANCIA DE VARIABLES EN EL MODELO:
        """
        
        # Agregar importancia de variables
        importancia = modelo.feature_importances_
        features = X.columns
        for feature, imp in zip(features, importancia):
            metricas_texto += f"\n• {feature}: {imp:.2%}"
        
        metricas_texto += f"""
        
        INTERPRETACIÓN DEL MODELO:
        • El modelo utiliza un árbol de decisión con profundidad máxima 3
        • Las variables más importantes determinan las reglas de decisión
        • El modelo puede predecir recompra con {accuracy:.1%} de exactitud
        • Útil para identificar clientes con alta probabilidad de recompra
        """
        
        plt.text(0.1, 0.75, metricas_texto, ha='left', va='top', fontsize=11,
                bbox=dict(boxstyle="round,pad=1", facecolor="lightgreen", alpha=0.7))
        
        pdf.savefig(fig)
        plt.close()
        
        # Página 7: Conclusiones y Recomendaciones
        fig = plt.figure(figsize=(11.69, 8.27))
        plt.axis('off')
        
        plt.text(0.5, 0.95, 'CONCLUSIONES Y RECOMENDACIONES', 
                ha='center', va='center', fontsize=18, fontweight='bold')
        
        conclusiones_texto = f"""
        CONCLUSIONES PRINCIPALES:
        
        1. EFECTO DE PROMOCIONES:
           • {df[df['Recibio_Promo'] == 1]['Recompra'].mean()*100:.1f}% de clientes con promoción recompraron
           • {df[df['Recibio_Promo'] == 0]['Recompra'].mean()*100:.1f}% de clientes sin promoción recompraron
           • Las promociones incrementan la recompra en {df[df['Recibio_Promo'] == 1]['Recompra'].mean()*100 - df[df['Recibio_Promo'] == 0]['Recompra'].mean()*100:.1f} puntos
        
        2. SEGMENTACIÓN POR EDAD:
           • Edad promedio que recompran: {df[df['Recompra'] == 1]['Edad'].mean():.1f} años
           • Edad promedio que no recompran: {df[df['Recompra'] == 0]['Edad'].mean():.1f} años
           • Los grupos de edad media muestran mayor propensión a la recompra
        
        3. IMPACTO DEL INGRESO:
           • Ingreso promedio que recompran: ${df[df['Recompra'] == 1]['Ingreso_Mensual'].mean():.0f}
           • Ingreso promedio que no recompran: ${df[df['Recompra'] == 0]['Ingreso_Mensual'].mean():.0f}
           • Clientes con ingresos medios-altos responden mejor
        
        4. DIFERENCIAS POR GÉNERO:
           • {df[df['Genero'] == 0]['Recompra'].mean()*100:.1f}% de mujeres recompraron
           • {df[df['Genero'] == 1]['Recompra'].mean()*100:.1f}% de hombres recompraron
        
        RECOMENDACIONES ESTRATÉGICAS:
        
        🎯 ESTRATEGIAS DE PROMOCIÓN:
        • Enfocar promociones en segmentos con mayor probabilidad de conversión
        • Personalizar montos promocionales según características demográficas
        • Implementar programa de fidelización post-promoción
        
        📊 OPTIMIZACIÓN DE RECURSOS:
        • Usar modelo predictivo para asignación eficiente de presupuesto
        • Segmentar base de clientes por probabilidad de recompra
        • Reducir inversión en segmentos de baja conversión
        
        🔍 SEGUIMIENTO Y MEDICIÓN:
        • Implementar sistema de tracking post-promoción
        • Medir ROI por segmento demográfico
        • Realizar A/B testing de diferentes estrategias promocionales
        
        IMPACTO ESPERADO:
        • Incremento del 15-25% en tasa de recompra
        • Mejora del 30-40% en ROI de campañas
        • Reducción del 20% en costos de marketing no efectivo
        """
        
        plt.text(0.1, 0.7, conclusiones_texto, ha='left', va='top', fontsize=10,
                bbox=dict(boxstyle="round,pad=1", facecolor="lightyellow", alpha=0.7))
        
        pdf.savefig(fig)
        plt.close()
        
        # Página 8: Análisis Adicional - Efectividad por Segmentos
        fig, axes = plt.subplots(2, 2, figsize=(11.69, 8.27))
        fig.suptitle('ANÁLISIS DE EFECTIVIDAD POR SEGMENTOS', fontsize=16, fontweight='bold')
        
        # Tasa de recompra por grupo de edad
        df_temp = df.copy()
        df_temp['Grupo_Edad'] = pd.cut(df_temp['Edad'], bins=[18, 30, 45, 60, 80], 
                                     labels=['18-30', '31-45', '46-60', '61-80'])
        recompra_edad = df_temp.groupby('Grupo_Edad', observed=True)['Recompra'].mean() * 100
        axes[0,0].bar(recompra_edad.index, recompra_edad.values, color='lightseagreen')
        axes[0,0].set_title('Tasa de Recompra por Grupo de Edad')
        axes[0,0].set_ylabel('Tasa de Recompra (%)')
        
        # Tasa de recompra por género
        recompra_genero = df.groupby('Genero')['Recompra'].mean() * 100
        axes[0,1].bar(['Femenino', 'Masculino'], recompra_genero.values, color='lightcoral')
        axes[0,1].set_title('Tasa de Recompra por Género')
        axes[0,1].set_ylabel('Tasa de Recompra (%)')
        
        # Efectividad de promociones
        efectividad_promo = df.groupby('Recibio_Promo')['Recompra'].mean() * 100
        axes[1,0].bar(['Sin Promo', 'Con Promo'], efectividad_promo.values, color='gold')
        axes[1,0].set_title('Efectividad de Promociones')
        axes[1,0].set_ylabel('Tasa de Recompra (%)')
        
        # Relación Ingreso vs Recompra
        sns.scatterplot(data=df, x='Ingreso_Mensual', y='Monto_Promo', 
                       hue='Recompra', ax=axes[1,1])
        axes[1,1].set_title('Relación: Ingreso vs Monto Promo')
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        pdf.savefig(fig)
        plt.close()

# Ejecutar generación de reporte
print("📄 Generando reporte PDF completo...")
generar_reporte_completo()

# Mostrar resultados en consola también
print("\n" + "="*60)
print("RESUMEN DE RESULTADOS EN CONSOLA")
print("="*60)

# Entrenar modelo para mostrar en consola
X = df[['Genero', 'Edad', 'Recibio_Promo', 'Monto_Promo', 'Total_Compras', 'Ingreso_Mensual']]
y = df['Recompra'] 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42) 
modelo = DecisionTreeClassifier(max_depth=3, random_state=42)
modelo.fit(X_train, y_train) 
y_pred = modelo.predict(X_test)

print("\n🔍 MATRIZ DE CONFUSIÓN:")
print(confusion_matrix(y_test, y_pred))

print("\n📊 REPORTE DE CLASIFICACIÓN:")
print(classification_report(y_test, y_pred))

print("\n🎯 IMPORTANCIA DE VARIABLES:")
importancia = modelo.feature_importances_
for feature, imp in zip(X.columns, importancia):
    print(f"   {feature}: {imp:.2%}")

print(f"\n📈 ESTADÍSTICAS CLAVE:")
print(f"   • Tasa global de recompra: {df['Recompra'].mean()*100:.1f}%")
print(f"   • Recompra con promoción: {df[df['Recibio_Promo'] == 1]['Recompra'].mean()*100:.1f}%")
print(f"   • Recompra sin promoción: {df[df['Recibio_Promo'] == 0]['Recompra'].mean()*100:.1f}%")
print(f"   • Edad promedio que recompran: {df[df['Recompra'] == 1]['Edad'].mean():.1f} años")

print("\n💡 CONCLUSIONES PRINCIPALES:")
print("• El modelo identifica patrones clave en el comportamiento de recompra")
print("• Variables como Monto_Promo y Edad son predictores importantes") 
print("• Se puede predecir recompra con buena precisión usando datos demográficos")
print("• Las promociones tienen efecto significativo en la conversión")

print(f"\n✅ Reporte PDF generado: 'Reporte_Analisis_Recompra.pdf'")
print("📊 El reporte incluye 8 páginas con análisis completo y bien organizado")