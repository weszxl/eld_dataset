# Notas de Dicionários e Regras de Limpeza — Pilar 2 (Acesso e Inclusão)

Levantamento dos dicionários e schemas reais em `data/1_raw/` antes do processamento das bases.

---

## 1. IBGE — Censo 2022 (Setores Censitários)

**Fontes:**
- `dicionario_de_dados_agregados_por_setores_censitarios_20261113.xlsx`
- `dicionario_de_dados_renda_responsavel_20260508.xlsx`
- CSVs usados no pipeline: `Agregados_por_setores_demografia_BR.csv` (`utf-8`, `;`) e `Agregados_por_setores_renda_responsavel_BR.csv` (`utf-8`, `;`).
  - *Remoção de redundância:* `Agregados_por_setores_basico_BR.csv` foi validado contra o `.gpkg` nas 9 colunas selecionadas para todos os `2.744` setores únicos de Porto Alegre (`0` divergências; diferença máxima em `AREA_KM2` de `5e-8` por arredondamento). Como o `.gpkg` já traz `v0001` (`int64`) e `AREA_KM2` (`float64`), o CSV básico nacional foi retirado do pipeline.
- Malha espacial: `RS_setores_CD2022.gpkg` (camada `RS_setores_CD2022`, CRS `EPSG:4674`)

### Chaves de identificação e filtro
- **Código do setor:** `CD_SETOR` (`RS_setores_CD2022.gpkg` e `renda_responsavel`) e **`CD_setor`** (com `setor` minúsculo em `demografia`).
- **Código do município (Porto Alegre):** `CD_MUN == "4314902"` (7 dígitos). Existe no `.gpkg`; em `demografia` e `renda_responsavel`, filtrar por `CD_SETOR.str.startswith("4314902")` ou via `merge`.

