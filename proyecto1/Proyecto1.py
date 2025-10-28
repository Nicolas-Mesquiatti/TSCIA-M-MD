import pandas as pd
import os
import math
from tabulate import tabulate

# Carpeta base
BASE = os.path.expanduser(r"~")
# Carpeta del proyecto (ruta fija)
CARPETA = r"D:\Desarrollo de sistemas\bd-ejercicio\proyecto1"


# Helpers para campos ID y generación de nuevos IDs
def is_id_field(field_name: str) -> bool:
    """Devuelve True si el nombre del campo parece ser un identificador (ej. 'id', 'id_cliente', 'ID')."""
    if not isinstance(field_name, str):
        return False
    n = field_name.strip().lower()
    # Reglas simples: empieza por 'id' o contiene 'id_' o termina en '_id' o es exactamente 'id'
    return n == "id" or n.startswith("id") or n.startswith("id_") or n.endswith("_id") or ("id" in n and n.startswith("id"))


def get_main_id_field(registro: dict) -> str:
    """Encuentra el campo ID principal de un registro."""
    id_fields = [f for f in registro.keys() if is_id_field(f)]
    # Preferir campos que empiecen con 'id' seguido de algo
    for field in id_fields:
        if field.lower().startswith('id_') or field.lower() == 'id':
            return field
    # Si no encuentra, usar el primer campo ID
    return id_fields[0] if id_fields else None


def get_modifiable_fields(registro: dict) -> list:
    """Devuelve la lista de campos que pueden modificarse (excluye campos id)."""
    return [f for f in registro.keys() if not is_id_field(f)]


def generate_new_id(tabla: list, id_field: str):
    """Intenta generar un nuevo id entero a partir del máximo existente + 1.
    Si no puede, devuelve la longitud actual (como fallback) o cadena vacía si no aplica.
    """
    try:
        valores = [r.get(id_field) for r in tabla if id_field in r]
        nums = []
        for v in valores:
            try:
                nums.append(int(float(v)))  # Convertir a float primero y luego a int
            except Exception:
                # Ignorar valores no convertibles
                pass
        if nums:
            return max(nums) + 1
        else:
            return len(tabla) + 1
    except Exception:
        return ""

# Leer CSV y convertir en diccionarios ---
def cargar_tablas():
    def read_csv_records(fname):
        ruta = os.path.join(CARPETA, fname)
        if not os.path.exists(ruta):
            print(f" Advertencia: archivo no encontrado: {ruta} -> se usará tabla vacía.")
            return []
        try:
            return pd.read_csv(ruta).to_dict(orient="records")
        except Exception as e:
            print(f" Error leyendo {ruta}: {e}")
            return []

    mapping = {
        "clientes": "clientes.csv",
        "localidades": "localidades.csv",
        "provincias": "provincias.csv",
        "productos": "productos.csv",
        "rubros": "rubros.csv",
        "sucursales": "sucursales.csv",
        "facturaenc": "facturaenc.csv",
        "facturadet": "facturadet.csv",
        "ventas": "ventas.csv",
        "proveedores": "proveedores.csv",
    }

    tablas = {}
    for key, fname in mapping.items():
        tablas[key] = read_csv_records(fname)

    return tablas


def guardar_todo(tablas):
    """Guarda cada tabla del diccionario en CARPETA con nombre clave.csv"""
    print("\n Guardando todos los cambios (CSV)...")
    if not os.path.isdir(CARPETA):
        os.makedirs(CARPETA, exist_ok=True)
    for key, tabla in tablas.items():
        fname = f"{key}.csv"
        ruta = os.path.join(CARPETA, fname)
        try:
            pd.DataFrame(tabla).to_csv(ruta, index=False)
            print(f" Guardado: {ruta}")
        except Exception as e:
            print(f" Error guardando {ruta}: {e}")
    print(" Archivos CSV actualizados correctamente.\n")


