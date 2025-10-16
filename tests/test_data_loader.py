"""Testes para carregamento de dados."""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mda_app.core.data_loader import processar_dados_geograficos


def test_processar_dados_geograficos():
    """Testar processamento de dados geográficos."""
    # Mock de GeoDataFrame
    mock_gdf = MagicMock()
    mock_gdf.to_crs.return_value = mock_gdf
    mock_gdf.__getitem__.return_value.apply.return_value = [1, 2, 3]
    
    # Processar dados
    resultado = processar_dados_geograficos(mock_gdf)
    
    # Verificar se to_crs foi chamado
    mock_gdf.to_crs.assert_called_once_with(epsg=4326)