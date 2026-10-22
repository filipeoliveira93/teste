# Simulação em grid discreto por ticks, desacoplada da Godot

Toda a lógica do jogo (movimento, combate, áreas de efeito, loot, progressão) roda num grid de células em ticks fixos, de forma determinística a partir de um seed, sem depender de nós de cena da Godot; a apresentação top-down apenas anima a transição entre ticks. Escolhemos isso em vez de movimento contínuo com física da engine para que a simulação seja testável, reproduzível e barata o bastante para rodar runs aceleradas, e para que a visualização possa mudar sem tocar nas regras.

## Consequences

- O progresso offline não é simulado tick a tick: é estimado a partir das médias das últimas runs reais com a mesma configuração.
- Áreas de efeito são formas sobre células (quadrado, cone, linha), não colisões físicas.
