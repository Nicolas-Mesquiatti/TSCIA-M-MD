# para ejecutar : py -m streamlit run "d:\Desarrollo de sistemas\bd-ejercicio\proyecto1\streamlit_app.py"
import streamlit as st
import pandas as pd
import pandas.api.types as pat
import os
import json
import time

# Carpeta del proyecto (ajustar si hace falta)
CARPETA = r"D:\Desarrollo de sistemas\bd-ejercicio\proyecto1"
CSV_LIST = [
    "clientes.csv", "localidades.csv", "provincias.csv", "productos.csv",
    "proveedores.csv", "rubros.csv", "sucursales.csv",
    "facturaenc.csv", "d_facturadet.csv", "ventas.csv"
]

st.set_page_config(page_title="Administrador CSV", layout="wide")


def is_id_field(colname: str) -> bool:
    n = str(colname).strip().lower()
    return n == "id" or n.startswith("id_") or n.startswith("id") or n.endswith("_id") or ("_id" in n)


@st.cache_data(ttl=60)
def load_tables():
    tablas = {}
    for f in CSV_LIST:
        ruta = os.path.join(CARPETA, f)
        key = os.path.splitext(f)[0]
        if os.path.exists(ruta):
            try:
                df = pd.read_csv(ruta, dtype=str).replace({"": pd.NA, "nan": pd.NA})
                # intentar normalizar columnas
                for col in df.columns:
                    if is_id_field(col):
                        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
                    else:
                        coerced = pd.to_numeric(df[col], errors="coerce")
                        non_na = coerced.notna().sum()
                        total = len(coerced)
                        if total > 0 and non_na / max(1, total) > 0.6:
                            # mayoría numérica -> elegir Int64 o float64
                            non_na_vals = coerced.dropna()
                            if (non_na_vals % 1 == 0).all():
                                df[col] = coerced.astype("Int64")
                            else:
                                df[col] = coerced.astype("float64")
                        else:
                            df[col] = df[col].astype("string")
                tablas[key] = df
            except Exception:
                tablas[key] = pd.DataFrame()
        else:
            tablas[key] = pd.DataFrame()
    return tablas


def save_tables(tablas):
    os.makedirs(CARPETA, exist_ok=True)
    for name, df in tablas.items():
        ruta = os.path.join(CARPETA, f"{name}.csv")
        # convertir tipos pandas a serializables al guardar
        s = df.copy()
        for c in s.columns:
            # Int64 -> convert to floats for CSV missing or to ints where possible
            if pat.is_integer_dtype(s[c].dtype):
                s[c] = s[c].astype("Int64")
            # string dtype -> convert to python str with <NA> -> ""
            if pd.api.types.is_string_dtype(s[c].dtype):
                s[c] = s[c].fillna("")
        s.to_csv(ruta, index=False)


def export_json(tablas, name):
    df = tablas[name].copy()
    # convertir NA/NaT a None y numpy/pandas tipos a nativos
    df = df.where(pd.notnull(df), None)
    records = []
    for rec in df.to_dict(orient="records"):
        clean = {}
        for k, v in rec.items():
            if v is None:
                clean[k] = None
            else:
                # pandas Int64 are python ints or numpy ints -> convertir
                try:
                    if pd.isna(v):
                        clean[k] = None
                        continue
                except Exception:
                    pass
                if hasattr(v, "item"):
                    try:
                        clean[k] = v.item()
                        continue
                    except Exception:
                        pass
                clean[k] = v
        records.append(clean)
    ruta = os.path.join(CARPETA, f"{name}.json")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def safe_rerun():
    """Intenta forzar rerun; si experimental_rerun no existe usa query params como fallback."""
    if hasattr(st, "experimental_rerun"):
        try:
            st.experimental_rerun()
        except Exception:
            st.experimental_set_query_params(_updated=str(time.time()))
    else:
        st.experimental_set_query_params(_updated=str(time.time()))


# Inicializar tablas en session_state (persistente durante la sesión)
if "tablas" not in st.session_state:
    st.session_state["tablas"] = load_tables()

