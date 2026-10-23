# PROTÓTIPO — descartável

**Pergunta:** em vez de pixel art, dá para o agente gerar sprites vetoriais (SVG, estilo cartoon) com mais detalhe, mantendo Endesga 32, paper-doll e variantes por troca de paleta?

```
pip install cairosvg                      # rasterizador SVG -> PNG (usa libcairo)
python3 tools/art_prototype_svg/build.py
```

Gera em `out/`: `hero_<armadura>_<arma>.svg|png` (4 × 5), `goblin_<variante>.svg|png`, `preview.png` (tamanho real, 160px) e `preview_zoom.png` (3x, mesmo vetor). Compare com `tools/art_prototype/` (32px) e `tools/art_prototype_64/` (64px).

## Formato (`sprites/*.svg`)

Fragmentos SVG comuns, com um ou mais grupos de topo `<g data-z="N">` (corpo 0, armadura 10, elmo 20, arma 25, mão 30).

- Cores: `fill="@green"`, sempre nomes da Endesga 32; o build troca pelo hex e aplica a troca de paleta.
- Sombreamento em blocos: `fill="url(#r-skin)"` (radial, para volumes) ou `url(#l-skin)` (linear, para peças alongadas). As rampas (luz, base, sombra) ficam em `RAMPS` no `build.py`.
- Contorno: todo elemento herda traço preto de 3px; detalhes usam `stroke="none"` ou um `stroke-width` menor.
- Textura: `url(#rings)` (malha) por cima de uma forma.

## Veredito (até aqui)

- Maior detalhe e acabamento dos três protótipos: expressão no rosto, costuras, anéis da malha, pluma, brilho do cajado.
- Escala sem perda (mesmo arquivo serve 160px, 480px...); o `.svg` gerado pode ir direto para o Godot (importa SVG nativamente) ou usar o `.png`.
- O agente escreve SVG com fluência e itera olhando o PNG renderizado.
- Custos: deixa de ser pixel art (muda o GDD §11); animação passa a ser por transformações (rotação/translação de grupos), o que combina com rig 2D (Skeleton2D) no Godot.
