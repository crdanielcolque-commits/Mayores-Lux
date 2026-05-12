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

PNL_ESTRUCTURA = [
    {"Logica": "mas", "Concepto": "Ventas", "Rubros": ["4-1"], "Grupo": "Margen Bruto Gestión Comercial"},
    {"Logica": "menos", "Concepto": "Descuentos sobre ventas", "Rubros": ["4-2"], "Grupo": "Margen Bruto Gestión Comercial"},
    {"Logica": "menos", "Concepto": "Costo de Ventas", "Rubros": ["5-1"], "Grupo": "Margen Bruto Gestión Comercial"},
    {"Logica": "menos", "Concepto": "Rdo. Neto Gestoría", "Rubros": ["6-1", "6-2"], "Grupo": "Margen Bruto Gestión Comercial"},
    {"Logica": "igual", "Concepto": "Margen Bruto Gestión Comercial", "Rubros": [], "Grupo": "Margen Bruto Gestión Comercial"},

    {"Logica": "menos", "Concepto": "Ajuste Costo de Reposición", "Rubros": [], "Grupo": "Margen Bruto Secundario"},
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

    # Formato argentino: 1.234.567,89
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")

    try:
        return float(s)
    except:
        return 0.0


def fmt_money(x):
    try:
        x = float(x)
    except:
        x = 0
    return "$ {:,.0f}".format(x).replace(",", ".")


def normalizar_rubro(x):
    if pd.isna(x):
        return ""
    s = str(x).strip()
    s = s.replace(".0", "")
    s = s.replace(" ", "")
    return s


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

    if "Sucursal" not in df.columns:
        df["Sucursal"] = "Sin sucursal"

    if "Nombre cuenta" not in df.columns:
        df["Nombre cuenta"] = ""

    if "Cuenta:" not in df.columns and "Cuenta" in df.columns:
        df["Cuenta:"] = df["Cuenta"]

    if "Cuenta:" not in df.columns:
        df["Cuenta:"] = ""

    if "Nombre del rubro" not in df.columns:
        df["Nombre del rubro"] = ""

    if "Detalle" not in df.columns:
        df["Detalle"] = ""

    if "des res" not in df.columns:
        df["des res"] = ""

    return df


def construir_pnl(df, campo_importe="Parcial"):
    filas = []
    acumulado = 0.0

    for item in PNL_ESTRUCTURA:
        rubros = item["Rubros"]

        if rubros:
            importe = df.loc[df["Rubro_calc"].isin(rubros), campo_importe].sum()
            acumulado += importe
        else:
            importe = acumulado

        filas.append({
            "Logica": item["Logica"],
            "Grupo": item["Grupo"],
            "Concepto": item["Concepto"],
            "Rubros": " + ".join(rubros),
            "Importe": importe,
            "Importe_fmt": fmt_money(importe)
        })

    return pd.DataFrame(filas)


def aplicar_filtros(df):
    with st.sidebar:
        st.header("Filtros")

        meses = sorted([m for m in df["Mes"].dropna().unique() if m != "NaT"])
        sucursales = sorted(df["Sucursal"].dropna().astype(str).unique())

        mes_sel = st.multiselect("Mes", meses, default=meses)
        suc_sel = st.multiselect("Sucursal", sucursales, default=sucursales)

        centro_sel = st.selectbox(
            "Vista monetaria",
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
st.caption("Cuenta de resultados, centros de costo, sucursales y drilldown contable.")

try:
    df = cargar_datos()
except Exception as e:
    st.error("No se pudo cargar la base desde Google Sheets.")
    st.exception(e)
    st.stop()

if df.empty:
    st.warning("La base está vacía o no pudo leerse correctamente.")
    st.stop()

df_filtrado, campo_importe = aplicar_filtros(df)
pnl = construir_pnl(df_filtrado, campo_importe=campo_importe)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏛️ Dirección",
    "📑 P&L",
    "💸 Costos",
    "🏢 Sucursales",
    "🧩 Centros de costo",
    "🔎 Drilldown"
])

