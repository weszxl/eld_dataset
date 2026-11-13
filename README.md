# Dataset e EDA — Mobilidade Sustentável em Porto Alegre

## Sobre

Scripts de coleta, limpeza e Análise Exploratória de Dados (EDA) para a criação de um dataset próprio sobre a infraestrutura viária e cicloviária de Porto Alegre.

## Objetivo Atual

O foco desta etapa é validar a qualidade das fontes, documentar o histórico de limpeza dos dados e gerar o dataset que servirá de base.

## Escolha das Bibliotecas

* **OSMnx e Shapely:** Extraem a malha viária, a infraestrutura cicloviária atual e os pontos de interesse diretamente do OpenStreetMap, permitindo calcular distâncias espaciais entre bairros e serviços.
* **GeoPandas e Pandas:** Realizam o cruzamento geográfico (como unir ruas aos setores censitários do IBGE e dados abertos da prefeitura), o tratamento de valores nulos e a estruturação da tabela do dataset.
* **Matplotlib, Seaborn e Folium:** Geram gráficos estatísticos e mapas interativos para a Análise Exploratória de Dados (EDA), permitindo inspecionar visualmente a distribuição das variáveis na cidade.
* **uv, Ruff e `.gitignore`:** O `uv` gerencia o ambiente Python e os pacotes, enquanto o `Ruff` garante a padronização e qualidade do código nos scripts de extração e limpeza. Os arquivos pesados de dados brutos são ignorados no controle de versão.

## Rodar o Ambiente

1. **Criaçao do env na pasta raiz:**
   ```bash
   uv venv
   ```

2. **Ativar o ambiente:**
   ```bash
   # Linux ou macOS
   source .venv/bin/activate

   # Windows
   .venv\Scripts\activate
   ```

3. **Instalar as bibliotecas:**
   ```bash
   uv pip install -r requirements.txt
   ```

4. **Verificar a formatação do código:**
   ```bash
   ruff check .
   ```

## Equipe (Grupo 5)

* Wesley Stark Ferreira
* Lorenzo Marques Conceição
* Gabrielli Borba de Oliveira
* Mariana Isabela Torres
* Miguel Rusch Rodrigues
* Eduardo Henrique Leite Calvani