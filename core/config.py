from dataclasses import dataclass


@dataclass
class AppConfig:
    """Configurações padrão da aplicação"""
    FREQUENCIES: tuple = ("Diário", "Semanal", "Mensal", "Semestral", "Anual")


# Instância única de configuração
config = AppConfig()

# Fator de anualização por frequência dos retornos (convenção do projeto,
# ver docs/catalogo-de-ativos.md, seção 26).
# Em ações, 252 dias úteis/ano é uma aproximação comum. Em criptoativos,
# que operam todos os dias, uma configuração futura pode usar 365.
# Toda frequência listada em AppConfig.FREQUENCIES deve ter uma entrada aqui
# (verificado por tests/test_config.py).
ANNUALIZATION_FACTORS = {
    "Diário": 252,
    "Semanal": 52,
    "Mensal": 12,
    "Semestral": 2,
    "Anual": 1,
}

# Frequências em que o último período pode ainda não ter terminado e, por
# isso, ter retorno parcial (o semestre ou o ano em andamento).
LONG_FREQUENCIES = ("Semestral", "Anual")