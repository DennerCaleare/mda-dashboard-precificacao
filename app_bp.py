import streamlit as st
import geopandas as gpd
import numpy as np
import folium
from folium.plugins import Fullscreen
from streamlit_folium import st_folium
import plotly.express as px
import os
from branca.element import Template, MacroElement

def reais(x):
    val = f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return val

st.set_page_config(layout="wide", page_title="Precificação de Áreas - MDA", page_icon="🏷️")

col1, col2, col3 = st.columns([1, 1, 1.3])  # adjust proportions (logo vs text)

with col1:
    st.image("dados/img_1.png", width=400)  # fixed width so it doesn’t stretch

with col2:
    st.markdown(
        """
        <div style="text-align: center;">
            <h1 style='color: #006199; margin-bottom: 0;'>
                Dashboard - Precificação de Áreas
            </h1>
            <h3 style='color:#006199; font-weight: normal; margin-top: 5px;'>
                Análise de notas e valores por município
            </h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Carregar dados
@st.cache_data
def carregar_dados():
    asd = gpd.read_file("dados/precificacao_al_ii.geojson")
    # Criar indicadores adicionais
    asd["valor_medio"] = (asd["valor_mun_perim"] + asd["valor_mun_area"]) / 2
    return asd

gdf = carregar_dados()
gdf = gdf.to_crs(epsg=4326)
gdf['nota_insalub_2'] = gdf['nota_insalub_2'].apply(lambda x: 1 if x < 1 else x)
gdf['valor_medio_car'] = np.where(
    gdf['area_car_total'] != 0,
    ((gdf['area_car_total'] / gdf['area_georef']) * gdf['valor_mun_area'])/gdf['num_imoveis'],
    0
)

gdf['val_med_car_perim'] = np.where(
    gdf['num_imoveis'] != 0,
    gdf['valor_mun_perim'] / gdf['num_imoveis'],
    0
)

# Filtros (sidebar)
st.markdown("""
    <style>
    /* Sidebar geral */
    [data-testid="stSidebar"] {
        background-color: #E5E5E5;
    }

    /* Texto dentro do multiselect */
    div[data-baseweb="select"] span {
        color: #006199;
        font-weight: 500;
    }.st-c1 {
    background-color:#E5E5E5;
}



}

    div[data-baseweb="slider"] > div > div {
        background-color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar filtros ---
ufs = gdf["SIGLA_UF"].unique()
uf_sel = st.sidebar.multiselect("Seleção de Estado (UF)", options=ufs, default=list(ufs))

# --- Seletor dinâmico de critério ---
criterios = [
    "valor_medio", "valor_mun_perim", "valor_mun_area", "nota_media", "nota_veg", "nota_area", "nota_relevo",
    "nota_insalub", "nota_insalub_2", "nota_total_q1", "nota_total_q2",
    "nota_total_q3", "nota_total_q4"
]
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

# Define explanations for each criterion
criterio_explicacao = {
    "nota_veg": "Nota relativa à vegetação do local. Calculada de acordo com a classe predominante no município (aberta, intermediária e fechada) e média de ocorrência de classe no intervalo.",
    "nota_area": "Nota relativa à área média de lotes CAR na área do município. Acima de 35ha, entre 15 e 35ha, até 15ha, conforme máximas e mínimas.",
    "nota_relevo": "Nota relativa ao relevo predominante no município.",
    "nota_insalub": "Nota relativa à insalubridade (casos de dengue por município). Distribuída conforme máximos e mínimos gerais.",
    "nota_insalub_2": "Nota relativa à insalubridade ajustada, incluindo incidência de ataques de animais peçonhentos.",
    "valor_mun_perim": "Valor total do município em relação ao perímetro total de imóveis CAR, utilizando dados do Quadro II da Tabela de Rendimento e Preço do Anexo I da INSTRUÇÃO NORMATIVA SEI/INCRA.",
    "valor_mun_area": "Valor total do município em relação à área georreferenciável.",
    "nota_media": "Média das notas utilizada para composição do valor final.",
"nota_total_q1": "Nota total somada para o trimestre", "nota_total_q2": "Nota total somada para o trimestre",
    "nota_total_q3": "Nota total somada para o trimestre", "nota_total_q4":"Nota total somada para o trimestre"
    # adicione mais critérios se necessário
}

# Sidebar selection of criterion
criterio_sel = st.sidebar.selectbox("Selecione o critério para visualização", options=list(criterio_explicacao.keys()), index=list(criterio_explicacao.keys()).index("nota_media"))

# Display explanation for selected criterion
st.sidebar.markdown(
    f"**Critério selecionado:** {criterios_labels[criterio_sel]}\n\n"

)

# --- Slider do critério selecionado ---
crit_min, crit_max = float(gdf[criterio_sel].min()), float(gdf[criterio_sel].max())
crit_sel = st.sidebar.slider(f"{criterios_labels[criterio_sel]}", crit_min, crit_max, (crit_min, crit_max))

# --- Aplicar filtros ---
filtros = (
    gdf["SIGLA_UF"].isin(uf_sel) &
    gdf[criterio_sel].between(*crit_sel)
)
gdf_filtrado = gdf[filtros]
gdf_filtrado2 = gdf_filtrado.to_crs(epsg=5880)

# Paleta de cores para notas
# Paleta de cores invertida: quanto maior, mais vermelho
def get_color(value, min_val, max_val):
    norm = (value - min_val) / (max_val - min_val)
    if norm < 0.5:
        r = 0
        g = int(255 * (2 * norm))
        b = int(255 * (1 - 2 * norm))
    else:
        try:
            norm2 = 2 * (norm - 0.5)
            r = int(255 * norm2)
            g = int(255 * (1 - norm2))
            b = 0
        except Exception as e:
            r= 55
            g= 110
            b = 33
            #print(e, e.__class__)
    return f'#{r:02x}{g:02x}{b:02x}'

# Abas
abas = st.tabs(["📌 Introdução", "🌍 Mapa", "📊 Estatística Geral", "📄 Tabela"])

# Introdução
with abas[0]:
    st.title("• Introdução")
    st.markdown("""
<p style="text-align: justify;">
“A partir do trabalho de elaboração e estabilização metodológica para o cálculo de estimativa de áreas a georreferenciar nos municípios do acordo judicial do desastre de Mariana, se faz necessário estimar, também, o valor de todo volume do serviço a ser realizado.
Para chegar ao valor estimado, foi utilizada a minuta de instrução normativa de referência SEI/INCRA – 20411255, dentro do sistema SEI.
Esta minuta estabelece critérios e parâmetros de cálculos para preços referenciais para execução de serviços geodésicos/cartográficos, para medição e demarcação de imóveis rurais em áreas sob jurisdição do INCRA.
A Tabela de Classificação estabelece, na minuta de Portaria, os critérios de pontuação para posterior comparação a tabela de Rendimento e Preço.”\n

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


# Mapa
with abas[1]:
    col1, col2= st.columns([5,1])
    with col1:
        st.title("🌍 **Mapa de Precificação**", width='content')
        st.markdown(f"**Critério selecionado:** <u>{criterios_labels[criterio_sel]}</u>\n\n"
    f"{criterio_explicacao[criterio_sel]}", unsafe_allow_html=True)
        m = folium.Map(
            location=[gdf_filtrado.centroid.y.mean(), gdf_filtrado.centroid.x.mean()],
            zoom_start=9,
            tiles="OpenStreetMap"
        )
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri", name="Esri Satélite", overlay=False, control=True
        ).add_to(m)
        Fullscreen().add_to(m)

        # Valores mínimo e máximo do critério selecionado
        min_val, max_val = gdf_filtrado[criterio_sel].min(), gdf_filtrado[criterio_sel].max()

        for _, row in gdf_filtrado.iterrows():
            fill = get_color(row[criterio_sel], min_val, max_val)
            valor_area = f"{row['valor_mun_area']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            valor_perim = f"{row['valor_mun_perim']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            tooltip_text = f"""
            <h4 style='text-align:center;font-weight:bold;'>{row['mun_nome']}</h4>
            <b>UF:</b> {row['SIGLA_UF']}<br>
            <b>Área Georreferenciável:</b> {row['area_georef']:.2f} ha<br>
            <b>{criterio_sel}:</b> {row[criterio_sel]:.2f}<br>
            <b>Valor Total por Área (R$):</b> {valor_area}<br>
            <b>Valor Total por Perímetro (R$):</b> {valor_perim}<br>
            <b>Valor Médio Por Imóvel (Área): {reais(row['valor_medio_car'])}<br>
            <b>Valor Médio Por imóvel (Perim): {reais(row['val_med_car_perim'])}<br>
            """
            folium.GeoJson(
                row["geometry"],
                tooltip=tooltip_text,
                style_function=lambda feature, fill=fill: {
                    'fillColor': fill,
                    'color': 'black',
                    'weight': 1.5,
                    'fillOpacity': 0.7,
                },
            ).add_to(m)
        # Valores mínimo e máximo do critério selecionado
        min_val, max_val = gdf_filtrado[criterio_sel].min(), gdf_filtrado[criterio_sel].max()

        if "valor" in criterio_sel.lower():
            min_val2, max_val2 = f"R${min_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), f"R${max_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            media = f"R${gdf_filtrado[criterio_sel].mean():,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            min_val2,max_val2 = round(min_val,3), round(max_val,3)
            media = round(gdf_filtrado[criterio_sel].mean(),3)
        # Gerar gradiente de cores dinamicamente
        gradient_colors = [get_color(v, min_val, max_val) for v in np.linspace(min_val, max_val, 100)]
        gradient_css = ','.join(gradient_colors)

        legend_html = f"""
        <div style="
            position: fixed; 
            bottom: 50px; left: 50px; width: 180px; 
            background-color: white; border:2px solid grey; z-index:9999; 
            font-size:10px; padding: 10px
        ">
        <b>Legenda: {criterio_sel}</b><br>
        <i style="display:block;height:15px;width:100%; background: linear-gradient(to right, {gradient_css}); margin-bottom:5px;"></i>
        <div style="display:flex; justify-content: space-between;">
        <span>{min_val2}</span>
        <span>{max_val2}</span>
        </div>
        </div>
        """

        m.get_root().html.add_child(folium.Element(legend_html))

        st_folium(m, width=1500, height=900)

    with col2:
        st.title(f"Stats: {criterios_labels[criterio_sel]}")

        # Estatísticas básicas

        st.metric("Mínimo", f"{min_val2}")
        st.metric("Médio", f"{media}")
        st.metric("Máximo", f"{max_val2}")

        st.write("Distribuição dos valores por município:")

        # Histograma
        fig_hist = px.histogram(
            gdf_filtrado,
            x=criterio_sel,
            nbins=15,
            title=f"Distribuição de {criterio_sel}",
            labels={criterio_sel: f"{criterio_sel}"}
        )
        st.plotly_chart(fig_hist, use_container_width=True)

# Análise Estatística
with abas[2]:
    st.title("📊 Estatística Geral")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Área Total", f"{(gdf_filtrado2.area.sum()/10000):,.2f} ha")
    col2.metric("Nota Média", f"{gdf_filtrado['nota_media'].mean():.2f}")
    col3.metric("Valor Médio por Perímetro", f"R$ {gdf_filtrado['valor_mun_perim'].mean():,.2f}")
    col4.metric("Valor Médio por Área", f"R$ {gdf_filtrado['valor_mun_area'].mean():,.2f}")
    valor_total_perim = f"R${gdf_filtrado['valor_mun_perim'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    valor_total_area = f"R${gdf_filtrado['valor_mun_area'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.markdown(
        f"**Valor Total Perímetro:** {valor_total_perim}\n\n"
        f"**Valor Total Área:** {valor_total_area}\n\n"

    )

    fig1 = px.histogram(gdf_filtrado, x="nota_media", nbins=15, title="Distribuição da Nota Média")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.box(gdf_filtrado, x="SIGLA_UF", y="valor_medio", title="Distribuição de Valor Médio por UF")
    st.plotly_chart(fig2, use_container_width=True)

# Tabela
with abas[3]:
    st.title("📄 Tabela de Municípios")
    st.dataframe(gdf_filtrado.drop(columns=["geometry", "fid"]))

