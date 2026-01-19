"""Componentes de visualização - mapas e gráficos."""

import folium
from folium.plugins import Fullscreen
from streamlit_folium import st_folium
import plotly.express as px
from branca.element import Template, MacroElement


def get_color(value, min_val, max_val, global_min=6, global_max=60):
    """Gerar cor baseada no valor normalizado.
    
    Args:
        value: Valor a ser colorido
        min_val: Valor mínimo no conjunto filtrado (não usado, mantido por compatibilidade)
        max_val: Valor máximo no conjunto filtrado (não usado, mantido por compatibilidade)
        global_min: Valor mínimo absoluto da escala (padrão: 6)
        global_max: Valor máximo absoluto da escala (padrão: 60)
    """
    # Sempre usar escala fixa de 6 a 60
    norm = (value - global_min) / (global_max - global_min)
    
    # Garantir que norm está entre 0 e 1
    norm = max(0, min(1, norm))
    
    # Novo gradiente: Verde escuro (#2a9104) → Amarelo (#ffe100) → Vermelho (#ff0000)
    # 0% = rgb(42, 145, 4), 40% = rgb(255, 225, 0), 100% = rgb(255, 0, 0)
    
    if norm <= 0.40:
        # Verde escuro para Amarelo (0-40%)
        factor = norm / 0.40
        r = int(42 + (255 - 42) * factor)
        g = int(145 + (225 - 145) * factor)
        b = int(4 * (1 - factor))
    else:
        # Amarelo para Vermelho (40-100%)
        factor = (norm - 0.40) / 0.60
        r = 255
        g = int(225 * (1 - factor))
        b = 0
    
    return f'#{r:02x}{g:02x}{b:02x}'


