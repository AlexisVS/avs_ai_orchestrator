# 📝 Naming Convention - AI Orchestrator

## 🎯 Principes généraux - Hiérarchie de priorité

### Ordre de priorité pour les standards
1. **Framework standards** (FastAPI, Django, Flask, etc.)
2. **Library conventions** (pytest, asyncio, pydantic, etc.)
3. **Work domain practices** (TDD, orchestration, AI/ML)
4. **Python ecosystem** (PEP 8, standard library patterns)

### Format des noms (Python ecosystem)
- **Python files**: `snake_case.py` (PEP 8)
- **Python packages**: `lowercase` or `snake_case` (PEP 8)
- **Config files**: `lowercase.yaml/json` (industry standard)
- **Documentation**: `UPPERCASE.md` (GitHub convention)
- **Scripts**: `snake_case.py` ou `kebab-case.sh/.bat`

### Structure hiérarchique
```
module_name/
├── core.py          # Fonctionnalité principale
├── config.py        # Configuration
├── models.py        # Modèles de données
├── handlers.py      # Gestionnaires
└── utils.py         # Utilitaires
```

## 📂 Plan de renommage

### Core Orchestrators
```
github_tdd_orchestrator.py     → orchestrator/github.py
universal_orchestrator.py      → orchestrator/core.py
main_autonomous_orchestrator.py → orchestrator/autonomous.py
orchestrator.py                → [SUPPRIMER - redondant]
```

### Configuration Files  
```
config/mcp_agents.yaml          → config/mcp-agents.yaml
config/secrets.yaml         → config/secrets.yaml
config/tdd.yaml                → config/tdd.yaml
config/evolution.yaml     → config/evolution.yaml
config/autonomous.yaml → config/autonomous.yaml
```

### Scripts & Launchers
```
scripts/start_mcp.bat          → scripts/start-mcp.bat
scripts/launch_autonomous.py → scripts/launch-autonomous.py
scripts/start_evolution.py       → scripts/start-evolution.py
```

### Documentation
```
MCP_SETUP.md                   → docs/MCP_SETUP.md
CLAUDE.md                      → docs/CLAUDE.md
PROJECT_RULES.md               → docs/PROJECT_RULES.md
README_AUTO_EVOLUTION.md      → docs/AUTO_EVOLUTION.md
README_ULTIMATE_INDEPENDENCE.md → docs/AUTONOMOUS_MODE.md
```

### MCP Components
```
src/orchestrator/mcp/
├── client.py        # mcp_client.py
├── server.py        # mcp_server.py  
├── manager.py       # mcp_manager.py
├── router.py        # mcp_router.py
├── balancer.py      # mcp_load_balancer.py
└── interface.py     # mcp_interface.py
```

### Agents
```
src/orchestrator/agents/
├── autonomous.py    # autonomous_orchestrator.py
├── bug_detector.py  # bug_detector_agent.py
├── code_gen.py      # code_generator_agent.py
├── github_sync.py   # github_sync_agent.py
├── meta_cognitive.py # meta_cognitive_agent.py
├── evolution.py     # self_evolution_agent.py
└── test_runner.py   # test_runner_agent.py
```

### Tests
```
tests/
├── unit/
│   ├── test_core.py           # test_core_orchestrator.py
│   ├── test_autonomous.py     # test_autonomous_orchestrator_basic.py
│   └── test_mcp.py           # test_mcp_integration.py
├── integration/
│   ├── test_github_sync.py   # test_github_sync_*.py
│   └── test_independence.py  # test_*_independence_*.py
└── e2e/
    ├── test_full_workflow.py # test_autonomous_orchestration.py
    └── test_evolution.py     # test_auto_generation_real.py
```

## 🔧 Standards de nommage

### Modules Python
- **Core functionality**: `core.py`, `main.py`
- **Specific domains**: `github.py`, `mcp.py`, `autonomous.py`
- **Utilities**: `utils.py`, `helpers.py`
- **Models**: `models.py`, `schemas.py`
- **Configuration**: `config.py`, `settings.py`

### Config Files
- **Main config**: `config.yaml`
- **Secrets**: `secrets.yaml`
- **Feature-specific**: `feature-name.yaml`
- **Environment**: `.env`, `.env.example`

### Scripts
- **Startup**: `start-service.sh/bat`
- **Setup**: `setup-feature.sh/bat`  
- **Utility**: `tool-name.sh/bat`

### Documentation
- **Main docs**: `UPPERCASE.md`
- **Guides**: `Guide_Name.md`
- **References**: `API_Reference.md`

## 🚫 À éviter

### Mauvais noms
- `main_autonomous_orchestrator.py` (trop long)
- `github_tdd_orchestrator.py` (préfixes redondants)
- `config/mcp_agents.yaml` (points dans config)
- `test_autonomous_orchestrator_basic.py` (trop verbeux)

### Bonnes alternatives  
- `autonomous.py`
- `github.py`
- `mcp-config.yaml`
- `test_autonomous.py`

## ✅ Règles de validation

### Longueur des noms
- **Fichiers**: Max 20 caractères
- **Modules**: Max 15 caractères  
- **Variables**: Descriptif mais concis

### Cohérence
- **Un style par type** (snake_case pour Python, kebab-case pour config)
- **Préfixes cohérents** par domaine
- **Suffixes standardisés** (`.py`, `.yaml`, `.md`)

### Lisibilité
- **Noms explicites** sans abréviations obscures
- **Hiérarchie claire** dans les dossiers
- **Regroupement logique** des fonctionnalités