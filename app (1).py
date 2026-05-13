import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="Dashboard Mayores Contables LUX",
    page_icon="📊",
    layout="wide"
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
    "Administr."
]

SIGNO_RUBRO = {
    "VENTAS": "-",
    "INCENTIVOS": "-",
    "COMIS. P/VTA DIRECTA": "-",
    "INGRESO EXTRAORDIN": "-",
    "OTROS ING FINANCIERO": "-",
    "INGRESOS SEGUROS": "-",
    "COMIS CONSIGNACIONES": "-",
    "SOBRANTES DE INV.": "-",

    "INTERESES IMPOSITIVO": "+",
    "MERMAS DE INVENTARIO": "+",
    "GTOS GESTIO JUDICIAL": "+",
    "COMISION CHANGO CAR": "+",
    "UTILES Y MAT. DE OFI": "+",
    "Adm Ctral (No Usar)": "+",
    "COMIS. A VENDEDORES": "+",
    "SUELDOS ADM. Y CS.SS": "+",
    "SEGUROS": "+",
    "SUELDOS ADM CENTRAL": "+",
    "GTOS ATENCION CLIENT": "+",
    "UTILES Y MAT DE OFIC": "+",
    "EGRESO EXTRAORDINARI": "+",
    "TELEFONO E INTERNET": "+",
    "MANT. RODADOS": "+",
    "IMPUESTOS Y TASAS": "+",
    "OTROS GTOS FIJOS": "+",
    "PREPARAC. Y PREENTRE": "+",
    "SEGURIDAD Y VIGILANC": "+",
    "HERRAM. MAT. Y FLETE": "+",
    "EGRESOS GESTORIA": "+",
    "MOVILIDAD Y VIATICOS": "+",
    "ALQUILERES": "+",
    "LUZ,AGUA Y GAS": "+",
    "HONORARIOS PROFESION": "+",
    "Serv. Limpieza": "+",
    "PUBLICIDAD Y PROMOC.": "+",
    "COSTO DE REAC. Y ACC": "+",
    "MANTENIM. BS. DE USO": "+",
    "SERV LUZ.TEL.SUSCRIP": "+",
    "COM. Y GTOS BANCARIO": "+",
    "INGRESOS GESTORIA": "+",
    "SS. GRAT. Y CS. INT.": "+",
    "AMORTIZACIONES": "+",
    "OTROS EGR. FINANCIER": "+",
    "IMPUESTOS FINANCIAC": "+",
    "INT. FINANC. VEHICUL": "+",
    "DESCUENTOS S/ VTAS.": "+",
    "COSTO DE VENTAS": "+"
}

