import re
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Dashboard Mayores Contables LUX", page_icon="📊", layout="wide")

SHEET_ID = "1Yu1UTf6LvdGTmlUsFgmwkDHsNckUoDv1tZDK1V9V0mE"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

CENTROS_COSTO = ["Vtas 0 Km", "Vtas Usado", "PPAA", "Repuestos", "Tl. Mec.", "Finanzas", "Mayorista", "ChapyPintu", "Central", "Administr."]
CENTROS_POSVENTA = ["Repuestos", "Tl. Mec.", "Mayorista", "ChapyPintu"]

SIGNO_RUBRO = {
    "VENTAS":"-", "INCENTIVOS":"-", "COMIS. P/VTA DIRECTA":"-", "INGRESO EXTRAORDIN":"-",
    "OTROS ING FINANCIERO":"-", "INGRESOS SEGUROS":"-", "COMIS CONSIGNACIONES":"-", "SOBRANTES DE INV.":"-",
    "INTERESES IMPOSITIVO":"+", "MERMAS DE INVENTARIO":"+", "GTOS GESTIO JUDICIAL":"+", "COMISION CHANGO CAR":"+",
    "UTILES Y MAT. DE OFI":"+", "Adm Ctral (No Usar)":"+", "COMIS. A VENDEDORES":"+", "SUELDOS ADM. Y CS.SS":"+",
    "SEGUROS":"+", "SUELDOS ADM CENTRAL":"+", "GTOS ATENCION CLIENT":"+", "UTILES Y MAT DE OFIC":"+",
    "EGRESO EXTRAORDINARI":"+", "TELEFONO E INTERNET":"+", "MANT. RODADOS":"+", "IMPUESTOS Y TASAS":"+",
    "OTROS GTOS FIJOS":"+", "PREPARAC. Y PREENTRE":"+", "SEGURIDAD Y VIGILANC":"+", "HERRAM. MAT. Y FLETE":"+",
    "EGRESOS GESTORIA":"+", "MOVILIDAD Y VIATICOS":"+", "ALQUILERES":"+", "LUZ,AGUA Y GAS":"+",
    "HONORARIOS PROFESION":"+", "Serv. Limpieza":"+", "PUBLICIDAD Y PROMOC.":"+", "COSTO DE REAC. Y ACC":"+",
    "MANTENIM. BS. DE USO":"+", "SERV LUZ.TEL.SUSCRIP":"+", "COM. Y GTOS BANCARIO":"+", "INGRESOS GESTORIA":"+",
    "SS. GRAT. Y CS. INT.":"+", "AMORTIZACIONES":"+", "OTROS EGR. FINANCIER":"+", "IMPUESTOS FINANCIAC":"+",
    "INT. FINANC. VEHICUL":"+", "DESCUENTOS S/ VTAS.":"+", "COSTO DE VENTAS":"+"
}

PNL = [
    ("mas","Ventas",["4-1"],"Margen Bruto Gestión Comercial"),("menos","Descuentos sobre ventas",["4-2"],"Margen Bruto Gestión Comercial"),
    ("menos","Costo de Ventas",["5-1"],"Margen Bruto Gestión Comercial"),("menos","Rdo. Neto Gestoría",["6-1","6-2"],"Margen Bruto Gestión Comercial"),
    ("igual","Margen Bruto Gestión Comercial",[],"Margen Bruto Gestión Comercial"),("menos","Costo Reacondic. y Acces.",["5-2"],"Margen Bruto Secundario"),
    ("igual","Margen Bruto Primario",[],"Margen Bruto Secundario"),("mas","Incentivos",["4-3"],"Margen Bruto Secundario"),
    ("mas","Incentivo Devengado",["4-4"],"Margen Bruto Secundario"),("mas","Comisión Consignaciones",["6-3"],"Margen Bruto Secundario"),
    ("menos","Comisión Pagadas",["6-6"],"Margen Bruto Secundario"),("mas","Comisión P/Vta Directa",["10-1"],"Margen Bruto Secundario"),
    ("igual","Margen Bruto Secundario",[],"Margen Bruto Secundario"),("menos","Mermas de Inventarios",["5-3"],"Otros Ingresos / Egresos"),
    ("menos","Sobrantes de Inventarios",["5-4"],"Otros Ingresos / Egresos"),("menos","Pérdida IVA Usados",["5-5"],"Otros Ingresos / Egresos"),
    ("menos","Horas no aplicadas mecánicos",["6-4"],"Otros Ingresos / Egresos"),("mas","Resultado Venta de PPAA MS",["6-5"],"Otros Ingresos / Egresos"),
    ("mas","Ingresos Seguros y Comis Gestión Vta",["10-4"],"Otros Ingresos / Egresos"),("menos","Egresos Seguros",["11-5"],"Otros Ingresos / Egresos"),
    ("igual","Utilidad Bruta",[],"Utilidad Bruta"),("menos","Comisiones sobre Ventas",["7-2"],"Costos Controlables"),
    ("menos","Sueldos y Cargas Sociales",["8-1"],"Costos Controlables"),("menos","Sueldos Administración y C. Soc.",["8-4"],"Costos Controlables"),
    ("menos","Gastos de Atención clientes",["7-1"],"Costos Controlables"),("menos","Servicios gratuitos y Cargos internos",["7-4"],"Costos Controlables"),
    ("menos","Herramientas, materiales y fletes",["7-6"],"Costos Controlables"),("menos","Publicidad y Promoción",["8-2"],"Costos Controlables"),
    ("menos","Mantenimiento rodados y equipos",["8-3"],"Costos Controlables"),("menos","Movilidad y Viáticos",["8-6"],"Costos Controlables"),
    ("menos","Mantenimiento Bienes de Uso",["8-8"],"Costos Controlables"),("menos","Fuerza motriz, luz, agua y gas",["8-9"],"Costos Controlables"),
    ("menos","Teléfonos e internet",["8-10"],"Costos Controlables"),("menos","Serv. Limpieza",["8-11"],"Costos Controlables"),
    ("menos","Útiles y materiales de oficina",["8-12"],"Costos Controlables"),("menos","Otros Gastos Fijos",["8-13"],"Costos Controlables"),
    ("menos","Alquileres",["8-14"],"Costos Controlables"),("menos","Previsiones Varias",["8-17"],"Costos Controlables"),
    ("menos","Deudores Incobrables",["8-19"],"Costos Controlables"),("menos","Preparación y entrega",["7-3"],"Costos Controlables"),
    ("menos","Seguridad y vigilancia",["8-20"],"Costos Controlables"),("menos","Impuestos",["7-5"],"Costos No Controlables"),
    ("menos","Honorarios profesionales",["8-5"],"Costos No Controlables"),("menos","Recupero de Gastos Toyota",["8-7"],"Costos No Controlables"),
    ("menos","Amortizaciones",["8-15"],"Costos No Controlables"),("menos","Seguros",["8-16"],"Costos No Controlables"),
    ("menos","Impuestos y tasas",["8-18"],"Costos No Controlables"),("igual","Utilidad Operativa Sucursal",[],"Utilidad Operativa Sucursal"),
    ("menos","Sueldos Gtes y Jefes Suc.",["9-1"],"Controlables de Estructura"),("menos","Sueldos Adm. Central",["9-2"],"Controlables de Estructura"),
    ("menos","Prestaciones La Luz",["9-3"],"Controlables de Estructura"),("menos","Movilidad y Viáticos Central",["9-4"],"Controlables de Estructura"),
    ("menos","Mantenimiento Bs Uso Central",["9-5"],"Controlables de Estructura"),("menos","Útiles y materiales de oficina Central",["9-6"],"Controlables de Estructura"),
    ("menos","Serv., Energía, Suscripciones Adm Central",["9-7"],"Controlables de Estructura"),("menos","Alquileres Adm Central",["9-9"],"Controlables de Estructura"),
    ("menos","Amortizaciones Estructura",["9-8"],"Costos no Controlables de Estructura"),("igual","Utilidad Operativa",[],"Utilidad Operativa"),
    ("mas","Intereses Financiación Vehículos",["10-2"],"Ingresos Financieros"),("mas","Otros Ingresos Financieros",["10-3"],"Ingresos Financieros"),
    ("menos","Impuestos Financiación",["11-1"],"Egresos Financieros"),("menos","Intereses Impositivos",["11-2"],"Egresos Financieros"),
    ("menos","Comisiones y gastos bancarios",["11-3"],"Egresos Financieros"),("menos","Financiación cap trab",["11-4"],"Egresos Financieros"),
    ("igual","Resultado antes de Impuestos",[],"Resultado antes de Impuestos"),("menos","Impuesto a las Ganancias",[],"Impuesto a las Ganancias"),
    ("igual","Resultado después de Impuestos",[],"Resultado después de Impuestos"),
    ("info","Egresos Dirección",["9-10"],"Fuera del Resultado Modelado"),
    ("info","Ingresos Extraordinarios",["12-1"],"Fuera del Resultado Modelado"),
    ("info","Egresos Extraordinarios",["12-2"],"Fuera del Resultado Modelado")
]

# ---------- formatos y limpieza ----------
def limpiar_numero(x):
    if pd.isna(x): return 0.0
    if isinstance(x, (int, float, np.number)): return float(x)
    s = str(x).strip().replace("$", "").replace(" ", "").replace("\xa0", "")
    if s == "": return 0.0
    if "," in s and "." in s: s = s.replace(".", "").replace(",", ".")
    elif "," in s: s = s.replace(",", ".")
    try: return float(s)
    except Exception: return 0.0

def limpiar_texto(x): return "" if pd.isna(x) else str(x).strip()
def normalizar_rubro(x): return "" if pd.isna(x) else str(x).strip().replace(".0", "").replace(" ", "")

def fmt_money(x):
    try: x = float(x)
    except Exception: x = 0
    return "$ {:,.0f}".format(x).replace(",", ".")

def fmt_money_short(x):
    try: x = float(x)
    except Exception: x = 0
    signo = "-" if x < 0 else ""; x = abs(x)
    if x >= 1_000_000_000: return f"{signo}$ {x/1_000_000_000:.1f}B"
    if x >= 1_000_000: return f"{signo}$ {x/1_000_000:.1f}M"
    if x >= 1_000: return f"{signo}$ {x/1_000:.0f}K"
    return f"{signo}$ {x:.0f}"

def fmt_pct(x):
    try:
        if pd.isna(x): return ""
        return "{:.1%}".format(float(x))
    except Exception: return ""

def signo_factor_por_rubro(nombre_rubro): return -1 if SIGNO_RUBRO.get(limpiar_texto(nombre_rubro), "+") == "-" else 1

def mapa_rubro_a_pnl():
    return pd.DataFrame([{"Rubro_calc": r, "Concepto_PNL": concepto, "Grupo_PNL": grupo, "Logica_PNL": logica} for logica, concepto, rubros, grupo in PNL for r in rubros])

# ---------- proveedor ----------
def extraer_factura_texto(texto):
    if pd.isna(texto): return ""
    texto = str(texto).upper()
    for patron in [r'\bF[A-Z]\s?\d{4}[- ]?\d{4,8}\b', r'\b[A-Z]{1,2}\s?\d{4}[- ]?\d{4,8}\b', r'\b[A-Z]\d{10,14}\b', r'\b\d{4}[- ]\d{6,8}\b']:
        m = re.search(patron, texto)
        if m: return m.group(0).strip()
    return ""

def extraer_factura(row): return extraer_factura_texto(" ".join([str(row.get(c, "")) for c in ["Detalle", "des res", "Detalle 2"]]))

def normalizar_proveedor_nombre(proveedor):
    p = str(proveedor).upper().strip()
    reglas = {"ROQUE JUAN LOZANO":"ROQUE JUAN LOZANO", "LOZANO MARIA":"LOZANO MARIA", "TOYOTA ENTINA":"TOYOTA ENTINA", "TOYOTA ARGENTINA":"TOYOTA ARGENTINA", "OVERSOFT":"OVERSOFT", "EJE EJE LAS LOMAS":"EJE EJE LAS LOMAS", "MERCADO LIBRE":"MERCADO LIBRE", "MERCADOLIBRE":"MERCADO LIBRE", "MERCADO PAGO":"MERCADO LIBRE", "META":"META", "FACEBOOK":"META", "GOOGLE":"GOOGLE", "YPF":"YPF", "SHELL":"SHELL", "AXION":"AXION", "TELECOM":"TELECOM", "PERSONAL":"TELECOM", "MOVISTAR":"MOVISTAR", "CLARO":"CLARO", "EDESA":"EDESA", "GASNOR":"GASNOR", "BETA SERVICIO LIMPIEZA":"BETA SERVICIO LIMPIEZA", "ATIEMPO SEGURIDAD":"ATIEMPO SEGURIDAD", "CHANGO TRUCK":"CHANGO TRUCK"}
    for k, v in reglas.items():
        if k in p: return v
    for q in ["ALQ LOC","ALQ LOCAL","MAYOR VALOR","MAR","FEB","ABR","ENE","NOCT","DIURNAS","MEJORAS","SOPORTE EVOLUTIVO","MANTENIMIENTO","ABONO","CUOTA","PAGO","FACTURA"]:
        p = p.replace(q, " ")
    palabras = [w for w in re.sub(r'\s+', ' ', p).strip().split(" ") if len(w) > 2]
    return " ".join(palabras[:3]) if palabras else "SIN IDENTIFICAR"