def exportar_tabla_json(tabla, nombre):
    """Exporta una tabla (lista de dicts) a JSON limpiando tipos no serializables
    y reemplazando NaN/NA/NaT/inf por JSON null.
    """
    import json
    import math
    import numpy as np
    import pandas as pd

    ruta = os.path.join(CARPETA, f"{nombre}.json")

    def sanitize_val(v):
        # Manejar pandas/NumPy NA/NaN/NaT -> None
        try:
            if pd.isna(v):
                return None
        except Exception:
            pass

        # Numpy types -> nativos
        if isinstance(v, (np.integer,)):
            return int(v)
        if isinstance(v, (np.floating,)):
            f = float(v)
            if math.isnan(f) or math.isinf(f):
                return None
            return f
        if isinstance(v, (np.bool_,)):
            return bool(v)
        if isinstance(v, (np.ndarray,)):
            # convertir arrays a listas sanitizadas
            return [sanitize_val(x) for x in v.tolist()]

        # pandas Timestamp / datetime -> ISO string
        try:
            if hasattr(v, "isoformat"):
                return v.isoformat()
        except Exception:
            pass

        # Valores ya serializables (str, int, bool, None)
        return v

    safe = []
    for rec in tabla:
        if not isinstance(rec, dict):
            safe.append(rec)
            continue
        clean = {}
        for k, v in rec.items():
            clean[k] = sanitize_val(v)
        safe.append(clean)

    try:
        # json.dump escribirá None como null
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(safe, f, ensure_ascii=False, indent=2)
        print(f" Tabla '{nombre}' exportada a {ruta}")
    except Exception as e:
        print(" Error exportando a JSON:", e)


def guardar_todo_json(tablas):
    """Guarda todas las tablas en archivos JSON en CARPETA."""
    print("\n Guardando todos los cambios (JSON)...")
    for nombre, tabla in tablas.items():
        exportar_tabla_json(tabla, nombre)
    print(" Archivos JSON actualizados correctamente.\n")


def normalize_id_value(value):
    """Normaliza un valor de ID para comparación, convirtiendo a float y luego a int si es posible."""
    if value is None or value == '' or value == '-':
        return None
    try:
        # Convertir a float primero y luego verificar si es entero
        float_val = float(value)
        if float_val.is_integer():
            return int(float_val)
        return float_val
    except (ValueError, TypeError):
        return str(value).strip()


# Mostrar tabla con formato organizado usando tabulate - MODIFICADA
def mostrar_tabla(tabla, nombre):
    print(f"\n{'='*80}")
    print(f"📊 TABLA: {nombre.upper()} ({len(tabla)} registros)")
    print(f"{'='*80}")
    
    if not tabla:
        print("❌ La tabla está vacía")
        return
    
    # Convertir a DataFrame para mejor manejo
    df = pd.DataFrame(tabla)
    
    # Crear una copia para mostrar, normalizando los valores numéricos
    df_display = df.copy()
    
    # Normalizar valores numéricos para mostrar sin .0 si son enteros
    for col in df_display.columns:
        if is_id_field(col) or is_numeric_field(col):
            df_display[col] = df_display[col].apply(lambda x: 
                int(float(x)) if x != '' and x is not None and str(x).replace('.', '').replace('-', '').isdigit() and float(x).is_integer() 
                else x
            )
    
    # Reemplazar valores nulos o vacíos para mejor visualización
    df_display = df_display.fillna('').replace('', '-')
    
    # MOSTRAR SIN ÍNDICE AUTOMÁTICO - solo los IDs reales de la base de datos
    print(tabulate(df_display, headers='keys', tablefmt='grid', showindex=False, numalign='center', stralign='left'))
    print(f"{'='*80}")


