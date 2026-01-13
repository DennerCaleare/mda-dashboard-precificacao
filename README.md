# MDA Dashboard - Precificação de Áreas 🗺️

> Dashboard interativo para análise e precificação de áreas de georreferenciamento desenvolvido para o Ministério do Desenvolvimento Agrário.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://mda-dashboard-precificacao.streamlit.app/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🚀 Versão Online

**Acesse o dashboard em tempo real:**

👉 **[MDA Dashboard - Precificação](https://mda-dashboard-precificacao.streamlit.app/)**

## 📋 Sobre o Projeto

Sistema completo de análise e visualização de dados para precificação de serviços de georreferenciamento em municípios brasileiros. A plataforma integra dados de múltiplas fontes (MapBiomas, SRTM, DataSUS, INMET) para calcular valores de referência baseados em critérios técnicos.

### ✨ Funcionalidades Principais

- 📍 **Mapa Interativo**: Visualização geoespacial com filtros por estado e município
- 📊 **10 Indicadores Estatísticos**: Área total, perímetro, valores médios, mínimos e máximos
- 📈 **Análise Temporal**: Visualização trimestral de notas e valores
- 🎯 **Medidor de Performance**: Percentual de área georreferenciável
- 🔄 **Filtros Dinâmicos**: Seleção granular por UF, município e critérios
- 📑 **Tabelas Detalhadas**: Exportação de dados completos
- 📱 **Interface Responsiva**: Funciona em desktop e mobile

## 🏗️ Critérios de Precificação

| Critério | Fonte de Dados | Descrição |
|----------|----------------|----------|
| **Vegetação** | MapBiomas (10m) | Classificação de cobertura vegetal predominante |
| **Relevo** | SRTM/Google Earth Engine | Tipologia de Lepsch (1983) |
| **Insalubridade** | DataSUS | Dengue e ataques de animais peçonhentos |
| **Clima** | INMET/BigQuery (25 anos) | Séries históricas com aplicação de krigagem |
| **Área** | CAR | Média de áreas de lotes por município |
| **Acesso** | Vias rodoviárias | Disponibilidade de vias de acesso |

## 💰 Tabela de Valores

```
≤ 15 pontos    →  R$ 49,83/ha
16-25 pontos   →  R$ 59,80/ha
26-35 pontos   →  R$ 104,78/ha
36-45 pontos   →  R$ 134,88/ha
46-55 pontos   →  R$ 164,95/ha
> 55 pontos    →  R$ 202,87/ha
```

## 🛠️ Tecnologias

```python
Streamlit        # Framework web
GeoPandas        # Análise geoespacial
Folium          # Mapas interativos
Plotly          # Gráficos avançados
Pandas/NumPy    # Processamento de dados
```

## 📦 Instalação e Uso

### Opção 1: Com `uv` (Recomendado)

```bash
uvx sync
uv run streamlit run main.py
```

### Opção 2: Com `pip`

```bash
pip install -r requirements.txt
streamlit run main.py
```

## 📂 Estrutura do Projeto

```
.
├── main.py                      # Ponto de entrada
├── requirements.txt             # Dependências
├── src/
│   └── mda_app/
│       ├── app.py              # Aplicação principal
│       ├── components/         # Componentes de UI
│       ├── config/             # Configurações
│       ├── core/               # Lógica de dados
│       └── utils/              # Utilitários
├── data/
│   └── raw/                    # Dados brutos
├── notebooks/                  # Análises exploratórias
└── tests/                      # Testes unitários
```

## 📊 Fontes de Dados

- **MapBiomas**: Mosaicos de cobertura vegetal
- **USGS SRTM**: Modelo digital de elevação (30m)
- **DataSUS**: Indicadores de saúde pública
- **INMET**: Dados climáticos e meteorológicos
- **IBGE**: Limites administrativos e dados populacionais
- **Base Zetta**: Dados fundiários (CAR, SIGEF, TIs, UCs)

## 🎓 Desenvolvido por

**Denner Caleare** | [GitHub](https://github.com/DennerCaleare) | [LinkedIn](https://linkedin.com/in/dennercaleare)

Em parceria com a **Agência Zetta** para o Ministério do Desenvolvimento Agrário.

## 📄 Requisitos do Sistema

- Python 3.9 ou superior
- pip ou uv instalado
- 2GB de RAM disponível
- Conexão com internet (para dados MapBiomas)

## 📝 Licença

Este projeto é de uso interno do Ministério do Desenvolvimento Agrário.

---

**Desenvolvido com ❤️ em Lavras, MG**
