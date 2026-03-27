"""
Módulo de gerenciamento de alertas para equipamentos offline.
Emite alertas visuais e sonoros quando equipamentos ficam indisponíveis.
"""

import platform
from datetime import datetime
from typing import Dict, List


class AlertManager:
    """Classe para gerenciar alertas de equipamentos offline."""
    
    def __init__(self):
        """Inicializa o gerenciador de alertas."""
        self.active_alerts: Dict[str, Dict] = {}  # IP -> {'timestamp': datetime, 'notified': bool}
        self.alert_history: List[Dict] = []  # Histórico de todos os alertas
        self.sound_enabled = True
        
    def process_status_change(self, ip: str, old_status: str, new_status: str, timestamp: datetime):
        """
        Processa mudança de status de um equipamento.
        
        Args:
            ip: Endereço IP do equipamento
            old_status: Status anterior ('online', 'offline', 'unknown')
            new_status: Novo status ('online', 'offline')
            timestamp: Momento da mudança
        """
        if new_status == 'offline' and old_status == 'online':
            # Equipamento ficou offline - criar alerta
            self._create_alert(ip, timestamp)
        elif new_status == 'online' and old_status == 'offline':
            # Equipamento voltou online - remover alerta
            self._clear_alert(ip, timestamp)
    
    def _create_alert(self, ip: str, timestamp: datetime):
        """
        Cria um novo alerta para um IP offline.
        
        Args:
            ip: Endereço IP
            timestamp: Momento do alerta
        """
        if ip not in self.active_alerts:
            self.active_alerts[ip] = {
                'timestamp': timestamp,
                'notified': False
            }
            
            # Adicionar ao histórico
            self.alert_history.append({
                'type': 'offline',
                'ip': ip,
                'timestamp': timestamp
            })
            
            # Emitir som de alerta
            if self.sound_enabled:
                self._play_alert_sound()
    
    def _clear_alert(self, ip: str, timestamp: datetime):
        """
        Remove um alerta quando equipamento volta online.
        
        Args:
            ip: Endereço IP
            timestamp: Momento da recuperação
        """
        if ip in self.active_alerts:
            del self.active_alerts[ip]
            
            # Adicionar recuperação ao histórico
            self.alert_history.append({
                'type': 'recovered',
                'ip': ip,
                'timestamp': timestamp
            })
    
    def _play_alert_sound(self):
        """Emite um beep sonoro de alerta."""
        try:
            if platform.system().lower() == 'windows':
                import winsound
                # Beep: frequência 1000 Hz, duração 500 ms
                winsound.Beep(1000, 500)
            else:
                # Em Linux/Mac, usa o beep do terminal
                print('\a', end='', flush=True)
        except Exception:
            # Se falhar, não faz nada
            pass
    
    def get_active_alerts(self) -> List[Dict]:
        """
        Obtém lista de alertas ativos.
        
        Returns:
            Lista de dicionários com informações dos alertas ativos
        """
        alerts = []
        for ip, data in self.active_alerts.items():
            alerts.append({
                'ip': ip,
                'timestamp': data['timestamp'],
                'duration': (datetime.now() - data['timestamp']).total_seconds()
            })
        return sorted(alerts, key=lambda x: x['timestamp'], reverse=True)
    
    def get_alert_count(self) -> int:
        """
        Obtém número de alertas ativos.
        
        Returns:
            Número de equipamentos offline com alertas ativos
        """
        return len(self.active_alerts)
    
    def has_alert(self, ip: str) -> bool:
        """
        Verifica se há alerta ativo para um IP.
        
        Args:
            ip: Endereço IP
            
        Returns:
            True se há alerta ativo, False caso contrário
        """
        return ip in self.active_alerts
    
    def get_alert_history(self, limit: int = 50) -> List[Dict]:
        """
        Obtém histórico de alertas.
        
        Args:
            limit: Número máximo de eventos a retornar (padrão: 50)
            
        Returns:
            Lista dos últimos eventos de alerta
        """
        return self.alert_history[-limit:]
    
    def clear_all_alerts(self):
        """Remove todos os alertas ativos."""
        self.active_alerts.clear()
    
    def clear_history(self):
        """Limpa o histórico de alertas."""
        self.alert_history.clear()
    
    def set_sound_enabled(self, enabled: bool):
        """
        Habilita ou desabilita alertas sonoros.
        
        Args:
            enabled: True para habilitar som, False para desabilitar
        """
        self.sound_enabled = enabled
    
    def get_summary(self) -> Dict:
        """
        Obtém resumo dos alertas.
        
        Returns:
            Dicionário com estatísticas de alertas
        """
        total_offline_events = sum(1 for event in self.alert_history if event['type'] == 'offline')
        total_recovered_events = sum(1 for event in self.alert_history if event['type'] == 'recovered')
        
        return {
            'active_alerts': len(self.active_alerts),
            'total_offline_events': total_offline_events,
            'total_recovered_events': total_recovered_events,
            'sound_enabled': self.sound_enabled
        }
