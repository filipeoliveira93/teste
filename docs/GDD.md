# GDD — Idle ARPG (v0.2)

> Resultado da sessão de grilling. Termos em **negrito** seguem o `GLOSSARY.md`; decisões de arquitetura estão em `docs/adr/`.

## 1. Visão geral

Um **idle ARPG** dark fantasy para PC (Steam/itch, mouse e teclado). O jogador monta a **build** — equipamento, skills, passivas e **regras de prioridade** — e o **personagem** repete runs sozinho. A graça está em planejar e otimizar a build; o jogador pode simplesmente fechar o jogo e o progresso continua.

- **Inspirações:** Path of Exile (árvore de passivas, afixos, crafting), Albion Online (skills por arma e armadura, mão secundária), Last Epoch (necromante, xamã, druida), Diablo (loot e dificuldade por modificadores).
- **Engine:** Godot 4.x (GDScript).
- **Pilares:**
  1. **A build decide tudo:** não há sorte de bênçãos nem escolhas durante a run; o resultado vem da build.
  2. **Loot que vale olhar:** afixos sorteados e chance real de upgrade.
  3. **Progresso sempre andando:** loop automático e progresso offline sem exigir nada do jogador.
  4. **Rendimento por hora:** o jogador escolhe quanto risco (tier e modificadores) a build aguenta.

## 2. Loop principal

```
Escolher mapa + modificadores de mapa
        ↓
Loop de runs automático (salas → chefe)
        ↓
Loot ao fim de cada sala → filtro de loot → baú (rejeitado vira pó rúnico)
        ↓
Gastar pontos (passivas), evoluir maestria, equipar e craftar com runas
        ↓
Tiers maiores / mais modificadores
```

- Um **personagem** por save no MVP.
- O **loop de runs** repete o mesmo mapa e modificadores até o jogador mudar algo ou o personagem morrer **3 vezes seguidas** (aviso: "Sua build não está aguentando este mapa/modificadores").
- **Morte** custa apenas o tempo da run: sem perda de loot, nível ou EXP.

## 3. Personagem e progressão

### 3.1 Nível
- EXP por monstro morto e por run concluída.
- **1 ponto de passiva por nível**; nível máximo **60 no MVP**.

### 3.2 Atributos, recurso e defesas
- **Atributos:** Força, Destreza, Inteligência — vêm da árvore e dos itens; bases de item exigem mínimos.
- **Mana:** recurso único das skills; regenera **apenas com o tempo** (o ataque básico não custa nem gera mana).
- **Defesa no MVP:** Vida, Armadura, Resistências (fogo/gelo/raio/caos) e bloqueio (escudo). Sem acerto/evasão no MVP: todo golpe acerta. Evasão e escudo de energia ficam para depois.

### 3.3 Maestria
- Cada **tipo de arma** tem sua **maestria** (1 a 50), ganha lutando com ele; trocar de arma não perde a maestria da anterior.
- Em cada slot da arma, as opções se desbloqueiam na maestria **1, 10 e 25**.
- **Nível das skills** daquele tipo de arma = 1 + maestria ÷ 5 (até 11).

## 4. Tipos de arma e skills

### 4.1 A arma define as skills (estilo Albion)
Não existe classe. O **tipo de arma** equipado define as skills dos slots da arma, o **comportamento de posicionamento** e as tags.

| # | Tipo de arma | Mãos | Atributo | Identidade | Mão secundária |
|---|---|---|---|---|---|
| 1 | Espada | 1 | Força | Guerreiro equilibrado: golpes, investida, gritos | Escudo / Foco |
| 2 | Machado | 2 | Força | Golpes pesados em área, sangramento | — |
| 3 | Adaga | 1 | Destreza | Crítico, veneno, golpes rápidos | Adaga (dual) / Escudo / Foco |
| 4 | Arco | 2 | Destreza | Projéteis, chuva de flechas, armadilhas | **somente Aljava** |
| 5 | Cajado elemental | 2 | Inteligência | Fogo, gelo e raio em área | — |
| 6 | Tomo arcano | 1 | Inteligência | Projéteis mágicos, controle, teleporte | Escudo / Foco |
| 7 | Grimório necromântico | 1 | Inteligência | Invocação de mortos-vivos, maldições | Escudo / Foco |
| 8 | Cetro de xamã | 1 | Força/Int | Totens, raio e terra | Escudo / Foco |
| 9 | Cajado de druida | 2 | Destreza/Int | Formas de Urso e Lobo, natureza | — |

> A combinação exata de mão secundária por arma de uma mão será fechada na spec; a regra fixa é: **Adaga secundária só com Adaga principal; duas mãos não usam secundária, exceto Arco + Aljava.**

O **tipo de arma** define as skills; dentro de cada tipo existem várias **bases de item** (ex.: Espada Curta, Espada Longa) que dão as mesmas skills e diferem em dano base, velocidade, requisitos e implícito.

