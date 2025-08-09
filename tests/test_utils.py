#!/usr/bin/env python3
"""
Utilitaires pour les tests - Import sécurisé des modules
"""

import sys
import os
import importlib.util
from pathlib import Path

def get_independent_orchestrator():
    """Import sécurisé de IndependentOrchestrator pour les tests"""
    
    # Assurer le bon chemin pour l'import
    project_root = str(Path(__file__).parent.parent)
    sys.path.insert(0, project_root)
    os.chdir(project_root)
    
    try:
        from orchestrator.autonomous import IndependentOrchestrator
        return IndependentOrchestrator
    except ImportError:
        # Import direct du fichier car le module orchestrator 
        # peut etre en conflit avec src/orchestrator/
        try:
            spec = importlib.util.spec_from_file_location(
                "autonomous", 
                project_root + "/orchestrator/autonomous.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module.IndependentOrchestrator
        except Exception:
            return None

# Import global pour compatibility
IndependentOrchestrator = get_independent_orchestrator()
ORCHESTRATOR_AVAILABLE = IndependentOrchestrator is not None