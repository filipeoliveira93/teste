# AGENTS.md

Idle ARPG em **Godot 4.x (GDScript)**: personagem repete runs em mapas automaticamente (combate top-down em grid, por regras de prioridade), com loot de afixos, árvore de passivas, skills definidas pela arma e crafting com runas.

- Design do jogo: `docs/GDD.md` · Vocabulário: `GLOSSARY.md` · Decisões: `docs/adr/`
- Idioma: conversas e documentação em português-BR; identificadores de código em inglês.
- Regra de arquitetura: a simulação roda em grid por ticks, determinística e sem depender de nós de cena (ADR 0001).

## Agent skills

Skills de [mattpocock/skills](https://github.com/mattpocock/skills) copiadas em `.claude/skills/` (Claude Code) e `.agents/skills/` (Codex). Fluxo padrão: `/grill-with-docs` → `/to-spec` → `/to-tickets` → `/implement` (com `/tdd`) → `/code-review`.

### Issue tracker

Specs e tickets em markdown local, em `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Os cinco papéis padrão (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`) gravados como linha `Status:` nos tickets. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `GLOSSARY.md` e `docs/adr/` na raiz. See `docs/agents/domain.md`.
