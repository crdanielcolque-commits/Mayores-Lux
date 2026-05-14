import re
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
    "Vtas 0 Km", "Vtas Usado", "PPAA", "Repuestos", "Tl. Mec.",
    "Finanzas", "Mayorista", "ChapyPintu", "Central", "Administr."
]

CENTROS_POSVENTA = ["Repuestos", "Tl. Mec.", "Mayorista", "ChapyPintu"]

SIGNO_RUBRO = {
    "VENTAS": "-", "INCENTIVOS": "-", "COMIS. P/VTA DIRECTA": "-",
    "INGRESO EXTRAORDIN": "-", "OTROS ING FINANCIERO": "-",
    "INGRESOS SEGUROS": "-", "COMIS CONSIGNACIONES": "-", "SOBRANTES DE INV.": "-",
    "INTERESES IMPOSITIVO": "+", "MERMAS DE INVENTARIO": "+",
    "GTOS GESTIO JUDICIAL": "+", "COMISION CHANGO CAR": "+",
    "UTILES Y MAT. DE OFI": "+", "Adm Ctral (No Usar)": "+",
    "COMIS. A VENDEDORES": "+", "SUELDOS ADM. Y CS.SS": "+",
    "SEGUROS": "+", "SUELDOS ADM CENTRAL": "+", "GTOS ATENCION CLIENT": "+",
    "UTILES Y MAT DE OFIC": "+", "EGRESO EXTRAORDINARI": "+",
    "TELEFONO E INTERNET": "+", "MANT. RODADOS": "+",
    "IMPUESTOS Y TASAS": "+", "OTROS GTOS FIJOS": "+",
    "PREPARAC. Y PREENTRE": "+", "SEGURIDAD Y VIGILANC": "+",
    "HERRAM. MAT. Y FLETE": "+", "EGRESOS GESTORIA": "+",
    "MOVILIDAD Y VIATICOS": "+", "ALQUILERES": "+",
    "LUZ,AGUA Y GAS": "+", "HONORARIOS PROFESION": "+",
    "Serv. Limpieza": "+", "PUBLICIDAD Y PROMOC.": "+",
    "COSTO DE REAC. Y ACC": "+", "MANTENIM. BS. DE USO": "+",
    "SERV LUZ.TEL.SUSCRIP": "+", "COM. Y GTOS BANCARIO": "+",
    "INGRESOS GESTORIA": "+", "SS. GRAT. Y CS. INT.": "+",
    "AMORTIZACIONES": "+", "OTROS EGR. FINANCIER": "+",
    "IMPUESTOS FINANCIAC": "+", "INT. FINANC. VEHICUL": "+",
    "DESCUENTOS S/ VTAS.": "+", "COSTO DE VENTAS": "+"
}

PNL_ESTRUCTURA = [
    ("mas", "Ventas", ["4-1"], "Margen Bruto Gestión Comercial"),
    ("menos", "Descuentos sobre ventas", ["4-2"], "Margen Bruto Gestión Comercial"),
    ("menos", "Costo de Ventas", ["5-1"], "Margen Bruto Gestión Comercial"),
    ("menos", "Rdo. Neto Gestoría", ["6-1", "6-2"], "Margen Bruto Gestión Comercial"),
    ("igual", "Margen Bruto Gestión Comercial", [], "Margen Bruto Gestión Comercial"),

    ("menos", "Costo Reacondic. y Acces.", ["5-2"], "Margen Bruto Secundario"),
    ("igual", "Margen Bruto Primario", [], "Margen Bruto Secundario"),
    ("mas", "Incentivos", ["4-3"], "Margen Bruto Secundario"),
    ("mas", "Incentivo Devengado", ["4-4"], "Margen Bruto Secundario"),
    ("mas", "Comisión Consignaciones", ["6-3"], "Margen Bruto Secundario"),
    ("menos", "Comisión Pagadas", ["6-6"], "Margen Bruto Secundario"),
    ("mas", "Comisión P/Vta Directa", ["10-1"], "Margen Bruto Secundario"),
    ("igual", "Margen Bruto Secundario", [], "Margen Bruto Secundario"),

    ("menos", "Mermas de Inventarios", ["5-3"], "Otros Ingresos / Egresos"),
    ("menos", "Sobrantes de Inventarios", ["5-4"], "Otros Ingresos / Egresos"),
    ("menos", "Pérdida IVA Usados", ["5-5"], "Otros Ingresos / Egresos"),
    ("menos", "Horas no aplicadas mecánicos", ["6-4"], "Otros Ingresos / Egresos"),
    ("mas", "Resultado Venta de PPAA MS", ["6-5"], "Otros Ingresos / Egresos"),
    ("mas", "Ingresos Seguros y Comis Gestión Vta", ["10-4"], "Otros Ingresos / Egresos"),
    ("menos", "Egresos Seguros", ["11-5"], "Otros Ingresos / Egresos"),
    ("igual", "Utilidad Bruta", [], "Utilidad Bruta"),

    ("menos", "Comisiones sobre Ventas", ["7-2"], "Costos Controlables"),
    ("menos", "Sueldos y Cargas Sociales", ["8-1"], "Costos Controlables"),
    ("menos", "Sueldos Administración y C. Soc.", ["8-4"], "Costos Controlables"),
    ("menos", "Gastos de Atención clientes", ["7-1"], "Costos Controlables"),
    ("menos", "Servicios gratuitos y Cargos internos", ["7-4"], "Costos Controlables"),
    ("menos", "Herramientas, materiales y fletes", ["7-6"], "Costos Controlables"),
    ("menos", "Publicidad y Promoción", ["8-2"], "Costos Controlables"),
    ("menos", "Mantenimiento rodados y equipos", ["8-3"], "Costos Controlables"),
    ("menos", "Movilidad y Viáticos", ["8-6"], "Costos Controlables"),
    ("menos", "Mantenimiento Bienes de Uso", ["8-8"], "Costos Controlables"),
    ("menos", "Fuerza motriz, luz, agua y gas", ["8-9"], "Costos Controlables"),
    ("menos", "Teléfonos e internet", ["8-10"], "Costos Controlables"),
    ("menos", "Serv. Limpieza", ["8-11"], "Costos Controlables"),
    ("menos", "Útiles y materiales de oficina", ["8-12"], "Costos Controlables"),
    ("menos", "Otros Gastos Fijos", ["8-13"], "Costos Controlables"),
    ("menos", "Alquileres", ["8-14"], "Costos Controlables"),
    ("menos", "Previsiones Varias", ["8-17"], "Costos Controlables"),
    ("menos", "Deudores Incobrables", ["8-19"], "Costos Controlables"),
    ("menos", "Preparación y entrega", ["7-3"], "Costos Controlables"),
    ("menos", "Seguridad y vigilancia", ["8-20"], "Costos Controlables"),

    ("menos", "Impuestos", ["7-5"], "Costos No Controlables"),
    ("menos", "Honorarios profesionales", ["8-5"], "Costos No Controlables"),
    ("menos", "Recupero de Gastos Toyota", ["8-7"], "Costos No Controlables"),
    ("menos", "Amortizaciones", ["8-15"], "Costos No Controlables"),
    ("menos", "Seguros", ["8-16"], "Costos No Controlables"),
    ("menos", "Impuestos y tasas", ["8-18"], "Costos No Controlables"),
    ("igual", "Utilidad Operativa Sucursal", [], "Utilidad Operativa Sucursal"),

    ("menos", "Sueldos Gtes y Jefes Suc.", ["9-1"], "Controlables de Estructura"),
    ("menos", "Sueldos Adm. Central", ["9-2"], "Controlables de Estructura"),
    ("menos", "Prestaciones La Luz", ["9-3"], "Controlables de Estructura"),
    ("menos", "Movilidad y Viáticos Central", ["9-4"], "Controlables de Estructura"),
    ("menos", "Mantenimiento Bs Uso Central", ["9-5"], "Controlables de Estructura"),
    ("menos", "Útiles y materiales de oficina Central", ["9-6"], "Controlables de Estructura"),
    ("menos", "Serv., Energía, Suscripciones Adm Central", ["9-7"], "Controlables de Estructura"),
    ("menos", "Alquileres Adm Central", ["9-9"], "Controlables de Estructura"),
    ("menos", "Amortizaciones Estructura", ["9-8"], "Costos no Controlables de Estructura"),
    ("igual", "Utilidad Operativa", [], "Utilidad Operativa"),

    ("mas", "Intereses Financiación Vehículos", ["10-2"], "Ingresos Financieros"),
    ("mas", "Otros Ingresos Financieros", ["10-3"], "Ingresos Financieros"),
    ("menos", "Impuestos Financiación", ["11-1"], "Egresos Financieros"),
    ("menos", "Intereses Impositivos", ["11-2"], "Egresos Financieros"),
    ("menos", "Comisiones y gastos bancarios", ["11-3"], "Egresos Financieros"),
    ("menos", "Financiación cap trab", ["11-4"], "Egresos Financieros"),
    ("igual", "Resultado antes de Impuestos", [], "Resultado antes de Impuestos"),
    ("menos", "Impuesto a las Ganancias", [], "Impuesto a las Ganancias"),
    ("igual", "Resultado después de Impuestos", [], "Resultado después de Impuestos"),
]


