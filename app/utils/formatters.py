"""
Utilitários para formatação de dados e mensagens.
"""

from typing import Optional
from datetime import datetime


def format_whatsapp_number(number: str) -> str:
    """
    Formata número de WhatsApp para o padrão brasileiro.
    
    Args:
        number: Número de telefone em qualquer formato
    
    Returns:
        Número formatado (+5511999999999)
    
    Example:
        >>> format_whatsapp_number("11999999999")
        '+5511999999999'
        >>> format_whatsapp_number("+55 11 99999-9999")
        '+5511999999999'
    """
    # Remove caracteres não numéricos
    clean_number = "".join(filter(str.isdigit, number))
    
    # Adiciona código do país se não tiver
    if not clean_number.startswith("55"):
        clean_number = f"55{clean_number}"
    
    # Adiciona o +
    if not clean_number.startswith("+"):
        clean_number = f"+{clean_number}"
    
    return clean_number


def format_currency(value: float) -> str:
    """
    Formata valor monetário em Real brasileiro.
    
    Args:
        value: Valor numérico
    
    Returns:
        String formatada (R$ 1.234,56)
    
    Example:
        >>> format_currency(1234.56)
        'R$ 1.234,56'
    """
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_politician_name(full_name: str) -> str:
    """
    Formata nome de político (capitalização correta).
    
    Args:
        full_name: Nome completo
    
    Returns:
        Nome formatado
    
    Example:
        >>> format_politician_name("JOÃO DA SILVA")
        'João da Silva'
    """
    # Palavras que devem ficar minúsculas
    lowercase_words = ["de", "da", "do", "das", "dos", "e"]
    
    words = full_name.lower().split()
    formatted_words = []
    
    for i, word in enumerate(words):
        if i == 0 or word not in lowercase_words:
            formatted_words.append(word.capitalize())
        else:
            formatted_words.append(word)
    
    return " ".join(formatted_words)


def format_date_br(date: datetime) -> str:
    """
    Formata data no padrão brasileiro.
    
    Args:
        date: Objeto datetime
    
    Returns:
        Data formatada (DD/MM/YYYY)
    
    Example:
        >>> format_date_br(datetime(2024, 1, 15))
        '15/01/2024'
    """
    return date.strftime("%d/%m/%Y")


def format_datetime_br(dt: datetime) -> str:
    """
    Formata data e hora no padrão brasileiro.
    
    Args:
        dt: Objeto datetime
    
    Returns:
        Data e hora formatadas (DD/MM/YYYY HH:MM)
    
    Example:
        >>> format_datetime_br(datetime(2024, 1, 15, 14, 30))
        '15/01/2024 14:30'
    """
    return dt.strftime("%d/%m/%Y %H:%M")


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Trunca texto mantendo palavras inteiras.
    
    Args:
        text: Texto a ser truncado
        max_length: Comprimento máximo
        suffix: Sufixo a adicionar se truncado
    
    Returns:
        Texto truncado
    
    Example:
        >>> truncate_text("Este é um texto longo demais", max_length=20)
        'Este é um texto...'
    """
    if len(text) <= max_length:
        return text
    
    # Trunca e encontra o último espaço
    truncated = text[:max_length - len(suffix)]
    last_space = truncated.rfind(" ")
    
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return truncated + suffix