def criar_mapa(gdf_filtrado, criterio_sel, mostrar_controle_camadas=True, padding_zoom=30):
    """Criar mapa folium com dados filtrados.
    
    Args:
        gdf_filtrado: GeoDataFrame com dados filtrados
        criterio_sel: Critério selecionado (usado para grau de dificuldade)
        mostrar_controle_camadas: Mostrar ou não o controle de camadas
        padding_zoom: Padding para o zoom automático
    """
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
    
    # Criar duas camadas overlay (mas com comportamento mutuamente exclusivo): uma para cada tipo de visualização
    # Camada 1: Grau de Dificuldade
    layer_grau_dificuldade = folium.FeatureGroup(name='Grau de Dificuldade', show=True, control=True, overlay=True)
    
    # Adicionar polígonos para Grau de Dificuldade
    coluna_dados = criterio_sel
    global_min = 0
    global_max = 60
    min_val = gdf_filtrado[coluna_dados].min()
    max_val = gdf_filtrado[coluna_dados].max()
    
    for idx, row in gdf_filtrado.iterrows():
        color = get_color(row[coluna_dados], min_val, max_val, global_min, global_max)
        
        # Usar mun_nome se disponível, senão NM_MUN
        nome_municipio = row.get('mun_nome', row['NM_MUN'])
        
        # Criar tooltip simples com o nome do município
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
        
        # Adicionar GeoJson apenas com tooltip, sem popup
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
        ).add_to(layer_grau_dificuldade)
    
    # Adicionar a camada de Grau de Dificuldade ao mapa
    layer_grau_dificuldade.add_to(m)
    
    # Camada 2: % Área Georreferenciável
    layer_area_georef = folium.FeatureGroup(name='% Área Georreferenciável', show=False, control=True, overlay=True)
    
    # Adicionar polígonos para % Área Georreferenciável
    coluna_dados_georef = "percent_area_georef"
    global_min_georef = 0
    global_max_georef = 100
    min_val_georef = gdf_filtrado[coluna_dados_georef].min()
    max_val_georef = gdf_filtrado[coluna_dados_georef].max()
    
    for idx, row in gdf_filtrado.iterrows():
        color_georef = get_color(row[coluna_dados_georef], min_val_georef, max_val_georef, global_min_georef, global_max_georef)
        
        # Usar mun_nome se disponível, senão NM_MUN
        nome_municipio_georef = row.get('mun_nome', row['NM_MUN'])
        
        # Criar tooltip simples com o nome do município
        tooltip_georef = folium.Tooltip(
            nome_municipio_georef,
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
        
        # Adicionar GeoJson apenas com tooltip, sem popup
        folium.GeoJson(
            row['geometry'],
            style_function=lambda feature, color=color_georef: {
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
            tooltip=tooltip_georef
        ).add_to(layer_area_georef)
    
    # Adicionar a camada de % Área Georreferenciável ao mapa
    layer_area_georef.add_to(m)
    
    # Ajustar zoom automaticamente para os limites dos dados filtrados
    bounds = gdf_filtrado.total_bounds  # [minx, miny, maxx, maxy]
    m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]], padding=[padding_zoom, padding_zoom])
    
    # Gerar cores de exemplo para verificar o gradiente correto
    num_steps = 100
    gradient_colors = []
    for i in range(num_steps):
        norm = i / (num_steps - 1)
        
        # Novo gradiente: Verde escuro (#2a9104) → Amarelo (#ffe100) → Vermelho (#ff0000)
        if norm <= 0.40:
            # Verde escuro para Amarelo (0-40%)
            factor = norm / 0.40
            r = int(42 + (255 - 42) * factor)
            g = int(145 + (225 - 145) * factor)
            b = int(4 * (1 - factor))
        else:
            # Amarelo para Vermelho (40-100%)
            factor = (norm - 0.40) / 0.60
            r = 255
            g = int(225 * (1 - factor))
            b = 0
        
        gradient_colors.append(f'#{r:02x}{g:02x}{b:02x}')
    
    gradient_str = ', '.join(gradient_colors)
    
    # Criar duas legendas: uma para cada camada
    legend_grau_html = f'''
    <div id="legend-grau" style="position: fixed; 
                bottom: 50px; 
                left: 50px; 
                width: 200px; 
                background-color: white; 
                border: 2px solid grey; 
                border-radius: 5px;
                z-index: 9999; 
                font-size: 14px;
                padding: 10px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                display: block;">
        <p style="margin: 0 0 10px 0; font-weight: bold; text-align: center; font-size: 12px;">Grau de Dificuldade</p>
        <div style="background: linear-gradient(to right, {gradient_str}); 
                    height: 20px; 
                    border: 1px solid #333;
                    border-radius: 3px;"></div>
        <div style="display: flex; justify-content: space-between; margin-top: 5px; font-size: 11px;">
            <span>6.00</span>
            <span>60.00</span>
        </div>
    </div>
    '''
    
    legend_georef_html = f'''
    <div id="legend-georef" style="position: fixed; 
                bottom: 50px; 
                left: 50px; 
                width: 200px; 
                background-color: white; 
                border: 2px solid grey; 
                border-radius: 5px;
                z-index: 9999; 
                font-size: 14px;
                padding: 10px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                display: none;">
        <p style="margin: 0 0 10px 0; font-weight: bold; text-align: center; font-size: 12px;">% Área Georreferenciável</p>
        <div style="background: linear-gradient(to right, {gradient_str}); 
                    height: 20px; 
                    border: 1px solid #333;
                    border-radius: 3px;"></div>
        <div style="display: flex; justify-content: space-between; margin-top: 5px; font-size: 11px;">
            <span>0.00</span>
            <span>100.00</span>
        </div>
    </div>
    '''
    
    # Script JavaScript para alternar legendas conforme camadas ativas
    legend_toggle_script = '''
    <script>
    (function() {
        var grauInput = null;
        var georefInput = null;
        var isSetup = false;
        
        function updateLegends() {
            var legendGrau = document.getElementById('legend-grau');
            var legendGeoref = document.getElementById('legend-georef');
            
            if (legendGrau && grauInput) {
                legendGrau.style.display = grauInput.checked ? 'block' : 'none';
            }
            if (legendGeoref && georefInput) {
                legendGeoref.style.display = georefInput.checked ? 'block' : 'none';
            }
        }
        
        function setupLegends() {
            if (isSetup) return;
            
            // Buscar todos os inputs no controle de layers
            var allInputs = document.querySelectorAll('.leaflet-control-layers-overlays label');
            
            allInputs.forEach(function(label) {
                var span = label.querySelector('span');
                if (span) {
                    var text = span.textContent.trim();
                    var input = label.querySelector('input');
                    
                    if (text === 'Grau de Dificuldade') {
                        grauInput = input;
                    } else if (text === '% Área Georreferenciável') {
                        georefInput = input;
                    }
                }
            });
            
            if (!grauInput || !georefInput) return;
            
            // Adicionar listeners para atualizar legendas
            grauInput.addEventListener('change', function() {
                updateLegends();
            });
            
            georefInput.addEventListener('change', function() {
                updateLegends();
            });
            
            isSetup = true;
            updateLegends();
        }
        
        // Usar MutationObserver para detectar quando o controle é adicionado
        var observer = new MutationObserver(function(mutations) {
            setupLegends();
        });
        
        // Observar mudanças no body
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Tentar setup imediatamente também
        setTimeout(setupLegends, 500);
        setTimeout(setupLegends, 1000);
        setTimeout(setupLegends, 2000);
    })();
    </script>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_grau_html))
    m.get_root().html.add_child(folium.Element(legend_georef_html))
    m.get_root().html.add_child(folium.Element(legend_toggle_script))
    
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