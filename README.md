# 🗺️ MDA Dashboard - Precificação de Áreas
## Prototipagem que Virou Padrão Federal

> **Dashboard que serviu de base para o site oficial do MDA (Ministério do Desenvolvimento Agrário). Desenvolvido como protótipo, a solução foi to tal adotada pelos devs do governo para implementação em escala.**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://mda-dashboard-precificacao.streamlit.app/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MDA - Gov](https://img.shields.io/badge/Usado%20por-MDA%20Federal-red.svg)](#)

## 🚀 Acesso Rápido

**Veja em ação:** https://mda-dashboard-precificacao.streamlit.app/

**Desenvolvedor:** Denner Caleare | [GitHub](https://github.com/DennerCaleare) | [LinkedIn](https://linkedin.com/in/dennercaleare)

---

## 📚 O Desafio do MDA

O Ministério do Desenvolvimento Agrário precisava de uma forma de:
- 🗺️ Visualizar custos de georreferenciamento por região
- 📊 Tomar decisões estratégicas baseadas em dados geográficos
- 📋 Identificar áreas críticas vs. áreas favoraéveis
- 📤 Apresentar dados de forma intuitiva

## ✨ A Solução que Entreguei

**Dashboard interativo com 6 critérios de precificação:**

### 🗺️ Visualização Geográfica
- Mapa interativo mostrando custos por múnicipío
- Cores degradadas indicando faixas de valor
- Filtros por Estado e Múnicipo
- Zoom dinâmico e tooltips informativos

### 📊 Análise Multidimensional
- 10+ indicadores principais
- Área total e perímetro
- Valores médios, mínimos e máximos
- Análise por trimestre
- Medidor de área georreferenciável

### 📈 Critérios de Precificação
Integra dados de 6 fontes públicas:
1. **Vegetação** - MapBiomas
2. **Relevo** - SRTM/Google Earth Engine
3. **Insalubridade** - DataSUS
4. **Clima** - INMET (25 anos de dados)
5. **Área** - CAR
6. **Acesso** - Vias rodoviárias

## 📙 Impacto Entregue

✅ **Protótipo virou padrão** - Governo federal adotou a solução
✅ **Tomá da de decisão** - Identifica regiões críticas vs. favóveis
✅ **Autômato de oramento** - Suporta decisões de alo cação de recursos
✅ **Documentado** - Devs do gov conseguiram replicar sem dificuldades
✅ **Escalável** - Base para integração com sistemas federais

## 🛠️ Stack Técnico

```python
Streamlit 1.32+         # Framework web para visualização
GeoPandas 0.14+        # Análise geoespacial
Folium 0.14+           # Mapas interativos
Plotly                 # Gráficos dinâmicos
Pandas/NumPy          # Processamento de dados
Python 3.9+           # Linguagem
```

## 📂 Estrutura do Projeto

```
mda-dashboard-precificacao/
├── main.py                         # Aplicação principal
├── requirements.txt               # Dependências
├── README.md                      # Este arquivo
├── src/mda_app/
│   ├── app.py                     # Lógica principal
│   ├── components/                # Componentes UI
│   ├── config/                    # Configurações
│   ├── core/                      # Lógica de dados
│   └── utils/                     # Utilitários
├── data/raw/                     # Dados brutos
├── notebooks/                    # Análises exploratórias
└── tests/                        # Testes
```

## 🚀 Como Usar

### Acessar Online
```
https://mda-dashboard-precificacao.streamlit.app/
```

### Rodar Localmente
```bash
git clone https://github.com/DennerCaleare/mda-dashboard-precificacao.git
cd mda-dashboard-precificacao
pip install -r requirements.txt
streamlit run main.py
```

## 📊 Tabela de Precificação

| Pontos | Valor/hectare |
|--------|---------------|
| ≤ 15 | R$ 49,83 |
| 16-25 | R$ 59,80 |
| 26-35 | R$ 104,78 |
| 36-45 | R$ 134,88 |
| 46-55 | R$ 164,95 |
| > 55 | R$ 202,87 |

## 📚 Fontes de Dados Inteligradas

- **MapBiomas** - Cobertura vegetal (10m resolução)
- **USGS SRTM** - Modelo digital de elevação (30m)
- **DataSUS** - Saúde pública
- **INMET** - Dados climáticos (25 anos)
- **IBGE** - Limites administrativos
- **Base Zetta** - Dados fundiários

## 👨‍💻 Desenvolvido por

**Denner Caleare**

- 🌟 Desenvolvedor especialista em dashboards geoespaciais
- 📚 Author de soluções adotadas por gov federal
- 💼 Agência Zetta - UFLA

**Contato:**
- [GitHub](https://github.com/DennerCaleare)
- [LinkedIn](https://linkedin.com/in/dennercaleare)

## 📝 Licença

Desenvolvido para o Ministério do Desenvolvimento Agrário. Protótipo para adopção federal.

---

**Desenvolvido com ❤️ em Lavras, MG**
