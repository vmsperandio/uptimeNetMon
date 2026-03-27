"""
Módulo de geração de relatórios de uptime.
Exporta dados de monitoramento em formato TXT.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from io import StringIO


class ReportGenerator:
    """Classe para gerar relatórios de uptime em formato TXT."""
    
    def __init__(self):
        """Inicializa o gerador de relatórios."""
        pass
    
    def generate_report(
        self,
        monitor_stats: Dict[str, Dict],
        config: Dict,
        alert_history: List[Dict],
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> str:
        """
        Gera relatório completo de uptime.
        
        Args:
            monitor_stats: Estatísticas de monitoramento por IP
            config: Configurações usadas no monitoramento
            alert_history: Histórico de alertas
            start_time: Início do período (opcional)
            end_time: Fim do período (opcional)
            
        Returns:
            String com conteúdo do relatório em formato TXT
        """
        output = StringIO()
        
        # Cabeçalho
        output.write("=" * 80 + "\n")
        output.write("RELATÓRIO DE MONITORAMENTO DE UPTIME DE REDE\n")
        output.write("=" * 80 + "\n\n")
        
        # Período do relatório
        output.write("PERÍODO DO RELATÓRIO\n")
        output.write("-" * 80 + "\n")
        
        if start_time:
            output.write(f"Início: {start_time.strftime('%d/%m/%Y %H:%M:%S')}\n")
        
        if end_time:
            output.write(f"Fim:    {end_time.strftime('%d/%m/%Y %H:%M:%S')}\n")
        else:
            output.write(f"Fim:    {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        
        output.write("\n")
        
        # Configurações
        output.write("CONFIGURAÇÕES\n")
        output.write("-" * 80 + "\n")
        output.write(f"Intervalo entre pings: {config.get('ping_interval', 5)} segundos\n")
        output.write(f"Timeout de ping: 2 segundos\n")
        output.write(f"Intervalo de movimento do mouse: {config.get('mouse_interval', 60)} segundos\n")
        output.write(f"Intervalo de atualização da interface: {config.get('ui_refresh_interval', 5)} segundos\n")
        output.write("\n")
        
        # Resumo geral
        output.write("RESUMO GERAL\n")
        output.write("-" * 80 + "\n")
        output.write(f"Total de IPs monitorados: {len(monitor_stats)}\n")
        
        # Calcular disponibilidade média
        if monitor_stats:
            avg_uptime = sum(
                stats.get('uptime_percent', 0) 
                for stats in monitor_stats.values()
            ) / len(monitor_stats)
            output.write(f"Disponibilidade média: {avg_uptime:.2f}%\n")
        else:
            output.write("Disponibilidade média: N/A\n")
        
        output.write("\n")
        
        # Detalhes por IP
        output.write("DETALHES POR EQUIPAMENTO\n")
        output.write("=" * 80 + "\n\n")
        
        for ip, stats in sorted(monitor_stats.items()):
            self._write_ip_details(output, ip, stats)
            output.write("\n")
        
        # Timeline de eventos críticos
        if alert_history:
            output.write("TIMELINE DE EVENTOS CRÍTICOS\n")
            output.write("=" * 80 + "\n\n")
            self._write_event_timeline(output, alert_history)
        
        # Rodapé
        output.write("\n")
        output.write("=" * 80 + "\n")
        output.write(f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        output.write("=" * 80 + "\n")
        
        return output.getvalue()
    
    def _write_ip_details(self, output: StringIO, ip: str, stats: Dict):
        """
        Escreve detalhes de um IP no relatório.
        
        Args:
            output: Buffer de saída
            ip: Endereço IP
            stats: Estatísticas do IP
        """
        output.write(f"IP: {ip}\n")
        output.write("-" * 80 + "\n")
        
        # Status atual
        status = stats.get('status', 'unknown')
        status_text = {
            'online': '🟢 ONLINE',
            'offline': '🔴 OFFLINE',
            'unknown': '⚪ DESCONHECIDO'
        }.get(status, status.upper())
        output.write(f"Status Atual: {status_text}\n")
        
        # Uptime percentual
        uptime_percent = stats.get('uptime_percent', 0)
        output.write(f"Disponibilidade: {uptime_percent:.2f}%\n")
        
        # Tempo total de monitoramento
        total_time = stats.get('total_time', 0)
        total_duration = self._format_duration(total_time)
        output.write(f"Tempo Total Monitorado: {total_duration}\n")
        
        # Total de pings
        total_pings = stats.get('total_pings', 0)
        successful = stats.get('successful_pings', 0)
        failed = stats.get('failed_pings', 0)
        output.write(f"Total de Pings: {total_pings} (Sucesso: {successful}, Falha: {failed})\n")
        
        # Tempo online/offline
        if total_time > 0 and total_pings > 0:
            avg_interval = total_time / total_pings if total_pings > 0 else 0
            online_time = successful * avg_interval
            offline_time = failed * avg_interval
            
            output.write(f"Tempo Online (estimado): {self._format_duration(online_time)}\n")
            output.write(f"Tempo Offline (estimado): {self._format_duration(offline_time)}\n")
        
        # Última verificação
        last_check = stats.get('last_check')
        if last_check:
            output.write(f"Última Verificação: {last_check.strftime('%d/%m/%Y %H:%M:%S')}\n")
        
        # Última mudança de status
        last_change = stats.get('last_status_change')
        if last_change:
            output.write(f"Última Mudança de Status: {last_change.strftime('%d/%m/%Y %H:%M:%S')}\n")
    
    def _write_event_timeline(self, output: StringIO, alert_history: List[Dict]):
        """
        Escreve timeline de eventos no relatório.
        
        Args:
            output: Buffer de saída
            alert_history: Lista de eventos de alerta
        """
        # Ordenar eventos por timestamp (mais recentes primeiro)
        sorted_events = sorted(
            alert_history,
            key=lambda x: x.get('timestamp', datetime.min),
            reverse=True
        )
        
        for event in sorted_events[:50]:  # Limitar a 50 eventos mais recentes
            timestamp = event.get('timestamp')
            event_type = event.get('type', 'unknown')
            ip = event.get('ip', 'N/A')
            
            if timestamp:
                time_str = timestamp.strftime('%d/%m/%Y %H:%M:%S')
            else:
                time_str = 'N/A'
            
            if event_type == 'offline':
                icon = '🔴'
                description = 'FICOU OFFLINE'
            elif event_type == 'recovered':
                icon = '🟢'
                description = 'RECUPERADO'
            else:
                icon = '⚪'
                description = event_type.upper()
            
            output.write(f"{time_str} | {icon} {ip} - {description}\n")
    
    def _format_duration(self, seconds: float) -> str:
        """
        Formata duração em segundos para formato legível.
        
        Args:
            seconds: Duração em segundos
            
        Returns:
            String formatada (ex: "2d 5h 30m 15s")
        """
        if seconds < 0:
            return "0s"
        
        delta = timedelta(seconds=int(seconds))
        
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")
        
        return " ".join(parts)
    
    def generate_filename(self) -> str:
        """
        Gera nome de arquivo para o relatório.
        
        Returns:
            Nome do arquivo com timestamp
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"relatorio_uptime_{timestamp}.txt"