# =========================
# HELPERS
# =========================

def limpiar_numero(x):
    if pd.isna(x):
        return 0.0
    if isinstance(x, (int, float, np.number)):
        return float(x)

    s = str(x).strip().replace("$", "").replace(" ", "").replace("\xa0", "")
    if s == "":
        return 0.0

    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")

    try:
        return float(s)
    except Exception:
        return 0.0


def limpiar_texto(x):
    return "" if pd.isna(x) else str(x).strip()


def normalizar_rubro(x):
    if pd.isna(x):
        return ""
    return str(x).strip().replace(".0", "").replace(" ", "")


def fmt_money(x):
    try:
        x = float(x)
    except Exception:
        x = 0
    return "$ {:,.0f}".format(x).replace(",", ".")


def fmt_money_short(x):
    try:
        x = float(x)
    except Exception:
        x = 0
    signo = "-" if x < 0 else ""
    x = abs(x)
    if x >= 1_000_000_000:
        return f"{signo}$ {x/1_000_000_000:.1f}B"
    if x >= 1_000_000:
        return f"{signo}$ {x/1_000_000:.1f}M"
    if x >= 1_000:
        return f"{signo}$ {x/1_000:.0f}K"
    return f"{signo}$ {x:.0f}"


def fmt_pct(x):
    try:
        if pd.isna(x):
            return ""
        return "{:.1%}".format(float(x))
    except Exception:
        return ""


def signo_factor_por_rubro(nombre_rubro):
    signo = SIGNO_RUBRO.get(limpiar_texto(nombre_rubro), "+")
    return -1 if signo == "-" else 1


def mapa_rubro_a_pnl():
    filas = []
    for logica, concepto, rubros, grupo in PNL_ESTRUCTURA:
        for rubro in rubros:
            filas.append({
                "Rubro_calc": rubro,
                "Concepto_PNL": concepto,
                "Grupo_PNL": grupo,
                "Logica_PNL": logica
            })
    return pd.DataFrame(filas)


def extraer_factura_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).upper()

    patrones = [
        r'\bF[A-Z]\s?\d{4}[- ]?\d{4,8}\b',
        r'\b[A-Z]{1,2}\s?\d{4}[- ]?\d{4,8}\b',
        r'\b[A-Z]\d{10,14}\b',
        r'\b\d{4}[- ]\d{6,8}\b'
    ]

    for patron in patrones:
        m = re.search(patron, texto)
        if m:
            return m.group(0).strip()
    return ""


def extraer_factura(row):
    texto = " ".join([str(row.get(c, "")) for c in ["Detalle", "des res", "Detalle 2"]])
    return extraer_factura_texto(texto)


def normalizar_proveedor_nombre(proveedor):
    p = str(proveedor).upper().strip()

    reglas_contiene = {
        "ROQUE JUAN LOZANO": "ROQUE JUAN LOZANO",
        "LOZANO MARIA": "LOZANO MARIA",
        "TOYOTA ENTINA": "TOYOTA ENTINA",
        "TOYOTA ARGENTINA": "TOYOTA ARGENTINA",
        "OVERSOFT": "OVERSOFT",
        "EJE EJE LAS LOMAS": "EJE EJE LAS LOMAS",
        "MERCADO LIBRE": "MERCADO LIBRE",
        "MERCADOLIBRE": "MERCADO LIBRE",
        "MERCADO PAGO": "MERCADO LIBRE",
        "META": "META",
        "FACEBOOK": "META",
        "GOOGLE": "GOOGLE",
        "YPF": "YPF",
        "SHELL": "SHELL",
        "AXION": "AXION",
        "TELECOM": "TELECOM",
        "PERSONAL": "TELECOM",
        "MOVISTAR": "MOVISTAR",
        "CLARO": "CLARO",
        "EDESA": "EDESA",
        "GASNOR": "GASNOR",
        "BETA SERVICIO LIMPIEZA": "BETA SERVICIO LIMPIEZA",
        "ATIEMPO SEGURIDAD": "ATIEMPO SEGURIDAD",
        "CHANGO TRUCK": "CHANGO TRUCK",
    }

    for k, v in reglas_contiene.items():
        if k in p:
            return v

    quitar = [
        "ALQ LOC", "ALQ LOCAL", "MAYOR VALOR", "MAR", "FEB", "ABR", "ENE",
        "NOCT", "DIURNAS", "MEJORAS", "SOPORTE EVOLUTIVO", "MANTENIMIENTO",
        "ABONO", "CUOTA", "PAGO", "FACTURA"
    ]

    for q in quitar:
        p = p.replace(q, " ")

    p = re.sub(r'\s+', ' ', p).strip()
    palabras = [w for w in p.split(" ") if len(w) > 2]

    if len(palabras) >= 3:
        return " ".join(palabras[:3])
    if len(palabras) >= 1:
        return " ".join(palabras)
    return "SIN IDENTIFICAR"


