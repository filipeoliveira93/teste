# PROTÓTIPO — descartável

**Pergunta:** dá para o agente gerar personagens no Blender, por script, e renderizar sprites top-down 3/4 em 8 direções?

```
uv venv -p 3.11 .venv-bpy && uv pip install -p .venv-bpy/bin/python bpy   # Blender 5.0 como módulo
.venv-bpy/bin/python tools/art_prototype_blender/build.py 128             # 8 PNGs em ~15 s (CPU)
python3 tools/art_prototype_blender/sheet.py                              # pranchas 128 e 512
```

## Veredito (até aqui)

- **O pipeline funciona:** Blender sem interface, Cycles na CPU, luz quente + contraluz fria, sombra no chão com fundo transparente, 8 direções idênticas em ~2 s cada. A consistência entre direções é perfeita (é o mesmo modelo).
- **A modelagem por primitivas não serve como arte final:** corpo pelo modificador Skin + esferas/cilindros fica com cara de boneco de brinquedo; a capa e a ferrugem precisam de ajuste.
- **Para ficar realista, o modelo tem que vir de fora:** humanos realistas CC0 (MakeHuman/MPFB), pacotes de armadura e criaturas (CC0 ou pagos), ou um artista 3D. O agente entra na montagem (equipamento como malhas trocáveis = paper-doll), materiais, luz, animação aplicada ao rig e render em lote.
- Os sites de modelos (quaternius.com, itch.io, poly.pizza, download.blender.org) estão bloqueados neste ambiente; só o PyPI passou.
