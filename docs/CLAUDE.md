# Claude AI Assistant - Project Context and Initialization

## 🚀 AUTO-INITIALIZATION CHECKLIST

When starting a conversation in this folder, Claude should automatically:

### 1. Check Docker MCP Servers Status
```bash
docker ps | grep mcp
```
- If not running: Alert user to run `.\scripts/start_mcp.bat`
- Verify 22 MCP servers are available

### 2. Verify GitHub Connection
- Check GitHub token in environment
- Test connection to repository: AlexisVS/avs_ai_orchestrator
- Check for new issues in GitHub Project #12

### 3. Load Project Context
- This is an AI Agent Orchestrator with TDD workflow
- Multi-agent system with specialized agents (refactor, test, doc, db, git)
- Uses local LM Studio (Qwen3-Coder-30B) on port 1234
- Parent MCP agent available at ../mcp-agent

### 4. Available MCP Tools
You have access to 22 Docker MCP servers:
- **Core**: github, filesystem, git, memory, python
- **Web**: playwright, fetch, wikipedia, youtube-transcript
- **Dev**: dockerhub, npm-sentinel, node-code-sandbox, jetbrains
- **AI**: sequential-thinking, ref-tools, needle
- **API**: api-gateway, openapi-schema
- **Utility**: time, paper-search

### 5. Development Workflow
1. **TDD Cycle**: RED → GREEN → REFACTOR
2. **Quality Gates**: Min 80% coverage, max complexity 10
3. **Auto-features**: Check GitHub issues for auto-generated tasks
4. **Commit Style**: Conventional commits with emojis

## 📋 PROJECT QUICK REFERENCE

### Key Files
- `github_tdd_orchestrator.py` - Main TDD orchestrator
- `universal_orchestrator.py` - Generic project orchestrator
- `config/mcp_agents.yaml` - Agent configurations
- `config/tdd.yaml` - TDD workflow settings

### Current Project Phase
Check GitHub Project #12 for current phase:
- Phase 1: Architecture Multi-Mode Orchestration
- Phase 2: Communication Avancée Inter-Agents
- Phase 3: Monitoring & Auto-Optimisation
- Phase 4: Enterprise Features & Governance

### Active Issues Categories
- ⚡ Auto-Optimisation (Performance)
- 🐛 Auto-Fix (Bug fixes)
- ✨ Auto-Feature (New features)
- 🧪 Auto-Test (Test improvements)

## 🛠️ COMMON TASKS

### Start MCP Servers
```bash
.\scripts/start_mcp.bat
```

### Run TDD Orchestrator
```bash
python github_tdd_orchestrator.py
```

### Check Test Coverage
```bash
python -m pytest --cov=. --cov-report=term-missing
```

### Process GitHub Issues
```python
# The orchestrator will:
1. Fetch issues from GitHub Project #12
2. Generate tests (RED phase)
3. Implement features (GREEN phase)
4. Refactor code (REFACTOR phase)
5. Update GitHub issue with progress
```

## ⚠️ CRITICAL PROJECT RULES

### 🚫 FILE CREATION RULES (MANDATORY)
1. **NEVER CREATE VARIANT FILES** - No demo_*, dev_*, test_*, final_*, enhanced_*, v2, etc.
2. **ALWAYS REFACTOR EXISTING FILES** instead of creating new ones
3. **NO DUPLICATE FUNCTIONALITY** across multiple files
4. **CONSOLIDATE, DON'T PROLIFERATE** - Extend existing classes/functions

### 📁 AUTHORIZED FILES ONLY
- **Core**: `github_tdd_orchestrator.py`, `universal_orchestrator.py`
- **Config**: `config/mcp_agents.yaml`, `config/tdd.yaml`, `mcp.json`, `.env.mcp`
- **Setup**: `docker_compose_mcp.yml`, `scripts/start_mcp.bat`
- **Docs**: `CLAUDE.md`, `PROJECT_RULES.md`, `MCP_SETUP.md`

### 🔧 REFACTORING REQUIREMENTS
1. **Always run lint/typecheck** after code changes
2. **Maintain 80% test coverage** minimum
3. **Follow TDD strictly**: Tests first, then implementation
4. **Use conventional commits** with appropriate emojis
5. **Check GitHub issues** before implementing new features
6. **Verify MCP servers** are running before using them
7. **READ PROJECT_RULES.md** before making any changes

## 🔧 TROUBLESHOOTING

### If MCP servers not accessible:
1. Check Docker is running: `docker info`
2. Start servers: `.\scripts/start_mcp.bat`
3. Verify: `docker ps | grep mcp`

### If GitHub sync fails:
1. Check token: `echo %GITHUB_TOKEN%`
2. Test API: `curl -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/user`

### If tests fail:
1. Run with verbose: `pytest -vvs`
2. Check coverage: `pytest --cov=. --cov-report=html`
3. Open htmlcov/index.html

## 📊 PROJECT METRICS

Track these KPIs:
- Test Coverage: Target >80%
- Code Complexity: Max 10
- Issue Resolution Time: <24h
- Build Success Rate: >95%
- Documentation Coverage: 100%

## 🎯 CURRENT PRIORITIES

1. Implement bidirectional GitHub sync (Issue #1)
2. Enhance TDD workflow (Issue #4)
3. Add vector embeddings support (Issue #5)
4. Implement real-time monitoring (Issue #6)
5. Complete Phase 1 architecture tasks

---

**Note to Claude**: This file should be automatically loaded at the start of each conversation in this project folder. Always check the initialization checklist and alert the user if any required services are not running.