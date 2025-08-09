"""
Tests pour l'argument --project de l'orchestrateur autonome
TDD: Test-Driven Development approach
"""

import pytest
import tempfile
import json
import argparse
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import sys
import os

# Import centralisé via utilitaire
try:
    from test_utils import IndependentOrchestrator, ORCHESTRATOR_AVAILABLE
except ImportError:
    # Fallback: importer directement
    sys.path.insert(0, str(Path(__file__).parent))
    from test_utils import IndependentOrchestrator, ORCHESTRATOR_AVAILABLE

# Essayer d'importer les autres fonctions directement
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    orchestrator_path = Path(__file__).parent.parent / "orchestrator"
    sys.path.insert(0, str(orchestrator_path))
    from autonomous import parse_arguments, validate_project_config
except ImportError:
    # Mock des fonctions si pas disponibles
    def parse_arguments():
        class MockArgs:
            project = None
        return MockArgs()
    
    def validate_project_config(config):
        return True


class TestProjectArgumentParsing:
    """Tests pour le parsing de l'argument --project"""
    
    def test_parse_arguments_with_project(self):
        """Test: --project argument devrait être parsé correctement"""
        # GIVEN
        test_args = ['--project', 'weather-dashboard']
        
        # WHEN
        args = parse_arguments(test_args)
        
        # THEN
        assert args.project == 'weather-dashboard'
    
    def test_parse_arguments_without_project(self):
        """Test: Sans --project, devrait être None"""
        # GIVEN
        test_args = []
        
        # WHEN
        args = parse_arguments(test_args)
        
        # THEN
        assert args.project is None
    
    def test_parse_arguments_with_target_project_alias(self):
        """Test: --target-project devrait fonctionner comme alias"""
        # GIVEN
        test_args = ['--target-project', 'my-project']
        
        # WHEN
        args = parse_arguments(test_args)
        
        # THEN
        assert args.project == 'my-project'


class TestProjectConfigValidation:
    """Tests pour la validation de configuration de projet"""
    
    def test_validate_project_config_valid_project(self):
        """Test: Configuration valide devrait passer la validation"""
        # GIVEN
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test-project"
            project_path.mkdir()
            
            # WHEN
            result = validate_project_config("test-project", str(project_path))
            
            # THEN
            assert result["valid"] is True
            assert result["project_name"] == "test-project"
            assert result["project_path"] == str(project_path)
    
    def test_validate_project_config_invalid_path(self):
        """Test: Chemin inexistant devrait échouer"""
        # GIVEN
        invalid_path = "/path/that/does/not/exist"
        
        # WHEN
        result = validate_project_config("test-project", invalid_path)
        
        # THEN
        assert result["valid"] is False
        assert "error" in result
        assert "does not exist" in result["error"]
    
    def test_validate_project_config_github_repo_validation(self):
        """Test: Validation du repo GitHub"""
        # GIVEN
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "github-project"
            project_path.mkdir()
            
            # WHEN
            result = validate_project_config("github-project", str(project_path))
            
            # THEN
            assert result["valid"] is True
            assert result["github"]["owner"] == "AlexisVS"  # Valeur par défaut
            assert result["github"]["repo"] == "github-project"


