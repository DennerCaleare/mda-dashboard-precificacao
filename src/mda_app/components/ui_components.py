"""Componentes de interface do usuário."""

import streamlit as st
from mda_app.config.settings import COLORS


def render_header():
    """Renderizar cabeçalho da aplicação."""
    col1, col2, col3 = st.columns([1, 1, 3])

    with col1:
        st.image("assets/images/img_1.png", width=250)

    with col2:
        st.markdown(
            f"""
            <div style="text-align: center;">
                <h1 style='color: {COLORS["primary"]}; margin-bottom: 0; white-space: nowrap;'>
                    Dashboard - Precificação de Áreas Georreferenciáveis
                </h1>
                <h3 style='color:{COLORS["primary"]}; font-weight: normal; margin-top: 5px; white-space: nowrap;'>
                    Graus de Dificuldade e Valores
                </h3>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_metrics(gdf_filtrado):
    """Renderizar métricas principais."""
    
    # Seção: Informações Gerais
    st.markdown("### 📍 Informações Gerais")
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Número de Municípios", len(gdf_filtrado))
    col2.metric("Nota Média", f"{gdf_filtrado['nota_media'].mean():.2f}")
    
    # Área Georreferenciável Total
    if 'area_georef' in gdf_filtrado.columns:
        area_total = gdf_filtrado['area_georef'].sum()
        area_total_fmt = f"{area_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        col3.metric("Área Georreferenciável (ha)", area_total_fmt)
    
    st.markdown("---")
    
    # Seção: Perímetro
    st.markdown("### 📏 Perímetro")
    col1, col2, col3 = st.columns(3)
    
    # Perímetro Georreferenciável Total (km)
    if 'perimetro_total_car' in gdf_filtrado.columns:
        perimetro_total = gdf_filtrado['perimetro_total_car'].sum()
        perimetro_total_fmt = f"{perimetro_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        col1.metric("Perímetro Georreferenciável (km)", perimetro_total_fmt)
    
    # Tamanho médio do imóvel (ha)
    if 'area_car_media' in gdf_filtrado.columns:
        tamanho_medio = gdf_filtrado['area_car_media'].mean()
        tamanho_medio_fmt = f"{tamanho_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        col2.metric("Tamanho Médio do Imóvel (ha)", tamanho_medio_fmt)
    
    # Perímetro médio do imóvel (km)
    if 'perimetro_medio_car' in gdf_filtrado.columns:
        perimetro_medio = gdf_filtrado['perimetro_medio_car'].mean()
        perimetro_medio_fmt = f"{perimetro_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        col3.metric("Perímetro Médio do Imóvel (km)", perimetro_medio_fmt)
    
    st.markdown("---")
    
    # Seção: Valores Totais
    st.markdown("### 💰 Valores Totais")
    col1, col2 = st.columns(2)
    
    # Valor total por área (R$)
    if 'valor_mun_area' in gdf_filtrado.columns:
        valor_area_total = gdf_filtrado['valor_mun_area'].sum()
        valor_area_total_fmt = f"R$ {valor_area_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        col1.metric("Valor Total por Área", valor_area_total_fmt)
    
    # Valor total por Perímetro (R$)
    if 'valor_mun_perim' in gdf_filtrado.columns:
        valor_perim_total = gdf_filtrado['valor_mun_perim'].sum()
        valor_perim_total_fmt = f"R$ {valor_perim_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        col2.metric("Valor Total por Perímetro", valor_perim_total_fmt)
    
    st.markdown("---")
    
    # Seção: Valores Médios
    st.markdown("### 📊 Valores Médios")
    col1, col2 = st.columns(2)
    
    # Valor médio por hectare (agregado)
    if 'valor_mun_area' in gdf_filtrado.columns and 'area_georef' in gdf_filtrado.columns:
        area_total = gdf_filtrado['area_georef'].sum()
        if area_total > 0:
            valor_medio_ha = gdf_filtrado['valor_mun_area'].sum() / area_total
            valor_medio_ha_fmt = f"R$ {valor_medio_ha:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            col1.metric("Valor Médio por Hectare", valor_medio_ha_fmt)
    
    # Valor médio por quilômetro (agregado)
    if 'valor_mun_perim' in gdf_filtrado.columns and 'perimetro_total_car' in gdf_filtrado.columns:
        perimetro_total = gdf_filtrado['perimetro_total_car'].sum()
        if perimetro_total > 0:
            valor_medio_km = gdf_filtrado['valor_mun_perim'].sum() / perimetro_total
            valor_medio_km_fmt = f"R$ {valor_medio_km:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            col2.metric("Valor Médio por Quilômetro", valor_medio_km_fmt)
    
    st.markdown("---")
    
    # Seção: Valores Mínimos e Máximos
    st.markdown("### 📈 Valores Mínimos e Máximos (por município)")
    
    # Calcular valor por hectare para cada município
    if 'valor_mun_area' in gdf_filtrado.columns and 'area_georef' in gdf_filtrado.columns:
        gdf_temp_ha = gdf_filtrado[gdf_filtrado['area_georef'] > 0].copy()
        if len(gdf_temp_ha) > 0:
            gdf_temp_ha['valor_por_ha'] = gdf_temp_ha['valor_mun_area'] / gdf_temp_ha['area_georef']
            
            col1, col2 = st.columns(2)
            
            # Valor mínimo por hectare
            valor_min_ha = gdf_temp_ha['valor_por_ha'].min()
            valor_min_ha_fmt = f"R$ {valor_min_ha:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            col1.metric("Valor Mínimo por Hectare", valor_min_ha_fmt)
            
            # Valor máximo por hectare
            valor_max_ha = gdf_temp_ha['valor_por_ha'].max()
            valor_max_ha_fmt = f"R$ {valor_max_ha:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            col2.metric("Valor Máximo por Hectare", valor_max_ha_fmt)
    
    # Calcular valor por quilômetro para cada município
    if 'valor_mun_perim' in gdf_filtrado.columns and 'perimetro_total_car' in gdf_filtrado.columns:
        gdf_temp_km = gdf_filtrado[gdf_filtrado['perimetro_total_car'] > 0].copy()
        if len(gdf_temp_km) > 0:
            gdf_temp_km['valor_por_km'] = gdf_temp_km['valor_mun_perim'] / gdf_temp_km['perimetro_total_car']
            
            col1, col2 = st.columns(2)
            
            # Valor mínimo por km
            valor_min_km = gdf_temp_km['valor_por_km'].min()
            valor_min_km_fmt = f"R$ {valor_min_km:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            col1.metric("Valor Mínimo por km", valor_min_km_fmt)
            
            # Valor máximo por km
            valor_max_km = gdf_temp_km['valor_por_km'].max()
            valor_max_km_fmt = f"R$ {valor_max_km:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            col2.metric("Valor Máximo por km", valor_max_km_fmt)
    
    st.markdown("---")