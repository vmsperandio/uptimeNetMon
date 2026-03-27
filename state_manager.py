"""
Módulo de gerenciamento de estado persistente.
Salva e carrega configurações e histórico de monitoramento em JSON.
"""

import json
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any
import tempfile
import shutil


class StateManager:
    """Classe para gerenciar persistência de estado do monitoramento."""
    
    def __init__(self, state_file: str = "monitoring_state.json", history_days: int = 7):
        """
        Inicializa o gerenciador de estado.
        
        Args:
            state_file: Caminho do arquivo de estado (padrão: monitoring_state.json)
            history_days: Dias de histórico a manter (padrão: 7)
        """
        self.state_file = Path(state_file)
        self.history_days = history_days
        self.lock = threading.Lock()
        
    def save_state(self, monitor_data: Dict, config: Dict, alert_history: list) -> bool:
        """
        Salva o estado atual do monitoramento.
        
        Args:
            monitor_data: Dados do PingMonitor
            config: Configurações do aplicativo
            alert_history: Histórico de alertas
            
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        with self.lock:
            try:
                # Preparar dados para serialização
                state = {
                    'version': '1.0',
                    'saved_at': datetime.now().isoformat(),
                    'config': config,
                    'monitor_data': self._serialize_monitor_data(monitor_data),
                    'alert_history': self._serialize_alert_history(alert_history)
                }
                
                # Limpar dados antigos antes de salvar
                state = self._clean_old_data(state)
                
                # Salvar com atomic write (escreve em temp e depois move)
                temp_file = None
                try:
                    # Criar arquivo temporário no mesmo diretório
                    temp_fd, temp_path = tempfile.mkstemp(
                        dir=self.state_file.parent if self.state_file.parent.exists() else None,
                        prefix='.tmp_',
                        suffix='.json'
                    )
                    temp_file = Path(temp_path)
                    
                    # Escrever no arquivo temporário
                    with open(temp_fd, 'w', encoding='utf-8') as f:
                        json.dump(state, f, indent=2, ensure_ascii=False)
                    
                    # Mover arquivo temporário para o arquivo final
                    shutil.move(str(temp_file), str(self.state_file))
                    
                    return True
                    
                except Exception as e:
                    # Limpar arquivo temporário se falhar
                    if temp_file and temp_file.exists():
                        temp_file.unlink()
                    raise e
                    
            except Exception as e:
                print(f"Erro ao salvar estado: {e}")
                return False
    
    def load_state(self) -> Optional[Dict]:
        """
        Carrega o estado salvo do arquivo.
        
        Returns:
            Dicionário com estado salvo ou None se não existir/erro
        """
        with self.lock:
            try:
                if not self.state_file.exists():
                    return None
                
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                # Desserializar dados
                state['monitor_data'] = self._deserialize_monitor_data(state.get('monitor_data', {}))
                state['alert_history'] = self._deserialize_alert_history(state.get('alert_history', []))
                
                # Limpar dados antigos ao carregar
                state = self._clean_old_data(state)
                
                return state
                
            except Exception as e:
                print(f"Erro ao carregar estado: {e}")
                return None
    
    def _serialize_monitor_data(self, monitor_data: Dict) -> Dict:
        """
        Serializa dados do monitor para JSON.
        
        Args:
            monitor_data: Dados do PingMonitor
            
        Returns:
            Dados serializáveis em JSON
        """
        serialized = {}
        
        for ip, data in monitor_data.items():
            serialized[ip] = {
                'status': data.get('status', 'unknown'),
                'last_check': data.get('last_check').isoformat() if data.get('last_check') else None,
                'uptime_seconds': data.get('uptime_seconds', 0),
                'downtime_seconds': data.get('downtime_seconds', 0),
                'total_pings': data.get('total_pings', 0),
                'successful_pings': data.get('successful_pings', 0),
                'failed_pings': data.get('failed_pings', 0),
                'start_time': data.get('start_time').isoformat() if data.get('start_time') else None,
                'last_status_change': data.get('last_status_change').isoformat() if data.get('last_status_change') else None,
                'history': [
                    (ts.isoformat(), status) 
                    for ts, status in data.get('history', [])
                ]
            }
        
        return serialized
    
    def _deserialize_monitor_data(self, serialized: Dict) -> Dict:
        """
        Desserializa dados do monitor de JSON.
        
        Args:
            serialized: Dados serializados
            
        Returns:
            Dados do monitor reconstruídos
        """
        deserialized = {}
        
        for ip, data in serialized.items():
            deserialized[ip] = {
                'status': data.get('status', 'unknown'),
                'last_check': datetime.fromisoformat(data['last_check']) if data.get('last_check') else None,
                'uptime_seconds': data.get('uptime_seconds', 0),
                'downtime_seconds': data.get('downtime_seconds', 0),
                'total_pings': data.get('total_pings', 0),
                'successful_pings': data.get('successful_pings', 0),
                'failed_pings': data.get('failed_pings', 0),
                'start_time': datetime.fromisoformat(data['start_time']) if data.get('start_time') else datetime.now(),
                'last_status_change': datetime.fromisoformat(data['last_status_change']) if data.get('last_status_change') else datetime.now(),
                'history': [
                    (datetime.fromisoformat(ts), status)
                    for ts, status in data.get('history', [])
                ]
            }
        
        return deserialized
    
    def _serialize_alert_history(self, alert_history: list) -> list:
        """
        Serializa histórico de alertas para JSON.
        
        Args:
            alert_history: Lista de eventos de alerta
            
        Returns:
            Histórico serializável em JSON
        """
        serialized = []
        
        for event in alert_history:
            serialized.append({
                'type': event.get('type'),
                'ip': event.get('ip'),
                'timestamp': event.get('timestamp').isoformat() if event.get('timestamp') else None
            })
        
        return serialized
    
    def _deserialize_alert_history(self, serialized: list) -> list:
        """
        Desserializa histórico de alertas de JSON.
        
        Args:
            serialized: Histórico serializado
            
        Returns:
            Lista de eventos reconstruída
        """
        deserialized = []
        
        for event in serialized:
            deserialized.append({
                'type': event.get('type'),
                'ip': event.get('ip'),
                'timestamp': datetime.fromisoformat(event['timestamp']) if event.get('timestamp') else None
            })
        
        return deserialized
    
    def _clean_old_data(self, state: Dict) -> Dict:
        """
        Remove dados mais antigos que history_days.
        
        Args:
            state: Estado completo
            
        Returns:
            Estado com dados antigos removidos
        """
        cutoff_date = datetime.now() - timedelta(days=self.history_days)
        
        # Limpar histórico de pings
        if 'monitor_data' in state:
            for ip, data in state['monitor_data'].items():
                if 'history' in data:
                    data['history'] = [
                        (ts, status) for ts, status in data['history']
                        if (isinstance(ts, datetime) and ts > cutoff_date) or
                           (isinstance(ts, str) and datetime.fromisoformat(ts) > cutoff_date)
                    ]
        
        # Limpar histórico de alertas
        if 'alert_history' in state:
            state['alert_history'] = [
                event for event in state['alert_history']
                if event.get('timestamp') and (
                    (isinstance(event['timestamp'], datetime) and event['timestamp'] > cutoff_date) or
                    (isinstance(event['timestamp'], str) and datetime.fromisoformat(event['timestamp']) > cutoff_date)
                )
            ]
        
        return state
    
    def delete_state(self) -> bool:
        """
        Remove o arquivo de estado.
        
        Returns:
            True se removeu com sucesso, False caso contrário
        """
        with self.lock:
            try:
                if self.state_file.exists():
                    self.state_file.unlink()
                return True
            except Exception as e:
                print(f"Erro ao deletar estado: {e}")
                return False