# Menú de selección 
def menu():
    tablas = cargar_tablas()

    while True:
        nombres = list(tablas.keys())
        print("\n" + "="*50)
        print(" SISTEMA DE GESTIÓN DE BASE DE DATOS")
        
        print("\n📋 Tablas disponibles:")
        for i, nombre in enumerate(nombres, start=1):
            count = len(tablas[nombre])
            print(f"  {i}. {nombre:15} ({count} registros)")

        # Opciones globales
        print(f"\n💾 Opciones globales:")
        print(f"  {len(nombres) + 1}. Guardar todo (CSV)")
        print(f"  {len(nombres) + 2}. Guardar todo (JSON)")
        print(f"  {len(nombres) + 3}. Salir")

        try:
            opcion = int(input(f"\n🎯 Elige una tabla por número (1-{len(nombres)}): "))
        except ValueError:
            print("❌ Opción inválida. Ingresa un número.")
            continue

        # Manejar opciones globales
        if opcion == len(nombres) + 1:
            guardar_todo(tablas)
            continue

        if opcion == len(nombres) + 2:
            guardar_todo_json(tablas)
            continue

        if opcion == len(nombres) + 3:
            print(" Saliendo del programa...")
            break

        if opcion < 1 or opcion > len(nombres):
            print("❌ Número fuera de rango.")
            continue

        nombre_tabla = nombres[opcion - 1]
        tabla = tablas[nombre_tabla]
        mostrar_tabla(tabla, nombre_tabla)

        # Submenú por tabla
        while True:
            print(f"\n🛠️  OPCIONES PARA: {nombre_tabla.upper()}")
            # Encontrar el campo ID principal para mostrar en los mensajes
            id_field = None
            if tabla:
                id_field = get_main_id_field(tabla[0])
            
            accion = input("(A)gregar / (M)odificar / (B)orrar / (E)xportar / (V)olver: ").strip().lower()

            if accion == "v":
                break

            elif accion == "a":
                # Agregar: no pedir campos identificadores (id)
                nuevo = {}
                campos = list(tabla[0].keys()) if tabla else []
                for campo in campos:
                    if is_id_field(campo):
                        # Generar id automáticamente si es posible
                        nuevo[campo] = generate_new_id(tabla, campo)
                    else:
                        raw = input(f"📝 Ingrese {campo}: ")
                        nuevo[campo] = parse_input_value(campo, raw)
                tabla.append(nuevo)
                if id_field and id_field in nuevo:
                    print(f"✅ Registro agregado con {id_field} {nuevo[id_field]}")
                else:
                    print("✅ Registro agregado")
                mostrar_tabla(tabla, nombre_tabla)

                # Preguntar si se desea guardar la tabla en CSV/JSON/both inmediatamente
                guardar_choice = input("💾 Guardar cambios para esta tabla ahora? (C)SV / (J)SON / (B)oth / (N)o: ").strip().lower()
                if guardar_choice == 'c':
                    pd.DataFrame(tabla).to_csv(os.path.join(CARPETA, f"{nombre_tabla}.csv"), index=False)
                    print("✅ Guardado CSV de la tabla.")
                elif guardar_choice == 'j':
                    exportar_tabla_json(tabla, nombre_tabla)
                elif guardar_choice == 'b':
                    pd.DataFrame(tabla).to_csv(os.path.join(CARPETA, f"{nombre_tabla}.csv"), index=False)
                    exportar_tabla_json(tabla, nombre_tabla)

            elif accion == "m":
                if not id_field:
                    print("❌ No se puede identificar el campo ID para modificar")
                    continue
                    
                try:
                    # Pedir el ID real de la base de datos, no el índice automático
                    id_valor = input(f"🔧 Ingrese el {id_field} del registro a modificar: ").strip()
                    # Buscar el registro por el ID real usando comparación normalizada
                    registro_idx = None
                    for idx, registro in enumerate(tabla):
                        registro_id_valor = registro.get(id_field, '')
                        # Normalizar ambos valores para comparación
                        if normalize_id_value(registro_id_valor) == normalize_id_value(id_valor):
                            registro_idx = idx
                            break
                    
                    if registro_idx is None:
                        print(f"❌ No se encontró registro con {id_field} = {id_valor}")
                        continue
                        
                except ValueError:
                    print("❌ Ingrese un valor válido.")
                    continue

                if 0 <= registro_idx < len(tabla):
                    campos_mod = get_modifiable_fields(tabla[registro_idx])
                    if not campos_mod:
                        print("ℹ️  No hay campos modificables en este registro.")
                        continue

                    print("📝 Campos modificables:")
                    for i_c, campo in enumerate(campos_mod, start=1):
                        valor_actual = tabla[registro_idx].get(campo, 'N/A')
                        # Mostrar valor normalizado
                        valor_normalizado = normalize_id_value(valor_actual)
                        if valor_normalizado is not None:
                            print(f"  {i_c}. {campo} = {valor_normalizado}")
                        else:
                            print(f"  {i_c}. {campo} = {valor_actual}")
                    print("  T. Modificar todos los campos anteriores")
                    elec = input("🎯 Elija el número del campo a modificar (o 'T'): ").strip().lower()
                    if elec == 't':
                        for campo in campos_mod:
                            valor_actual = tabla[registro_idx].get(campo, 'N/A')
                            valor_normalizado = normalize_id_value(valor_actual)
                            if valor_normalizado is not None:
                                valor = input(f"📝 {campo} [{valor_normalizado}]: ")
                            else:
                                valor = input(f"📝 {campo} [{valor_actual}]: ")
                            if valor:
                                tabla[registro_idx][campo] = parse_input_value(campo, valor)
                    else:
                        try:
                            sel = int(elec) - 1
                        except ValueError:
                            print("❌ Ingrese un número válido o 'T'.")
                            continue
                        if 0 <= sel < len(campos_mod):
                            campo = campos_mod[sel]
                            valor_actual = tabla[registro_idx].get(campo, 'N/A')
                            valor_normalizado = normalize_id_value(valor_actual)
                            if valor_normalizado is not None:
                                valor = input(f"📝 {campo} [{valor_normalizado}]: ")
                            else:
                                valor = input(f"📝 {campo} [{valor_actual}]: ")
                            if valor:
                                tabla[registro_idx][campo] = parse_input_value(campo, valor)
                        else:
                            print("❌ Número de campo inválido.")

                    print("✅ Registro modificado.")
                    mostrar_tabla(tabla, nombre_tabla)

                    # Opciones de guardado al modificar
                    guardar_choice = input("💾 Guardar cambios para esta tabla ahora? (C)SV / (J)SON / (B)oth / (N)o: ").strip().lower()
                    if guardar_choice == 'c':
                        pd.DataFrame(tabla).to_csv(os.path.join(CARPETA, f"{nombre_tabla}.csv"), index=False)
                        print("✅ Guardado CSV de la tabla.")
                    elif guardar_choice == 'j':
                        exportar_tabla_json(tabla, nombre_tabla)
                    elif guardar_choice == 'b':
                        pd.DataFrame(tabla).to_csv(os.path.join(CARPETA, f"{nombre_tabla}.csv"), index=False)
                        exportar_tabla_json(tabla, nombre_tabla)

                else:
                    print("❌ ID fuera de rango.")

            elif accion == "b":
                if not id_field:
                    print("❌ No se puede identificar el campo ID para borrar")
                    continue
                    
                try:
                    # Pedir el ID real de la base de datos, no el índice automático
                    id_valor = input(f"🗑️  Ingrese el {id_field} del registro a borrar: ").strip()
                    # Buscar el registro por el ID real usando comparación normalizada
                    registro_idx = None
                    for idx, registro in enumerate(tabla):
                        registro_id_valor = registro.get(id_field, '')
                        # Normalizar ambos valores para comparación
                        if normalize_id_value(registro_id_valor) == normalize_id_value(id_valor):
                            registro_idx = idx
                            break
                    
                    if registro_idx is None:
                        print(f"❌ No se encontró registro con {id_field} = {id_valor}")
                        continue
                        
                except ValueError:
                    print("❌ Ingrese un valor válido.")
                    continue

                if 0 <= registro_idx < len(tabla):
                    # No borrar/alterar campos id: vaciar solo campos modificables
                    campos_no_id = get_modifiable_fields(tabla[registro_idx])
                    for campo in campos_no_id:
                        tabla[registro_idx][campo] = ""
                    print(f"✅ Registro {id_field} {id_valor} vaciado (campos no id).")
                    mostrar_tabla(tabla, nombre_tabla)

                    # Preguntar guardar tras borrar/vaciar campos
                    guardar_choice = input("💾 Guardar cambios para esta tabla ahora? (C)SV / (J)SON / (B)oth / (N)o: ").strip().lower()
                    if guardar_choice == 'c':
                        pd.DataFrame(tabla).to_csv(os.path.join(CARPETA, f"{nombre_tabla}.csv"), index=False)
                        print("✅ Guardado CSV de la tabla.")
                    elif guardar_choice == 'j':
                        exportar_tabla_json(tabla, nombre_tabla)
                    elif guardar_choice == 'b':
                        pd.DataFrame(tabla).to_csv(os.path.join(CARPETA, f"{nombre_tabla}.csv"), index=False)
                        exportar_tabla_json(tabla, nombre_tabla)
                else:
                    print("❌ ID fuera de rango.")

            elif accion == "e":
                # Exportar tabla a JSON
                exportar_tabla_json(tabla, nombre_tabla)
                print("✅ Exportación completada.")

            else:
                print("❌ Acción no válida. Use A, M, B, E o V")


