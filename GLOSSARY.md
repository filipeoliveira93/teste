# Idle ARPG

Jogo idle de action RPG em dark fantasy: um personagem limpa mapas sozinho seguindo a build e as regras que o jogador montou.

## Personagem e build

**Personagem**:
O herói controlado pelo jogador; no MVP existe apenas um por save.
_Avoid_: Herói, avatar, conta

**Nível**:
Progressão geral do personagem, ganha com EXP; cada nível concede pontos de passiva.
_Avoid_: Level de skill

**Build**:
O conjunto de escolhas do jogador que define como o personagem luta: equipamento, skills escolhidas, passivas e regras de prioridade.
_Avoid_: Setup, loadout

**Tipo de arma**:
Categoria de arma (ex.: espada de duas mãos, arco, cajado) que determina as skills disponíveis nos slots da arma e o comportamento de posicionamento.
_Avoid_: Classe

**Mão secundária**:
Peça empunhada junto a uma arma de uma mão (Escudo, Foco ou Adaga); armas de duas mãos não a permitem, exceto o Arco, que aceita somente Aljava.
_Avoid_: Off-hand, secundária

**Tag**:
Rótulo que descreve uma skill ou tipo de arma (ex.: corpo a corpo, projétil, invocação, fogo, duas mãos) e pelo qual passivas e afixos a afetam.
_Avoid_: Categoria, keyword

**Maestria**:
Progressão própria de cada tipo de arma, ganha lutando com ela, que desbloqueia opções e níveis das skills daquela arma.
_Avoid_: Fama, especialização, proficiência

## Skills

**Skill**:
Habilidade ativa concedida por uma arma ou peça de armadura equipada; as de armadura são sempre de suporte (buff, defesa ou mobilidade), nunca de dano.
_Avoid_: Magia, habilidade, gema, spell

**Slot de skill**:
Posição fixa de uma arma ou peça de armadura que comporta uma skill escolhida entre as opções daquele slot.
_Avoid_: Soquete, barra de skill

**Invocação**:
Entidade aliada criada por uma skill, que ocupa uma célula e luta com comportamento próprio; existe um limite simultâneo por skill.
_Avoid_: Minion, pet, servo

**Totem**:
Invocação imóvel que usa uma skill sozinha.
_Avoid_: Torre, estátua

**Forma**:
Transformação (ex.: Urso, Lobo) disponível só com o Cajado de druida, que troca as skills dos slots da arma e o comportamento de posicionamento enquanto durar.
_Avoid_: Metamorfose, shapeshift

**Regra de prioridade**:
Par condição → skill, avaliado em ordem numa lista configurada pelo jogador, que decide qual skill o personagem usa a cada momento.
_Avoid_: Gambit, macro, script

**Comportamento de posicionamento**:
Forma automática como o personagem se movimenta em combate (aproximar, manter distância), definida pelo tipo de arma.
_Avoid_: IA de movimento, kite

**Atributo**:
Força, Destreza ou Inteligência; vem da árvore e dos itens e é exigido pelas bases de item.
_Avoid_: Stat principal

**Mana**:
Recurso único gasto pelas skills e regenerado com o tempo.
_Avoid_: Energia, fúria, recurso

**Ataque básico**:
Ação padrão da arma, usada quando nenhuma regra de prioridade se aplica.
_Avoid_: Auto-ataque, ataque padrão

## Itens e loot

**Base do item**:
Tipo fixo de um item (ex.: Espada Longa, Peitoral de Couro) que define seu slot, status base e, em armas e armaduras, as opções de skill.
_Avoid_: Modelo, template

**Nível do item**:
Nível de um item, igual ao tier do mapa onde caiu, que limita os tiers de afixo possíveis nele.
_Avoid_: iLvl, poder do item

**Raridade**:
Classe de um item quanto ao número de afixos: Normal, Mágico ou Raro.
_Avoid_: Qualidade, cor

**Afixo**:
Bônus sorteado num item, como prefixo ou sufixo, com tier de valor.
_Avoid_: Mod, atributo, encantamento

**Baú**:
Armazenamento dos itens e materiais do jogador; o loot chega aqui ao fim de cada sala.
_Avoid_: Inventário, stash, mochila

**Filtro de loot**:
Conjunto de critérios do jogador que decide quais drops vão para o baú; o que é rejeitado vira material de crafting.
_Avoid_: Auto-venda, loot filter

**Runa**:
Item consumível de crafting que altera a raridade ou os afixos de outro item (ex.: Runa da Centelha, Runa da Ruína).
_Avoid_: Orbe, moeda, currency

**Pó rúnico**:
Material obtido dos drops rejeitados pelo filtro de loot, acumulado para formar runas.
_Avoid_: Fragmento, sucata

**Árvore de passivas**:
Grafo de nós de bônus permanentes, comum a qualquer tipo de arma, onde o personagem gasta os pontos ganhos por nível, partindo sempre do centro; dividida em regiões de Força, Destreza e Inteligência e nas zonas híbridas entre elas.
_Avoid_: Talentos, skill tree, atlas

## Mapas e runs

**Mapa**:
Local de combate de uma lista fixa organizada por tier; matar o chefe de um mapa libera o seguinte.
_Avoid_: Fase, nível, dungeon

**Fenda**:
Mapa originado por uma ruptura do Selo, povoado por criaturas corrompidas; é uma das origens possíveis de mapa, não a única.
_Avoid_: Portal, rift

**Tier**:
Grau de dificuldade e recompensa de um mapa.
_Avoid_: Dificuldade, ato

**Modificador de mapa**:
Condição adversa que o jogador liga num mapa em troca de mais quantidade e raridade de loot.
_Avoid_: Afixo de mapa, maldição, tormento

**Run**:
Uma tentativa de limpar um mapa, sala por sala até o chefe; termina em sucesso ou morte.
_Avoid_: Partida, incursão, expedição

**Sala**:
Arena em grid onde acontece uma etapa da run, com ondas de monstros ou o chefe.
_Avoid_: Fase, onda, área

**Elite**:
Monstro mais forte que o normal, com um ou dois modificadores de monstro.
_Avoid_: Raro, campeão

**Modificador de monstro**:
Característica sorteada que torna um elite mais perigoso (ex.: rápido, explode ao morrer).
_Avoid_: Afixo de monstro, aura

**Família de monstros**:
Grupo temático de monstros (ex.: mortos-vivos, bestas, cultistas) que povoa um mapa.
_Avoid_: Raça, facção

**Chefe**:
Monstro da última sala de uma run; derrotá-lo conclui a run.
_Avoid_: Boss, guardião

**Loop de runs**:
Repetição automática de runs no mesmo mapa e modificadores até o jogador mudar a configuração ou o personagem morrer três vezes seguidas.
_Avoid_: Farm, auto-run

**Morte**:
Fim de uma run com fracasso; custa apenas o tempo da run, sem perda de loot, nível ou EXP.
_Avoid_: Game over, derrota

**Progresso offline**:
Recompensa pelo tempo em que o jogo ficou fechado (até 3h), projetada a partir de runs simuladas com a configuração atual no momento em que o jogador volta.
_Avoid_: AFK, idle gain

## Simulação

**Célula**:
Unidade do grid de uma sala; cada personagem ou monstro ocupa uma.
_Avoid_: Tile, quadrado

**Tick**:
Passo fixo de tempo em que todas as ações e movimentos da simulação acontecem.
_Avoid_: Frame, turno
