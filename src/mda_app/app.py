"""Aplicação principal MDA Precificação de Áreas."""

import streamlit as st
import numpy as np
from mda_app.config.settings import APP_CONFIG
from mda_app.core.data_loader import carregar_dados, processar_dados_geograficos
from mda_app.components.ui_components import render_header, render_metrics
from mda_app.components.visualizations import criar_mapa, criar_histograma, criar_scatter_plot
from mda_app.utils.formatters import reais


def calcular_valor_por_nota(pontuacao, area):
    """Calcula valor baseado na pontuação e área."""
    if pontuacao <= 15:
        return area * 49.83
    elif pontuacao <= 25:
        return area * 59.80
    elif pontuacao <= 35:
        return area * 104.78
    elif pontuacao <= 45:
        return area * 134.88
    elif pontuacao <= 55:
        return area * 164.95
    else:
        return area * 202.87


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
        
        # Inicializar estado de municípios selecionados
        if 'municipios_selecionados' not in st.session_state:
            st.session_state.municipios_selecionados = []
        
        # Multiselect com placeholder "Todos"
        municipios_sel = st.sidebar.multiselect(
            "Filtro de Municípios",
            options=municipios,
            default=st.session_state.municipios_selecionados,
            placeholder="Todos os municípios",
            help="Deixe vazio para mostrar todos, ou selecione um ou mais municípios específicos.",
            key="multiselect_municipios"
        )
        
        # Atualizar session_state apenas se houver mudança real
        if municipios_sel != st.session_state.municipios_selecionados:
            st.session_state.municipios_selecionados = municipios_sel
        
        # Seção de Adição Rápida - Mostrar apenas se não filtrado
        if not municipios_sel or len(municipios_sel) < len(municipios):
            st.sidebar.markdown("---")
            st.sidebar.markdown("**⚡ Adicionar Rápido ao Filtro**")
            
            # Mostrar municípios não selecionados como botões
            municipios_nao_selecionados = [m for m in municipios if m not in st.session_state.municipios_selecionados]
            
            # Limitar a 10 primeiros para não sobrecarregar
            if len(municipios_nao_selecionados) > 0:
                num_mostrar = min(10, len(municipios_nao_selecionados))
                st.sidebar.caption(f"Mostrando {num_mostrar} de {len(municipios_nao_selecionados)} municípios disponíveis")
                
                # Criar 2 colunas para botões
                cols = st.sidebar.columns(2)
                for i, municipio in enumerate(municipios_nao_selecionados[:num_mostrar]):
                    col_idx = i % 2
                    with cols[col_idx]:
                        if st.button(f"➕ {municipio[:15]}...", key=f"add_{municipio}", use_container_width=True):
                            if municipio not in st.session_state.municipios_selecionados:
                                st.session_state.municipios_selecionados.append(municipio)
                                st.rerun()

        
        # Se nenhum município selecionado, usar todos
        if not municipios_sel:
            municipios_sel = municipios
    else:
        municipios_sel = []
    
    # Critério fixo em nota_media para melhor performance
    criterio_sel = "nota_media"
    
    # Slider do critério (Grau de Dificuldade Médio)
    crit_min, crit_max = float(gdf[criterio_sel].min()), float(gdf[criterio_sel].max())
    crit_sel = st.sidebar.slider(
        "Grau de Dificuldade Médio", 
        crit_min, crit_max, 
        (crit_min, crit_max)
    )
    
    return uf_sel, municipios_sel, criterio_sel, crit_sel


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
    uf_sel, municipios_sel, criterio_sel, crit_sel = criar_filtros_sidebar(gdf)
    
    # Aplicar filtros
    gdf_filtrado = aplicar_filtros(gdf, uf_sel, municipios_sel, criterio_sel, crit_sel)
    
    # Verificar se há dados após aplicar filtros
    if len(gdf_filtrado) == 0:
        st.warning("⚠️ Nenhum município encontrado com os filtros selecionados. Por favor, ajuste os filtros.")
        st.stop()
    
    gdf_filtrado2 = gdf_filtrado.to_crs(epsg=5880)
    
    # Criar abas
    abas = st.tabs(["Mapa", "Introdução"])
    
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
        # Criar mapa simples sem interação de cliques
        m = criar_mapa(gdf_filtrado, criterio_sel, mostrar_controle_camadas=True)
        
        from streamlit_folium import st_folium
        
        # A chave do mapa muda apenas quando UFs mudam
        mapa_key = f"mapa_{'_'.join(sorted(uf_sel))}"
        
        # Renderizar mapa sem captura de cliques
        st_folium(
            m, 
            width=None, 
            height=500, 
            key=mapa_key
        )
        
        st.markdown("---")
        
        # Estatísticas - mostrar dados agregados ou de município específico se houver apenas 1 no filtro
        if len(gdf_filtrado) == 1:
            # Um único município selecionado - mostrar dados específicos
            municipio_especifico = gdf_filtrado.iloc[0]
            nome_municipio = municipio_especifico.get('mun_nome', municipio_especifico['NM_MUN'])
            st.markdown(f"<h3 style='text-align: center;'>Informações Adicionais - {nome_municipio}</h3>", unsafe_allow_html=True)
        else:
            # Múltiplos municípios - mostrar dados agregados
            st.markdown("<h3 style='text-align: center;'>Informações Adicionais</h3>", unsafe_allow_html=True)
        
        # Linha 1: 5 colunas
        col1, col2, col3, col4, col5 = st.columns(5)
        
        if len(gdf_filtrado) == 1:
            # Dados do município específico
            municipio_especifico = gdf_filtrado.iloc[0]
            
            if 'area_georef' in municipio_especifico:
                area_fmt = f"{municipio_especifico['area_georef']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                col1.metric("Área total do Município (ha)", area_fmt)
            
            if 'perimetro_total_car' in municipio_especifico:
                perimetro_fmt = f"{municipio_especifico['perimetro_total_car']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                col2.metric("Perímetro Georreferencial do Município (km)", perimetro_fmt)
            
            if 'area_car_media' in municipio_especifico:
                tamanho_fmt = f"{municipio_especifico['area_car_media']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                col3.metric("Tamanho Médio Imóvel CAR (ha)", tamanho_fmt)
            
            if 'perimetro_medio_car' in municipio_especifico:
                perimetro_medio_fmt = f"{municipio_especifico['perimetro_medio_car']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                col4.metric("Perímetro Médio Imóvel CAR (km)", perimetro_medio_fmt)
            
            # Valor médio por hectare
            if 'valor_mun_area' in municipio_especifico and 'area_georef' in municipio_especifico:
                if municipio_especifico['area_georef'] > 0:
                    valor_ha = municipio_especifico['valor_mun_area'] / municipio_especifico['area_georef']
                    valor_fmt = f"R$ {valor_ha:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    col5.metric("Valor Médio/ha", valor_fmt)
        else:
            # Dados agregados
            if 'area_georef' in gdf_filtrado.columns:
                area_total = gdf_filtrado['area_georef'].sum()
                area_fmt = f"{area_total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                col1.metric("Área Total (ha)", area_fmt)
            
            if 'perimetro_total_car' in gdf_filtrado.columns:
                perimetro_total = gdf_filtrado['perimetro_total_car'].sum()
                perimetro_fmt = f"{perimetro_total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
                col2.metric("Perímetro Total Georreferenciável (km)", perimetro_fmt)
            
            if 'area_car_media' in gdf_filtrado.columns:
                tamanho_medio = gdf_filtrado['area_car_media'].mean()
                tamanho_fmt = f"{tamanho_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                col3.metric("Tamanho Médio Imóvel CAR (ha)", tamanho_fmt)
            
            if 'perimetro_medio_car' in gdf_filtrado.columns:
                perimetro_medio = gdf_filtrado['perimetro_medio_car'].mean()
                perimetro_medio_fmt = f"{perimetro_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                col4.metric("Perímetro Médio Imóvel CAR (km)", perimetro_medio_fmt)
            
            # Valor médio por hectare
            if 'valor_mun_area' in gdf_filtrado.columns and 'area_georef' in gdf_filtrado.columns:
                gdf_temp = gdf_filtrado[gdf_filtrado['area_georef'] > 0].copy()
                if len(gdf_temp) > 0:
                    gdf_temp['valor_por_ha'] = gdf_temp['valor_mun_area'] / gdf_temp['area_georef']
                    valor_medio_ha = gdf_temp['valor_por_ha'].mean()
                    valor_medio_fmt = f"R$ {valor_medio_ha:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    col5.metric("Valor Médio/ha", valor_medio_fmt)
        
        # Linha 2: 5 colunas
        col1, col2, col3, col4, col5 = st.columns(5)
        
        if len(gdf_filtrado) == 1:
            # Dados do município específico
            municipio_especifico = gdf_filtrado.iloc[0]
            
            # Valor médio por quilômetro
            if 'valor_mun_perim' in municipio_especifico and 'perimetro_total_car' in municipio_especifico:
                if municipio_especifico['perimetro_total_car'] > 0:
                    valor_km = municipio_especifico['valor_mun_perim'] / municipio_especifico['perimetro_total_car']
                    valor_km_fmt = f"R$ {valor_km:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    col1.metric("Valor Médio/km", valor_km_fmt)
        else:
            # Dados agregados
            # Valor médio por quilômetro
            if 'valor_mun_perim' in gdf_filtrado.columns and 'perimetro_total_car' in gdf_filtrado.columns:
                gdf_temp = gdf_filtrado[gdf_filtrado['perimetro_total_car'] > 0].copy()
                if len(gdf_temp) > 0:
                    gdf_temp['valor_por_km'] = gdf_temp['valor_mun_perim'] / gdf_temp['perimetro_total_car']
                    valor_medio_km = gdf_temp['valor_por_km'].mean()
                    valor_medio_km_fmt = f"R$ {valor_medio_km:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    col1.metric("Valor Médio/km", valor_medio_km_fmt)
            
            # Valores Min/Max por hectare
            if 'valor_mun_area' in gdf_filtrado.columns and 'area_georef' in gdf_filtrado.columns:
                gdf_temp = gdf_filtrado[gdf_filtrado['area_georef'] > 0].copy()
                if len(gdf_temp) > 0:
                    gdf_temp['valor_por_ha'] = gdf_temp['valor_mun_area'] / gdf_temp['area_georef']
                    
                    valor_min = gdf_temp['valor_por_ha'].min()
                    valor_min_fmt = f"R$ {valor_min:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    col2.metric("Valor Mínimo/ha", valor_min_fmt)
                    
                    valor_max = gdf_temp['valor_por_ha'].max()
                    valor_max_fmt = f"R$ {valor_max:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    col3.metric("Valor Máximo/ha", valor_max_fmt)
            
            # Valores Min/Max por quilômetro
            if 'valor_mun_perim' in gdf_filtrado.columns and 'perimetro_total_car' in gdf_filtrado.columns:
                gdf_temp = gdf_filtrado[gdf_filtrado['perimetro_total_car'] > 0].copy()
                if len(gdf_temp) > 0:
                    gdf_temp['valor_por_km'] = gdf_temp['valor_mun_perim'] / gdf_temp['perimetro_total_car']
                    
                    valor_min_km = gdf_temp['valor_por_km'].min()
                    valor_min_km_fmt = f"R$ {valor_min_km:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    col4.metric("Valor Mínimo/km", valor_min_km_fmt)
                    
                    valor_max_km = gdf_temp['valor_por_km'].max()
                    valor_max_km_fmt = f"R$ {valor_max_km:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    col5.metric("Valor Máximo/km", valor_max_km_fmt)
        
        st.markdown("---")
        
        # Gráficos antes da tabela
        col_grafico1, col_grafico2 = st.columns(2)
        
        with col_grafico1:
            st.markdown("<h4 style='text-align: center;'>Grau de Dificuldade por Trimestre</h4>", unsafe_allow_html=True)
            # Se houver município único, mostrar dados dele; senão, médias gerais
            if len(gdf_filtrado) == 1:
                import plotly.graph_objects as go
                municipio_especifico = gdf_filtrado.iloc[0]
                
                trimestres = ['Trimestre 1', 'Trimestre 2', 'Trimestre 3', 'Trimestre 4']
                valores = [
                    municipio_especifico.get('nota_total_q1', 0),
                    municipio_especifico.get('nota_total_q2', 0),
                    municipio_especifico.get('nota_total_q3', 0),
                    municipio_especifico.get('nota_total_q4', 0)
                ]
                
                fig_barras = go.Figure(data=[
                    go.Bar(
                        x=trimestres, 
                        y=valores,
                        marker_color=['#6C9BCF', '#8BB8E8', '#A9CCE3', '#C5DEDD'],
                        text=[f'{v:.2f}' for v in valores],
                        textposition='outside',
                    )
                ])
                
                fig_barras.update_layout(
                    yaxis=dict(
                        title='',
                        showticklabels=False,
                        showgrid=False,
                        zeroline=False,
                        range=[0, max(valores) * 1.15]
                    ),
                    xaxis=dict(
                        title='',
                        showgrid=False
                    ),
                    height=350,
                    showlegend=False,
                    margin=dict(l=40, r=40, t=50, b=40)
                )
                
                st.plotly_chart(fig_barras, use_container_width=True)
            else:
                # Mostrar médias gerais
                import plotly.graph_objects as go
                
                trimestres = ['Trimestre 1', 'Trimestre 2', 'Trimestre 3', 'Trimestre 4']
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
                        marker_color=['#6C9BCF', '#8BB8E8', '#A9CCE3', '#C5DEDD'],
                        text=[f'{v:.2f}' for v in valores],
                        textposition='outside',
                    )
                ])
                
                fig_barras.update_layout(
                    yaxis=dict(
                        title='',
                        showticklabels=False,
                        showgrid=False,
                        zeroline=False,
                        range=[0, max(valores) * 1.15]
                    ),
                    xaxis=dict(
                        title='',
                        showgrid=False
                    ),
                    height=350,
                    showlegend=False,
                    margin=dict(l=40, r=40, t=50, b=40)
                )
                
                st.plotly_chart(fig_barras, use_container_width=True)
        
        with col_grafico2:
            st.markdown("<h4 style='text-align: center;'>Percentual de Área Georreferenciável</h4>", unsafe_allow_html=True)
            
            # Calcular percentagem de área georreferenciável da coluna percent_area_georef
            if len(gdf_filtrado) == 1:
                # Para município individual - usar a coluna percent_area_georef
                municipio_especifico = gdf_filtrado.iloc[0]
                if 'percent_area_georef' in municipio_especifico:
                    percentual = float(municipio_especifico['percent_area_georef'])
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
                    'axis': {
                        'range': [0, 100], 
                        'tickwidth': 1, 
                        'tickcolor': "darkblue",
                        'tickmode': 'array',
                        'tickvals': [0, 25, 50, 75, 90, 100],
                        'ticktext': ['0', '25', '50', '75', '90', '100']
                    },
                    'bar': {'color': "rgba(0,0,0,0)"},  # Barra invisível
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 2.5], 'color': '#27ae60'},
                        {'range': [2.5, 5], 'color': '#29b15e'},
                        {'range': [5, 7.5], 'color': '#2cb55d'},
                        {'range': [7.5, 10], 'color': '#2eb85b'},
                        {'range': [10, 12.5], 'color': '#31bc5a'},
                        {'range': [12.5, 15], 'color': '#36bf5c'},
                        {'range': [15, 17.5], 'color': '#3dc261'},
                        {'range': [17.5, 20], 'color': '#44c565'},
                        {'range': [20, 22.5], 'color': '#4ec96a'},
                        {'range': [22.5, 25], 'color': '#56cc6e'},
                        {'range': [25, 27.5], 'color': '#5fcf73'},
                        {'range': [27.5, 30], 'color': '#67d277'},
                        {'range': [30, 32.5], 'color': '#70d57c'},
                        {'range': [32.5, 35], 'color': '#78d880'},
                        {'range': [35, 37.5], 'color': '#81db85'},
                        {'range': [37.5, 40], 'color': '#89de89'},
                        {'range': [40, 42.5], 'color': '#92e08e'},
                        {'range': [42.5, 45], 'color': '#9ae292'},
                        {'range': [45, 47.5], 'color': '#a3e597'},
                        {'range': [47.5, 50], 'color': '#abe79b'},
                        {'range': [50, 52.5], 'color': '#b4e9a0'},
                        {'range': [52.5, 55], 'color': '#bceba4'},
                        {'range': [55, 57.5], 'color': '#c5eda9'},
                        {'range': [57.5, 60], 'color': '#cdefad'},
                        {'range': [60, 62.5], 'color': '#d6f0b2'},
                        {'range': [62.5, 65], 'color': '#def2b6'},
                        {'range': [65, 67.5], 'color': '#e7f3bb'},
                        {'range': [67.5, 70], 'color': '#eff4bf'},
                        {'range': [70, 72.5], 'color': '#f8f5c4'},
                        {'range': [72.5, 75], 'color': '#f9f2b8'},
                        {'range': [75, 77.5], 'color': '#fae9a0'},
                        {'range': [77.5, 80], 'color': '#f9e18e'},
                        {'range': [80, 82.5], 'color': '#f7d87c'},
                        {'range': [82.5, 85], 'color': '#f6d06a'},
                        {'range': [85, 87.5], 'color': '#f4c258'},
                        {'range': [87.5, 90], 'color': '#f2b446'},
                        {'range': [90, 92.5], 'color': '#f0a634'},
                        {'range': [92.5, 95], 'color': '#ec8e2c'},
                        {'range': [95, 97.5], 'color': '#e96a30'},
                        {'range': [97.5, 100], 'color': '#e74c3c'}
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

        # Valores Totais Trimestrais por Nota
        st.markdown("""
                    <div style='text-align: center; display: flex; align-items: center; justify-content: center;'>
                        <h3 style='margin: 0; padding-right: 5px;'>Valores Totais Trimestrais por Nota</h3>
                        <div class="tooltip">
                            <span style='cursor: help; color: #0066cc; font-size: 16px;'>ⓘ</span>
                            <span class="tooltiptext">
                                Valores totais calculados para cada trimestre considerando a nota total 
                                do período e a área georreferenciável. O cálculo é feito aplicando-se 
                                as faixas de valores da tabela INCRA de acordo com a pontuação obtida 
                                em cada trimestre.
                            </span>
                        </div>
                    </div>
                    <style>
                    .tooltip {
                        position: relative;
                        display: inline-block;
                    }
                    .tooltip .tooltiptext {
                        visibility: hidden;
                        width: 300px;
                        background-color: #555;
                        color: #fff;
                        text-align: center;
                        border-radius: 6px;
                        padding: 10px;
                        position: absolute;
                        z-index: 1;
                        bottom: 125%;
                        left: 50%;
                        margin-left: -150px;
                        opacity: 0;
                        transition: opacity 0.3s;
                        font-size: 14px;
                    }
                    .tooltip:hover .tooltiptext {
                        visibility: visible;
                        opacity: 1;
                    }
                    </style>
                    """, unsafe_allow_html=True)
        
        # Calcular valores totais por trimestre
        total_q1 = sum(calcular_valor_por_nota(row['nota_total_q1'], row['area_georef']) 
                       for _, row in gdf_filtrado.iterrows())
        total_q2 = sum(calcular_valor_por_nota(row['nota_total_q2'], row['area_georef'])
                       for _, row in gdf_filtrado.iterrows())
        total_q3 = sum(calcular_valor_por_nota(row['nota_total_q3'], row['area_georef'])
                       for _, row in gdf_filtrado.iterrows())
        total_q4 = sum(calcular_valor_por_nota(row['nota_total_q4'], row['area_georef'])
                       for _, row in gdf_filtrado.iterrows())
        
        # Exibir cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_q1_mi = total_q1 / 1_000_000
            total_q1_fmt = f"R$ {total_q1_mi:,.3f} Mi".replace(",", "X").replace(".", ",").replace("X", ".")
            st.metric("1º Trimestre", total_q1_fmt)
        
        with col2:
            total_q2_mi = total_q2 / 1_000_000
            total_q2_fmt = f"R$ {total_q2_mi:,.3f} Mi".replace(",", "X").replace(".", ",").replace("X", ".")
            st.metric("2º Trimestre", total_q2_fmt)
        
        with col3:
            total_q3_mi = total_q3 / 1_000_000
            total_q3_fmt = f"R$ {total_q3_mi:,.3f} Mi".replace(",", "X").replace(".", ",").replace("X", ".")
            st.metric("3º Trimestre", total_q3_fmt)
        
        with col4:
            total_q4_mi = total_q4 / 1_000_000
            total_q4_fmt = f"R$ {total_q4_mi:,.3f} Mi".replace(",", "X").replace(".", ",").replace("X", ".")
            st.metric("4º Trimestre", total_q4_fmt)
        
        st.markdown("---")
        
        # --- Gráfico: Composição média das notas por UF (versão final) ---
        st.markdown("<h3 style='text-align: center;'>Composição Média dos Graus de Dificuldade por UF</h3>", unsafe_allow_html=True)

        # Selecionar colunas principais de notas
        colunas_notas = ["nota_veg", "nota_area", "nota_relevo", "nota_insalub_2",
                        "nota_total_q1", "nota_total_q2", "nota_total_q3", "nota_total_q4"]
        colunas_presentes = [c for c in colunas_notas if c in gdf_filtrado.columns]

        if len(colunas_presentes) >= 3:
            # Calcular média das notas por UF
            df_uf = (
                gdf_filtrado.groupby("SIGLA_UF")[colunas_presentes]
                .mean()
                .reset_index()
            )
            
            # Calcular total para ordenar por complexidade/custo
            df_uf['total_notas'] = df_uf[colunas_presentes].sum(axis=1)
            df_uf = df_uf.sort_values("total_notas", ascending=False)

            # Dicionário de legendas amigáveis (ordem invertida para legenda)
            legendas = {
                "nota_total_q1": "Clima T1",
                "nota_total_q2": "Clima T2",
                "nota_total_q3": "Clima T3",
                "nota_total_q4": "Clima T4",
                "nota_insalub_2": "Insalubridade",
                "nota_relevo": "Relevo",
                "nota_area": "Área CAR",
                "nota_veg": "Vegetação",
            }

            # Paleta suave consistente com o restante do app
            cores = {
                "nota_total_q1": "#6C9BCF",
                "nota_total_q2": "#8BB8E8", 
                "nota_total_q3": "#A9CCE3",
                "nota_total_q4": "#C5DEDD",
                "nota_insalub_2": "#9AD0EC",
                "nota_relevo": "#C9E4F3",
                "nota_area": "#A3C4BC",
                "nota_veg": "#F2E8CF"
            }

            # Criar figura de barras empilhadas
            fig_empilhado = go.Figure()

            # Adicionar traços na ordem da legenda (invertida)
            ordem_legenda = ["nota_total_q1", "nota_total_q2", "nota_total_q3", "nota_total_q4",
                            "nota_insalub_2", "nota_relevo", "nota_area", "nota_veg"]
            
            # Filtrar apenas colunas presentes
            ordem_legenda = [col for col in ordem_legenda if col in colunas_presentes]
            
            for coluna in ordem_legenda:
                valores = df_uf[coluna].values
                
                fig_empilhado.add_trace(go.Bar(
                    x=df_uf["SIGLA_UF"],
                    y=valores,
                    name=legendas.get(coluna, coluna),
                    marker_color=cores.get(coluna, "#CCCCCC"),
                    text="",  # Sem texto nas barras
                    hovertemplate=legendas.get(coluna, coluna) + ": %{y:.2f}<extra></extra>"
                ))

            fig_empilhado.update_layout(
                barmode="stack",
                xaxis=dict(
                    title="", 
                    showgrid=False,
                    tickfont=dict(size=12)
                ),
                yaxis=dict(
                    title="", 
                    showticklabels=False,  # Remove valores do eixo Y
                    showgrid=False,
                    zeroline=False
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=11),
                    traceorder="normal"
                ),
                margin=dict(l=20, r=20, t=60, b=40),
                height=600,
                showlegend=True,
                plot_bgcolor="white",
                paper_bgcolor="white",
                hovermode="x unified"
            )
            
            # Customizar o hover
            fig_empilhado.update_layout(
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Arial"
                )
            )
            
            # Remover linha tracejada vertical do hover
            fig_empilhado.update_xaxes(showspikes=False)
            fig_empilhado.update_yaxes(showspikes=False)

            st.plotly_chart(fig_empilhado, use_container_width=True)
            
            # Texto explicativo abaixo do gráfico
            st.caption("* Estados ordenados por pontuação total. Passe o mouse sobre as barras para ver valores detalhados.")
        else:
            st.info("Graus de dificuldade insuficientes para gerar o gráfico de composição média por UF.")

        st.markdown("---")
        
        # Tabela de Municípios
        st.markdown("<h3 style='text-align: center;'>Tabela de Municípios</h3>", unsafe_allow_html=True)
        colunas_excluir = ["geometry"]
        if "fid" in gdf_filtrado.columns:
            colunas_excluir.append("fid")
        st.dataframe(gdf_filtrado.drop(columns=colunas_excluir), use_container_width=True)


if __name__ == "__main__":
    main()