def extraer_proveedor(row):
    texto = " ".join([str(row.get(c, "")) for c in ["Detalle 2", "des res", "Detalle"]]).upper()
    factura = extraer_factura_texto(texto)
    if factura and factura in texto: texto = texto[texto.find(factura)+len(factura):]
    for b in ["FACTURA","RECIBO","COMP","COMPROBANTE","PAGO","PAGOS","TRANSFERENCIA","FC","FA","FB","NC","ND","CUIT","IVA","ARG","S.A.","SA","SRL","S.R.L.","LTDA","NRO","Nº","NUM","PESOS"]:
        texto = texto.replace(b, " ")
    texto = re.sub(r'\d+', ' ', texto); texto = re.sub(r'[-_/.,:;()]+', ' ', texto); texto = re.sub(r'\s+', ' ', texto).strip()
    palabras = [p for p in texto.split(" ") if len(p) > 2]
    proveedor = " ".join(palabras[:6]).strip() or "SIN IDENTIFICAR"
    return normalizar_proveedor_nombre(proveedor)

def categoria_proveedor(proveedor, detalle):
    texto = f"{proveedor} {detalle}".upper()
    reglas = {"Marketing digital":["META","GOOGLE","FACEBOOK","INSTAGRAM","ADS","PUBLICIDAD"], "Marketplace / plataformas":["MERCADO LIBRE","MERCADOLIBRE","MERCADO PAGO"], "Combustible / movilidad":["YPF","SHELL","AXION","COMBUSTIBLE","NAFTA","GASOIL"], "Telecomunicaciones":["TELECOM","PERSONAL","MOVISTAR","CLARO","INTERNET","TELEFONO"], "Energía / servicios":["EDESA","GASNOR","LUZ","GAS","AGUA","ENERGIA"], "Seguros":["SEGURO","SANCOR","FEDERACION","MAPFRE","ZURICH"], "Limpieza / seguridad":["LIMPIEZA","SEGURIDAD","VIGILANC","ATIEMPO"], "Toyota / terminal":["TOYOTA"], "Sistemas / software":["OVERSOFT","SIAC","SISTEMA","SOFTWARE"], "Alquileres":["LOZANO","ALQUILER","ALQ"], "Honorarios / profesionales":["HONORARIO","ESTUDIO","ASESOR","CONSULT"]}
    for cat, keys in reglas.items():
        if any(k in texto for k in keys): return cat
    return "Otros / no clasificado"

# ---------- lógica de gestión ----------
def semaforo_variacion(var):
    if pd.isna(var): return "⚪ Sin comparación"
    if var > 0: return "🔴 Aumentó costo"
    if var < 0: return "🟢 Bajó costo"
    return "🟡 Sin cambio"

def severidad_y_motivo(row):
    var_abs = abs(row.get("Variación $", row.get("Evolución $", 0))) if not pd.isna(row.get("Variación $", row.get("Evolución $", np.nan))) else 0
    var_pct_raw = row.get("Variación %", row.get("Evolución %", np.nan)); var_pct = abs(var_pct_raw) if not pd.isna(var_pct_raw) else 0
    actual = abs(row.get("Mes actual", 0)) if not pd.isna(row.get("Mes actual", np.nan)) else 0
    anterior = abs(row.get("Mes anterior", 0)) if not pd.isna(row.get("Mes anterior", np.nan)) else 0
    score, motivos = 0, []
    if anterior == 0 and actual > 0: score += 20; motivos.append("sin gasto en mes anterior")
    if var_abs >= 5_000_000: score += 40; motivos.append("variación mayor a $5M")
    elif var_abs >= 1_000_000: score += 25; motivos.append("variación mayor a $1M")
    elif var_abs >= 300_000: score += 10; motivos.append("variación mayor a $300K")
    if var_pct >= 1: score += 35; motivos.append("variación superior al 100%")
    elif var_pct >= 0.4: score += 20; motivos.append("variación superior al 40%")
    elif var_pct >= 0.15: score += 10; motivos.append("variación superior al 15%")
    if actual >= 5_000_000: score += 20; motivos.append("importe actual mayor a $5M")
    elif actual >= 1_000_000: score += 10; motivos.append("importe actual mayor a $1M")
    sev = "🔴 Crítico" if score >= 70 else "🟠 Alto" if score >= 45 else "🟡 Medio" if score >= 20 else "🟢 Bajo"
    return sev, "; ".join(motivos or ["impacto bajo o sin variación relevante"])

def tipo_evento(row):
    ant, act = row.get("Mes anterior", 0), row.get("Mes actual", 0)
    var = row.get("Variación $", row.get("Evolución $", 0)); var_pct = row.get("Variación %", row.get("Evolución %", np.nan))
    if ant == 0 and act > 0: return "🆕 Nuevo / sin histórico"
    if not pd.isna(var_pct) and var_pct > 1: return "📈 Crecimiento abrupto"
    if var > 0: return "🔴 Mayor presión"
    if var < 0: return "🟢 Mejora"
    return "🟡 Estable"

def preparar_para_labels(fig):
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode="hide")
    return fig


def ordenar_categorias_por_total(df, categoria_col, valor_col):
    if df.empty or categoria_col not in df.columns or valor_col not in df.columns:
        return []
    return (
        df.groupby(categoria_col, as_index=False)[valor_col]
        .sum()
        .sort_values(valor_col, ascending=False)[categoria_col]
        .astype(str)
        .tolist()
    )

def centros_disponibles(df): return list(dict.fromkeys([x for x in CENTROS_POSVENTA + CENTROS_COSTO if f"{x}_Gestion" in df.columns]))
def default_centros(disponibles, modo="repuestos"):
    if modo == "posventa":
        p = [c for c in CENTROS_POSVENTA if c in disponibles]
        return p if p else disponibles[:1]
    return ["Repuestos"] if "Repuestos" in disponibles else disponibles[:1]
def label_centros(centros_sel):
    if not centros_sel: return "Sin centros"
    p = [c for c in CENTROS_POSVENTA if c in centros_sel]
    if len(centros_sel) == len(p) and len(p) > 1: return "Todos Posventa"
    return " + ".join(centros_sel)
def campo_centros_gestion(df, centros_sel):
    cols = [f"{c}_Gestion" for c in centros_sel if f"{c}_Gestion" in df.columns]
    return df[cols].sum(axis=1) if cols else pd.Series(0, index=df.index)

@st.cache_data(ttl=600)
def cargar_datos():
    df = pd.read_csv(CSV_URL)
    df.columns = [str(c).strip() for c in df.columns]
    if "Fecha" in df.columns:
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce", dayfirst=True)
        df["Mes"] = df["Fecha"].dt.to_period("M").astype(str)
    else:
        df["Fecha"] = pd.NaT; df["Mes"] = "Sin fecha"
    for col in ["Debe", "Haber", "Parcial"] + CENTROS_COSTO:
        df[col] = df[col].apply(limpiar_numero) if col in df.columns else 0.0
    if "Rub" in df.columns and "SRub" in df.columns:
        df["Rubro_calc"] = df["Rub"].apply(normalizar_rubro) + "-" + df["SRub"].apply(normalizar_rubro)
    elif "union" in df.columns:
        df["Rubro_calc"] = df["union"].apply(normalizar_rubro)
    else: df["Rubro_calc"] = ""
    for col in ["Sucursal", "Nombre cuenta", "Cuenta:", "Cuenta", "Nombre del rubro", "Detalle", "des res", "Detalle 2", "Dpto", "Nro."]:
        if col not in df.columns: df[col] = ""
    if "Cuenta:" not in df.columns and "Cuenta" in df.columns: df["Cuenta:"] = df["Cuenta"]
    df["Sucursal"] = df["Sucursal"].fillna("Sin sucursal").astype(str)
    df["Nombre del rubro"] = df["Nombre del rubro"].apply(limpiar_texto)
    df["Signo_rubro"] = df["Nombre del rubro"].map(SIGNO_RUBRO).fillna("+")
    df["Factor_signo"] = df["Nombre del rubro"].apply(signo_factor_por_rubro)
    df["Parcial_Gestion"] = df["Parcial"] * df["Factor_signo"]
    for col in CENTROS_COSTO: df[f"{col}_Gestion"] = df[col] * df["Factor_signo"]
    df = df.merge(mapa_rubro_a_pnl(), on="Rubro_calc", how="left")
    df["Grupo_PNL"] = df["Grupo_PNL"].fillna("Sin clasificar"); df["Concepto_PNL"] = df["Concepto_PNL"].fillna("Sin clasificar"); df["Logica_PNL"] = df["Logica_PNL"].fillna("sin lógica")
    df["Factura_detectada"] = df.apply(extraer_factura, axis=1)
    df["Proveedor_detectado"] = df.apply(extraer_proveedor, axis=1)
    df["Texto_movimiento"] = df["Detalle"].astype(str) + " " + df["des res"].astype(str) + " " + df["Detalle 2"].astype(str)
    df["Categoria_proveedor"] = df.apply(lambda r: categoria_proveedor(r["Proveedor_detectado"], r["Texto_movimiento"]), axis=1)
    return df

def preparar_costos(df, centros_sel, grupos, meses):
    base = df[(df["Grupo_PNL"].isin(grupos)) & (df["Mes"].isin(meses))].copy()
    base["Importe_CC"] = campo_centros_gestion(base, centros_sel)
    return base[base["Importe_CC"] != 0].copy()

def tabla_variaciones(base, index_cols):
    meses = sorted(base["Mes"].dropna().unique())
    piv = base.pivot_table(index=index_cols, columns="Mes", values="Importe_CC", aggfunc="sum", fill_value=0).reset_index()
    if len(meses) >= 2:
        ant, act = meses[-2], meses[-1]
        piv["Mes anterior"] = piv[ant]; piv["Mes actual"] = piv[act]
        piv["Variación $"] = piv["Mes actual"] - piv["Mes anterior"]
        piv["Variación %"] = np.where(piv["Mes anterior"].abs() > 0, piv["Variación $"] / piv["Mes anterior"].abs(), np.nan)
    elif len(meses) == 1:
        act = meses[-1]; piv["Mes anterior"] = np.nan; piv["Mes actual"] = piv[act]; piv["Variación $"] = np.nan; piv["Variación %"] = np.nan
    else:
        piv["Mes anterior"] = np.nan; piv["Mes actual"] = np.nan; piv["Variación $"] = np.nan; piv["Variación %"] = np.nan
    sev = piv.apply(severidad_y_motivo, axis=1)
    piv["Severidad"] = [x[0] for x in sev]; piv["Motivo severidad"] = [x[1] for x in sev]
    piv["Tipo evento"] = piv.apply(tipo_evento, axis=1)
    piv["Semáforo"] = piv["Variación $"].apply(semaforo_variacion)
    piv["Impacto_abs"] = piv["Variación $"].abs()
    return piv.sort_values("Impacto_abs", ascending=False)


def _importe_rubros_mes(df, mes, rubros, centros_sel, magnitud=True):
    """
    Devuelve el importe imputado a los centros seleccionados para los rubros indicados.
    Usa las columnas monetarias de centro de costo, no Parcial_Gestion.
    """
    dmes = df[(df["Mes"] == mes) & (df["Rubro_calc"].isin(rubros))].copy()
    if dmes.empty:
        return 0.0
    valor = campo_centros_gestion(dmes, centros_sel).sum()
    return abs(valor) if magnitud else float(valor)


def _importe_texto_mes(df, mes, centros_sel, palabras_todas=None, palabras_alguna=None):
    """
    Busca movimientos no identificados por Rub/SRub a partir de Detalle/des res/Detalle 2/Nombre cuenta/Nombre rubro.
    Sirve para líneas especiales como Ajuste Costo de Reposición y Transferencia repuestos a taller.
    """
    dmes = df[df["Mes"] == mes].copy()
    if dmes.empty:
        return 0.0

    texto = (
        dmes["Detalle"].astype(str) + " " +
        dmes["des res"].astype(str) + " " +
        dmes["Detalle 2"].astype(str) + " " +
        dmes["Nombre cuenta"].astype(str) + " " +
        dmes["Nombre del rubro"].astype(str)
    ).str.upper()

    mask = pd.Series(True, index=dmes.index)
    if palabras_todas:
        for p in palabras_todas:
            mask &= texto.str.contains(str(p).upper(), na=False, regex=False)
    if palabras_alguna:
        mask_alguna = pd.Series(False, index=dmes.index)
        for p in palabras_alguna:
            mask_alguna |= texto.str.contains(str(p).upper(), na=False, regex=False)
        mask &= mask_alguna

    encontrados = dmes[mask].copy()
    if encontrados.empty:
        return 0.0
    return float(campo_centros_gestion(encontrados, centros_sel).sum())


