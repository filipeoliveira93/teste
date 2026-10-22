# GDD — Idle ARPG (rascunho v0.1)

> Documento vivo. Seções marcadas com **[ABERTO]** ainda precisam de decisão.

## 1. Visão geral

Um **idle ARPG**: o jogador cria um personagem, monta a build (arma, skills, passivas, itens) e o personagem limpa mapas sozinho. A graça está em **planejar e otimizar a build**, não em reflexo.

- **Inspirações:** Path of Exile (árvore de passivas, afixos, crafting com moedas), Diablo (loot, raridades), Last Epoch (crafting controlado, especialização de skills), jogos idle (progresso automático/offline).
- **Engine:** Godot 4.x (GDScript).
- **Pilares:**
  1. **Build é tudo:** cada escolha (arma, nó da árvore, afixo) muda o resultado de forma perceptível.
  2. **Loot que dá vontade de olhar:** drops com afixos aleatórios e chance real de upgrade.
  3. **Progresso sempre andando:** mesmo sem jogar ativamente, algo evolui.
  4. **Risco nas runs:** cada mapa é uma aposta com modificadores e recompensas.

## 2. Loop principal

```
Escolher mapa (+ modificadores)
        ↓
Run automática (combate por prioridades)
        ↓
Fim da run: sucesso → loot + EXP | morte → perde loot da run
        ↓
Gastar pontos (árvore / skills), equipar e craftar itens
        ↓
Mapas mais difíceis
```

## 3. Personagem e "classe pela arma"

- Não existe classe fixa: **a arma equipada define o conjunto de skills ativas disponíveis**.
- Trocar de arma = trocar de "classe" (skills), mas a árvore de passivas e o nível continuam.
- **Tipos de arma iniciais (proposta):**

| Arma | Arquétipo | Atributo principal | Exemplos de skill |
|---|---|---|---|
| Espada / Machado (2 mãos) | Guerreiro, corpo a corpo pesado | Força | Golpe Giratório, Investida, Grito de Guerra |
| Adagas (dual) | Assassino, crítico e veneno | Destreza | Golpe Venenoso, Lâminas Voadoras, Evasão |
| Arco | Atirador à distância | Destreza | Chuva de Flechas, Tiro Perfurante, Armadilha |
| Cajado | Mago elemental | Inteligência | Bola de Fogo, Nova de Gelo, Corrente Elétrica |
| Cetro + Escudo | Paladino, defesa e aura | Força/Int | Martelo Sagrado, Aura de Proteção, Consagrar |

**[ABERTO]** Skills ficam presas à arma ou o jogador pode ter "gemas"/skills avulsas que exigem tipo de arma?

## 4. Progressão

### 4.1 Nível e EXP
- EXP por monstro morto e bônus ao concluir o mapa.
- Cada nível = **1 ponto de passiva** (+ ponto de skill a cada N níveis).
- Curva exponencial suave; penalidade de EXP em morte **[ABERTO]**.

### 4.2 Árvore de passivas (grande, estilo PoE)
- Árvore **compartilhada** por todos os personagens.
- **Ponto de partida depende da arma inicial** escolhida na criação (região Força / Destreza / Inteligência e híbridas).
- Tipos de nó:
  - **Pequeno:** +atributo, +% dano, +vida etc.
  - **Notável:** bônus forte e temático.
  - **Keystone:** muda regras (ex.: "Sem regeneração de vida, mas +50% roubo de vida").
- Respec com custo (moeda) para incentivar planejamento.
- Dados da árvore definidos em arquivo (JSON/Resource) para facilitar balanceamento e editor visual.

### 4.3 Skills ativas
- Cada skill tem nível próprio e **mini-árvore de especialização** (estilo Last Epoch) **[ABERTO: entra no MVP?]**.
- Tags: `ataque`, `magia`, `projétil`, `área`, `fogo`, `gelo`, `raio`, `físico`, `caos`, `invocação` — passivas e afixos escalam por tag.

## 5. Combate automático com prioridades

- O personagem age sozinho em ticks de simulação.
- O jogador configura uma **lista de regras** (estilo gambits), avaliadas de cima para baixo:

```
1. SE vida < 35%           → usar Poção
2. SE inimigos próximos ≥ 3 → usar Golpe Giratório
3. SE alvo é Elite/Chefe   → usar Investida
4. SEMPRE                   → Ataque Básico
```

- Condições iniciais: vida/mana %, nº de inimigos, tipo de alvo, buff ativo/inativo, cooldown pronto.
- Slots de regra limitados e desbloqueáveis com a progressão.

### 5.1 Estatísticas base
Vida, Mana, Armadura, Evasão, Escudo de Energia, Resistências (fogo/gelo/raio/caos), Chance/Multiplicador de crítico, Velocidade de ataque/conjuração, Roubo de vida.

