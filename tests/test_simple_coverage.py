"""
Tests simples pour améliorer rapidement la couverture de code
"""

import pytest
from src.orchestrator.core.todo_loop_manager import TodoLoopManager, TaskStatus, Task
from src.orchestrator.mcp.mcp_load_balancer import MCPLoadBalancer


class TestSimpleCoverage:
    """Tests simples pour améliorer la couverture"""
    
    def test_task_creation(self):
        """Test création d'une tâche"""
        task = Task(1, "Test task")
        assert task.id == 1
        assert task.title == "Test task"
        assert task.status == TaskStatus.PENDING
    
    def test_task_status_enum(self):
        """Test enum TaskStatus"""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.TDD_RED.value == "tdd_red"
        assert TaskStatus.TDD_GREEN.value == "tdd_green"
        assert TaskStatus.TDD_REFACTOR.value == "tdd_refactor"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.BLOCKED.value == "blocked"
    
    def test_mcp_load_balancer_basic(self):
        """Test MCPLoadBalancer de base"""
        balancer = MCPLoadBalancer()
        
        # Test ajout serveur
        server = {"host": "localhost", "port": 8080}
        balancer.add_server(server)
        
        assert len(balancer.servers) == 1
        assert balancer.current_index == 0
        
        # Test avec deuxième serveur
        server2 = {"host": "localhost", "port": 8081}
        balancer.add_server(server2)
        
        assert len(balancer.servers) == 2
    
    def test_todo_manager_stats(self):
        """Test statistiques TodoLoopManager"""
        manager = TodoLoopManager({})
        
        # Test stats vides
        stats = manager.get_loop_statistics()
        assert stats["total_tasks"] == 0
        assert stats["completed"] == 0
        assert stats["in_progress"] == 0
        
        # Test rapport vide
        report = manager.generate_progress_report()
        assert "0/0" in report
    
    @pytest.mark.asyncio
    async def test_todo_manager_simple_flow(self):
        """Test flux simple TodoLoopManager"""
        manager = TodoLoopManager({})
        
        # Sync pour créer des tâches
        tasks = await manager.sync_with_github_issues()
        assert len(tasks) == 3
        
        # Vérifier que les tâches sont dans manager
        assert len(manager.tasks) == 3
        
        # Test stats après création
        stats = manager.get_loop_statistics()
        assert stats["total_tasks"] == 3
        assert stats["completed"] == 0
        
        # Test mise à jour statut
        await manager.update_task_status(1, TaskStatus.COMPLETED)
        
        # Vérifier la mise à jour
        updated_stats = manager.get_loop_statistics()
        assert updated_stats["completed"] == 1
        
        # Test commentaire
        await manager.comment_on_github_issue(1, "Test comment")
        
        # Test rapport final
        final_report = manager.generate_progress_report()
        assert "1/3" in final_report