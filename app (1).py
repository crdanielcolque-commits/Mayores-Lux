# ============================================================
# Dashboard Mayores LUX - Streamlit
# Fuente: Google Sheets público/exportable
# Autor: Daniel Colque / Autolux
# ============================================================

import re
import io
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# -----------------------------
# Configuración general
# -----------------------------
st.set_page_config(
    page_title="Dashboard Mayores LUX",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

SHEET_ID = "1Yu1UTf6LvdGTmlUsFgmwkDHsNckUoDv1tZDK1V9V0mE"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"


CENTROS_COSTO = [
    "Vtas 0 Km",
    "Vtas Usado",
    "PPAA",
    "Repuestos",
    "Tl. Mec.",
    "Finanzas",
    "Mayorista",
    "ChapyPintu",
    "Central",
    "Administr.",
]

PCT_CENTROS = [
    "% Vtas 0 Km",
    "% Vtas Usado",
    "% PPAA",
    "% Repuestos",
    "% Tl. Mec.",
    "% Finanzas",
    "% Mayorista",
    "% ChapyPintu",
    "% Central",
    "% Administr.",
]


# -----------------------------
# CSS premium simple
# -----------------------------
st.markdown(
    """
    <style>
    .main {
        background: #0f172a;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3, h4 {
        color: #e5e7eb;
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        padding: 18px;
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 8px 22px rgba(0,0,0,0.20);
    }
    div[data-testid="stMetric"] label {
        color: #cbd5e1 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    .soft-card {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        padding: 18px;
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 12px;
    }
    .small-muted {
        color: #94a3b8;
        font-size: 0.9rem;
    }
    .ok {color:#22c55e;font-weight:700;}
    .warn {color:#f59e0b;font-weight:700;}
    .bad {color:#ef4444;font-weight:700;}
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Utilidades
# -----------------------------
def normalizar_texto(x):
    if pd.isna(x):
        return ""
    return str(x).strip()


def limpiar_numero(valor):
    """
    Convierte importes argentinos o formatos mixtos a float.
    Soporta:
    - 1.234.567,89
    - -1.234.567,89
    - 1234567.89
    - (1.234,56)
    - $ 1.234,56
    """
    if pd.isna(valor):
        return 0.0

    if isinstance(valor, (int, float, np.number)):
        return float(valor)

    s = str(valor).strip()
    if s == "":
        return 0.0

    negativo = False
    if "(" in s and ")" in s:
        negativo = True

    s = (
        s.replace("$", "")
        .replace("ARS", "")
        .replace(" ", "")
        .replace("\u00a0", "")
        .replace("(", "")
        .replace(")", "")
    )

    if s.startswith("-"):
        negativo = True
        s = s[1:]

    # Si tiene coma, asumimos decimal argentina.
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        # Si tiene muchos puntos, probablemente miles.
        if s.count(".") > 1:
            s = s.replace(".", "")

    try:
        n = float(s)
    except Exception:
        n = 0.0

    return -n if negativo else n


def form_money(x):
    try:
        x = float(x)
    except Exception:
        x = 0
    signo = "-" if x < 0 else ""
    x_abs = abs(x)
    return f"{signo}${x_abs:,.0f}".replace(",", ".")


def form_pct(x):
    try:
        return f"{float(x):.1f}%"
    except Exception:
        return "0,0%"


def clean_colnames(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def make_union(rub, srub):
    rub = normalizar_texto(rub)
    srub = normalizar_texto(srub)
    rub = rub.replace(".0", "")
    srub = srub.replace(".0", "")
    if rub == "" or srub == "":
        return ""
    return f"{rub}-{srub}"


# -----------------------------
# Mapa P&L
# -----------------------------
PNL_ROWS = [
    {"Logica": "mas", "Concepto": "Ventas", "Rubro": "4-1", "Grupo": "Margen Bruto Gestion Comercial"},
    {"Logica": "menos", "Concepto": "Descuentos sobre ventas", "Rubro": "4-2", "Grupo": "Margen Bruto Gestion Comercial"},
    {"Logica": "menos", "Concepto": "Costo de Ventas", "Rubro": "5-1", "Grupo": "Margen Bruto Gestion Comercial"},
    {"Logica": "menos", "Concepto": "Rdo. Neto Gestoria", "Rubro": "6-1 + 6-2", "Grupo": "Margen Bruto Gestion Comercial"},

    {"Logica": "menos", "Concepto": "Ajuste Costo de Reposición", "Rubro": "", "Grupo": "Margen Bruto Secundario"},
    {"Logica": "menos", "Concepto": "Costo Reacondic. y Acces.", "Rubro": "5-2", "Grupo": "Margen Bruto Secundario"},
    {"Logica": "mas", "Concepto": "Incentivos", "Rubro": "4-3", "Grupo": "Margen Bruto Secundario"},
    {"Logica": "mas", "Concepto": "Incentivo Devengado", "Rubro": "4-4", "Grupo": "Margen Bruto Secundario"},
    {"Logica": "mas", "Concepto": "Comision Consignaciones", "Rubro": "6-3", "Grupo": "Margen Bruto Secundario"},
    {"Logica": "menos", "Concepto": "Comisión Pagadas", "Rubro": "6-6", "Grupo": "Margen Bruto Secundario"},
    {"Logica": "mas", "Concepto": "Comision P/Vta Directa", "Rubro": "10-1", "Grupo": "Margen Bruto Secundario"},

    {"Logica": "menos", "Concepto": "Mermas de Inventarios", "Rubro": "5-3", "Grupo": "Otros Ingresos / Egresos"},
    {"Logica": "menos", "Concepto": "Sobrantes de Inventarios", "Rubro": "5-4", "Grupo": "Otros Ingresos / Egresos"},
    {"Logica": "menos", "Concepto": "Perdida Iva Usados", "Rubro": "5-5", "Grupo": "Otros Ingresos / Egresos"},
    {"Logica": "menos", "Concepto": "Horas no aplicadas mecanicos", "Rubro": "6-4", "Grupo": "Otros Ingresos / Egresos"},
    {"Logica": "mas", "Concepto": "Resultado Venta de PPAA MS", "Rubro": "6-5", "Grupo": "Otros Ingresos / Egresos"},
    {"Logica": "mas", "Concepto": "Ingresos Seguros y Comis Gtion Vta", "Rubro": "10-4", "Grupo": "Otros Ingresos / Egresos"},
    {"Logica": "menos", "Concepto": "Egresos Seguros", "Rubro": "11-5", "Grupo": "Otros Ingresos / Egresos"},

    {"Logica": "mas", "Concepto": "Transferencia repuestos a taller", "Rubro": "", "Grupo": "Transferencia"},
    {"Logica": "menos", "Concepto": "Comisiones sobre Ventas", "Rubro": "7-2", "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Sueldos y Cargas Sociales", "Rubro": "8-1", "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Sueldos Administración y C. Soc.", "Rubro": "8-4", "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Gastos de Atención clientes", "Rubro": "7-1", "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Servicios gratuitos y Cargos internos", "Rubro": "7-4", "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Herramientas, materiales y fletes", "Rubro": "7-6", "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Publicidad y Promoción", "Rubro": "8-2", "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Mantenimiento rodados y equipos", "Rubro": "8-3", "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Movilidad y Viáticos", "Rubro": "8-6", "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Mantenimiento Bienes de Uso", "Rubro": "8-8", "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Fuerza motriz, luz, agua y gas", "Rubro": "8-9", "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Telefonos e internet", "Rubro": "8-10", "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Serv. Limpieza", "Rubro": "8-11", "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Utiles y materiales de oficina", "Rubro": "8-12", "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Otros Gastos Fijos", "Rubro": "8-13", "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Alquileres", "Rubro": "8-14", "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Previsiones Varias", "Rubro": "8-17", "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Deudores Incobrables", "Rubro": "8-19", "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Preparación y entrega", "Rubro": "7-3", "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Seguridad y vigilancia", "Rubro": "8-20", "Grupo": "Costos Controlables"},

    {"Logica": "menos", "Concepto": "Impuestos", "Rubro": "7-5", "Grupo": "Costos No Controlables"},
    {"Logica": "menos", "Concepto": "Honorarios profesionales", "Rubro": "8-5", "Grupo": "Costos No Controlables"},
    {"Logica": "menos", "Concepto": "Recupero de Gastos Toyota", "Rubro": "8-7", "Grupo": "Costos No Controlables"},
    {"Logica": "menos", "Concepto": "Amortizaciones", "Rubro": "8-15", "Grupo": "Costos No Controlables"},
    {"Logica": "menos", "Concepto": "Seguros", "Rubro": "8-16", "Grupo": "Costos No Controlables"},
    {"Logica": "menos", "Concepto": "Impuestos y tasas", "Rubro": "8-18", "Grupo": "Costos No Controlables"},

    {"Logica": "menos", "Concepto": "Sueldos Gtes y Jefes Suc.", "Rubro": "9-1", "Grupo": "Controlables de Estructura"},
    {"Logica": "menos", "Concepto": "Sueldos Adm. Central", "Rubro": "9-2", "Grupo": "Controlables de Estructura"},
    {"Logica": "menos", "Concepto": "Prestaciones La Luz", "Rubro": "9-3", "Grupo": "Controlables de Estructura"},
    {"Logica": "menos", "Concepto": "Movilidad y Viáticos Estructura", "Rubro": "9-4", "Grupo": "Controlables de Estructura"},
    {"Logica": "menos", "Concepto": "Mantenimiento Bs Uso Central", "Rubro": "9-5", "Grupo": "Controlables de Estructura"},
    {"Logica": "menos", "Concepto": "Útiles y materiales de oficina Estructura", "Rubro": "9-6", "Grupo": "Controlables de Estructura"},
    {"Logica": "menos", "Concepto": "Serv, Energía, Suscripciones Adm Central", "Rubro": "9-7", "Grupo": "Controlables de Estructura"},
    {"Logica": "menos", "Concepto": "Alquileres Adm Central", "Rubro": "9-9", "Grupo": "Controlables de Estructura"},
    {"Logica": "menos", "Concepto": "Amortizaciones Estructura", "Rubro": "9-8", "Grupo": "Costos no Controlables de Estructura"},

    {"Logica": "mas", "Concepto": "Intereses Financiación Vehículos", "Rubro": "10-2", "Grupo": "Ingresos Financieros"},
    {"Logica": "mas", "Concepto": "Otros Ingresos Financieros", "Rubro": "10-3", "Grupo": "Ingresos Financieros"},
    {"Logica": "menos", "Concepto": "Impuestos Financiación", "Rubro": "11-1", "Grupo": "Egresos Financieros"},
    {"Logica": "menos", "Concepto": "Intereses Impositivos", "Rubro": "11-2", "Grupo": "Egresos Financieros"},
    {"Logica": "menos", "Concepto": "Comisiones y gastos bancarios", "Rubro": "11-3", "Grupo": "Egresos Financieros"},
    {"Logica": "menos", "Concepto": "Financiacion cap trab", "Rubro": "11-4", "Grupo": "Egresos Financieros"},
]


def expand_rubros(rubro_str):
    """
    Convierte '6-1 + 6-2' en ['6-1','6-2'].
    """
    if pd.isna(rubro_str) or str(rubro_str).strip() == "":
        return []
    parts = re.split(r"\s*\+\s*", str(rubro_str).strip())
    return [p.strip() for p in parts if p.strip()]


@st.cache_data(ttl=600)
def cargar_base():
    df = pd.read_csv(CSV_URL)
    df = clean_colnames(df)

    # Validaciones mínimas
    required = ["Fecha", "Parcial", "Rub", "SRub"]
    faltantes = [c for c in required if c not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas obligatorias: {faltantes}")

    # Fecha
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce", dayfirst=True)
    df["Mes"] = df["Fecha"].dt.to_period("M").astype(str)
    df["Mes_nombre"] = df["Fecha"].dt.strftime("%Y-%m")

    # Importes principales
    for c in ["Debe", "Haber", "Parcial"] + CENTROS_COSTO + PCT_CENTROS:
        if c in df.columns:
            df[c] = df[c].apply(limpiar_numero)

    # Uniones
    if "union" not in df.columns:
        df["union"] = df.apply(lambda r: make_union(r.get("Rub", ""), r.get("SRub", "")), axis=1)
    else:
        df["union"] = df["union"].apply(normalizar_texto)
        faltan_union = df["union"].eq("")
        if faltan_union.any():
            df.loc[faltan_union, "union"] = df.loc[faltan_union].apply(
                lambda r: make_union(r.get("Rub", ""), r.get("SRub", "")), axis=1
            )

    # Texto
    for c in ["Cuenta", "Nombre cuenta", "Detalle", "des res", "Detalle 2", "Sucursal", "Dpto", "Nombre del rubro"]:
        if c in df.columns:
            df[c] = df[c].apply(normalizar_texto)

    # Mapa P&L
    map_rows = []
    for row in PNL_ROWS:
        for rubro in expand_rubros(row["Rubro"]):
            map_rows.append(
                {
                    "union": rubro,
                    "Concepto_PyG": row["Concepto"],
                    "Grupo_PyG": row["Grupo"],
                    "Logica_PyG": row["Logica"],
                }
            )

    map_df = pd.DataFrame(map_rows).drop_duplicates("union")
    df = df.merge(map_df, on="union", how="left")

    df["Concepto_PyG"] = df["Concepto_PyG"].fillna("Sin clasificar")
    df["Grupo_PyG"] = df["Grupo_PyG"].fillna("Sin clasificar")
    df["Logica_PyG"] = df["Logica_PyG"].fillna("")

    return df


def filtrar_df(df):
    st.sidebar.markdown("## 🎛️ Filtros")

    meses = sorted([m for m in df["Mes"].dropna().unique()])
    mes_sel = st.sidebar.multiselect("Mes", meses, default=meses)

    sucursales = sorted([s for s in df.get("Sucursal", pd.Series(dtype=str)).dropna().unique() if s != ""])
    suc_sel = st.sidebar.multiselect("Sucursal", sucursales, default=sucursales)

    grupos = sorted([g for g in df["Grupo_PyG"].dropna().unique()])
    grupo_sel = st.sidebar.multiselect("Grupo P&L", grupos, default=grupos)

    df2 = df.copy()
    if mes_sel:
        df2 = df2[df2["Mes"].isin(mes_sel)]
    if suc_sel and "Sucursal" in df2.columns:
        df2 = df2[df2["Sucursal"].isin(suc_sel)]
    if grupo_sel:
        df2 = df2[df2["Grupo_PyG"].isin(grupo_sel)]

    return df2


def total_por_rubros(df, rubros, columna="Parcial"):
    rubros = set(rubros)
    if columna not in df.columns:
        return 0.0
    return df.loc[df["union"].isin(rubros), columna].sum()


def calcular_kpis(df, columna="Parcial"):
    ventas = total_por_rubros(df, ["4-1"], columna)
    descuentos = total_por_rubros(df, ["4-2"], columna)
    costo_ventas = total_por_rubros(df, ["5-1"], columna)
    gestoria = total_por_rubros(df, ["6-1", "6-2"], columna)

    mb_gestion = ventas + descuentos + costo_ventas + gestoria

    reacond = total_por_rubros(df, ["5-2"], columna)
    incentivos = total_por_rubros(df, ["4-3", "4-4"], columna)
    comisiones = total_por_rubros(df, ["6-3", "6-6", "10-1"], columna)
    mb_secundario = mb_gestion + reacond + incentivos + comisiones

    otros = total_por_rubros(df, ["5-3","5-4","5-5","6-4","6-5","10-4","11-5"], columna)
    utilidad_bruta = mb_secundario + otros

    costos_controlables = df.loc[df["Grupo_PyG"].eq("Costos Controlables"), columna].sum() if columna in df.columns else 0
    costos_no_controlables = df.loc[df["Grupo_PyG"].eq("Costos No Controlables"), columna].sum() if columna in df.columns else 0
    utilidad_operativa_sucursal = utilidad_bruta + costos_controlables + costos_no_controlables

    estructura_controlable = df.loc[df["Grupo_PyG"].eq("Controlables de Estructura"), columna].sum() if columna in df.columns else 0
    estructura_no_controlable = df.loc[df["Grupo_PyG"].eq("Costos no Controlables de Estructura"), columna].sum() if columna in df.columns else 0
    utilidad_operativa = utilidad_operativa_sucursal + estructura_controlable + estructura_no_controlable

    ingresos_financieros = df.loc[df["Grupo_PyG"].eq("Ingresos Financieros"), columna].sum() if columna in df.columns else 0
    egresos_financieros = df.loc[df["Grupo_PyG"].eq("Egresos Financieros"), columna].sum() if columna in df.columns else 0
    resultado_antes_imp = utilidad_operativa + ingresos_financieros + egresos_financieros

    # Impuesto ganancias no tiene rubro definido en el mapa cargado.
    impuesto_ganancias = 0
    resultado_despues_imp = resultado_antes_imp + impuesto_ganancias

    margen_bruto_pct = utilidad_bruta / ventas * 100 if ventas else 0
    controlables_pct = abs(costos_controlables) / abs(ventas) * 100 if ventas else 0

    return {
        "Ventas": ventas,
        "Margen Bruto Gestión": mb_gestion,
        "Margen Bruto Secundario": mb_secundario,
        "Utilidad Bruta": utilidad_bruta,
        "Costos Controlables": costos_controlables,
        "Costos No Controlables": costos_no_controlables,
        "Utilidad Operativa Sucursal": utilidad_operativa_sucursal,
        "Estructura Controlable": estructura_controlable,
        "Estructura No Controlable": estructura_no_controlable,
        "Utilidad Operativa": utilidad_operativa,
        "Ingresos Financieros": ingresos_financieros,
        "Egresos Financieros": egresos_financieros,
        "Resultado antes de Impuestos": resultado_antes_imp,
        "Resultado después de Impuestos": resultado_despues_imp,
        "Margen Bruto %": margen_bruto_pct,
        "Costos Controlables % ventas": controlables_pct,
    }


def pnl_table(df, columna="Parcial"):
    filas = []
    acumulado = 0.0

    def agregar(label, valor, tipo="concepto", grupo=""):
        filas.append({
            "Tipo": tipo,
            "Grupo": grupo,
            "Concepto": label,
            "Importe": valor,
            "Importe_fmt": form_money(valor),
        })

    # Construcción ordenada similar a tu cuenta de resultados
    bloques = [
        ("Margen Bruto Gestion Comercial", "Margen Bruto Gestión Comercial"),
        ("Margen Bruto Secundario", "Margen Bruto Secundario"),
        ("Otros Ingresos / Egresos", "Utilidad Bruta"),
        ("Costos Controlables", None),
        ("Costos No Controlables", "Utilidad Operativa Sucursal"),
        ("Controlables de Estructura", None),
        ("Costos no Controlables de Estructura", "Utilidad Operativa"),
        ("Ingresos Financieros", None),
        ("Egresos Financieros", "Resultado antes de Impuestos"),
    ]

    kpis = calcular_kpis(df, columna)

    for grupo, subtotal_name in bloques:
        sub = df[df["Grupo_PyG"].eq(grupo)]
        if not sub.empty:
            tmp = sub.groupby("Concepto_PyG", as_index=False)[columna].sum()
            for _, r in tmp.iterrows():
                agregar(r["Concepto_PyG"], r[columna], "concepto", grupo)

        if subtotal_name:
            agregar(subtotal_name, kpis.get(subtotal_name, 0), "subtotal", grupo)

    agregar("Resultado después de Impuestos", kpis["Resultado después de Impuestos"], "total", "")

    return pd.DataFrame(filas)


def dataframe_download(df, filename="detalle.csv"):
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Descargar CSV",
        data=csv,
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
    )


# -----------------------------
# Carga
# -----------------------------
st.title("📊 Dashboard Mayores Contables LUX")
st.markdown('<div class="small-muted">Cuenta de resultados, centros de costo, sucursales y drilldown contable.</div>', unsafe_allow_html=True)

try:
    df_raw = cargar_base()
except Exception as e:
    st.error("No pude cargar la base desde Google Sheets.")
    st.exception(e)
    st.stop()

df = filtrar_df(df_raw)

st.sidebar.markdown("---")
centro_analisis = st.sidebar.selectbox(
    "Columna de análisis",
    ["Parcial"] + [c for c in CENTROS_COSTO if c in df.columns],
    index=0,
)

st.sidebar.markdown("### Estado de carga")
st.sidebar.write(f"Filas cargadas: **{len(df_raw):,}**".replace(",", "."))
st.sidebar.write(f"Filas filtradas: **{len(df):,}**".replace(",", "."))


# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏛️ Dirección",
    "📑 P&L",
    "💸 Costos",
    "🏢 Sucursales",
    "🧩 Centros de costo",
    "🔎 Drilldown",
])


with tab1:
    st.subheader("Vista Dirección")

    k = calcular_kpis(df, centro_analisis)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ventas", form_money(k["Ventas"]))
    c2.metric("Utilidad Bruta", form_money(k["Utilidad Bruta"]), form_pct(k["Margen Bruto %"]))
    c3.metric("Utilidad Operativa", form_money(k["Utilidad Operativa"]))
    c4.metric("Resultado Final", form_money(k["Resultado después de Impuestos"]))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Costos Controlables", form_money(k["Costos Controlables"]), form_pct(k["Costos Controlables % ventas"]))
    c6.metric("Utilidad Op. Sucursal", form_money(k["Utilidad Operativa Sucursal"]))
    c7.metric("Resultado Financiero", form_money(k["Ingresos Financieros"] + k["Egresos Financieros"]))
    c8.metric("Movimientos", f"{len(df):,}".replace(",", "."))

    st.markdown("### Evolución mensual")
    if centro_analisis in df.columns and "Mes" in df.columns:
        mensual = df.groupby("Mes", as_index=False)[centro_analisis].sum()
        fig = px.line(mensual, x="Mes", y=centro_analisis, markers=True)
        fig.update_layout(template="plotly_dark", height=420, yaxis_title="Importe", xaxis_title="Mes")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Waterfall ejecutivo")
    wf_labels = [
        "Ventas",
        "Utilidad Bruta",
        "Costos Controlables",
        "Costos No Controlables",
        "Estructura",
        "Resultado Financiero",
        "Resultado Final",
    ]
    wf_values = [
        k["Ventas"],
        k["Utilidad Bruta"] - k["Ventas"],
        k["Costos Controlables"],
        k["Costos No Controlables"],
        k["Estructura Controlable"] + k["Estructura No Controlable"],
        k["Ingresos Financieros"] + k["Egresos Financieros"],
        k["Resultado después de Impuestos"],
    ]
    fig_w = go.Figure(go.Waterfall(
        name="P&L",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "relative", "relative", "total"],
        x=wf_labels,
        y=wf_values,
        text=[form_money(v) for v in wf_values],
        textposition="outside",
    ))
    fig_w.update_layout(template="plotly_dark", height=460)
    st.plotly_chart(fig_w, use_container_width=True)


with tab2:
    st.subheader("P&L interactivo")
    p = pnl_table(df, centro_analisis)

    # Estilo visual del P&L
    def style_pnl(row):
        if row["Tipo"] == "total":
            return ["background-color: #f97316; color: black; font-weight: 900"] * len(row)
        if row["Tipo"] == "subtotal":
            return ["background-color: #facc15; color: black; font-weight: 800"] * len(row)
        return [""] * len(row)

    st.dataframe(
        p[["Grupo", "Concepto", "Importe_fmt"]].style.apply(style_pnl, axis=1),
        use_container_width=True,
        height=720,
    )

    st.markdown("### Composición por grupo")
    grupo = df.groupby("Grupo_PyG", as_index=False)[centro_analisis].sum().sort_values(centro_analisis, ascending=False)
    fig = px.bar(grupo, x="Grupo_PyG", y=centro_analisis, text_auto=".2s")
    fig.update_layout(template="plotly_dark", height=450, xaxis_title="", yaxis_title="Importe")
    st.plotly_chart(fig, use_container_width=True)


with tab3:
    st.subheader("Análisis de costos")

    costos_grupos = [
        "Costos Controlables",
        "Costos No Controlables",
        "Controlables de Estructura",
        "Costos no Controlables de Estructura",
    ]
    costos = df[df["Grupo_PyG"].isin(costos_grupos)].copy()

    c1, c2, c3 = st.columns(3)
    c1.metric("Costos Controlables", form_money(df.loc[df["Grupo_PyG"].eq("Costos Controlables"), centro_analisis].sum()))
    c2.metric("No Controlables", form_money(df.loc[df["Grupo_PyG"].eq("Costos No Controlables"), centro_analisis].sum()))
    c3.metric("Estructura", form_money(df.loc[df["Grupo_PyG"].isin(["Controlables de Estructura","Costos no Controlables de Estructura"]), centro_analisis].sum()))

    if not costos.empty:
        st.markdown("### Ranking de conceptos de costo")
        rank = costos.groupby(["Grupo_PyG", "Concepto_PyG"], as_index=False)[centro_analisis].sum()
        rank["Abs"] = rank[centro_analisis].abs()
        rank = rank.sort_values("Abs", ascending=False).head(25)
        fig = px.bar(rank, y="Concepto_PyG", x=centro_analisis, color="Grupo_PyG", orientation="h")
        fig.update_layout(template="plotly_dark", height=650, yaxis_title="", xaxis_title="Importe")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Evolución mensual por grupo de costo")
        evo = costos.groupby(["Mes", "Grupo_PyG"], as_index=False)[centro_analisis].sum()
        fig2 = px.line(evo, x="Mes", y=centro_analisis, color="Grupo_PyG", markers=True)
        fig2.update_layout(template="plotly_dark", height=450)
        st.plotly_chart(fig2, use_container_width=True)


with tab4:
    st.subheader("Comparativo por sucursal")

    if "Sucursal" in df.columns:
        suc = df.groupby("Sucursal", as_index=False)[centro_analisis].sum().sort_values(centro_analisis, ascending=False)
        fig = px.bar(suc, x="Sucursal", y=centro_analisis, text_auto=".2s")
        fig.update_layout(template="plotly_dark", height=450, xaxis_title="", yaxis_title="Importe")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Matriz sucursal x grupo P&L")
        mat = df.pivot_table(
            index="Sucursal",
            columns="Grupo_PyG",
            values=centro_analisis,
            aggfunc="sum",
            fill_value=0,
        )
        st.dataframe(mat.style.format(lambda x: form_money(x)), use_container_width=True, height=500)
    else:
        st.info("No encontré la columna Sucursal.")


with tab5:
    st.subheader("Centros de costo")

    centros_disponibles = [c for c in CENTROS_COSTO if c in df.columns]
    if centros_disponibles:
        tot_centros = df[centros_disponibles].sum().reset_index()
        tot_centros.columns = ["Centro de costo", "Importe"]
        tot_centros = tot_centros.sort_values("Importe", ascending=False)

        fig = px.bar(tot_centros, x="Centro de costo", y="Importe", text_auto=".2s")
        fig.update_layout(template="plotly_dark", height=440)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Evolución mensual por centro")
        df_long = df.melt(
            id_vars=["Mes"],
            value_vars=centros_disponibles,
            var_name="Centro",
            value_name="Importe",
        )
        evo_cc = df_long.groupby(["Mes", "Centro"], as_index=False)["Importe"].sum()
        fig2 = px.line(evo_cc, x="Mes", y="Importe", color="Centro", markers=True)
        fig2.update_layout(template="plotly_dark", height=520)
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### Tabla centro de costo x grupo")
        long2 = df.melt(
            id_vars=["Grupo_PyG"],
            value_vars=centros_disponibles,
            var_name="Centro",
            value_name="Importe",
        )
        mat2 = long2.pivot_table(index="Grupo_PyG", columns="Centro", values="Importe", aggfunc="sum", fill_value=0)
        st.dataframe(mat2.style.format(lambda x: form_money(x)), use_container_width=True, height=520)
    else:
        st.info("No encontré columnas de centros de costo monetarios.")


with tab6:
    st.subheader("Drilldown contable")

    texto = st.text_input("Buscar en cuenta, detalle, descripción o rubro")
    det = df.copy()

    if texto:
        patron = texto.lower()
        cols_texto = [c for c in ["Cuenta", "Nombre cuenta", "Detalle", "des res", "Detalle 2", "Nombre del rubro", "Concepto_PyG"] if c in det.columns]
        mask = False
        for c in cols_texto:
            mask = mask | det[c].astype(str).str.lower().str.contains(patron, na=False)
        det = det[mask]

    cols_show = [
        c for c in [
            "Fecha", "Cuenta", "Nombre cuenta", "Nro.", "Detalle", "des res", "Detalle 2",
            "Sucursal", "Dpto", "Rub", "SRub", "union", "Nombre del rubro",
            "Grupo_PyG", "Concepto_PyG", "Debe", "Haber", "Parcial"
        ] if c in det.columns
    ]

    st.write(f"Movimientos encontrados: **{len(det):,}**".replace(",", "."))
    st.dataframe(det[cols_show], use_container_width=True, height=620)
    dataframe_download(det[cols_show], "drilldown_mayores_lux.csv")


st.markdown("---")
st.markdown('<div class="small-muted">Nota: el dashboard usa los signos tal como vienen en la base. Si una cuenta requiere tratamiento especial, se ajusta desde el mapa P&L.</div>', unsafe_allow_html=True)