PNL_ESTRUCTURA = [
    {"Logica": "mas", "Concepto": "Ventas", "Rubros": ["4-1"], "Grupo": "Margen Bruto Gestión Comercial"},
    {"Logica": "menos", "Concepto": "Descuentos sobre ventas", "Rubros": ["4-2"], "Grupo": "Margen Bruto Gestión Comercial"},
    {"Logica": "menos", "Concepto": "Costo de Ventas", "Rubros": ["5-1"], "Grupo": "Margen Bruto Gestión Comercial"},
    {"Logica": "menos", "Concepto": "Rdo. Neto Gestoría", "Rubros": ["6-1", "6-2"], "Grupo": "Margen Bruto Gestión Comercial"},
    {"Logica": "igual", "Concepto": "Margen Bruto Gestión Comercial", "Rubros": [], "Grupo": "Margen Bruto Gestión Comercial"},

    {"Logica": "menos", "Concepto": "Costo Reacondic. y Acces.", "Rubros": ["5-2"], "Grupo": "Margen Bruto Secundario"},
    {"Logica": "igual", "Concepto": "Margen Bruto Primario", "Rubros": [], "Grupo": "Margen Bruto Secundario"},
    {"Logica": "mas", "Concepto": "Incentivos", "Rubros": ["4-3"], "Grupo": "Margen Bruto Secundario"},
    {"Logica": "mas", "Concepto": "Incentivo Devengado", "Rubros": ["4-4"], "Grupo": "Margen Bruto Secundario"},
    {"Logica": "mas", "Concepto": "Comisión Consignaciones", "Rubros": ["6-3"], "Grupo": "Margen Bruto Secundario"},
    {"Logica": "menos", "Concepto": "Comisión Pagadas", "Rubros": ["6-6"], "Grupo": "Margen Bruto Secundario"},
    {"Logica": "mas", "Concepto": "Comisión P/Vta Directa", "Rubros": ["10-1"], "Grupo": "Margen Bruto Secundario"},
    {"Logica": "igual", "Concepto": "Margen Bruto Secundario", "Rubros": [], "Grupo": "Margen Bruto Secundario"},

    {"Logica": "menos", "Concepto": "Mermas de Inventarios", "Rubros": ["5-3"], "Grupo": "Otros Ingresos / Egresos"},
    {"Logica": "menos", "Concepto": "Sobrantes de Inventarios", "Rubros": ["5-4"], "Grupo": "Otros Ingresos / Egresos"},
    {"Logica": "menos", "Concepto": "Pérdida IVA Usados", "Rubros": ["5-5"], "Grupo": "Otros Ingresos / Egresos"},
    {"Logica": "menos", "Concepto": "Horas no aplicadas mecánicos", "Rubros": ["6-4"], "Grupo": "Otros Ingresos / Egresos"},
    {"Logica": "mas", "Concepto": "Resultado Venta de PPAA MS", "Rubros": ["6-5"], "Grupo": "Otros Ingresos / Egresos"},
    {"Logica": "mas", "Concepto": "Ingresos Seguros y Comis Gestión Vta", "Rubros": ["10-4"], "Grupo": "Otros Ingresos / Egresos"},
    {"Logica": "menos", "Concepto": "Egresos Seguros", "Rubros": ["11-5"], "Grupo": "Otros Ingresos / Egresos"},
    {"Logica": "igual", "Concepto": "Utilidad Bruta", "Rubros": [], "Grupo": "Utilidad Bruta"},

    {"Logica": "menos", "Concepto": "Comisiones sobre Ventas", "Rubros": ["7-2"], "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Sueldos y Cargas Sociales", "Rubros": ["8-1"], "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Sueldos Administración y C. Soc.", "Rubros": ["8-4"], "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Gastos de Atención clientes", "Rubros": ["7-1"], "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Servicios gratuitos y Cargos internos", "Rubros": ["7-4"], "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Herramientas, materiales y fletes", "Rubros": ["7-6"], "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Publicidad y Promoción", "Rubros": ["8-2"], "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Mantenimiento rodados y equipos", "Rubros": ["8-3"], "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Movilidad y Viáticos", "Rubros": ["8-6"], "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Mantenimiento Bienes de Uso", "Rubros": ["8-8"], "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Fuerza motriz, luz, agua y gas", "Rubros": ["8-9"], "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Teléfonos e internet", "Rubros": ["8-10"], "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Serv. Limpieza", "Rubros": ["8-11"], "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Útiles y materiales de oficina", "Rubros": ["8-12"], "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Otros Gastos Fijos", "Rubros": ["8-13"], "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Alquileres", "Rubros": ["8-14"], "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Previsiones Varias", "Rubros": ["8-17"], "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Deudores Incobrables", "Rubros": ["8-19"], "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Preparación y entrega", "Rubros": ["7-3"], "Grupo": "Costos Controlables"},
    {"Logica": "menos", "Concepto": "Seguridad y vigilancia", "Rubros": ["8-20"], "Grupo": "Costos Controlables"},

    {"Logica": "menos", "Concepto": "Impuestos", "Rubros": ["7-5"], "Grupo": "Costos No Controlables"},
    {"Logica": "menos", "Concepto": "Honorarios profesionales", "Rubros": ["8-5"], "Grupo": "Costos No Controlables"},
    {"Logica": "menos", "Concepto": "Recupero de Gastos Toyota", "Rubros": ["8-7"], "Grupo": "Costos No Controlables"},
    {"Logica": "menos", "Concepto": "Amortizaciones", "Rubros": ["8-15"], "Grupo": "Costos No Controlables"},
    {"Logica": "menos", "Concepto": "Seguros", "Rubros": ["8-16"], "Grupo": "Costos No Controlables"},
    {"Logica": "menos", "Concepto": "Impuestos y tasas", "Rubros": ["8-18"], "Grupo": "Costos No Controlables"},
    {"Logica": "igual", "Concepto": "Utilidad Operativa Sucursal", "Rubros": [], "Grupo": "Utilidad Operativa Sucursal"},

    {"Logica": "menos", "Concepto": "Sueldos Gtes y Jefes Suc.", "Rubros": ["9-1"], "Grupo": "Controlables de Estructura"},
    {"Logica": "menos", "Concepto": "Sueldos Adm. Central", "Rubros": ["9-2"], "Grupo": "Controlables de Estructura"},
    {"Logica": "menos", "Concepto": "Prestaciones La Luz", "Rubros": ["9-3"], "Grupo": "Controlables de Estructura"},
    {"Logica": "menos", "Concepto": "Movilidad y Viáticos Central", "Rubros": ["9-4"], "Grupo": "Controlables de Estructura"},
    {"Logica": "menos", "Concepto": "Mantenimiento Bs Uso Central", "Rubros": ["9-5"], "Grupo": "Controlables de Estructura"},
    {"Logica": "menos", "Concepto": "Útiles y materiales de oficina Central", "Rubros": ["9-6"], "Grupo": "Controlables de Estructura"},
    {"Logica": "menos", "Concepto": "Serv., Energía, Suscripciones Adm Central", "Rubros": ["9-7"], "Grupo": "Controlables de Estructura"},
    {"Logica": "menos", "Concepto": "Alquileres Adm Central", "Rubros": ["9-9"], "Grupo": "Controlables de Estructura"},
    {"Logica": "menos", "Concepto": "Amortizaciones Estructura", "Rubros": ["9-8"], "Grupo": "Costos no Controlables de Estructura"},
    {"Logica": "igual", "Concepto": "Utilidad Operativa", "Rubros": [], "Grupo": "Utilidad Operativa"},

    {"Logica": "mas", "Concepto": "Intereses Financiación Vehículos", "Rubros": ["10-2"], "Grupo": "Ingresos Financieros"},
    {"Logica": "mas", "Concepto": "Otros Ingresos Financieros", "Rubros": ["10-3"], "Grupo": "Ingresos Financieros"},
    {"Logica": "menos", "Concepto": "Impuestos Financiación", "Rubros": ["11-1"], "Grupo": "Egresos Financieros"},
    {"Logica": "menos", "Concepto": "Intereses Impositivos", "Rubros": ["11-2"], "Grupo": "Egresos Financieros"},
    {"Logica": "menos", "Concepto": "Comisiones y gastos bancarios", "Rubros": ["11-3"], "Grupo": "Egresos Financieros"},
    {"Logica": "menos", "Concepto": "Financiación cap trab", "Rubros": ["11-4"], "Grupo": "Egresos Financieros"},
    {"Logica": "igual", "Concepto": "Resultado antes de Impuestos", "Rubros": [], "Grupo": "Resultado antes de Impuestos"},
    {"Logica": "menos", "Concepto": "Impuesto a las Ganancias", "Rubros": [], "Grupo": "Impuesto a las Ganancias"},
    {"Logica": "igual", "Concepto": "Resultado después de Impuestos", "Rubros": [], "Grupo": "Resultado después de Impuestos"},
]