**Ataque vs. magia:** skills de **ataque** (Espada, Machado, Adaga, Arco) usam o dano da arma — físico na base; elementos vêm de **afixos** do item. Skills de **magia** (Cajado elemental, Tomo, Grimório…) têm dano e tipo próprios; afixos aumentam o dano mas não mudam o tipo.

### 4.2 Slots de skill
- **Arma:** 3 slots, cada um com **3 opções** desbloqueadas pela maestria:
  - **Slot 1 — Principal:** custo baixo, sem recarga, dano do dia a dia.
  - **Slot 2 — Tática:** recarga curta; controle, mobilidade ou área média.
  - **Slot 3 — Assinatura:** recarga longa, efeito forte; define a build.
  - Regra de design: as 3 opções de um slot diferem na forma de uso — em geral (a) alvo único, (b) área, (c) especialista (acúmulo de aflição ou utilidade).
- **Elmo, peitoral, botas:** 1 slot cada. As opções vêm do **peso da armadura + slot** (todas as bases do mesmo peso e slot compartilham as opções) e são desbloqueadas pelo **nível** do personagem. Skills de armadura são **sempre suporte, nunca dano**:
  - **Pesos:** Tecido (Inteligência), Couro (Destreza), Placas (Força).
  - **Elmo:** recurso e utilidade (mana, recarga). **Peitoral:** defesa (escudo temporário, resistência, limiar). **Botas:** mobilidade (dash, salto, velocidade).
- Sem árvore de modificadores por skill no MVP: a skill evolui só pelo nível.
- **Mão secundária:** não dá skill; tem status base, implícito e afixos.
- **Ataque básico:** usado quando nenhuma regra se aplica.

### 4.3 Mecânicas especiais
- **Invocação:** entidade aliada que ocupa uma célula, tem vida e comportamento simples (atacar o mais próximo); limite simultâneo por skill.
- **Totem:** invocação imóvel que usa uma skill sozinha (Cetro de xamã).
- **Forma (pós-MVP):** só com o Cajado de druida. Urso e Lobo são opções do slot 3; enquanto transformado, os 3 slots da arma usam 3 skills fixas da forma, o posicionamento vira corpo a corpo e os status mudam (Urso: +vida/armadura; Lobo: +velocidade). Skills de armadura continuam disponíveis.

### 4.4 Tags
Skills e tipos de arma declaram **tags** (ex.: `corpo a corpo`, `projétil`, `magia`, `área`, `invocação`, `transformação`, `uma mão`, `duas mãos`, `físico`, `fogo`, `gelo`, `raio`). Passivas e afixos escalam por tag.

## 5. Combate

### 5.1 Simulação (ADR 0001)
- Top-down 2D em **grid de células**, avançando em **ticks** fixos (**10 ticks/s**), determinístico a partir de um seed.
- Movimento em 8 direções (diagonal vale 1), 1 entidade por célula; salas do MVP sem obstáculos.
- Formas de área: célula única, linha, cone (90°), quadrado N×N, raio R. Projéteis viajam célula a célula e param no primeiro inimigo (salvo "perfurar").
- Ações, recargas e durações contadas em ticks; velocidade de ataque/conjuração reduz a duração da ação.
- Áreas de efeito são formas sobre células (quadrado, cone, linha).
- A cena Godot só anima a transição entre ticks.

### 5.2 Movimento
Automático, pelo **comportamento de posicionamento** do tipo de arma (aproximar, manter distância). Formas forçam corpo a corpo. Skills de mobilidade das botas podem ser acionadas pelas regras.

### 5.3 Regras de prioridade
- **6 regras** no MVP (pode crescer com a progressão), avaliadas de cima para baixo; cada uma aponta para uma skill equipada.
- Condições: vida/mana %, nº de inimigos num raio, alvo é elite/chefe, buff ativo/inativo, skill fora de recarga, nº de invocações ativas, em forma X / fora de forma.

```
1. SE vida < 35%              → Pele de Pedra (peitoral)
2. SE invocações ativas < 3   → Erguer Esqueleto
3. SE inimigos em raio 2 ≥ 3  → Nova de Ossos
4. SE alvo é elite/chefe      → Maldição da Fraqueza
5. (nenhuma) → ataque básico
```

### 5.4 Tipos de dano e mitigação

| Tipo | Mitigado por | Identidade |
|---|---|---|
| Físico | Armadura | Base das armas |
| Fogo | Resistência a fogo | Dano alto em área |
| Gelo | Resistência a gelo | Controle |
| Raio | Resistência a raio | Dano variável (mín. baixo, máx. alto) |
| Caos | Resistência a caos | Dano do Âmago bruto; armadura não reduz; resistência começa negativa |

