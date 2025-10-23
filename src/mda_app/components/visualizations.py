"""Componentes de visualização - mapas e gráficos."""

import folium
from folium.plugins import Fullscreen
from streamlit_folium import st_folium
import plotly.express as px
from branca.element import Template, MacroElement


def get_color(value, min_val, max_val, global_min=0, global_max=60):
    """Gerar cor baseada no valor normalizado.
    
    Args:
        value: Valor a ser colorido
        min_val: Valor mínimo no conjunto filtrado
        max_val: Valor máximo no conjunto filtrado
        global_min: Valor mínimo absoluto da escala (padrão: 0)
        global_max: Valor máximo absoluto da escala (padrão: 60)
    """
    # Se min e max são iguais, usar escala global
    if max_val == min_val or (max_val - min_val) < 0.01:
        norm = (value - global_min) / (global_max - global_min)
    else:
        norm = (value - min_val) / (max_val - min_val)
    
    # Garantir que norm está entre 0 e 1
    norm = max(0, min(1, norm))
    
    if norm < 0.5:
        r = 0
        g = int(255 * (2 * norm))
        b = int(255 * (1 - 2 * norm))
    else:
        norm2 = 2 * (norm - 0.5)
        r = int(255 * norm2)
        g = int(255 * (1 - norm2))
        b = 0
    
    return f'#{r:02x}{g:02x}{b:02x}'


def criar_mapa(gdf_filtrado, criterio_sel, mostrar_controle_camadas=True, padding_zoom=30):
    """Criar mapa folium com dados filtrados."""
    # Calcular o centro dos dados
    centro_lat = gdf_filtrado.centroid.y.mean()
    centro_lon = gdf_filtrado.centroid.x.mean()
    
    # Criar mapa com zoom_start None para usar fit_bounds
    m = folium.Map(
        location=[centro_lat, centro_lon],
        tiles=None
    )
    
    # Adicionar camadas de tile - OpenStreetMap primeiro (será a padrão)
    folium.TileLayer(
        'OpenStreetMap',
        name='OpenStreetMap',
        overlay=False,
        control=True,
        show=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Imagem de Satélite',
        overlay=False,
        control=True,
        show=False
    ).add_to(m)
    
    # Valores mínimo e máximo do critério
    min_val = gdf_filtrado[criterio_sel].min()
    max_val = gdf_filtrado[criterio_sel].max()
    
    # Definir escala global (0 a 60 para notas)
    global_min = 0
    global_max = 60
    
    # Criar um FeatureGroup para agrupar todos os municípios (não aparece no controle de camadas)
    municipios_layer = folium.FeatureGroup(name='Municípios', show=True, control=False)
    
    # Adicionar polígonos ao mapa com ID único para capturar cliques
    for idx, row in gdf_filtrado.iterrows():
        color = get_color(row[criterio_sel], min_val, max_val, global_min, global_max)
        
        # Usar mun_nome se disponível, senão NM_MUN
        nome_municipio = row.get('mun_nome', row['NM_MUN'])
        
        # Criar tooltip discreto com o nome do município
        tooltip = folium.Tooltip(
            nome_municipio,
            sticky=False,
            style="""
                background-color: rgba(255, 255, 255, 0.95);
                border: 2px solid #0066cc;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 500;
                color: #333;
                box-shadow: 0 3px 6px rgba(0,0,0,0.3);
            """
        )
        
        # Adicionar ao FeatureGroup ao invés de adicionar diretamente ao mapa
        folium.GeoJson(
            row['geometry'],
            style_function=lambda feature, color=color: {
                'fillColor': color,
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.7,
            },
            highlight_function=lambda x: {
                'weight': 3,
                'color': '#0066cc',
                'fillOpacity': 0.9
            },
            tooltip=tooltip
        ).add_to(municipios_layer)
    
    # Adicionar o FeatureGroup ao mapa
    municipios_layer.add_to(m)
    
    # Ajustar zoom automaticamente para os limites dos dados filtrados
    bounds = gdf_filtrado.total_bounds  # [minx, miny, maxx, maxy]
    m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]], padding=[padding_zoom, padding_zoom])
    
    # Criar legenda com gradiente de cores
    # Gerar cores de exemplo para verificar o gradiente correto
    num_steps = 100
    gradient_colors = []
    for i in range(num_steps):
        norm = i / (num_steps - 1)
        if norm < 0.5:
            r = 0
            g = int(255 * (2 * norm))
            b = int(255 * (1 - 2 * norm))
        else:
            norm2 = 2 * (norm - 0.5)
            r = int(255 * norm2)
            g = int(255 * (1 - norm2))
            b = 0
        gradient_colors.append(f'#{r:02x}{g:02x}{b:02x}')
    
    gradient_str = ', '.join(gradient_colors)
    
    # Determinar valores para a legenda
    # Se há apenas um município ou valores muito próximos, usar escala global
    if max_val == min_val or (max_val - min_val) < 0.01:
        legend_min = global_min
        legend_max = global_max
    else:
        legend_min = min_val
        legend_max = max_val
    
    legend_html = f'''
    <div style="position: fixed; 
                bottom: 50px; 
                left: 50px; 
                width: 200px; 
                background-color: white; 
                border: 2px solid grey; 
                border-radius: 5px;
                z-index: 9999; 
                font-size: 14px;
                padding: 10px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.3);">
        <p style="margin: 0 0 10px 0; font-weight: bold; text-align: center; font-size: 12px;">Grau de Dificuldade</p>
        <div style="background: linear-gradient(to right, {gradient_str}); 
                    height: 20px; 
                    border: 1px solid #333;
                    border-radius: 3px;"></div>
        <div style="display: flex; justify-content: space-between; margin-top: 5px; font-size: 11px;">
            <span>{legend_min:.2f}</span>
            <span>{legend_max:.2f}</span>
        </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Adicionar controle de camadas (opcional)
    if mostrar_controle_camadas:
        folium.LayerControl().add_to(m)
    
    # Adicionar plugin de tela cheia
    Fullscreen().add_to(m)
    
    return m


def criar_histograma(gdf_filtrado, coluna, titulo):
    """Criar histograma com plotly."""
    fig = px.histogram(gdf_filtrado, x=coluna, nbins=15, title=titulo)
    return fig


def criar_scatter_plot(gdf_filtrado, x_col, y_col, titulo):
    """Criar gráfico de dispersão."""
    fig = px.scatter(gdf_filtrado, x=x_col, y=y_col, title=titulo, 
                     hover_data=['NM_MUN'])
    return fig


def criar_bar_chart(gdf_filtrado, x_col, y_col, titulo):
    """Criar gráfico de barras."""
    fig = px.bar(gdf_filtrado, x=x_col, y=y_col, title=titulo)
    return fig