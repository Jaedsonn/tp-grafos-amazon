# Rede de coavaliação de produtos de videogame da Amazon

Este projeto analisa como os jogos de videogame se conectam entre si com base no comportamento dos jogadores. Abaixo, explicamos de forma simples como transformamos uma lista de avaliações em um mapa completo do universo dos games.

## Grafo atribuído

Trabalho prático **Analisando Grafos do SNAP**, Teoria dos Grafos, IC/UFBA. Autor: Jaedson Barbosa Macedo, matrícula **224215943**.

O índice do grafo é $f(M) = (S(M) \times (U(M) + 1)) \bmod 129$, em que $S(M)$ é a soma dos dígitos e $U(M)$ os dois últimos dígitos da matrícula (se o resto for 0, usa-se 129):

| Passo | Valor |
| --- | --- |
| Soma dos dígitos $S$ | 2 + 2 + 4 + 2 + 1 + 5 + 9 + 4 + 3 = **32** |
| Dois últimos dígitos $U$ | **43** |
| $S \times (U + 1)$ | 32 × 44 = 1.408 |
| $1.408 \bmod 129$ | 1.408 − 10 × 129 = **118** |

Grafo atribuído: **G118 — web-Amazon**.

## Execução rápida

```bash
uv sync
uv run python scripts/run_all.py
```

O `run_all` roda o pré-processamento (se os arquivos brutos estiverem em `data/raw/`) e os cinco notebooks, na ordem, gravando tabelas em `results/` e figuras em `imagens/`. Sem os dados brutos, tudo roda com os arquivos de `data/processado/`. Para não remedir os tempos da Parte II, use `--sem-parte2`; para escolher notebooks, `--notebooks 04 05`.

## Checklist do enunciado

| Requisito | Onde está |
| --- | --- |
| Cálculo de determinação do grafo | Seção acima; relatório, Seção 2 |
| Código, dados tratados e README | `src/`, `notebooks/`, `scripts/run_all.py`; [`data/processado/`](data/processado/); este arquivo |
| Descrição do grafo original e tratamento | Relatório, Seção 3; `src/etl/`; [`funil.csv`](data/processado/funil.csv) |
| Metodologia | Relatório, Seção 4 |
| **Parte I** — vértices, arestas, graus, distribuição, densidade | [`01_parte1`](notebooks/01_parte1.ipynb); `src/parte1/topologia.py`; [`parte1_medidas.csv`](results/parte1_medidas.csv) |
| Parte I — componentes e tamanhos | [`componentes.csv`](data/processado/componentes.csv); `src/comum/grafo.py` |
| Parte I — diâmetro, raio, caminho médio (exatos, código próprio) | `src/parte1/distancias.py`, conferido com igraph |
| Parte I — clusterização, triângulos, visualização | `src/parte1/topologia.py`; [`parte1_nucleo_300`](imagens/parte1_nucleo_300.png) |
| Parte I — tabela "computado ou não" | [`parte1_status.csv`](results/parte1_status.csv); relatório, tabela de status da Parte I |
| **Parte II** — BFS, DFS, Euler | [`02_parte2`](notebooks/02_parte2.ipynb); `src/comum/grafo.py`, `src/parte2/buscas.py` |
| Parte II — Dijkstra, Bellman–Ford, Floyd–Warshall | `src/parte2/caminhos_minimos.py` |
| Parte II — Tarjan (componentes fortes; pontes e articulações) | `src/parte2/buscas.py` |
| Parte II — Prim e Kruskal | `src/parte2/arvore_geradora.py` |
| Parte II — complexidade teórica e observada; média, DP e IC (Z se n ≥ 30, t se n < 30) | `src/parte2/desempenho.py`, `src/comum/estatistica.py`; [`parte2_resumo.csv`](results/parte2_resumo.csv), [`parte2_tempos.csv`](results/parte2_tempos.csv) |
| **Parte III, Q1** — small-world, código próprio, contra ER e nulo bipartido | [`03_parte3`](notebooks/03_parte3.ipynb); `src/parte3/pequeno_mundo.py`; [`parte3_pequeno_mundo.csv`](results/parte3_pequeno_mundo.csv) |
| Q2 — lei de potência (MLE, KS, razão de verossimilhança) | `src/parte3/lei_potencia.py`; [`parte3_lei_potencia.csv`](results/parte3_lei_potencia.csv) |
| Q3 — robustez aleatória e direcionada, métricas A–D, boxplot | `src/parte3/robustez.py`; [`parte3_robustez.csv`](results/parte3_robustez.csv) |
| Q4 — descoberta mais interessante (mapa dos consoles) | [`04_consoles`](notebooks/04_consoles.ipynb); `src/parte3/consoles.py`; `results/parte3_consoles_*.csv` |
| Q5 (extra) — ER, BA e WS simulados com código próprio | [`05_modelos`](notebooks/05_modelos.ipynb); `src/parte3/modelos.py`; [`parte3_modelos.csv`](results/parte3_modelos.csv) |
| Relatório no template WebMedia, PDF com a matrícula | [`relatorio.tex`](relatorio.tex), [`224215943.pdf`](224215943.pdf) |

