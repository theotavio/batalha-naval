# Batalha Naval

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame CE](https://img.shields.io/badge/Pygame--CE-2.5%2B-brightgreen?style=for-the-badge)
![WebSockets](https://img.shields.io/badge/WebSockets-13.0%2B-black?style=for-the-badge&logo=websocket&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Render](https://img.shields.io/badge/Render-Deployed%20Live-46E3B7?style=for-the-badge&logo=render&logoColor=white)
![Status](https://img.shields.io/badge/Status-Concluido-success?style=for-the-badge)

Jogo completo de **Batalha Naval** desenvolvido em Python para ambiente desktop, estruturado sobre uma arquitetura orientada a objetos desacoplada, separando rigorosamente as regras de negócio (`backend`) da camada visual e de interação (`frontend`). O projeto combina computação gráfica via Pygame Community Edition, persistência relacional SQLite e comunicação assíncrona cliente-servidor via WebSockets.

---

## Decisoes de Arquitetura e Engenharia de Software

1. **Separacao Estrita entre Backend e Frontend**:
   - Todo o estado do jogo, validacao de regras, modelos de entidades (Navio, Posicao, Tabuleiro, Jogador, Partida) e algoritmos de Inteligencia Artificial residem exclusivamente no pacote `backend`.
   - A camada `frontend` atua como visualizadora e controladora de interface, reagindo a eventos de entrada e renderizando o estado fornecido pelo backend, garantindo baixo acoplamento e alta testabilidade.

2. **Canvas Virtual e Independencia de Resolucao**:
   - A aplicacao renderiza internamente em uma superficie virtual fixa de 1280x720 pixels (`canvas_virtual`).
   - A janela de exibicao final redimensiona e projeta esse canvas mantendo a proporcao correta (com barras pretas/letterbox se necessario), permitindo transitar entre Modo Janela (padrao) e Tela Cheia sem distorcao visual.

3. **Padroes de Projeto de Software Adotados**:
   - **Strategy e Factory Method (`backend/ia`)**: As diferentes dificuldades de IA herdam de uma interface abstrata (`IABase`) e sao instanciadas dinamicamente via `FabricaIA`.
   - **Repository Pattern (`backend/database`)**: O acesso ao banco SQLite e encapsulado na classe `Repositorio`, isolando consultas SQL do restante da aplicacao.
   - **Singleton (`frontend/core`)**: Os gerenciadores de recursos visuais (`GerenciadorAssets`) e sonoros (`GerenciadorSom`) utilizam instancia unica para evitar recarregamento repetido de arquivos em disco.
   - **State Pattern / Pilha de Telas (`main.py` e `frontend/telas`)**: A navegacao entre telas utiliza uma pilha historica, viabilizando transicoes consistentes e retrocesso multinivel.

4. **Persistencia Relacional com SQLite**:
   - Optou-se pelo SQLite nativo da biblioteca padrao Python por sua confiabilidade ACID, sem necessidade de servidores externos locais.
   - O esquema armazena perfis de jogadores, metricas agregadas de desempenho (vitorias, derrotas, precisao, sequencias de acertos) e a serializacao completa em formato JSON das partidas para reproducao em Replay.

5. **Multiplayer Online Assincrono via WebSockets**:
   - Em vez de sockets TCP brutos bloqueantes, utilizou-se o protocolo WebSocket (`asyncio` / `websockets`), viabilizando comunicacao bidirecional em tempo real imune a bloqueios de thread da interface grafica.
   - Foi desenvolvido um servidor de matchmaking hospedado na nuvem (Render) com fila de pareamento, negociacao de aceite e sincronizacao de frotas customizadas antes do inicio da batalha.

---

## Mapeamento de Requisitos

### Requisitos Funcionais (RF)
* **[RF01]** **Menu Principal**: Interface interativa com opcoes de Novo Jogo, Opcoes, Estatisticas, Replays, Creditos e Saida.
* **[RF02]** **Tabuleiro 10x10**: Matrizes de 10 linhas por 10 colunas (A a J, 1 a 10) para cada jogador com coordenadas matriciais e alfanumericas.
* **[RF03]** **Tipos de Navio**: Suporte a Navios Pequenos (2 posicoes) e Navios Grandes (4 posicoes).
* **[RF04]** **Posicionamento Automático**: Algoritmo para posicionamento randomico e estrategico de frotas sem sobreposicoes e respeitando limites do tabuleiro.
* **[RF05]** **Validação de Jogadas**: Validacao rigorosa de coordenadas (A1-J10) e rejeicao imediata de jogadas repetidas com excecoes dedicadas.
* **[RF06]** **Feedback de Disparos**: Mensagens visuais explicativas e animacoes com particulas para Agua, Acerto e Navio Afundado.
* **[RF07]** **Encerramento da Partida**: Janela final exibindo vencedor, total de jogadas, aproveitamento e tempo total de jogo.
* **[RF08]** **Nova Partida**: Permite reiniciar ou iniciar novas partidas a qualquer momento.
* **[RF09]** **Modos de Jogo**: Jogador vs Computador (4 dificuldades), Dois Jogadores Local, Computador vs Computador (Simulacao) e Dois Jogadores Online via WebSocket.
* **[RF10]** **Posicionamento e Conferência**: Interface interativa com posicionamento por clique, rotacao com tecla 'R'/botao direito, contadores em tempo real e validacao antes da batalha.
* **[RF11]** **Histórico de Jogadas**: Painel lateral em tempo real com rolagem exibindo turno, jogador, coordenada, resultado e embarcacao atingida.
* **[RF12]** **Estatísticas de Desempenho**: Dashboard com partidas jogadas, vitorias, derrotas, taxa de precisao %, maior sequencia de acertos e recorde de menor numero de jogadas para vencer.
* **[RF13]** **Modo Replay Interativo**: Gravador e reprodutor completo com Play/Pause, avancar passo a passo, voltar, reiniciar e velocidade variavel (1x, 2x, 4x).

### Requisitos Não Funcionais (RNF)
* **[RNF01]** Projeto individual.
* **[RNF02]** Implementacao em Python 3.10 ou superior.
* **[RNF03]** Codigo estritamente aderente ao padrao PEP8 com tipagem estatica (`typing`).
* **[RNF04]** Organizacao modular em pacotes coesos (`backend`, `frontend`).
* **[RNF05]** Tratamento de excecoes e de entradas invalidas em todos os pontos de interacao.
* **[RNF06]** Execucao multiplataforma testada nativamente em Linux.
* **[RNF07 / RNF08]** Interface grafica moderna construida inteiramente sobre Pygame Community Edition.

### Regras de Negócio (RN)
* **[RN01]** Coordenadas no formato Letra + Numero (A1 a J10).
* **[RN02]** Jogada repetida e rejeitada com aviso explicativo, sem consumir o turno do jogador.
* **[RN03]** Embarcacao considerada afundada apenas quando 100% de suas celulas forem atingidas.
* **[RN04]** Partida finalizada imediatamente quando todos os navios de uma frota forem destruidos.
* **[RN05]** O Computador (IA) opera de maneira autonoma com escolhas estritamente validas e sem trapaça (exceto na modalidade extrema onisciente).

---

## Funcionalidades Implementadas

1. **Menu Inicial Completo**: Novo Jogo (JxC com selecao dedicada de dificuldade e descricao tatica, JxJ Local e Online com tutoriais, Simulacao CxC com escolha de algoritmo para cada computador), Opcoes, Estatisticas, Replays com gerenciamento, Creditos com atribuicoes e Saida.
2. **Menu de Opções**: Alternancia entre Modo Janela (padrao ao iniciar) e Tela Cheia, selecao dinamica de Resolucao, controles independentes de volume (Master, Musica, Efeitos de Batalha e Interface) e Area de Risco para exclusao total de registros e perfil.
3. **Navegacao Hierarquica**: Pilha de navegacao que garante retorno consistente ao nivel anterior.
4. **Cronometro em Tempo Real**: Temporizador isolado no HUD com suporte a pausa automatica.
5. **Painel de Historico Lateral**: Registro cronologico das jogadas com scroll e badges tematicos.
6. **Estatisticas Persistidas em SQLite**: Banco de dados relacional em `data/batalha_naval.db` com criacao automatica de tabelas e calculo de taxas de conversao.
7. **Captura e Selecao de Perfil**: Identificacao inicial do jogador salva e associada a todas as partidas.
8. **Player de Replays Interativo**: Visualizador com duplo tabuleiro, autoplay, retrocesso passo a passo, variacao de velocidade e exclusao de gravacoes.
9. **UI Moderna e Efeitos Sonoros**: Sprites nauticos Kenney, particulas de fumaca e impacto, sons de canhao, explosoes, trilha sonora e feedback auditivo.
10. **Janelas Modais e Notificacoes Toasts**: Modais dinamicos de confirmacao e notificacoes flutuantes temporizadas na base da tela.
11. **4 Níveis de Inteligência Artificial**:
    - **Facil**: Disparos puramente aleatorios entre as celulas disponiveis.
    - **Medio**: Estrategia de Caca e Alvo (*Hunt and Target*) com padrao checkerboard de paridade e busca ortogonal.
    - **Dificil**: Mapa de Densidade de Probabilidade (*Probability Density Function*) calculando sobreposicoes possiveis de navios remanescentes em tempo real.
    - **Impossivel (Marechal Anthony)**: Onisciencia tatica com 100% de precisao e capacidade de reposicionar estrategicamente as proprias embarcacoes em alto mar a cada turno.
12. **Multiplayer Online com Matchmaking**: Conexao WebSocket com servidor na nuvem (Render), fila de espera automatica, popup de aceite com contagem regressiva de 10 segundos e preparacao manual de frota para ambos os jogadores.

---

## Instalação e Execução

### Pré-requisitos
- **Python 3.10 ou superior**
- **pip** (gerenciador de pacotes)

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Executar o Jogo
```bash
python3 main.py
```

### 3. (Opcional) Executar Servidor Local de Matchmaking
```bash
python3 backend/rede/servidor_matchmaking.py
```

---

## Licenças e Atribuições dos Assets

* **Sprites e Arte Gráfica**: Pirate Pack por *Kenney Vleugels* ([Kenney.nl](https://www.kenney.nl)) - Licença **CC0 1.0 Universal** (Domínio Público).
* **Efeitos Sonoros de UI**: *"Menu sound effects"*, por *Vircon32 (Carra)* no OpenGameArt sob licença **CC-BY 4.0**.
* **Músicas e Trilha Sonora**: *War on Water Soundtrack Tracks* por *HorrorPen* ([OpenGameArt](https://opengameart.org/content/war-on-water-tracks)) sob licença **CC-BY 3.0**.