def extraer_proveedor(row):
    textos = []
    for col in ["Detalle 2", "des res", "Detalle"]:
        val = row.get(col, "")
        if pd.notna(val):
            textos.append(str(val))

    texto = " ".join(textos).upper()

    factura = extraer_factura_texto(texto)
    if factura:
        pos = texto.find(factura)
        if pos >= 0:
            texto = texto[pos + len(factura):]

    basura = [
        "FACTURA", "RECIBO", "COMP", "COMPROBANTE", "PAGO", "PAGOS", "TRANSFERENCIA",
        "FC", "FA", "FB", "NC", "ND", "CUIT", "IVA", "ARG", "S.A.", "SA", "SRL",
        "S.R.L.", "LTDA", "NRO", "Nº", "NUM", "PESOS"
    ]

    for b in basura:
        texto = texto.replace(b, " ")

    texto = re.sub(r'\d+', ' ', texto)
    texto = re.sub(r'[-_/.,:;()]+', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()

    palabras = [p for p in texto.split(" ") if len(p) > 2]
    proveedor = " ".join(palabras[:6]).strip()

    if proveedor == "":
        proveedor = "SIN IDENTIFICAR"

    return normalizar_proveedor_nombre(proveedor)


def categoria_proveedor(proveedor, detalle):
    texto = f"{proveedor} {detalle}".upper()

    reglas = {
        "Marketing digital": ["META", "GOOGLE", "FACEBOOK", "INSTAGRAM", "ADS", "PUBLICIDAD"],
        "Marketplace / plataformas": ["MERCADO LIBRE", "MERCADOLIBRE", "MERCADO PAGO"],
        "Combustible / movilidad": ["YPF", "SHELL", "AXION", "COMBUSTIBLE", "NAFTA", "GASOIL"],
        "Telecomunicaciones": ["TELECOM", "PERSONAL", "MOVISTAR", "CLARO", "INTERNET", "TELEFONO"],
        "Energía / servicios": ["EDESA", "GASNOR", "LUZ", "GAS", "AGUA", "ENERGIA"],
        "Seguros": ["SEGURO", "SANCOR", "FEDERACION", "MAPFRE", "ZURICH"],
        "Limpieza / seguridad": ["LIMPIEZA", "SEGURIDAD", "VIGILANC", "ATIEMPO"],
        "Toyota / terminal": ["TOYOTA"],
        "Sistemas / software": ["OVERSOFT", "SIAC", "SISTEMA", "SOFTWARE"],
        "Alquileres": ["LOZANO", "ALQUILER", "ALQ"],
        "Honorarios / profesionales": ["HONORARIO", "ESTUDIO", "ASESOR", "CONSULT"],
    }

    for cat, keys in reglas.items():
        if any(k in texto for k in keys):
            return cat
    return "Otros / no clasificado"


def semaforo_variacion(var):
    if pd.isna(var):
        return "⚪ Sin comparación"
    if var > 0:
        return "🔴 Aumentó costo"
    if var < 0:
        return "🟢 Bajó costo"
    return "🟡 Sin cambio"


def severidad_y_motivo(row):
    var_abs = abs(row.get("Variación $", 0)) if not pd.isna(row.get("Variación $", np.nan)) else 0
    var_pct_raw = row.get("Variación %", np.nan)
    var_pct = abs(var_pct_raw) if not pd.isna(var_pct_raw) else 0
    actual = abs(row.get("Mes actual", 0)) if not pd.isna(row.get("Mes actual", np.nan)) else 0
    anterior = abs(row.get("Mes anterior", 0)) if not pd.isna(row.get("Mes anterior", np.nan)) else 0

    score = 0
    motivos = []

    if anterior == 0 and actual > 0:
        score += 20
        motivos.append("sin gasto en mes anterior")

    if var_abs >= 5_000_000:
        score += 40
        motivos.append("variación mayor a $5M")
    elif var_abs >= 1_000_000:
        score += 25
        motivos.append("variación mayor a $1M")
    elif var_abs >= 300_000:
        score += 10
        motivos.append("variación mayor a $300K")

    if var_pct >= 1:
        score += 35
        motivos.append("variación superior al 100%")
    elif var_pct >= 0.4:
        score += 20
        motivos.append("variación superior al 40%")
    elif var_pct >= 0.15:
        score += 10
        motivos.append("variación superior al 15%")

    if actual >= 5_000_000:
        score += 20
        motivos.append("importe actual mayor a $5M")
    elif actual >= 1_000_000:
        score += 10
        motivos.append("importe actual mayor a $1M")

    if score >= 70:
        sev = "🔴 Crítico"
    elif score >= 45:
        sev = "🟠 Alto"
    elif score >= 20:
        sev = "🟡 Medio"
    else:
        sev = "🟢 Bajo"

    if not motivos:
        motivos = ["impacto bajo o sin variación relevante"]

    return sev, "; ".join(motivos)


def tipo_evento(row):
    ant = row.get("Mes anterior", 0)
    act = row.get("Mes actual", 0)
    var = row.get("Variación $", 0)
    var_pct = row.get("Variación %", np.nan)

    if ant == 0 and act > 0:
        return "🆕 Nuevo / sin histórico"
    if not pd.isna(var_pct) and var_pct > 1:
        return "📈 Crecimiento abrupto"
    if var > 0:
        return "🔴 Mayor presión"
    if var < 0:
        return "🟢 Mejora"
    return "🟡 Estable"


def preparar_para_labels(fig):
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode="hide")
    return fig


# =========================
# DATA
# =========================

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

    for col in ["Debe", "Haber", "Parcial"] + CENTROS_COSTO:
        if col in df.columns:
            df[col] = df[col].apply(limpiar_numero)
        else:
            df[col] = 0.0

    if "Rub" in df.columns and "SRub" in df.columns:
        df["Rubro_calc"] = df["Rub"].apply(normalizar_rubro) + "-" + df["SRub"].apply(normalizar_rubro)
    elif "union" in df.columns:
        df["Rubro_calc"] = df["union"].apply(normalizar_rubro)
    else:
        df["Rubro_calc"] = ""

    for col in ["Sucursal", "Nombre cuenta", "Cuenta:", "Cuenta", "Nombre del rubro",
                "Detalle", "des res", "Detalle 2", "Dpto", "Nro."]:
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

    df["Factura_detectada"] = df.apply(extraer_factura, axis=1)
    df["Proveedor_detectado"] = df.apply(extraer_proveedor, axis=1)
    df["Texto_movimiento"] = (
        df["Detalle"].astype(str) + " " +
        df["des res"].astype(str) + " " +
        df["Detalle 2"].astype(str)
    )

    df["Categoria_proveedor"] = df.apply(
        lambda r: categoria_proveedor(r["Proveedor_detectado"], r["Texto_movimiento"]),
        axis=1
    )

    return df


