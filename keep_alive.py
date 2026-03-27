"""
Módulo para manter o notebook ativo.
Move o mouse periodicamente para evitar hibernação do Windows.
"""

import threading
import time
import pyautogui


class KeepAlive:
    """Classe para manter o sistema ativo movendo o mouse periodicamente."""
    
    def __init__(self, interval: int = 60):
        """
        Inicializa o keep-alive.
        
        Args:
            interval: Intervalo entre movimentos do mouse em segundos (padrão: 60)
        """
        self.interval = interval
        self.running = False
        self.thread: threading.Thread = None
        self.stop_event = threading.Event()
        
        # Configurar pyautogui para ser mais seguro
        pyautogui.FAILSAFE = True  # Mover mouse para canto superior esquerdo aborta
        pyautogui.PAUSE = 0.1  # Pequena pausa entre comandos
    
    def _worker(self):
        """Thread worker que move o mouse periodicamente."""
        while not self.stop_event.is_set():
            try:
                # Movimento imperceptível: move 1 pixel para direita e depois volta
                pyautogui.moveRel(1, 0, duration=0.1)
                time.sleep(0.2)
                pyautogui.moveRel(-1, 0, duration=0.1)
                
            except Exception as e:
                # Se falhar (por exemplo, pyautogui não disponível), apenas ignora
                print(f"Aviso: Erro ao mover mouse: {e}")
            
            # Aguardar intervalo antes do próximo movimento
            # Usar wait com timeout para poder interromper rapidamente
            self.stop_event.wait(self.interval)
    
    def start(self):
        """Inicia o keep-alive."""
        if self.running:
            return
        
        self.running = True
        self.stop_event.clear()
        
        # Criar e iniciar thread
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Para o keep-alive."""
        if not self.running:
            return
        
        self.running = False
        self.stop_event.set()
        
        # Aguardar thread finalizar
        if self.thread:
            self.thread.join(timeout=2)
            self.thread = None
    
    def is_running(self) -> bool:
        """
        Verifica se o keep-alive está rodando.
        
        Returns:
            True se está rodando, False caso contrário
        """
        return self.running
    
    def set_interval(self, interval: int):
        """
        Define novo intervalo entre movimentos.
        
        Args:
            interval: Novo intervalo em segundos
        """
        self.interval = max(1, interval)  # Mínimo de 1 segundo
        
        # Se está rodando, reiniciar para aplicar novo intervalo
        if self.running:
            self.stop()
            self.start()
    
    def get_interval(self) -> int:
        """
        Obtém o intervalo atual.
        
        Returns:
            Intervalo em segundos
        """
        return self.interval