**[ABERTO]** Visualização do combate: cena 2D com sprites se movendo, ou representação abstrata (barras, log, ícones)?

## 6. Mapas e runs (roguelike)

- Cada mapa tem **tier** (dificuldade), bioma e lista de monstros.
- Uma **run** = sequência de salas/ondas + chefe final.
- **Modificadores** aleatórios no mapa (estilo PoE): "+30% vida dos monstros", "monstros causam dano de fogo extra" → aumentam quantidade/raridade do loot.
- **Escolhas durante a run** (roguelike): entre salas o jogo oferece bênçãos/caminhos (ex.: "+20% dano até o fim da run" ou "sala de tesouro com elite").
- **Morte:** termina a run e perde o loot acumulado nela; personagem e EXP já obtida ficam **[ABERTO: penalidade de EXP?]**.
- Concluir mapas desbloqueia tiers superiores (atlas/progressão de mapas).

## 7. Loot e itens

### 7.1 Raridades
| Raridade | Afixos | Observação |
|---|---|---|
| Normal | 0 | Base pura |
| Mágico | 1–2 | 1 prefixo + 1 sufixo |
| Raro | 3–6 | até 3 prefixos + 3 sufixos |
| Único | fixos | Efeitos especiais que mudam builds |

### 7.2 Estrutura de item
- **Base** (ex.: Espada Longa) → dano/defesa base, requisitos, implícito.
- **Afixos** sorteados de um pool por slot e nível do item, cada um com **tiers** (T1 melhor) e faixa de valores.
- Slots: arma principal, mão secundária, elmo, peitoral, luvas, botas, cinto, amuleto, 2 anéis.

### 7.3 Filtro de loot
Essencial em idle: regras para auto-descartar/vender itens abaixo de um critério.

## 8. Crafting

Moedas que caem dos mapas (nomes provisórios):

| Moeda | Efeito |
|---|---|
| Fragmento de Transmutação | Normal → Mágico |
| Fragmento de Alteração | Re-sorteia afixos de item mágico |
| Fragmento de Ascensão | Mágico → Raro |
| Fragmento do Caos | Re-sorteia todos os afixos de item raro |
| Fragmento de Exaltação | Adiciona 1 afixo a item raro |
| Fragmento de Purificação | Remove 1 afixo aleatório |
| Fragmento Divino | Re-sorteia valores dentro do tier |

**[ABERTO]** Incluir crafting determinístico (estilo Last Epoch, escolher afixo) no MVP ou depois?

## 9. Idle / progresso offline

- Ao voltar, o jogo **simula o tempo ausente** de forma resumida (estatística, não tick a tick) usando a última run configurada.
- Limite de tempo offline (ex.: 12h) **[ABERTO]**.
- Loot offline passa pelo filtro de loot automaticamente.

## 10. Arquitetura técnica (proposta)

- **Simulação separada da apresentação:** toda a lógica de combate, loot e progresso em scripts puros (sem depender de nós de cena), para permitir:
  - simulação offline acelerada;
  - testes automatizados;
  - trocar a visualização sem mexer nas regras.
- **Dados em Resources/JSON:** armas, skills, afixos, árvore, mapas, monstros → balanceamento sem tocar em código.
- **RNG com seed** por run, para reprodutibilidade e depuração.
- **Save** em JSON versionado (`user://save.json`) com migração entre versões.

Estrutura de pastas sugerida:
```
project.godot
data/          # definições (armas, skills, afixos, árvore, mapas)
scripts/
  core/        # simulação: combate, stats, loot, crafting, progressão
  systems/     # save, offline, RNG
  ui/          # telas e componentes
scenes/        # cenas Godot
tests/         # testes (GUT ou gdUnit4)
docs/          # GDD e notas
```

## 11. Escopo do MVP

1. Criar personagem escolhendo arma inicial (2–3 tipos de arma no começo).
2. Combate automático com regras de prioridade.
3. 3–5 mapas com tiers e modificadores; runs com salas + chefe.
4. Loot com raridades e afixos; equipar itens.
5. Árvore de passivas (versão reduzida, ~60–100 nós, estrutura pronta para crescer).
6. Crafting com 4–5 moedas básicas.
7. Save/load + progresso offline simples.

## 12. Questões em aberto (resumo)

- [ ] Nome do jogo e ambientação (dark fantasy?).
- [ ] Visualização do combate: 2D com sprites ou abstrata.
- [ ] Skills presas à arma ou gemas avulsas com requisito de arma.
- [ ] Mini-árvore de especialização de skills no MVP?
- [ ] Penalidade de morte (só loot da run, ou também EXP?).
- [ ] Limite de progresso offline.
- [ ] Monetização / plataforma de lançamento (Steam, mobile, web).