def preparar_costos(df, centro, grupos, meses):
    campo = f"{centro}_Gestion"
    base = df[
        (df["Grupo_PNL"].isin(grupos)) &
        (df["Mes"].isin(meses))
    ].copy()
    base["Importe_CC"] = base[campo]
    base = base[base["Importe_CC"] != 0].copy()
    return base


def tabla_variaciones(base, index_cols):
    meses = sorted(base["Mes"].dropna().unique())

    piv = base.pivot_table(
        index=index_cols,
        columns="Mes",
        values="Importe_CC",
        aggfunc="sum",
        fill_value=0
    ).reset_index()

    if len(meses) >= 2:
        ant, act = meses[-2], meses[-1]
        piv["Mes anterior"] = piv[ant]
        piv["Mes actual"] = piv[act]
        piv["Variación $"] = piv["Mes actual"] - piv["Mes anterior"]
        piv["Variación %"] = np.where(
            piv["Mes anterior"].abs() > 0,
            piv["Variación $"] / piv["Mes anterior"].abs(),
            np.nan
        )
    elif len(meses) == 1:
        act = meses[-1]
        piv["Mes anterior"] = np.nan
        piv["Mes actual"] = piv[act]
        piv["Variación $"] = np.nan
        piv["Variación %"] = np.nan
    else:
        piv["Mes anterior"] = np.nan
        piv["Mes actual"] = np.nan
        piv["Variación $"] = np.nan
        piv["Variación %"] = np.nan

    sev_motivos = piv.apply(severidad_y_motivo, axis=1)
    piv["Severidad"] = [x[0] for x in sev_motivos]
    piv["Motivo severidad"] = [x[1] for x in sev_motivos]
    piv["Tipo evento"] = piv.apply(tipo_evento, axis=1)
    piv["Semáforo"] = piv["Variación $"].apply(semaforo_variacion)
    piv["Impacto_abs"] = piv["Variación $"].abs()

    return piv.sort_values("Impacto_abs", ascending=False)


def construir_pnl_mensual(df, meses):
    filas = []
    acumulados = {m: 0.0 for m in meses}

    for logica, concepto, rubros, grupo in PNL_ESTRUCTURA:
        fila = {
            "Lógica": logica,
            "Grupo": grupo,
            "Concepto": concepto,
            "Rubros": " + ".join(rubros)
        }

        for mes in meses:
            dmes = df[df["Mes"] == mes]

            if rubros:
                bruto = dmes.loc[dmes["Rubro_calc"].isin(rubros), "Parcial_Gestion"].sum()
                if logica == "menos":
                    importe = -abs(bruto)
                elif logica == "mas":
                    importe = abs(bruto)
                else:
                    importe = bruto

                acumulados[mes] += importe
                fila[mes] = importe
            else:
                fila[mes] = acumulados[mes]

        fila["Acumulado"] = sum(fila[m] for m in meses)
        filas.append(fila)

    return pd.DataFrame(filas)


def styled_heatmap_percent(df_num):
    row_totals = df_num.abs().sum(axis=1).replace(0, np.nan)
    pct = df_num.abs().div(row_totals, axis=0)

    df_display = df_num.copy().astype(str)
    for idx in df_num.index:
        for col in df_num.columns:
            val = df_num.loc[idx, col]
            p = pct.loc[idx, col]
            if pd.isna(p):
                df_display.loc[idx, col] = f"{fmt_money(val)} (0,0%)"
            else:
                df_display.loc[idx, col] = f"{fmt_money(val)} ({p:.1%})"

    def color_cell(v):
        try:
            p = float(str(v).split("(")[1].replace("%)", "").replace(",", ".")) / 100
        except Exception:
            p = 0

        if p >= 0.50:
            return "background-color: #ffb3b3; color: #111;"
        if p >= 0.30:
            return "background-color: #ffd6a5; color: #111;"
        if p >= 0.15:
            return "background-color: #fff3b0; color: #111;"
        if p > 0:
            return "background-color: #d8f3dc; color: #111;"
        return "background-color: #f5f5f5; color: #777;"

    return df_display.style.applymap(color_cell)


# =========================
# STYLE
# =========================

st.markdown("""
<style>
h1 {font-weight: 800; color: #1f2a44;}
h2, h3 {color: #1f2a44;}
[data-testid="stMetricValue"] {font-size: 26px;}
.block-container {padding-top: 1.4rem;}
</style>
""", unsafe_allow_html=True)


# =========================
# APP
# =========================

st.title("📊 Dashboard Mayores Contables LUX")
st.caption("Control de costos, alertas, proveedores, benchmark, insights y drilldown contable.")

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
    sucursales = sorted(df["Sucursal"].dropna().astype(str).unique())
    suc_sel = st.multiselect("Sucursal", sucursales, default=sucursales)

df_filtrado = df[df["Sucursal"].isin(suc_sel)].copy() if suc_sel else df.copy()
meses_all = sorted(df_filtrado["Mes"].dropna().unique())

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🎯 Control de Costos",
    "🚨 Alertas & Insights",
    "🏭 Proveedores",
    "🏢 Benchmark Sucursales",
    "📑 P&L",
    "🧾 Control signos",
    "🔎 Drilldown",
    "⚙️ Diccionario"
])


# =========================
# TAB 1 CONTROL COSTOS
# =========================

