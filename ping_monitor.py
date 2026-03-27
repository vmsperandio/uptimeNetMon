"""
Módulo de monitoramento de ping para equipamentos de rede.
Executa pings em múltiplos IPs com timeout de 2 segundos e rastreia histórico de uptime.
"""

import subprocess
import threading
import queue
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import platform


class PingMonitor:
    """Classe para monitorar múltiplos IPs via ping e calcular uptime."""
    
    def __init__(self, ips: List[str], ping_interval: int = 5, history_days: int = 7):
        """
        Inicializa o monitor de ping.
        
        Args:
            ips: Lista de endereços IP para monitorar
            ping_interval: Intervalo entre pings em segundos (padrão: 5)
            history_days: Dias de histórico a manter (padrão: 7)
        """
        self.ips = ips
        self.ping_interval = ping_interval
        self.history_days = history_days
        self.timeout = 2  # Timeout fixo de 2 segundos
        
        # Estrutura de dados para cada IP
        self.data: Dict[str, Dict] = {}
        for ip in ips:
            self.data[ip] = {
                'status': 'unknown',  # 'online', 'offline', 'unknown'
                'last_check': None,
                'uptime_seconds': 0,
                'downtime_seconds': 0,
                'total_pings': 0,
                'successful_pings': 0,
                'failed_pings': 0,
                'history': [],  # Lista de (timestamp, status)
                'start_time': datetime.now(),
                'last_status_change': datetime.now()
            }
        
        # Controle de threads
        self.running = False
        self.threads: List[threading.Thread] = []
        self.event_queue = queue.Queue()
        self.lock = threading.Lock()
        
    def _execute_ping(self, ip: str) -> bool:
        """
        Executa um ping para o IP especificado.
        
        Args:
            ip: Endereço IP para pingar
            
        Returns:
            True se o ping foi bem-sucedido, False caso contrário
        """
        try:
            # Comando ping varia entre Windows e Linux/Mac
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'
            
            # Windows: -w em milissegundos, Linux/Mac: -W em segundos
            timeout_value = str(self.timeout * 1000) if platform.system().lower() == 'windows' else str(self.timeout)
            
            command = ['ping', param, '1', timeout_param, timeout_value, ip]
            
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self.timeout + 1  # Timeout extra para o subprocess
            )
            
            return result.returncode == 0
            
        except (subprocess.TimeoutExpired, Exception) as e:
            return False
    
    def _ping_worker(self, ip: str):
        """
        Thread worker que executa pings continuamente para um IP.
        
        Args:
            ip: Endereço IP para monitorar
        """
        while self.running:
            timestamp = datetime.now()
            success = self._execute_ping(ip)
            
            with self.lock:
                # Atualizar estatísticas
                old_status = self.data[ip]['status']
                new_status = 'online' if success else 'offline'
                
                self.data[ip]['status'] = new_status
                self.data[ip]['last_check'] = timestamp
                self.data[ip]['total_pings'] += 1
                
                if success:
                    self.data[ip]['successful_pings'] += 1
                else:
                    self.data[ip]['failed_pings'] += 1
                
                # Adicionar ao histórico
                self.data[ip]['history'].append((timestamp, new_status))
                
                # Detectar mudança de estado
                if old_status != new_status and old_status != 'unknown':
                    self.data[ip]['last_status_change'] = timestamp
                    # Enviar evento de alerta
                    self.event_queue.put({
                        'type': 'status_change',
                        'ip': ip,
                        'old_status': old_status,
                        'new_status': new_status,
                        'timestamp': timestamp
                    })
                
                # Limpar histórico antigo (mais de history_days)
                cutoff_date = timestamp - timedelta(days=self.history_days)
                self.data[ip]['history'] = [
                    (ts, status) for ts, status in self.data[ip]['history']
                    if ts > cutoff_date
                ]
            
            # Enviar evento de log
            self.event_queue.put({
                'type': 'ping_result',
                'ip': ip,
                'status': new_status,
                'timestamp': timestamp
            })
            
            # Aguardar intervalo antes do próximo ping
            time.sleep(self.ping_interval)
    
    def start(self):
        """Inicia o monitoramento de todos os IPs."""
        if self.running:
            return
        
        self.running = True
        
        # Criar thread para cada IP
        for ip in self.ips:
            thread = threading.Thread(target=self._ping_worker, args=(ip,), daemon=True)
            thread.start()
            self.threads.append(thread)
    
    def stop(self):
        """Para o monitoramento de todos os IPs."""
        self.running = False
        
        # Aguardar threads finalizarem (com timeout)
        for thread in self.threads:
            thread.join(timeout=self.ping_interval + 2)
        
        self.threads.clear()
    
    def get_events(self) -> List[Dict]:
        """
        Obtém eventos pendentes da fila.
        
        Returns:
            Lista de eventos (dicionários)
        """
        events = []
        while not self.event_queue.empty():
            try:
                events.append(self.event_queue.get_nowait())
            except queue.Empty:
                break
        return events
    
    def get_statistics(self, ip: str) -> Optional[Dict]:
        """
        Obtém estatísticas de uptime para um IP específico.
        
        Args:
            ip: Endereço IP
            
        Returns:
            Dicionário com estatísticas ou None se IP não encontrado
        """
        with self.lock:
            if ip not in self.data:
                return None
            
            data = self.data[ip].copy()
            
            # Calcular uptime percentual
            if data['total_pings'] > 0:
                data['uptime_percent'] = (data['successful_pings'] / data['total_pings']) * 100
            else:
                data['uptime_percent'] = 0.0
            
            # Calcular tempo total de monitoramento
            if data['last_check']:
                data['total_time'] = (data['last_check'] - data['start_time']).total_seconds()
            else:
                data['total_time'] = 0
            
            return data
    
    def get_all_statistics(self) -> Dict[str, Dict]:
        """
        Obtém estatísticas de todos os IPs monitorados.
        
        Returns:
            Dicionário com IP como chave e estatísticas como valor
        """
        stats = {}
        for ip in self.ips:
            stats[ip] = self.get_statistics(ip)
        return stats
    
    def get_history_for_chart(self, ip: str, hours: int = 24) -> Dict:
        """
        Obtém dados do histórico formatados para gráficos.
        
        Args:
            ip: Endereço IP
            hours: Número de horas de histórico (padrão: 24)
            
        Returns:
            Dicionário com timestamps e valores para gráfico
        """
        with self.lock:
            if ip not in self.data:
                return {'timestamps': [], 'values': []}
            
            cutoff = datetime.now() - timedelta(hours=hours)
            history = self.data[ip]['history']
            
            # Filtrar histórico recente
            recent = [(ts, status) for ts, status in history if ts > cutoff]
            
            timestamps = [ts for ts, _ in recent]
            values = [1 if status == 'online' else 0 for _, status in recent]
            
            return {
                'timestamps': timestamps,
                'values': values
            }
    
    def add_ip(self, ip: str):
        """
        Adiciona um novo IP para monitoramento.
        
        Args:
            ip: Endereço IP para adicionar
        """
        with self.lock:
            if ip in self.data:
                return
            
            self.data[ip] = {
                'status': 'unknown',
                'last_check': None,
                'uptime_seconds': 0,
                'downtime_seconds': 0,
                'total_pings': 0,
                'successful_pings': 0,
                'failed_pings': 0,
                'history': [],
                'start_time': datetime.now(),
                'last_status_change': datetime.now()
            }
            
            self.ips.append(ip)
            
            # Se já está rodando, iniciar thread para este IP
            if self.running:
                thread = threading.Thread(target=self._ping_worker, args=(ip,), daemon=True)
                thread.start()
                self.threads.append(thread)
    
    def remove_ip(self, ip: str):
        """
        Remove um IP do monitoramento.
        
        Args:
            ip: Endereço IP para remover
        """
        with self.lock:
            if ip in self.data:
                del self.data[ip]
            if ip in self.ips:
                self.ips.remove(ip)
