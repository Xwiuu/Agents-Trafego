import collections
import os
import logging
import re
from logging.handlers import RotatingFileHandler
from datetime import datetime
from rich.logging import RichHandler

# --- CONFIGURAÇÃO DO LOG BUFFER (Dashboard) ---

class LogBuffer:
    """Mantém os logs em memória para exibição no Dashboard Next.js."""
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
        memory_active = os.path.exists("./chroma_db")
        uptime_delta = datetime.now() - self.start_time
        uptime_str = f"{uptime_delta.days}d {uptime_delta.seconds // 3600}h"

        memory_percent = 0.0
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

# Instância global para o Dashboard
global_logs = LogBuffer()

# --- CUSTOM HANDLER PARA O LOG BUFFER ---

class DashboardHandler(logging.Handler):
    """Handler customizado que desvia logs para o LogBuffer do Dashboard."""
    def emit(self, record):
        try:
            msg = self.format(record)
            global_logs.add_log(msg, record.levelname)
        except Exception:
            self.handleError(record)

# --- REDACTING FORMATTER ---

class RedactingFormatter(logging.Formatter):
    """Formatador que sanitiza credenciais sensíveis dos logs."""
    
    # Padrão expandido: gsk_..., sk-..., EAAG..., lsv2_..., chaves hexadecimais longas
    _SENSITIVE_PATTERN = re.compile(
        r'(gsk_[a-zA-Z0-9]{30,}|sk-[a-zA-Z0-9]{20,}|EAAG[a-zA-Z0-9]{50,}|lsv2_[a-z]_[a-zA-Z0-9]{30,}|[a-f0-9]{32,})',
        re.IGNORECASE
    )
    
    def format(self, record):
        if not isinstance(record.msg, str):
            return super().format(record)
        
        # Redigir a mensagem antes da formatação final
        record.msg = self._SENSITIVE_PATTERN.sub('[REDACTED]', record.msg)
        return super().format(record)

# --- CONFIGURAÇÃO DO LOGGING NATIVO (Enterprise) ---

# Garantir que o diretório de logs existe
os.makedirs("logs", exist_ok=True)

# Logger principal
logger = logging.getLogger("meta_agent")
logger.setLevel(logging.INFO)

# Formatação
log_format = '[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s'
file_formatter = RedactingFormatter(log_format)
console_formatter = logging.Formatter(log_format)
# RichHandler já cuida da formatação no console de forma bonita

# Handlers
# 1. Console (Rich)
console_handler = RichHandler(rich_tracebacks=True, markup=True)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(console_formatter)

# 2. Arquivo (Rotating)
file_handler = RotatingFileHandler("logs/system.log", maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.DEBUG)

# 3. Dashboard Bridge
dashboard_handler = DashboardHandler()
dashboard_handler.setFormatter(logging.Formatter('%(message)s')) # Apenas a mensagem, o buffer adiciona o resto

# Adicionar handlers ao logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.addHandler(dashboard_handler)

# Mensagens iniciais
logger.info("Omnichannel Traffic AI Squad v2.0 carregado.")
logger.info("Conexão com ChromaDB estabelecida.")
logger.info("Aguardando ativação do Monitoramento...")