# =========================
# FUNCIONES
# =========================

def limpiar_numero(x):
    if pd.isna(x):
        return 0.0
    if isinstance(x, (int, float, np.number)):
        return float(x)

    s = str(x).strip()
    if s == "":
        return 0.0

    s = s.replace("$", "")
    s = s.replace(" ", "")
    s = s.replace("\xa0", "")

    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")

    try:
        return float(s)
    except Exception:
        return 0.0


def limpiar_texto(x):
    if pd.isna(x):
        return ""
    return str(x).strip()


def fmt_money(x):
    try:
        x = float(x)
    except Exception:
        x = 0
    return "$ {:,.0f}".format(x).replace(",", ".")


def fmt_pct(x):
    try:
        if pd.isna(x):
            return ""
        return "{:.1%}".format(float(x))
    except Exception:
        return ""


def normalizar_rubro(x):
    if pd.isna(x):
        return ""
    s = str(x).strip()
    s = s.replace(".0", "")
    s = s.replace(" ", "")
    return s


def signo_factor_por_rubro(nombre_rubro):
    nombre = limpiar_texto(nombre_rubro)

    if nombre in SIGNO_RUBRO:
        signo = SIGNO_RUBRO[nombre]
    else:
        signo = "+"

    # Si el mayor trae el rubro con signo contable negativo,
    # para gestión lo convertimos a magnitud positiva.
    # Si trae signo positivo, también trabajamos como magnitud positiva.
    return -1 if signo == "-" else 1


