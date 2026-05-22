"""
Dashboard Interactivo MFT Analytics con Streamlit
Visualiza métricas en tiempo real de los agentes colaborativos
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from datos_muestra import generar_datos_muestra
from agentes_mft import AgenteValidador, AgenteAnalizador
import queue


# Configuración de página
st.set_page_config(
    page_title="MFT Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .alert-warning {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .alert-success {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def cargar_datos():
    """Carga datos y ejecuta agentes una sola vez"""
    col_val = queue.Queue()
    col_ana = queue.Queue()

    validador = AgenteValidador(col_val, col_ana)
    analizador = AgenteAnalizador(col_ana)

    # Procesar datos
    datos = generar_datos_muestra(100)
    for trans in datos:
        resultado = validador.validar_transferencia(trans)
        analizador.procesar_transferencia(resultado)

    return validador, analizador


def main():
    validador, analizador = cargar_datos()

    # HEADER
    st.title("📊 MFT Analytics Dashboard")
    st.markdown("Sistema colaborativo de análisis de transferencias de archivos")

    # TABS
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Inicio",
        "👥 Clientes",
        "👤 Usuarios",
        "💰 Facturación",
        "⚙️ Housekeeping"
    ])

    # ============ TAB 1: INICIO ============
    with tab1:
        st.subheader("Resumen General")

        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Transferencias",
                len(analizador.transferencias_procesadas),
                "Total procesadas"
            )

        with col2:
            total_gb = sum(
                t.tamaño_bytes for t in analizador.transferencias_procesadas
            ) / 1024 / 1024 / 1024
            st.metric("Total Transferido", f"{total_gb:.2f} GB", "Histórico")

        with col3:
            st.metric(
                "Clientes Activos",
                len(analizador.estadisticas_clientes),
                "Con transferencias"
            )

        with col4:
            st.metric(
                "Usuarios Únicos",
                len(analizador.metricas_usuarios),
                "En el sistema"
            )

        # Gráfico de actividad
        st.subheader("Actividad por Día")

        # Agrupar por día
        df_trans = pd.DataFrame([
            {
                "fecha": t.hora_inicio.date(),
                "cliente": t.cliente_id,
                "gb": t.tamaño_bytes / 1024 / 1024 / 1024
            }
            for t in analizador.transferencias_procesadas
        ])

        if len(df_trans) > 0:
            df_diario = df_trans.groupby("fecha").agg({"gb": "sum"}).reset_index()
            fig = px.line(df_diario, x="fecha", y="gb", title="GB Transferidos por Día",
                         labels={"gb": "GB", "fecha": "Fecha"})
            st.plotly_chart(fig, use_container_width=True)

    # ============ TAB 2: CLIENTES ============
    with tab2:
        st.subheader("Análisis por Cliente")

        clientes_data = []
        for cliente_id, stats in analizador.estadisticas_clientes.items():
            gb_mes = analizador.obtener_uso_mensual(cliente_id)
            clientes_data.append({
                "Cliente": cliente_id,
                "Transferencias": stats.total_transferencias,
                "GB (30 días)": round(gb_mes, 2),
                "GB (Total)": round(stats.total_gb, 2),
                "Usuarios": len(stats.usuarios_unicos),
                "IPs": len(stats.ips_unicas),
                "Perfiles": len(stats.perfiles_usados)
            })

        df_clientes = pd.DataFrame(clientes_data).sort_values("GB (30 días)", ascending=False)

        # Mostrar tabla
        st.dataframe(df_clientes, use_container_width=True)

        # Gráfico comparativo
        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(
                df_clientes, x="Cliente", y="GB (30 días)",
                title="Uso Mensual por Cliente",
                labels={"GB (30 días)": "GB"}
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(
                df_clientes, x="Cliente", y="Usuarios",
                title="Usuarios por Cliente",
                labels={"Usuarios": "Cantidad"}
            )
            st.plotly_chart(fig, use_container_width=True)

    # ============ TAB 3: USUARIOS ============
    with tab3:
        st.subheader("Detalle de Usuarios")

        usuarios_data = []
        for key, met in analizador.metricas_usuarios.items():
            usuarios_data.append({
                "Usuario": met.usuario,
                "IP": met.ip,
                "Cliente": met.cliente_id,
                "Transferencias": met.transferencias,
                "GB": round(met.total_gb, 2),
                "Último uso": met.ultimo_uso.strftime("%Y-%m-%d %H:%M")
            })

        df_usuarios = pd.DataFrame(usuarios_data).sort_values("GB", ascending=False)

        # Filtro por cliente
        cliente_sel = st.selectbox("Filtrar por cliente", ["Todos"] + list(analizador.estadisticas_clientes.keys()))

        if cliente_sel != "Todos":
            df_usuarios = df_usuarios[df_usuarios["Cliente"] == cliente_sel]

        st.dataframe(df_usuarios, use_container_width=True)

        # Gráfico top usuarios
        st.subheader("Top 10 Usuarios por Volumen")
        fig = px.bar(
            df_usuarios.head(10), x="Usuario", y="GB",
            color="Cliente",
            title="10 Usuarios con Mayor Volumen",
            labels={"GB": "GB transferidos"}
        )
        st.plotly_chart(fig, use_container_width=True)

    # ============ TAB 4: FACTURACIÓN ============
    with tab4:
        st.subheader("Análisis de Facturación")

        reporte = analizador.obtener_reporte_facturacion()

        # Tabla de facturación
        fact_data = []
        for cliente, datos in reporte.items():
            fact_data.append({
                "Cliente": cliente,
                "GB/Mes": round(datos['gb_mes'], 2),
                "Transferencias/Mes": datos['transferencias_mes'],
                "Usuarios": datos['usuarios'],
                "IPs": datos['ips'],
                "Tarifa": datos['tarifa_actual']
            })

        df_fact = pd.DataFrame(fact_data).sort_values("GB/Mes", ascending=False)
        st.dataframe(df_fact, use_container_width=True)

        # Alertas de upgrade
        st.subheader("⚠️ Alertas de Tarificación")
        for _, row in df_fact.iterrows():
            if row['Tarifa'] != 'Estándar':
                st.markdown(
                    f"""
                    <div class='alert-warning'>
                    <b>{row['Cliente']}</b>: {row['GB/Mes']} GB/mes → <b>{row['Tarifa']}</b>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Proyección mensual
        st.subheader("Proyección de Costos")
        tarifas = {
            "Estándar": 100,  # Ejemplo: $100/mes
            "Premium": 300,
            "Enterprise": 1000
        }

        costo_total = sum(tarifas.get(row['Tarifa'], 0) for _, row in df_fact.iterrows())
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Costo Total Mensual", f"${costo_total:,.0f}")

        with col2:
            st.metric("Clientes Upgrade", len(df_fact[df_fact['Tarifa'] != 'Estándar']))

        with col3:
            st.metric("Clientes Estándar", len(df_fact[df_fact['Tarifa'] == 'Estándar']))

    # ============ TAB 5: HOUSEKEEPING ============
    with tab5:
        st.subheader("Housekeeping y Mantenimiento")

        # Selector de días de inactividad
        dias = st.slider("Usuarios sin actividad en (días):", 1, 90, 30)

        inactivos = analizador.detectar_usuarios_inactivos(dias_inactividad=dias)

        if inactivos:
            st.warning(f"⚠️ {len(inactivos)} usuarios sin actividad en {dias} días")

            # Tabla de inactivos
            inact_data = []
            for usuario in inactivos:
                inact_data.append({
                    "Usuario": usuario.usuario,
                    "IP": usuario.ip,
                    "Cliente": usuario.cliente_id,
                    "Días inactivo": usuario.dias_sin_uso,
                    "Último uso": usuario.ultimo_uso.strftime("%Y-%m-%d %H:%M"),
                    "Transferencias": usuario.transferencias
                })

            df_inact = pd.DataFrame(inact_data).sort_values("Días inactivo", ascending=False)
            st.dataframe(df_inact, use_container_width=True)

            # Recomendaciones
            st.subheader("📋 Recomendaciones")
            muy_inactivos = [u for u in inactivos if u.dias_sin_uso > 60]
            if muy_inactivos:
                st.markdown(
                    f"""
                    <div class='alert-warning'>
                    <b>Considerar desactivar:</b> {len(muy_inactivos)} usuarios sin actividad >60 días
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        else:
            st.success(f"✓ Todos los usuarios activos en últimos {dias} días")

        # Análisis de perfiles
        st.subheader("Análisis de Perfiles de Conexión")

        perfiles_uso = {}
        for trans in analizador.transferencias_procesadas:
            perfil = trans.id_conectividad
            if perfil not in perfiles_uso:
                perfiles_uso[perfil] = {"count": 0, "gb": 0}
            perfiles_uso[perfil]["count"] += 1
            perfiles_uso[perfil]["gb"] += trans.tamaño_bytes / 1024 / 1024 / 1024

        perfil_data = [
            {"Perfil": p, "Transferencias": v["count"], "GB": round(v["gb"], 2)}
            for p, v in perfiles_uso.items()
        ]

        df_perfiles = pd.DataFrame(perfil_data).sort_values("Transferencias", ascending=False)
        st.dataframe(df_perfiles, use_container_width=True)


if __name__ == "__main__":
    main()
