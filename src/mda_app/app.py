"""Aplicação principal MDA Precificação de Áreas."""

import streamlit as st
import numpy as np
from mda_app.config.settings import APP_CONFIG
from mda_app.core.data_loader import carregar_dados, processar_dados_geograficos
from mda_app.components.ui_components import render_header, render_metrics
from mda_app.components.visualizations import criar_mapa, criar_histograma, criar_scatter_plot
from mda_app.utils.formatters import reais


def configurar_pagina():
    """Configurar página do Streamlit."""
    st.set_page_config(
        layout=APP_CONFIG["layout"],
        page_title=APP_CONFIG["page_title"],
        page_icon=APP_CONFIG["page_icon"]
    )


def configurar_sidebar_styles():
    """Configurar estilos da sidebar."""
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            background-color: #E5E5E5;
        }
        div[data-baseweb="select"] span {
            color: #006199;
            font-weight: 500;
        }
        .st-c1 {
            background-color:#E5E5E5;
        }
        div[data-baseweb="slider"] > div > div {
            background-color: black !important;
        }
        </style>
        """, unsafe_allow_html=True)


def criar_filtros_sidebar(gdf):
    """Criar filtros na sidebar."""
    # Filtro de UF
    ufs = gdf["SIGLA_UF"].unique()
    uf_sel = st.sidebar.multiselect("Seleção de Estado (UF)", options=ufs, default=list(ufs))
    
    # Filtro de Municípios (baseado nas UFs selecionadas)
    if uf_sel:
        # Filtrar municípios apenas das UFs selecionadas
        gdf_filtrado_uf = gdf[gdf["SIGLA_UF"].isin(uf_sel)]
        # Usar mun_nome se disponível, senão NM_MUN
        if 'mun_nome' in gdf_filtrado_uf.columns:
            municipios = sorted(gdf_filtrado_uf["mun_nome"].unique())
        else:
            municipios = sorted(gdf_filtrado_uf["NM_MUN"].unique())
        
        # Verificar se há município selecionado via clique no mapa
        default_municipios = []
        if 'municipio_selecionado_mapa' in st.session_state and st.session_state.municipio_selecionado_mapa:
            if st.session_state.municipio_selecionado_mapa in municipios:
                default_municipios = [st.session_state.municipio_selecionado_mapa]
                # Limpar session_state após usar
                st.session_state.municipio_selecionado_mapa = None
        
        # Multiselect com placeholder "Todos"
        municipios_sel = st.sidebar.multiselect(
            "Filtro de Municípios",
            options=municipios,
            default=default_municipios,
            placeholder="Todos os municípios",
            help="Deixe vazio para mostrar todos, ou selecione um ou mais municípios específicos"
        )
        
        # Se nenhum município selecionado, usar todos
        if not municipios_sel:
            municipios_sel = municipios
    else:
        municipios_sel = []
    
    # Critérios disponíveis
    criterios_labels = {
        "valor_medio": "Valor Médio",
        "valor_mun_perim": "Valor por Perímetro", 
        "valor_mun_area": "Valor por Área",
        "nota_media": "Nota Média",
        "nota_veg": "Vegetação",
        "nota_area": "Área Média dos Lotes CAR",
        "nota_relevo": "Relevo",
        "nota_insalub": "Insalubridade (Dengue)",
        "nota_insalub_2": "Insalubridade Ajustada",
        "nota_total_q1": "Precipitação - Trimestre 1",
        "nota_total_q2": "Precipitação - Trimestre 2", 
        "nota_total_q3": "Precipitação - Trimestre 3",
        "nota_total_q4": "Precipitação - Trimestre 4",
    }
    criterio_explicacao = {
        "valor_medio": "Média entre valor por perímetro e valor por área.",
        "nota_veg": "Nota relativa à vegetação do local. Calculada de acordo com a classe predominante no município (aberta, intermediária e fechada) e média de ocorrência de classe no intervalo.",
        "nota_area": "Nota relativa à área média de lotes CAR na área do município. Acima de 35ha, entre 15 e 35ha, até 15ha, conforme máximas e mínimas.",
        "nota_relevo": "Nota relativa ao relevo predominante no município.",
        "nota_insalub": "Nota relativa à insalubridade (casos de dengue por município). Distribuída conforme máximos e mínimos gerais.",
        "nota_insalub_2": "Nota relativa à insalubridade ajustada, incluindo incidência de ataques de animais peçonhentos.",
        "valor_mun_perim": "Valor total do município em relação ao perímetro total de imóveis CAR, utilizando dados do Quadro II da Tabela de Rendimento e Preço do Anexo I da INSTRUÇÃO NORMATIVA SEI/INCRA.",
        "valor_mun_area": "Valor total do município em relação à área georreferenciável.",
        "nota_media": "Média das notas utilizada para composição do valor final.",
        "nota_total_q1": "Nota total somada para o trimestre 1",
        "nota_total_q2": "Nota total somada para o trimestre 2",
        "nota_total_q3": "Nota total somada para o trimestre 3", 
        "nota_total_q4": "Nota total somada para o trimestre 4"
    }
    
    # Seleção de critério
    criterio_sel = st.sidebar.selectbox(
        "Selecione o critério para visualização", 
        options=list(criterio_explicacao.keys()),
        index=list(criterio_explicacao.keys()).index("nota_media")
    )
    
    # Slider do critério selecionado
    crit_min, crit_max = float(gdf[criterio_sel].min()), float(gdf[criterio_sel].max())
    crit_sel = st.sidebar.slider(
        f"{criterios_labels[criterio_sel]}", 
        crit_min, crit_max, 
        (crit_min, crit_max)
    )
    
    return uf_sel, municipios_sel, criterio_sel, crit_sel, criterios_labels, criterio_explicacao


def aplicar_filtros(gdf, uf_sel, municipios_sel, criterio_sel, crit_sel):
    """Aplicar filtros aos dados."""
    # Determinar qual coluna de nome usar
    coluna_nome = 'mun_nome' if 'mun_nome' in gdf.columns else 'NM_MUN'
    
    filtros = (
        gdf["SIGLA_UF"].isin(uf_sel) &
        gdf[coluna_nome].isin(municipios_sel) &
        gdf[criterio_sel].between(*crit_sel)
    )
    return gdf[filtros]


def main():
    """Função principal da aplicação."""
    configurar_pagina()
    configurar_sidebar_styles()
    
    # Renderizar cabeçalho
    render_header()
    
    # Carregar e processar dados
    gdf = carregar_dados()
    gdf = processar_dados_geograficos(gdf)
    
    # Criar filtros
    uf_sel, municipios_sel, criterio_sel, crit_sel, criterios_labels, criterio_explicacao = criar_filtros_sidebar(gdf)
    
    # Aplicar filtros
    gdf_filtrado = aplicar_filtros(gdf, uf_sel, municipios_sel, criterio_sel, crit_sel)
    
    # Verificar se há dados após aplicar filtros
    if len(gdf_filtrado) == 0:
        st.warning("⚠️ Nenhum município encontrado com os filtros selecionados. Por favor, ajuste os filtros.")
        st.stop()
    
    gdf_filtrado2 = gdf_filtrado.to_crs(epsg=5880)
    
    # Criar abas
    abas = st.tabs(["🌍 Mapa", "📌 Introdução"])
    
    # Aba Introdução (índice 1)
    with abas[1]:
        st.title("• Introdução")
        st.markdown("""
