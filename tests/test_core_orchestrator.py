"""
Tests TDD pour le Core Orchestrator
Phase RED : Ces tests doivent échouer initialement
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from orchestrator.core import MainOrchestrator


class TestMainOrchestrator:
    """Tests pour l'orchestrateur principal"""
    
    @pytest.mark.unit
    def test_orchestrator_initialization(self, config_file):
        """Test l'initialisation de l'orchestrateur"""
        # GIVEN un fichier de configuration valide
        # WHEN on crée un orchestrateur
        orchestrator = MainOrchestrator(config_file)
        
        # THEN l'orchestrateur doit être initialisé correctement
        assert orchestrator is not None
        assert orchestrator.config_path == config_file
        assert hasattr(orchestrator, 'universal_orchestrator')
        assert hasattr(orchestrator, 'todo_manager')
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_run_full_workflow_success(self, config_file, mock_ai_client):
        """Test le workflow complet avec succès"""
        # GIVEN un orchestrateur configuré
        with patch('orchestrator.core.main.UniversalOrchestrator') as MockUniversal:
            with patch('orchestrator.core.main.TodoLoopManager') as MockTodo:
                mock_universal = MockUniversal.return_value
                mock_universal.test_ai_connection = AsyncMock(return_value=True)
                mock_universal.load_templates = Mock()
                mock_universal.create_github_repository = AsyncMock(return_value=True)
                mock_universal.create_github_issues = AsyncMock(return_value=[{"id": 1, "title": "Test"}])
                mock_universal.generate_project_structure = AsyncMock()
                mock_universal.run_tests = AsyncMock(return_value=True)
                mock_universal.deploy_project = AsyncMock()
                mock_universal.config = {"project": {"name": "test", "type": "python"}, "github": {"owner": "test", "repo_name": "test"}}
                mock_universal.project_root = "/test/path"
                
                mock_todo = MockTodo.return_value
                mock_todo.sync_with_github_issues = AsyncMock(return_value=[Mock(id=1, title="Test")])
                mock_todo.update_task_status = AsyncMock()
                mock_todo.comment_on_github_issue = AsyncMock()
                mock_todo.generate_progress_report = Mock(return_value="Report")
                mock_todo.get_loop_statistics = Mock(return_value={})
                
                orchestrator = MainOrchestrator(config_file)
                
                # WHEN on exécute le workflow complet
                result = await orchestrator.run_full_workflow()
                
                # THEN le workflow doit se terminer avec succès
                assert result is True
                mock_universal.test_ai_connection.assert_called_once()
                mock_universal.load_templates.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_initialization_phase_failure(self, config_file):
        """Test l'échec de la phase d'initialisation"""
        # GIVEN un orchestrateur avec connexion AI défaillante
        with patch('orchestrator.core.main.UniversalOrchestrator') as MockUniversal:
            mock_universal = MockUniversal.return_value
            mock_universal.test_ai_connection = AsyncMock(return_value=False)
            mock_universal.config = {}
            
            orchestrator = MainOrchestrator(config_file)
            
            # WHEN la phase d'initialisation échoue
            result = await orchestrator._initialization_phase()
            
            # THEN la phase doit retourner False
            assert result is False
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_github_phase_creates_issues(self, config_file):
        """Test la création des issues GitHub"""
        # GIVEN un orchestrateur avec GitHub activé
        with patch('orchestrator.core.main.UniversalOrchestrator') as MockUniversal:
            with patch('orchestrator.core.main.TodoLoopManager') as MockTodo:
                mock_universal = MockUniversal.return_value
                mock_universal.create_github_repository = AsyncMock(return_value=True)
                mock_universal.create_github_issues = AsyncMock(return_value=[
                    {"id": 1, "title": "Issue 1"},
                    {"id": 2, "title": "Issue 2"}
                ])
                mock_universal.config = {}
                
                mock_todo = MockTodo.return_value
                mock_todo.sync_with_github_issues = AsyncMock(return_value=[
                    Mock(id=1, title="Issue 1"),
                    Mock(id=2, title="Issue 2")
                ])
                
                orchestrator = MainOrchestrator(config_file)
                
                # WHEN on exécute la phase GitHub
                tasks = await orchestrator._github_phase()
                
                # THEN des tâches doivent être créées
                assert len(tasks) == 2
                mock_universal.create_github_repository.assert_called_once()
                mock_universal.create_github_issues.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_tdd_red_phase(self, config_file):
        """Test la phase RED du TDD"""
        # GIVEN une tâche à traiter
        task = Mock(id=1, title="Test Task")
        
        with patch('orchestrator.core.main.UniversalOrchestrator') as MockUniversal:
            with patch('orchestrator.core.main.TodoLoopManager') as MockTodo:
                mock_universal = MockUniversal.return_value
                mock_universal.config = {}
                
                mock_todo = MockTodo.return_value
                mock_todo.update_task_status = AsyncMock()
                mock_todo.comment_on_github_issue = AsyncMock()
                
                orchestrator = MainOrchestrator(config_file)
                
                # WHEN on exécute la phase RED
                await orchestrator._tdd_red_phase(task)
                
                # THEN le statut doit être mis à jour
                mock_todo.update_task_status.assert_called()
                mock_todo.comment_on_github_issue.assert_called()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_tdd_green_phase(self, config_file):
        """Test la phase GREEN du TDD"""
        # GIVEN une tâche avec tests écrits
        task = Mock(id=1, title="Test Task")
        
        with patch('orchestrator.core.main.UniversalOrchestrator') as MockUniversal:
            with patch('orchestrator.core.main.TodoLoopManager') as MockTodo:
                mock_universal = MockUniversal.return_value
                mock_universal.config = {}
                
                mock_todo = MockTodo.return_value
                mock_todo.update_task_status = AsyncMock()
                mock_todo.comment_on_github_issue = AsyncMock()
                
                orchestrator = MainOrchestrator(config_file)
                
                # WHEN on exécute la phase GREEN
                await orchestrator._tdd_green_phase(task)
                
                # THEN le code minimal doit être généré
                mock_todo.update_task_status.assert_called()
                mock_todo.comment_on_github_issue.assert_called()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_tdd_refactor_phase(self, config_file):
        """Test la phase REFACTOR du TDD"""
        # GIVEN une tâche avec code minimal
        task = Mock(id=1, title="Test Task")
        
        with patch('orchestrator.core.main.UniversalOrchestrator') as MockUniversal:
            with patch('orchestrator.core.main.TodoLoopManager') as MockTodo:
                mock_universal = MockUniversal.return_value
                mock_universal.config = {}
                
                mock_todo = MockTodo.return_value
                mock_todo.update_task_status = AsyncMock()
                mock_todo.comment_on_github_issue = AsyncMock()
                
                orchestrator = MainOrchestrator(config_file)
                
                # WHEN on exécute la phase REFACTOR
                await orchestrator._tdd_refactor_phase(task)
                
                # THEN le code doit être refactorisé
                mock_todo.update_task_status.assert_called()
                mock_todo.comment_on_github_issue.assert_called()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_tdd_cycle(self, config_file):
        """Test le cycle TDD complet pour une tâche"""
        # GIVEN une liste de tâches
        tasks = [
            Mock(id=1, title="Task 1"),
            Mock(id=2, title="Task 2")
        ]
        
        with patch('orchestrator.core.main.UniversalOrchestrator') as MockUniversal:
            with patch('orchestrator.core.main.TodoLoopManager') as MockTodo:
                mock_universal = MockUniversal.return_value
                mock_universal.config = {}
                
                mock_todo = MockTodo.return_value
                mock_todo.update_task_status = AsyncMock()
                mock_todo.comment_on_github_issue = AsyncMock()
                
                orchestrator = MainOrchestrator(config_file)
                
                # WHEN on exécute le cycle TDD complet
                result = await orchestrator._tdd_phase(tasks)
                
                # THEN toutes les phases doivent être exécutées
                assert result is True
                # 3 phases × 2 tâches = 6 appels minimum
                assert mock_todo.update_task_status.call_count >= 6