@st.cache_data(ttl=600)
def cargar_datos():
    df = pd.read_csv(CSV_URL)
    df.columns = [str(c).strip() for c in df.columns]

    if "Fecha" in df.columns:
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce", dayfirst=True)
        df["Mes"] = df["Fecha"].dt.to_period("M").astype(str)
    else:
        df["Fecha"] = pd.NaT
        df["Mes"] = "Sin fecha"

    columnas_importe = ["Debe", "Haber", "Parcial"] + CENTROS_COSTO
    for col in columnas_importe:
        if col in df.columns:
            df[col] = df[col].apply(limpiar_numero)
        else:
            df[col] = 0.0

    if "Rub" in df.columns and "SRub" in df.columns:
        df["Rubro_calc"] = (
            df["Rub"].apply(normalizar_rubro)
            + "-"
            + df["SRub"].apply(normalizar_rubro)
        )
    elif "union" in df.columns:
        df["Rubro_calc"] = df["union"].apply(normalizar_rubro)
    else:
        df["Rubro_calc"] = ""

    columnas_texto = [
        "Sucursal", "Nombre cuenta", "Cuenta:", "Cuenta", "Nombre del rubro",
        "Detalle", "des res", "Detalle 2", "Dpto", "Nro."
    ]

    for col in columnas_texto:
        if col not in df.columns:
            df[col] = ""

    if "Cuenta:" not in df.columns and "Cuenta" in df.columns:
        df["Cuenta:"] = df["Cuenta"]

    df["Sucursal"] = df["Sucursal"].fillna("Sin sucursal").astype(str)
    df["Nombre del rubro"] = df["Nombre del rubro"].apply(limpiar_texto)

    df["Signo_rubro"] = df["Nombre del rubro"].map(SIGNO_RUBRO).fillna("+")
    df["Factor_signo"] = df["Nombre del rubro"].apply(signo_factor_por_rubro)

    # Columnas corregidas para gestión.
    # Estas convierten ingresos que vienen negativos en positivos para gestión.
    # Luego el P&L aplica la lógica mas/menos.
    df["Parcial_Gestion"] = df["Parcial"] * df["Factor_signo"]

    for col in CENTROS_COSTO:
        df[f"{col}_Gestion"] = df[col] * df["Factor_signo"]

    return df


def campo_gestion(campo):
    if campo == "Parcial":
        return "Parcial_Gestion"
    if campo in CENTROS_COSTO:
        return f"{campo}_Gestion"
    return campo


def construir_pnl(df, campo_importe="Parcial_Gestion"):
    filas = []
    acumulado = 0.0

    for item in PNL_ESTRUCTURA:
        rubros = item["Rubros"]
        logica = item["Logica"]

        if rubros:
            importe_bruto = df.loc[df["Rubro_calc"].isin(rubros), campo_importe].sum()

            if logica == "menos":
                importe_resultado = -abs(importe_bruto)
            elif logica == "mas":
                importe_resultado = abs(importe_bruto)
            else:
                importe_resultado = importe_bruto

            acumulado += importe_resultado
            importe_mostrar = importe_resultado
        else:
            importe_mostrar = acumulado

        filas.append({
            "Logica": item["Logica"],
            "Grupo": item["Grupo"],
            "Concepto": item["Concepto"],
            "Rubros": " + ".join(rubros),
            "Importe": importe_mostrar,
            "Importe_fmt": fmt_money(importe_mostrar)
        })

    return pd.DataFrame(filas)


def mapa_rubro_a_pnl():
    filas = []
    for item in PNL_ESTRUCTURA:
        for rubro in item["Rubros"]:
            filas.append({
                "Rubro_calc": rubro,
                "Concepto_PNL": item["Concepto"],
                "Grupo_PNL": item["Grupo"],
                "Logica_PNL": item["Logica"]
            })
    return pd.DataFrame(filas)