- **Armadura:** `redução = armadura / (armadura + 5 × dano do golpe)`, máx. 90% — forte contra muitos golpes pequenos, fraca contra golpes pesados.
- **Resistências:** em %, limite de 75%; Fendas de tier alto aplicam penalidade de resistência.

### 5.5 Cálculo de dano
1. Dano base (arma para ataques, skill para magias).
2. \+ dano adicionado.
3. × (1 + soma dos "aumentado %").
4. × cada "mais %" (só skills e keystones).
5. Crítico (chance e multiplicador).
6. Mitigação no alvo (armadura ou resistência).

### 5.6 Aflições (modelo de acúmulo, estilo Horizon Zero Dawn)

| Tipo de dano | Aflição | Categoria | Efeito |
|---|---|---|---|
| Físico | Sangramento | Dano | Dano contínuo físico |
| Fogo | Incendiar | Dano | Dano contínuo de fogo |
| Caos | Veneno | Dano | Dano contínuo de caos |
| Gelo | Lentidão | Controle | Reduz velocidade de ação e movimento |
| Raio | Atordoamento | Controle | Interrompe e paralisa por poucos ticks |

- Cada alvo tem um **medidor** por aflição. O **dano já mitigado** de um tipo enche o medidor correspondente; ao atingir o **limiar**, a aflição dispara e o medidor zera.
- O medidor **decai** se o alvo ficar alguns segundos sem receber dano daquele tipo (é preciso pressão contínua).
- **Limiar** = % da vida máxima do alvo (base 30%) × modificador da família de monstros (**fraqueza** < 1, resistência > 1, ou imune — ex.: esqueletos não sangram).
- **Competição entre aflições de dano:** enquanto Sangramento, Incendiar ou Veneno está ativo num alvo, o limiar das outras duas aflições de dano **dobra**. Aflições de controle não afetam nem são afetadas.
- Aflições de controle não reduzem o próprio limiar; após o Atordoamento o alvo fica imune a atordoamento por alguns segundos; chefes têm duração reduzida.
- A build controla aflições por três alavancas: **acúmulo** (quanto cada ponto de dano enche o medidor, ex.: "+30% de acúmulo de incendiar"), **força** (dano/efeito da aflição) e **duração**. Skills especialistas têm acúmulo multiplicado (ex.: Flecha Envenenada ×3).
- Fontes: skills, afixos, passivas (por tag) e implícitos de base.
- O mesmo sistema vale para monstros contra o personagem; afixos e passivas podem subir os limiares do personagem.
- Misturar vários elementos é possível, mas caro: elementos ficam em áreas diferentes da árvore e afixos de conversão são exclusivos (um elemento por item).

### 5.7 Monstros em combate
Perfis: **corpo a corpo** (aproxima e ataca), **à distância** (mantém 4–6 células), **conjurador** (distância, área telegrafada ou invocação). Todos miram o alvo mais próximo (personagem ou invocação). Chefes têm padrão scriptado.

## 6. Mapas e runs

- **Mapas:** lista fixa organizada por **tier**; matar o chefe de um mapa libera o próximo.
- **Modificadores de mapa:** escolhidos pelo jogador ("monstros +40% vida", "dano de fogo extra"); aumentam quantidade e chance de raridade do loot (não o nível do item).
- **Run:** sequência de **salas** em grid (~15x15 células) com ondas de monstros + **chefe** na última. O número de salas cresce com o tier (ex.: tier 1 = 4 salas + chefe; tiers altos = 7 + chefe).
- **Duração alvo:** 3 a 8 minutos, resultado da velocidade de clear da build (não há cronômetro).

### 6.1 Monstros
- **Normal**, **Elite** (mais vida + 1–2 modificadores de monstro, ex.: rápido, explode ao morrer, resistente a fogo) e **Chefe** (padrão próprio: áreas telegrafadas no grid, invocar ajudantes).
- Cada mapa tem uma **família de monstros** temática (mortos-vivos, bestas, cultistas…).

## 7. Árvore de passivas (ADR 0002)

- Uma árvore só, comum a qualquer tipo de arma; o personagem começa **sempre do centro**.
- Regiões de **Força**, **Destreza** e **Inteligência** e zonas híbridas entre elas (Força/Destreza, Força/Inteligência, Destreza/Inteligência).
- Nós citam apenas **atributos, status e tags** — nunca um tipo de arma pelo nome. Armas novas entram declarando tags, sem alterar a árvore.
- Tipos de nó: pequeno, notável e keystone (muda regras).
- MVP: ~60–100 nós.
- **Respec** nó a nó pagando **pó rúnico**; só pode remover nós que não deixem outros desconectados.

## 8. Itens e loot

### 8.1 Slots de equipamento (9)
Arma, mão secundária, elmo, peitoral, botas, luvas, amuleto e 2 anéis. Cinto: **[ABERTO]**.