def construir_pnl_mensual_validado(df, meses, centros_sel):
    """
    Replica la lógica validada contra la cuenta de resultados compartida:
    Margen Bruto Gestión Comercial
    -> Margen Bruto Primario
    -> Margen Bruto Secundario
    -> Otros Ingresos / Egresos
    -> Utilidad Bruta
    -> Transferencia Repuestos a Taller
    -> Costos Controlables / No Controlables
    -> Utilidad Operativa Sucursal
    -> Costos de Estructura
    -> Utilidad Operativa
    -> Resultado Financiero Operativo
    -> Resultado antes de Impuestos
    -> Impuesto a las Ganancias
    -> Resultado después de Impuestos

    Importante:
    - Los gastos se muestran como magnitud positiva, igual que en el modelo validado.
    - Descuentos e Impuesto a las Ganancias se muestran negativos.
    - La transferencia conserva signo según el/los centros seleccionados y se neutraliza al consolidar
      Repuestos + Taller, si la base contiene el movimiento explícito.
    - 9-10 / 12-1 / 12-2 se muestran aparte y NO se incorporan al resultado validado.
    """
    filas = []

    def add(concepto, grupo, rubros="", logica="", valores=None, tipo="detalle"):
        fila = {
            "Grupo": grupo,
            "Concepto": concepto,
            "Rubros": rubros,
            "Lógica": logica,
            "Tipo": tipo,
        }
        for m in meses:
            fila[m] = float(valores.get(m, 0.0)) if valores else 0.0
        fila["Acumulado"] = sum(fila[m] for m in meses)
        filas.append(fila)

    # Diccionarios mensuales para subtotales
    ventas = {}
    descuentos = {}
    costo_ventas = {}
    gestoria = {}
    mb_gestion = {}
    ajuste_repos = {}
    reacond = {}
    mb_primario = {}
    incentivos = {}
    incentivo_dev = {}
    consignaciones = {}
    comisiones_pagadas = {}
    com_vta_directa = {}
    mb_secundario = {}

    mermas = {}
    sobrantes = {}
    perdida_iva = {}
    horas_no_aplicadas = {}
    resultado_ppaa = {}
    ingresos_seguros = {}
    egresos_seguros = {}
    otros_ie = {}
    utilidad_bruta = {}
    transferencia = {}

    # Controlables
    controlables_rubros = [
        ("Comisiones sobre Ventas", ["7-2"]),
        ("Sueldos y Cargas Sociales", ["8-1"]),
        ("Sueldos Administración y C. Soc.", ["8-4"]),
        ("Gastos de Atención clientes", ["7-1"]),
        ("Servicios gratuitos y Cargos internos", ["7-4"]),
        ("Herramientas, materiales y fletes", ["7-6"]),
        ("Publicidad y Promoción", ["8-2"]),
        ("Mantenimiento rodados y equipos", ["8-3"]),
        ("Movilidad y Viáticos", ["8-6"]),
        ("Mantenimiento Bienes de Uso", ["8-8"]),
        ("Fuerza motriz, luz, agua y gas", ["8-9"]),
        ("Teléfonos e internet", ["8-10"]),
        ("Serv. Limpieza", ["8-11"]),
        ("Útiles y materiales de oficina", ["8-12"]),
        ("Otros Gastos Fijos", ["8-13"]),
        ("Alquileres", ["8-14"]),
        ("Previsiones Varias", ["8-17"]),
        ("Deudores Incobrables", ["8-19"]),
        ("Preparación y entrega", ["7-3"]),
        ("Seguridad y vigilancia", ["8-20"]),
    ]

    no_controlables_rubros = [
        ("Impuestos", ["7-5"]),
        ("Honorarios profesionales", ["8-5"]),
        ("Recupero de Gastos Toyota", ["8-7"]),
        ("Amortizaciones", ["8-15"]),
        ("Seguros", ["8-16"]),
        ("Impuestos y tasas", ["8-18"]),
    ]

    estructura_controlable_rubros = [
        ("Sueldos Gtes y Jefes Suc.", ["9-1"]),
        ("Sueldos Adm. Central", ["9-2"]),
        ("Prestaciones La Luz", ["9-3"]),
        ("Movilidad y Viáticos", ["9-4"]),
        ("Mantenimiento Bs Uso Central", ["9-5"]),
        ("Útiles y materiales de oficina", ["9-6"]),
        ("Serv., Energía, Suscripciones Adm Central", ["9-7"]),
        ("Alquileres Adm Central", ["9-9"]),
    ]

    estructura_no_controlable_rubros = [
        ("Amortizaciones", ["9-8"]),
    ]

    controlables_detalle = {nombre: {} for nombre, _ in controlables_rubros}
    no_controlables_detalle = {nombre: {} for nombre, _ in no_controlables_rubros}
    est_ctrl_detalle = {nombre: {} for nombre, _ in estructura_controlable_rubros}
    est_noctrl_detalle = {nombre: {} for nombre, _ in estructura_no_controlable_rubros}

    total_controlables = {}
    total_no_controlables = {}
    total_control_no_control = {}
    utilidad_operativa_sucursal = {}
    total_est_ctrl = {}
    total_est_noctrl = {}
    total_estructura = {}
    utilidad_operativa = {}

    int_fin_veh = {}
    otros_ing_fin = {}
    total_ing_fin = {}
    imp_fin = {}
    int_impositivos = {}
    com_gastos_banc = {}
    fin_cap_trab = {}
    total_egr_fin = {}
    resultado_fin_operativo = {}
    resultado_antes_imp = {}
    imp_ganancias = {}
    resultado_despues_imp = {}

    egresos_direccion = {}
    ingresos_extra = {}
    egresos_extra = {}

    for m in meses:
        ventas[m] = _importe_rubros_mes(df, m, ["4-1"], centros_sel, magnitud=True)
        descuentos[m] = -_importe_rubros_mes(df, m, ["4-2"], centros_sel, magnitud=True)
        costo_ventas[m] = _importe_rubros_mes(df, m, ["5-1"], centros_sel, magnitud=True)
        gestoria[m] = _importe_rubros_mes(df, m, ["6-1", "6-2"], centros_sel, magnitud=True)

        mb_gestion[m] = ventas[m] + descuentos[m] - costo_ventas[m] - gestoria[m]

        # Sin Rub/SRub fijo en el esquema compartido: se intenta localizar por texto.
        ajuste_repos[m] = abs(_importe_texto_mes(
            df, m, centros_sel,
            palabras_todas=["AJUSTE", "COSTO"],
            palabras_alguna=["REPOSICION", "REPOSICIÓN"]
        ))
        reacond[m] = _importe_rubros_mes(df, m, ["5-2"], centros_sel, magnitud=True)
        mb_primario[m] = mb_gestion[m] - ajuste_repos[m] - reacond[m]

        incentivos[m] = _importe_rubros_mes(df, m, ["4-3"], centros_sel, magnitud=True)
        incentivo_dev[m] = _importe_rubros_mes(df, m, ["4-4"], centros_sel, magnitud=True)
        consignaciones[m] = _importe_rubros_mes(df, m, ["6-3"], centros_sel, magnitud=True)
        comisiones_pagadas[m] = _importe_rubros_mes(df, m, ["6-6"], centros_sel, magnitud=True)
        com_vta_directa[m] = _importe_rubros_mes(df, m, ["10-1"], centros_sel, magnitud=True)

        mb_secundario[m] = (
            mb_primario[m]
            + incentivos[m]
            + incentivo_dev[m]
            + consignaciones[m]
            - comisiones_pagadas[m]
            + com_vta_directa[m]
        )

        mermas[m] = _importe_rubros_mes(df, m, ["5-3"], centros_sel, magnitud=True)
        sobrantes[m] = _importe_rubros_mes(df, m, ["5-4"], centros_sel, magnitud=True)
        perdida_iva[m] = _importe_rubros_mes(df, m, ["5-5"], centros_sel, magnitud=True)
        horas_no_aplicadas[m] = _importe_rubros_mes(df, m, ["6-4"], centros_sel, magnitud=True)
        resultado_ppaa[m] = _importe_rubros_mes(df, m, ["6-5"], centros_sel, magnitud=True)
        ingresos_seguros[m] = _importe_rubros_mes(df, m, ["10-4"], centros_sel, magnitud=True)
        egresos_seguros[m] = _importe_rubros_mes(df, m, ["11-5"], centros_sel, magnitud=True)

        otros_ie[m] = (
            - mermas[m]
            - sobrantes[m]
            - perdida_iva[m]
            - horas_no_aplicadas[m]
            + resultado_ppaa[m]
            + ingresos_seguros[m]
            - egresos_seguros[m]
        )
        utilidad_bruta[m] = mb_secundario[m] + otros_ie[m]

        # Línea especial. Mantiene el signo que traen los centros seleccionados.
        transferencia[m] = _importe_texto_mes(
            df, m, centros_sel,
            palabras_todas=["REPUEST"],
            palabras_alguna=["TRANSFER", "TALLER"]
        )

        tc = 0.0
        for nombre, rubros in controlables_rubros:
            val = _importe_rubros_mes(df, m, rubros, centros_sel, magnitud=True)
            controlables_detalle[nombre][m] = val
            tc += val
        total_controlables[m] = tc

        tnc = 0.0
        for nombre, rubros in no_controlables_rubros:
            val = _importe_rubros_mes(df, m, rubros, centros_sel, magnitud=True)
            no_controlables_detalle[nombre][m] = val
            tnc += val
        total_no_controlables[m] = tnc
        total_control_no_control[m] = tc + tnc

        utilidad_operativa_sucursal[m] = (
            utilidad_bruta[m]
            + transferencia[m]
            - total_controlables[m]
            - total_no_controlables[m]
        )

        tec = 0.0
        for nombre, rubros in estructura_controlable_rubros:
            val = _importe_rubros_mes(df, m, rubros, centros_sel, magnitud=True)
            est_ctrl_detalle[nombre][m] = val
            tec += val
        total_est_ctrl[m] = tec

        tenc = 0.0
        for nombre, rubros in estructura_no_controlable_rubros:
            val = _importe_rubros_mes(df, m, rubros, centros_sel, magnitud=True)
            est_noctrl_detalle[nombre][m] = val
            tenc += val
        total_est_noctrl[m] = tenc
        total_estructura[m] = tec + tenc

        utilidad_operativa[m] = utilidad_operativa_sucursal[m] - total_estructura[m]

        int_fin_veh[m] = _importe_rubros_mes(df, m, ["10-2"], centros_sel, magnitud=True)
        otros_ing_fin[m] = _importe_rubros_mes(df, m, ["10-3"], centros_sel, magnitud=True)
        total_ing_fin[m] = int_fin_veh[m] + otros_ing_fin[m]

        imp_fin[m] = _importe_rubros_mes(df, m, ["11-1"], centros_sel, magnitud=True)
        int_impositivos[m] = _importe_rubros_mes(df, m, ["11-2"], centros_sel, magnitud=True)
        com_gastos_banc[m] = _importe_rubros_mes(df, m, ["11-3"], centros_sel, magnitud=True)
        fin_cap_trab[m] = _importe_rubros_mes(df, m, ["11-4"], centros_sel, magnitud=True)
        total_egr_fin[m] = imp_fin[m] + int_impositivos[m] + com_gastos_banc[m] + fin_cap_trab[m]

        resultado_fin_operativo[m] = total_ing_fin[m] - total_egr_fin[m]
        resultado_antes_imp[m] = utilidad_operativa[m] + resultado_fin_operativo[m]

        # En la base de mayores puede no existir una línea calculada de impuesto a las ganancias.
        # Si existe rubro/cuenta explícito por texto, se toma; si no, queda 0 y no se inventa.
        imp_ganancias[m] = -abs(_importe_texto_mes(
            df, m, centros_sel,
            palabras_todas=["GANANCIAS"],
            palabras_alguna=["IMPUESTO", "IMP"]
        ))
        resultado_despues_imp[m] = resultado_antes_imp[m] + imp_ganancias[m]

        # Informativos: presentes en el modelo compartido, fuera del resultado mostrado.
        egresos_direccion[m] = _importe_rubros_mes(df, m, ["9-10"], centros_sel, magnitud=True)
        ingresos_extra[m] = _importe_rubros_mes(df, m, ["12-1"], centros_sel, magnitud=True)
        egresos_extra[m] = _importe_rubros_mes(df, m, ["12-2"], centros_sel, magnitud=True)

    # Construcción de la presentación en el mismo orden lógico del modelo validado
    add("Ventas", "Margen Bruto Gestión Comercial", "4-1", "más", ventas)
    add("Descuentos sobre ventas", "Margen Bruto Gestión Comercial", "4-2", "menos", descuentos)
    add("Costo de Ventas", "Margen Bruto Gestión Comercial", "5-1", "menos", costo_ventas)
    add("Rdo. Neto Gestoría", "Margen Bruto Gestión Comercial", "6-1 + 6-2", "menos", gestoria)
    add("Margen Bruto Gestión Comercial", "Margen Bruto Gestión Comercial", "", "igual", mb_gestion, "subtotal")

    add("Ajuste Costo de Reposición", "Margen Bruto Secundario", "", "menos", ajuste_repos)
    add("Costo Reacondic. y Acces.", "Margen Bruto Secundario", "5-2", "menos", reacond)
    add("Margen Bruto Primario", "Margen Bruto Secundario", "", "igual", mb_primario, "subtotal")
    add("Incentivos", "Margen Bruto Secundario", "4-3", "más", incentivos)
    add("Incentivo Devengado", "Margen Bruto Secundario", "4-4", "más", incentivo_dev)
    add("Comisión Consignaciones", "Margen Bruto Secundario", "6-3", "más", consignaciones)
    add("Comisión Pagadas", "Margen Bruto Secundario", "6-6", "menos", comisiones_pagadas)
    add("Comisión P/Vta Directa", "Margen Bruto Secundario", "10-1", "más", com_vta_directa)
    add("Margen Bruto Secundario", "Margen Bruto Secundario", "", "igual", mb_secundario, "subtotal")

    add("Otros Ingresos / Egresos", "Otros Ingresos / Egresos", "", "subtotal", otros_ie, "subtotal")
    add("Mermas de Inventarios", "Otros Ingresos / Egresos", "5-3", "menos", mermas)
    add("Sobrantes de Inventarios", "Otros Ingresos / Egresos", "5-4", "menos", sobrantes)
    add("Pérdida IVA Usados", "Otros Ingresos / Egresos", "5-5", "menos", perdida_iva)
    add("Horas no aplicadas mecánicos", "Otros Ingresos / Egresos", "6-4", "menos", horas_no_aplicadas)
    add("Resultado Venta de PPAA MS", "Otros Ingresos / Egresos", "6-5", "más", resultado_ppaa)
    add("Ingresos Seguros y Comis Gestión Vta", "Otros Ingresos / Egresos", "10-4", "más", ingresos_seguros)
    add("Egresos Seguros", "Otros Ingresos / Egresos", "11-5", "menos", egresos_seguros)
    add("Utilidad Bruta", "Utilidad Bruta", "", "igual", utilidad_bruta, "subtotal")

    add("Transferencia repuestos a taller", "Transferencia interna", "", "+/-", transferencia)
    add("Ctos Controlables y no Controlables", "Costos Operativos", "", "subtotal", total_control_no_control, "subtotal")

    add("Costos Controlables", "Costos Controlables", "", "grupo", {m: 0 for m in meses}, "encabezado")
    for nombre, rubros in controlables_rubros:
        add(nombre, "Costos Controlables", " + ".join(rubros), "menos", controlables_detalle[nombre])
    add("Total costos controlables", "Costos Controlables", "", "total", total_controlables, "subtotal")

    add("Costos No Controlables", "Costos No Controlables", "", "grupo", {m: 0 for m in meses}, "encabezado")
    for nombre, rubros in no_controlables_rubros:
        add(nombre, "Costos No Controlables", " + ".join(rubros), "menos", no_controlables_detalle[nombre])
    add("Total costos no controlables", "Costos No Controlables", "", "total", total_no_controlables, "subtotal")

    add("Utilidad Operativa Sucursal", "Utilidad Operativa Sucursal", "", "igual", utilidad_operativa_sucursal, "subtotal")

    add("Costos Estruct. Adm. Central", "Estructura", "", "subtotal", total_estructura, "subtotal")
    for nombre, rubros in estructura_controlable_rubros:
        add(nombre, "Controlables de Estructura", " + ".join(rubros), "menos", est_ctrl_detalle[nombre])
    add("Total costos Controlables de Estructura", "Controlables de Estructura", "", "total", total_est_ctrl, "subtotal")
    for nombre, rubros in estructura_no_controlable_rubros:
        add(nombre, "Costos no Controlables de Estructura", " + ".join(rubros), "menos", est_noctrl_detalle[nombre])
    add("Total costos no Controlables de Estructura", "Costos no Controlables de Estructura", "", "total", total_est_noctrl, "subtotal")

    add("Utilidad Operativa", "Utilidad Operativa", "", "igual", utilidad_operativa, "subtotal")

    add("Ingresos Financieros", "Ingresos Financieros", "", "subtotal", total_ing_fin, "subtotal")
    add("Intereses Financiación Vehículos", "Ingresos Financieros", "10-2", "más", int_fin_veh)
    add("Otros Ingresos Financieros", "Ingresos Financieros", "10-3", "más", otros_ing_fin)

    add("Egresos Financieros", "Egresos Financieros", "", "subtotal", total_egr_fin, "subtotal")
    add("Impuestos Financiación", "Egresos Financieros", "11-1", "menos", imp_fin)
    add("Intereses Impositivos", "Egresos Financieros", "11-2", "menos", int_impositivos)
    add("Comisiones y gastos bancarios", "Egresos Financieros", "11-3", "menos", com_gastos_banc)
    add("Financiación cap trab", "Egresos Financieros", "11-4", "menos", fin_cap_trab)

    add("Resultado Financiero Operativo", "Resultado Financiero Operativo", "", "igual", resultado_fin_operativo, "subtotal")
    add("Resultado antes de Impuestos", "Resultado antes de Impuestos", "", "igual", resultado_antes_imp, "subtotal")
    add("Impuesto a las Ganancias", "Impuesto a las Ganancias", "", "menos", imp_ganancias)
    add("Resultado después de Impuestos", "Resultado después de Impuestos", "", "igual", resultado_despues_imp, "subtotal")

    add("Egresos Dirección (fuera del resultado validado)", "Fuera del Resultado Modelado", "9-10", "informativo", egresos_direccion)
    add("Ingresos Extraordinarios (fuera del resultado validado)", "Fuera del Resultado Modelado", "12-1", "informativo", ingresos_extra)
    add("Egresos Extraordinarios (fuera del resultado validado)", "Fuera del Resultado Modelado", "12-2", "informativo", egresos_extra)

    return pd.DataFrame(filas)


