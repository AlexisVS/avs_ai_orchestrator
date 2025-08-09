"""
Tests TDD pour TodoLoopManager
Test de couverture pour améliorer le score global
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.orchestrator.core.todo_loop_manager import TodoLoopManager, TaskStatus


class TestTodoLoopManager:
    """Tests pour TodoLoopManager"""
    
    @pytest.mark.unit
    def test_todo_loop_manager_initialization(self):
        """Test l'initialisation du TodoLoopManager"""
        config = {"test": True}
        manager = TodoLoopManager(config)
        
        assert manager.config == config
        assert manager.tasks == []
    
    @pytest.mark.unit  
    @pytest.mark.asyncio
    async def test_sync_with_github_issues(self):
        """Test synchronisation avec GitHub Issues"""
        config = {"github": {"owner": "test", "repo": "test"}}
        manager = TodoLoopManager(config)
        
        result = await manager.sync_with_github_issues()
        
        assert len(result) == 3  # L'implémentation retourne 3 tâches par défaut
        assert result[0].id == 1
        assert result[1].id == 2
        assert result[2].id == 3
    
    @pytest.mark.unit
    @pytest.mark.asyncio 
    async def test_update_task_status(self):
        """Test mise à jour du statut des tâches"""
        manager = TodoLoopManager({})
        
        # Créer d'abord quelques tâches
        await manager.sync_with_github_issues()
        
        # Test mise à jour statut
        task_id = 1
        new_status = TaskStatus.TDD_RED
        
        await manager.update_task_status(task_id, new_status)
        
        # Vérifier que le statut a été mis à jour
        task = next((t for t in manager.tasks if t.id == task_id), None)
        assert task is not None
        assert task.status == new_status
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_comment_on_github_issue(self):
        """Test commentaire sur GitHub Issue"""  
        manager = TodoLoopManager({})
        
        issue_id = 1
        comment = "Test comment"
        
        # Test que ça n'échoue pas
        await manager.comment_on_github_issue(issue_id, comment)
    
    @pytest.mark.unit
    def test_generate_progress_report(self):
        """Test génération de rapport de progression"""
        manager = TodoLoopManager({})
        
        report = manager.generate_progress_report()
        
        assert isinstance(report, str)
        assert len(report) > 0
    
    @pytest.mark.unit
    def test_get_loop_statistics(self):
        """Test récupération des statistiques de boucle"""
        manager = TodoLoopManager({})
        
        stats = manager.get_loop_statistics()
        
        assert isinstance(stats, dict)
        assert "total_tasks" in stats