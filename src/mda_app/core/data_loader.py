"""Carregamento e processamento de dados geoespaciais."""

import geopandas as gpd
import numpy as np
import streamlit as st


@st.cache_data
def carregar_dados():
    """Carregar e processar dados geoespaciais."""
    asd = gpd.read_file("data/raw/precificacao_al_ii.geojson")
    # Criar indicadores adicionais
    asd["valor_medio"] = (asd["valor_mun_perim"] + asd["valor_mun_area"]) / 2
    return asd


def processar_dados_geograficos(gdf):
    """Processar dados geográficos."""
    gdf = gdf.to_crs(epsg=4326)
    gdf['nota_insalub_2'] = gdf['nota_insalub_2'].apply(lambda x: 1 if x < 1 else x)
    
    # Calcular média entre nota_insalub e nota_insalub_2
    gdf['nota_insalub_media'] = (gdf['nota_insalub'] + gdf['nota_insalub_2']) / 2
    
    gdf['valor_medio_car'] = np.where(
        gdf['area_car_total'] != 0,
        ((gdf['area_car_total'] / gdf['area_georef']) * gdf['valor_mun_area'])/gdf['num_imoveis'],
        0
    )
    return gdf