## 1. O nosso Dataset (Os Dados)
O grafo atribuído é o **G118 — web-Amazon**. Na página [web-Amazon do SNAP](https://snap.stanford.edu/data/web-Amazon.html), os links dos arquivos remetem ao [aviso de acesso](https://snap.stanford.edu/data/amazon/amazon_readme.txt), que encaminha para a [página da coleção na UCSD](https://nijianmo.github.io/amazon/index.html). Usamos **Amazon Review Data (2018), categoria Video Games**, com 2.565.349 avaliações. A categoria permite estudar coavaliações de jogos, consoles e acessórios em um recorte viável para o trabalho.

Cada linha registra **quem** avaliou, **qual produto**, **qual nota** e **quando**. Para construir o grafo estático, usamos apenas o par usuário–produto.

## 2. Tipos de Grafos: Usuário-Jogo vs. Jogo-Jogo
Para transformar essa tabela em uma rede, pensamos em duas abordagens diferentes:

* **A visão Usuário-Jogo (Grafo Bipartido):** É a forma mais direta de olhar os dados. De um lado ficam os usuários, do outro ficam os jogos. Uma linha liga a pessoa ao produto que ela avaliou. Nessa visão, os vínculos entre produtos aparecem indiretamente, por caminhos que passam pelos usuários.

* **A visão Jogo-Jogo (Grafo Projetado):** É a visão que escolhemos. Aqui, nós ligamos os jogos diretamente uns aos outros, criando uma rede dos produtos da categoria Video Games. Mas como fazemos isso se os dados originais não conectam os jogos? A resposta está nos jogadores em comum.

## 3. Como modelamos o nosso Grafo Final (Jogo-Jogo)
Nossa ideia final foi usar os usuários como "pontes". A regra é muito simples:

Se a Maria avaliou o *Jogo A* e também avaliou o *Jogo B*, nós desenhamos uma linha conectando o *Jogo A* diretamente ao *Jogo B*. Nós assumimos que existe uma relação ali.

Se 500 pessoas avaliaram ambos os títulos, o **peso** da aresta é 500. Na rede analisada, mantemos apenas as arestas com peso de pelo menos dois.

Depois de aplicar essa regra para todos os jogadores da base de dados, nós basicamente "apagamos" as pessoas do desenho. O que sobra é uma rede de jogos, consoles e acessórios conectados por coavaliações.

**Por que fizemos isso?**
A projeção permite observar grupos de produtos associados a uma plataforma e identificar itens centrais que conectam grupos diferentes.

## 4. Como reproduzir

### Preparar o ambiente

Na raiz do projeto, com o `uv` instalado, execute:

```bash
uv sync
```

O projeto usa Python 3.11. As versões das dependências estão em `uv.lock`.

### Rodar com os dados tratados

Depois de clonar o repositório e executar `uv sync`, todos os notebooks rodam com os arquivos versionados em `data/processado/`. Para abri-los, rode `uv run jupyter lab` na raiz do projeto.

### Obter os dados brutos

Na página [Amazon Review Data (2018)](https://cseweb.ucsd.edu/~jmcauley/datasets/amazon_v2/), selecione a categoria **Video Games**. Baixe os dois arquivos abaixo e salve-os em `data/raw/` com os nomes indicados. Mantenha os metadados compactados.

| Arquivo | Onde baixar |
| --- | --- |
| `Video_Games.csv` | [Ratings only, com 2.565.349 avaliações](https://mcauleylab.ucsd.edu/public_datasets/data/amazon_v2/categoryFilesSmall/Video_Games.csv) |
| `meta_Video_Games.json.gz` | [Metadata da categoria](https://mcauleylab.ucsd.edu/public_datasets/data/amazon_v2/metaFiles2/meta_Video_Games.json.gz) |

Os dados brutos ficam fora da entrega. Eles só são necessários para refazer o pré-processamento e duas etapas da Parte III, o nulo bipartido e a sensibilidade ao limiar. Sem eles, o notebook 03 lê os resumos dessas duas etapas em [`parte3_nulo_bipartido.csv`](results/parte3_nulo_bipartido.csv) e [`parte3_sensibilidade.csv`](results/parte3_sensibilidade.csv), gravados pela última execução com os dados brutos, e recalcula todo o resto.

### Regenerar os dados tratados e executar os notebooks

Execute os comandos na raiz do projeto:

```bash
uv run python -m src.etl.pipeline
uv run jupyter lab
```

No JupyterLab, abra os notebooks pelo diretório `notebooks/`, selecione o kernel Python do ambiente criado pelo `uv` e execute todas as células de cada notebook na ordem abaixo.

| Ordem | Etapa | Tempo observado |
| --- | --- | ---: |
| 1 | Pré-processamento com `uv run python -m src.etl.pipeline` | 14 s |
| 2 | [Parte I — Topologia](notebooks/01_parte1.ipynb) | 8 min |
| 3 | [Parte II — Algoritmos e tempos](notebooks/02_parte2.ipynb) | 7,5 min |
| 4 | [Parte III — Pequeno mundo, lei de potência e robustez](notebooks/03_parte3.ipynb) | 14 min |
| 5 | [Parte III, Q4 — Concentração em consoles](notebooks/04_consoles.ipynb) | 2 min |
| 6 | [Parte III, Q5 — Modelos clássicos](notebooks/05_modelos.ipynb) | 6 min |

Os tempos são aproximados e dependem da máquina. Os notebooks gravam tabelas em `results/` e figuras em `imagens/`. O repositório inclui as [medições da Parte II](results/parte2_tempos.csv) a [comparação dos limiares de coavaliação](results/parte3_sensibilidade.csv) e o [resumo da análise de consoles](results/parte3_consoles_resumo.csv). O notebook de consoles usa só os arquivos de `data/processado/` e roda sem os dados brutos.

## 5. Arquivos da entrega

Os dados tratados estão incluídos em [`data/processado/`](data/processado/):

| Arquivo | Conteúdo |
| --- | --- |
| `funil.csv` | Contagens de usuários, produtos e arestas em cada etapa do tratamento. |
| `componentes.csv` | Quantidade de componentes por tamanho antes de selecionar a maior componente conexa. |
| `jogos_lcc.csv` | Catálogo dos 21.284 produtos da maior componente conexa. |
| `arestas_lcc.csv.gz` | Lista compactada das 320.742 arestas da maior componente, com pesos de coavaliação. |

O [PDF do relatório](224215943.pdf) e o [fonte LaTeX](relatorio.tex) estão na raiz do projeto. Para recompilar no Overleaf, mantenha `webmedia.cls` e a pasta `imagens/` junto do fonte e selecione `relatorio.tex` como documento principal. O PDF da entrega usa o número da matrícula no nome.