### 8.2 Estrutura do item
- **Base do item:** define slot, status base, implícito e, em armas e armaduras, as opções de skill.
- **Raridade:** Normal (0 afixos), Mágico (1–2), Raro (3–6: até 3 prefixos + 3 sufixos). **Únicos fora do MVP.**
- **Afixos:** prefixos e sufixos sorteados com tiers de valor.
- **Nível do item:** igual ao tier do mapa de origem; limita os tiers de afixo possíveis.

### 8.3 Baú e filtro de loot
- O loot vai para o **baú** ao fim de cada sala.
- O **filtro de loot** decide por raridade mínima, tipo de base e (opcional) presença de afixo.
- O que o filtro rejeita vira **pó rúnico**.

## 9. Crafting — Runas

| Runa | Efeito |
|---|---|
| Runa da Centelha | Normal → Mágico |
| Runa do Eco | Re-sorteia os afixos de um Mágico |
| Runa da Coroa | Mágico → Raro |
| Runa da Ruína | Re-sorteia os afixos de um Raro |
| Runa do Acréscimo | Adiciona 1 afixo a um Raro |

- **Pó rúnico** se acumula e é convertido em runas; também paga o respec.
- Fora do MVP: remover afixo, re-sortear valores, crafting determinístico.

## 10. Progresso offline

- Limite de **3 horas**.
- Ao voltar, o jogo simula sem tela algumas runs aceleradas (ex.: 5) com a configuração **atual**, tira as médias (tempo por run, taxa de morte, loot) e projeta para o tempo ausente. O jogador não precisa revisar nada.
- Se o loop pararia por 3 mortes seguidas, o offline conta só até esse ponto.

## 11. Arte e apresentação

- **Pixel art top-down, 32x32 por célula.**
- MVP com arte placeholder (formas/assets gratuitos); arte final depois de validar o loop.
- Interface pensada para mouse, com tooltips densos de itens.

## 12. Save

- Local, JSON versionado com migração entre versões.
- Autosave a cada sala concluída e ao fechar o jogo.
- Save na nuvem (ex.: Steam Cloud) fora do MVP.

## 13. Facções (pós-MVP)

No MVP as facções existem só na lore e nos NPCs da Fogueira; o sistema entra na versão seguinte. Ver `docs/LORE.md`.

- **Reputação** independente por facção: ganhar com uma nunca faz perder com outra; o personagem não se filia.
- **Contratos:** objetivos que avançam sozinhos durante o loop (inclusive offline). O jogador escolhe quais ativar, até um limite de contratos ativos — o único custo de escolha.

| Facção | Contratos (exemplos) | Sistema que libera |
|---|---|---|
| O Bastião | Estabilizar Fendas (matar chefes), runs sem morte | Bases defensivas, mais regras de prioridade |
| O Círculo da Névoa | Caçar famílias de monstros, matar elites | Novas Fendas e modificadores de mapa exclusivos |
| O Conclave Rúnico | Fendas com N modificadores, recuperar runas | Novas runas, melhor conversão de pó rúnico, crafting determinístico |

- Recompensas de facção nunca alteram a árvore de passivas (ADR 0002).
- NPCs de cada facção têm arcos próprios que avançam com a reputação e revelam o mistério da Quebra por pontos de vista diferentes; não há afinidade numérica por NPC nem escolhas exclusivas entre facções nos sistemas.

## 14. Escopo do MVP (primeiro jogável)

1. Um personagem, nível máximo 60.
2. **4 tipos de arma:** Espada + Escudo (corpo a corpo, mão secundária), Arco + Aljava (à distância), Grimório necromântico (caos, invocações), Cajado elemental (magia de área, fogo/gelo/raio). Druida e Xamã ficam fora do MVP por serem mais complexos; as demais entram em seguida reaproveitando os sistemas.
   - Skills no MVP: 4 × 9 = 36 de arma + 18 de armadura (2 opções por peso e slot) ≈ **54**. Design completo: 81 de arma + 6 de forma + 27 de armadura + 9 ataques básicos ≈ 123.
3. Combate em grid por ticks com comportamento de posicionamento e 6 regras de prioridade.
4. Mapas por tier com modificadores, salas + chefe, monstros normal/elite/chefe.
5. Itens Normal/Mágico/Raro com afixos, mão secundária, skills de armadura.
6. Árvore de passivas com ~60–100 nós.
7. Filtro de loot, pó rúnico e 5 runas.
8. Progresso offline de até 3h e save local.

## 15. Questões em aberto

- [ ] Nome do jogo.
- [ ] Cinto entra como slot no MVP?
- [ ] Quais mãos secundárias cada arma de uma mão aceita (Escudo e Foco para todas?).
- [ ] Monetização e plataforma de lançamento (Steam, itch).
