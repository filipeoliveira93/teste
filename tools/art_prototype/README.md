# PROTÓTIPO — descartável

**Pergunta:** dá para o agente gerar a arte 32x32 do jogo a partir de sprites em texto, com paleta travada (Endesga 32), paper-doll (corpo + armadura + arma) e variantes por troca de paleta?

```
python3 tools/art_prototype/build.py   # requer Pillow
```

Gera `out/hero_<armadura>_<arma>.png` (4 armaduras × 5 armas), `out/goblin_<variante>.png` (normal, fogo, gelo) e `out/preview.png` (prancha ampliada 6x).

## Formato do sprite (`sprites/*.txt`)

```
key o black            # caractere -> nome de cor da Endesga 32 (ver NAMES em build.py)
layer base z=0 at=0,5  # camada com profundidade z e deslocamento x,y na célula 32x32
....oooo....           # grade; '.' é transparente
```

- Paper-doll: todas as camadas dos sprites escolhidos são empilhadas por `z` (corpo 0, armadura 10, elmo 20, arma 25, mão 30). A mão fica numa camada própria do corpo para ficar por cima do cabo da arma.
- Variantes: `GOBLIN_VARIANTS` troca cores por nome (`green -> red`).
- O build falha se aparecer cor fora da paleta, caractere sem `key`, linha com largura diferente ou camada passando da borda.

## Veredito (até aqui)

- Funciona: personagem e inimigo legíveis em 32x32; 8 arquivos de texto geram 23 sprites; a troca de paleta sai de graça.
- O fluxo de iteração é viável: o agente renderiza a prancha, olha o PNG e corrige (arco e machado foram refeitos assim).
- Em aberto: animação (quadros por camada), direção (só frente ou 4 lados), atlas e import no Godot (filtro `nearest`).