# Helpers nuevos: detectar campos numéricos y parsear entradas de usuario
def is_numeric_field(field_name: str) -> bool:
    n = (field_name or "").strip().lower()
    keywords = ("precio", "importe", "valor", "stock", "cantidad", "qty", "monto", "total", "cost", "coste", "id_")
    return any(k in n for k in keywords)


def parse_input_value(field_name: str, value: str):
    """Convierte la entrada (string) a int/float/None según el nombre del campo y contenido."""
    if value is None:
        return pd.NA
    v = str(value).strip()
    if v == "":
        return pd.NA
    
    # Si el campo es numérico o es un campo ID, intentar convertir a número
    if is_numeric_field(field_name) or is_id_field(field_name):
        # quitar símbolos comunes (moneda, espacios, comas)
        cleaned = v.replace("$", "").replace("k", "000").replace("K", "000").replace(",", "").strip()
        
        try:
            # Convertir a float primero
            float_val = float(cleaned)
            # Si es un número entero (sin parte decimal), devolver como int
            if float_val.is_integer():
                return int(float_val)
            if math.isfinite(float_val):
                return float_val
            return pd.NA
        except Exception:
            # Si no se puede convertir, devolver el string original
            return v
    
    # Si no es numérico devolver el string
    return v


if __name__ == "__main__":
    # Verificar si tabulate está instalado
    try:
        from tabulate import tabulate
    except ImportError:
        print("❌ Error: La librería 'tabulate' no está instalada.")
        print("💡 Instálala con: pip install tabulate")
        exit(1)
    
    menu()
    
    
    
    
    
    
    # GENERACION DE INFORME 
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os
import math
from datetime import datetime

