# Modelagem de grafo para rede de grafos de video games

Este projeto analisa como os jogos de videogame se conectam entre si com base no comportamento dos jogadores. Abaixo, explicamos de forma simples como transformamos uma lista de avaliações em um mapa completo do universo dos games.

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

Depois de clonar o repositório e executar `uv sync`, rode `uv run pytest` para conferir os exemplos do código. As Partes I e II já podem ser executadas com os arquivos versionados em `data/processado/`. Para abrir os notebooks, rode `uv run jupyter lab` na raiz do projeto.

### Obter os dados brutos

Na página [Amazon Review Data (2018)](https://cseweb.ucsd.edu/~jmcauley/datasets/amazon_v2/), selecione a categoria **Video Games**. Baixe os dois arquivos abaixo e salve-os em `data/raw/` com os nomes indicados. Mantenha os metadados compactados.

| Arquivo | Onde baixar |
| --- | --- |
| `Video_Games.csv` | [Ratings only, com 2.565.349 avaliações](https://mcauleylab.ucsd.edu/public_datasets/data/amazon_v2/categoryFilesSmall/Video_Games.csv) |
| `meta_Video_Games.json.gz` | [Metadata da categoria](https://mcauleylab.ucsd.edu/public_datasets/data/amazon_v2/metaFiles2/meta_Video_Games.json.gz) |

Os dados brutos ficam fora da entrega. Para consultar os resultados ou executar as partes I e II, use os arquivos já incluídos em `data/processado/`. A Parte III volta a ler `Video_Games.csv` para construir o modelo nulo bipartido. Os dois arquivos brutos são necessários para refazer o pré-processamento completo.

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
| 2 | [Parte I — Topologia](notebooks/01_parte1.ipynb) | 4 min |
| 3 | [Parte II — Algoritmos e tempos](notebooks/02_parte2.ipynb) | 7,5 min |
| 4 | [Parte III — Pequeno mundo, lei de potência e robustez](notebooks/03_parte3.ipynb) | 9 min |

Os tempos são aproximados e dependem da máquina. Os notebooks gravam tabelas em `results/` e figuras em `imagens/`. O repositório inclui as [medições da Parte II](results/parte2_tempos.csv) e a [comparação dos limiares de coavaliação](results/parte3_sensibilidade.csv). Para rodar os testes e os exemplos executáveis dos módulos, use `uv run pytest`.

## 5. Arquivos da entrega

Os dados tratados estão incluídos em [`data/processado/`](data/processado/):

| Arquivo | Conteúdo |
| --- | --- |
| `funil.csv` | Contagens de usuários, produtos e arestas em cada etapa do tratamento. |
| `componentes.csv` | Quantidade de componentes por tamanho antes de selecionar a maior componente conexa. |
| `jogos_lcc.csv` | Catálogo dos 21.284 produtos da maior componente conexa. |
| `arestas_lcc.csv.gz` | Lista compactada das 320.742 arestas da maior componente, com pesos de coavaliação. |

O [PDF do relatório](224215943.pdf) e o [fonte LaTeX](relatorio.tex) estão na raiz do projeto. Para recompilar no Overleaf, mantenha `webmedia.cls` e a pasta `imagens/` junto do fonte e selecione `relatorio.tex` como documento principal. O PDF da entrega usa o número da matrícula no nome.