### Colunas de interesse
| Bloco | Coluna | Descrição | Observações |
| :--- | :--- | :--- | :--- |
| Setores (`.gpkg`) | `v0001` | Total de pessoas | Já vem em `int64` (no `.xlsx` aparece `V0001`) |
| Setores (`.gpkg`) | `AREA_KM2` | Área do setor em km² | Já vem em `float64` no `.gpkg` |
| Setores (`.gpkg`) | `SITUACAO`, `CD_SIT` | Situação do setor | POA: `1`, `2` (Urbana); `5`, `7`, `8` (Rural); `9` (massa d'água/`NaN`, `v0001=0`) |
| Setores (`.gpkg`) | `CD_TIPO` | Tipo de setor | POA: `0`, `1`, `2`, `4`, `5`, `6`, `7`, `9` (`1` coincide 100% com `CD_FCU` válido) |
| Setores (`.gpkg`) | `CD_FCU`, `NM_FCU` | Favelas e Comunidades Urbanas | Sem FCU usa `"."` em `CD_FCU` e `NaN` em `NM_FCU` (`2.421` sem FCU; `323` com FCU) |
| Demografia | `V01006` | Quantidade de moradores | — |
| Demografia | `V01040` | Pessoas de 60 a 69 anos | Somar `V01040 + V01041` para obter 60+ (ambos os sexos) |
| Demografia | `V01041` | Pessoas de 70 anos ou mais | Por sexo: masc. `V01018 + V01019`; fem. `V01029 + V01030` |
| Renda do Responsável | `V06001` | Pessoas responsáveis em DPPO | Domicílios Particulares Permanentes Ocupados |
| Renda do Responsável | `V06004` | Rendimento nominal médio mensal | Apenas responsáveis **com rendimentos** (exclui renda zero); CSV usa **ponto** decimal |
| Renda do Responsável | `V06006` | Rendimento nominal mediano mensal | Apenas responsáveis **com rendimentos**; menos sensível a outliers |

**Contagem de responsáveis com/sem rendimento e exclusão de `V06005`:** o dicionário `dicionario_de_dados_renda_responsavel_20260508.xlsx` possui apenas 6 variáveis e não traz uma contagem separada de responsáveis com rendimento ou sem rendimento. `V06001` conta todos os responsáveis em domicílios particulares permanentes ocupados; `V06004`, `V06005` (variância do rendimento nominal mensal — descartada por não ter uso no modelo) e `V06006` são indicadores apenas das pessoas responsáveis com rendimentos. Portanto, não existe neste dicionário um código direto para calcular a parcela com renda zero; essa estimativa exigiria outra base ou regra derivada que não está documentada aqui.

### Sigilo, omissões e cuidados na junção
- **Sigilo estatístico:** representado por **`"X"`** (em POA: `18` em `V01006`, `31` em `V01040`, `48` em `V01041` e `18` em cada coluna de renda `V06001`/`V06004`/`V06006`) -> converter para `NaN` via `pd.to_numeric(..., errors="coerce")`.
- **Setores sem moradores (`v0001 == 0`):** aparecem com `0` no `.gpkg`, mas **não têm linha** em `demografia` e `renda` (`2.744` setores únicos no `.gpkg` vs. `2.713` em `demografia`/`renda` em POA).
- **Geometrias multipolígono no `.gpkg`:** `RS_setores_CD2022.gpkg` possui `2.748` linhas para `2.744` setores únicos em POA — há **4 setores divididos em 2 polígonos distintos cada**, repetindo os mesmos atributos (`v0001` e `AREA_KM2`):
  - `431490205001131` (Vila Conceição, `v0001 = 373`)
  - `431490205001259` (Belém Novo, `v0001 = 544`)
  - `431490205003016` (Boa Vista do Sul, `v0001 = 150`)
  - `431490205003029` (Arquipélago, `v0001 = 0`)
  - *Atenção:* somar `v0001` antes de unificar gera `+1.067` moradores duplicados (`1.333.912` vs. `1.332.845` reais). Na limpeza, usar **`dissolve(by="CD_SETOR", aggfunc="first", as_index=False)`** (declarando `aggfunc="first"` explicitamente para evitar que uma mudança para `"sum"` reintroduza os moradores duplicados; nunca `drop_duplicates`, que descartaria parte da geometria do setor).
- **Consistência `v0001` vs. `V01006` (após `dissolve`):**
  - `2.695` setores comparáveis (numéricos): **`0` divergências** (`v0001 == V01006` em 100%, soma exata `1.330.054`).
  - `31` setores ausentes em `demografia_poa`: todos têm `v0001 = 0`.
  - `18` setores com sigilo (`"X"`) em `V01006`: somam `2.791` moradores em `v0001`.
  - Portanto, `v0001` (do `.gpkg`) é a coluna mais completa para população total.
- **Distribuição por `CD_SIT` (após `dissolve`, `2.744` setores / `1.332.845` hab):**
  - `1` (Urbana): `2.630` setores | `1.293.352` hab (`97,04%`) | `233,25 km²`
  - `2` (Urbana): `87` setores | `37.076` hab (`2,78%`) | `192,24 km²`
  - `5`, `7`, `8` (Rural): `21` setores (`2 + 8 + 11`) | `2.417` hab (`0,18%`) | `51,82 km²`
  - `9` (Massa d'água / `NaN`): `6` setores | `0` hab (`0,00%`) | `18,08 km²`
- **Distribuição por `CD_TIPO` (após `dissolve`):**
  - `0` (Comum): `2.359` setores (`7` com pop `0`) | `1.152.474` hab (`86,47%`) | `433,36 km²`
  - `1` (FCU): `323` setores (`1` com pop `0`) | `175.519` hab (`13,17%`) | `23,22 km²` — correspondência exata `1:1` com `CD_FCU != "."`
  - `2`: `1` setor (Partenon) | `0` hab | `0,27 km²`
  - `4`: `34` setores (`17` com pop `0`) | `231` hab (`0,02%`) | `36,62 km²`
  - `5`: `8` setores (`2` com pop `0`) | `302` hab (`0,02%`) | `1,33 km²`
  - `6`: `7` setores (`3` com pop `0`) | `2.801` hab (`0,21%`) | `0,22 km²` — concentrados em Coronel Aparício Borges (`2.033` em `0,077 km²`) e Partenon (`474` e `247`); perfil institucional/prisional que distorce densidade e não gera demanda de mobilidade ativa
  - `7`: `6` setores (`0` com pop `0`) | `398` hab (`0,03%`) | `0,18 km²`
  - `9`: `6` setores (`0` com pop `0`) | `1.120` hab (`0,08%`) | `0,19 km²`

---

## 2. CNES — Estabelecimentos de Saúde

**Fontes:**
- `SCNES_DOMINIOS.XLS` (formato `.xlsx` internamente)
- `SCNES_DICIONARIO_DE_DADOS/DICIONARIO_DE_DADOS.docx` (`TB_ESTABELECIMENTO`)
- `cnes_estabelecimentos.csv` (encoding explícito `cp1252`, separador `;` — evitar detecção automática `cp1250`)

### Colunas exatas no CSV
- **Município:** `CO_IBGE` — **6 dígitos** (Porto Alegre = **`"431490"`**; `10.294` linhas).
- **Identificação:** `CO_CNES`, `CO_UNIDADE`, `NO_FANTASIA`, `NO_RAZAO_SOCIAL`.
- **Tipo de unidade:** `TP_UNIDADE` (no CSV vem **sem zero à esquerda** para `<10`, ex.: `"2"`, `"4"`, `"5"`, `"7"`).
- **Natureza jurídica:** `CO_NATUREZA_JUR` (`1xxx` = Administração Pública; `2xxx` = Entidades Empresariais, ex.: `2011` Empresa Pública; `3xxx` = Sem Fins Lucrativos; `4xxx` = Pessoa Física).
  - *Atenção:* `DS_ESFERA_ADMINISTRATIVA` no CSV traz `MUNICIPAL` / `ESTADUAL` / `DUPLA` (espelhando `TP_GESTAO`), **não** diferencia público de privado.
- **Vínculo SUS:** `CO_AMBULATORIAL_SUS` (`"SIM"` / `"NAO"`).
- **Desativação:** `CO_MOTIVO_DESAB` (vazio = ativo; códigos `01` a `14` = desativado).
- **Coordenadas:** `NU_LATITUDE`, `NU_LONGITUDE` (`92` linhas em POA sem coordenadas).

### Códigos de `TP_UNIDADE` (aba `TIPOS DE ESTABELECIMENTO`)
- **Manter (após filtrar ativos):**
  - `01` (`1`): Posto de Saúde
  - `02` (`2`): Centro de Saúde / Unidade Básica (`142` ativos em POA)
  - `04` (`4`): Policlínica (`22` ativos)
  - `05` (`5`): Hospital Geral (`20` ativos)
  - `07` (`7`): Hospital Especializado (`11` ativos)
  - `20` (`20`): Pronto Socorro Geral / `21` (`21`): Pronto Socorro Especializado (`2` ativos)
  - `70` (`70`): Centro de Atenção Psicossocial / CAPS (`21` ativos)
  - `73` (`73`): Pronto Atendimento / UPA (`7` ativos)
- **Excluir:**
  - **Desativados:** `CO_MOTIVO_DESAB` preenchido (`1.091` linhas em POA, restando `9.203` ativas).
  - **Isolados / apoio / gestão:** `22` (Consultório Isolado), `36` (Clínica/Centro de Especialidade), `39` (SADT Isolado), `43` (Farmácia), `60` (Cooperativa), `68` (Central de Gestão), `77` (Home Care), `81` (Central de Regulação), `40`/`42` (Unidades Móveis), etc.

---

## 3. Decisões de Limpeza Definidas (Guia de Implementação)

1. **Idosos (IBGE):** converter `"X"` em `V01040` (`31` setores) e `V01041` (`48` setores) para **`NaN` — nunca zero** — antes de somar `V01040 + V01041` (se qualquer faixa estiver em sigilo, o total 60+ permanece `NaN`). Priorizar o **percentual de idosos** (`idosos_60_mais / v0001`) nas análises comparativas/espaciais, mantendo o absoluto apenas como referência de volume.
2. **Território (IBGE):**
   - **Exclusão definitiva da modelagem de demanda (`14` setores):** `CD_TIPO == "6"` (`7` setores, `2.801` hab), `CD_SIT == "9"` (`6` setores de massa d'água, `0` hab) e `CD_TIPO == "2"` (`1` setor, `0` hab).
   - **Flag territorial de vulnerabilidade:** o modelo usará **apenas `is_fcu` (`CD_TIPO == "1"`, `323` setores)** como flag territorial de vulnerabilidade — **sem** criar flag genérica de setor especial para `CD_TIPO` em `4, 5, 7, 9` (mantendo a coluna `CD_TIPO` original apenas para auditoria).
   - **Zona rural (`CD_SIT` em `5, 7, 8` — `21` setores, `51,82 km²`, `2.417` hab / `0,18%`):** tratados como setores comuns na modelagem (deixando a baixa densidade natural reduzir seu peso), mantendo uma flag auxiliar **`is_rural`** (`CD_SIT` em `5, 7, 8`) apenas para filtragem visual de mapas urbanos quando necessário.
   - **Setores terrestres sem moradores (`v0001 == 0`):** dos `31` setores com `v0001 == 0` em POA, `10` são removidos pelas exclusões acima (`6` de `CD_SIT == "9"`, `1` de `CD_TIPO == "2"` e `3` vazios de `CD_TIPO == "6"`, sem sobreposição). Os **`21` setores terrestres vazios restantes** continuam no arquivo para não abrir buracos no mapa, com **densidade `0`** e **`NaN` (sem imputação)** em renda e `%` idosos.
   - **Veredito final do IBGE (auditoria `c12-inspecao-sigilo-tipo7`):**
     - Dos `18` setores com sigilo `V01006 == "X"` (`2.791` hab), `3` (`2.327` hab — `83,4%`) já são eliminados pela regra de `CD_TIPO == "6"`. Sobram `15` setores (`464` hab): `6` de `CD_TIPO == "7"` (`398` hab), `7` de `CD_TIPO == "4"` (`43` hab), `1` de `CD_TIPO == "5"` (`19` hab) e `1` de `CD_TIPO == "0"` (`4` hab).
     - **`CD_TIPO == "7"` (todos os 6 setores mantidos):** todos os 6 já estão mascarados com `"X"` em `V01006`, `V01040`, `V01041` e `V06006` (zero risco de outlier em `%` idosos ou renda) e nenhum gera outlier de densidade — o maior (`431490205002972`, Cristal: `35.721,4` hab/km²) fica abaixo do `p95` de POA (`39.483,7` hab/km²) e os outros 5 ficam abaixo da mediana (`9.471,4` hab/km²).
     - **Setores mantidos com sigilo:** os setores residenciais/mantidos com `"X"` continuam no mapa com `NaN` em renda e/ou idosos, preservando a continuidade espacial sem imputar zero.
3. **Área (IBGE):** usar `AREA_KM2` que já vem em `float64` no `RS_setores_CD2022.gpkg`, conferindo a integridade das geometrias após `dissolve(by="CD_SETOR", aggfunc="first", as_index=False)`.
4. **Renda (IBGE):** usar **`V06006` (mediana)** como métrica principal (junto com `V06004` como apoio), registrando na documentação que o indicador considera apenas responsáveis **com rendimento positivo** e que valores `"X"` são sigilo estatístico (diferentes de setores sem moradores).
5. **CNES ativos:** filtrar obrigatoriamente `CO_MOTIVO_DESAB.isna()`.
6. **CNES SUS / público vs. privado:** combinar `CO_AMBULATORIAL_SUS == "SIM"` **OU** `CO_NATUREZA_JUR` pública (`1xxx` / `2011`), porque:
   - Filtrar só `CO_AMBULATORIAL_SUS == "SIM"` excluiria 8 CAPS e 9 UBS públicas;
   - Filtrar só `CO_NATUREZA_JUR` `1xxx` excluiria o Hospital Conceição (`2011`) e filantrópicos conveniados ao SUS como Santa Casa (`3069`) e Divina Providência (`3999`).
   - Revisar pontualmente exceções (ex.: unidades militares `HBMPA` / campanhas temporárias) e manter flag de atendimento SUS caso se decida comparar rede SUS vs. total hospitalar.

**Atendimento hospitalar no dicionário CNES:** o `DICIONARIO_DE_DADOS.docx` confirma uma coluna específica hospitalar SUS, `CO_HOSPITALAR_SUS`, além de `CO_HOSPITALAR` para atendimento hospitalar não SUS e `CO_AMBULATORIAL_SUS` para atendimento ambulatorial SUS. O CSV aberto não traz `CO_HOSPITALAR_SUS`; ele contém `ST_ATEND_HOSPITALAR` e `CO_AMBULATORIAL_SUS`. Assim, para identificar vínculo SUS ambulatorial, a regra atual continua baseada em `CO_AMBULATORIAL_SUS == "SIM"` combinada com natureza jurídica pública; `ST_ATEND_HOSPITALAR` só identifica existência de atendimento hospitalar, não vínculo exclusivo com o SUS.

---

## 4. Esquemas das Bases Complementares Restantes

### Escolas

- Fonte: `Tabela_da_lista_das_escolas_Detalhado.csv` (encoding explícito `utf-8-sig` para remover BOM `\ufeff`, separador `,`).
- A base possui 988 linhas e todos os registros são de **`Município == "Porto Alegre"`**, UF **RS**.
- Município: `Município`; a própria base já confirma que não há registros de outros municípios.
- Situação de funcionamento: a coluna `Restrição de Atendimento` contém 941 escolas em funcionamento sem restrição, 33 paralisadas e 14 que atendem exclusivamente alunos com deficiência. Não há uma categoria explícita chamada "extinta"; para excluir estabelecimentos encerrados, paralisadas devem ser tratadas como não ativas até haver uma regra mais específica.
- Rede: `Categoria Administrativa` informa 636 escolas privadas e 352 públicas; `Dependência Administrativa` detalha 636 privadas, 246 estaduais, 101 municipais e 5 federais.
- Coordenadas: `Latitude` e `Longitude` não apresentam `NaN` originais na leitura como texto, mas **`153` das `988` linhas contêm apenas espaços em branco** (`'                              '`) e não convertem com `pd.to_numeric(..., errors="coerce")`, deixando `835` escolas com coordenadas numéricas válidas.

### Assistência Social

- O `.csv` possui 35 linhas e cinco colunas: `categoria`, `nome`, `endereco`, `latitude`, `longitude`.
- O `.gpkg` possui 35 linhas e a mesma tabela mais `geometry`, na camada `assistencia_social_poa_100_oficial`, CRS `EPSG:4674`.
- Os cinco atributos comuns possuem os mesmos valores em ambos os formatos. O `.csv` é a versão tabular sem a geometria.
- A coluna que identifica o tipo de equipamento é `categoria`: 23 CRAS, 9 CREAS e 3 Centro POP.
- Coordenadas estão em `latitude` e `longitude` no `.csv`; no `.gpkg`, a mesma localização está em `geometry`, com os valores também presentes como atributos.

### Favelas / FCUs

- Pasta: `poligonos_FCUs_shp`.
- Os arquivos auxiliares estão presentes: `.shp`, `.shx`, `.dbf`, `.prj` e `.cpg`.
- A leitura foi bem-sucedida com GeoPandas/pyogrio: 12.348 feições no Brasil (`125` feições e `125` `cd_fcu` únicos em Porto Alegre), CRS `EPSG:4674`.
- Colunas principais observadas: `cd_fcu`, `nm_fcu`, `cd_uf`, `nm_uf`, `sigla_uf`, `cd_mun`, `nm_mun` e `geometry`.
- **Redundância com `RS_setores_CD2022.gpkg`:** os `125` `cd_fcu` de `fcu_poa` coincidem 100% (`0` exclusivos em cada lado) com os `125` `CD_FCU` válidos presentes nos `323` setores com `CD_TIPO == "1"` de `setores_poa`. Para análises por setor, a flag `is_fcu` já pode ser derivada direto do `.gpkg` sem spatial join; o shapefile fica apenas como camada opcional para plotar os contornos agregados das 125 comunidades.
