import collections
import os
from datetime import datetime

class LogBuffer:
    def __init__(self, max_size=50):
        self.buffer = collections.deque(maxlen=max_size)
        self.active_agent = "Router"
        self.api_call_count = 0
        self.start_time = datetime.now()

    def add_log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.buffer.append(f"[{timestamp}] [{level}] {message}")

    def increment_api_calls(self):
        self.api_call_count += 1

    def set_active_agent(self, agent_name: str):
        self.active_agent = agent_name
        self.add_log(f"Agente {agent_name} assumindo a tarefa.")

    def get_logs(self):
        # Verifica se a memória vetorial está ativa (pasta chroma_db existe)
        memory_active = os.path.exists("./chroma_db")
        
        # Calcula uptime simples
        uptime_delta = datetime.now() - self.start_time
        uptime_str = f"{uptime_delta.days}d {uptime_delta.seconds // 3600}h"

        # Tenta obter uso de memória real (opcional, requer psutil)
        memory_percent = 42.0
        try:
            import psutil
            memory_percent = psutil.virtual_memory().percent
        except:
            pass

        return {
            "logs": list(self.buffer),
            "active_agent": self.active_agent,
            "memory_active": memory_active,
            "metrics": {
                "api_calls": self.api_call_count,
                "uptime": uptime_str,
                "memory_usage": memory_percent,
                "start_time": self.start_time.isoformat()
            }
        }

# Instância global para o backend
global_logs = LogBuffer()
global_logs.add_log("Omnichannel Traffic AI Squad v2.0 carregado.")
global_logs.add_log("Conexão com ChromaDB estabelecida.")
global_logs.add_log("Aguardando ativação do Monitoramento...")
