import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

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
    signo = SIGNO_RUBRO.get(nombre, "+")
    return -1 if signo == "-" else 1


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

    df["Parcial_Gestion"] = df["Parcial"] * df["Factor_signo"]

    for col in CENTROS_COSTO:
        df[f"{col}_Gestion"] = df[col] * df["Factor_signo"]

    mapa = mapa_rubro_a_pnl()
    df = df.merge(mapa, on="Rubro_calc", how="left")

    df["Grupo_PNL"] = df["Grupo_PNL"].fillna("Sin clasificar")
    df["Concepto_PNL"] = df["Concepto_PNL"].fillna("Sin clasificar")
    df["Logica_PNL"] = df["Logica_PNL"].fillna("sin lógica")

    return df


def construir_pnl(df, campo_importe):
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


def semaforo_variacion_costos(var):
    if pd.isna(var):
        return "⚪ Sin comparación"
    if var > 0:
        return "🔴 Aumentó costo"
    if var < 0:
        return "🟢 Bajó costo"
    return "🟡 Sin cambio"


def impacto_label(var):
    if pd.isna(var):
        return "Sin comparación"
    if var > 0:
        return "Desfavorable"
    if var < 0:
        return "Favorable"
    return "Neutro"


st.markdown("""
<style>
h1 {
    font-weight: 800;
    color: #1f2a44;
}
h2, h3 {
    color: #1f2a44;
}
[data-testid="stMetricValue"] {
    font-size: 27px;
}
.block-container {
    padding-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)


st.title("📊 Dashboard Mayores Contables LUX")
st.caption("Foco ejecutivo: control de costos, variaciones mensuales, apertura por rubro y movimientos que explican desvíos.")

try:
    df = cargar_datos()
except Exception as e:
    st.error("No se pudo cargar la base desde Google Sheets.")
    st.exception(e)
    st.stop()

if df.empty:
    st.warning("La base está vacía.")
    st.stop()

with st.sidebar:
    st.header("Filtros generales")

    meses_all = sorted([m for m in df["Mes"].dropna().unique() if m != "NaT"])
    sucursales_all = sorted(df["Sucursal"].dropna().astype(str).unique())

    suc_sel = st.multiselect("Sucursal", sucursales_all, default=sucursales_all)

    df_filtrado = df.copy()
    if suc_sel:
        df_filtrado = df_filtrado[df_filtrado["Sucursal"].isin(suc_sel)]

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Control de Costos",
    "📑 P&L",
    "🏢 Centros de costo",
    "🧾 Control signos",
    "🔎 Drilldown"
])


with tab1:
    st.subheader("🎯 Control de costos controlables y no controlables")

    centros_foco = [c for c in ["Repuestos", "Tl. Mec.", "Mayorista", "ChapyPintu"] if f"{c}_Gestion" in df_filtrado.columns]
    centros_restantes = [c for c in CENTROS_COSTO if c not in centros_foco and f"{c}_Gestion" in df_filtrado.columns]
    centros_opciones = centros_foco + centros_restantes

    colf1, colf2, colf3 = st.columns(3)

    with colf1:
        centro = st.selectbox(
            "Centro de costo / sector",
            centros_opciones,
            index=0 if centros_opciones else None
        )

    with colf2:
        grupos_costos = [
            "Costos Controlables",
            "Costos No Controlables"
        ]

        grupos_sel = st.multiselect(
            "Categoría de costos",
            grupos_costos,
            default=grupos_costos
        )

    with colf3:
        modo_meses = st.selectbox(
            "Período a comparar",
            ["Últimos 2 meses", "Últimos 4 meses", "Selección manual"],
            index=1
        )

    meses_disponibles = sorted(df_filtrado["Mes"].dropna().unique())

    if modo_meses == "Últimos 2 meses":
        meses_sel = meses_disponibles[-2:]
    elif modo_meses == "Últimos 4 meses":
        meses_sel = meses_disponibles[-4:]
    else:
        meses_sel = st.multiselect(
            "Elegí los meses",
            meses_disponibles,
            default=meses_disponibles[-4:]
        )

    campo_cc = f"{centro}_Gestion"

    base_costos = df_filtrado[
        (df_filtrado["Grupo_PNL"].isin(grupos_sel)) &
        (df_filtrado["Mes"].isin(meses_sel))
    ].copy()

    base_costos["Importe_CC"] = base_costos[campo_cc]

    base_costos = base_costos[base_costos["Importe_CC"] != 0].copy()

    if base_costos.empty:
        st.info("No hay datos de costos para los filtros seleccionados.")
    else:
        meses_ordenados = sorted(base_costos["Mes"].unique())

        mes_actual = meses_ordenados[-1]
        mes_anterior = meses_ordenados[-2] if len(meses_ordenados) >= 2 else None

        total_actual = base_costos.loc[base_costos["Mes"] == mes_actual, "Importe_CC"].sum()
        total_anterior = base_costos.loc[base_costos["Mes"] == mes_anterior, "Importe_CC"].sum() if mes_anterior else np.nan
        var_total = total_actual - total_anterior if mes_anterior else np.nan
        var_total_pct = var_total / abs(total_anterior) if mes_anterior and total_anterior != 0 else np.nan

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Sector analizado", centro)
        c2.metric(f"Costo {mes_actual}", fmt_money(total_actual))
        c3.metric("Variación vs mes anterior", fmt_money(var_total), fmt_pct(var_total_pct))
        c4.metric("Lectura", impacto_label(var_total))

        st.divider()

        evolucion_grupo = (
            base_costos.groupby(["Mes", "Grupo_PNL"], as_index=False)["Importe_CC"]
            .sum()
            .sort_values("Mes")
        )

        st.markdown("### 1. Evolución mensual general")

        fig = px.line(
            evolucion_grupo,
            x="Mes",
            y="Importe_CC",
            color="Grupo_PNL",
            markers=True,
            title=f"Evolución mensual de costos - {centro}"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 2. Apertura por categoría y rubro")

        apertura = (
            base_costos.groupby(["Grupo_PNL", "Concepto_PNL", "Mes"], as_index=False)["Importe_CC"]
            .sum()
        )

        pivot = apertura.pivot_table(
            index=["Grupo_PNL", "Concepto_PNL"],
            columns="Mes",
            values="Importe_CC",
            aggfunc="sum",
            fill_value=0
        ).reset_index()

        for m in meses_ordenados:
            if m not in pivot.columns:
                pivot[m] = 0

        if len(meses_ordenados) >= 2:
            pivot["Mes anterior"] = pivot[mes_anterior]
            pivot["Mes actual"] = pivot[mes_actual]
            pivot["Variación $"] = pivot["Mes actual"] - pivot["Mes anterior"]
            pivot["Variación %"] = np.where(
                pivot["Mes anterior"].abs() > 0,
                pivot["Variación $"] / pivot["Mes anterior"].abs(),
                np.nan
            )
        else:
            pivot["Mes anterior"] = np.nan
            pivot["Mes actual"] = pivot[mes_actual]
            pivot["Variación $"] = np.nan
            pivot["Variación %"] = np.nan

        pivot["Semáforo"] = pivot["Variación $"].apply(semaforo_variacion_costos)
        pivot["Impacto"] = pivot["Variación $"].apply(impacto_label)
        pivot["Impacto_abs"] = pivot["Variación $"].abs()

        pivot = pivot.sort_values("Impacto_abs", ascending=False)

        pivot_mostrar = pivot.copy()
        for col in ["Mes anterior", "Mes actual", "Variación $"]:
            pivot_mostrar[col] = pivot_mostrar[col].apply(fmt_money)
        pivot_mostrar["Variación %"] = pivot_mostrar["Variación %"].apply(fmt_pct)

        st.dataframe(
            pivot_mostrar[[
                "Grupo_PNL",
                "Concepto_PNL",
                "Mes anterior",
                "Mes actual",
                "Variación $",
                "Variación %",
                "Semáforo",
                "Impacto"
            ]],
            use_container_width=True,
            height=430
        )

        st.markdown("### 3. Rubros que más explican el cambio")

        top_var = pivot.dropna(subset=["Variación $"]).copy()
        top_var = top_var[top_var["Variación $"] != 0].head(12)

        if not top_var.empty:
            fig = px.bar(
                top_var,
                x="Variación $",
                y="Concepto_PNL",
                color="Grupo_PNL",
                orientation="h",
                title="Principales variaciones vs mes anterior"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay variaciones suficientes para graficar.")

        st.markdown("### 4. Insight ejecutivo automático")

        if len(meses_ordenados) >= 2 and not pivot.empty:
            aumentos = pivot[pivot["Variación $"] > 0].sort_values("Variación $", ascending=False)
            mejoras = pivot[pivot["Variación $"] < 0].sort_values("Variación $", ascending=True)

            texto = ""

            if var_total > 0:
                texto += f"🔴 En **{centro}**, los costos seleccionados aumentaron **{fmt_money(var_total)}** en **{mes_actual}** versus **{mes_anterior}**. "
            elif var_total < 0:
                texto += f"🟢 En **{centro}**, los costos seleccionados bajaron **{fmt_money(abs(var_total))}** en **{mes_actual}** versus **{mes_anterior}**. "
            else:
                texto += f"🟡 En **{centro}**, los costos seleccionados no tuvieron variación relevante entre **{mes_anterior}** y **{mes_actual}**. "

            if not aumentos.empty:
                p = aumentos.iloc[0]
                texto += f"El principal aumento se observa en **{p['Concepto_PNL']}**, con una suba de **{fmt_money(p['Variación $'])}**. "

            if not mejoras.empty:
                m = mejoras.iloc[0]
                texto += f"La principal mejora se observa en **{m['Concepto_PNL']}**, con una baja de **{fmt_money(abs(m['Variación $']))}**. "

            texto += "Abajo se muestran los movimientos individuales que explican estos cambios."

            st.info(texto)

        st.markdown("### 5. Movimientos que explican los desvíos")

        if len(meses_ordenados) >= 2 and not top_var.empty:
            concepto_focus = st.selectbox(
                "Elegí un concepto para ver movimientos",
                top_var["Concepto_PNL"].tolist(),
                index=0
            )
        else:
            concepto_focus = st.selectbox(
                "Elegí un concepto para ver movimientos",
                sorted(base_costos["Concepto_PNL"].unique())
            )

        movimientos = base_costos[
            (base_costos["Concepto_PNL"] == concepto_focus) &
            (base_costos["Mes"].isin([mes_actual] + ([mes_anterior] if mes_anterior else [])))
        ].copy()

        movimientos["Impacto_abs"] = movimientos["Importe_CC"].abs()
        movimientos = movimientos.sort_values(["Mes", "Impacto_abs"], ascending=[False, False])

        movimientos["Importe_CC_fmt"] = movimientos["Importe_CC"].apply(fmt_money)

        columnas_mov = [
            "Mes",
            "Fecha",
            "Sucursal",
            "Cuenta:",
            "Nombre cuenta",
            "Nombre del rubro",
            "Grupo_PNL",
            "Concepto_PNL",
            "Detalle",
            "des res",
            "Detalle 2",
            "Importe_CC_fmt"
        ]

        columnas_mov = [c for c in columnas_mov if c in movimientos.columns]

        st.dataframe(
            movimientos[columnas_mov].head(80),
            use_container_width=True,
            height=520
        )

        st.download_button(
            "⬇️ Descargar movimientos del análisis",
            data=movimientos.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"movimientos_costos_{centro}_{concepto_focus}.csv",
            mime="text/csv"
        )


with tab2:
    st.subheader("📑 P&L resumido")

    campo_importe = "Parcial_Gestion"
    pnl = construir_pnl(df_filtrado, campo_importe)

    st.dataframe(
        pnl[["Logica", "Grupo", "Concepto", "Rubros", "Importe_fmt"]],
        use_container_width=True,
        height=720
    )


with tab3:
    st.subheader("🏢 Centros de costo")

    resumen = pd.DataFrame({
        "Centro de costo": [c for c in CENTROS_COSTO if f"{c}_Gestion" in df_filtrado.columns],
        "Importe": [df_filtrado[f"{c}_Gestion"].sum() for c in CENTROS_COSTO if f"{c}_Gestion" in df_filtrado.columns]
    })

    resumen["Importe_fmt"] = resumen["Importe"].apply(fmt_money)
    resumen = resumen.sort_values("Importe", ascending=False)

    fig = px.bar(
        resumen,
        x="Centro de costo",
        y="Importe",
        title="Resultado por centro de costo"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(resumen[["Centro de costo", "Importe_fmt"]], use_container_width=True)


with tab4:
    st.subheader("🧾 Control de signos")

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


with tab5:
    st.subheader("🔎 Drilldown contable")

    buscar = st.text_input("Buscar por cuenta, detalle, descripción, proveedor o rubro")

    drill = df_filtrado.copy()

    if buscar:
        texto = buscar.lower()
        mask = pd.Series(False, index=drill.index)

        for col in ["Nombre cuenta", "Detalle", "des res", "Detalle 2", "Nombre del rubro"]:
            if col in drill.columns:
                mask = mask | drill[col].astype(str).str.lower().str.contains(texto, na=False)

        drill = drill[mask]

    drill["Parcial_fmt"] = drill["Parcial"].apply(fmt_money)
    drill["Parcial_Gestion_fmt"] = drill["Parcial_Gestion"].apply(fmt_money)

    columnas = [
        "Fecha",
        "Mes",
        "Sucursal",
        "Cuenta:",
        "Nombre cuenta",
        "Rubro_calc",
        "Nombre del rubro",
        "Grupo_PNL",
        "Concepto_PNL",
        "Signo_rubro",
        "Detalle",
        "des res",
        "Detalle 2",
        "Parcial_fmt",
        "Parcial_Gestion_fmt"
    ]

    columnas = [c for c in columnas if c in drill.columns]

    st.dataframe(
        drill[columnas],
        use_container_width=True,
        height=650
    )

    st.download_button(
        "⬇️ Descargar drilldown filtrado",
        data=drill.to_csv(index=False).encode("utf-8-sig"),
        file_name="drilldown_mayores_lux.csv",
        mime="text/csv"
    )
# =========================
# TAB PROVEEDORES
# =========================

import re

def extraer_factura(texto):
    if pd.isna(texto):
        return ""

    texto = str(texto)

    patrones = [
        r'(F[A-Z]\s?\d{4}[- ]?\d{4,8})',
        r'([A-Z]{1,2}\d{4}[- ]\d{4,8})',
        r'(\d{4}[- ]\d{8})'
    ]

    for patron in patrones:
        match = re.search(patron, texto)
        if match:
            return match.group(1)

    return ""


def extraer_proveedor(row):

    textos = []

    for col in ["Detalle 2", "des res", "Detalle"]:
        if col in row and pd.notna(row[col]):
            textos.append(str(row[col]))

    texto = " ".join(textos).upper()

    basura = [
        "FACTURA",
        "RECIBO",
        "NC",
        "ND",
        "FC",
        "FA",
        "FB",
        "COMPRA",
        "PAGO"
    ]

    proveedor = texto

    for b in basura:
        proveedor = proveedor.replace(b, "")

    proveedor = re.sub(r'\d+', ' ', proveedor)
    proveedor = re.sub(r'[-_/]', ' ', proveedor)
    proveedor = re.sub(r'\s+', ' ', proveedor)

    proveedor = proveedor.strip()

    palabras = proveedor.split(" ")

    palabras = [p for p in palabras if len(p) > 2]

    proveedor = " ".join(palabras[:4])

    if proveedor == "":
        proveedor = "SIN IDENTIFICAR"

    return proveedor


df_filtrado["Factura_detectada"] = (
    df_filtrado["Detalle"].astype(str).apply(extraer_factura)
)

df_filtrado["Proveedor_detectado"] = (
    df_filtrado.apply(extraer_proveedor, axis=1)
)

tab_prov = st.tabs(["🏭 Proveedores"])[0]

with tab_prov:

    st.subheader("🏭 Análisis de proveedores")

    colp1, colp2 = st.columns(2)

    with colp1:
        centro_prov = st.selectbox(
            "Centro de costo",
            [c for c in CENTROS_COSTO if f"{c}_Gestion" in df_filtrado.columns],
            index=3
        )

    with colp2:
        categoria_prov = st.multiselect(
            "Categoría",
            [
                "Costos Controlables",
                "Costos No Controlables"
            ],
            default=[
                "Costos Controlables",
                "Costos No Controlables"
            ]
        )

    campo_prov = f"{centro_prov}_Gestion"

    base_prov = df_filtrado[
        df_filtrado["Grupo_PNL"].isin(categoria_prov)
    ].copy()

    base_prov["Importe_Prov"] = base_prov[campo_prov]

    base_prov = base_prov[
        base_prov["Importe_Prov"] != 0
    ]

    prov_mes = (
        base_prov.groupby(
            ["Mes", "Proveedor_detectado"],
            as_index=False
        )["Importe_Prov"]
        .sum()
    )

    ranking = (
        prov_mes.groupby(
            "Proveedor_detectado",
            as_index=False
        )["Importe_Prov"]
        .sum()
        .sort_values("Importe_Prov", ascending=False)
        .head(20)
    )

    ranking["Importe_fmt"] = ranking["Importe_Prov"].apply(fmt_money)

    st.markdown("### Top proveedores")

    fig = px.bar(
        ranking,
        x="Proveedor_detectado",
        y="Importe_Prov",
        title="Top proveedores por gasto"
    )

    fig.update_layout(
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        ranking[
            [
                "Proveedor_detectado",
                "Importe_fmt"
            ]
        ],
        use_container_width=True
    )

    st.markdown("### Evolución mensual")

    top10 = ranking[
        "Proveedor_detectado"
    ].head(10).tolist()

    evo = prov_mes[
        prov_mes["Proveedor_detectado"].isin(top10)
    ]

    fig2 = px.line(
        evo,
        x="Mes",
        y="Importe_Prov",
        color="Proveedor_detectado",
        markers=True,
        title="Evolución mensual proveedores"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Variaciones detectadas")

    pivot = prov_mes.pivot_table(
        index="Proveedor_detectado",
        columns="Mes",
        values="Importe_Prov",
        aggfunc="sum",
        fill_value=0
    ).reset_index()

    meses_cols = [
        c for c in pivot.columns
        if c != "Proveedor_detectado"
    ]

    meses_cols = sorted(meses_cols)

    if len(meses_cols) >= 2:

        mes_ant = meses_cols[-2]
        mes_act = meses_cols[-1]

        pivot["Variacion"] = (
            pivot[mes_act] - pivot[mes_ant]
        )

        pivot["Variacion_%"] = np.where(
            pivot[mes_ant].abs() > 0,
            pivot["Variacion"] / pivot[mes_ant].abs(),
            np.nan
        )

        pivot = pivot.sort_values(
            "Variacion",
            ascending=False
        )

        pivot["Mes anterior"] = pivot[
            mes_ant
        ].apply(fmt_money)

        pivot["Mes actual"] = pivot[
            mes_act
        ].apply(fmt_money)

        pivot["Variación"] = pivot[
            "Variacion"
        ].apply(fmt_money)

        pivot["Variación %"] = pivot[
            "Variacion_%"
        ].apply(fmt_pct)

        st.dataframe(
            pivot[
                [
                    "Proveedor_detectado",
                    "Mes anterior",
                    "Mes actual",
                    "Variación",
                    "Variación %"
                ]
            ].head(30),
            use_container_width=True,
            height=500
        )

    st.markdown("### Movimientos asociados")

    proveedor_sel = st.selectbox(
        "Proveedor",
        sorted(
            base_prov["Proveedor_detectado"]
            .dropna()
            .unique()
        )
    )

    movs = base_prov[
        base_prov["Proveedor_detectado"]
        == proveedor_sel
    ].copy()

    movs = movs.sort_values(
        "Importe_Prov",
        ascending=False
    )

    movs["Importe_fmt"] = (
        movs["Importe_Prov"]
        .apply(fmt_money)
    )

    columnas_mov = [
        "Mes",
        "Fecha",
        "Sucursal",
        "Factura_detectada",
        "Proveedor_detectado",
        "Nombre del rubro",
        "Concepto_PNL",
        "Detalle",
        "des res",
        "Detalle 2",
        "Importe_fmt"
    ]

    columnas_mov = [
        c for c in columnas_mov
        if c in movs.columns
    ]

    st.dataframe(
        movs[columnas_mov].head(100),
        use_container_width=True,
        height=550
    )
