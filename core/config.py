from dataclasses import dataclass

@dataclass
class AppConfig:
    """Configurações padrão da aplicação"""
    DEFAULT_ACTIVE: str = "BTC-USD"
    DEFAULT_START_DATE: str = "2017-01-01"
    DEFAULT_END_DATE: str = "2025-12-31"
    FREQUENCIES: tuple = ("Diário", "Semanal", "Mensal")
    DEFAULT_FREQUENCY: str = "Mensal"

# Instância única de configuração
config = AppConfig()