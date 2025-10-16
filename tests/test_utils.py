"""Testes para utilitários."""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mda_app.utils.formatters import reais


def test_reais_formatter():
    """Testar formatador de reais."""
    assert reais(1000) == "R$ 1.000,00"
    assert reais(1234.56) == "R$ 1.234,56"
    assert reais(0) == "R$ 0,00"


def test_reais_large_numbers():
    """Testar formatador com números grandes."""
    assert reais(1000000) == "R$ 1.000.000,00"
    assert reais(1234567.89) == "R$ 1.234.567,89"