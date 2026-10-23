# PROTÓTIPO — descartável

**Pergunta:** dá para sair do visual "recorte de papel" e chegar a sprites vetoriais mais realistas e sombrios, ainda gerados pelo agente a partir de texto?

```
pip install cairosvg scipy
python3 tools/art_prototype_painted/build.py   # ~25 s para 5 sprites
```

## Ideia: SVG como silhueta + iluminação 2.5D

O SVG define só **silhuetas e materiais**; cada filho de `<g data-z>` é uma peça (`data-mat`, `data-vol`, `fill="@cor"`). O build, para cada peça, em 640px:

1. renderiza a máscara e gera um mapa de altura (máscara borrada por `data-vol` + textura do material);
2. tira as normais e ilumina: tocha quente vindo de cima/esquerda, ambiente frio, especular e reflexo falso (metal), luz de borda fria à direita;
3. projeta a sombra da peça no que já foi pintado (sombra de contato) e compõe; sem contorno;
4. `data-mat="glow"` soma brilho emissivo no fim; `flat` pinta o SVG como está (olhos, ferrugem, costelas);
5. reduz para 160px com Lanczos.

Materiais: cloth, skin, leather, hair, wood, metal, mail (anéis procedurais), glow, flat.

## Veredito (até aqui)

- O efeito de recorte some: volume, metal enegrecido com reflexo, malha, sombra entre camadas e olhos em brasa leem como sprite renderizado.
- Troca de cor continua de graça (carniçal podre / queimado / congelado).
- Limite: o realismo agora depende das **silhuetas**. Anatomia em formas simples ainda parece manequim (herói sem armadura). Personagens cobertos (armadura, criaturas) funcionam melhor.
- O sprite final é PNG (o Godot não reproduz esse pipeline a partir do SVG).
