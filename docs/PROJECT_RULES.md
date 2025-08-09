# PROJECT RULES - AVS AI ORCHESTRATOR

## 🚫 STRICT FILE MANAGEMENT RULES

### CORE PRINCIPLE: REFACTOR, DON'T DUPLICATE

**❌ FORBIDDEN ACTIONS:**
- Creating variant files (demo_*, dev_*, test_*, final_*, enhanced_*, etc.)
- Duplicating functionality across multiple files
- Creating new files when existing ones can be extended
- Adding "v2", "new", "improved", "better" versions

**✅ REQUIRED ACTIONS:**
- **ALWAYS REFACTOR** existing files instead of creating new ones
- Consolidate similar functionality into single files
- Use configuration/parameters for variants instead of separate files
- Extend existing classes/functions rather than rewriting them

## 📁 AUTHORIZED FILE STRUCTURE

### Core Orchestrators (ONLY THESE)
- `github_tdd_orchestrator.py` - GitHub TDD workflow orchestrator
- `universal_orchestrator.py` - Generic project orchestrator

### Configuration Files
- `config/mcp_agents.yaml` - MCP agent configuration
- `config/tdd.yaml` - TDD workflow settings
- `mcp.json` - MCP server definitions
- `.env.mcp` - Environment variables

### Setup Files
- `docker_compose_mcp.yml` - MCP Docker services
- `scripts/start_mcp.bat` - MCP server startup
- `MCP_SETUP.md` - MCP documentation

### Project Documentation
- `CLAUDE.md` - Claude context and instructions
- `PROJECT_RULES.md` - This file
- `README.md` - Project overview (when needed)

### Directory Structure
```
src/
├── agents/           # Specialized agents
├── workflows/        # Workflow definitions
├── utils/           # Shared utilities
└── tests/           # Test files
```

## 🔧 REFACTORING GUIDELINES

### When Adding Features
1. **Check existing files first** - Can functionality be added to existing orchestrator?
2. **Use configuration** - Add parameters/config instead of new files
3. **Extend classes** - Use inheritance/composition, not duplication
4. **Modular functions** - Add functions to existing modules

### When Fixing Issues
1. **Fix in place** - Modify existing file, don't create new version
2. **Backward compatibility** - Maintain existing interfaces
3. **Configuration flags** - Use flags for different behaviors
4. **Deprecation path** - Mark old code as deprecated if needed

### Code Organization
```python
# GOOD: Single orchestrator with modes
class Orchestrator:
    def __init__(self, mode="production"):
        self.mode = mode
    
    def run(self):
        if self.mode == "demo":
            return self._demo_workflow()
        elif self.mode == "test":
            return self._test_workflow()
        return self._production_workflow()

# BAD: Multiple orchestrator files
# demo_orchestrator.py
# test_orchestrator.py  
# production_orchestrator.py
```

## 🎯 IMPLEMENTATION RULES

### For New Features
1. **Analyze existing code** - Where does this functionality belong?
2. **Extend, don't replace** - Add to existing classes/modules
3. **Use factory patterns** - Create instances based on config
4. **Plugin architecture** - Make features pluggable

### For Bug Fixes
1. **Fix root cause** - Don't create workaround files
2. **Add tests** - Ensure fix works correctly
3. **Update documentation** - Reflect changes in existing docs
4. **Single source of truth** - One place for each functionality

### For Experiments
1. **Feature branches** - Use git branches, not files
2. **Configuration flags** - Enable/disable experimental features
3. **Environment variables** - Control behavior without code changes
4. **Plugin system** - Load experimental modules conditionally

## 📊 QUALITY METRICS

### File Count Targets
- **Core files**: ≤ 2 orchestrators
- **Config files**: ≤ 5 configuration files
- **Utility modules**: ≤ 3 in src/utils/
- **Documentation**: ≤ 5 .md files

### Complexity Limits
- **File size**: ≤ 500 lines per file (refactor if larger)
- **Function size**: ≤ 50 lines per function
- **Class methods**: ≤ 20 methods per class
- **Cyclomatic complexity**: ≤ 10 per function

## ❌ FORBIDDEN IN PYTHON CODE

### Encoding Issues Prevention
1. **NEVER use emojis in Python scripts** - Causes UnicodeEncodeError on Windows
2. **Use ASCII-only text** in print statements and user output
3. **Alternative text representations:**
   - ✅ → "OK" or "[OK]"
   - ❌ → "ERROR" or "[ERROR]"
   - ⚠️ → "WARN" or "[WARN]"
   - 🔧 → "INFO" or "[INFO]"
   - 🚀 → "START" or "[START]"

### Allowed Emoji Usage
- **Git commit messages** ✅
- **Markdown documentation** ✅ 
- **Code comments** ✅ (but not recommended)
- **Python strings/prints** ❌ **FORBIDDEN**

## 🚨 VIOLATION PENALTIES

### Automatic Actions on Rule Violation
1. **Immediate deletion** of variant files
2. **Mandatory refactoring** before proceeding
3. **Code review** required for structural changes
4. **Documentation update** required for any changes

### Code Review Checklist
- [ ] Does this create duplicate functionality?
- [ ] Could this be added to existing files?
- [ ] Is this the simplest solution?
- [ ] Does this follow the single responsibility principle?
- [ ] Can this be configured instead of hardcoded?

## 🔄 REFACTORING PROCESS

### Step 1: Analysis
- Identify duplicate/similar functionality
- Map dependencies and relationships
- Plan consolidation strategy

### Step 2: Consolidation
- Merge similar functions/classes
- Create unified interfaces
- Add configuration parameters

### Step 3: Testing
- Ensure all functionality still works
- Add tests for new consolidated code
- Verify backward compatibility

### Step 4: Cleanup
- Delete old/duplicate files
- Update imports and references
- Update documentation

## 💡 BEST PRACTICES

### Configuration Over Code
```python
# GOOD: Configurable behavior
config = {
    "workflow_type": "tdd",
    "github_integration": True,
    "auto_deploy": False
}
orchestrator = Orchestrator(config)

# BAD: Separate files for each configuration
# tdd_orchestrator.py
# github_orchestrator.py
# deploy_orchestrator.py
```

### Composition Over Inheritance
```python
# GOOD: Compose features
class Orchestrator:
    def __init__(self):
        self.github = GitHubIntegration()
        self.tdd = TDDWorkflow()
        self.deploy = DeploymentManager()

# BAD: Create variants
# GitHubTDDOrchestrator
# GitHubDeployOrchestrator
# TDDDeployOrchestrator
```

---

**REMEMBER: Every file you want to create should first be questioned - can this be refactored into an existing file instead?**