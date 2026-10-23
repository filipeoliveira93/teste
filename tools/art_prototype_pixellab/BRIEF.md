# PROTÓTIPO — teste da PixelLab (128px)

**Pergunta:** a PixelLab gera, a partir de texto, sprites dark fantasy em 128px, consistentes entre si, com 8 direções e animação, bons o bastante para o jogo?

Acesso: servidor MCP em `.mcp.json` (token em `PIXELLAB_SECRET`, secret do ambiente; nunca no repo).

## Direção de arte (vale para todos os prompts)

- Pixel art **dark fantasy**, vista **top-down 3/4** (câmera alta, levemente inclinada), canvas **128x128**.
- Paleta dessaturada e escura: ferro enegrecido, couro gasto, linho sujo, sangue seco, ferrugem; cor saturada só em brilhos (brasa, alma).
- Luz quente vinda de cima/esquerda (tocha); sombras profundas; contorno escuro seletivo.
- Proporção heroica (não chibi). Mundo após "a Quebra": decadente, ruínas, corrupção (ver `docs/LORE.md`).

## Lote do teste

| # | Asset | Saída | Critério de aprovação |
|---|---|---|---|
| 1 | Herói, armadura pesada (placas enegrecidas, capa rasgada, elmo fechado), espada longa | 8 direções | Silhueta legível em 128px; mesmo personagem em todas as direções |
| 2 | Herói nº 1 | animações parado, andar, ataque | Arma e capa coerentes entre quadros |
| 3 | Mesmo herói em armadura leve (couro + capuz) com arco | 8 direções | Mantém rosto, corpo e paleta do nº 1 (teste de "variante de equipamento") |
| 4 | Carniçal (corcunda, magro, garras, olhos em brasa) | 8 direções + andar | Consistente com o estilo do herói |
| 5 | Carniçal queimado e congelado | variação do nº 4 | Mesma forma, só material/cor muda |
| 6 | Ícones: espada longa, elmo fechado, anel com runa | 1 imagem cada | Lê bem no tooltip; mesma paleta |

## O que registrar

Para cada asset: prompt exato, parâmetros (seed, referência de estilo), custo em créditos e tempo. Saídas em `out/`, prancha comparativa em `out/preview.png`.

## Veredito

_A preencher depois do teste._
