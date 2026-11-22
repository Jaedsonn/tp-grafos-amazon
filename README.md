# Modelagem de grafo para rede de grafos de video games

Este projeto analisa como os jogos de videogame se conectam entre si com base no comportamento dos jogadores. Abaixo, explicamos de forma simples como transformamos uma lista de avaliações em um mapa completo do universo dos games.

## 1. O nosso Dataset (Os Dados)
Nosso ponto de partida é uma base de dados de avaliações (reviews) da Amazon. É basicamente um histórico de consumo enorme. Cada linha da nossa tabela nos diz três coisas principais: **quem** é o usuário, **qual** jogo ele avaliou e **quando** isso aconteceu. 

## 2. Tipos de Grafos: Usuário-Jogo vs. Jogo-Jogo
Para transformar essa tabela em uma rede, pensamos em duas abordagens diferentes:

* **A visão Usuário-Jogo (Grafo Bipartido):** É a forma mais direta de olhar os dados. De um lado ficam os usuários, do outro ficam os jogos. Uma linha liga a pessoa ao jogo que ela comprou. O problema dessa visão é que **um jogo nunca se conecta a outro jogo**. Sendo assim, é impossível ver "panelinhas" de jogos parecidos ou nichos de consoles.

* **A visão Jogo-Jogo (Grafo Projetado):** É a visão que escolhemos. Aqui, nós ligamos os jogos diretamente uns aos outros, criando um mapa apenas de games. Mas como fazemos isso se os dados originais não conectam os jogos? A resposta está nos jogadores em comum.

## 3. Como modelamos o nosso Grafo Final (Jogo-Jogo)
Nossa ideia final foi usar os usuários como "pontes". A regra é muito simples: 

Se a Maria jogou o *Jogo A* e também jogou o *Jogo B*, nós desenhamos uma linha conectando o *Jogo A* diretamente ao *Jogo B*. Nós assumimos que existe uma relação ali. 

Se 500 pessoas jogaram esses mesmos dois títulos, essa linha de conexão fica muito mais forte. Chamamos isso de **peso**.

Depois de aplicar essa regra para todos os jogadores da base de dados, nós basicamente "apagamos" as pessoas do desenho. O que sobra é uma rede gigantesca feita só de jogos conectados por essas pontes de afinidade.

**Por que fizemos isso?**
Porque ligando jogo com jogo, nossa rede ganha vida. Nós finalmente conseguimos enxergar as comunidades (como jogos de tiro que formam um grande grupo entre si) e conseguimos ver como jogos muito famosos (os grandes sucessos de vendas) funcionam como atalhos, conectando bolhas de jogadores que normalmente não se misturam.