with tab1:
    st.subheader("🎯 Control de costos controlables y no controlables")

    c1, c2, c3 = st.columns(3)

    centros_opciones = [c for c in CENTROS_POSVENTA + CENTROS_COSTO if f"{c}_Gestion" in df_filtrado.columns]
    centros_opciones = list(dict.fromkeys(centros_opciones))

    with c1:
        centro = st.selectbox("Centro de costo / sector", centros_opciones, index=0)

    with c2:
        grupos_sel = st.multiselect(
            "Categoría de costos",
            ["Costos Controlables", "Costos No Controlables"],
            default=["Costos Controlables", "Costos No Controlables"]
        )

    with c3:
        modo = st.selectbox("Período", ["Últimos 2 meses", "Últimos 4 meses", "Selección manual"], index=1)

    if modo == "Últimos 2 meses":
        meses_sel = meses_all[-2:]
    elif modo == "Últimos 4 meses":
        meses_sel = meses_all[-4:]
    else:
        meses_sel = st.multiselect("Meses", meses_all, default=meses_all[-4:])

    base = preparar_costos(df_filtrado, centro, grupos_sel, meses_sel)

    if base.empty:
        st.info("No hay datos para los filtros seleccionados.")
    else:
        meses = sorted(base["Mes"].unique())
        mes_act = meses[-1]
        mes_ant = meses[-2] if len(meses) >= 2 else None

        total_act = base.loc[base["Mes"] == mes_act, "Importe_CC"].sum()
        total_ant = base.loc[base["Mes"] == mes_ant, "Importe_CC"].sum() if mes_ant else np.nan
        var = total_act - total_ant if mes_ant else np.nan
        var_pct = var / abs(total_ant) if mes_ant and total_ant != 0 else np.nan

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Sector", centro)
        k2.metric(f"Costo {mes_act}", fmt_money(total_act))
        k3.metric("Variación", fmt_money(var), fmt_pct(var_pct))
        k4.metric("Semáforo", semaforo_variacion(var))

        evo = base.groupby(["Mes", "Grupo_PNL"], as_index=False)["Importe_CC"].sum()
        evo["Etiqueta"] = evo["Importe_CC"].apply(fmt_money_short)

        fig = px.line(
            evo,
            x="Mes",
            y="Importe_CC",
            color="Grupo_PNL",
            markers=True,
            text="Etiqueta",
            title=f"Evolución mensual de costos - {centro}"
        )
        fig.update_traces(textposition="top center")
        fig.update_yaxes(rangemode="tozero")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Apertura por concepto")
        piv = tabla_variaciones(base, ["Grupo_PNL", "Concepto_PNL"])

        mostrar = piv.copy()
        for col in ["Mes anterior", "Mes actual", "Variación $"]:
            mostrar[col] = mostrar[col].apply(fmt_money)
        mostrar["Variación %"] = mostrar["Variación %"].apply(fmt_pct)

        st.dataframe(
            mostrar[[
                "Grupo_PNL", "Concepto_PNL", "Mes anterior", "Mes actual",
                "Variación $", "Variación %", "Semáforo",
                "Severidad", "Motivo severidad", "Tipo evento"
            ]],
            use_container_width=True,
            height=430
        )

        st.markdown("### Principales variaciones")
        top = piv.dropna(subset=["Variación $"]).head(12).copy()
        top["Etiqueta"] = top["Variación $"].apply(fmt_money_short)

        if not top.empty:
            fig2 = px.bar(
                top,
                x="Variación $",
                y="Concepto_PNL",
                color="Semáforo",
                text="Etiqueta",
                orientation="h",
                title="Top variaciones vs mes anterior"
            )
            preparar_para_labels(fig2)
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### Insight ejecutivo")
        aumentos = piv[piv["Variación $"] > 0].sort_values("Variación $", ascending=False)
        bajas = piv[piv["Variación $"] < 0].sort_values("Variación $", ascending=True)

        texto = []
        if not pd.isna(var):
            if var > 0:
                texto.append(f"🔴 Los costos aumentaron **{fmt_money(var)}** vs el mes anterior (**{fmt_pct(var_pct)}**).")
            elif var < 0:
                texto.append(f"🟢 Los costos bajaron **{fmt_money(abs(var))}** vs el mes anterior (**{fmt_pct(var_pct)}**).")
            else:
                texto.append("🟡 No hubo variación relevante vs el mes anterior.")

        if not aumentos.empty:
            a = aumentos.iloc[0]
            texto.append(
                f"Principal presión: **{a['Concepto_PNL']}**, con suba de **{fmt_money(a['Variación $'])}**. "
                f"Motivo de severidad: {a['Motivo severidad']}."
            )

        if not bajas.empty:
            b = bajas.iloc[0]
            texto.append(
                f"Principal mejora: **{b['Concepto_PNL']}**, con baja de **{fmt_money(abs(b['Variación $']))}**. "
                f"Conviene validar si la baja es sostenible o si corresponde a un diferimiento de facturación."
            )

        st.info(" ".join(texto))

        st.markdown("### Movimientos que explican el desvío")
        opciones = top["Concepto_PNL"].tolist() if not top.empty else sorted(base["Concepto_PNL"].unique())
        concepto = st.selectbox("Concepto para revisar", opciones)

        movs = base[base["Concepto_PNL"] == concepto].copy()
        movs["Impacto_abs"] = movs["Importe_CC"].abs()
        movs = movs.sort_values(["Mes", "Impacto_abs"], ascending=[False, False])
        movs["Importe"] = movs["Importe_CC"].apply(fmt_money)

        cols = [
            "Mes", "Fecha", "Sucursal", "Proveedor_detectado", "Factura_detectada",
            "Nombre cuenta", "Nombre del rubro", "Detalle", "des res", "Detalle 2", "Importe"
        ]
        cols = [c for c in cols if c in movs.columns]
        st.dataframe(movs[cols].head(100), use_container_width=True, height=520)


# =========================
# TAB 2 ALERTAS & INSIGHTS
# =========================

with tab2:
    st.subheader("🚨 Alertas automáticas & motor de insights")

    centros_alerta = [c for c in CENTROS_POSVENTA if f"{c}_Gestion" in df_filtrado.columns]
    centro_a = st.selectbox("Centro de costo", centros_alerta + ["Todos Posventa"], index=0, key="centro_alertas")

    grupos_alerta = st.multiselect(
        "Categorías",
        ["Costos Controlables", "Costos No Controlables"],
        default=["Costos Controlables", "Costos No Controlables"],
        key="grupos_alertas"
    )

    meses_alerta = meses_all[-4:]

    if centro_a == "Todos Posventa":
        base_a = df_filtrado[
            (df_filtrado["Grupo_PNL"].isin(grupos_alerta)) &
            (df_filtrado["Mes"].isin(meses_alerta))
        ].copy()
        base_a["Importe_CC"] = sum(base_a[f"{c}_Gestion"] for c in centros_alerta)
    else:
        base_a = preparar_costos(df_filtrado, centro_a, grupos_alerta, meses_alerta)

    if base_a.empty:
        st.info("No hay datos suficientes para alertas.")
    else:
        piv = tabla_variaciones(base_a, ["Grupo_PNL", "Concepto_PNL"])
        alertas = piv[piv["Severidad"].isin(["🔴 Crítico", "🟠 Alto"])].copy()

        k1, k2, k3 = st.columns(3)
        k1.metric("Alertas críticas/altas", len(alertas))
        k2.metric("Mayor aumento", fmt_money(piv["Variación $"].max() if not piv.empty else 0))
        k3.metric("Mayor mejora", fmt_money(piv["Variación $"].min() if not piv.empty else 0))

        st.markdown("### Alertas priorizadas")
        if alertas.empty:
            st.success("No se detectan alertas críticas o altas.")
        else:
            mostrar = alertas.copy()
            for col in ["Mes anterior", "Mes actual", "Variación $"]:
                mostrar[col] = mostrar[col].apply(fmt_money)
            mostrar["Variación %"] = mostrar["Variación %"].apply(fmt_pct)

            st.dataframe(
                mostrar[[
                    "Severidad", "Motivo severidad", "Tipo evento", "Grupo_PNL", "Concepto_PNL",
                    "Mes anterior", "Mes actual", "Variación $", "Variación %", "Semáforo"
                ]],
                use_container_width=True,
                height=360
            )

        st.markdown("### Insights automáticos enriquecidos")

        insights = []

        aumentos = piv[piv["Variación $"] > 0].sort_values("Variación $", ascending=False).head(3)
        mejoras = piv[piv["Variación $"] < 0].sort_values("Variación $", ascending=True).head(3)

        for _, r in aumentos.iterrows():
            prov_concepto = base_a[base_a["Concepto_PNL"] == r["Concepto_PNL"]].copy()
            top_prov = (
                prov_concepto.groupby("Proveedor_detectado", as_index=False)["Importe_CC"]
                .sum()
                .sort_values("Importe_CC", ascending=False)
                .head(1)
            )

            proveedor_txt = ""
            if not top_prov.empty:
                proveedor_txt = f" El proveedor con mayor participación es **{top_prov.iloc[0]['Proveedor_detectado']}** con **{fmt_money(top_prov.iloc[0]['Importe_CC'])}**."

            insights.append(
                f"🔴 **{r['Concepto_PNL']}** aumenta **{fmt_money(r['Variación $'])}**. "
                f"No es solo un cambio porcentual: el impacto absoluto lo convierte en **{r['Severidad']}**. "
                f"**Hipótesis:** puede tratarse de gasto extraordinario, ajuste de contrato o concentración puntual de facturación."
                f"{proveedor_txt} **Acción sugerida:** revisar movimientos, proveedor principal y recurrencia del gasto."
            )

        for _, r in mejoras.iterrows():
            insights.append(
                f"🟢 **{r['Concepto_PNL']}** mejora **{fmt_money(abs(r['Variación $']))}**. "
                f"**Lectura:** la baja puede ser eficiencia real, diferimiento de facturación o cambio temporal. "
                f"**Acción sugerida:** validar si la mejora es sostenible antes de tomarla como ahorro estructural."
            )

        prov = base_a.groupby(["Proveedor_detectado", "Mes"], as_index=False)["Importe_CC"].sum()
        if not prov.empty:
            pv = prov.pivot_table(index="Proveedor_detectado", columns="Mes", values="Importe_CC", fill_value=0).reset_index()
            meses = sorted([c for c in pv.columns if c != "Proveedor_detectado"])
            if len(meses) >= 2:
                pv["Variación"] = pv[meses[-1]] - pv[meses[-2]]
                pv = pv.sort_values("Variación", ascending=False)
                if not pv.empty and pv.iloc[0]["Variación"] > 0:
                    insights.append(
                        f"🏭 **Proveedor con mayor presión:** **{pv.iloc[0]['Proveedor_detectado']}**, "
                        f"sube **{fmt_money(pv.iloc[0]['Variación'])}**. "
                        f"**Riesgo:** concentración de gasto o aparición de facturación no recurrente. "
                        f"**Acción sugerida:** revisar si corresponde a contrato recurrente, gasto extraordinario o reclasificación."
                    )

        if insights:
            for i in insights:
                st.info(i)
        else:
            st.success("No se detectan insights relevantes con los filtros actuales.")