<p style="text-align: justify;">
"A partir do trabalho de elaboração e estabilização metodológica para o cálculo de estimativa de áreas a georreferenciar nos municípios do acordo judicial do desastre de Mariana, se faz necessário estimar, também, o valor de todo volume do serviço a ser realizado.
Para chegar ao valor estimado, foi utilizada a minuta de instrução normativa de referência SEI/INCRA – 20411255, dentro do sistema SEI.
Esta minuta estabelece critérios e parâmetros de cálculos para preços referenciais para execução de serviços geodésicos/cartográficos, para medição e demarcação de imóveis rurais em áreas sob jurisdição do INCRA.
A Tabela de Classificação estabelece, na minuta de Portaria, os critérios de pontuação para posterior comparação a tabela de Rendimento e Preço."\n

A presente entrega tem como resultado um arquivo em formato GeoPackage (.gpkg), contendo os valores discriminados de cada critério estabelecido na minuta, bem como os valores calculados para cada município. A precificação foi feita de acordo com a minuta de instrução normativa de referência SEI/INCRA – 20411255, disponível para download no fim da página. A produção dos dados foi realizada em banco de dados espacial PostGIS e em ambiente Python 3.12, visando garantir controle e reprodutibilidade dos resultados.
Os resultados aqui apresentados correspondem à entrega piloto para o estado de Alagoas, contemplando os critérios de Vegetação, Relevo, Insalubridade, Clima, Área e Acesso.\n

