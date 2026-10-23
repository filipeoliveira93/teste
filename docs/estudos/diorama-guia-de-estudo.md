# Guia de estudo: Diorama

Material para entender, com calma, como funciona o [Diorama](https://github.com/leduardo99/diorama) (MIT), a ferramenta que gera sprites 2.5D a partir de código TypeScript. Está em avaliação como pipeline de arte do jogo.

> **Como usar este guia.** Leia na ordem. Cada nível depende do anterior. Não tente entender o código do motor antes de ter rodado o exemplo e mexido em um número. O código só faz sentido depois que você viu o resultado.

---

## Nível 0: a ideia em uma frase

**O arquivo `.ts` não guarda a imagem; guarda a receita para desenhá-la.** O exportador executa a receita num navegador invisível e salva o resultado como PNG + JSON.

Analogia: você descreve uma maquete por telefone ("uma caixa de 40×30×26 de madeira; em cima, uma vela"). Do outro lado, alguém com régua, câmera e lanterna fixas monta, fotografa de 8 ângulos e te devolve as fotos. O Diorama é esse "alguém".

```
receita (.ts)  ──►  motor monta a maquete 3D  ──►  fotografa com câmera fixa  ──►  PNG + JSON
```

Por que isso é bom para nós:
- A IA escreve código bem, mas não desenha pixel por pixel com consistência. O Diorama transforma "fazer arte" em "escrever código".
- Mudar é editar um número; todas as direções e frames mudam juntos.
- Mesma câmera, mesma luz, mesma paleta: tudo combina.
- O JSON traz dados de jogo (evento de dano, velocidade, sockets) gerados pelo mesmo código que desenha, então nunca saem de sincronia.

---

## Nível 1: usar sem entender o motor

Objetivo: **ver funcionando**. Nada de ler `core/` ainda.

### Instalação (Windows, PowerShell)

Requer Node.js 20+.

```powershell
cd C:\Users\Admin\Documents
git clone https://github.com/leduardo99/diorama
cd diorama
npm install
npx playwright install chromium
npm run doctor        # só siga quando aparecer "Environment is ready."
npm run example       # exporta o jogo de exemplo (~5 min, 165 sprites)
```

Depois, dois cliques em `dev.bat` abrem o viewer em `http://localhost:5173`.

### O que olhar no viewer

| Aba | O que fazer |
|---|---|
| **Assets** | Abrir um personagem e ver as 8 direções animadas |
| **Playground** | Andar com WASD, Shift corre, 1–9 atacam, H toma dano, K morre |
| **Customize** | Trocar a armadura de um personagem |
| **Scenery** | Pintar uma sala com chão, paredes e portas |

### As quatro fases do fluxo

```
1. PREPARAR   new-project → theme.ts (cores, luz, câmera) + space.ts (grid, escala) + STYLE.md
2. ESCREVER   src/ = a receita (código)   ·   sheets/ = lista do que exportar (1 linha cada)
3. EXPORTAR   check (tipos, layout, determinismo) → export (Chromium invisível → PNG + JSON)
4. CONFERIR   inspect/contact (o agente revisa a imagem) · viewer (você revisa) · --out-dir (copia para o Godot)
```

### Comandos que importam no começo

```powershell
npm run new-project -- meu-jogo --style --genre action-rpg
npm run new-asset   -- meu-jogo props/caixote --engine volume --directions 4
npm run check       -- meu-jogo
npm run export      -- meu-jogo
npm run contact     -- projects/meu-jogo/assets/props/caixote.png
```

### Com um agente (o jeito pensado)

Abra o Claude Code dentro da pasta `diorama` e peça:

> Leia `.agents/skills/diorama/SKILL.md` e crie no projeto `meu-jogo` um esqueleto guerreiro com idle, walk, attack, hit e death, em 8 direções.

O agente escreve o código, roda `check` e `export`, abre a folha de revisão como imagem e corrige o que ficou ruim.

✅ **Você terminou o nível 1 quando:** rodou o exemplo, andou com um personagem no Playground e exportou um caixote seu.

---

## Nível 2: os cinco conceitos de props e cenário

Agora sim, um pouco de motor. Tudo de props e cenário se apoia em **cinco ideias**.

### 1. Câmera (`core/volume/camera.ts`, 134 linhas)

Uma câmera **ortográfica inclinada** (48°, "estilo Hades"). Ortográfica = o que está longe **não** diminui.

Eixos do mundo: **x** para a direita, **y** na direção da câmera, **z** para cima. A projeção inteira:

```ts
tela.x = origem.x + p.x
tela.y = origem.y + p.y * sin(48°) - p.z * cos(48°) * 1.2
```

- Subir em **z** sobe na tela; vir em **y** (para a câmera) desce na tela.
- O `1.2` (`heightBoost`) estica alturas, porque a câmera inclinada achata pernas e paredes.

A **luz** também mora aqui: uma direção mais luz ambiente.

```ts
luz_na_face = ambiente + (1 - ambiente) * max(0, normal · direção_da_luz)
```

Existe **uma câmera por projeto**, em `theme.ts`.

### 2. Frame local (`core/volume/frame.ts`)

Um `Frame3` é um "sistema de coordenadas portátil": origem mais eixos **frente, direita, cima**. Você constrói o objeto em coordenadas locais:

```ts
const frame = Frame3.facing(origem, direcao);
frame.at(10, 0, 5);            // 10 à frente, 0 ao lado, 5 acima
frame.moved(0, 0, 20).turned(30).pitched(-15);  // sub-frames: tampa inclinada, braço girado
```

**É assim que as 8 direções saem de graça:** o exportador chama o mesmo código com `direcao` diferente para cada linha do sprite sheet.

### 3. Volumes (`core/volume/volume.ts`)

As peças de montar:

| Peça | Forma | Uso típico |
|---|---|---|
| `Solid.box`, `Solid.extrude` | faces planas | caixote, lápide, parede |
| `Round.cylinder`, `ellipsoid`, `lathe` | anéis empilhados | vela, vaso, cabeça, tronco |
| `Tube` | fita afinada por pontos | braços, cordas, chifres |
| `Blob` | junção de Rounds e Tubes | corpos orgânicos |
| `Decal` | desenho 2D colado numa face | rachadura, entalhe, musgo |

Como um sólido é pintado, em cinco passos:
1. Descarta as faces de costas para a câmera.
2. Projeta os cantos de cada face na tela.
3. Calcula a luz da face e escolhe **1 de 3 tons** do material (escuro, base ou claro). Isso é **cel shading**.
4. Pinta o polígono, a textura e os detalhes.
5. Traça a linha da silhueta e linhas finas nas dobras com mais de 30°.

Volumes redondos não têm faces: o motor calcula a **silhueta** de todos os anéis projetados e pinta um sombreamento de forma por dentro.

### 4. Palco: quem fica na frente (`core/volume/stage.ts`, 240 linhas)

Não há z-buffer. A ordem é o **algoritmo do pintor** (desenha do fundo para a frente), em dois níveis:

```
Stage
 ├── objeto "baú"   ← objetos ordenados por onde tocam o chão
 │    ├── corpo     ← partes ordenadas face por face pela profundidade
 │    ├── tampa
 │    └── fechadura { on: tampa }   ← "on" = sempre depois do hospedeiro
 └── objeto "vela"
```

O `stage.object()` agrupa as partes de uma coisa física. O `{ on: x }` diz "isto está preso em x". Antes de pintar as partes, o motor traça a **silhueta inteira com uma linha grossa**; as partes cobrem o lado de dentro e só a borda externa fica visível. É isso que dá o traço de ilustração.

### 5. Material (`VolumeStyle` em `volume.ts`, definido no `theme.ts`)

Um material é uma rampa de **três cores** (`lit`, `base`, `dark`) mais contorno, linha de dobra, textura e sombra. Ex.: `VOLUMES.wood`, `VOLUMES.stone`. **Só o `theme.ts` pode ter cores**; o `check` barra cor solta em outro arquivo.

### Juntando os cinco: o caixote

```ts
const caixote = stage.object();                                // 4. um objeto no palco
caixote.add(Solid.box(frame, 40, 30, 26), VOLUMES.wood);       // 3. volume · 2. frame · 5. material
stage.draw(ctx);                                               // 1. câmera projeta e ilumina; 4. ordena e pinta
```

✅ **Você terminou o nível 2 quando:** consegue explicar por que mudar `40` para `50` alonga o caixote nas 4 direções, e por que ele tem três tons.

---

## Nível 3: personagens animados

Um personagem tem **seis peças**. Leia nesta ordem.

### 1. Esqueleto (`core/rig/skeleton.ts`, `presets.ts`)

**Só dados**: um tronco (cadeia de juntas do quadril à cabeça), pernas (2 ossos + pé), braços, caudas e andares. `humanoid()` e `quadruped()` são presets.

### 2. IK de dois ossos (`core/rig/ik.ts`, 39 linhas)

"O pé tem que estar **aqui**; onde fica o joelho?" A resposta sai da lei dos cossenos. É o que mantém o pé plantado no chão.

### 3. Andar (`core/rig/gait.ts`)

Cada perna tem uma **fase** no ciclo (o bípede alterna 0 e 0.5). No apoio, o pé fica parado no chão e o corpo passa por cima; no balanço, o pé sobe e volta à frente. Daí sai a velocidade exata:

```
groundSpeed = passada × cadência ÷ fração_no_chão
```

O jogo move o sprite nessa velocidade e o pé não patina. Esse número vai para o JSON.

### 4. Drive e pose (`core/rig/pose.ts`)

- **Drive** = a intenção: onde estão os pés, quanto o tronco abaixa, quanto o braço balança.
- **Pose** = o resultado: a posição 3D de cada junta, resolvida com IK por `solvePose`.

### 5. Clipe (`core/rig/clips.ts`, `presets.ts`)

Um clipe é **uma função do tempo**: `drive(t)`, com `t` de 0 a 1, mais metadados (duração, loop, eventos como `hit` no frame do golpe).

Presets prontos: `idle`, `locomotion`, `slash`, `bite`, `hit`, `jump`, `dodge`, `death`. Para personalizar, você embrulha um preset e altera o drive:

```ts
const d = base.drive(t);                          // pose do preset
return { ...d, extra: { ears: s, jaw: 0.23 * s } }; // + orelhas baixando, mandíbula caindo
```

### 6. Pele e personagem (`core/rig/character.ts`)

A **pele** (*skin*) é uma função que recebe a pose e cria volumes presos às juntas: um `Tube` do ombro ao cotovelo, um `ellipsoid` na cabeça. Os **equipamentos** são peles reutilizáveis por slot.

Para **cada célula** do sprite sheet, `drawCharacterFrame` faz:

```
t = frame / total_de_frames
drive = clip.drive(t)               → a intenção
pose  = solvePose(esqueleto, drive) → juntas no lugar (IK)
frame girado para a direção da linha
pele cria volumes nas juntas → Stage ordena → câmera projeta e ilumina → Canvas pinta
```

✅ **Você terminou o nível 3 quando:** consegue explicar por que o `walk` do lobo tem um `groundSpeed` e por que o pé não escorrega.

---

## Nível 4: a saída e o jogo

### O contrato de asset (`core/asset.ts`)

Tudo o que é exportado passa por `defineAsset`: tamanho, `frames`, `directions`, `pivot`, `data` e uma função `render(ctx)`. O exportador chama `render` **uma vez por célula** (frame × direção).

Opção relevante para nós: `antialiasing`.
- `'native'`: bordas suaves (padrão).
- `'none'`: cada pixel vira totalmente opaco ou totalmente transparente.
- `'dither'`: transparência com padrão Bayer 4×4, visual retrô.

Isso deixa as bordas com cara de pixel art, mas **não** reduz a paleta nem a resolução.

### O exportador (`tools/export.ts`)

```
para cada arquivo em sheets/:
  sobe um servidor Vite → abre Chromium invisível (Playwright) → carrega a receita
  → render() em cada célula → print do canvas = PNG → metadados = JSON
  → grava em assets/ (e copia para --out-dir, se houver)
```

### O JSON do atlas (contrato em `docs/guides/rig/04-atlas-contract.md`)

| Campo | Para que o jogo usa |
|---|---|
| `frames` | Onde está cada frame no PNG |
| `meta.pivot` | Onde ficam os pés (ponto de ancoragem) |
| `meta.fps`, `loop`, `hold` | Como tocar a animação |
| `events` | `hit` = aplicar dano neste frame; `cast`, `release`, `step`… |
| `groundSpeed` | Velocidade para mover o sprite sem patinar |
| `sockets` | Posição da mão e da boca em cada frame, para encaixar efeitos |
| `travel` | Root motion de ataques que avançam |

Regra de prioridade sugerida pelo contrato: **morte > dano > ações > locomoção > idle**.

### Para o Godot

`--out-dir=<pasta do jogo>` já copia os arquivos. **Falta um importador GDScript** que leia o JSON e monte `SpriteFrames` mais os eventos. Isso fica do nosso lado e conversa com a simulação por ticks (ADR 0001): a simulação emite "atacou" e a apresentação toca o clipe e sincroniza com o evento `hit`.

---

## Roteiro de leitura do código

Leia só depois dos níveis 1 a 3. Ordem sugerida, do menor para o maior:

| # | Arquivo | Linhas | O que procurar |
|---|---|---|---|
| 1 | `core/asset.ts` | 297 | `defineAsset` e `createCanvas`: o que é um asset |
| 2 | `core/volume/camera.ts` | 134 | `project`, `depth`, `shade` |
| 3 | `core/volume/frame.ts` | 115 | `facing`, `at`, `turned` |
| 4 | `core/volume/stage.ts` | 240 | `StageObject.draw`, `Stage.draw` (as duas ordenações) |
| 5 | `core/volume/volume.ts` | 825 | `rampTone`, `Solid.pieces`, `Round.draw` |
| 6 | `examples/soulkeeper/src/scenery/props.ts` | — | Um prop de verdade usando tudo acima |
| 7 | `core/rig/skeleton.ts` + `presets.ts` (`humanoid`) | — | Como um esqueleto é descrito |
| 8 | `core/rig/ik.ts` | 39 | `twoBone` |
| 9 | `core/rig/gait.ts` | 87 | `groundSpeed`, fases das pernas |
| 10 | `core/rig/clips.ts` | 235 | `Clip`, `locomotion`, `idle` |
| 11 | `core/rig/character.ts` | 521 | `drawCharacterFrame`, `defineCharacterAsset` |
| 12 | `examples/soulkeeper/src/characters/wolf/` | — | Um personagem completo |

Leitura de apoio, em inglês e bem escrita: `docs/guides/volume/01…06` e `docs/guides/rig/01…05`.

---

## Exercícios, do mais fácil ao mais difícil

1. **Mudar um número.** No caixote, troque `40` por `60`, exporte e compare as 4 direções.
2. **Trocar o material.** Use `VOLUMES.stone` no lugar de `wood`. Por que a cor muda sem você escrever nenhuma cor?
3. **Empilhar.** Adicione um cilindro em cima do caixote com `{ on: corpo }`. Gire para todas as direções: ele fica sempre por cima?
4. **Mudar a luz.** Em `theme.ts`, altere o `azimuth` da luz. O que acontece com **todos** os assets?
5. **Andar mais rápido.** No `walk` de um personagem, aumente a cadência. Veja o `groundSpeed` no JSON mudar.
6. **Bordas duras.** Exporte o caixote com `antialiasing: 'none'` e compare com o nosso alvo de pixel art 32×32.
7. **Ler o JSON.** Abra o `.json` de um ataque e encontre o frame do evento `hit`.

---

## Glossário rápido (termo em inglês → o que significa)

| Termo | Significado |
|---|---|
| asset | qualquer coisa exportada (prop, personagem, ícone, efeito, HUD) |
| sheet / sprite sheet | o PNG em grade: linhas = direções, colunas = frames |
| atlas | o JSON que acompanha o PNG |
| facing / direction | direção que o objeto encara (4 ou 8) |
| pivot | ponto de ancoragem (os pés) |
| volume | forma 3D (Solid, Round, Tube, Blob, Decal) |
| stage | o palco que ordena e pinta |
| ramp | rampa de 3 tons de um material |
| cel shading | sombreamento em faixas, sem degradê |
| contour | contorno externo grosso da silhueta |
| rig | esqueleto + animação |
| IK | cinemática inversa: achar o joelho a partir do pé |
| gait | padrão de andar (walk, run, trot) |
| drive | a intenção de pose num instante |
| pose | as juntas resolvidas no espaço |
| clip | uma animação (função do tempo + metadados) |
| skin | a "pele": volumes presos às juntas |
| gear / outfit | equipamento / conjunto de equipamentos |
| socket | ponto nomeado (mão, boca) exportado por frame |
| kit / catalog | conjunto de peças de um tipo e seu índice |
| deterministic | mesma receita gera sempre os mesmos pixels |

---

## Decisões em aberto para o nosso jogo

1. **Direção de arte.** O `docs/GDD.md` §11 pede pixel art top-down 32×32. O Diorama gera 2.5D vetorial em câmera 3/4 (tile de 48×36 px no exemplo). Adotar o Diorama significa mudar o GDD, e isso pede um ADR.
2. **Pixel art com o Diorama?** Testar `antialiasing: 'none'` + `scale: 1` + paleta curta no `theme.ts`. Se não bastar, avaliar um pós-processamento (redução e quantização de cor).
3. **Importador Godot.** É um ticket próprio: JSON → `SpriteFrames` + eventos + sockets.
4. **Onde mora o projeto de arte.** Num repositório separado (`projects/<jogo>` dentro de um clone do Diorama), com `--out-dir` apontando para o projeto Godot.
