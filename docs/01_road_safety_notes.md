# Pilar: Segurança Viária (Porto Alegre - RS)

Este diretório contém a coleta, auditoria de qualidade, scripts de tratamento documentados (Jupyter Notebooks) e bases limpas referentes ao pilar de **Segurança Viária**, fundamentado na **Lei Complementar nº 951/2022** (Programa de Mobilidade Segura de Porto Alegre) para o projeto de priorização de ciclovias alimentadoras.

---

## 1. Estrutura do Diretório

* **`dados_brutos/`**: Bases originais extraídas sem modificações (`bruto_eptc_acidentes.csv`, `bruto_osm_malha_poa.geojson`, `bruto_osm_nos_poa.geojson`, `bruto_osm_ciclovias_poa.geojson`).
* **`scripts/`**: Notebooks individuais contendo documentação metodológica em Markdown e código executável (`0_extrair_bruto_osm.ipynb` a `8_auditoria_bases_brutas_e_limpas.ipynb`).
* **`dados_limpos/`**: Outputs individuais auditados e prontos para integração espacial/tabular no dataset final do grupo.

---

## 2. Rastreabilidade das 9 Variáveis Mapeadas

| # | Variável Original (LC 951/2022) | Status | Fonte Oficial / Técnica | Notebook de Tratamento | Arquivo Limpo Gerado |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | Histórico de acidentes com ciclistas | **Concluído** | DataPOA / EPTC | `limpar_01_historico_ciclistas.ipynb` | `limpo_01_historico_ciclistas.csv` |
| **2** | Quantidade de acidentes por gravidade | **Concluído** | DataPOA / EPTC | `limpar_02_gravidade_acidentes.ipynb` | `limpo_02_gravidade_acidentes.csv` |
| **3** | Localização georreferenciada | **Concluído** | DataPOA / EPTC + OSM Local | `limpar_03_geolocalizacao_acidentes.ipynb` | `limpo_03_geolocalizacao_acidentes.geojson` |
| **4** | Quantidade de cruzamentos e interseções | **Concluído** | OpenStreetMap (`OSMnx`) | `limpar_04_cruzamentos.ipynb` | `limpo_04_cruzamentos.geojson` |
| **5** | Existência de ciclovias e ciclofaixas | **Concluído** | Ref. ObservaMOB / OSM | `limpar_05_ciclovias_existentes.ipynb` | `limpo_05_ciclovias_existentes.geojson` |
| **6** | Limites de velocidade das vias | **Concluído** | Ref. EPTC + Art. 61 CTB / OSM | `limpar_06_velocidade_maxima.ipynb` | `limpo_06_velocidade_maxima.geojson` |
| **7** | Volume de veículos por via | **Adaptado (Proxy)** | Ref. EPTC Transparente / OSM | `limpar_07_proxy_volume_trafego.ipynb` | `limpo_07_proxy_volume_trafego.geojson` |
| **8** | Velocidade média dos veículos | **Descartado** | EPTC / ObservaMOB | — | *Substituído pelo item 6 (cobertura restrita a radares)* |
| **9** | Iluminação pública por trecho | **Descartado** | IPSul POA / DataPOA | — | *Sem base aberta georreferenciada por logradouro* |

---

## 3. Decisões Metodológicas e Auditoria de Qualidade

Todas as bases limpas passaram por auditoria automatizada (`8_auditoria_bases_brutas_e_limpas.ipynb`) atingindo **100% de completude** nas variáveis-chave de modelagem e geometria:

* **Precisão Espacial nos Acidentes (`limpo_03`):** Dos 1.627 sinistros envolvendo ciclistas registrados pela EPTC, 1.458 possuíam GPS nativo. Dos 169 sem coordenadas, **91 registros com endereço exato** (62 cruzamentos via interseção topológica e 29 em vias curtas $\le 3\text{ km}$ com número predial) foram recuperados localmente, atingindo **1.549 pontos (95,2% de cobertura)**. Os 78 registros sem número ou localizados em avenidas extensas sem esquina foram descartados intencionalmente deste arquivo espacial para evitar viés de centroide (permanecendo preservados nos arquivos `limpo_01` e `limpo_02` para análises globais).
* **Imputação Normativa de Velocidade (`limpo_06`):** Como 70,2% dos 88.347 trechos viários não possuíam placa cadastrada colaborativamente no OpenStreetMap, aplicou-se a regra legal do **Art. 61 do Código de Trânsito Brasileiro (CTB)** com base na hierarquia funcional da via (`80 km/h` trânsito rápido, `60 km/h` arteriais, `40 km/h` coletoras e `30 km/h` locais), preservando os **26.350 trechos** com medição real (`OSM_Real`) e rastreando os **61.997 imputados** (`Imputado_CTB`).
* **Proxy de Volume Veicular e Descartes (Itens 7, 8 e 9):** Como os medidores eletrônicos de fluxo e velocidade média da EPTC cobrem apenas pontos isolados da cidade, utilizou-se a classificação hierárquica da via (`highway`) como indicador indireto contínuo de intensidade de tráfego (Item 7) e descartou-se a velocidade média pontual (Item 8). A iluminação pública por trecho (Item 9) foi descartada pela inexistência de base aberta georreferenciada no DataPOA ou na concessionária IPSul.

---

## 4. Como Reproduzir o Ambiente

1. Crie e ative um ambiente virtual Python na raiz deste diretório:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