def generar_informe_explicativo():
    """Genera un PDF explicativo del sistema de gestión de base de datos"""
    
    with PdfPages('Informe_Sistema_Gestion_BD.pdf') as pdf:
        
        # Página 1: Portada
        fig = plt.figure(figsize=(11.69, 8.27))
        plt.axis('off')
        
        plt.text(0.5, 0.7, 'INFORME EXPLICATIVO', 
                ha='center', va='center', fontsize=24, fontweight='bold')
        plt.text(0.5, 0.6, 'SISTEMA DE GESTIÓN DE BASE DE DATOS', 
                ha='center', va='center', fontsize=18, style='italic')
        plt.text(0.5, 0.5, 'Análisis Técnico y Funcional', 
                ha='center', va='center', fontsize=14)
        
        # Información del sistema
        info_texto = f"""
        DESCRIPCIÓN GENERAL:
        • Sistema completo de gestión de bases de datos en CSV/JSON
        • Interfaz de línea de comandos interactiva
        • Soporte para múltiples tablas relacionadas
        • Funciones CRUD completas (Crear, Leer, Actualizar, Eliminar)
        
        CARACTERÍSTICAS PRINCIPALES:
        • Gestión automática de campos ID
        • Exportación a múltiples formatos
        • Validación y normalización de datos
        • Interfaz intuitiva con menús jerárquicos
        
        Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """
        
        plt.text(0.1, 0.3, info_texto, ha='left', va='top', fontsize=11,
                bbox=dict(boxstyle="round,pad=1", facecolor="lightblue", alpha=0.7))
        
        pdf.savefig(fig)
        plt.close()
        
        # Página 2: Arquitectura del Sistema
        fig = plt.figure(figsize=(11.69, 8.27))
        plt.axis('off')
        
        plt.text(0.5, 0.95, 'ARQUITECTURA DEL SISTEMA', 
                ha='center', va='center', fontsize=18, fontweight='bold')
        
        arquitectura_texto = """
        COMPONENTES PRINCIPALES:
        
        1. GESTIÓN DE ARCHIVOS
           • Carga automática de tablas desde archivos CSV
           • Exportación a formatos CSV y JSON
           • Manejo robusto de errores de archivos
           • Creación automática de directorios
        
        2. GESTIÓN DE DATOS
           • Detección automática de campos ID
           • Generación inteligente de nuevos IDs
           • Normalización de valores numéricos
           • Validación y parsing de entradas
        
        3. INTERFAZ DE USUARIO
           • Menú principal con lista de tablas
           • Submenús específicos por tabla
           • Operaciones CRUD individuales
           • Confirmaciones de guardado
        
        4. FUNCIONALIDADES AVANZADAS
           • Detección de campos modificables
           • Comparación normalizada de IDs
           • Sanitización de datos para JSON
           • Formateo tabular de salida
        
        ESTRUCTURA DE DATOS:
        • Diccionario principal: tablas['nombre_tabla'] = lista_de_registros
        • Cada registro: diccionario con campos->valores
        • Soporte para tipos mixtos (strings, números, nulos)
        """
        
        plt.text(0.1, 0.75, arquitectura_texto, ha='left', va='top', fontsize=10,
                bbox=dict(boxstyle="round,pad=1", facecolor="lightgreen", alpha=0.7))
        
        # Diagrama conceptual simple
        diagrama_texto = """
        FLUJO DE DATOS:
        
        Archivos CSV → Diccionario Python → Operaciones CRUD → Archivos CSV/JSON
              ↑               ↑                   ↑                 ↑
           Carga           Memoria            Modificación      Persistencia
           Inicial        Principal            Usuario          Cambios
        
        MENÚ JERÁRQUICO:
        
        Menú Principal → Selección Tabla → Submenú CRUD → Guardado
              ↓                   ↓              ↓            ↓
          Lista tablas        Tabla específica  A/M/B/E    Confirmación
        """
        
        plt.text(0.1, 0.3, diagrama_texto, ha='left', va='top', fontsize=10,
                bbox=dict(boxstyle="round,pad=1", facecolor="lightyellow", alpha=0.7))
        
        pdf.savefig(fig)
        plt.close()
        
        # Página 3: Funciones Helper Explicadas
        fig = plt.figure(figsize=(11.69, 8.27))
        plt.axis('off')
        
        plt.text(0.5, 0.95, 'FUNCIONES HELPER Y UTILIDADES', 
                ha='center', va='center', fontsize=18, fontweight='bold')
        
        helpers_texto = """
        FUNCIONES PRINCIPALES DE IDENTIFICACIÓN:
        
        is_id_field(field_name):
        • Detecta campos que son identificadores
        • Reglas: empieza con 'id', contiene 'id_', termina con '_id'
        • Ejemplos: 'id', 'id_cliente', 'producto_id', 'ID'
        
        get_main_id_field(registro):
        • Encuentra el campo ID principal de un registro
        • Prioriza campos que empiezan con 'id_' o son exactamente 'id'
        
        get_modifiable_fields(registro):
        • Devuelve campos que pueden modificarse (excluye IDs)
        • Permite operaciones seguras de modificación
        
        GENERACIÓN Y NORMALIZACIÓN:
        
        generate_new_id(tabla, id_field):
        • Genera nuevo ID como máximo existente + 1
        • Maneja conversión robusta de tipos numéricos
        • Fallback a longitud actual si hay errores
        
        normalize_id_value(value):
        • Normaliza valores ID para comparación consistente
        • Convierte a float→int si es posible
        • Maneja valores nulos, vacíos y strings
        
        is_numeric_field(field_name):
        • Detecta campos que probablemente son numéricos
        • Keywords: 'precio', 'stock', 'cantidad', 'monto', 'total'
        
        parse_input_value(field_name, value):
        • Convierte entrada de usuario al tipo apropiado
        • Limpia símbolos de moneda, comas, etc.
        • Convierte a int/float según el campo
        """
        
        plt.text(0.1, 0.7, helpers_texto, ha='left', va='top', fontsize=9,
                bbox=dict(boxstyle="round,pad=1", facecolor="lightcoral", alpha=0.7))
        
        pdf.savefig(fig)
        plt.close()
        
        # Página 4: Gestión de Archivos y Persistencia
        fig = plt.figure(figsize=(11.69, 8.27))
        plt.axis('off')
        
        plt.text(0.5, 0.95, 'GESTIÓN DE ARCHIVOS Y PERSISTENCIA', 
                ha='center', va='center', fontsize=18, fontweight='bold')
        
        archivos_texto = """
        FUNCIONES DE CARGA:
        
        cargar_tablas():
        • Carga todas las tablas definidas en el mapping
        • Maneja archivos faltantes creando tablas vacías
        • Convierte DataFrames pandas a listas de diccionarios
        • Mapping predefinido para 10 tablas diferentes
        
        TABLAS SOPORTADAS:
        • clientes, localidades, provincias, productos
        • rubros, sucursales, facturaenc, facturadet
        • ventas, proveedores
        
        FUNCIONES DE GUARDADO:
        
        guardar_todo(tablas):
        • Guarda todas las tablas en archivos CSV
        • Crea directorios si no existen
        • Manejo robusto de errores de escritura
        
        guardar_todo_json(tablas):
        • Exporta todas las tablas a formato JSON
        • Usa sanitización para tipos no serializables
        • Maneja NaN/NaT/inf convirtiéndolos a null
        
        exportar_tabla_json(tabla, nombre):
        • Exporta tabla individual a JSON
        • Sanitiza valores: pandas NA → None, numpy → nativos
        • Convierte timestamps a formato ISO
        • Encoding UTF-8 con indentación para legibilidad
        
        CARACTERÍSTICAS DE PERSISTENCIA:
        • Guardado automático tras operaciones CRUD
        • Opciones: CSV, JSON, o ambos
        • Confirmación de usuario antes de guardar
        • Mensajes de estado claros
        """
        
        plt.text(0.1, 0.7, archivos_texto, ha='left', va='top', fontsize=9,
                bbox=dict(boxstyle="round,pad=1", facecolor="lightseagreen", alpha=0.7))
        
        pdf.savefig(fig)
        plt.close()
        
        # Página 5: Interfaz de Usuario y Navegación
        fig = plt.figure(figsize=(11.69, 8.27))
        plt.axis('off')
        
        plt.text(0.5, 0.95, 'INTERFAZ DE USUARIO Y NAVEGACIÓN', 
                ha='center', va='center', fontsize=18, fontweight='bold')
        
        interfaz_texto = """
        ESTRUCTURA DE MENÚS:
        
        MENÚ PRINCIPAL:
        • Lista numerada de todas las tablas disponibles
        • Muestra conteo de registros por tabla
        • Opciones globales: Guardar todo (CSV/JSON), Salir
        • Validación de entrada numérica
        
        SUBMENÚ POR TABLA:
        • (A)gregar: Crea nuevo registro con ID automático
        • (M)odificar: Edita campos existentes por ID
        • (B)orrar: Vacía campos no-ID (preserva estructura)
        • (E)xportar: Exporta tabla individual a JSON
        • (V)olver: Regresa al menú principal
        
        FUNCIONALIDADES DE VISUALIZACIÓN:
        
        mostrar_tabla(tabla, nombre):
        • Muestra tabla formateada con tabulate
        • Normaliza valores numéricos (elimina .0 decimal)
        • Reemplaza valores vacíos/nulos por '-'
        • Oculta índices automáticos, muestra solo IDs reales
        • Encabezados claros con conteo de registros
        
        EXPERIENCIA DE USUARIO:
        • Mensajes descriptivos con emojis
        • Validación en tiempo real
        • Confirmaciones antes de acciones destructivas
        • Feedback inmediato de operaciones
        • Opciones de guardado flexibles
        """
        
        plt.text(0.1, 0.7, interfaz_texto, ha='left', va='top', fontsize=9,
                bbox=dict(boxstyle="round,pad=1", facecolor="gold", alpha=0.7))
        
        pdf.savefig(fig)
        plt.close()
        
        # Página 6: Operaciones CRUD Detalladas
        fig = plt.figure(figsize=(11.69, 8.27))
        plt.axis('off')
        
        plt.text(0.5, 0.95, 'OPERACIONES CRUD DETALLADAS', 
                ha='center', va='center', fontsize=18, fontweight='bold')
        
        crud_texto = """
        AGREGAR (A):
        1. Genera automáticamente nuevo ID
        2. Solicita valores para campos no-ID
        3. Parsea entradas según tipo de campo
        4. Agrega registro a la tabla en memoria
        5. Muestra tabla actualizada
        6. Ofrece opciones de guardado
        
        MODIFICAR (M):
        1. Solicita ID del registro a modificar
        2. Busca usando comparación normalizada
        3. Muestra campos modificables con valores actuales
        4. Permite modificar campo individual o todos
        5. Actualiza solo campos con nuevos valores
        6. Ofrece opciones de guardado
        
        BORRAR (B):
        1. Solicita ID del registro a "borrar"
        2. En lugar de eliminar, vacía campos no-ID
        3. Preserva campos ID y estructura del registro
        4. Mantiene integridad referencial
        5. Ofrece opciones de guardado
        
        EXPORTAR (E):
        1. Exporta tabla actual a JSON
        2. Aplica sanitización completa
        3. Mantiene estructura de datos original
        
        CARACTERÍSTICAS DE SEGURIDAD:
        • No se permiten modificaciones en campos ID
        • Validación de existencia de registros
        • Preservación de estructura de datos
        • Confirmaciones antes de guardar
        """
        
        plt.text(0.1, 0.7, crud_texto, ha='left', va='top', fontsize=9,
                bbox=dict(boxstyle="round,pad=1", facecolor="lightpink", alpha=0.7))
        
        pdf.savefig(fig)
        plt.close()
        
        # Página 7: Manejo de Errores y Robustez
        fig = plt.figure(figsize=(11.69, 8.27))
        plt.axis('off')
        
        plt.text(0.5, 0.95, 'MANEJO DE ERRORES Y ROBUSTEZ', 
                ha='center', va='center', fontsize=18, fontweight='bold')
        
        errores_texto = """
        ESTRATEGIAS DE MANEJO DE ERRORES:
        
        1. ARCHIVOS:
           • Verifica existencia de archivos antes de cargar
           • Crea tablas vacías para archivos faltantes
           • Maneja excepciones de lectura/escritura
           • Proporciona mensajes de error descriptivos
        
        2. DATOS:
           • Conversión segura de tipos numéricos
           • Manejo de valores nulos/vacíos
           • Normalización para comparaciones
           • Parsing robusto de entradas de usuario
        
        3. INTERFAZ:
           • Validación de entradas numéricas
           • Manejo de opciones inválidas
           • Verificación de rangos y existencia
           • Recuperación graceful de errores
        
        4. SERIALIZACIÓN:
           • Sanitización de tipos no serializables
           • Manejo de valores especiales (NaN, inf)
           • Conversión de tipos numpy/pandas
           • Encoding UTF-8 explícito
        
        CARACTERÍSTICAS DE ROBUSTEZ:
        • El sistema nunca crashea por datos inválidos
        • Mensajes de error informativos
        • Estado consistente tras errores
        • Capacidad de recuperación
        • Preservación de datos existentes
        """
        
        plt.text(0.1, 0.7, errores_texto, ha='left', va='top', fontsize=9,
                bbox=dict(boxstyle="round,pad=1", facecolor="plum", alpha=0.7))
        
        pdf.savefig(fig)
        plt.close()
        
        # Página 8: Conclusión y Características Destacadas
        fig = plt.figure(figsize=(11.69, 8.27))
        plt.axis('off')
        
        plt.text(0.5, 0.95, 'CONCLUSIÓN Y CARACTERÍSTICAS DESTACADAS', 
                ha='center', va='center', fontsize=18, fontweight='bold')
        
        conclusion_texto = """
        RESUMEN DEL SISTEMA:
        
        FORTALEZAS PRINCIPALES:
        ✅ Gestión automática e inteligente de IDs
        ✅ Interfaz intuitiva con navegación jerárquica
        ✅ Soporte múltiple de formatos (CSV/JSON)
        ✅ Operaciones CRUD completas y seguras
        ✅ Manejo robusto de errores y datos inválidos
        ✅ Normalización inteligente de valores
        ✅ Persistencia flexible con confirmaciones
        
        INNOVACIONES TÉCNICAS:
        • Detección automática de campos ID y numéricos
        • Generación inteligente de IDs secuenciales
        • Comparación normalizada para búsquedas
        • Sanitización completa para serialización JSON
        • Parsing contextual de entradas de usuario
        • Preservación de estructura en operaciones de borrado
        
        USO PRÁCTICO:
        • Ideal para bases de datos pequeñas/medianas
        • Perfecto para prototipado y desarrollo
        • Excelente para migraciones entre formatos
        • Útil para enseñanza de conceptos de BD
        • Flexible para personalización y extensión
        
        POTENCIALES MEJORAS:
        • Agregar validaciones de integridad referencial
        • Implementar búsquedas y filtros avanzados
        • Agregar soporte para transacciones
        • Implementar logging de operaciones
        • Agregar interfaz web o gráfica
        """
        
        plt.text(0.1, 0.7, conclusion_texto, ha='left', va='top', fontsize=9,
                bbox=dict(boxstyle="round,pad=1", facecolor="lightsteelblue", alpha=0.7))
        
        pdf.savefig(fig)
        plt.close()

# Generar el informe
print("📊 Generando informe explicativo del sistema...")
generar_informe_explicativo()
print("✅ Informe generado: 'Informe_Sistema_Gestion_BD.pdf'")
print("📄 El PDF contiene 8 páginas con análisis completo del sistema")