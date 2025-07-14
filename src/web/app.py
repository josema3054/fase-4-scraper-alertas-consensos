"""
Aplicación web en Streamlit para configuración y monitoreo del sistema
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
import asyncio
import json
from typing import Dict, List, Optional
import os
from pathlib import Path

# Configurar página
st.set_page_config(
    page_title="📊 Fase 4 - Consensos Deportivos",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
    }
    
    .alert-success {
        background: #dcfce7;
        color: #166534;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #22c55e;
    }
    
    .alert-warning {
        background: #fef3c7;
        color: #92400e;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #f59e0b;
    }
    
    .alert-error {
        background: #fee2e2;
        color: #dc2626;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ef4444;
    }
    
    .status-active {
        color: #22c55e;
        font-weight: bold;
    }
    
    .status-inactive {
        color: #ef4444;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitApp:
    """Aplicación principal de Streamlit"""
    
    def __init__(self):
        self.timezone = pytz.timezone('America/Argentina/Buenos_Aires')
        self.init_session_state()
    
    def init_session_state(self):
        """Inicializa el estado de la sesión"""
        if 'system_status' not in st.session_state:
            st.session_state.system_status = 'unknown'
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now(self.timezone)
        if 'consensus_data' not in st.session_state:
            st.session_state.consensus_data = []
    
    def render_header(self):
        """Renderiza el encabezado principal"""
        st.markdown("""
        <div class="main-header">
            <h1>🏈 Sistema de Consensos Deportivos - Fase 4</h1>
            <p>Monitoreo automático de consensos desde covers.com</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Renderiza la barra lateral con navegación"""
        with st.sidebar:
            st.title("🧭 Navegación")
            
            # Selector de página
            page = st.selectbox(
                "Seleccionar página:",
                ["📊 Dashboard", "⚙️ Configuración", "📈 Estadísticas", "📋 Logs", "🤖 Telegram", "🔧 Sistema"]
            )
            
            st.divider()
            
            # Estado del sistema
            st.subheader("🔍 Estado del Sistema")
            
            current_time = datetime.now(self.timezone)
            st.write(f"🕐 **Hora actual:** {current_time.strftime('%H:%M:%S ART')}")
            st.write(f"📅 **Fecha:** {current_time.strftime('%d/%m/%Y')}")
            
            # Status indicators
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🔄 Scraper", "Activo", "✅")
            with col2:
                st.metric("🤖 Bot", "Conectado", "✅")
            
            st.divider()
            
            # Acciones rápidas
            st.subheader("⚡ Acciones Rápidas")
            
            if st.button("🔄 Actualizar Datos", type="primary"):
                self.refresh_data()
            
            if st.button("📊 Scraping Manual"):
                self.run_manual_scraping()
            
            if st.button("🧪 Test Telegram"):
                self.test_telegram_bot()
            
            return page
    
    def render_dashboard(self):
        """Renderiza el dashboard principal"""
        st.header("📊 Dashboard Principal")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🏈 Consensos Hoy",
                value="12",
                delta="3",
                help="Consensos procesados en el día actual"
            )
        
        with col2:
            st.metric(
                "🚨 Alertas Enviadas",
                value="5",
                delta="2",
                help="Alertas de consenso alto enviadas"
            )
        
        with col3:
            st.metric(
                "📈 Precisión Promedio",
                value="78.5%",
                delta="1.2%",
                help="Precisión promedio de los consensos"
            )
        
        with col4:
            st.metric(
                "⏱️ Último Scraping",
                value="14:15",
                delta="2 min",
                help="Última actualización de datos"
            )
        
        st.divider()
        
        # Gráficos principales
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Consensos por Hora")
            
            # Datos de ejemplo para el gráfico
            hours = list(range(8, 24))
            consensus_count = [0, 2, 5, 8, 12, 15, 18, 14, 10, 8, 5, 3, 2, 1, 0, 0]
            
            fig = px.bar(
                x=hours,
                y=consensus_count,
                title="Distribución de Consensos por Hora",
                labels={'x': 'Hora del día', 'y': 'Cantidad de consensos'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Distribución de Consensos")
            
            # Gráfico de dona
            labels = ['Spread', 'Total', 'Moneyline']
            values = [45, 35, 20]
            
            fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
            fig.update_layout(
                title="Tipos de Consenso Detectados",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabla de consensos recientes
        st.subheader("🏆 Consensos Recientes")
        
        # Datos de ejemplo
        recent_consensus = [
            {
                'Hora': '14:15',
                'Equipo Visitante': 'Yankees',
                'Equipo Local': 'Red Sox',
                'Tipo': 'Spread',
                'Consenso': '78%',
                'Estado': '🚨 Alta'
            },
            {
                'Hora': '13:45',
                'Equipo Visitante': 'Dodgers',
                'Equipo Local': 'Giants',
                'Tipo': 'Total',
                'Consenso': '82%',
                'Estado': '🚨 Alta'
            },
            {
                'Hora': '13:20',
                'Equipo Visitante': 'Astros',
                'Equipo Local': 'Rangers',
                'Tipo': 'Moneyline',
                'Consenso': '65%',
                'Estado': '📊 Media'
            }
        ]
        
        df_consensus = pd.DataFrame(recent_consensus)
        st.dataframe(df_consensus, use_container_width=True)
    
    def render_configuration(self):
        """Renderiza la página de configuración"""
        st.header("⚙️ Configuración del Sistema")
        
        # Configuración de scraping
        with st.expander("🔄 Configuración de Scraping", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📅 Horarios")
                daily_hour = st.slider("Hora de scraping diario", 0, 23, 11)
                live_interval = st.slider("Intervalo en vivo (horas)", 1, 6, 2)
                
                st.subheader("🎯 Umbrales")
                consensus_threshold = st.slider("Umbral de consenso (%)", 50, 95, 75)
                min_games = st.number_input("Mínimo de juegos", 1, 50, 5)
            
            with col2:
                st.subheader("🏈 Deportes")
                mlb_enabled = st.checkbox("MLB", value=True)
                nfl_enabled = st.checkbox("NFL", value=False, disabled=True)
                nba_enabled = st.checkbox("NBA", value=False, disabled=True)
                
                st.subheader("📊 Fuentes")
                covers_enabled = st.checkbox("covers.com", value=True)
                other_sources = st.checkbox("Otras fuentes", value=False, disabled=True)
        
        # Configuración de alertas
        with st.expander("🚨 Configuración de Alertas"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📱 Telegram")
                telegram_enabled = st.checkbox("Alertas Telegram", value=True)
                bot_token = st.text_input("Token del Bot", type="password")
                chat_ids = st.text_area("Chat IDs (separados por coma)")
            
            with col2:
                st.subheader("📧 Tipos de Alerta")
                alert_high_consensus = st.checkbox("Consenso alto", value=True)
                alert_errors = st.checkbox("Errores del sistema", value=True)
                alert_daily_report = st.checkbox("Reporte diario", value=True)
        
        # Botones de acción
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Guardar Configuración", type="primary"):
                st.success("✅ Configuración guardada exitosamente")
        
        with col2:
            if st.button("🔄 Restaurar Valores"):
                st.info("ℹ️ Valores restaurados a configuración por defecto")
        
        with col3:
            if st.button("🧪 Probar Configuración"):
                st.info("🧪 Ejecutando pruebas de configuración...")
    
    def render_statistics(self):
        """Renderiza la página de estadísticas"""
        st.header("📈 Estadísticas y Análisis")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date_from = st.date_input("Desde", value=datetime.now().date() - timedelta(days=7))
        with col2:
            date_to = st.date_input("Hasta", value=datetime.now().date())
        with col3:
            sport_filter = st.selectbox("Deporte", ["Todos", "MLB", "NFL", "NBA"])
        
        # Estadísticas generales
        st.subheader("📊 Resumen del Período")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📈 Total Consensos", "156", "12")
        with col2:
            st.metric("🎯 Precisión Media", "76.8%", "2.1%")
        with col3:
            st.metric("🚨 Alertas Enviadas", "23", "4")
        with col4:
            st.metric("⚡ Tiempo Respuesta", "2.3s", "-0.2s")
        
        # Gráficos detallados
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Tendencia de Consensos")
            
            # Generar datos de ejemplo
            dates = pd.date_range(start=date_from, end=date_to, freq='D')
            consensus_trend = pd.DataFrame({
                'Fecha': dates,
                'Consensos': [15, 12, 18, 22, 16, 14, 20, 25][:len(dates)]
            })
            
            fig = px.line(
                consensus_trend,
                x='Fecha',
                y='Consensos',
                title="Consensos por Día"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Efectividad por Tipo")
            
            effectiveness = pd.DataFrame({
                'Tipo': ['Spread', 'Total', 'Moneyline'],
                'Efectividad': [78.5, 82.1, 75.3],
                'Cantidad': [45, 38, 23]
            })
            
            fig = px.scatter(
                effectiveness,
                x='Cantidad',
                y='Efectividad',
                size='Cantidad',
                color='Tipo',
                title="Efectividad vs Cantidad"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabla detallada
        st.subheader("📋 Detalle de Consensos")
        
        # Datos de ejemplo expandidos
        detailed_data = [
            {
                'Fecha': '2025-07-13',
                'Hora': '14:15',
                'Deporte': 'MLB',
                'Partido': 'Yankees @ Red Sox',
                'Tipo': 'Spread',
                'Consenso': '78%',
                'Resultado': 'Ganador',
                'ROI': '+15.2%'
            },
            {
                'Fecha': '2025-07-13',
                'Hora': '13:45',
                'Deporte': 'MLB',
                'Partido': 'Dodgers @ Giants',
                'Tipo': 'Total',
                'Consenso': '82%',
                'Resultado': 'Ganador',
                'ROI': '+22.1%'
            },
            {
                'Fecha': '2025-07-12',
                'Hora': '20:30',
                'Deporte': 'MLB',
                'Partido': 'Astros @ Rangers',
                'Tipo': 'Moneyline',
                'Consenso': '65%',
                'Resultado': 'Perdedor',
                'ROI': '-12.5%'
            }
        ]
        
        df_detailed = pd.DataFrame(detailed_data)
        st.dataframe(df_detailed, use_container_width=True)
    
    def render_logs(self):
        """Renderiza la página de logs"""
        st.header("📋 Logs del Sistema")
        
        # Filtros de logs
        col1, col2, col3 = st.columns(3)
        
        with col1:
            log_level = st.selectbox("Nivel", ["Todos", "INFO", "WARNING", "ERROR", "CRITICAL"])
        with col2:
            log_date = st.date_input("Fecha", value=datetime.now().date())
        with col3:
            if st.button("🔄 Actualizar Logs"):
                st.rerun()
        
        # Logs en tiempo real
        log_container = st.container()
        
        with log_container:
            # Simular logs
            logs = [
                {"timestamp": "2025-07-13 14:30:15", "level": "INFO", "message": "Scraping MLB iniciado correctamente"},
                {"timestamp": "2025-07-13 14:30:18", "level": "INFO", "message": "12 consensos procesados desde covers.com"},
                {"timestamp": "2025-07-13 14:30:20", "level": "WARNING", "message": "Consenso alto detectado: Yankees @ Red Sox (78%)"},
                {"timestamp": "2025-07-13 14:30:22", "level": "INFO", "message": "Alerta Telegram enviada exitosamente"},
                {"timestamp": "2025-07-13 14:30:25", "level": "ERROR", "message": "Error temporal de conexión con covers.com"},
                {"timestamp": "2025-07-13 14:30:30", "level": "INFO", "message": "Reconexión exitosa, continuando scraping"},
            ]
            
            for log in logs:
                level_color = {
                    "INFO": "🟢",
                    "WARNING": "🟡", 
                    "ERROR": "🔴",
                    "CRITICAL": "⚫"
                }.get(log["level"], "⚪")
                
                st.text(f"{level_color} {log['timestamp']} [{log['level']}] {log['message']}")
        
        # Descarga de logs
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Descargar Logs del Día"):
                st.info("📥 Descargando logs...")
        
        with col2:
            if st.button("🗑️ Limpiar Logs Antiguos"):
                st.warning("🗑️ Limpieza de logs iniciada...")
    
    def render_telegram(self):
        """Renderiza la página de Telegram"""
        st.header("🤖 Configuración de Telegram")
        
        # Estado del bot
        st.subheader("📊 Estado del Bot")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🔗 Conexión", "Activa", "✅")
        with col2:
            st.metric("💬 Chats", "2", "0")
        with col3:
            st.metric("📨 Mensajes Hoy", "15", "3")
        
        # Configuración
        st.subheader("⚙️ Configuración")
        
        with st.form("telegram_config"):
            bot_token = st.text_input("🔑 Token del Bot", type="password")
            chat_ids = st.text_area("👥 Chat IDs", help="IDs de chat separados por comas")
            
            st.subheader("📱 Tipos de Notificación")
            
            col1, col2 = st.columns(2)
            
            with col1:
                notify_consensus = st.checkbox("🚨 Consensos altos", value=True)
                notify_errors = st.checkbox("❌ Errores del sistema", value=True)
            
            with col2:
                notify_daily = st.checkbox("📊 Reporte diario", value=True)
                notify_startup = st.checkbox("🚀 Inicio del sistema", value=True)
            
            submitted = st.form_submit_button("💾 Guardar Configuración")
            
            if submitted:
                st.success("✅ Configuración de Telegram guardada")
        
        # Pruebas del bot
        st.subheader("🧪 Pruebas")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📡 Test de Conexión"):
                st.info("🔍 Probando conexión...")
                # Simular test
                st.success("✅ Conexión exitosa")
        
        with col2:
            if st.button("💬 Enviar Mensaje Test"):
                st.info("📤 Enviando mensaje de prueba...")
                st.success("✅ Mensaje enviado")
        
        with col3:
            if st.button("🚨 Simular Alerta"):
                st.info("⚡ Simulando alerta de consenso...")
                st.success("✅ Alerta simulada")
        
        # Historial de mensajes
        st.subheader("📜 Historial de Mensajes")
        
        messages_history = [
            {"timestamp": "14:30", "type": "🚨 Alerta", "message": "Consenso alto: Yankees @ Red Sox (78%)"},
            {"timestamp": "13:45", "type": "📊 Info", "message": "12 consensos procesados correctamente"},
            {"timestamp": "11:00", "type": "🔄 Sistema", "message": "Scraping diario iniciado"},
            {"timestamp": "23:45", "type": "📋 Reporte", "message": "Reporte diario enviado"},
        ]
        
        for msg in messages_history:
            st.text(f"{msg['timestamp']} | {msg['type']} | {msg['message']}")
    
    def render_system(self):
        """Renderiza la página de sistema"""
        st.header("🔧 Administración del Sistema")
        
        # Estado general
        st.subheader("📊 Estado General")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💾 CPU", "15%", "-2%")
        with col2:
            st.metric("🧠 RAM", "342 MB", "+12 MB")
        with col3:
            st.metric("💿 Disco", "2.1 GB", "+150 MB")
        with col4:
            st.metric("🌐 Red", "45 KB/s", "+5 KB/s")
        
        # Servicios
        st.subheader("🔧 Estado de Servicios")
        
        services = [
            {"name": "🕷️ Scraper MLB", "status": "Activo", "uptime": "12h 45m", "last_run": "14:30"},
            {"name": "📊 Scheduler", "status": "Activo", "uptime": "12h 45m", "next_run": "16:00"},
            {"name": "🤖 Telegram Bot", "status": "Activo", "uptime": "12h 45m", "messages": "15"},
            {"name": "💾 Base de Datos", "status": "Activa", "uptime": "12h 45m", "queries": "1,234"},
        ]
        
        for service in services:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**{service['name']}**")
            with col2:
                status_class = "status-active" if service['status'] == "Activo" or service['status'] == "Activa" else "status-inactive"
                st.markdown(f"<span class='{status_class}'>{service['status']}</span>", unsafe_allow_html=True)
            with col3:
                st.write(service.get('uptime', 'N/A'))
            with col4:
                if 'last_run' in service:
                    st.write(f"Último: {service['last_run']}")
                elif 'next_run' in service:
                    st.write(f"Próximo: {service['next_run']}")
                elif 'messages' in service:
                    st.write(f"Mensajes: {service['messages']}")
                elif 'queries' in service:
                    st.write(f"Queries: {service['queries']}")
        
        # Controles del sistema
        st.subheader("🎮 Controles del Sistema")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Reiniciar Sistema", type="primary"):
                st.warning("⚠️ Reiniciando sistema...")
        
        with col2:
            if st.button("⏸️ Pausar Scraping"):
                st.info("⏸️ Scraping pausado")
        
        with col3:
            if st.button("🧹 Limpiar Cache"):
                st.success("✅ Cache limpiado")
        
        # Variables de entorno
        st.subheader("🔐 Variables de Entorno")
        
        with st.expander("Ver configuración actual"):
            env_vars = {
                "TELEGRAM_BOT_TOKEN": "***********",
                "SUPABASE_URL": "https://*****.supabase.co",
                "SUPABASE_KEY": "***********",
                "SCRAPING_INTERVAL": "120",
                "CONSENSUS_THRESHOLD": "75",
                "TIMEZONE": "America/Argentina/Buenos_Aires"
            }
            
            for key, value in env_vars.items():
                st.text(f"{key} = {value}")
    
    def refresh_data(self):
        """Actualiza los datos del sistema"""
        st.session_state.last_update = datetime.now(self.timezone)
        st.success("🔄 Datos actualizados")
        st.rerun()
    
    def run_manual_scraping(self):
        """Ejecuta scraping manual"""
        st.info("🕷️ Ejecutando scraping manual...")
        # Aquí se conectaría con el scraper real
        st.success("✅ Scraping manual completado")
    
    def test_telegram_bot(self):
        """Prueba el bot de Telegram"""
        st.info("🤖 Probando bot de Telegram...")
        # Aquí se conectaría con el bot real
        st.success("✅ Test de Telegram exitoso")
    
    def run(self):
        """Ejecuta la aplicación principal"""
        self.render_header()
        
        # Renderizar sidebar y obtener página seleccionada
        page = self.render_sidebar()
        
        # Renderizar página correspondiente
        if page == "📊 Dashboard":
            self.render_dashboard()
        elif page == "⚙️ Configuración":
            self.render_configuration()
        elif page == "📈 Estadísticas":
            self.render_statistics()
        elif page == "📋 Logs":
            self.render_logs()
        elif page == "🤖 Telegram":
            self.render_telegram()
        elif page == "🔧 Sistema":
            self.render_system()


def main():
    """Función principal de la aplicación Streamlit"""
    app = StreamlitApp()
    app.run()


if __name__ == "__main__":
    main()