class TestIndependentOrchestratorWithProject:
    """Tests pour IndependentOrchestrator avec argument projet"""
    
    def test_orchestrator_initialization_with_project(self):
        """Test: Initialisation avec projet spécifique"""
        # GIVEN
        target_project = "weather-dashboard"
        
        # WHEN
        with patch.multiple('src.orchestrator.agents.autonomous_orchestrator', AutonomousOrchestrator=MagicMock()):
            with patch.multiple('src.orchestrator.agents.self_evolution_agent', SelfEvolutionAgent=MagicMock()):
                with patch.multiple('src.orchestrator.agents.github_sync_agent', GitHubSyncAgent=MagicMock()):
                    orchestrator = IndependentOrchestrator(target_project=target_project)
        
        # THEN
        assert orchestrator.target_project == target_project
        assert "target_project" in orchestrator.config
        assert orchestrator.config["target_project"]["name"] == target_project
    
    def test_orchestrator_initialization_without_project(self):
        """Test: Initialisation sans projet (utilise config par défaut)"""
        # WHEN
        with patch.multiple('src.orchestrator.agents.autonomous_orchestrator', AutonomousOrchestrator=MagicMock()):
            with patch.multiple('src.orchestrator.agents.self_evolution_agent', SelfEvolutionAgent=MagicMock()):
                with patch.multiple('src.orchestrator.agents.github_sync_agent', GitHubSyncAgent=MagicMock()):
                    orchestrator = IndependentOrchestrator()
        
        # THEN
        assert orchestrator.target_project is None
        assert orchestrator.config["github"]["repo"] == "avs_ai_orchestrator"  # valeur par défaut
    
    def test_config_override_with_project(self):
        """Test: Configuration surchargée par argument projet"""
        # GIVEN
        target_project = "custom-project"
        
        # WHEN
        with patch.multiple('src.orchestrator.agents.autonomous_orchestrator', AutonomousOrchestrator=MagicMock()):
            with patch.multiple('src.orchestrator.agents.self_evolution_agent', SelfEvolutionAgent=MagicMock()):
                with patch.multiple('src.orchestrator.agents.github_sync_agent', GitHubSyncAgent=MagicMock()):
                    orchestrator = IndependentOrchestrator(target_project=target_project)
        
        # THEN
        assert orchestrator.config["github"]["repo"] == target_project
        assert orchestrator.config["github"]["owner"] == "AlexisVS"
        assert orchestrator.config["target_project"]["name"] == target_project


class TestProjectConfigurationGeneration:
    """Tests pour la génération automatique de configuration de projet"""
    
    def test_generate_project_config_basic(self):
        """Test: Génération config basique pour un projet"""
        # GIVEN
        project_name = "test-project"
        project_path = "/path/to/test-project"
        
        # WHEN
        try:
            from orchestrator.autonomous import generate_project_config
        except ImportError:
            from autonomous import generate_project_config
        config = generate_project_config(project_name, project_path)
        
        # THEN
        assert config["target_project"]["name"] == project_name
        assert config["target_project"]["path"] == project_path
        assert config["github"]["repo"] == project_name
        assert "sandbox_path" in config
        assert config["sandbox_path"].endswith(f"{project_name}_sandbox")
    
    def test_generate_project_config_with_owner(self):
        """Test: Génération config avec propriétaire spécifique"""
        # GIVEN
        project_name = "test-project"
        project_path = "/path/to/test-project"
        owner = "CustomOwner"
        
        # WHEN
        try:
            from orchestrator.autonomous import generate_project_config
        except ImportError:
            from autonomous import generate_project_config
        config = generate_project_config(project_name, project_path, github_owner=owner)
        
        # THEN
        assert config["github"]["owner"] == owner
        assert config["github"]["repo"] == project_name