st.title("Administrador de CSV (Web)")

tablas = st.session_state["tablas"]
table_names = list(tablas.keys())

col1, col2 = st.columns([1, 3])
with col1:
    selected = st.selectbox("Seleccione tabla", table_names)
    st.write("Filas:", len(tablas[selected]))
    if st.button("Guardar todos (CSV)"):
        save_tables(tablas)
        st.success("CSV guardados.")
    if st.button("Exportar tabla a JSON"):
        export_json(tablas, selected)
        st.success(f"{selected}.json creado.")

with col2:
    df = tablas[selected]
    st.subheader(selected)
    st.dataframe(df.reset_index(drop=False).rename(columns={"index": "ID"}), width="stretch")

st.markdown("---")
st.subheader("Operaciones sobre la tabla")

op = st.radio("Acción", ["Agregar", "Modificar", "Borrar (vaciar campos)"], horizontal=True)

if op == "Agregar":
    st.info("Agregar nueva fila. Si la tabla está vacía, primero asegúrate de tener los encabezados en el CSV.")
    if df.empty:
        st.warning("Tabla vacía: no se pueden generar campos automáticamente.")
    else:
        with st.form("form_add"):
            values = {}
            for c in df.columns:
                values[c] = st.text_input(c, value="")
            submitted = st.form_submit_button("Agregar")
        if submitted:
            normalized = {}
            for c, v in values.items():
                if v == "" or v is None:
                    normalized[c] = pd.NA
                else:
                    col_dtype = tablas[selected].dtypes.get(c)
                    if pat.is_integer_dtype(col_dtype):
                        try:
                            normalized[c] = int(v)
                        except Exception:
                            normalized[c] = pd.NA
                    elif pat.is_float_dtype(col_dtype):
                        try:
                            normalized[c] = float(v)
                        except Exception:
                            normalized[c] = pd.NA
                    else:
                        normalized[c] = v
            new_row = pd.DataFrame([normalized])
            # respetar dtypes cuando sea posible
            for col, dtype in tablas[selected].dtypes.items():
                try:
                    new_row[col] = new_row[col].astype(dtype)
                except Exception:
                    pass
            tablas[selected] = pd.concat([df, new_row], ignore_index=True)
            st.session_state["tablas"] = tablas
            st.success("Fila agregada.")
            safe_rerun()

elif op == "Modificar":
    if df.empty:
        st.warning("Tabla vacía: no hay registros para modificar.")
    else:
        idx = st.selectbox("Elija ID (índice 0..n-1)", list(range(len(df))))
        row = df.loc[idx]
        with st.form("form_edit"):
            newvals = {}
            for c in df.columns:
                display = "" if pd.isna(row[c]) else str(row[c])
                newvals[c] = st.text_input(c, value=display)
            submitted = st.form_submit_button("Guardar cambios")
        if submitted:
            for c, s in newvals.items():
                if s == "" or s is None:
                    tablas[selected].at[idx, c] = pd.NA
                else:
                    col_dtype = tablas[selected].dtypes.get(c)
                    if pat.is_integer_dtype(col_dtype):
                        try:
                            tablas[selected].at[idx, c] = int(s)
                        except Exception:
                            tablas[selected].at[idx, c] = pd.NA
                    elif pat.is_float_dtype(col_dtype):
                        try:
                            tablas[selected].at[idx, c] = float(s)
                        except Exception:
                            tablas[selected].at[idx, c] = pd.NA
                    else:
                        tablas[selected].at[idx, c] = s
            st.session_state["tablas"] = tablas
            st.success("Registro modificado.")
            safe_rerun()

elif op == "Borrar (vaciar campos)":
    if df.empty:
        st.warning("Tabla vacía.")
    else:
        idx = st.selectbox("Elija ID a vaciar", list(range(len(df))))
        if st.button("Vaciar campos"):
            for c in df.columns:
                tablas[selected].at[idx, c] = pd.NA
            st.session_state["tablas"] = tablas
            st.success(f"Registro {idx} vaciado.")
            safe_rerun()