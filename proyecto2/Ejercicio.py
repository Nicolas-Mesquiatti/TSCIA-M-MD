"""EJERCICIO FINAL DE REPASO 
Caso: Una cadena de gimnasios quiere predecir qué clientes tienen mayor riesgo de 
cancelar su suscripción. 
Pasos sugeridos: 
 Importar y explorar datos de clientes (edad, frecuencia de asistencia, pagos, 
etc.). 
 Transformar y limpiar datos. 
 Crear modelo de clasificación (ej. árbol de decisión). 
 Evaluar modelo. 
 Visualizar resultados y entregar recomendaciones para reducir la pérdida de 
clientes. """
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix
 
 
#carga de datos

df = pd.read_csv("D:/Desarrollo de sistemas/bd-ejercicio/proyecto2/clientes_gimnasio.csv")
#print(df.info())
#print(df.describe())
print(df['Canceló'].value_counts()) # cuenta cuántos clientes cancelaron (1) y cuántos siguen activos (0):

# transformacion de datos
df['Pagos_Puntuales'] = df['Pagos_Puntuales'].map({'Sí': 1, 'No': 0})
df.dropna(inplace=True)


#Modelo de clasificación

X = df.drop('Canceló', axis=1)
y = df['Canceló']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

modelo = DecisionTreeClassifier(max_depth=4)
modelo.fit(X_train, y_train)
y_pred = modelo.predict(X_test)
print(confusion_matrix(y_test, y_pred)) # compara predicciones vs realidad
print(classification_report(y_test, y_pred))

"""classification_report:

Precision: porcentaje de predicciones correctas sobre las predicciones hechas para cada clase.

Recall: porcentaje de verdaderos positivos detectados.

F1-score: promedio armónico de precision y recall.

Support: cantidad de casos reales por clase.

Resultado: el modelo predijo correctamente todos los clientes en el set de prueba, por eso precisión, recall y F1 = 1.00."""

#Visualización del árbol de decisión

from sklearn.tree import plot_tree
import matplotlib.pyplot as plt

plt.figure(figsize=(12,8))
plot_tree(modelo, feature_names=X.columns, class_names=["Activo", "Canceló"], filled=True)
plt.show()


#Resultados 
"""Si la frecuencia de asistencia es menor o igual a 2.5 → el cliente probablemente canceló. Si la frecuencia es mayor a 2.5 → el cliente probablemente sigue activo."""
print("Recomendaciones para reducir la pérdida de clientes:")
print("1. Implementar programas de fidelización para clientes con baja asistencia.")
print("2. Ofrecer incentivos para pagos puntuales.")
print("3. Realizar encuestas para entender las razones de cancelación.")
print("4. Mejorar la experiencia del cliente en el gimnasio.")
print("5. Monitorear regularmente los patrones de asistencia y pagos.")