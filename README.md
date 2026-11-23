# Rede de coavaliação de produtos de videogame da Amazon

Trabalho Prático da disciplina MATA53 – Teoria dos Grafos (2026.1), IC/UFBA.
Autor: Jaedson Barbosa Macedo, matrícula **224215943**.

**Relatório:** [`224215943.pdf`](224215943.pdf) (fonte LaTeX: [`relatorio.tex`](relatorio.tex))

## Grafo atribuído

$f(M) = (S(M) \times (U(M) + 1)) \bmod 129$, em que $S$ é a soma dos dígitos e $U$ são os dois últimos dígitos da matrícula:

$S = 32$, $U = 43$, $32 \times 44 = 1408$, $1408 \bmod 129 = 118$. O resultado é **G118, web-Amazon**.

Os links de dados da [página do SNAP](https://snap.stanford.edu/data/web-Amazon.html) levam a um [aviso](https://snap.stanford.edu/data/amazon/amazon_readme.txt) que encaminha para a coleção da UCSD. Por isso, usamos a [Amazon Review Data (2018)](https://cseweb.ucsd.edu/~jmcauley/datasets/amazon_v2/), categoria **Video Games**. A Seção 2 do relatório explica essa troca.

Dois produtos ficam ligados quando ao menos dois usuários avaliaram ambos. A análise usa a maior componente conexa, com 21.284 vértices e 320.742 arestas.

## Conteúdo da entrega

| Pedido no enunciado | Onde está |
| --- | --- |
| Códigos e scripts | [`src/`](src/) (implementações próprias), [`notebooks/`](notebooks/) (uma análise por notebook), [`scripts/run_all.py`](scripts/run_all.py) |
| Dados tratados | [`data/processado/`](data/processado/) |
| Como executar | Seção [Como executar](#como-executar) abaixo |
| Tabelas e figuras do relatório | [`results/`](results/) e [`imagens/`](imagens/) |

| Notebook | Conteúdo |
| --- | --- |
| [`01_parte1`](notebooks/01_parte1.ipynb) | Parte I: medidas estruturais, componentes e visualização |
| [`02_parte2`](notebooks/02_parte2.ipynb) | Parte II: BFS, DFS, Euler, Dijkstra, Bellman–Ford, Floyd–Warshall, Tarjan, Prim e Kruskal, com os tempos medidos |
| [`03_parte3`](notebooks/03_parte3.ipynb) | Parte III, Q1 a Q3: pequeno mundo, lei de potência e robustez |
| [`04_consoles`](notebooks/04_consoles.ipynb) | Parte III, Q4: descoberta mais interessante (mapa dos consoles) |
| [`05_modelos`](notebooks/05_modelos.ipynb) | Parte III, Q5 (extra): Erdős–Rényi, Barabási–Albert e Watts–Strogatz |

## Como executar

É preciso ter Python 3.11 e o [uv](https://docs.astral.sh/uv/). Na raiz do projeto:

```bash
uv sync                                  # instala as dependências fixadas em uv.lock
uv run python scripts/run_all.py         # executa os cinco notebooks em ordem
```

Os notebooks gravam as tabelas em `results/` e as figuras em `imagens/`. Opções do `run_all.py`:

- `--sem-parte2` pula a medição de tempos;
- `--notebooks 04 05` executa só os notebooks indicados.

Para abrir os notebooks de forma interativa, use `uv run jupyter lab`. A execução completa leva cerca de 25 minutos; com `--sem-parte2`, cerca de 16.

## Dados

**Dados tratados**, versionados em [`data/processado/`](data/processado/). Bastam para executar todos os notebooks:

| Arquivo | Conteúdo |
| --- | --- |
| [`arestas_lcc.csv.gz`](data/processado/arestas_lcc.csv.gz) | 320.742 arestas da maior componente, com peso de coavaliação |
| [`jogos_lcc.csv`](data/processado/jogos_lcc.csv) | 21.284 produtos da maior componente, com título e plataforma |
| [`funil.csv`](data/processado/funil.csv) | Contagens de cada etapa do tratamento (T1 a T6) |
| [`componentes.csv`](data/processado/componentes.csv) | Quantidade de componentes por tamanho, antes de extrair a maior componente |

**Dados brutos**, opcionais e não redistribuídos. Servem para refazer o pré-processamento. Baixe os arquivos e salve-os em `data/raw/`:

- [`Video_Games.csv`](https://mcauleylab.ucsd.edu/public_datasets/data/amazon_v2/categoryFilesSmall/Video_Games.csv), com 2.565.349 avaliações;
- [`meta_Video_Games.json.gz`](https://mcauleylab.ucsd.edu/public_datasets/data/amazon_v2/metaFiles2/meta_Video_Games.json.gz), sem descompactar.

Quando esses arquivos estão presentes, o `run_all.py` roda antes o pré-processamento (`uv run python -m src.etl.pipeline`). Sem eles, o notebook 03 lê de [`results/`](results/) os resumos do nulo bipartido e da sensibilidade ao limiar, as duas únicas etapas que dependem dos dados brutos.
