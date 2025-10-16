"""Funções utilitárias para formatação e processamento de dados."""

def reais(x):
    """Formatar valor para real brasileiro."""
    val = f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return val