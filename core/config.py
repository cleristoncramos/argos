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

# Fator de anualização usado como simplificação para mercados tradicionais.
# Em ações, 252 dias úteis/ano é uma aproximação comum. Em criptoativos,
# que operam todos os dias, uma configuração futura pode usar 365.
# O valor deve ser configurável por mercado/frequência e não aplicado sem ressalva.
ANNUALIZATION_FACTORS = {
    "Diário": 252,
    "Semanal": 52,
    "Mensal": 12,
}