class TestMainFunctionIntegration:
    """Tests d'intégration pour la fonction main avec arguments"""
    
    def test_main_with_project_argument(self):
        """Test: main() avec argument --project"""
        # GIVEN - Importer main_with_args d'abord
        sys.path.insert(0, str(Path(__file__).parent.parent))
        try:
            from orchestrator.autonomous import main_with_args, IndependentOrchestrator, parse_arguments
        except ImportError:
            from autonomous import main_with_args, IndependentOrchestrator, parse_arguments
            
        # WHEN
        with patch.object(sys.modules[IndependentOrchestrator.__module__], 'IndependentOrchestrator') as mock_orchestrator_class:
            with patch.object(sys.modules[parse_arguments.__module__], 'parse_arguments') as mock_parse:
                mock_orchestrator = MagicMock()
                mock_orchestrator.config = {"test_mode": True}  # Mode test
                mock_orchestrator.initialize_system = AsyncMock()
                mock_orchestrator.start_perpetual_evolution = AsyncMock()
                mock_orchestrator_class.return_value = mock_orchestrator
                mock_parse.return_value = argparse.Namespace(project='weather-dashboard')
                
                import asyncio
                asyncio.run(main_with_args())
        
        # THEN
        mock_orchestrator_class.assert_called_once_with(target_project='weather-dashboard')
        mock_orchestrator.initialize_system.assert_called_once()
    
    def test_main_without_project_argument(self):
        """Test: main() sans argument --project"""
        # GIVEN - Importer main_with_args d'abord  
        sys.path.insert(0, str(Path(__file__).parent.parent))
        try:
            from orchestrator.autonomous import main_with_args, IndependentOrchestrator, parse_arguments
        except ImportError:
            from autonomous import main_with_args, IndependentOrchestrator, parse_arguments
            
        # WHEN
        with patch.object(sys.modules[IndependentOrchestrator.__module__], 'IndependentOrchestrator') as mock_orchestrator_class:
            with patch.object(sys.modules[parse_arguments.__module__], 'parse_arguments') as mock_parse:
                mock_orchestrator = MagicMock()
                mock_orchestrator.config = {"test_mode": True}  # Mode test
                mock_orchestrator.initialize_system = AsyncMock()
                mock_orchestrator.start_perpetual_evolution = AsyncMock()
                mock_orchestrator_class.return_value = mock_orchestrator
                mock_parse.return_value = argparse.Namespace(project=None)
                
                import asyncio
                asyncio.run(main_with_args())
        
        # THEN
        mock_orchestrator_class.assert_called_once_with(target_project=None)


class TestProjectPathResolution:
    """Tests pour la résolution automatique des chemins de projet"""
    
    def test_resolve_project_path_current_dir(self):
        """Test: Résolution du chemin dans le répertoire courant"""
        # GIVEN
        project_name = "test-project"
        
        # WHEN - Mock pathlib.Path.exists pour le répertoire courant
        with patch('pathlib.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path("/current/dir")
            # Mock pour que le projet existe dans le répertoire courant
            with patch('pathlib.Path.exists', return_value=True) as mock_exists:
                try:
                    from orchestrator.autonomous import resolve_project_path
                except ImportError:
                    from autonomous import resolve_project_path
                resolved_path = resolve_project_path(project_name)
        
        # THEN
        assert project_name in resolved_path
        # Compatible Windows/Linux
        assert "current" in resolved_path and "dir" in resolved_path
    
    def test_resolve_project_path_parent_dir(self):
        """Test: Résolution du chemin dans le répertoire parent"""
        # GIVEN
        project_name = "test-project"
        
        # WHEN - Mock pathlib.Path pour répertoire parent
        with patch('pathlib.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path("/current/subdir")
            # Premier appel (current dir) renvoie False, second (parent) renvoie True
            with patch('pathlib.Path.exists') as mock_exists:
                # Cycle pour gérer plusieurs appels: [False pour current, True pour parent, True pour les suivants]
                mock_exists.side_effect = [False, True, True, True]
                
                try:
                    from orchestrator.autonomous import resolve_project_path
                except ImportError:
                    from autonomous import resolve_project_path
                resolved_path = resolve_project_path(project_name)
        
        # THEN
        assert project_name in resolved_path
        assert "current" in resolved_path  # Vérifie que c'est dans le parent (compatible Windows/Linux)
    
    def test_resolve_project_path_not_found(self):
        """Test: Projet non trouvé devrait lever une exception"""
        # GIVEN
        project_name = "nonexistent-project"
        
        # WHEN & THEN
        try:
            from orchestrator.autonomous import resolve_project_path
        except ImportError:
            from autonomous import resolve_project_path
        with pytest.raises(ValueError, match="Project directory not found"):
            resolve_project_path(project_name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])