# =========================
# TAB 3 PROVEEDORES
# =========================

with tab3:
    st.subheader("🏭 Análisis de proveedores")

    p1, p2, p3 = st.columns(3)

    with p1:
        centro_p = st.selectbox(
            "Centro de costo",
            [c for c in CENTROS_POSVENTA + CENTROS_COSTO if f"{c}_Gestion" in df_filtrado.columns],
            key="centro_prov"
        )

    with p2:
        grupos_p = st.multiselect(
            "Categoría",
            ["Costos Controlables", "Costos No Controlables"],
            default=["Costos Controlables", "Costos No Controlables"],
            key="grupo_prov"
        )

    with p3:
        meses_p = st.multiselect("Meses", meses_all, default=meses_all[-4:], key="meses_prov")

    base_p = preparar_costos(df_filtrado, centro_p, grupos_p, meses_p)

    if base_p.empty:
        st.info("No hay datos para proveedores.")
    else:
        prov_mes = base_p.groupby(
            ["Mes", "Proveedor_detectado", "Categoria_proveedor"],
            as_index=False
        )["Importe_CC"].sum()

        ranking_total = prov_mes.groupby(
            ["Proveedor_detectado", "Categoria_proveedor"],
            as_index=False
        )["Importe_CC"].sum().sort_values("Importe_CC", ascending=False)

        top_proveedores = ranking_total.head(15)["Proveedor_detectado"].tolist()
        stacked = prov_mes[prov_mes["Proveedor_detectado"].isin(top_proveedores)].copy()
        stacked["Etiqueta"] = stacked.apply(lambda r: f"{r['Mes']}: {fmt_money_short(r['Importe_CC'])}", axis=1)

        st.markdown("### Top proveedores por costo — apertura mensual")
        fig = px.bar(
            stacked,
            x="Proveedor_detectado",
            y="Importe_CC",
            color="Mes",
            text="Etiqueta",
            title="Top proveedores por gasto, dividido por mes"
        )
        fig.update_layout(xaxis_tickangle=-45)
        fig.update_traces(textposition="inside", insidetextanchor="middle")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Tabla mensual por proveedor")

        tabla_prov = prov_mes.pivot_table(
            index=["Proveedor_detectado", "Categoria_proveedor"],
            columns="Mes",
            values="Importe_CC",
            aggfunc="sum",
            fill_value=0
        ).reset_index()

        meses_cols = sorted([c for c in tabla_prov.columns if c not in ["Proveedor_detectado", "Categoria_proveedor"]])
        tabla_prov["Total"] = tabla_prov[meses_cols].sum(axis=1)
        tabla_prov["Promedio mensual"] = tabla_prov[meses_cols].mean(axis=1)
        tabla_prov["Mes pico"] = tabla_prov[meses_cols].idxmax(axis=1)
        tabla_prov["Importe mes pico"] = tabla_prov[meses_cols].max(axis=1)
        tabla_prov["% concentración pico"] = np.where(
            tabla_prov["Total"].abs() > 0,
            tabla_prov["Importe mes pico"] / tabla_prov["Total"].abs(),
            0
        )

        tabla_prov = tabla_prov.sort_values("Total", ascending=False)

        tabla_mostrar = tabla_prov.copy()
        for m in meses_cols:
            tabla_mostrar[m] = tabla_mostrar[m].apply(fmt_money)
        tabla_mostrar["Total"] = tabla_mostrar["Total"].apply(fmt_money)
        tabla_mostrar["Promedio mensual"] = tabla_mostrar["Promedio mensual"].apply(fmt_money)
        tabla_mostrar["Importe mes pico"] = tabla_mostrar["Importe mes pico"].apply(fmt_money)
        tabla_mostrar["% concentración pico"] = tabla_mostrar["% concentración pico"].apply(fmt_pct)

        st.dataframe(
            tabla_mostrar[
                ["Proveedor_detectado", "Categoria_proveedor"] +
                meses_cols +
                ["Total", "Promedio mensual", "Mes pico", "Importe mes pico", "% concentración pico"]
            ].head(50),
            use_container_width=True,
            height=430
        )

        st.markdown("### Proveedores que más crecieron")
        pivp = tabla_variaciones(base_p, ["Proveedor_detectado", "Categoria_proveedor"])
        crec = pivp.dropna(subset=["Variación $"]).sort_values("Variación $", ascending=False).head(30)
        crec_m = crec.copy()

        for col in ["Mes anterior", "Mes actual", "Variación $"]:
            crec_m[col] = crec_m[col].apply(fmt_money)
        crec_m["Variación %"] = crec_m["Variación %"].apply(fmt_pct)

        st.dataframe(
            crec_m[[
                "Proveedor_detectado", "Categoria_proveedor", "Mes anterior", "Mes actual",
                "Variación $", "Variación %", "Severidad", "Motivo severidad", "Tipo evento"
            ]],
            use_container_width=True,
            height=420
        )

        st.markdown("### Evolución acumulada Top 10 proveedores")

        top10 = ranking_total["Proveedor_detectado"].head(10).tolist()
        evo = prov_mes[prov_mes["Proveedor_detectado"].isin(top10)].copy()
        evo = evo.sort_values(["Proveedor_detectado", "Mes"])
        evo["Acumulado"] = evo.groupby("Proveedor_detectado")["Importe_CC"].cumsum()
        evo["Etiqueta"] = evo["Acumulado"].apply(fmt_money_short)

        fig2 = px.line(
            evo,
            x="Mes",
            y="Acumulado",
            color="Proveedor_detectado",
            markers=True,
            text="Etiqueta",
            title="Evolución acumulada por proveedor"
        )
        fig2.update_traces(textposition="top center")
        fig2.update_yaxes(rangemode="tozero")
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### Movimientos por proveedor")

        if "busqueda_proveedor" not in st.session_state:
            st.session_state["busqueda_proveedor"] = ""

        col_busq1, col_busq2 = st.columns([4, 1])
        with col_busq1:
            busqueda = st.text_input("Buscar proveedor", key="busqueda_proveedor")
        with col_busq2:
            if st.button("Limpiar búsqueda"):
                st.session_state["busqueda_proveedor"] = ""
                st.rerun()

        proveedores_lista = sorted(base_p["Proveedor_detectado"].dropna().unique())
        if busqueda:
            proveedores_filtrados = [p for p in proveedores_lista if busqueda.upper() in p.upper()]
        else:
            proveedores_filtrados = proveedores_lista

        if proveedores_filtrados:
            proveedor_sel = st.selectbox("Proveedor", proveedores_filtrados)
            movp = base_p[base_p["Proveedor_detectado"] == proveedor_sel].copy()
            movp["Impacto_abs"] = movp["Importe_CC"].abs()
            movp = movp.sort_values("Impacto_abs", ascending=False)
            movp["Importe"] = movp["Importe_CC"].apply(fmt_money)

            cols = [
                "Mes", "Fecha", "Sucursal", "Factura_detectada", "Proveedor_detectado",
                "Categoria_proveedor", "Nombre del rubro", "Concepto_PNL",
                "Detalle", "des res", "Detalle 2", "Importe"
            ]
            cols = [c for c in cols if c in movp.columns]
            st.dataframe(movp[cols].head(150), use_container_width=True, height=520)
        else:
            st.info("No hay proveedores que coincidan con la búsqueda.")