def construir_pnl_porcentajes(pnl_df, meses):
    """Calcula cada línea como % de Ventas del mismo mes, igual que el modelo de validación."""
    out = pnl_df[["Grupo", "Concepto", "Rubros", "Lógica", "Tipo"]].copy()
    for m in meses:
        ventas_rows = pnl_df[pnl_df["Concepto"] == "Ventas"]
        ventas = float(ventas_rows[m].iloc[0]) if not ventas_rows.empty else 0.0
        out[m] = np.where(
            ventas != 0,
            pnl_df[m].astype(float) / abs(ventas),
            np.nan
        )
    return out

def styled_heatmap_percent(df_num):
    row_totals = df_num.abs().sum(axis=1).replace(0, np.nan)
    pct = df_num.abs().div(row_totals, axis=0)
    df_display = df_num.copy().astype(str)
    for idx in df_num.index:
        for col in df_num.columns:
            val, p = df_num.loc[idx, col], pct.loc[idx, col]
            df_display.loc[idx, col] = f"{fmt_money(val)} ({0 if pd.isna(p) else p:.1%})"
    def color_cell(v):
        try: p = float(str(v).split("(")[1].replace("%)", "").replace(",", ".")) / 100
        except Exception: p = 0
        if p >= 0.50: return "background-color: #ffb3b3; color: #111;"
        if p >= 0.30: return "background-color: #ffd6a5; color: #111;"
        if p >= 0.15: return "background-color: #fff3b0; color: #111;"
        if p > 0: return "background-color: #d8f3dc; color: #111;"
        return "background-color: #f5f5f5; color: #777;"
    styler = df_display.style
    return styler.map(color_cell) if hasattr(styler, "map") else styler.applymap(color_cell)