def preparar_base_pnl(df):
    mapa = mapa_rubro_a_pnl()
    base = df.merge(mapa, on="Rubro_calc", how="left")
    base["Grupo_PNL"] = base["Grupo_PNL"].fillna("Sin clasificar")
    base["Concepto_PNL"] = base["Concepto_PNL"].fillna("Sin clasificar")
    base["Logica_PNL"] = base["Logica_PNL"].fillna("sin lógica")
    return base


def aplicar_filtros(df):
    with st.sidebar:
        st.header("Filtros generales")

        meses = sorted([m for m in df["Mes"].dropna().unique() if m != "NaT"])
        sucursales = sorted(df["Sucursal"].dropna().astype(str).unique())

        mes_sel = st.multiselect("Mes", meses, default=meses)
        suc_sel = st.multiselect("Sucursal", sucursales, default=sucursales)

        centro_sel = st.selectbox(
            "Vista monetaria general",
            ["Parcial"] + [c for c in CENTROS_COSTO if c in df.columns]
        )

    dff = df.copy()

    if mes_sel:
        dff = dff[dff["Mes"].isin(mes_sel)]

    if suc_sel:
        dff = dff[dff["Sucursal"].astype(str).isin(suc_sel)]

    return dff, centro_sel


# =========================
# ESTILO
# =========================

st.markdown("""
<style>
.main {
    background-color: #f7f9fc;
}
h1 {
    font-weight: 800;
    color: #1f2a44;
}
h2, h3 {
    color: #1f2a44;
}
[data-testid="stMetricValue"] {
    font-size: 28px;
}
.card {
    background: white;
    padding: 18px;
    border-radius: 18px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
    border: 1px solid #e8edf5;
}
</style>
""", unsafe_allow_html=True)


# =========================
# APP
# =========================

st.title("📊 Dashboard Mayores Contables LUX")
st.caption("Cuenta de resultados, centros de costo, sucursales, evolución mensual y drilldown contable.")

try:
    df = cargar_datos()
except Exception as e:
    st.error("No se pudo cargar la base desde Google Sheets.")
    st.exception(e)
    st.stop()

if df.empty:
    st.warning("La base está vacía o no pudo leerse correctamente.")
    st.stop()

df_filtrado, campo_importe_original = aplicar_filtros(df)
campo_importe = campo_gestion(campo_importe_original)

df_pnl = preparar_base_pnl(df_filtrado)
pnl = construir_pnl(df_filtrado, campo_importe=campo_importe)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🏛️ Dirección",
    "📑 P&L",
    "💸 Costos",
    "🏢 Sucursales",
    "🧩 Centros de costo",
    "📈 Desvíos mensuales",
    "🧾 Control signos",
    "🔎 Drilldown"
])


# =========================
# TAB 1 DIRECCIÓN
# =========================

with tab1:
    st.subheader("Resumen ejecutivo")

    ventas = pnl.loc[pnl["Concepto"] == "Ventas", "Importe"].sum()
    utilidad_bruta = pnl.loc[pnl["Concepto"] == "Utilidad Bruta", "Importe"].sum()
    utilidad_operativa = pnl.loc[pnl["Concepto"] == "Utilidad Operativa", "Importe"].sum()
    resultado_final = pnl.loc[pnl["Concepto"] == "Resultado después de Impuestos", "Importe"].sum()

    margen_bruto_pct = utilidad_bruta / ventas if ventas != 0 else 0
    margen_operativo_pct = utilidad_operativa / ventas if ventas != 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ventas", fmt_money(ventas))
    c2.metric("Utilidad Bruta", fmt_money(utilidad_bruta), f"{margen_bruto_pct:.1%}")
    c3.metric("Utilidad Operativa", fmt_money(utilidad_operativa), f"{margen_operativo_pct:.1%}")
    c4.metric("Resultado Final", fmt_money(resultado_final))

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Evolución mensual")
        evo = df_filtrado.groupby("Mes", as_index=False)[campo_importe].sum()
        fig = px.line(evo, x="Mes", y=campo_importe, markers=True)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Resultado por sucursal")
        suc = df_filtrado.groupby("Sucursal", as_index=False)[campo_importe].sum()
        fig = px.bar(suc, x="Sucursal", y=campo_importe)
        st.plotly_chart(fig, use_container_width=True)


# =========================
# TAB 2 P&L
# =========================