**Dados Utilizados**\n
Os dados utilizados para a composição da nota final foram obtidos a partir de APIs e plataformas online como DataSUS, Google Earth Engine (GEE), MapBiomas, BigQuery/INMET, entre outras.\n
**Critérios e Fontes**\n
**-Vegetação**\n
Os dados de vegetação foram obtidos na plataforma MapBiomas, sendo a nota por município calculada com base na vegetação predominante e na vegetação média.
Fonte: MapBiomas – Coleção 2 (beta) de Mapas Anuais de Cobertura e Uso da Terra do Brasil (10m de resolução espacial).
Link: Mapbiomas - https://brasil.mapbiomas.org/mapbiomas-cobertura-10m/.\n
**-Insalubridade**\n
Os dados de insalubridade foram obtidos na plataforma DataSUS, considerando as ocorrências de dengue registradas entre 2024 e 2025. As notas foram atribuídas a partir da distribuição entre valores máximos e mínimos observados.
Além disso, foi proposta a inclusão de uma nova métrica, também oriunda do DataSUS, referente a ocorrência de acidentes com animais peçonhentos, visando maior coerência com o contexto de trabalho de campo. Para essa métrica foi criado o campo insalub_2, no qual a distribuição apresentou comportamento mais próximo de uma normal em comparação ao uso exclusivo da dengue.
Fonte: DataSUS – Transferência de Arquivos - https://datasus.saude.gov.br/transferencia-de-arquivos/#.\n
**-Relevo**\n
O relevo foi classificado a partir de dados raster do Modelo Digital de Elevação SRTM (30m), obtidos via API do Google Earth Engine (GEE). Com base nos dados de altitude, foi calculada a inclinação do terreno, posteriormente classificada segundo a tipologia de Lepsch (1983). As notas foram atribuídas considerando a classe predominante de relevo e a média das classes.
Fonte: USGS SRTM 30m – Google Earth Engine
Link: https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003?hl=pt-br.\n
**-Clima**\n
Os dados de clima foram obtidos por meio da plataforma BigQuery do INMET, aplicando-se krigagem ordinária sobre séries históricas de estações meteorológicas brasileiras dos últimos 25 anos. As notas foram atribuídas com base na distribuição de temperaturas máximas e mínimas.
Propõe-se ainda a atribuição de notas por trimestre, permitindo expressar com maior precisão a sazonalidade da pluviosidade.
Exemplo de implementação da krigagem:\n
OK = OrdinaryKriging(
x, y, z,
variogram_model='spherical',
verbose=False,
enable_plotting=False
)\n
Fonte: BigQuery - https://console.cloud.google.com/bigquery?p=basedosdados.\n
**-Área**\n
A nota referente à área média de lotes foi calculada a partir da média das áreas dos assentamentos do CAR que se encontram total ou parcialmente dentro de cada município, de modo a reduzir desvios estatísticos nas médias.
Fonte: Base de dados Zetta.\n
**-Acesso**\n
Para este critério, foi atribuída nota única (1) a todos os municípios, uma vez que todos possuem acesso por vias rodoviárias.\n
**- Auxiliares**\n
Shapefile de municípios do Brasil e estimativa populacional por município. Fonte: IBGE. \n
Dados fundiários e territoriais (CAR, SIGEF, Terras da União, UCs, TIs). Fonte: Base de dados Zetta.\n
**Dicionário de dados**\n

