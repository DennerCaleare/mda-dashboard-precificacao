# MDA Dashboard - Precificação de Áreas

Dashboard interativo para análise de precificação de áreas de georreferenciamento desenvolvido para o Ministério do Desenvolvimento Agrário.

## 🚀 Versão Online

[Ver Dashboard em Produção](https://mda-dashboard-precificacao-main-main-py.streamlit.app)

## Descrição

Este projeto apresenta um dashboard desenvolvido em Streamlit para análise e visualização de dados de precificação de serviços de georreferenciamento em municípios brasileiros. A ferramenta permite análise espacial, estatística e temporal dos critérios que compõem a precificação de áreas.

## Funcionalidades Principais

- **Mapa Interativo**: Visualização geoespacial dos municípios com diferentes critérios de análise
- **Estatísticas Detalhadas**: 10 indicadores principais incluindo área total, perímetro, valores médios, mínimos e máximos
- **Análise por Trimestre**: Visualização de notas e valores por período
- **Gráfico de Notas**: Comparativo visual das notas por trimestre
- **Medidor de Área Georreferenciável**: Percentual de área disponível para georreferenciamento
- **Filtros Dinâmicos**: Seleção por UF, município e critérios específicos
- **Tabela Completa**: Visualização detalhada de todos os dados dos municípios

## Como Executar

### Opção 1: Com uv (recomendado)

```bash
uv sync
uv run streamlit run main.py
```

### Opção 2: Com pip

```bash
pip install -r requirements.txt
streamlit run main.py
```

## Tecnologias Utilizadas

- **Streamlit** - Framework para aplicações web em Python
- **GeoPandas** - Manipulação e análise de dados geoespaciais
- **Folium** - Visualização de mapas interativos
- **Plotly** - Gráficos interativos
- **Pandas/NumPy** - Análise e manipulação de dados

## Critérios de Precificação

A precificação é calculada com base nos seguintes critérios:

### Vegetação

Dados obtidos da plataforma MapBiomas (Coleção 2 - 10m de resolução). A nota é calculada com base na vegetação predominante e média do município.

### Relevo

Classificação baseada em dados SRTM (30m) do Google Earth Engine, seguindo a tipologia de Lepsch (1983).

### Insalubridade

Dados do DataSUS considerando ocorrências de dengue e ataques de animais peçonhentos.

### Clima

Séries históricas de 25 anos do INMET via BigQuery, com aplicação de krigagem ordinária para distribuição espacial.

### Área

Média das áreas de lotes CAR por município.

### Acesso

Disponibilidade de acesso por vias rodoviárias.

## Estrutura de Valores

A precificação segue a tabela de referência baseada na pontuação total:

- ** 15 pontos**: R$ 49,83/ha
- **16-25 pontos**: R$ 59,80/ha
- **26-35 pontos**: R$ 104,78/ha
- **36-45 pontos**: R$ 134,88/ha
- **46-55 pontos**: R$ 164,95/ha
- **> 55 pontos**: R$ 202,87/ha

## Estrutura do Projeto

```
 main.py                 # Ponto de entrada da aplicação
 src/
    mda_app/
        app.py          # Aplicação principal
        components/     # Componentes de UI e visualizações
        config/         # Configurações
        core/           # Lógica de carregamento de dados
        utils/          # Utilitários e formatadores
 .streamlit/
    config.toml         # Configuração do tema
 data/                   # Dados do projeto
 requirements.txt        # Dependências
```

## Requisitos do Sistema

- Python 3.9 ou superior
- Bibliotecas listadas em requirements.txt

## Fontes de Dados

- **MapBiomas**: Dados de vegetação
- **USGS SRTM**: Modelo digital de elevação
- **DataSUS**: Dados de saúde pública
- **INMET/BigQuery**: Dados climáticos
- **IBGE**: Limites municipais e dados populacionais
- **Base Zetta**: Dados fundiários (CAR, SIGEF, Terras da União, UCs, TIs)

## Desenvolvimento

Desenvolvido pela **Agência Zetta** para análise de precificação de serviços de georreferenciamento.

## Licença

Este projeto é destinado ao uso interno do Ministério do Desenvolvimento Agrário.
