"""
Integration Tests for Project & Orchestrator (TDD Integration Layer)
Tests d'intégration entre les services de projet et l'orchestrateur
"""

import pytest
import tempfile
import asyncio
from pathlib import Path
import sys
from unittest.mock import Mock, patch, MagicMock

# Ajouter le path src pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from orchestrator.application.project_service import ProjectApplicationService
try:
    from orchestrator.autonomous import IndependentOrchestrator
except ImportError:
    # Fallback pour les tests
    orchestrator_path = Path(__file__).parent.parent.parent / "orchestrator"
    sys.path.insert(0, str(orchestrator_path))
    from autonomous import IndependentOrchestrator


class TestProjectOrchestratorIntegration:
    """Integration tests between Project services and Orchestrator"""
    
    @patch('orchestrator.agents.autonomous_orchestrator.AutonomousOrchestrator')
    @patch('orchestrator.agents.self_evolution_agent.SelfEvolutionAgent')  
    @patch('orchestrator.agents.github_sync_agent.GitHubSyncAgent')
    def test_orchestrator_should_integrate_with_project_service_successfully(
        self, mock_github, mock_evolution, mock_orchestrator
    ):
        """Test: Orchestrator should integrate with ProjectService correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # GIVEN
            project_dir = Path(temp_dir) / "integration-project"
            project_dir.mkdir()
            
            # WHEN - Create orchestrator with project targeting
            orchestrator = IndependentOrchestrator(target_project="integration-project")
            
            # THEN - Should have project service and correct configuration
            assert orchestrator.project_service is not None
            assert isinstance(orchestrator.project_service, ProjectApplicationService)
            assert orchestrator.target_project == "integration-project"
            assert "target_project" in orchestrator.config
    
    @patch('orchestrator.agents.autonomous_orchestrator.AutonomousOrchestrator')
    @patch('orchestrator.agents.self_evolution_agent.SelfEvolutionAgent')
    @patch('orchestrator.agents.github_sync_agent.GitHubSyncAgent')
    def test_orchestrator_should_generate_project_config_via_service(
        self, mock_github, mock_evolution, mock_orchestrator
    ):
        """Test: Orchestrator should use ProjectService for configuration generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # GIVEN
            project_dir = Path(temp_dir) / "config-test-project"
            project_dir.mkdir()
            
            import os
            old_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                # WHEN
                orchestrator = IndependentOrchestrator(target_project="config-test-project")
                
                # THEN - Configuration should be generated correctly
                config = orchestrator.config
                assert config["target_project"]["name"] == "config-test-project"
                assert config["github"]["repo"] == "config-test-project"
                assert "sandbox_path" in config
                
            finally:
                os.chdir(old_cwd)
    
    def test_project_service_should_handle_path_resolution_across_strategies(self):
        """Test: ProjectService should integrate multiple path resolution strategies"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # GIVEN - Create project in parent directory scenario
            project_dir = Path(temp_dir) / "strategy-test-project"
            project_dir.mkdir()
            
            sub_dir = Path(temp_dir) / "subdir"
            sub_dir.mkdir()
            
            import os
            old_cwd = os.getcwd()
            try:
                os.chdir(str(sub_dir))  # Work from subdirectory
                
                # WHEN
                service = ProjectApplicationService()
                resolved_path = service.resolve_project_path("strategy-test-project")
                
                # THEN - Should find project in parent directory
                assert resolved_path == str(project_dir)
                
            finally:
                os.chdir(old_cwd)
    
    def test_project_service_should_integrate_validation_with_github_service(self):
        """Test: ProjectService should integrate validation with GitHubService"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # GIVEN
            service = ProjectApplicationService()
            
            # WHEN
            validation_result = service.validate_project_configuration(
                "github-integration-project", 
                temp_dir
            )
            
            # THEN - Should include GitHub validation results
            assert validation_result["valid"] is True
            assert "github" in validation_result
            assert validation_result["github"]["owner"] == "AlexisVS"
            assert validation_result["github"]["repo"] == "github-integration-project"
    
    def test_project_service_should_provide_fallback_when_validation_fails(self):
        """Test: ProjectService should provide fallback configuration gracefully"""
        # GIVEN
        service = ProjectApplicationService()
        
        # WHEN - Invalid project (nonexistent path)
        config_dict = service.generate_configuration_dict(
            "nonexistent-project",
            "/completely/invalid/path"
        )
        
        # THEN - Should return fallback configuration
        assert config_dict["target_project"]["name"] == "nonexistent-project"
        assert config_dict["github"]["repo"] == "nonexistent-project"
        assert config_dict["github"]["owner"] == "AlexisVS"


class TestEndToEndIntegration:
    """End-to-end integration tests across all layers"""
    
    def test_complete_project_workflow_should_work_end_to_end(self):
        """Test: Complete project workflow from CLI argument to configuration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # GIVEN - Realistic project structure
            project_dir = Path(temp_dir) / "e2e-project"
            project_dir.mkdir()
            
            # Create some project files to make it realistic
            (project_dir / "README.md").write_text("# E2E Test Project")
            (project_dir / "src").mkdir()
            (project_dir / "tests").mkdir()
            
            import os
            old_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                # WHEN - Full workflow: CLI → Service → Configuration
                service = ProjectApplicationService()
                
                # 1. Path resolution
                resolved_path = service.resolve_project_path("e2e-project")
                assert resolved_path == str(project_dir)
                
                # 2. Validation
                validation = service.validate_project_configuration("e2e-project", resolved_path)
                assert validation["valid"] is True
                
                # 3. Configuration generation
                config = service.generate_configuration_dict("e2e-project")
                
                # THEN - Complete configuration should be correct
                assert config["target_project"]["name"] == "e2e-project"
                assert config["target_project"]["path"] == str(project_dir)
                assert config["github"]["repo"] == "e2e-project"
                assert config["sandbox_path"].endswith("e2e-project_sandbox")
                
            finally:
                os.chdir(old_cwd)


class TestErrorHandlingIntegration:
    """Integration tests for error handling across services"""
    
    def test_orchestrator_should_handle_project_service_errors_gracefully(self):
        """Test: Orchestrator should handle ProjectService errors gracefully"""
        # GIVEN - Mock project service to raise exception
        with patch('orchestrator.application.project_service.ProjectApplicationService') as mock_service:
            mock_service.return_value.generate_configuration_dict.side_effect = Exception("Service error")
            
            # WHEN - Should not crash, should use fallback
            with patch('orchestrator.agents.autonomous_orchestrator.AutonomousOrchestrator'):
                with patch('orchestrator.agents.self_evolution_agent.SelfEvolutionAgent'):
                    with patch('orchestrator.agents.github_sync_agent.GitHubSyncAgent'):
                        orchestrator = IndependentOrchestrator(target_project="error-project")
                        
                        # THEN - Should have fallback configuration
                        assert orchestrator.config is not None
                        # Should have basic fallback values
    
    def test_project_service_should_handle_domain_validation_errors(self):
        """Test: ProjectService should handle domain validation errors"""
        # GIVEN
        service = ProjectApplicationService()
        
        # WHEN - Invalid project name (domain validation error)
        config = service.generate_configuration_dict("invalid@project#name")
        
        # THEN - Should return fallback configuration
        assert config is not None
        assert config["target_project"]["name"] == "invalid@project#name"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])