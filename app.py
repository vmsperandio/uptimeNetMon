"""
Aplicativo Streamlit para Monitoramento de Uptime de Rede.
Interface web para monitorar disponibilidade de equipamentos via ping.
"""

import streamlit as st
import time
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path

from ping_monitor import PingMonitor
from alert_manager import AlertManager
from state_manager import StateManager
from keep_alive import KeepAlive
from report_generator import ReportGenerator


# Configuração da página
st.set_page_config(
    page_title="Monitoramento de Uptime de Rede",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar session state
if 'monitor' not in st.session_state:
    st.session_state.monitor = None
if 'alert_manager' not in st.session_state:
    st.session_state.alert_manager = AlertManager()
if 'keep_alive' not in st.session_state:
    st.session_state.keep_alive = None
if 'monitoring_active' not in st.session_state:
    st.session_state.monitoring_active = False
if 'keep_alive_active' not in st.session_state:
    st.session_state.keep_alive_active = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'state_manager' not in st.session_state:
    st.session_state.state_manager = StateManager()
if 'last_save_time' not in st.session_state:
    st.session_state.last_save_time = datetime.now()
if 'monitoring_start_time' not in st.session_state:
    st.session_state.monitoring_start_time = None


def add_log(message: str):
    """Adiciona mensagem ao log com timestamp."""
    timestamp = datetime.now().strftime('%H:%M:%S')
    st.session_state.logs.append(f"[{timestamp}] {message}")
    # Limitar logs a 100 últimas entradas
    if len(st.session_state.logs) > 100:
        st.session_state.logs = st.session_state.logs[-100:]


def parse_ips(ip_text: str) -> list:
    """Parse IPs do textarea."""
    lines = ip_text.strip().split('\n')
    ips = [line.strip() for line in lines if line.strip()]
    return ips


def start_monitoring(ips: list, ping_interval: int):
    """Inicia o monitoramento."""
    if not ips:
        st.error("Por favor, insira pelo menos um endereço IP.")
        return
    
    # Criar monitor
    st.session_state.monitor = PingMonitor(
        ips=ips,
        ping_interval=ping_interval,
        history_days=7
    )
    st.session_state.monitor.start()
    st.session_state.monitoring_active = True
    st.session_state.monitoring_start_time = datetime.now()
    
    add_log(f"Monitoramento iniciado para {len(ips)} IP(s)")


def stop_monitoring():
    """Para o monitoramento."""
    if st.session_state.monitor:
        st.session_state.monitor.stop()
        
        # Salvar estado antes de parar
        save_state()
        
        st.session_state.monitoring_active = False
        add_log("Monitoramento parado")


def start_keep_alive(interval: int):
    """Inicia o keep-alive."""
    st.session_state.keep_alive = KeepAlive(interval=interval)
    st.session_state.keep_alive.start()
    st.session_state.keep_alive_active = True
    add_log(f"Keep-Alive iniciado (intervalo: {interval}s)")


def stop_keep_alive():
    """Para o keep-alive."""
    if st.session_state.keep_alive:
        st.session_state.keep_alive.stop()
        st.session_state.keep_alive_active = False
        add_log("Keep-Alive parado")


def save_state():
    """Salva o estado atual."""
    if st.session_state.monitor:
        config = {
            'ips': st.session_state.monitor.ips,
            'ping_interval': st.session_state.monitor.ping_interval,
            'mouse_interval': st.session_state.keep_alive.get_interval() if st.session_state.keep_alive else 60,
            'ui_refresh_interval': st.session_state.get('ui_refresh_interval', 5)
        }
        
        st.session_state.state_manager.save_state(
            monitor_data=st.session_state.monitor.data,
            config=config,
            alert_history=st.session_state.alert_manager.alert_history
        )
        st.session_state.last_save_time = datetime.now()


def load_state():
    """Carrega estado salvo."""
    state = st.session_state.state_manager.load_state()
    
    if state:
        config = state.get('config', {})
        monitor_data = state.get('monitor_data', {})
        alert_history = state.get('alert_history', [])
        
        # Restaurar alertas
        st.session_state.alert_manager.alert_history = alert_history
        
        return config, monitor_data
    
    return None, None


def process_monitor_events():
    """Processa eventos do monitor."""
    if not st.session_state.monitor:
        return
    
    events = st.session_state.monitor.get_events()
    
    for event in events:
        event_type = event.get('type')
        
        if event_type == 'status_change':
            # Processar mudança de status
            ip = event.get('ip')
            old_status = event.get('old_status')
            new_status = event.get('new_status')
            timestamp = event.get('timestamp')
            
            st.session_state.alert_manager.process_status_change(
                ip, old_status, new_status, timestamp
            )
            
            # Log
            status_icon = '🟢' if new_status == 'online' else '🔴'
            add_log(f"{status_icon} {ip}: {old_status} → {new_status}")
        
        elif event_type == 'ping_result':
            # Log de ping (apenas para mudanças ou a cada N pings)
            pass


# Sidebar - Configurações
st.sidebar.title("⚙️ Configurações")

# Carregar estado salvo
if st.sidebar.button("📥 Carregar Estado Salvo"):
    config, monitor_data = load_state()
    if config:
        st.sidebar.success("Estado carregado com sucesso!")
        add_log("Estado carregado do arquivo")
    else:
        st.sidebar.info("Nenhum estado salvo encontrado")

st.sidebar.markdown("---")

# Input de IPs
st.sidebar.subheader("🌐 Endereços IP")
ip_input = st.sidebar.text_area(
    "IPs a monitorar (um por linha):",
    value="8.8.8.8\n1.1.1.1",
    height=150,
    help="Digite um endereço IP por linha"
)

st.sidebar.markdown("---")

# Configurações de intervalo
st.sidebar.subheader("⏱️ Intervalos")

ping_interval = st.sidebar.slider(
    "Intervalo entre pings (segundos):",
    min_value=1,
    max_value=60,
    value=5,
    help="Tempo de espera entre cada ping"
)

mouse_interval = st.sidebar.slider(
    "Intervalo de movimento do mouse (segundos):",
    min_value=10,
    max_value=300,
    value=60,
    help="Frequência de movimento do mouse para evitar hibernação"
)

ui_refresh_interval = st.sidebar.slider(
    "Intervalo de atualização da interface (segundos):",
    min_value=1,
    max_value=30,
    value=5,
    help="Frequência de atualização dos dados na tela"
)

st.session_state.ui_refresh_interval = ui_refresh_interval

st.sidebar.markdown("---")

# Controles
st.sidebar.subheader("🎮 Controles")

col1, col2 = st.sidebar.columns(2)

# Botão de iniciar/parar monitoramento
if not st.session_state.monitoring_active:
    if col1.button("▶️ Iniciar", use_container_width=True):
        ips = parse_ips(ip_input)
        start_monitoring(ips, ping_interval)
        st.rerun()
else:
    if col1.button("⏹️ Parar", use_container_width=True):
        stop_monitoring()
        st.rerun()

# Botão de keep-alive
if not st.session_state.keep_alive_active:
    if col2.button("🖱️ Ativar Keep-Alive", use_container_width=True):
        start_keep_alive(mouse_interval)
        st.rerun()
else:
    if col2.button("🖱️ Desativar Keep-Alive", use_container_width=True):
        stop_keep_alive()
        st.rerun()

st.sidebar.markdown("---")

# Botão de salvar estado
if st.sidebar.button("💾 Salvar Estado", use_container_width=True):
    save_state()
    st.sidebar.success("Estado salvo!")

# Botão de limpar histórico
if st.sidebar.button("🗑️ Limpar Histórico", use_container_width=True):
    if st.session_state.monitor:
        for ip in st.session_state.monitor.ips:
            st.session_state.monitor.data[ip]['history'] = []
    st.session_state.logs = []
    st.session_state.alert_manager.clear_history()
    st.sidebar.success("Histórico limpo!")
    st.rerun()

# Main content
st.title("🌐 Monitoramento de Uptime de Rede")

# Status do monitoramento
status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    if st.session_state.monitoring_active:
        st.success("✅ Monitoramento Ativo")
    else:
        st.info("⏸️ Monitoramento Parado")

with status_col2:
    if st.session_state.keep_alive_active:
        st.success("🖱️ Keep-Alive Ativo")
    else:
        st.info("🖱️ Keep-Alive Inativo")

with status_col3:
    alert_count = st.session_state.alert_manager.get_alert_count()
    if alert_count > 0:
        st.error(f"⚠️ {alert_count} Alerta(s) Ativo(s)")
    else:
        st.success("✅ Sem Alertas")

st.markdown("---")

# Processar eventos se monitoramento ativo
if st.session_state.monitoring_active:
    process_monitor_events()
    
    # Auto-save periódico (a cada 5 minutos)
    if (datetime.now() - st.session_state.last_save_time).total_seconds() > 300:
        save_state()

# Exibir dados se monitoramento existe
if st.session_state.monitor:
    stats = st.session_state.monitor.get_all_statistics()
    
    # Métricas por IP
    st.subheader("📊 Métricas por Equipamento")
    
    num_ips = len(stats)
    cols_per_row = 3
    
    for i in range(0, num_ips, cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, (ip, data) in enumerate(list(stats.items())[i:i+cols_per_row]):
            with cols[j]:
                # Card de métrica
                status = data.get('status', 'unknown')
                uptime_percent = data.get('uptime_percent', 0)
                
                # Cor baseada no status
                if status == 'online':
                    status_icon = "🟢"
                elif status == 'offline':
                    status_icon = "🔴"
                else:
                    status_icon = "⚪"
                
                # Verificar se há alerta
                has_alert = st.session_state.alert_manager.has_alert(ip)
                
                if has_alert:
                    st.error(f"⚠️ **{ip}**")
                else:
                    st.info(f"**{ip}**")
                
                st.metric(
                    label=f"{status_icon} Status",
                    value=f"{uptime_percent:.2f}%",
                    delta=status.capitalize()
                )
                
                # Estatísticas adicionais
                total_pings = data.get('total_pings', 0)
                successful = data.get('successful_pings', 0)
                failed = data.get('failed_pings', 0)
                
                st.caption(f"Total: {total_pings} | ✅ {successful} | ❌ {failed}")
    
    st.markdown("---")
    
    # Gráficos de uptime
    st.subheader("📈 Histórico de Disponibilidade (Últimas 24 Horas)")
    
    for ip in st.session_state.monitor.ips:
        with st.expander(f"📊 {ip}", expanded=False):
            history_data = st.session_state.monitor.get_history_for_chart(ip, hours=24)
            
            if history_data['timestamps']:
                # Criar DataFrame para o gráfico
                df = pd.DataFrame({
                    'Timestamp': history_data['timestamps'],
                    'Status': history_data['values']
                })
                
                # Gráfico de linha
                st.line_chart(df.set_index('Timestamp')['Status'])
                
                st.caption("1 = Online | 0 = Offline")
            else:
                st.info("Sem dados de histórico ainda")
    
    st.markdown("---")
    
    # Alertas ativos
    active_alerts = st.session_state.alert_manager.get_active_alerts()
    
    if active_alerts:
        st.subheader("⚠️ Alertas Ativos")
        
        for alert in active_alerts:
            ip = alert['ip']
            timestamp = alert['timestamp']
            duration = alert['duration']
            
            duration_str = f"{int(duration // 60)}m {int(duration % 60)}s"
            
            st.error(f"🔴 **{ip}** está offline há {duration_str} (desde {timestamp.strftime('%H:%M:%S')})")
    
    st.markdown("---")
    
    # Botão de exportar relatório
    st.subheader("📄 Relatório")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write("Exporte um relatório completo com estatísticas e histórico de eventos.")
    
    with col2:
        if st.button("📥 Exportar Relatório", use_container_width=True):
            # Gerar relatório
            generator = ReportGenerator()
            
            config = {
                'ping_interval': st.session_state.monitor.ping_interval,
                'mouse_interval': st.session_state.keep_alive.get_interval() if st.session_state.keep_alive else 60,
                'ui_refresh_interval': ui_refresh_interval
            }
            
            report_content = generator.generate_report(
                monitor_stats=stats,
                config=config,
                alert_history=st.session_state.alert_manager.alert_history,
                start_time=st.session_state.monitoring_start_time,
                end_time=datetime.now()
            )
            
            filename = generator.generate_filename()
            
            st.download_button(
                label="⬇️ Download TXT",
                data=report_content,
                file_name=filename,
                mime="text/plain"
            )
            
            add_log("Relatório gerado")

st.markdown("---")

# Logs em tempo real
st.subheader("📋 Logs em Tempo Real")

log_container = st.container()

with log_container:
    if st.session_state.logs:
        # Exibir últimos 20 logs
        for log in st.session_state.logs[-20:][::-1]:
            st.text(log)
    else:
        st.info("Nenhum log ainda. Inicie o monitoramento.")

# Auto-refresh se monitoramento ativo
if st.session_state.monitoring_active:
    time.sleep(ui_refresh_interval)
    st.rerun()
