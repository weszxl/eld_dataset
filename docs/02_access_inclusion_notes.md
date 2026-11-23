# Notas de Dicionários e Regras de Limpeza — Pilar 2 (Acesso e Inclusão)

Levantamento dos dicionários e schemas reais em `data/1_raw/` antes do processamento das bases.

---

## 1. IBGE — Censo 2022 (Setores Censitários)

**Fontes:**
- `dicionario_de_dados_agregados_por_setores_censitarios_20261113.xlsx`
- `dicionario_de_dados_renda_responsavel_20260508.xlsx`
- CSVs: `Agregados_por_setores_basico_BR.csv`, `Agregados_por_setores_demografia_BR.csv`, `Agregados_por_setores_renda_responsavel_BR.csv` (separador `;`)
- Malha espacial: `RS_setores_CD2022.gpkg` (camada `RS_setores_CD2022`, CRS `EPSG:4674`)

### Chaves de identificação e filtro
- **Código do setor:** `CD_SETOR` (`basico`, `renda_responsavel` e `.gpkg`) e **`CD_setor`** (com `setor` minúsculo em `demografia`).
- **Código do município (Porto Alegre):** `CD_MUN == "4314902"` (7 dígitos). Existe apenas no `basico` e no `.gpkg`; em `demografia` e `renda_responsavel`, filtrar por `CD_SETOR.str.startswith("4314902")` ou via `merge`.

### Colunas de interesse
| Bloco | Coluna | Descrição | Observações |
| :--- | :--- | :--- | :--- |
| Básico / `.gpkg` | `v0001` | Total de pessoas | Minúsculo nos arquivos reais (no `.xlsx` aparece `V0001`) |
| Básico / `.gpkg` | `AREA_KM2` | Área do setor em km² | No CSV `basico` usa **vírgula** decimal; no `.gpkg` já é `REAL` |
| Básico / `.gpkg` | `SITUACAO`, `CD_SIT` | Situação do setor | POA: `1`, `2` (Urbana); `5`, `7`, `8` (Rural); `9` (massa d'água/Arquipélago, `v0001=0`) |
| Básico / `.gpkg` | `CD_TIPO` | Tipo de setor | POA: `0`, `1`, `2`, `4`, `5`, `6`, `7`, `9` (`1` coincide com `NM_FCU`) |
| Básico / `.gpkg` | `CD_FCU`, `NM_FCU` | Favelas e Comunidades Urbanas | Campos sem valor usam `"."` no CSV `basico` |
| Demografia | `V01006` | Quantidade de moradores | — |
| Demografia | `V01040` | Pessoas de 60 a 69 anos | Somar `V01040 + V01041` para obter 60+ (ambos os sexos) |
| Demografia | `V01041` | Pessoas de 70 anos ou mais | Por sexo: masc. `V01018 + V01019`; fem. `V01029 + V01030` |
| Renda do Responsável | `V06001` | Pessoas responsáveis em DPPO | Domicílios Particulares Permanentes Ocupados |
| Renda do Responsável | `V06004` | Rendimento nominal médio mensal | Apenas responsáveis **com rendimentos** (exclui renda zero); CSV usa **ponto** decimal |
| Renda do Responsável | `V06006` | Rendimento nominal mediano mensal | Apenas responsáveis **com rendimentos**; menos sensível a outliers |

### Sigilo, omissões e cuidados na junção
- **Sigilo estatístico:** representado por **`"X"`** (`3.116` ocorrências em `demografia` e `108` em `renda` para POA) -> converter para `NaN` antes de tipar como numérico.
- **Setores sem moradores (`v0001 == 0`):** aparecem com `0` no `basico`, mas **não têm linha** em `demografia` e `renda` (`2.744` setores no `basico` vs. `2.713` em `demografia`/`renda` em POA).
- **Geometrias no `.gpkg`:** `RS_setores_CD2022.gpkg` possui `2.748` linhas para POA (`4` linhas extras por setores com múltiplas partes no Arquipélago) -> fazer `dissolve(by="CD_SETOR")` se precisar garantir 1 linha por setor.

---

## 2. CNES — Estabelecimentos de Saúde

**Fontes:**
- `SCNES_DOMINIOS.XLS` (formato `.xlsx` internamente)
- `SCNES_DICIONARIO_DE_DADOS/DICIONARIO_DE_DADOS.docx` (`TB_ESTABELECIMENTO`)
- `cnes_estabelecimentos.csv` (separador `;`)

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

1. **Idosos (IBGE):** somar `V01040 + V01041` e priorizar o **percentual de idosos** (`idosos_60_mais / v0001`) nas análises comparativas/espaciais, mantendo o absoluto apenas como referência de volume.
2. **Território (IBGE):** remover `CD_SIT == "9"` (massas d'água sem moradores); avaliar `CD_TIPO` (`4, 5, 6, 7, 9`) e `CD_SIT` rural (`5, 7, 8`) com flags antes de descartar, pois alguns setores especiais concentram moradores.
3. **Área (IBGE):** usar `AREA_KM2` já presente na base (padronizando separador decimal), evitando recálculo desnecessário, mas conferindo geometrias após `dissolve` no `.gpkg`.
4. **Renda (IBGE):** usar **`V06006` (mediana)** como métrica principal (junto com `V06004` como apoio), registrando na documentação que o indicador considera apenas responsáveis **com rendimento positivo** e que valores `"X"` são sigilo estatístico (diferentes de setores sem moradores).
5. **CNES ativos:** filtrar obrigatoriamente `CO_MOTIVO_DESAB.isna()`.
6. **CNES SUS / público vs. privado:** combinar `CO_AMBULATORIAL_SUS == "SIM"` **OU** `CO_NATUREZA_JUR` pública (`1xxx` / `2011`), porque:
   - Filtrar só `CO_AMBULATORIAL_SUS == "SIM"` excluiria 8 CAPS e 9 UBS públicas;
   - Filtrar só `CO_NATUREZA_JUR` `1xxx` excluiria o Hospital Conceição (`2011`) e filantrópicos conveniados ao SUS como Santa Casa (`3069`) e Divina Providência (`3999`).
   - Revisar pontualmente exceções (ex.: unidades militares `HBMPA` / campanhas temporárias) e manter flag de atendimento SUS caso se decida comparar rede SUS vs. total hospitalar.