# =========================
# TAB 1 DIRECCIÓN
# =========================

with tab1:
    st.subheader("Resumen ejecutivo")

    ventas = df_filtrado.loc[df_filtrado["Rubro_calc"].isin(["4-1"]), campo_importe].sum()
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
        if not evo.empty:
            fig = px.line(evo, x="Mes", y=campo_importe, markers=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos para mostrar evolución.")

    with col2:
        st.markdown("### Resultado por sucursal")
        suc = df_filtrado.groupby("Sucursal", as_index=False)[campo_importe].sum()
        if not suc.empty:
            fig = px.bar(suc, x="Sucursal", y=campo_importe)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos por sucursal.")

# =========================
# TAB 2 P&L
# =========================

with tab2:
    st.subheader("P&L interactivo")

    if pnl.empty:
        st.warning("No hay datos para construir el P&L.")
    else:
        st.dataframe(
            pnl[["Logica", "Grupo", "Concepto", "Rubros", "Importe_fmt"]],
            use_container_width=True,
            height=720
        )

        st.markdown("### Waterfall P&L")
        pnl_detalle = pnl[pnl["Logica"].isin(["mas", "menos"])].copy()

        if not pnl_detalle.empty:
            fig = px.bar(
                pnl_detalle,
                x="Concepto",
                y="Importe",
                color="Grupo",
                title="Aportes por concepto"
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay conceptos con movimiento para graficar.")

# =========================
# TAB 3 COSTOS
# =========================

with tab3:
    st.subheader("Análisis de costos")

    rubros_costos = []
    for item in PNL_ESTRUCTURA:
        if "Costo" in item["Grupo"] or "Controlables" in item["Grupo"] or "Egresos" in item["Grupo"]:
            rubros_costos += item["Rubros"]

    costos = df_filtrado[df_filtrado["Rubro_calc"].isin(rubros_costos)].copy()

    if costos.empty:
        st.info("No hay costos para los filtros seleccionados.")
    else:
        costos_rubro = costos.groupby(["Rubro_calc", "Nombre del rubro"], as_index=False)[campo_importe].sum()
        costos_rubro = costos_rubro.sort_values(campo_importe)

        fig = px.bar(
            costos_rubro,
            x=campo_importe,
            y="Nombre del rubro",
            orientation="h",
            title="Costos por rubro"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            costos_rubro,
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

    if suc.empty:
        st.info("No hay datos por sucursal.")
    else:
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

    centros_disponibles = [c for c in CENTROS_COSTO if c in df_filtrado.columns]

    if not centros_disponibles:
        st.warning("No se encontraron columnas de centros de costo.")
    else:
        resumen_centros = pd.DataFrame({
            "Centro de costo": centros_disponibles,
            "Importe": [df_filtrado[c].sum() for c in centros_disponibles]
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
# TAB 6 DRILLDOWN
# =========================

with tab6:
    st.subheader("Drilldown contable")

    columnas_drill = [
        "Fecha",
        "Mes",
        "Sucursal",
        "Cuenta:",
        "Nombre cuenta",
        "Rubro_calc",
        "Nombre del rubro",
        "Detalle",
        "des res",
        "Debe",
        "Haber",
        "Parcial"
    ]

    columnas_drill = [c for c in columnas_drill if c in df_filtrado.columns]

    buscar = st.text_input("Buscar en cuenta, detalle o descripción")

    drill = df_filtrado.copy()

    if buscar:
        texto = buscar.lower()
        mask = False
        for col in ["Nombre cuenta", "Detalle", "des res", "Nombre del rubro"]:
            if col in drill.columns:
                mask = mask | drill[col].astype(str).str.lower().str.contains(texto, na=False)
        drill = drill[mask]

    st.dataframe(
        drill[columnas_drill],
        use_container_width=True,
        height=650
    )

    st.download_button(
        label="⬇️ Descargar drilldown filtrado",
        data=drill.to_csv(index=False).encode("utf-8-sig"),
        file_name="drilldown_mayores_lux.csv",
        mime="text/csv"
    )