**CD_MUN**: Código do município (IBGE).
**NM_MUN**: Nome do município (IBGE).
**SIGLA_UF**: Sigla da unidade federativa (IBGE).
**ckey**: Chave composta contendo nome + unidade federativa do município.
**populacao**: Numero de indivíduos residentes no município segundo estimativa do IBGE.
**geometry**: Coluna de geometrias.
**nota_veg**: Nota relativa à vegetação do local. Calculada de acordo com classe
predominante no município (aberta, intermediária e fechada) e nota específica com média de ocorrência de classe no intervalo.
**nota_area**: Nota relativa à área média de Lotes CAR na área do município (Acima de 35ha, acima de 15 até 35 ha, até 15 ha), atribuindo-se as notas em cada intervalo de acordo com máximas e mínimas.
**nota relevo**: Nota relativa ao relevo predominante no município.
**nota_p_qx**: Notas relativas à quantidade de precipitação no município por trimestre (..._q1, ..._q2, ..._q3, ..._q4). Notas distribuídas de acordo com máximas e mínimas gerais.
**nota_insalub**: Nota relativa à insalubridade (casos de dengue por município). Notas distribuídas de acordo com máximas e mínimas gerais.
**nota_insalub2**: Nota relativa à insalubridade ajustada, incluindo-se incidência de ataque de animais peçonhentos. Notas distribuídas de acordo com máximas e mínimas gerais.
**area_cidade**: Área total do município.
**area_georef**: Área total georreferenciável do município, excluindo-se: Terras indígenas, Terras da União, Unidades de Conservação, SIGEF.
**percent_area_georef**: Percentual de área georreferenciável em relação à área do município.
**num_imoveis**: Número de imóveis do CAR presentes no município.
**area_car_total**: Área total de imóveis CAR no município.
**area_car_media**: Área média de imóveis CAR no município.
**perimetro_total_car**: Perímetro somado de todos os imóveis CAR no município.
**perimetro_medio_car**: Perímetro médio de imóveis CAR no município.
**area_max_perim**: Área máxima alcançável de acordo com perímetro médio. Serve para avaliar a relação média entre perímetro e área dos imóveis do município.
**nota_total_qx**: Nota total somada para o trimestre 'x' (...q1, ...q2, etc)
**nota_media**: Média das notas utilizada para composição do valor final.
**valor_mun_perim**: Valor total do município em relação ao perímetro total de imóveis car, utilizando-se os dados do Quadro II - Tabela de Rendimento e Preço do Anexo I da Instrução Normativa Minuta SEI/INCRA.
**valor_mun_area**: Valor total do município em relação à área georreferenciável. </p>
    """, unsafe_allow_html=True)

        url = "https://raw.githubusercontent.com/victor-arantes/mda-app/main/dados/mi_normref_incra_20411255.pdf"
        st.markdown('''
    **Downloads**''')
        st.markdown(f'[📑Minuta de Instrução Normativa de Referência SEI/INCRA – 20411255]({url})')
    
    # Aba Mapa (índice 0)
    with abas[0]:
        # Verificar se há município destacado no session_state
        municipio_clicado_alt = None
        nome_municipio_clicado = None
        
        # Criar mapa
        m = criar_mapa(gdf_filtrado, criterio_sel, mostrar_controle_camadas=True)
        
        # Se há município destacado no session_state, adicionar borda vermelha
        if 'municipio_destacado' in st.session_state and st.session_state.municipio_destacado:
            try:
                import folium
                # Encontrar o município no gdf_filtrado
                if 'mun_nome' in gdf_filtrado.columns:
                    municipio_row = gdf_filtrado[gdf_filtrado['mun_nome'] == st.session_state.municipio_destacado]
                else:
                    municipio_row = gdf_filtrado[gdf_filtrado['NM_MUN'] == st.session_state.municipio_destacado]
                
                if len(municipio_row) > 0:
                    municipio_clicado_alt = municipio_row.iloc[0]
                    # Adicionar polígono de destaque com borda vermelha grossa
                    folium.GeoJson(
                        municipio_clicado_alt['geometry'],
                        style_function=lambda x: {
                            'fillColor': 'transparent',
                            'color': '#FF0000',
                            'weight': 5,
                            'fillOpacity': 0,
                            'dashArray': '10, 5'
                        },
                        name="destaque"
                    ).add_to(m)
            except:
                pass
        
        from streamlit_folium import st_folium
        map_data_alt = st_folium(
            m, 
            width=None, 
            height=500, 
            returned_objects=["last_object_clicked"],
            key=f"mapa_alternativa_{len(gdf_filtrado)}_{criterio_sel}"
        )
        
        st.markdown("---")
        
        # Verificar se há município clicado
        if map_data_alt and map_data_alt.get("last_object_clicked"):
            clicked_data = map_data_alt["last_object_clicked"]
            if clicked_data:
                try:
                    from shapely.geometry import Point
                    clicked_point = Point(clicked_data.get("lng", 0), clicked_data.get("lat", 0))
                    for idx, row in gdf_filtrado.iterrows():
                        if row['geometry'].contains(clicked_point):
                            nome_municipio_clicado = row.get('mun_nome', row['NM_MUN'])
                            
                            # Verificar se é um NOVO clique (diferente do anterior)
                            ultimo_clique = st.session_state.get('ultimo_municipio_clicado', None)
                            if ultimo_clique != nome_municipio_clicado:
                                # É um novo clique - salvar e recarregar
                                st.session_state.municipio_selecionado_mapa = nome_municipio_clicado
                                st.session_state.municipio_destacado = nome_municipio_clicado
                                st.session_state.ultimo_municipio_clicado = nome_municipio_clicado
                                st.rerun()
                            else:
                                # Mesmo município - apenas atualizar a variável local
                                municipio_clicado_alt = row
                            break
                except:
                    pass
        
        # Se houver município clicado, usar seus dados; senão, usar dados agregados
        if municipio_clicado_alt is not None:
            # Usar mun_nome se disponível
            nome_municipio = municipio_clicado_alt.get('mun_nome', municipio_clicado_alt['NM_MUN'])
            st.markdown(f"### 📊 Estatísticas - {nome_municipio}")
        else:
            st.markdown("### 📊 Estatísticas")
        
        # Linha 1: Informações Gerais
        col1, col2, col3, col4 = st.columns(4)
        
        if municipio_clicado_alt is not None:
            # Dados do município clicado
            col1.metric("Município", municipio_clicado_alt.get('mun_nome', municipio_clicado_alt['NM_MUN']))
            col2.metric("Nota Média", f"{municipio_clicado_alt['nota_media']:.2f}")
            
            if 'area_georef' in municipio_clicado_alt:
                area_fmt = f"{municipio_clicado_alt['area_georef']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                col3.metric("Área (ha)", area_fmt)
            
            if 'perimetro_total_car' in municipio_clicado_alt:
                perimetro_fmt = f"{municipio_clicado_alt['perimetro_total_car']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                col4.metric("Perímetro (km)", perimetro_fmt)
        else:
            # Dados agregados
            col1.metric("Municípios", len(gdf_filtrado))
            col2.metric("Nota Média", f"{gdf_filtrado['nota_media'].mean():.2f}")
        
        
        if municipio_clicado_alt is None:
            # Dados agregados - só mostrar quando não há município clicado
            if 'area_georef' in gdf_filtrado.columns:
                area_total = gdf_filtrado['area_georef'].sum()
                area_fmt = f"{area_total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                col3.metric("Área Total (ha)", area_fmt)
            
            if 'perimetro_total_car' in gdf_filtrado.columns:
                perimetro_total = gdf_filtrado['perimetro_total_car'].sum()
                perimetro_fmt = f"{perimetro_total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                col4.metric("Perímetro Total (km)", perimetro_fmt)
        
        # Linha 2: Valores
        col1, col2, col3, col4 = st.columns(4)
        
        if municipio_clicado_alt is not None:
            # Dados do município clicado
            if 'valor_mun_area' in municipio_clicado_alt:
                valor_area_fmt = f"R$ {municipio_clicado_alt['valor_mun_area']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                col1.metric("Valor - Área", valor_area_fmt)
            
            if 'valor_mun_perim' in municipio_clicado_alt:
                valor_perim_fmt = f"R$ {municipio_clicado_alt['valor_mun_perim']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                col2.metric("Valor - Perímetro", valor_perim_fmt)
            
            # Valor por hectare
            if 'valor_mun_area' in municipio_clicado_alt and 'area_georef' in municipio_clicado_alt:
                if municipio_clicado_alt['area_georef'] > 0:
                    valor_ha = municipio_clicado_alt['valor_mun_area'] / municipio_clicado_alt['area_georef']
                    valor_ha_fmt = f"R$ {valor_ha:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    col3.metric("Valor/ha", valor_ha_fmt)
            
            # Valor por quilômetro
            if 'valor_mun_perim' in municipio_clicado_alt and 'perimetro_total_car' in municipio_clicado_alt:
                if municipio_clicado_alt['perimetro_total_car'] > 0:
                    valor_km = municipio_clicado_alt['valor_mun_perim'] / municipio_clicado_alt['perimetro_total_car']
                    valor_km_fmt = f"R$ {valor_km:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    col4.metric("Valor/km", valor_km_fmt)
        else:
            # Dados agregados
            if 'valor_mun_area' in gdf_filtrado.columns:
                valor_area = gdf_filtrado['valor_mun_area'].sum()
                valor_area_fmt = f"R$ {valor_area:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                col1.metric("Valor Total - Área", valor_area_fmt)
            
            if 'valor_mun_perim' in gdf_filtrado.columns:
                valor_perim = gdf_filtrado['valor_mun_perim'].sum()
                valor_perim_fmt = f"R$ {valor_perim:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                col2.metric("Valor Total - Perímetro", valor_perim_fmt)
            
            # Valor médio por hectare
            if 'valor_mun_area' in gdf_filtrado.columns and 'area_georef' in gdf_filtrado.columns:
                area_total = gdf_filtrado['area_georef'].sum()
                if area_total > 0:
                    valor_medio_ha = gdf_filtrado['valor_mun_area'].sum() / area_total
                    valor_medio_ha_fmt = f"R$ {valor_medio_ha:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    col3.metric("Valor Médio/ha", valor_medio_ha_fmt)
            
            # Valor médio por quilômetro
            if 'valor_mun_perim' in gdf_filtrado.columns and 'perimetro_total_car' in gdf_filtrado.columns:
                perimetro_total = gdf_filtrado['perimetro_total_car'].sum()
                if perimetro_total > 0:
                    valor_medio_km = gdf_filtrado['valor_mun_perim'].sum() / perimetro_total
                    valor_medio_km_fmt = f"R$ {valor_medio_km:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    col4.metric("Valor Médio/km", valor_medio_km_fmt)
        
        # Linha 3: Tamanhos Médios
        col1, col2, col3, col4 = st.columns(4)
        
        if municipio_clicado_alt is not None:
            # Dados do município clicado
            if 'area_car_media' in municipio_clicado_alt:
                tamanho_fmt = f"{municipio_clicado_alt['area_car_media']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                col1.metric("Tamanho Médio Imóvel (ha)", tamanho_fmt)
            
            if 'perimetro_medio_car' in municipio_clicado_alt:
                perimetro_medio_fmt = f"{municipio_clicado_alt['perimetro_medio_car']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                col2.metric("Perímetro Médio Imóvel (km)", perimetro_medio_fmt)
            
            # Para município individual, não mostrar Min/Max (são os mesmos valores)
            if 'valor_mun_area' in municipio_clicado_alt and 'area_georef' in municipio_clicado_alt:
                if municipio_clicado_alt['area_georef'] > 0:
                    valor_ha = municipio_clicado_alt['valor_mun_area'] / municipio_clicado_alt['area_georef']
                    valor_fmt = f"R$ {valor_ha:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    col3.metric("Valor/ha", valor_fmt)
        else:
            # Dados agregados
            if 'area_car_media' in gdf_filtrado.columns:
                tamanho_medio = gdf_filtrado['area_car_media'].mean()
                tamanho_fmt = f"{tamanho_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                col1.metric("Tamanho Médio Imóvel (ha)", tamanho_fmt)
            
            if 'perimetro_medio_car' in gdf_filtrado.columns:
                perimetro_medio = gdf_filtrado['perimetro_medio_car'].mean()
                perimetro_medio_fmt = f"{perimetro_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                col2.metric("Perímetro Médio Imóvel (km)", perimetro_medio_fmt)
            
            # Valores Min/Max por hectare
            if 'valor_mun_area' in gdf_filtrado.columns and 'area_georef' in gdf_filtrado.columns:
                gdf_temp = gdf_filtrado[gdf_filtrado['area_georef'] > 0].copy()
                if len(gdf_temp) > 0:
                    gdf_temp['valor_por_ha'] = gdf_temp['valor_mun_area'] / gdf_temp['area_georef']
                    
                    valor_min = gdf_temp['valor_por_ha'].min()
                    valor_min_fmt = f"R$ {valor_min:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    col3.metric("Valor Mín/ha", valor_min_fmt)
                    
                    valor_max = gdf_temp['valor_por_ha'].max()
                    valor_max_fmt = f"R$ {valor_max:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    col4.metric("Valor Máx/ha", valor_max_fmt)
        
        st.markdown("---")
        
        # Gráficos antes da tabela
        col_grafico1, col_grafico2 = st.columns(2)
        
        with col_grafico1:
            st.markdown("#### 📊 Notas por Trimestre")
            # Se houver município clicado, mostrar dados dele; senão, médias gerais
            if municipio_clicado_alt is not None:
                import plotly.graph_objects as go
                
                trimestres = ['Q1', 'Q2', 'Q3', 'Q4']
                valores = [
                    municipio_clicado_alt.get('nota_total_q1', 0),
                    municipio_clicado_alt.get('nota_total_q2', 0),
                    municipio_clicado_alt.get('nota_total_q3', 0),
                    municipio_clicado_alt.get('nota_total_q4', 0)
                ]
                
                fig_barras = go.Figure(data=[
                    go.Bar(
                        x=trimestres, 
                        y=valores,
                        marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'],
                        text=[f'{v:.2f}' for v in valores],
                        textposition='auto',
                    )
                ])
                
                fig_barras.update_layout(
                    yaxis_title='Nota Total',
                    xaxis_title='Trimestre',
                    height=300,
                    showlegend=False,
                    margin=dict(l=40, r=40, t=40, b=40)
                )
                
                st.plotly_chart(fig_barras, use_container_width=True)
            else:
                # Mostrar médias gerais
                import plotly.graph_objects as go
                
                trimestres = ['Q1', 'Q2', 'Q3', 'Q4']
                valores = [
                    gdf_filtrado['nota_total_q1'].mean() if 'nota_total_q1' in gdf_filtrado.columns else 0,
                    gdf_filtrado['nota_total_q2'].mean() if 'nota_total_q2' in gdf_filtrado.columns else 0,
                    gdf_filtrado['nota_total_q3'].mean() if 'nota_total_q3' in gdf_filtrado.columns else 0,
                    gdf_filtrado['nota_total_q4'].mean() if 'nota_total_q4' in gdf_filtrado.columns else 0
                ]
                
                fig_barras = go.Figure(data=[
                    go.Bar(
                        x=trimestres, 
                        y=valores,
                        marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'],
                        text=[f'{v:.2f}' for v in valores],
                        textposition='auto',
                    )
                ])
                
                fig_barras.update_layout(
                    yaxis_title='Nota Total (Média)',
                    xaxis_title='Trimestre',
                    height=300,
                    showlegend=False,
                    margin=dict(l=40, r=40, t=40, b=40)
                )
                
                st.plotly_chart(fig_barras, use_container_width=True)
        
        with col_grafico2:
            st.markdown("#### 📏 Percentagem Área Georref")
            
            # Calcular percentagem de área georreferenciável da coluna percent_area_georef
            if municipio_clicado_alt is not None:
                # Para município individual - usar a coluna percent_area_georef
                if 'percent_area_georef' in municipio_clicado_alt:
                    percentual = float(municipio_clicado_alt['percent_area_georef'])
                else:
                    percentual = 0.0
            else:
                # Para agregado - média dos percentuais
                if 'percent_area_georef' in gdf_filtrado.columns:
                    percentual = float(gdf_filtrado['percent_area_georef'].mean())
                else:
                    percentual = 0.0
            
            import plotly.graph_objects as go
            
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=percentual,
                domain={'x': [0, 1], 'y': [0, 1]},
                number={'suffix': "%", 'font': {'size': 40}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "rgba(0,0,0,0)"},  # Barra invisível
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 25], 'color': '#27ae60'},      # Verde escuro
                        {'range': [25, 50], 'color': '#2ecc71'},     # Verde claro
                        {'range': [50, 75], 'color': '#f1c40f'},     # Amarelo
                        {'range': [75, 90], 'color': '#e67e22'},     # Laranja
                        {'range': [90, 100], 'color': '#e74c3c'}     # Vermelho
                    ],
                    'threshold': {
                        'line': {'color': "darkblue", 'width': 4},
                        'thickness': 0.75,
                        'value': percentual
                    }
                }
            ))
            
            fig_gauge.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        st.markdown("---")
        
        # Tabela de Municípios
        st.markdown("### 📄 Tabela de Municípios")
        colunas_excluir = ["geometry"]
        if "fid" in gdf_filtrado.columns:
            colunas_excluir.append("fid")
        st.dataframe(gdf_filtrado.drop(columns=colunas_excluir), use_container_width=True)


if __name__ == "__main__":
    main()



if __name__ == "__main__":
    main()