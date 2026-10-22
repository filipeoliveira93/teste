# AGENTS.md

Idle ARPG em **Godot 4.x (GDScript)**: personagem limpa mapas automaticamente (combate por regras de prioridade), com loot de afixos, árvore de passivas, skills definidas pela arma, crafting e runs de mapa roguelike.

- Design do jogo: `docs/GDD.md`
- Idioma: conversas e documentação em português-BR; identificadores de código em inglês.
- Regra de arquitetura: a simulação (combate, stats, loot, crafting, progressão) não depende de nós de cena, para permitir progresso offline e testes automatizados.

## Agent skills

Skills de [mattpocock/skills](https://github.com/mattpocock/skills) copiadas em `.claude/skills/` (Claude Code) e `.agents/skills/` (Codex). Fluxo padrão: `/grill-with-docs` → `/to-spec` → `/to-tickets` → `/implement` (com `/tdd`) → `/code-review`.

### Issue tracker

Specs e tickets em markdown local, em `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Os cinco papéis padrão (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`) gravados como linha `Status:` nos tickets. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `GLOSSARY.md` e `docs/adr/` na raiz. See `docs/agents/domain.md`.
