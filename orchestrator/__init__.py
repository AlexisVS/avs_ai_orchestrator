"""
AI Orchestrator - Core Module

Main orchestration components for AI-powered development workflows.
"""

try:
    from .core import UniversalOrchestrator
except ImportError:
    UniversalOrchestrator = None

try:
    from .github import GitHubTDDOrchestrator
except ImportError:
    GitHubTDDOrchestrator = None

try:
    from .autonomous import IndependentOrchestrator
except ImportError:
    IndependentOrchestrator = None

__version__ = "1.0.0"
__all__ = [
    "UniversalOrchestrator", 
    "GitHubTDDOrchestrator",
    "IndependentOrchestrator"
]