with tab2:
    st.subheader("P&L interactivo")

    st.dataframe(
        pnl[["Logica", "Grupo", "Concepto", "Rubros", "Importe_fmt"]],
        use_container_width=True,
        height=720
    )

    st.markdown("### Aportes por concepto")
    pnl_detalle = pnl[pnl["Logica"].isin(["mas", "menos"])].copy()

    fig = px.bar(
        pnl_detalle,
        x="Concepto",
        y="Importe",
        color="Grupo",
        title="Aportes por concepto"
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)


# =========================
# TAB 3 COSTOS
# =========================

with tab3:
    st.subheader("Análisis de costos")

    grupos_costos = [
        "Costos Controlables",
        "Costos No Controlables",
        "Controlables de Estructura",
        "Costos no Controlables de Estructura",
        "Egresos Financieros",
        "Otros Ingresos / Egresos"
    ]

    costos = df_pnl[df_pnl["Grupo_PNL"].isin(grupos_costos)].copy()

    if costos.empty:
        st.info("No hay costos para los filtros seleccionados.")
    else:
        costos_rubro = costos.groupby(
            ["Grupo_PNL", "Concepto_PNL", "Rubro_calc", "Nombre del rubro"],
            as_index=False
        )[campo_importe].sum()

        costos_rubro = costos_rubro.sort_values(campo_importe)
        costos_rubro["Importe_fmt"] = costos_rubro[campo_importe].apply(fmt_money)

        fig = px.bar(
            costos_rubro,
            x=campo_importe,
            y="Concepto_PNL",
            color="Grupo_PNL",
            orientation="h",
            title="Costos por concepto"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            costos_rubro[["Grupo_PNL", "Concepto_PNL", "Rubro_calc", "Nombre del rubro", "Importe_fmt"]],
            use_container_width=True,
            height=500
        )


# =========================
# TAB 4 SUCURSALES
# =========================

