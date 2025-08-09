"""
Tests basiques pour AutonomousOrchestrator - Ameliorer couverture 
Tests simples pour faire passer la couverture globale au-dessus de 50%
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
from datetime import datetime

from src.orchestrator.agents.autonomous_orchestrator import AutonomousOrchestrator


class TestAutonomousOrchestratorBasics:
    """Tests basiques pour AutonomousOrchestrator"""
    
    def test_initialization(self):
        """Test l'initialisation de l'orchestrateur"""
        config = {"test": True, "autonomy_threshold": 0.8}
        orchestrator = AutonomousOrchestrator(config)
        
        assert orchestrator.config == config
        assert orchestrator.autonomy_level == 0.0  # Commence bas
        assert orchestrator.agents == {}
        assert orchestrator.task_queue == []
        assert orchestrator.is_running == False
        assert orchestrator.performance_metrics == {}
    
    @pytest.mark.asyncio
    async def test_add_agent(self):
        """Test l'ajout d'agents"""
        config = {}
        orchestrator = AutonomousOrchestrator(config)
        
        await orchestrator.add_agent("test_agent", "bug_detector", {"enabled": True})
        
        assert "test_agent" in orchestrator.agents
        assert orchestrator.agents["test_agent"]["type"] == "bug_detector"
        assert orchestrator.agents["test_agent"]["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_remove_agent(self):
        """Test la suppression d'agents"""
        config = {}
        orchestrator = AutonomousOrchestrator(config)
        
        # Ajouter puis supprimer un agent
        await orchestrator.add_agent("test_agent", "code_generator", {})
        await orchestrator.remove_agent("test_agent")
        
        assert "test_agent" not in orchestrator.agents
    
    @pytest.mark.asyncio
    async def test_add_task(self):
        """Test l'ajout de taches"""
        config = {}
        orchestrator = AutonomousOrchestrator(config)
        
        task = {"id": "task1", "type": "code_generation", "priority": "high"}
        await orchestrator.add_task(task)
        
        assert len(orchestrator.task_queue) == 1
        assert orchestrator.task_queue[0]["id"] == "task1"
    
    @pytest.mark.asyncio
    async def test_process_all_tasks(self):
        """Test le traitement de toutes les taches"""
        config = {}
        orchestrator = AutonomousOrchestrator(config)
        
        # Ajouter quelques taches
        await orchestrator.add_task({"id": "task1", "type": "test"})
        await orchestrator.add_task({"id": "task2", "type": "test"})
        
        result = await orchestrator.process_all_tasks()
        
        assert isinstance(result, dict)
        assert "processed_tasks" in result
    
    def test_get_startup_metrics(self):
        """Test l'obtention des metriques de demarrage"""
        config = {}
        orchestrator = AutonomousOrchestrator(config)
        
        metrics = orchestrator._get_startup_metrics()
        
        assert isinstance(metrics, dict)
        assert "initialization_time" in metrics
        assert "component_count" in metrics
    
    @pytest.mark.asyncio
    async def test_collect_base_metrics(self):
        """Test la collecte des metriques de base"""
        config = {}
        orchestrator = AutonomousOrchestrator(config)
        
        # Ajouter quelques agents et taches pour les metriques
        await orchestrator.add_agent("agent1", "test", {})
        await orchestrator.add_task({"id": "task1", "type": "test"})
        
        metrics = await orchestrator._collect_base_metrics()
        
        assert isinstance(metrics, dict)
        assert "active_agents" in metrics
        assert "pending_tasks" in metrics
        assert metrics["active_agents"] == 1
        assert metrics["pending_tasks"] == 1
    
    @pytest.mark.asyncio
    async def test_calculate_performance_scores(self):
        """Test le calcul des scores de performance"""
        config = {}
        orchestrator = AutonomousOrchestrator(config)
        
        scores = await orchestrator._calculate_performance_scores()
        
        assert isinstance(scores, dict)
        assert "efficiency_score" in scores
        assert "reliability_score" in scores
        assert "autonomy_score" in scores
        assert all(0.0 <= score <= 1.0 for score in scores.values())
    
    @pytest.mark.asyncio
    async def test_optimize_performance(self):
        """Test l'optimisation des performances"""
        config = {}
        orchestrator = AutonomousOrchestrator(config)
        
        # Ajouter des elements pour declencher l'optimisation
        for i in range(12):  # Plus de 10 taches pour declencher l'optimisation
            await orchestrator.add_task({"id": f"task{i}", "type": "test"})
        
        for i in range(7):  # Plus de 5 agents pour declencher l'optimisation
            await orchestrator.add_agent(f"agent{i}", "test", {})
        
        result = await orchestrator._optimize_performance()
        
        assert isinstance(result, dict)
        assert "optimizations_applied" in result
        assert "performance_improvement" in result
        assert len(result["optimizations_applied"]) >= 2  # task_queue_optimization + agent_load_balancing
    
    @pytest.mark.asyncio
    async def test_coordinate_with_agents(self):
        """Test la coordination avec les agents"""
        config = {}
        orchestrator = AutonomousOrchestrator(config)
        
        # Creer des mocks d'agents
        mock_agents = [
            Mock(config={"test": True}),
            Mock(config={"test2": True})
        ]
        mock_agents[0].__class__.__name__ = "TestAgent1"
        mock_agents[1].__class__.__name__ = "TestAgent2"
        
        result = await orchestrator._coordinate_with_agents(mock_agents)
        
        assert isinstance(result, dict)
        assert result["coordination_success"] == True
        assert len(result["coordinated_agents"]) == 2
        assert "TestAgent1" in result["coordinated_agents"]
        assert "TestAgent2" in result["coordinated_agents"]
    
    @pytest.mark.asyncio
    async def test_get_complete_system_status(self):
        """Test l'obtention du statut complet du systeme"""
        config = {}
        orchestrator = AutonomousOrchestrator(config)
        
        # Ajouter quelques elements pour un statut plus riche
        await orchestrator.add_agent("test_agent", "test", {})
        orchestrator.is_running = True
        
        status = await orchestrator._get_complete_system_status()
        
        assert isinstance(status, dict)
        assert status["orchestrator_status"] == "running"
        assert "agents_status" in status
        assert status["agents_status"]["total_agents"] == 1
        assert status["agents_status"]["active_agents"] == 1
        assert "overall_health" in status
        assert "last_updated" in status


class TestAutonomousOrchestratorAdvanced:
    """Tests avances pour les fonctionnalites d'orchestration"""
    
    @pytest.mark.asyncio
    async def test_start_autonomous_operation(self):
        """Test le demarrage d'operations autonomes"""
        config = {"test_mode": True}  # Active le mode test rapide
        orchestrator = AutonomousOrchestrator(config)
        
        # Test simple de demarrage
        orchestrator.is_running = False
        result = await orchestrator.start_autonomous_operation()
        
        assert isinstance(result, dict)
        assert result.get("status") == "started"
    
    @pytest.mark.asyncio
    async def test_stop_autonomous_operation(self):
        """Test l'arret d'operations autonomes"""
        config = {"test_mode": True}  # Active le mode test rapide
        orchestrator = AutonomousOrchestrator(config)
        
        # Test simple d'arret
        orchestrator.is_running = True
        result = await orchestrator.stop_autonomous_operation()
        
        assert isinstance(result, dict)
        assert result.get("status") == "stopped"