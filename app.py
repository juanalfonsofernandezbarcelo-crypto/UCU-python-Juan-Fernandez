import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ─────────────────────────────────────────
# Configuración de la página
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Análisis Bancario",
    page_icon="🏦",
    layout="wide",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
    h1, h2, h3 { font-family: 'IBM Plex Mono', monospace; letter-spacing: -0.5px; }
    .tag {
        display: inline-block; background: #1d4ed8; color: white;
        border-radius: 4px; padding: 3px 12px; font-size: 13px;
        font-family: 'IBM Plex Mono', monospace; margin-bottom: 10px;
    }
    div[data-testid="metric-container"] {
        background: #f8fafc; border: 1px solid #e2e8f0;
        border-radius: 8px; padding: 12px 16px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# Carga de datos
# ─────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/bancario_procesado.csv")
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Fecha Registro en la App"] = pd.to_datetime(df["Fecha Registro en la App"], errors="coerce")
    return df

try:
    df_raw = load_data()
except FileNotFoundError:
    st.error(
        "⚠️ No se encontró `data/processed/bancario_procesado.csv`. "
        "Ejecutá primero el notebook `practice.ipynb` para generar el archivo procesado."
    )
    st.stop()

# ─────────────────────────────────────────
# Sidebar – Filtros
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏦 Panel de Control")
    st.markdown("---")
    st.markdown("### 🎛️ Filtros")

    monto_min = float(df_raw["Monto USD"].min())
    monto_max = float(df_raw["Monto USD"].max())
    st.markdown("**Rango de Monto USD**")
    rango_monto = st.slider(
        label="Monto USD",
        min_value=monto_min,
        max_value=monto_max,
        value=(monto_min, monto_max),
        step=100.0,
        label_visibility="collapsed",
    )

    st.markdown("---")

    productos = ["Todos"] + sorted(df_raw["Producto"].dropna().unique().tolist())
    filtro_producto = st.selectbox("Producto:", productos)

    estados_mora = ["Todos"] + sorted(df_raw["estado_mora"].dropna().unique().tolist())
    filtro_mora = st.selectbox("Estado de mora:", estados_mora)

    sucursales = ["Todos"] + sorted(df_raw["Sucursal"].dropna().unique().tolist())
    filtro_sucursal = st.selectbox("Sucursal:", sucursales)

    estados_app = ["Todos"] + sorted(df_raw["Estado App"].dropna().unique().tolist())
    filtro_app = st.selectbox("Estado App:", estados_app)

    st.markdown("---")
    st.markdown("<small>Proyecto Final · P4DA · 2025</small>", unsafe_allow_html=True)

# ─────────────────────────────────────────
# Aplicar filtros
# ─────────────────────────────────────────
df = df_raw.copy()
df = df[(df["Monto USD"] >= rango_monto[0]) & (df["Monto USD"] <= rango_monto[1])]
if filtro_producto != "Todos":
    df = df[df["Producto"] == filtro_producto]
if filtro_mora != "Todos":
    df = df[df["estado_mora"] == filtro_mora]
if filtro_sucursal != "Todos":
    df = df[df["Sucursal"] == filtro_sucursal]
if filtro_app != "Todos":
    df = df[df["Estado App"] == filtro_app]

# ─────────────────────────────────────────
# Encabezado
# ─────────────────────────────────────────
st.markdown('<span class="tag">DATASET BANCARIO</span>', unsafe_allow_html=True)
st.title("🏦 Análisis de Productos Bancarios")
st.markdown("Exploración interactiva de clientes, productos, montos y estado de mora.")
st.markdown(f"**{len(df):,} registros** seleccionados de **{len(df_raw):,}** totales.")
st.markdown("---")

# ─────────────────────────────────────────
# Métricas principales
# ─────────────────────────────────────────
montos_validos = df[df["Monto USD"] > 0]["Monto USD"]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Media Monto USD", f"${montos_validos.mean():,.0f}" if len(montos_validos) > 0 else "—")
c2.metric("Mediana Monto USD", f"${montos_validos.median():,.0f}" if len(montos_validos) > 0 else "—")
c3.metric("Desv. Estándar", f"${montos_validos.std():,.0f}" if len(montos_validos) > 0 else "—")
c4.metric("Rango (Máx - Mín)", f"${montos_validos.max() - montos_validos.min():,.0f}" if len(montos_validos) > 0 else "—")
c5.metric("% en Mora", f"{(df['estado_mora'].isin(['En Mora','Incobrable']).mean()*100):.1f}%" if len(df) > 0 else "—")

st.markdown("---")

# ─────────────────────────────────────────
# Estadísticas descriptivas
# ─────────────────────────────────────────
with st.expander("📋 Estadísticas descriptivas completas"):
    cols_excluir = ["Número ID", "Tiene_mora"]
    num_cols = [c for c in df.select_dtypes(include="number").columns.tolist() if c not in cols_excluir]
    stats = df[num_cols].describe().T
    stats["Rango"] = stats["max"] - stats["min"]
    stats.rename(columns={
        "mean": "Media", "50%": "Mediana", "std": "Desv. Est.",
        "25%": "Q1", "75%": "Q3", "min": "Mín", "max": "Máx", "count": "N"
    }, inplace=True)
    stats["N"] = len(df)
    cols_show = [c for c in ["N", "Media", "Mediana", "Desv. Est.", "Q1", "Q3", "Mín", "Máx", "Rango"] if c in stats.columns]
    st.dataframe(stats[cols_show].style.format("{:.2f}"), use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────
# Visualizaciones – Fila 1
# ─────────────────────────────────────────
st.subheader("📈 Distribución y relaciones")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Distribución de Monto USD**")
    fig_hist = px.histogram(
        df[df["Monto USD"] > 0],
        x="Monto USD",
        nbins=35,
        color_discrete_sequence=["#1d4ed8"],
        template="plotly_white",
        labels={"Monto USD": "Monto (USD)"},
    )
    fig_hist.update_layout(bargap=0.05, xaxis_title="Monto USD", yaxis_title="Frecuencia", margin=dict(t=20, b=40))
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    st.markdown("**Monto USD vs Días hasta registro en App**")
    scatter_df = df[df["Monto USD"] > 0].dropna(subset=["Dias_hasta_app"])
    fig_scatter = px.scatter(
        scatter_df,
        x="Monto USD",
        y="Dias_hasta_app",
        color="estado_mora",
        symbol="Producto",
        labels={"Monto USD": "Monto (USD)", "Dias_hasta_app": "Días hasta registro en App", "estado_mora": "Estado de Mora"},
        template="plotly_white",
        opacity=0.7,
        color_discrete_map={"Cobrado": "#22c55e", "En Mora": "#f59e0b", "Incobrable": "#ef4444"},
    )
    fig_scatter.update_layout(margin=dict(t=20, b=40))
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────
# Visualizaciones – Fila 2
# ─────────────────────────────────────────
st.subheader("🔍 Análisis por categorías")

col3, col4 = st.columns(2)

with col3:
    mora_counts = df["estado_mora"].value_counts().reset_index()
    mora_counts.columns = ["Estado", "Cantidad"]
    fig_mora = px.bar(
        mora_counts, x="Estado", y="Cantidad", color="Estado", template="plotly_white",
        title="Clientes por estado de mora",
        color_discrete_map={"Cobrado": "#22c55e", "En Mora": "#f59e0b", "Incobrable": "#ef4444"},
    )
    fig_mora.update_layout(showlegend=False, margin=dict(t=40, b=40))
    st.plotly_chart(fig_mora, use_container_width=True)

with col4:
    avg_monto = (
        df[df["Monto USD"] > 0].groupby("Producto")["Monto USD"].mean().sort_values().reset_index()
    )
    fig_prod = px.bar(
        avg_monto, x="Monto USD", y="Producto", orientation="h",
        template="plotly_white", title="Monto USD promedio por producto",
        color_discrete_sequence=["#1d4ed8"],
        labels={"Monto USD": "Monto promedio (USD)"},
    )
    fig_prod.update_layout(margin=dict(t=40, b=40))
    st.plotly_chart(fig_prod, use_container_width=True)

col5, col6 = st.columns(2)

with col5:
    suc = df["Sucursal"].value_counts().head(12).reset_index()
    suc.columns = ["Sucursal", "Clientes"]
    fig_suc = px.bar(
        suc, x="Clientes", y="Sucursal", orientation="h",
        template="plotly_white", title="Clientes por sucursal (top 12)",
        color_discrete_sequence=["#0ea5e9"],
    )
    fig_suc.update_layout(margin=dict(t=40, b=40))
    st.plotly_chart(fig_suc, use_container_width=True)

with col6:
    mora_pct = (
        df.groupby("Producto")["estado_mora"]
        .apply(lambda x: (x.isin(["En Mora", "Incobrable"]).sum() / len(x) * 100))
        .sort_values(ascending=True)
        .reset_index()
    )
    mora_pct.columns = ["Producto", "% Mora"]
    fig_mpct = px.bar(
        mora_pct, x="% Mora", y="Producto", orientation="h",
        template="plotly_white", title="% de mora por producto",
        color_discrete_sequence=["#f59e0b"],
        labels={"% Mora": "% en mora o incobrable"},
    )
    fig_mpct.update_layout(margin=dict(t=40, b=40))
    st.plotly_chart(fig_mpct, use_container_width=True)

st.markdown("---")

with st.expander("🔎 Ver datos filtrados"):
    st.dataframe(df.reset_index(drop=True), use_container_width=True)