# =========================
# TAB 4 BENCHMARK
# =========================

with tab4:
    st.subheader("🏢 Benchmark de costos entre sucursales")

    centro_b = st.selectbox(
        "Centro de costo",
        [c for c in CENTROS_POSVENTA + CENTROS_COSTO if f"{c}_Gestion" in df_filtrado.columns],
        key="centro_bench"
    )

    grupos_b = st.multiselect(
        "Categoría",
        ["Costos Controlables", "Costos No Controlables"],
        default=["Costos Controlables"],
        key="grupo_bench"
    )

    meses_b = st.multiselect("Meses", meses_all, default=meses_all[-4:], key="mes_bench")

    base_b = preparar_costos(df_filtrado, centro_b, grupos_b, meses_b)

    if base_b.empty:
        st.info("No hay datos para benchmark.")
    else:
        bench = base_b.groupby(["Sucursal", "Grupo_PNL", "Concepto_PNL"], as_index=False)["Importe_CC"].sum()
        total_suc = base_b.groupby("Sucursal", as_index=False)["Importe_CC"].sum().rename(columns={"Importe_CC": "Costo total"})
        total_suc = total_suc.sort_values("Costo total", ascending=False)
        total_suc["Etiqueta"] = total_suc["Costo total"].apply(fmt_money_short)
        total_suc["Costo total fmt"] = total_suc["Costo total"].apply(fmt_money)

        fig = px.bar(
            total_suc,
            x="Sucursal",
            y="Costo total",
            text="Etiqueta",
            title=f"Costo total por sucursal - {centro_b}"
        )
        preparar_para_labels(fig)
        st.plotly_chart(fig, use_container_width=True)

        tabla_suc = total_suc[["Sucursal", "Costo total fmt"]].rename(columns={"Costo total fmt": "Costo total"})
        st.dataframe(tabla_suc, use_container_width=True)

        st.markdown("### Heatmap por concepto y sucursal")
        heat_num = bench.pivot_table(
            index="Concepto_PNL",
            columns="Sucursal",
            values="Importe_CC",
            aggfunc="sum",
            fill_value=0
        )

        st.dataframe(styled_heatmap_percent(heat_num), use_container_width=True, height=520)

        st.markdown("### Insight benchmark")

        if not total_suc.empty:
            mayor = total_suc.iloc[0]
            menor = total_suc.iloc[-1]
            total_general = total_suc["Costo total"].sum()
            part_mayor = mayor["Costo total"] / total_general if total_general else 0

            concepto_mayor_suc = (
                base_b[base_b["Sucursal"] == mayor["Sucursal"]]
                .groupby("Concepto_PNL", as_index=False)["Importe_CC"]
                .sum()
                .sort_values("Importe_CC", ascending=False)
                .head(3)
            )

            conceptos_txt = ", ".join([
                f"{r['Concepto_PNL']} ({fmt_money(r['Importe_CC'])})"
                for _, r in concepto_mayor_suc.iterrows()
            ])

            st.info(
                f"🧠 **{mayor['Sucursal']}** concentra **{fmt_pct(part_mayor)}** del costo total analizado "
                f"en **{centro_b}**, con **{fmt_money(mayor['Costo total'])}**. "
                f"La sucursal de menor impacto es **{menor['Sucursal']}** con **{fmt_money(menor['Costo total'])}**. "
                f"Los conceptos que más explican la concentración en la sucursal líder son: **{conceptos_txt}**. "
                f"✅ Recomendación: revisar si la diferencia se justifica por escala operativa o si existen contratos, consumos o imputaciones particulares que deban corregirse."
            )


# =========================
# TAB 5 P&L
# =========================