st.markdown("""
<style>
h1 {font-weight: 800; color: #1f2a44;}
h2, h3 {color: #1f2a44;}
[data-testid="stMetricValue"] {font-size: 26px;}
.block-container {padding-top: 1.4rem;}
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard Mayores Contables LUX")
st.caption("Control de costos, alertas, proveedores, benchmark, cuentas contables, insights y drilldown.")

try: df = cargar_datos()
except Exception as e:
    st.error("No se pudo cargar la base desde Google Sheets."); st.exception(e); st.stop()
if df.empty: st.warning("La base está vacía."); st.stop()

with st.sidebar:
    st.header("Filtros generales")
    sucursales = sorted(df["Sucursal"].dropna().astype(str).unique())
    suc_sel = st.multiselect("Sucursal", sucursales, default=sucursales)

df_filtrado = df[df["Sucursal"].isin(suc_sel)].copy() if suc_sel else df.copy()
meses_all = sorted(df_filtrado["Mes"].dropna().unique())
centros_base = centros_disponibles(df_filtrado)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs(["🎯 Control de Costos", "🚨 Alertas & Insights", "💼 Reducción de Gastos", "💰 Oportunidades de Ahorro", "🏭 Proveedores", "🏢 Benchmark Sucursales", "📑 P&L", "📒 Cuentas contables", "🧾 Control signos", "🔎 Drilldown", "⚙️ Diccionario"])

with tab1:
    st.subheader("🎯 Control de costos controlables y no controlables")
    c1, c2, c3 = st.columns(3)
    with c1: centros_sel = st.multiselect("Centro de costo / sector", centros_base, default=default_centros(centros_base, "repuestos"), key="centros_control")
    with c2: grupos_sel = st.multiselect("Categoría de costos", ["Costos Controlables", "Costos No Controlables"], default=["Costos Controlables", "Costos No Controlables"])
    with c3: modo = st.selectbox("Período", ["Últimos 2 meses", "Últimos 4 meses", "Selección manual"], index=1)
    meses_sel = meses_all[-2:] if modo == "Últimos 2 meses" else meses_all[-4:] if modo == "Últimos 4 meses" else st.multiselect("Meses", meses_all, default=meses_all[-4:])
    base = preparar_costos(df_filtrado, centros_sel, grupos_sel, meses_sel)
    if base.empty: st.info("No hay datos para los filtros seleccionados.")
    else:
        meses = sorted(base["Mes"].unique()); mes_act = meses[-1]; mes_ant = meses[-2] if len(meses) >= 2 else None
        total_act = base.loc[base["Mes"] == mes_act, "Importe_CC"].sum(); total_ant = base.loc[base["Mes"] == mes_ant, "Importe_CC"].sum() if mes_ant else np.nan
        var = total_act - total_ant if mes_ant else np.nan; var_pct = var / abs(total_ant) if mes_ant and total_ant != 0 else np.nan
        k1,k2,k3,k4 = st.columns(4); k1.metric("Sector", label_centros(centros_sel)); k2.metric(f"Costo {mes_act}", fmt_money(total_act)); k3.metric("Variación", fmt_money(var), fmt_pct(var_pct)); k4.metric("Semáforo", semaforo_variacion(var))
        evo = base.groupby(["Mes", "Grupo_PNL"], as_index=False)["Importe_CC"].sum(); evo["Etiqueta"] = evo["Importe_CC"].apply(fmt_money_short)
        fig = px.line(evo, x="Mes", y="Importe_CC", color="Grupo_PNL", markers=True, text="Etiqueta", title=f"Evolución mensual de costos - {label_centros(centros_sel)}")
        fig.update_traces(textposition="top center"); fig.update_yaxes(rangemode="tozero"); st.plotly_chart(fig, use_container_width=True)
        st.markdown("### Apertura por concepto")
        piv = tabla_variaciones(base, ["Grupo_PNL", "Concepto_PNL"]); mostrar = piv.copy()
        for col in ["Mes anterior", "Mes actual", "Variación $"]: mostrar[col] = mostrar[col].apply(fmt_money)
        mostrar["Variación %"] = mostrar["Variación %"].apply(fmt_pct)
        st.dataframe(mostrar[["Grupo_PNL","Concepto_PNL","Mes anterior","Mes actual","Variación $","Variación %","Semáforo","Severidad","Motivo severidad","Tipo evento"]], use_container_width=True, height=430)
        st.markdown("### Principales variaciones")
        top = piv.dropna(subset=["Variación $"]).head(12).copy(); top["Etiqueta"] = top["Variación $"].apply(fmt_money_short)
        if not top.empty:
            fig2 = px.bar(top, x="Variación $", y="Concepto_PNL", color="Semáforo", text="Etiqueta", orientation="h", title="Top variaciones vs mes anterior")
            preparar_para_labels(fig2); st.plotly_chart(fig2, use_container_width=True)
        st.markdown("### Insight ejecutivo")
        aumentos = piv[piv["Variación $"] > 0].sort_values("Variación $", ascending=False); bajas = piv[piv["Variación $"] < 0].sort_values("Variación $", ascending=True); texto=[]
        if not pd.isna(var): texto.append(("🔴 Los costos aumentaron" if var>0 else "🟢 Los costos bajaron" if var<0 else "🟡 No hubo variación relevante") + f" **{fmt_money(abs(var))}** vs el mes anterior (**{fmt_pct(var_pct)}**).")
        if not aumentos.empty:
            a=aumentos.iloc[0]; texto.append(f"Principal presión: **{a['Concepto_PNL']}**, suba de **{fmt_money(a['Variación $'])}**. Motivo: {a['Motivo severidad']}.")
        if not bajas.empty:
            b=bajas.iloc[0]; texto.append(f"Principal mejora: **{b['Concepto_PNL']}**, baja de **{fmt_money(abs(b['Variación $']))}**. Validar si es ahorro real o diferimiento.")
        st.info(" ".join(texto))
        st.markdown("### Movimientos que explican el desvío")
        opciones = top["Concepto_PNL"].tolist() if not top.empty else sorted(base["Concepto_PNL"].unique())
        concepto = st.selectbox("Concepto para revisar", opciones)
        movs = base[base["Concepto_PNL"] == concepto].copy(); movs["Impacto_abs"] = movs["Importe_CC"].abs(); movs = movs.sort_values(["Mes", "Impacto_abs"], ascending=[False, False]); movs["Importe"] = movs["Importe_CC"].apply(fmt_money)
        cols = ["Mes","Fecha","Sucursal","Proveedor_detectado","Factura_detectada","Nombre cuenta","Nombre del rubro","Detalle","des res","Detalle 2","Importe"]
        st.dataframe(movs[[c for c in cols if c in movs.columns]].head(100), use_container_width=True, height=520)

with tab2:
    st.subheader("🚨 Alertas automáticas & motor de insights")
    centros_a = st.multiselect("Centro de costo", centros_base, default=default_centros(centros_base, "posventa"), key="centros_alertas")
    grupos_alerta = st.multiselect("Categorías", ["Costos Controlables", "Costos No Controlables"], default=["Costos Controlables", "Costos No Controlables"], key="grupos_alertas")
    base_a = preparar_costos(df_filtrado, centros_a, grupos_alerta, meses_all[-4:])
    if base_a.empty: st.info("No hay datos suficientes para alertas.")
    else:
        piv = tabla_variaciones(base_a, ["Grupo_PNL", "Concepto_PNL"]); alertas = piv[piv["Severidad"].isin(["🔴 Crítico", "🟠 Alto"])].copy()
        k1,k2,k3 = st.columns(3); k1.metric("Alertas críticas/altas", len(alertas)); k2.metric("Mayor aumento", fmt_money(piv["Variación $"].max() if not piv.empty else 0)); k3.metric("Mayor mejora", fmt_money(piv["Variación $"].min() if not piv.empty else 0))
        st.markdown("### Alertas priorizadas")
        if alertas.empty: st.success("No se detectan alertas críticas o altas.")
        else:
            m=alertas.copy();
            for col in ["Mes anterior", "Mes actual", "Variación $"]: m[col] = m[col].apply(fmt_money)
            m["Variación %"] = m["Variación %"].apply(fmt_pct)
            st.dataframe(m[["Severidad","Motivo severidad","Tipo evento","Grupo_PNL","Concepto_PNL","Mes anterior","Mes actual","Variación $","Variación %","Semáforo"]], use_container_width=True, height=360)
        st.markdown("### Insights automáticos enriquecidos")
        insights=[]
        for _, r in piv[piv["Variación $"] > 0].sort_values("Variación $", ascending=False).head(3).iterrows():
            prov_concepto = base_a[base_a["Concepto_PNL"] == r["Concepto_PNL"]].copy(); top_prov = prov_concepto.groupby("Proveedor_detectado", as_index=False)["Importe_CC"].sum().sort_values("Importe_CC", ascending=False).head(1)
            proveedor_txt = f" El proveedor con mayor participación es **{top_prov.iloc[0]['Proveedor_detectado']}** con **{fmt_money(top_prov.iloc[0]['Importe_CC'])}**." if not top_prov.empty else ""
            insights.append(f"🔴 **{r['Concepto_PNL']}** aumenta **{fmt_money(r['Variación $'])}** y queda como **{r['Severidad']}**. **Hipótesis:** gasto extraordinario, ajuste de contrato o concentración puntual.{proveedor_txt} **Acción:** revisar movimientos, proveedor y recurrencia.")
        for _, r in piv[piv["Variación $"] < 0].sort_values("Variación $", ascending=True).head(3).iterrows(): insights.append(f"🟢 **{r['Concepto_PNL']}** mejora **{fmt_money(abs(r['Variación $']))}**. Validar si es ahorro real o diferimiento de facturación.")
        for i in insights: st.info(i)
        if not insights: st.success("No se detectan insights relevantes con los filtros actuales.")

with tab3:
    st.subheader("💼 Comité de Reducción de Gastos")
    st.caption("Vista ejecutiva para identificar rubros, sucursales y proveedores con mayor oportunidad de eficiencia.")

    r1, r2, r3 = st.columns(3)
    with r1:
        centros_red = st.multiselect(
            "Centro de costo",
            centros_base,
            default=default_centros(centros_base, "posventa"),
            key="centros_reduccion"
        )
    with r2:
        grupos_red = st.multiselect(
            "Tipo de costo",
            ["Costos Controlables", "Costos No Controlables"],
            default=["Costos Controlables", "Costos No Controlables"],
            key="grupos_reduccion"
        )
    with r3:
        meses_red = st.multiselect(
            "Meses a analizar",
            meses_all,
            default=meses_all[-4:],
            key="meses_reduccion"
        )

    base_red = preparar_costos(df_filtrado, centros_red, grupos_red, meses_red)

    if base_red.empty:
        st.info("No hay datos para los filtros seleccionados.")
    else:
        meses_red_ord = sorted(base_red["Mes"].dropna().unique())
        mes_act = meses_red_ord[-1]
        mes_ant = meses_red_ord[-2] if len(meses_red_ord) >= 2 else None

        total_gasto = base_red["Importe_CC"].sum()
        total_actual = base_red.loc[base_red["Mes"] == mes_act, "Importe_CC"].sum()
        total_anterior = base_red.loc[base_red["Mes"] == mes_ant, "Importe_CC"].sum() if mes_ant else np.nan
        var_total = total_actual - total_anterior if mes_ant else np.nan
        var_pct = var_total / abs(total_anterior) if mes_ant and total_anterior != 0 else np.nan

        # Rubros y proveedores principales
        por_concepto_total = base_red.groupby(["Grupo_PNL", "Concepto_PNL"], as_index=False)["Importe_CC"].sum().sort_values("Importe_CC", ascending=False)
        por_proveedor_total = base_red.groupby(["Proveedor_detectado", "Categoria_proveedor"], as_index=False)["Importe_CC"].sum().sort_values("Importe_CC", ascending=False)
        por_sucursal_total = base_red.groupby("Sucursal", as_index=False)["Importe_CC"].sum().sort_values("Importe_CC", ascending=False)

        top_rubro = por_concepto_total.iloc[0]["Concepto_PNL"] if not por_concepto_total.empty else "Sin datos"
        top_proveedor = por_proveedor_total.iloc[0]["Proveedor_detectado"] if not por_proveedor_total.empty else "Sin datos"
        top_sucursal = por_sucursal_total.iloc[0]["Sucursal"] if not por_sucursal_total.empty else "Sin datos"

        # Estimación simple de oportunidad: rubros controlables/negociables con mayor presión
        reducibles_inmediatos = [
            "Publicidad y Promoción", "Movilidad y Viáticos", "Útiles y materiales de oficina",
            "Teléfonos e internet", "Serv. Limpieza", "Herramientas, materiales y fletes",
            "Otros Gastos Fijos", "Gastos de Atención clientes", "Mantenimiento rodados y equipos",
            "Mantenimiento Bienes de Uso", "Seguridad y vigilancia"
        ]
        negociables = ["Alquileres", "Honorarios profesionales", "Seguros", "Fuerza motriz, luz, agua y gas"]

        matriz_base = tabla_variaciones(base_red, ["Grupo_PNL", "Concepto_PNL"])
        matriz_base["Controlabilidad"] = np.select(
            [
                matriz_base["Concepto_PNL"].isin(reducibles_inmediatos),
                matriz_base["Concepto_PNL"].isin(negociables),
                matriz_base["Grupo_PNL"].eq("Costos No Controlables")
            ],
            ["Alta", "Media / negociable", "Baja"],
            default="Media"
        )
        matriz_base["Acción sugerida"] = np.select(
            [
                matriz_base["Controlabilidad"].eq("Alta"),
                matriz_base["Controlabilidad"].eq("Media / negociable"),
                matriz_base["Controlabilidad"].eq("Baja")
            ],
            [
                "Revisar consumo, necesidad y autorización del gasto",
                "Renegociar contrato / validar condiciones",
                "Monitorear, validar imputación y buscar optimización indirecta"
            ],
            default="Analizar caso puntual"
        )
        matriz_base["Ahorro potencial 10%"] = np.where(
            matriz_base["Controlabilidad"].isin(["Alta", "Media", "Media / negociable"]),
            matriz_base["Mes actual"].abs() * 0.10,
            0
        )
        ahorro_potencial = matriz_base["Ahorro potencial 10%"].sum()

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Gasto analizado", fmt_money(total_gasto))
        k2.metric(f"Gasto {mes_act}", fmt_money(total_actual))
        k3.metric("Variación vs mes anterior", fmt_money(var_total), fmt_pct(var_pct))
        k4.metric("Ahorro potencial 10%", fmt_money(ahorro_potencial))
        k5.metric("Sucursal foco", top_sucursal)

        st.markdown("### 1. Mapa ejecutivo de oportunidad")
        matriz = matriz_base.copy()
        matriz["Prioridad"] = np.select(
            [
                matriz["Severidad"].isin(["🔴 Crítico", "🟠 Alto"]) & matriz["Controlabilidad"].isin(["Alta", "Media", "Media / negociable"]),
                matriz["Severidad"].isin(["🟡 Medio"]) & matriz["Controlabilidad"].isin(["Alta", "Media", "Media / negociable"]),
                matriz["Controlabilidad"].eq("Baja")
            ],
            ["🔴 Prioridad alta", "🟡 Prioridad media", "⚪ Baja controlabilidad"],
            default="🟢 Monitorear"
        )

        matriz_mostrar = matriz.copy()
        for col in ["Mes anterior", "Mes actual", "Variación $", "Ahorro potencial 10%"]:
            matriz_mostrar[col] = matriz_mostrar[col].apply(fmt_money)
        matriz_mostrar["Variación %"] = matriz_mostrar["Variación %"].apply(fmt_pct)

        st.dataframe(
            matriz_mostrar[[
                "Prioridad", "Grupo_PNL", "Concepto_PNL", "Controlabilidad",
                "Mes anterior", "Mes actual", "Variación $", "Variación %",
                "Ahorro potencial 10%", "Severidad", "Motivo severidad", "Acción sugerida"
            ]],
            use_container_width=True,
            height=430
        )

        st.markdown("### 2. Rubros con mayor consumo y presión")
        top_rubros = matriz.sort_values("Mes actual", ascending=False).head(12).copy()
        top_rubros["Etiqueta"] = top_rubros["Mes actual"].apply(fmt_money_short)
        fig_r = px.bar(
            top_rubros,
            x="Mes actual",
            y="Concepto_PNL",
            color="Grupo_PNL",
            text="Etiqueta",
            orientation="h",
            title="Rubros con mayor gasto actual"
        )
        preparar_para_labels(fig_r)
        st.plotly_chart(fig_r, use_container_width=True)

        st.markdown("### 3. Proveedores con mayor representación")
        top_prov = por_proveedor_total.head(15).copy()
        top_prov["Participación"] = np.where(total_gasto != 0, top_prov["Importe_CC"] / abs(total_gasto), 0)
        top_prov["Importe"] = top_prov["Importe_CC"].apply(fmt_money)
        top_prov["Participación %"] = top_prov["Participación"].apply(fmt_pct)
        top_prov["Etiqueta"] = top_prov["Importe_CC"].apply(fmt_money_short)
        orden_proveedores_red = ordenar_categorias_por_total(top_prov, "Proveedor_detectado", "Importe_CC")
        fig_p = px.bar(
            top_prov,
            x="Importe_CC",
            y="Proveedor_detectado",
            color="Categoria_proveedor",
            text="Etiqueta",
            orientation="h",
            title="Top proveedores por gasto total analizado",
            category_orders={"Proveedor_detectado": orden_proveedores_red[::-1]}
        )
        preparar_para_labels(fig_p)
        st.plotly_chart(fig_p, use_container_width=True)
        st.dataframe(top_prov[["Proveedor_detectado", "Categoria_proveedor", "Importe", "Participación %"]], use_container_width=True, height=360)

        st.markdown("### 4. Apertura por sucursal")
        suc_concepto = base_red.groupby(["Sucursal", "Concepto_PNL"], as_index=False)["Importe_CC"].sum()
        heat_suc = suc_concepto.pivot_table(index="Concepto_PNL", columns="Sucursal", values="Importe_CC", aggfunc="sum", fill_value=0)
        st.dataframe(styled_heatmap_percent(heat_suc), use_container_width=True, height=420)

        st.markdown("### 5. Plan de acción sugerido para comité")
        acciones = matriz[matriz["Prioridad"].isin(["🔴 Prioridad alta", "🟡 Prioridad media"])].copy()
        acciones = acciones.sort_values(["Prioridad", "Ahorro potencial 10%"], ascending=[True, False]).head(15)
        acciones_m = acciones.copy()
        for col in ["Mes actual", "Variación $", "Ahorro potencial 10%"]:
            acciones_m[col] = acciones_m[col].apply(fmt_money)
        acciones_m["Variación %"] = acciones_m["Variación %"].apply(fmt_pct)
        st.dataframe(
            acciones_m[[
                "Prioridad", "Concepto_PNL", "Grupo_PNL", "Controlabilidad", "Mes actual",
                "Variación $", "Variación %", "Ahorro potencial 10%", "Acción sugerida"
            ]],
            use_container_width=True,
            height=360
        )

        st.markdown("### 6. Insight para presentar a dirección")
        insight = []
        if not pd.isna(var_total):
            if var_total > 0:
                insight.append(f"🔴 En **{label_centros(centros_red)}**, el gasto aumentó **{fmt_money(var_total)}** versus el mes anterior (**{fmt_pct(var_pct)}**).")
            elif var_total < 0:
                insight.append(f"🟢 En **{label_centros(centros_red)}**, el gasto bajó **{fmt_money(abs(var_total))}** versus el mes anterior (**{fmt_pct(var_pct)}**).")
        insight.append(f"El rubro de mayor consumo es **{top_rubro}** y el proveedor con mayor representación es **{top_proveedor}**.")
        if ahorro_potencial > 0:
            insight.append(f"Si se trabajara una reducción selectiva del 10% sobre rubros controlables/negociables, el ahorro potencial estimado sería de **{fmt_money(ahorro_potencial)}** para el período analizado.")
        insight.append("La recomendación no es aplicar un recorte lineal, sino priorizar rubros con alta controlabilidad, alta severidad y concentración por proveedor/sucursal.")
        st.info(" ".join(insight))

        st.markdown("### 7. Drilldown de rubro/proveedor")
        coldr1, coldr2 = st.columns(2)
        with coldr1:
            rubro_sel = st.selectbox("Rubro para revisar", sorted(base_red["Concepto_PNL"].dropna().unique()), key="rubro_reduccion")
        with coldr2:
            provs_rubro = sorted(base_red.loc[base_red["Concepto_PNL"] == rubro_sel, "Proveedor_detectado"].dropna().unique())
            prov_sel = st.selectbox("Proveedor", ["Todos"] + provs_rubro, key="prov_reduccion")
        mov_red = base_red[base_red["Concepto_PNL"] == rubro_sel].copy()
        if prov_sel != "Todos":
            mov_red = mov_red[mov_red["Proveedor_detectado"] == prov_sel]
        mov_red["Importe"] = mov_red["Importe_CC"].apply(fmt_money)
        mov_red["Impacto_abs"] = mov_red["Importe_CC"].abs()
        mov_red = mov_red.sort_values("Impacto_abs", ascending=False)
        cols_red = [
            "Mes", "Fecha", "Sucursal", "Cuenta:", "Nombre cuenta", "Nombre del rubro",
            "Concepto_PNL", "Proveedor_detectado", "Factura_detectada",
            "Detalle", "des res", "Detalle 2", "Importe"
        ]
        st.dataframe(mov_red[[c for c in cols_red if c in mov_red.columns]].head(200), use_container_width=True, height=520)



with tab4:
    st.subheader("💰 Oportunidades de Ahorro")
    st.caption("Vista ejecutiva para separar gasto alto de gasto accionable y priorizar acciones concretas de reducción.")

    col1, col2, col3 = st.columns(3)
    with col1:
        centros_opp = st.multiselect(
            "Centro de costo",
            centros_base,
            default=default_centros(centros_base, "posventa"),
            key="centros_oportunidades"
        )
    with col2:
        grupos_opp = st.multiselect(
            "Tipo de costo",
            ["Costos Controlables", "Costos No Controlables"],
            default=["Costos Controlables", "Costos No Controlables"],
            key="grupos_oportunidades"
        )
    with col3:
        meses_opp = st.multiselect(
            "Meses a analizar",
            meses_all,
            default=meses_all[-4:],
            key="meses_oportunidades"
        )

    base_opp = preparar_costos(df_filtrado, centros_opp, grupos_opp, meses_opp)

    if base_opp.empty:
        st.info("No hay datos para los filtros seleccionados.")
    else:
        st.markdown("### 1. Reglas de accionabilidad")
        st.caption("El objetivo no es mirar solo el gasto más alto, sino separar lo no negociable de lo realmente trabajable.")

        proveedores_baja = ["ROQUE JUAN LOZANO", "TOYOTA ENTINA", "TOYOTA ARGENTINA", "OVERSOFT"]
        categorias_baja = ["Toyota / terminal", "Sistemas / software", "Alquileres"]
        conceptos_baja = ["Alquileres", "Recupero de Gastos Toyota", "Amortizaciones"]
        conceptos_media = [
            "Fuerza motriz, luz, agua y gas", "Seguridad y vigilancia", "Honorarios profesionales",
            "Seguros", "Impuestos", "Impuestos y tasas", "Teléfonos e internet"
        ]
        conceptos_alta = [
            "Publicidad y Promoción", "Movilidad y Viáticos", "Útiles y materiales de oficina",
            "Serv. Limpieza", "Herramientas, materiales y fletes", "Otros Gastos Fijos",
            "Gastos de Atención clientes", "Mantenimiento rodados y equipos",
            "Mantenimiento Bienes de Uso", "Preparación y entrega", "Servicios gratuitos y Cargos internos"
        ]

        base_opp["Proveedor_detectado"] = base_opp["Proveedor_detectado"].fillna("SIN IDENTIFICAR")
        base_opp["Categoria_proveedor"] = base_opp["Categoria_proveedor"].fillna("Otros / no clasificado")

        def clasificar_accionabilidad(row):
            proveedor = str(row.get("Proveedor_detectado", "")).upper()
            concepto = str(row.get("Concepto_PNL", ""))
            categoria = str(row.get("Categoria_proveedor", ""))
            if any(p in proveedor for p in proveedores_baja) or categoria in categorias_baja or concepto in conceptos_baja:
                return "Baja"
            if concepto in conceptos_alta:
                return "Alta"
            if concepto in conceptos_media:
                return "Media"
            if row.get("Grupo_PNL") == "Costos Controlables":
                return "Media"
            return "Baja"

        def accion_sugerida(row):
            acc = row.get("Accionabilidad", "")
            concepto = str(row.get("Concepto_PNL", ""))
            categoria = str(row.get("Categoria_proveedor", ""))
            if acc == "Alta":
                if "Publicidad" in concepto:
                    return "Revisar pauta, objetivo, ROAS y necesidad del gasto."
                if "Viáticos" in concepto or "Movilidad" in concepto:
                    return "Definir política de autorización, topes y rendición por motivo."
                if "Limpieza" in concepto or categoria == "Limpieza / seguridad":
                    return "Cotizar alternativa, renegociar frecuencia y alcance del servicio."
                if "Herramientas" in concepto or "Útiles" in concepto:
                    return "Centralizar compras, consolidar pedidos y comparar proveedores."
                return "Revisar necesidad, autorización, frecuencia y proveedor alternativo."
            if acc == "Media":
                if "energ" in concepto.lower() or "luz" in concepto.lower():
                    return "Continuar plan LED/interruptores y medir consumo por sede."
                if "Seguridad" in concepto:
                    return "Revisar dotación, horarios cubiertos y condiciones contractuales."
                if "Honorarios" in concepto:
                    return "Validar alcance, duplicidades y posibilidad de fee fijo."
                return "Renegociar condiciones, validar contrato y controlar recurrencia."
            return "Baja acción directa: monitorear, validar imputación y evitar crecimiento no justificado."

        base_opp["Accionabilidad"] = base_opp.apply(clasificar_accionabilidad, axis=1)
        base_opp["% ahorro estimado"] = np.select(
            [base_opp["Accionabilidad"].eq("Alta"), base_opp["Accionabilidad"].eq("Media")],
            [0.10, 0.05],
            default=0.00
        )
        base_opp["Ahorro potencial"] = base_opp["Importe_CC"].abs() * base_opp["% ahorro estimado"]

        excluir_baja = st.checkbox(
            "Excluir del análisis principal proveedores/rubros de baja accionabilidad: Roque Lozano, Toyota, Oversoft, alquileres y licencias",
            value=True,
            key="excluir_baja_oportunidades"
        )
        base_acc = base_opp[base_opp["Accionabilidad"].ne("Baja")].copy() if excluir_baja else base_opp.copy()

        total_gasto = base_opp["Importe_CC"].sum()
        gasto_accionable = base_acc["Importe_CC"].sum()
        ahorro_potencial = base_acc["Ahorro potencial"].sum()
        pct_accionable = gasto_accionable / total_gasto if total_gasto else np.nan

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Gasto total analizado", fmt_money(total_gasto))
        k2.metric("Gasto accionable", fmt_money(gasto_accionable), fmt_pct(pct_accionable))
        k3.metric("Ahorro potencial estimado", fmt_money(ahorro_potencial))
        k4.metric("Proveedores accionables", base_acc["Proveedor_detectado"].nunique())
        k5.metric("Rubros accionables", base_acc["Concepto_PNL"].nunique())

        st.info(
            "Lectura ejecutiva: este tab separa gastos estructurales o poco negociables de los gastos con margen real de gestión. "
            "La estimación es conservadora: 10% sobre gastos de alta accionabilidad y 5% sobre gastos de accionabilidad media."
        )

        if base_acc.empty:
            st.warning("Con la exclusión activa no quedan gastos accionables para analizar. Desactivá el check para ver todo el gasto.")
        else:
            st.markdown("### 2. Ranking de oportunidades por rubro")
            rubros = base_acc.groupby(["Grupo_PNL", "Concepto_PNL", "Accionabilidad"], as_index=False).agg(
                Gasto=("Importe_CC", "sum"),
                Ahorro_potencial=("Ahorro potencial", "sum"),
                Movimientos=("Importe_CC", "count"),
                Proveedores=("Proveedor_detectado", "nunique")
            ).sort_values("Ahorro_potencial", ascending=False)
            rubros["Etiqueta"] = rubros["Ahorro_potencial"].apply(fmt_money_short)
            fig = px.bar(
                rubros.head(15),
                x="Ahorro_potencial",
                y="Concepto_PNL",
                color="Accionabilidad",
                text="Etiqueta",
                orientation="h",
                title="Top rubros por ahorro potencial estimado"
            )
            preparar_para_labels(fig)
            st.plotly_chart(fig, use_container_width=True)
            rubros_m = rubros.copy()
            rubros_m["Gasto"] = rubros_m["Gasto"].apply(fmt_money)
            rubros_m["Ahorro_potencial"] = rubros_m["Ahorro_potencial"].apply(fmt_money)
            st.dataframe(
                rubros_m[["Grupo_PNL", "Concepto_PNL", "Accionabilidad", "Gasto", "Ahorro_potencial", "Movimientos", "Proveedores"]],
                use_container_width=True,
                height=380
            )

            st.markdown("### 3. Proveedores trabajables: gasto, recurrencia y oportunidad")
            prov = base_acc.groupby(["Proveedor_detectado", "Categoria_proveedor", "Accionabilidad"], as_index=False).agg(
                Gasto=("Importe_CC", "sum"),
                Ahorro_potencial=("Ahorro potencial", "sum"),
                Movimientos=("Importe_CC", "count"),
                Meses_con_gasto=("Mes", "nunique"),
                Sucursales=("Sucursal", "nunique")
            )
            prov["Recurrencia"] = np.where(prov["Meses_con_gasto"] >= 3, "🔁 Recurrente", np.where(prov["Meses_con_gasto"] == 2, "🟡 Intermitente", "⚠️ Puntual"))
            prov = prov.sort_values("Ahorro_potencial", ascending=False)
            prov["Etiqueta"] = prov["Ahorro_potencial"].apply(fmt_money_short)
            fig2 = px.bar(
                prov.head(20),
                x="Ahorro_potencial",
                y="Proveedor_detectado",
                color="Recurrencia",
                text="Etiqueta",
                orientation="h",
                title="Top proveedores trabajables por ahorro potencial"
            )
            preparar_para_labels(fig2)
            st.plotly_chart(fig2, use_container_width=True)
            prov_m = prov.copy()
            prov_m["Gasto"] = prov_m["Gasto"].apply(fmt_money)
            prov_m["Ahorro_potencial"] = prov_m["Ahorro_potencial"].apply(fmt_money)
            st.dataframe(
                prov_m[["Proveedor_detectado", "Categoria_proveedor", "Accionabilidad", "Recurrencia", "Gasto", "Ahorro_potencial", "Movimientos", "Meses_con_gasto", "Sucursales"]].head(50),
                use_container_width=True,
                height=430
            )

            st.markdown("### 4. Pareto de proveedores accionables")
            pareto = prov[["Proveedor_detectado", "Gasto"]].copy().sort_values("Gasto", ascending=False)
            pareto["% gasto"] = pareto["Gasto"] / pareto["Gasto"].sum() if pareto["Gasto"].sum() else 0
            pareto["% acumulado"] = pareto["% gasto"].cumsum()
            pareto["Gasto"] = pareto["Gasto"].apply(fmt_money)
            pareto["% gasto"] = pareto["% gasto"].apply(fmt_pct)
            pareto["% acumulado"] = pareto["% acumulado"].apply(fmt_pct)
            st.dataframe(pareto.head(30), use_container_width=True, height=360)

            st.markdown("### 5. Oportunidad por sucursal")
            suc = base_acc.groupby("Sucursal", as_index=False).agg(
                Gasto=("Importe_CC", "sum"),
                Ahorro_potencial=("Ahorro potencial", "sum"),
                Proveedores=("Proveedor_detectado", "nunique"),
                Movimientos=("Importe_CC", "count")
            ).sort_values("Ahorro_potencial", ascending=False)
            suc["Etiqueta"] = suc["Ahorro_potencial"].apply(fmt_money_short)
            fig3 = px.bar(suc, x="Sucursal", y="Ahorro_potencial", text="Etiqueta", title="Ahorro potencial estimado por sucursal")
            preparar_para_labels(fig3)
            st.plotly_chart(fig3, use_container_width=True)
            suc_m = suc.copy()
            suc_m["Gasto"] = suc_m["Gasto"].apply(fmt_money)
            suc_m["Ahorro_potencial"] = suc_m["Ahorro_potencial"].apply(fmt_money)
            st.dataframe(suc_m[["Sucursal", "Gasto", "Ahorro_potencial", "Proveedores", "Movimientos"]], use_container_width=True)

            st.markdown("### 6. Plan de acción sugerido para dirección")
            acciones = base_acc.groupby(["Concepto_PNL", "Proveedor_detectado", "Sucursal", "Accionabilidad", "Categoria_proveedor"], as_index=False).agg(
                Gasto=("Importe_CC", "sum"),
                Ahorro_potencial=("Ahorro potencial", "sum"),
                Movimientos=("Importe_CC", "count"),
                Meses_con_gasto=("Mes", "nunique")
            )
            acciones["Acción sugerida"] = acciones.apply(accion_sugerida, axis=1)
            acciones["Prioridad"] = np.select(
                [acciones["Ahorro_potencial"] >= 1_000_000, acciones["Ahorro_potencial"] >= 300_000],
                ["🔴 Alta", "🟠 Media"],
                default="🟡 Monitorear"
            )
            acciones = acciones.sort_values(["Ahorro_potencial", "Gasto"], ascending=False)
            acciones_m = acciones.copy()
            acciones_m["Gasto"] = acciones_m["Gasto"].apply(fmt_money)
            acciones_m["Ahorro_potencial"] = acciones_m["Ahorro_potencial"].apply(fmt_money)
            st.dataframe(
                acciones_m[["Prioridad", "Concepto_PNL", "Proveedor_detectado", "Sucursal", "Accionabilidad", "Gasto", "Ahorro_potencial", "Movimientos", "Meses_con_gasto", "Acción sugerida"]].head(80),
                use_container_width=True,
                height=520
            )

            st.markdown("### 7. Insight para presentar")
            if not acciones.empty and not suc.empty and not rubros.empty:
                top_accion = acciones.iloc[0]
                top_suc = suc.iloc[0]
                top_rubro = rubros.iloc[0]
                st.info(
                    f"🧠 El mayor potencial de gestión no necesariamente está en el gasto más grande, sino en el gasto accionable. "
                    f"Con los filtros actuales se identifica un ahorro potencial estimado de **{fmt_money(ahorro_potencial)}**. "
                    f"El rubro con mayor oportunidad es **{top_rubro['Concepto_PNL']}** y la principal acción puntual aparece en **{top_accion['Proveedor_detectado']} / {top_accion['Sucursal']}**, "
                    f"con una oportunidad estimada de **{fmt_money(top_accion['Ahorro_potencial'])}**. "
                    f"La sucursal donde conviene empezar es **{top_suc['Sucursal']}**."
                )

            st.download_button(
                "⬇️ Descargar plan de oportunidades",
                data=acciones.to_csv(index=False).encode("utf-8-sig"),
                file_name="plan_oportunidades_ahorro.csv",
                mime="text/csv"
            )

with tab5:
    st.subheader("🏭 Análisis de proveedores")
    p1,p2,p3=st.columns(3)
    with p1: centros_p=st.multiselect("Centro de costo", centros_base, default=default_centros(centros_base,"repuestos"), key="centros_prov")
    with p2: grupos_p=st.multiselect("Categoría", ["Costos Controlables", "Costos No Controlables"], default=["Costos Controlables", "Costos No Controlables"], key="grupo_prov")
    with p3: meses_p=st.multiselect("Meses", meses_all, default=meses_all[-4:], key="meses_prov")
    base_p=preparar_costos(df_filtrado, centros_p, grupos_p, meses_p)
    if base_p.empty: st.info("No hay datos para proveedores.")
    else:
        prov_mes=base_p.groupby(["Mes","Proveedor_detectado","Categoria_proveedor"], as_index=False)["Importe_CC"].sum()
        ranking_total=prov_mes.groupby(["Proveedor_detectado","Categoria_proveedor"], as_index=False)["Importe_CC"].sum().sort_values("Importe_CC", ascending=False)
        stacked=prov_mes[prov_mes["Proveedor_detectado"].isin(ranking_total.head(15)["Proveedor_detectado"].tolist())].copy(); stacked["Etiqueta"]=stacked.apply(lambda r:f"{r['Mes']}: {fmt_money_short(r['Importe_CC'])}", axis=1)
        st.markdown("### Top proveedores por costo — apertura mensual")
        orden_proveedores = ordenar_categorias_por_total(stacked, "Proveedor_detectado", "Importe_CC")
        fig=px.bar(
            stacked,
            x="Proveedor_detectado",
            y="Importe_CC",
            color="Mes",
            text="Etiqueta",
            title=f"Top proveedores por gasto, dividido por mes - {label_centros(centros_p)}",
            category_orders={"Proveedor_detectado": orden_proveedores}
        )
        fig.update_layout(xaxis_tickangle=-45)
        fig.update_traces(textposition="inside",insidetextanchor="middle")
        st.plotly_chart(fig,use_container_width=True)
        st.markdown("### Tabla mensual por proveedor")
        tabla=prov_mes.pivot_table(index=["Proveedor_detectado","Categoria_proveedor"],columns="Mes",values="Importe_CC",aggfunc="sum",fill_value=0).reset_index(); meses_cols=sorted([c for c in tabla.columns if c not in ["Proveedor_detectado","Categoria_proveedor"]])
        tabla["Total"]=tabla[meses_cols].sum(axis=1); tabla["Promedio mensual"]=tabla[meses_cols].mean(axis=1); tabla["Mes pico"]=tabla[meses_cols].idxmax(axis=1); tabla["Importe mes pico"]=tabla[meses_cols].max(axis=1); tabla["% concentración pico"]=np.where(tabla["Total"].abs()>0,tabla["Importe mes pico"]/tabla["Total"].abs(),0); tabla=tabla.sort_values("Total",ascending=False)
        tm=tabla.copy();
        for m in meses_cols: tm[m]=tm[m].apply(fmt_money)
        for c in ["Total","Promedio mensual","Importe mes pico"]: tm[c]=tm[c].apply(fmt_money)
        tm["% concentración pico"]=tm["% concentración pico"].apply(fmt_pct)
        st.dataframe(tm[["Proveedor_detectado","Categoria_proveedor"]+meses_cols+["Total","Promedio mensual","Mes pico","Importe mes pico","% concentración pico"]].head(50), use_container_width=True, height=430)
        st.markdown("### Proveedores que más crecieron")
        pivp=tabla_variaciones(base_p,["Proveedor_detectado","Categoria_proveedor"]); crec=pivp.dropna(subset=["Variación $"]).sort_values("Variación $",ascending=False).head(30); cm=crec.copy()
        for col in ["Mes anterior","Mes actual","Variación $"]: cm[col]=cm[col].apply(fmt_money)
        cm["Variación %"]=cm["Variación %"].apply(fmt_pct)
        st.dataframe(cm[["Proveedor_detectado","Categoria_proveedor","Mes anterior","Mes actual","Variación $","Variación %","Severidad","Motivo severidad","Tipo evento"]], use_container_width=True, height=420)
        st.markdown("### Evolución acumulada Top 10 proveedores")
        evo=prov_mes[prov_mes["Proveedor_detectado"].isin(ranking_total.head(10)["Proveedor_detectado"].tolist())].copy().sort_values(["Proveedor_detectado","Mes"]); evo["Acumulado"]=evo.groupby("Proveedor_detectado")["Importe_CC"].cumsum(); evo["Etiqueta"]=evo["Acumulado"].apply(fmt_money_short)
        fig2=px.line(evo,x="Mes",y="Acumulado",color="Proveedor_detectado",markers=True,text="Etiqueta",title="Evolución acumulada por proveedor"); fig2.update_traces(textposition="top center"); fig2.update_yaxes(rangemode="tozero"); st.plotly_chart(fig2,use_container_width=True)
        st.markdown("### Movimientos por proveedor")
        if "busqueda_proveedor" not in st.session_state: st.session_state["busqueda_proveedor"]=""
        colb1,colb2=st.columns([4,1])
        with colb1: busqueda=st.text_input("Buscar proveedor", key="busqueda_proveedor")
        with colb2:
            if st.button("Limpiar búsqueda"): st.session_state["busqueda_proveedor"]=""; st.rerun()
        proveedores=sorted(base_p["Proveedor_detectado"].dropna().unique()); filtrados=[p for p in proveedores if busqueda.upper() in p.upper()] if busqueda else proveedores
        if filtrados:
            ps=st.selectbox("Proveedor",filtrados); mov=base_p[base_p["Proveedor_detectado"]==ps].copy(); mov["Impacto_abs"]=mov["Importe_CC"].abs(); mov=mov.sort_values("Impacto_abs",ascending=False); mov["Importe"]=mov["Importe_CC"].apply(fmt_money)
            cols=["Mes","Fecha","Sucursal","Factura_detectada","Proveedor_detectado","Categoria_proveedor","Nombre del rubro","Concepto_PNL","Detalle","des res","Detalle 2","Importe"]
            st.dataframe(mov[[c for c in cols if c in mov.columns]].head(150), use_container_width=True, height=520)

with tab6:
    st.subheader("🏢 Benchmark de costos entre sucursales")
    centros_b=st.multiselect("Centro de costo", centros_base, default=default_centros(centros_base,"repuestos"), key="centros_bench")
    grupos_b=st.multiselect("Categoría", ["Costos Controlables","Costos No Controlables"], default=["Costos Controlables"], key="grupo_bench")
    meses_b=st.multiselect("Meses", meses_all, default=meses_all[-4:], key="mes_bench")
    base_b=preparar_costos(df_filtrado, centros_b, grupos_b, meses_b)
    if base_b.empty: st.info("No hay datos para benchmark.")
    else:
        bench=base_b.groupby(["Sucursal","Grupo_PNL","Concepto_PNL"], as_index=False)["Importe_CC"].sum(); total_suc=base_b.groupby("Sucursal",as_index=False)["Importe_CC"].sum().rename(columns={"Importe_CC":"Costo total"}).sort_values("Costo total",ascending=False); total_suc["Etiqueta"]=total_suc["Costo total"].apply(fmt_money_short); total_suc["Costo total fmt"]=total_suc["Costo total"].apply(fmt_money)
        fig=px.bar(total_suc,x="Sucursal",y="Costo total",text="Etiqueta",title=f"Costo total por sucursal - {label_centros(centros_b)}"); preparar_para_labels(fig); st.plotly_chart(fig,use_container_width=True)
        st.dataframe(total_suc[["Sucursal","Costo total fmt"]].rename(columns={"Costo total fmt":"Costo total"}), use_container_width=True)
        st.markdown("### Heatmap por concepto y sucursal"); heat=bench.pivot_table(index="Concepto_PNL", columns="Sucursal", values="Importe_CC", aggfunc="sum", fill_value=0); st.dataframe(styled_heatmap_percent(heat), use_container_width=True, height=520)
        st.markdown("### Insight benchmark")
        mayor=total_suc.iloc[0]; menor=total_suc.iloc[-1]; total_general=total_suc["Costo total"].sum(); part=mayor["Costo total"]/total_general if total_general else 0
        topc=base_b[base_b["Sucursal"]==mayor["Sucursal"]].groupby("Concepto_PNL",as_index=False)["Importe_CC"].sum().sort_values("Importe_CC",ascending=False).head(3); ctxt=", ".join([f"{r['Concepto_PNL']} ({fmt_money(r['Importe_CC'])})" for _,r in topc.iterrows()])
        st.info(f"🧠 **{mayor['Sucursal']}** concentra **{fmt_pct(part)}** del costo total en **{label_centros(centros_b)}**, con **{fmt_money(mayor['Costo total'])}**. La menor es **{menor['Sucursal']}** con **{fmt_money(menor['Costo total'])}**. Principales conceptos: **{ctxt}**. ✅ Revisar escala operativa, contratos, consumos o imputaciones.")

with tab7:
    st.subheader("📑 P&L mensual interactivo — modelo validado")
    st.caption(
        "Estructura replicada contra la cuenta de resultados de referencia: "
        "Utilidad Bruta → Transferencia interna → Costos Controlables / No Controlables "
        "→ Utilidad Operativa Sucursal → Estructura → Utilidad Operativa → Resultado Financiero → Resultado final."
    )

    p1, p2 = st.columns(2)
    with p1:
        centros_pnl = st.multiselect(
            "Centro(s) de costo",
            centros_base,
            default=[c for c in ["Repuestos", "Tl. Mec."] if c in centros_base] or default_centros(centros_base, "repuestos"),
            key="centros_pnl_validado"
        )
    with p2:
        meses_pnl = st.multiselect(
            "Meses a mostrar",
            meses_all,
            default=meses_all[-4:],
            key="meses_pnl_validado"
        )

    if not centros_pnl:
        st.warning("Seleccioná al menos un centro de costo.")
    elif not meses_pnl:
        st.warning("Seleccioná al menos un mes.")
    else:
        meses_pnl = sorted(meses_pnl)
        pnl = construir_pnl_mensual_validado(df_filtrado, meses_pnl, centros_pnl)

        # KPIs del último mes seleccionado
        ultimo_mes = meses_pnl[-1]

        def _valor_pnl(concepto):
            x = pnl.loc[pnl["Concepto"] == concepto, ultimo_mes]
            return float(x.iloc[0]) if not x.empty else 0.0

        ventas_pnl = _valor_pnl("Ventas")
        ub_pnl = _valor_pnl("Utilidad Bruta")
        uos_pnl = _valor_pnl("Utilidad Operativa Sucursal")
        uo_pnl = _valor_pnl("Utilidad Operativa")
        rai_pnl = _valor_pnl("Resultado antes de Impuestos")
        rdi_pnl = _valor_pnl("Resultado después de Impuestos")

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Centro(s)", label_centros(centros_pnl))
        k2.metric("Ventas", fmt_money(ventas_pnl))
        k3.metric("Utilidad Bruta", fmt_money(ub_pnl), fmt_pct(ub_pnl / ventas_pnl if ventas_pnl else np.nan))
        k4.metric("Utilidad Operativa", fmt_money(uo_pnl), fmt_pct(uo_pnl / ventas_pnl if ventas_pnl else np.nan))
        k5.metric("Resultado antes Imp.", fmt_money(rai_pnl), fmt_pct(rai_pnl / ventas_pnl if ventas_pnl else np.nan))

        st.markdown("### Estado de resultados — importes")

        pnl_mostrar = pnl[["Grupo", "Concepto", "Rubros", "Lógica", "Tipo"] + meses_pnl + ["Acumulado"]].copy()
        for col in meses_pnl + ["Acumulado"]:
            pnl_mostrar[col] = pnl_mostrar[col].apply(fmt_money)

        st.dataframe(
            pnl_mostrar,
            use_container_width=True,
            height=820,
            hide_index=True
        )

        st.markdown("### Estado de resultados — % sobre ventas")
        pnl_pct = construir_pnl_porcentajes(pnl, meses_pnl)
        pnl_pct_mostrar = pnl_pct.copy()
        for col in meses_pnl:
            pnl_pct_mostrar[col] = pnl_pct_mostrar[col].apply(fmt_pct)

        st.dataframe(
            pnl_pct_mostrar,
            use_container_width=True,
            height=620,
            hide_index=True
        )

        st.markdown("### Validaciones automáticas del modelo")
        v1, v2, v3, v4 = st.columns(4)
        v1.metric("Utilidad Bruta", fmt_money(ub_pnl))
        v2.metric("Utilidad Oper. Sucursal", fmt_money(uos_pnl))
        v3.metric("Utilidad Operativa", fmt_money(uo_pnl))
        v4.metric("Resultado después Imp.", fmt_money(rdi_pnl))

        # Transferencia interna: explica si netea o no
        transf = _valor_pnl("Transferencia repuestos a taller")
        if "Repuestos" in centros_pnl and "Tl. Mec." in centros_pnl:
            if abs(transf) < 1:
                st.success(
                    "✅ La transferencia Repuestos → Taller se neutraliza en el consolidado seleccionado, "
                    "como corresponde a una transferencia interna."
                )
            else:
                st.warning(
                    f"⚠️ Se detectó una transferencia neta de {fmt_money(transf)} aun consolidando Repuestos + Taller. "
                    "Conviene revisar la imputación del movimiento en el mayor."
                )
        elif abs(transf) > 0:
            st.info(
                f"ℹ️ Transferencia interna detectada para la selección: **{fmt_money(transf)}**. "
                "La línea conserva su signo porque se está visualizando un centro individual o un subconjunto."
            )
        else:
            st.caption(
                "Transferencia Repuestos → Taller: no se detectó un movimiento explícito por texto en la base para este período. "
                "El modelo no inventa el importe; queda en $0 si el mayor no lo identifica."
            )

        st.markdown("### Resultado financiero")
        rfo = _valor_pnl("Resultado Financiero Operativo")
        st.info(
            f"Para **{ultimo_mes}**, la Utilidad Operativa es **{fmt_money(uo_pnl)}** y el "
            f"Resultado Financiero Operativo es **{fmt_money(rfo)}**, llegando a un "
            f"Resultado antes de Impuestos de **{fmt_money(rai_pnl)}**."
        )

        st.caption(
            "Nota: Egresos Dirección (9-10), Ingresos Extraordinarios (12-1) y Egresos Extraordinarios (12-2) "
            "se muestran como líneas informativas y quedan fuera del resultado validado, tal como en el modelo de referencia."
        )

with tab8:
    st.subheader("📒 Evolución por cuenta contable")
    col1,col2,col3=st.columns(3)
    with col1: centros_cta=st.multiselect("Centro de costo", centros_base, default=default_centros(centros_base,"repuestos"), key="centros_cuentas")
    with col2: grupos_cta=st.multiselect("Categoría", ["Costos Controlables","Costos No Controlables"], default=["Costos Controlables","Costos No Controlables"], key="grupo_cuentas")
    with col3: meses_cta=st.multiselect("Meses", meses_all, default=meses_all[-4:], key="meses_cuentas")
    base_cta=df_filtrado[(df_filtrado["Grupo_PNL"].isin(grupos_cta))&(df_filtrado["Mes"].isin(meses_cta))].copy(); base_cta["Importe_CC"]=campo_centros_gestion(base_cta, centros_cta); base_cta=base_cta[base_cta["Importe_CC"]!=0].copy()
    if base_cta.empty: st.info("No hay datos para los filtros seleccionados.")
    else:
        meses_ord=sorted(base_cta["Mes"].dropna().unique())
        tabla=base_cta.pivot_table(index=["Cuenta:","Nombre cuenta","Rubro_calc","Nombre del rubro","Grupo_PNL"], columns="Mes", values="Importe_CC", aggfunc="sum", fill_value=0).reset_index()
        if len(meses_ord)>=2:
            ant,act=meses_ord[-2],meses_ord[-1]; tabla["Mes anterior"]=tabla[ant]; tabla["Mes actual"]=tabla[act]; tabla["Evolución $"]=tabla["Mes actual"]-tabla["Mes anterior"]; tabla["Evolución %"]=np.where(tabla["Mes anterior"].abs()>0,tabla["Evolución $"]/tabla["Mes anterior"].abs(),np.nan)
        else:
            tabla["Mes anterior"]=np.nan; tabla["Mes actual"]=tabla[meses_ord[-1]]; tabla["Evolución $"]=np.nan; tabla["Evolución %"]=np.nan
        tabla["Impacto_abs"]=tabla["Evolución $"].abs(); tabla["Semáforo"]=tabla["Evolución $"].apply(semaforo_variacion); sev=tabla.apply(severidad_y_motivo, axis=1); tabla["Severidad"]=[x[0] for x in sev]; tabla["Motivo severidad"]=[x[1] for x in sev]; tabla["Tipo evento"]=tabla.apply(tipo_evento, axis=1); tabla=tabla.sort_values("Impacto_abs",ascending=False)
        total_act=tabla["Mes actual"].sum(); total_ant=tabla["Mes anterior"].sum(); ev=total_act-total_ant; evp=ev/abs(total_ant) if total_ant!=0 else np.nan
        k1,k2,k3,k4=st.columns(4); k1.metric("Centro de costo", label_centros(centros_cta)); k2.metric("Costo mes actual", fmt_money(total_act)); k3.metric("Evolución total", fmt_money(ev), fmt_pct(evp)); k4.metric("Cuentas analizadas", len(tabla))
        st.markdown("### Top cuentas con mayor evolución vs mes anterior")
        top=tabla.dropna(subset=["Evolución $"]).head(15).copy(); top["Etiqueta"]=top["Evolución $"].apply(fmt_money_short)
        if not top.empty:
            fig=px.bar(top,x="Evolución $",y="Nombre cuenta",color="Semáforo",text="Etiqueta",orientation="h",title="Cuentas con mayor variación absoluta vs mes anterior"); preparar_para_labels(fig); st.plotly_chart(fig,use_container_width=True)
        st.markdown("### Evolución mensual por cuenta contable")
        mt=tabla.copy()
        for m in meses_ord: mt[m]=mt[m].apply(fmt_money)
        for col in ["Mes anterior","Mes actual","Evolución $"]: mt[col]=mt[col].apply(fmt_money)
        mt["Evolución %"]=mt["Evolución %"].apply(fmt_pct)
        st.dataframe(mt[["Cuenta:","Nombre cuenta","Rubro_calc","Nombre del rubro","Grupo_PNL"]+meses_ord+["Evolución $","Evolución %","Semáforo","Severidad","Motivo severidad","Tipo evento"]], use_container_width=True, height=560)
        st.markdown("### Movimientos de la cuenta seleccionada")
        cuentas=(tabla["Cuenta:"].astype(str)+" - "+tabla["Nombre cuenta"].astype(str)).tolist(); cs=st.selectbox("Seleccioná una cuenta", cuentas, key="cuenta_movimientos"); cn=cs.split(" - ")[0]
        mov=base_cta[base_cta["Cuenta:"].astype(str)==cn].copy(); mov["Importe"]=mov["Importe_CC"].apply(fmt_money); mov["Impacto_abs"]=mov["Importe_CC"].abs(); mov=mov.sort_values("Impacto_abs",ascending=False)
        cols=["Mes","Fecha","Sucursal","Cuenta:","Nombre cuenta","Rubro_calc","Nombre del rubro","Grupo_PNL","Concepto_PNL","Proveedor_detectado","Factura_detectada","Detalle","des res","Detalle 2","Importe"]
        st.dataframe(mov[[c for c in cols if c in mov.columns]].head(150), use_container_width=True, height=520)
        st.download_button("⬇️ Descargar evolución por cuenta contable", data=tabla.to_csv(index=False).encode("utf-8-sig"), file_name=f"evolucion_cuentas_{label_centros(centros_cta)}.csv", mime="text/csv")

with tab9:
    st.subheader("🧾 Control de signos")
    control=df_filtrado.groupby(["Nombre del rubro","Signo_rubro"],as_index=False).agg(Parcial_original=("Parcial","sum"),Parcial_gestion=("Parcial_Gestion","sum")); control["Parcial original"]=control["Parcial_original"].apply(fmt_money); control["Parcial gestión"]=control["Parcial_gestion"].apply(fmt_money)
    st.dataframe(control[["Nombre del rubro","Signo_rubro","Parcial original","Parcial gestión"]], use_container_width=True, height=650)

with tab10:
    st.subheader("🔎 Drilldown contable")
    buscar=st.text_input("Buscar por cuenta, proveedor, factura, detalle, descripción o rubro")
    drill=df_filtrado.copy()
    if buscar:
        t=buscar.lower(); mask=pd.Series(False,index=drill.index)
        for col in ["Nombre cuenta","Detalle","des res","Detalle 2","Nombre del rubro","Proveedor_detectado","Factura_detectada"]:
            if col in drill.columns: mask=mask|drill[col].astype(str).str.lower().str.contains(t,na=False)
        drill=drill[mask]
    total=drill["Parcial_Gestion"].sum(); cant=len(drill)
    rub="Sin datos"; prov="Sin datos"; suc="Sin datos"
    if not drill.empty:
        rub=drill.groupby("Nombre del rubro")["Parcial_Gestion"].sum().abs().sort_values(ascending=False).index[0]; prov=drill.groupby("Proveedor_detectado")["Parcial_Gestion"].sum().abs().sort_values(ascending=False).index[0]; suc=drill.groupby("Sucursal")["Parcial_Gestion"].sum().abs().sort_values(ascending=False).index[0]
    k1,k2,k3,k4=st.columns(4); k1.metric("Total selección filtrada",fmt_money(total)); k2.metric("Cantidad movimientos",f"{cant}"); k3.metric("Proveedor principal",prov); k4.metric("Rubro principal",rub); st.caption(f"Sucursal con mayor impacto en la búsqueda: {suc}")
    dm=drill.copy(); dm["Parcial"]=dm["Parcial"].apply(fmt_money); dm["Parcial gestión"]=dm["Parcial_Gestion"].apply(fmt_money)
    cols=["Fecha","Mes","Sucursal","Cuenta:","Nombre cuenta","Rubro_calc","Nombre del rubro","Grupo_PNL","Concepto_PNL","Proveedor_detectado","Factura_detectada","Categoria_proveedor","Detalle","des res","Detalle 2","Parcial","Parcial gestión"]
    st.dataframe(dm[[c for c in cols if c in dm.columns]], use_container_width=True, height=650)
    st.download_button("⬇️ Descargar drilldown filtrado", data=drill.to_csv(index=False).encode("utf-8-sig"), file_name="drilldown_mayores_lux.csv", mime="text/csv")

with tab11:
    st.subheader("⚙️ Diccionario y reglas del modelo")
    st.markdown("""
### P&L validado
La pestaña **📑 P&L** sigue la secuencia validada contra la cuenta de resultados de referencia:

1. Ventas - Descuentos - Costo de Ventas - Rdo. Neto Gestoría = **Margen Bruto Gestión Comercial**.
2. Ajustes + reacondicionamiento + incentivos/comisiones = **Margen Bruto Secundario**.
3. Otros ingresos/egresos = **Utilidad Bruta**.
4. Se incorpora la **Transferencia Repuestos → Taller** con signo por centro; al consolidar ambos centros debe neutralizarse.
5. Se restan **Costos Controlables + Costos No Controlables** = **Utilidad Operativa Sucursal**.
6. Se restan **Costos de Estructura de Administración Central** = **Utilidad Operativa**.
7. Ingresos financieros - egresos financieros = **Resultado Financiero Operativo**.
8. Utilidad Operativa + Resultado Financiero = **Resultado antes de Impuestos**.
9. Se descuenta **Impuesto a las Ganancias** cuando existe movimiento identificable = **Resultado después de Impuestos**.

Las líneas 9-10, 12-1 y 12-2 se informan aparte y no se incorporan al resultado validado.
""")

    st.markdown("""
### 1. Lógica principal
- Cada fila del mayor es un movimiento contable individual.
- `Parcial_Gestion` normaliza signos para lectura gerencial.
- Para costos: variación positiva = aumentó el costo; variación negativa = bajó el costo.
- Los tabs principales permiten seleccionar **más de un centro de costo**.

### 2. Severidad
Combina impacto absoluto, variación porcentual e importe actual.

### 3. Proveedores
El proveedor se detecta automáticamente desde `Detalle`, `des res` y `Detalle 2`.

### 4. Heatmap sucursales
Cada celda muestra `$ importe (% participación dentro del concepto)` con color por concentración.

### 5. Oportunidades de Ahorro
Este tab separa gastos de baja accionabilidad (alquileres, licencias Toyota, Oversoft, etc.) de gastos trabajables. Estima ahorro potencial conservador: 10% para alta accionabilidad y 5% para media.

### 6. Cuentas contables
Permite ver número de cuenta, nombre, rubro+subrubro, categoría, importe mensual, evolución, severidad y movimientos explicativos.
""")
