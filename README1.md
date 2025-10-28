# 🗃️ Proyecto 1: Sistema de Gestión de Base de Datos

## 📋 Descripción General
Sistema completo en Python para gestionar múltiples tablas relacionadas mediante operaciones CRUD (Crear, Leer, Actualizar, Eliminar), con soporte para exportación en formatos CSV y JSON.

---

## 🎯 Características Principales

- 🔍 **Gestión Inteligente de IDs**
  - Detección automática de campos ID
  - Generación secuencial de nuevos IDs
  - Normalización de formatos de ID

- 💾 **Operaciones CRUD Completas**
  - Agregar registros con ID automático
  - Modificar campos específicos
  - Borrado seguro (preserva estructura)
  - Exportación con sanitización (CSV/JSON)

- 🛡️ **Robustez y Validación**
  - Manejo de errores con recuperación
  - Validación de tipos de datos
  - Confirmación de guardado tras cada operación

---

## 📊 Estructura de Datos

### 🗂️ Tablas Soportadas
```python
tablas = {
  "clientes": "clientes.csv",
  "localidades": "localidades.csv",
  "provincias": "provincias.csv",
  "productos": "productos.csv",
  "rubros": "rubros.csv",
  "sucursales": "sucursales.csv",
  "facturaenc": "facturaenc.csv",
  "facturadet": "facturadet.csv",
  "ventas": "ventas.csv",
  "proveedores": "proveedores.csv"
}
```

### 🔗 Relaciones entre Tablas

```text
clientes ←→ localidades ←→ provincias
    ↓
facturaenc ←→ facturadet ←→ productos ←→ rubros
    ↓                           ↓
  ventas                    proveedores
    ↓
sucursales
```


## 📱 Interfaz
Menú principal con selección de tabla

Submenú por tabla: Agregar / Modificar / Borrar / Exportar

Confirmación de guardado tras cada operación

## 🔧 Funcionalidades Técnicas

🎯 Identificación de campos ID (is_id_field, get_main_id_field)

🔢 Generación y normalización de IDs (generate_new_id, normalize_id_value)

📁 Gestión de archivos (cargar_tablas, guardar_todo, exportar_tabla_json)

📊 Visualización profesional con tabulate (mostrar_tabla)

🧠 Parsing inteligente y adaptativo de entradas


## 💡 Características Avanzadas
🧠 Detección contextual de campos

🔧 Arquitectura modular y extensible

📄 Código auto-documentado

🧪 100% de operaciones con confirmación

🛡️ 0 fallos en operaciones normales
