"""
Validadores customizados para a aplicação.
"""

import re
from typing import Optional


def validate_whatsapp_number(number: str) -> bool:
    """
    Valida se o número de WhatsApp está no formato correto.
    
    Args:
        number: Número a ser validado
    
    Returns:
        True se válido, False caso contrário
    
    Example:
        >>> validate_whatsapp_number("+5511999999999")
        True
        >>> validate_whatsapp_number("invalid")
        False
    """
    # Padrão: +55 (DDD 2 dígitos) (9 dígitos para celular)
    pattern = r"^\+55\d{2}9\d{8}$"
    return bool(re.match(pattern, number))


def validate_cpf(cpf: str) -> bool:
    """
    Valida CPF brasileiro.
    
    Args:
        cpf: CPF a ser validado (apenas números)
    
    Returns:
        True se válido, False caso contrário
    
    Example:
        >>> validate_cpf("12345678909")
        False  # CPF inválido
    """
    # Remove caracteres não numéricos
    cpf = "".join(filter(str.isdigit, cpf))
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Valida primeiro dígito verificador
    sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digit1 = 11 - (sum1 % 11)
    digit1 = 0 if digit1 >= 10 else digit1
    
    if digit1 != int(cpf[9]):
        return False
    
    # Valida segundo dígito verificador
    sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digit2 = 11 - (sum2 % 11)
    digit2 = 0 if digit2 >= 10 else digit2
    
    return digit2 == int(cpf[10])


def validate_uf(uf: str) -> bool:
    """
    Valida sigla de Unidade Federativa (UF) brasileira.
    
    Args:
        uf: Sigla da UF (2 letras)
    
    Returns:
        True se válida, False caso contrário
    
    Example:
        >>> validate_uf("SP")
        True
        >>> validate_uf("XX")
        False
    """
    valid_ufs = [
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
        "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
        "RS", "RO", "RR", "SC", "SP", "SE", "TO"
    ]
    return uf.upper() in valid_ufs


def validate_political_party(party: str) -> bool:
    """
    Valida se a sigla do partido político é válida.
    
    Args:
        party: Sigla do partido
    
    Returns:
        True se válido, False caso contrário
    
    Note:
        Lista simplificada dos principais partidos brasileiros
    """
    valid_parties = [
        "PT", "PSDB", "MDB", "PP", "PDT", "PSB", "REPUBLICANOS", "PL",
        "PSD", "PSOL", "PSL", "PODE", "PCdoB", "CIDADANIA", "AVANTE",
        "SOLIDARIEDADE", "NOVO", "PATRIOTA", "PROS", "PSC", "PTB",
        "DEM", "PV", "REDE", "PMB", "PMN", "PRTB", "DC", "PCB", "PCO",
        "PSTU", "UP", "UNIÃO"
    ]
    return party.upper() in valid_parties