with tab4:
    st.subheader("Comparativo por sucursal")

    suc = df_filtrado.groupby("Sucursal", as_index=False)[campo_importe].sum()
    suc = suc.sort_values(campo_importe, ascending=False)
    suc["Importe_fmt"] = suc[campo_importe].apply(fmt_money)

    fig = px.bar(
        suc,
        x="Sucursal",
        y=campo_importe,
        title="Resultado por sucursal"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(suc, use_container_width=True)


# =========================
# TAB 5 CENTROS DE COSTO
# =========================

with tab5:
    st.subheader("Análisis por centros de costo")

    centros_disponibles = [c for c in CENTROS_COSTO if f"{c}_Gestion" in df_filtrado.columns]

    resumen_centros = pd.DataFrame({
        "Centro de costo": centros_disponibles,
        "Importe": [df_filtrado[f"{c}_Gestion"].sum() for c in centros_disponibles]
    })

    resumen_centros = resumen_centros.sort_values("Importe", ascending=False)
    resumen_centros["Importe_fmt"] = resumen_centros["Importe"].apply(fmt_money)

    fig = px.bar(
        resumen_centros,
        x="Centro de costo",
        y="Importe",
        title="Resultado por centro de costo"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        resumen_centros[["Centro de costo", "Importe_fmt"]],
        use_container_width=True
    )


# =========================
# TAB 6 DESVÍOS MENSUALES
# =========================

with tab6:
    st.subheader("📈 Desvíos mensuales por centro de costo")

    centros_posventa = [c for c in ["Repuestos", "Tl. Mec.", "Mayorista", "ChapyPintu"] if f"{c}_Gestion" in df_pnl.columns]
    centros_validos = centros_posventa if centros_posventa else [c for c in CENTROS_COSTO if f"{c}_Gestion" in df_pnl.columns]

    colf1, colf2 = st.columns(2)

    with colf1:
        centro_analisis = st.selectbox(
            "Centro de costo",
            centros_validos,
            index=0
        )

    grupos_disponibles = [
        "Costos Controlables",
        "Costos No Controlables",
        "Controlables de Estructura",
        "Costos no Controlables de Estructura",
        "Egresos Financieros",
        "Otros Ingresos / Egresos"
    ]

    with colf2:
        grupos_sel = st.multiselect(
            "Categorías a analizar",
            grupos_disponibles,
            default=["Costos Controlables", "Costos No Controlables"]
        )

    campo_cc = f"{centro_analisis}_Gestion"

    base_desvios = df_pnl[df_pnl["Grupo_PNL"].isin(grupos_sel)].copy()
    base_desvios["Importe_CC"] = base_desvios[campo_cc]

    if base_desvios.empty:
        st.info("No hay datos para los filtros seleccionados.")
    else:
        total_periodo = base_desvios["Importe_CC"].sum()

        mensual_total = (
            base_desvios.groupby("Mes", as_index=False)["Importe_CC"]
            .sum()
            .sort_values("Mes")
        )

        mensual_total["Mes_anterior"] = mensual_total["Importe_CC"].shift(1)
        mensual_total["Variacion_$"] = mensual_total["Importe_CC"] - mensual_total["Mes_anterior"]
        mensual_total["Variacion_%"] = np.where(
            mensual_total["Mes_anterior"].abs() > 0,
            mensual_total["Variacion_$"] / mensual_total["Mes_anterior"].abs(),
            np.nan
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Centro analizado", centro_analisis)
        c2.metric("Total período", fmt_money(total_periodo))

        mayor_salto = mensual_total.dropna(subset=["Variacion_$"]).copy()
        if not mayor_salto.empty:
            mayor_salto["Impacto_abs"] = mayor_salto["Variacion_$"].abs()
            fila_salto = mayor_salto.sort_values("Impacto_abs", ascending=False).iloc[0]
            c3.metric(
                "Mayor salto mensual",
                fmt_money(fila_salto["Variacion_$"]),
                f"{fila_salto['Mes']}"
            )
        else:
            c3.metric("Mayor salto mensual", "Sin comparación")

        st.markdown("### Evolución mensual de la categoría seleccionada")

        fig = px.line(
            mensual_total,
            x="Mes",
            y="Importe_CC",
            markers=True,
            title=f"Evolución mensual - {centro_analisis}"
        )
        st.plotly_chart(fig, use_container_width=True)

        mensual_componentes = (
            base_desvios.groupby(["Mes", "Grupo_PNL", "Concepto_PNL"], as_index=False)["Importe_CC"]
            .sum()
            .sort_values(["Grupo_PNL", "Concepto_PNL", "Mes"])
        )

        mensual_componentes["Mes_anterior"] = mensual_componentes.groupby(
            ["Grupo_PNL", "Concepto_PNL"]
        )["Importe_CC"].shift(1)

        mensual_componentes["Variacion_$"] = mensual_componentes["Importe_CC"] - mensual_componentes["Mes_anterior"]

        mensual_componentes["Variacion_%"] = np.where(
            mensual_componentes["Mes_anterior"].abs() > 0,
            mensual_componentes["Variacion_$"] / mensual_componentes["Mes_anterior"].abs(),
            np.nan
        )

        ranking_desvios = mensual_componentes.dropna(subset=["Variacion_$"]).copy()
        ranking_desvios["Impacto_abs"] = ranking_desvios["Variacion_$"].abs()
        ranking_desvios = ranking_desvios.sort_values("Impacto_abs", ascending=False)

        st.markdown("### Principales componentes que explican los desvíos")

        if ranking_desvios.empty:
            st.info("No hay meses suficientes para calcular variaciones.")
        else:
            top_desvios = ranking_desvios.head(15).copy()
            top_desvios["Importe_fmt"] = top_desvios["Importe_CC"].apply(fmt_money)
            top_desvios["Var_fmt"] = top_desvios["Variacion_$"].apply(fmt_money)
            top_desvios["Var_%_fmt"] = top_desvios["Variacion_%"].apply(fmt_pct)

            fig = px.bar(
                top_desvios,
                x="Variacion_$",
                y="Concepto_PNL",
                color="Grupo_PNL",
                orientation="h",
                title="Top desvíos mensuales por componente"
            )
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(
                top_desvios[[
                    "Mes",
                    "Grupo_PNL",
                    "Concepto_PNL",
                    "Importe_fmt",
                    "Var_fmt",
                    "Var_%_fmt"
                ]],
                use_container_width=True,
                height=420
            )

            principal = top_desvios.iloc[0]
            st.info(
                f"El principal desvío detectado corresponde a **{principal['Concepto_PNL']}** "
                f"en el mes **{principal['Mes']}**, dentro del grupo **{principal['Grupo_PNL']}**. "
                f"La variación mensual fue de **{fmt_money(principal['Variacion_$'])}**. "
                f"Este componente debería revisarse primero porque es el mayor salto absoluto del período filtrado."
            )

        st.markdown("### Movimientos contables atípicos que pueden explicar el salto")

        movimientos = base_desvios.copy()
        movimientos["Impacto_abs"] = movimientos["Importe_CC"].abs()
        movimientos = movimientos.sort_values("Impacto_abs", ascending=False)

        columnas_mov = [
            "Fecha",
            "Mes",
            "Sucursal",
            "Cuenta:",
            "Nombre cuenta",
            "Rubro_calc",
            "Nombre del rubro",
            "Grupo_PNL",
            "Concepto_PNL",
            "Detalle",
            "des res",
            campo_cc
        ]

        columnas_mov = [c for c in columnas_mov if c in movimientos.columns]

        movimientos_top = movimientos.head(30).copy()
        movimientos_top["Importe_CC_fmt"] = movimientos_top[campo_cc].apply(fmt_money)

        columnas_mostrar = [c for c in columnas_mov if c != campo_cc] + ["Importe_CC_fmt"]

        st.dataframe(
            movimientos_top[columnas_mostrar],
            use_container_width=True,
            height=520
        )

        st.download_button(
            label="⬇️ Descargar análisis de desvíos",
            data=base_desvios.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"desvios_{centro_analisis}.csv",
            mime="text/csv"
        )


# =========================
# TAB 7 CONTROL SIGNOS
# =========================

with tab7:
    st.subheader("🧾 Control de signos por rubro")

    control = (
        df_filtrado.groupby(["Nombre del rubro", "Signo_rubro"], as_index=False)
        .agg(
            Parcial_original=("Parcial", "sum"),
            Parcial_gestion=("Parcial_Gestion", "sum")
        )
        .sort_values("Nombre del rubro")
    )

    control["Parcial_original_fmt"] = control["Parcial_original"].apply(fmt_money)
    control["Parcial_gestion_fmt"] = control["Parcial_gestion"].apply(fmt_money)

    st.dataframe(
        control[[
            "Nombre del rubro",
            "Signo_rubro",
            "Parcial_original_fmt",
            "Parcial_gestion_fmt"
        ]],
        use_container_width=True,
        height=650
    )

    st.caption("Parcial original = signo tal como viene del mayor. Parcial gestión = importe normalizado para construir el P&L.")


# =========================
# TAB 8 DRILLDOWN
# =========================

with tab8:
    st.subheader("Drilldown contable")

    columnas_drill = [
        "Fecha",
        "Mes",
        "Sucursal",
        "Cuenta:",
        "Nombre cuenta",
        "Rubro_calc",
        "Nombre del rubro",
        "Signo_rubro",
        "Detalle",
        "des res",
        "Debe",
        "Haber",
        "Parcial",
        "Parcial_Gestion"
    ]

    columnas_drill = [c for c in columnas_drill if c in df_filtrado.columns]

    buscar = st.text_input("Buscar en cuenta, detalle o descripción")

    drill = df_filtrado.copy()

    if buscar:
        texto = buscar.lower()
        mask = pd.Series(False, index=drill.index)
        for col in ["Nombre cuenta", "Detalle", "des res", "Nombre del rubro"]:
            if col in drill.columns:
                mask = mask | drill[col].astype(str).str.lower().str.contains(texto, na=False)
        drill = drill[mask]

    drill_mostrar = drill[columnas_drill].copy()

    if "Parcial" in drill_mostrar.columns:
        drill_mostrar["Parcial_fmt"] = drill_mostrar["Parcial"].apply(fmt_money)

    if "Parcial_Gestion" in drill_mostrar.columns:
        drill_mostrar["Parcial_Gestion_fmt"] = drill_mostrar["Parcial_Gestion"].apply(fmt_money)

    st.dataframe(
        drill_mostrar,
        use_container_width=True,
        height=650
    )

    st.download_button(
        label="⬇️ Descargar drilldown filtrado",
        data=drill.to_csv(index=False).encode("utf-8-sig"),
        file_name="drilldown_mayores_lux.csv",
        mime="text/csv"
    )
