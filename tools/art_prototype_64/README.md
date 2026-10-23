# PROTÓTIPO — descartável

**Pergunta:** em 64x64, dá para o agente gerar pixel art com detalhe suficiente descrevendo **formas** em vez de pixels, mantendo a Endesga 32, o paper-doll e as variantes por troca de paleta?

```
python3 tools/art_prototype_64/build.py   # requer Pillow
```

Gera `out/hero_<armadura>_<arma>.png` (4 × 5), `out/goblin_<variante>.png` e `out/preview.png` (prancha 4x). Compare com `tools/art_prototype/` (32x32, pixel a pixel).

## Pipeline

1. Formas → rasterização sem antialias (centro do pixel dentro/fora).
2. Cada forma é um volume (domo/cilindro); a normal × luz (canto superior esquerdo) escolhe a cor numa **rampa** da paleta.
3. Linha interna na borda da peça de cima: preta entre camadas, cor mais escura da rampa entre peças da mesma camada.
4. Contorno externo preto.
5. Troca de paleta por nome de cor (variantes do goblin).

## Formato (`sprites/*.txt`)

```
ramp skin peach skin_light skin_mid brown   # da luz para a sombra
layer base z=0                              # corpo 0, armadura 10, elmo 20, arma 25, mão 30
ellipse cx cy rx ry RAMPA [opções]
capsule x1 y1 x2 y2 r RAMPA [opções]
rect x y w h RAMPA [opções]
poly RAMPA x,y x,y ... [opções]
dot x y COR | line x1 y1 x2 y2 COR | box x y w h COR   # detalhes de cor fixa
```

Opções: `group=` (formas que se fundem sem linha interna), `flat=i` (índice fixo da rampa), `soft=0..1` (achata o volume), `clip=y` (corta abaixo de y), `pattern=mail|grain` (textura).

## Veredito (até aqui)

- Funciona, e o salto de qualidade é grande: rosto, cabelo, cota de malha, placas e armas leem bem.
- Peças paper-doll de 6 a 25 linhas de texto cada; ajustar é mudar números, e o agente itera olhando a prancha (rosto e armadura pesada foram corrigidos assim).
- Limites: tudo é frontal e simétrico; ainda sem animação nem outras direções; formas orgânicas complexas (capas, cabelo longo) vão exigir mais primitivas (curvas).
