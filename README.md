# Batalha Naval

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame CE](https://img.shields.io/badge/Pygame--CE-2.5%2B-brightgreen?style=for-the-badge)
![WebSockets](https://img.shields.io/badge/WebSockets-13.0%2B-black?style=for-the-badge&logo=websocket&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Render](https://img.shields.io/badge/Render-Deployed%20Live-46E3B7?style=for-the-badge&logo=render&logoColor=white)
![Status](https://img.shields.io/badge/Status-Concluido-success?style=for-the-badge)

Jogo completo de **Batalha Naval** desenvolvido em Python para ambiente desktop, estruturado sobre uma arquitetura orientada a objetos desacoplada, separando rigorosamente as regras de negócio (`backend`) da camada visual e de interação (`frontend`). O projeto combina computação gráfica via Pygame Community Edition, persistência relacional SQLite e comunicação assíncrona cliente-servidor via WebSockets.

---

## Decisões de Arquitetura e Engenharia de Software

1. **Separação Estrita entre Backend e Frontend**:
   - Todo o estado do jogo, validação de regras, modelos de entidades (Navio, Posição, Tabuleiro, Jogador, Partida) e algoritmos de Inteligência Artificial residem exclusivamente no pacote `backend`.
   - A camada `frontend` atua como visualizadora e controladora de interface, reagindo a eventos de entrada e renderizando o estado fornecido pelo backend, garantindo baixo acoplamento e alta testabilidade.

2. **Canvas Virtual e Independência de Resolução**:
   - A aplicação renderiza internamente em uma superfície virtual fixa de 1280x720 pixels (`canvas_virtual`).
   - A janela de exibição final redimensiona e projeta esse canvas mantendo a proporção correta (com barras pretas/letterbox se necessário), permitindo transitar entre Modo Janela (padrão) e Tela Cheia sem distorção visual.

3. **Padrões de Projeto de Software Adotados**:
   - **Strategy e Factory Method (`backend/ia`)**: As diferentes dificuldades de IA herdam de uma interface abstrata (`IABase`) e são instanciadas dinamicamente via `FabricaIA`.
   - **Repository Pattern (`backend/database`)**: O acesso ao banco SQLite é encapsulado na classe `Repositorio`, isolando consultas SQL do restante da aplicação.
   - **Singleton (`frontend/core`)**: Os gerenciadores de recursos visuais (`GerenciadorAssets`) e sonoros (`GerenciadorSom`) utilizam instância única para evitar recarregamento repetido de arquivos em disco.
   - **State Pattern / Pilha de Telas (`main.py` e `frontend/telas`)**: A navegação entre telas utiliza uma pilha histórica, viabilizando transições consistentes e retrocesso multinível.

4. **Persistência Relacional com SQLite**:
   - Optou-se pelo SQLite nativo da biblioteca padrão Python por sua confiabilidade ACID, sem necessidade de servidores externos locais.
   - O esquema armazena perfis de jogadores, métricas agregadas de desempenho (vitórias, derrotas, precisão, sequências de acertos) e a serialização completa em formato JSON das partidas para reprodução em Replay.

5. **Multiplayer Online Assíncrono via WebSockets**:
   - Em vez de sockets TCP brutos bloqueantes, utilizou-se o protocolo WebSocket (`asyncio` / `websockets`), viabilizando comunicação bidirecional em tempo real imune a bloqueios de thread da interface gráfica.
   - Foi desenvolvido um servidor de matchmaking hospedado na nuvem (Render) com fila de pareamento, negociação de aceite e sincronização de frotas customizadas antes do início da batalha.

---

## Mapeamento de Requisitos

### Requisitos Funcionais (RF)
* **[RF01]** **Menu Principal**: Interface interativa com opções de Novo Jogo, Opções, Estatísticas, Replays, Créditos e Saída.
* **[RF02]** **Tabuleiro 10x10**: Matrizes de 10 linhas por 10 colunas (A a J, 1 a 10) para cada jogador com coordenadas matriciais e alfanuméricas.
* **[RF03]** **Tipos de Navio**: Suporte a Navios Pequenos (2 posições) e Navios Grandes (4 posições).
* **[RF04]** **Posicionamento Automático**: Algoritmo para posicionamento randômico e estratégico de frotas sem sobreposições e respeitando limites do tabuleiro.
* **[RF05]** **Validação de Jogadas**: Validação rigorosa de coordenadas (A1-J10) e rejeição imediata de jogadas repetidas com exceções dedicadas.
* **[RF06]** **Feedback de Disparos**: Mensagens visuais explicativas e animações com partículas para Água, Acerto e Navio Afundado.
* **[RF07]** **Encerramento da Partida**: Janela final exibindo vencedor, total de jogadas, aproveitamento e tempo total de jogo.
* **[RF08]** **Nova Partida**: Permite reiniciar ou iniciar novas partidas a qualquer momento.
* **[RF09]** **Modos de Jogo**: Jogador vs Computador (4 dificuldades), Dois Jogadores Local, Computador vs Computador (Simulação) e Dois Jogadores Online via WebSocket.
* **[RF10]** **Posicionamento e Conferência**: Interface interativa com posicionamento por clique, rotação com tecla 'R'/botão direito, contadores em tempo real e validação antes da batalha.
* **[RF11]** **Histórico de Jogadas**: Painel lateral em tempo real com rolagem exibindo turno, jogador, coordenada, resultado e embarcação atingida.
* **[RF12]** **Estatísticas de Desempenho**: Dashboard com partidas jogadas, vitórias, derrotas, taxa de precisão %, maior sequência de acertos e recorde de menor número de jogadas para vencer.
* **[RF13]** **Modo Replay Interativo**: Gravador e reprodutor completo com Play/Pause, avançar passo a passo, voltar, reiniciar e velocidade variável (1x, 2x, 4x).

### Requisitos Não Funcionais (RNF)
* **[RNF01]** Projeto individual.
* **[RNF02]** Implementação em Python 3.10 ou superior.
* **[RNF03]** Código estritamente aderente ao padrão PEP8 com tipagem estática (`typing`).
* **[RNF04]** Organização modular em pacotes coesos (`backend`, `frontend`).
* **[RNF05]** Tratamento de exceções e de entradas inválidas em todos os pontos de interação.
* **[RNF06]** Execução multiplataforma testada nativamente em Linux.
* **[RNF07 / RNF08]** Interface gráfica moderna construída inteiramente sobre Pygame Community Edition.

### Regras de Negócio (RN)
* **[RN01]** Coordenadas no formato Letra + Número (A1 a J10).
* **[RN02]** Jogada repetida é rejeitada com aviso explicativo, sem consumir o turno do jogador.
* **[RN03]** Embarcação considerada afundada apenas quando 100% de suas células forem atingidas.
* **[RN04]** Partida finalizada imediatamente quando todos os navios de uma frota forem destruídos.
* **[RN05]** O Computador (IA) opera de maneira autônoma com escolhas estritamente válidas e sem trapaça (exceto na modalidade extrema onisciente).

---

## Funcionalidades Implementadas

1. **Menu Inicial Completo**: Novo Jogo (JxC com seleção dedicada de dificuldade e descrição tática, JxJ Local e Online com tutoriais, Simulação CxC com escolha de algoritmo para cada computador), Opções, Estatísticas, Replays com gerenciamento, Créditos com atribuições e Saída.
2. **Menu de Opções**: Alternância entre Modo Janela (padrão ao iniciar) e Tela Cheia, seleção dinâmica de Resolução, controles independentes de volume (Master, Música, Efeitos de Batalha e Interface) e Área de Risco para exclusão total de registros e perfil.
3. **Navegação Hierárquica**: Pilha de navegação que garante retorno consistente ao nível anterior.
4. **Cronômetro em Tempo Real**: Temporizador isolado no HUD com suporte a pausa automática.
5. **Painel de Histórico Lateral**: Registro cronológico das jogadas com scroll e badges temáticos.
6. **Estatísticas Persistidas em SQLite**: Banco de dados relacional em `data/batalha_naval.db` com criação automática de tabelas e cálculo de taxas de conversão.
7. **Captura e Seleção de Perfil**: Identificação inicial do jogador salva e associada a todas as partidas.
8. **Player de Replays Interativo**: Visualizador com duplo tabuleiro, autoplay, retrocesso passo a passo, variação de velocidade e exclusão de gravações.
9. **UI Moderna e Efeitos Sonoros**: Sprites náuticos Kenney, partículas de fumaça e impacto, sons de canhão, explosões, trilha sonora e feedback auditivo.
10. **Janelas Modais e Notificações Toasts**: Modais dinâmicos de confirmação e notificações flutuantes temporizadas na base da tela.
11. **4 Níveis de Inteligência Artificial**:
    - **Fácil**: Disparos puramente aleatórios entre as células disponíveis (~95 tiros por partida).
    - **Médio**: Estratégia clássica de Caça e Alvo (*Hunt and Target*) com busca ortogonal (~70 tiros por partida).
    - **Difícil**: Amostragem Monte Carlo e Mapa de Densidade de Probabilidade (*PDF*) com Poda de Espaços Mortos (*Dead-Space Pruning*) e Paridade Ótima (~50 tiros por partida).
    - **Impossível (Marechal Anthony)**: Onisciência tática com 100% de precisão (16 tiros) e capacidade de reposicionar estrategicamente as próprias embarcações em alto mar a cada turno.
12. **Multiplayer Online com Matchmaking**: Conexão WebSocket com servidor na nuvem (Render), fila de espera automática, popup de aceite com contagem regressiva de 10 segundos e preparação manual de frota para ambos os jogadores.

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
