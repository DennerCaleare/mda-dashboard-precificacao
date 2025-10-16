# MDA Precificação de Áreas

Dashboard interativo para análise de precificação de áreas - Ministério do Desenvolvimento Agrário.

## 📋 Descrição

Este projeto apresenta um dashboard desenvolvido em Streamlit para análise e visualização de dados de precificação de serviços de georreferenciamento na região nordeste.

## 🚀 Como executar

### Com uv (recomendado)
```bash
uv sync
uv run streamlit run main.py
```

### Alternativa com pip
```bash
pip install -r requirements.txt
streamlit run main.py
```

## 📁 Estrutura do Projeto

```
├── main.py                     # Ponto de entrada da aplicação
├── app_bp.py                   # Versão original (legacy)
├── requirements.txt            # Dependências
├── pyproject.toml             # Configuração do projeto
├── README.md                  # Este arquivo
├── src/
│   └── mda_app/              # Código fonte principal
│       ├── __init__.py
│       ├── app.py            # Aplicação principal
│       ├── components/       # Componentes de UI
│       │   ├── ui_components.py
│       │   └── visualizations.py
│       ├── config/           # Configurações
│       │   └── settings.py
│       ├── core/             # Lógica central
│       │   └── data_loader.py
│       ├── models/           # Modelos de dados
│       ├── pages/            # Páginas da aplicação
│       └── utils/            # Utilitários
│           └── formatters.py
├── data/                     # Dados do projeto
│   ├── raw/                 # Dados brutos
│   └── processed/           # Dados processados
├── assets/                  # Recursos estáticos
│   └── images/             # Imagens
├── notebooks/              # Jupyter notebooks
├── tests/                  # Testes automatizados
└── docs/                   # Documentação
```

## 🛠️ Tecnologias Utilizadas

- **Streamlit**: Framework para criação de aplicações web
- **GeoPandas**: Manipulação de dados geoespaciais
- **Folium**: Visualização de mapas interativos
- **Plotly**: Gráficos interativos
- **NumPy/Pandas**: Manipulação de dados

## 📊 Funcionalidades

- 🗺️ **Mapa Interativo**: Visualização geoespacial dos municípios
- 📈 **Análise Estatística**: Métricas e indicadores
- 🔍 **Filtros Dinâmicos**: Seleção por critérios específicos
- 📋 **Tabela de Dados**: Visualização tabular completa
- 📱 **Interface Responsiva**: Design adaptável

## 📄 Critérios de Avaliação

- **Vegetação**: Baseado em dados do MapBiomas
- **Relevo**: Análise de modelo digital de elevação (SRTM)
- **Insalubridade**: Dados do DataSUS (dengue e animais peçonhentos)
- **Clima**: Séries históricas do INMET com krigagem
- **Área**: Média de lotes CAR por município
- **Acesso**: Disponibilidade de vias rodoviárias

## 🔧 Desenvolvimento

```bash
# Setup
uv sync --group dev

# Executar testes  
uv run pytest

# Formatação e linting
uv run black src/ tests/
uv run flake8 src/ tests/
```

## 📋 Requisitos

- Python 3.9+
- uv ou pip

## 👥 Equipe

Desenvolvido pela Agência Zetta para análise de precificação de serviços de georreferenciamento na região nordeste.