with tab5:
    st.subheader("📑 P&L mensual interactivo")

    meses_pnl = st.multiselect("Meses a mostrar", meses_all, default=meses_all[-4:])

    if not meses_pnl:
        st.warning("Seleccioná al menos un mes.")
    else:
        pnl = construir_pnl_mensual(df_filtrado, meses_pnl)

        resumen_grupo = pnl.groupby("Grupo", as_index=False)[meses_pnl + ["Acumulado"]].sum()

        mostrar_resumen = resumen_grupo.copy()
        for col in meses_pnl + ["Acumulado"]:
            mostrar_resumen[col] = mostrar_resumen[col].apply(fmt_money)

        st.markdown("### Resumen por grupo")
        st.dataframe(mostrar_resumen, use_container_width=True)

        st.markdown("### Detalle expandible por grupo")

        for grupo in pnl["Grupo"].drop_duplicates():
            df_g = pnl[pnl["Grupo"] == grupo].copy()

            total_grupo = df_g[df_g["Lógica"] != "igual"]["Acumulado"].sum()
            with st.expander(f"➕ {grupo} | Acumulado {fmt_money(total_grupo)}", expanded=False):
                mostrar_g = df_g[["Lógica", "Concepto", "Rubros"] + meses_pnl + ["Acumulado"]].copy()
                for col in meses_pnl + ["Acumulado"]:
                    mostrar_g[col] = mostrar_g[col].apply(fmt_money)
                st.dataframe(mostrar_g, use_container_width=True, height=350)


# =========================
# TAB 6 SIGNOS
# =========================

with tab6:
    st.subheader("🧾 Control de signos")

    control = df_filtrado.groupby(["Nombre del rubro", "Signo_rubro"], as_index=False).agg(
        Parcial_original=("Parcial", "sum"),
        Parcial_gestion=("Parcial_Gestion", "sum")
    )

    control["Parcial original"] = control["Parcial_original"].apply(fmt_money)
    control["Parcial gestión"] = control["Parcial_gestion"].apply(fmt_money)

    st.dataframe(
        control[["Nombre del rubro", "Signo_rubro", "Parcial original", "Parcial gestión"]],
        use_container_width=True,
        height=650
    )


# =========================
# TAB 7 DRILLDOWN
# =========================

with tab7:
    st.subheader("🔎 Drilldown contable")

    buscar = st.text_input("Buscar por cuenta, proveedor, factura, detalle, descripción o rubro")

    drill = df_filtrado.copy()

    if buscar:
        t = buscar.lower()
        mask = pd.Series(False, index=drill.index)
        for col in [
            "Nombre cuenta", "Detalle", "des res", "Detalle 2",
            "Nombre del rubro", "Proveedor_detectado", "Factura_detectada"
        ]:
            if col in drill.columns:
                mask = mask | drill[col].astype(str).str.lower().str.contains(t, na=False)
        drill = drill[mask]

    total_sel = drill["Parcial_Gestion"].sum()
    cant_movs = len(drill)

    rubro_principal = "Sin datos"
    proveedor_principal = "Sin datos"
    sucursal_principal = "Sin datos"

    if not drill.empty:
        rubro_principal = (
            drill.groupby("Nombre del rubro")["Parcial_Gestion"]
            .sum().abs().sort_values(ascending=False).index[0]
        )
        proveedor_principal = (
            drill.groupby("Proveedor_detectado")["Parcial_Gestion"]
            .sum().abs().sort_values(ascending=False).index[0]
        )
        sucursal_principal = (
            drill.groupby("Sucursal")["Parcial_Gestion"]
            .sum().abs().sort_values(ascending=False).index[0]
        )

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total selección filtrada", fmt_money(total_sel))
    k2.metric("Cantidad movimientos", f"{cant_movs}")
    k3.metric("Proveedor principal", proveedor_principal)
    k4.metric("Rubro principal", rubro_principal)

    st.caption(f"Sucursal con mayor impacto en la búsqueda: {sucursal_principal}")

    drill_mostrar = drill.copy()
    drill_mostrar["Parcial"] = drill_mostrar["Parcial"].apply(fmt_money)
    drill_mostrar["Parcial gestión"] = drill_mostrar["Parcial_Gestion"].apply(fmt_money)

    cols = [
        "Fecha", "Mes", "Sucursal", "Cuenta:", "Nombre cuenta", "Rubro_calc", "Nombre del rubro",
        "Grupo_PNL", "Concepto_PNL", "Proveedor_detectado", "Factura_detectada", "Categoria_proveedor",
        "Detalle", "des res", "Detalle 2", "Parcial", "Parcial gestión"
    ]
    cols = [c for c in cols if c in drill_mostrar.columns]

    st.dataframe(drill_mostrar[cols], use_container_width=True, height=650)

    st.download_button(
        "⬇️ Descargar drilldown filtrado",
        data=drill.to_csv(index=False).encode("utf-8-sig"),
        file_name="drilldown_mayores_lux.csv",
        mime="text/csv"
    )


# =========================
# TAB 8 DICCIONARIO
# =========================

with tab8:
    st.subheader("⚙️ Diccionario y reglas del modelo")

    st.markdown("""
### 1. Lógica principal

- Cada fila del mayor es un movimiento contable individual.
- `Parcial_Gestion` normaliza signos para lectura gerencial.
- Para análisis de costos:
  - Variación positiva = aumentó el costo.
  - Variación negativa = bajó el costo.
- Los centros de costo usados son las columnas monetarias:
  - Repuestos
  - Tl. Mec.
  - Mayorista
  - ChapyPintu
  - y demás centros disponibles.

### 2. Severidad

La severidad combina tres elementos:

| Factor | Criterio |
|---|---|
| Impacto absoluto | Cuánto dinero cambió contra el mes anterior |
| Variación porcentual | Qué tan grande fue el salto relativo |
| Importe actual | Qué peso tiene el gasto actual |

Clasificación:

| Nivel | Interpretación |
|---|---|
| 🔴 Crítico | Alto impacto económico y/o variación muy fuerte |
| 🟠 Alto | Desvío relevante que requiere revisión |
| 🟡 Medio | Cambio visible pero no necesariamente crítico |
| 🟢 Bajo | Cambio menor o de bajo impacto |

### 3. Motivo severidad

La columna **Motivo severidad** explica por qué el sistema clasificó una línea como crítica, alta, media o baja.

Ejemplos:
- variación mayor a $5M
- variación superior al 100%
- importe actual mayor a $1M
- sin gasto en mes anterior

### 4. Proveedores

El proveedor se detecta automáticamente desde:
- Detalle
- des res
- Detalle 2

La detección es aproximada. El sistema además normaliza variantes frecuentes, por ejemplo:
- ROQUE JUAN LOZANO ALQ LOC
- ROQUE JUAN LOZANO ALQ LOCAL
- ROQUE JUAN LOZANO MAYOR VALOR

se agrupan como:

**ROQUE JUAN LOZANO**

### 5. Heatmap sucursales

En el benchmark, cada celda muestra:

`$ importe (% participación dentro del concepto)`

El color indica concentración:
- rojo: mayor concentración
- naranja: concentración relevante
- amarillo: concentración media
- verde: baja concentración
- gris: sin impacto

### 6. Recomendación de uso

1. Revisar primero **Alertas & Insights**.
2. Abrir el desvío en **Control de Costos**.
3. Validar proveedores en **Proveedores**.
4. Comparar sucursales en **Benchmark**.
5. Bajar al detalle en **Drilldown**.
""")
