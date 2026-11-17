# Dataset e EDA — Mobilidade Sustentável em Porto Alegre

## Sobre

Scripts de coleta, limpeza e Análise Exploratória de Dados (EDA) para a criação de um dataset próprio sobre a infraestrutura viária e cicloviária de Porto Alegre.

## Objetivo Atual

Validar a qualidade das fontes, documentar o histórico de limpeza dos dados e gerar o dataset que servirá de base para o projeto.

## Estrutura do Projeto

```text
eld_dataset/
├── data/                     # (Local — não commitado) Criar manualmente
│   ├── 1_raw/                # Dados brutos
│   ├── 2_processing/         # Dados em tratamento
│   └── 3_done/               # Dados prontos
├── notebooks/                # Notebooks por pilar (ex: 02_access_inclusion.ipynb)
├── src/                      # Scripts de coleta de dados e utilitários
├── tests/                    # Testes de código e funcionalidades
└── requirements.txt          # Bibliotecas Python do projeto
```

* **`data/`:** está no `.gitignore` e não é commitado. A estrutura `1_raw/`, `2_processing/` e `3_done/` é uma sugestão de organização e deve ser criada localmente por cada pessoa.
* **`notebooks/`:** cada integrante cria seu notebook conforme o pilar escolhido (exemplo: `02_access_inclusion.ipynb`).
* **`src/`:** scripts usados para puxar dados ou outras rotinas do projeto.
* **`tests/`:** diretório para testar qualquer script ou funcionalidade.

## Rodar o Ambiente

1. **Criar o ambiente virtual na pasta raiz:**
   ```bash
   # Linux ou macOS
   python3 -m venv .venv

   # Windows
   python -m venv .venv
   ```

2. **Ativar o ambiente:**
   ```bash
   # Linux ou macOS
   source .venv/bin/activate

   # Windows (CMD)
   .venv\Scripts\activate

   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   ```

3. **Instalar as bibliotecas:**
   ```bash
   pip install -r requirements.txt
   ```
   > Se instalar alguma biblioteca nova no seu ambiente, adicione o nome dela no `requirements.txt`.

4. **(opcional) Verificar a formatação do código:**
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