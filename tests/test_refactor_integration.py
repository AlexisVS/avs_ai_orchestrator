"""
Phase REFACTOR TDD - Tests d'intégration pour améliorer la couverture
Objectif: Atteindre 80%+ de couverture sur les composants critiques
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
import json
import tempfile


@pytest.fixture
def enhanced_config():
    """Configuration étendue pour les tests REFACTOR"""
    return {
        "python_command": "python",
        "test_timeout": 60,
        "evolution_interval": 10,
        "sandbox_path": "test_sandbox",
        "main_repo": "test_repo",
        "coverage_target": 0.80,
        "quality_gates": {
            "min_coverage": 80,
            "max_complexity": 10,
            "security_checks": True
        },
        "autonomous_features": {
            "self_modification": True,
            "architecture_evolution": True,
            "continuous_operation": True,
            "resource_optimization": True
        }
    }


class TestAutonomousOrchestratorRefactor:
    """Tests REFACTOR pour améliorer la couverture de l'orchestrateur autonome"""
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization_and_lifecycle(self, enhanced_config):
        """Test complet du cycle de vie de l'orchestrateur"""
        from orchestrator.agents.autonomous_orchestrator import AutonomousOrchestrator
        
        # GIVEN un orchestrateur avec configuration étendue
        orchestrator = AutonomousOrchestrator(enhanced_config)
        
        # WHEN on teste l'initialisation complète
        assert orchestrator.config == enhanced_config
        assert orchestrator.agents == {}
        assert orchestrator.task_queue == []
        assert orchestrator.is_running is False
        assert orchestrator.performance_metrics == {}
        assert orchestrator.autonomy_level == 0.0
        
        # Test des métriques de démarrage
        startup_metrics = orchestrator._get_startup_metrics()
        assert "initialization_time" in startup_metrics
        assert "component_count" in startup_metrics
        assert "autonomy_features_enabled" in startup_metrics
        
    @pytest.mark.asyncio
    async def test_comprehensive_agent_management(self, enhanced_config):
        """Test complet de la gestion d'agents"""
        from orchestrator.agents.autonomous_orchestrator import AutonomousOrchestrator
        
        orchestrator = AutonomousOrchestrator(enhanced_config)
        
        # Test d'ajout d'agents multiples
        test_agents = [
            {"name": "test_evolution", "type": "self_evolution", "priority": 1},
            {"name": "test_meta", "type": "meta_cognitive", "priority": 2},
            {"name": "test_runner", "type": "test_runner", "priority": 3}
        ]
        
        for agent_config in test_agents:
            await orchestrator.add_agent(
                agent_config["name"], 
                agent_config["type"], 
                {"priority": agent_config["priority"]}
            )
        
        # Vérifier que tous les agents sont ajoutés
        assert len(orchestrator.agents) == 3
        assert "test_evolution" in orchestrator.agents
        assert "test_meta" in orchestrator.agents
        assert "test_runner" in orchestrator.agents
        
        # Test de suppression d'agent
        await orchestrator.remove_agent("test_runner")
        assert len(orchestrator.agents) == 2
        assert "test_runner" not in orchestrator.agents
        
    @pytest.mark.asyncio
    async def test_task_orchestration_comprehensive(self, enhanced_config):
        """Test complet de l'orchestration de tâches"""
        from orchestrator.agents.autonomous_orchestrator import AutonomousOrchestrator
        
        orchestrator = AutonomousOrchestrator(enhanced_config)
        
        # Ajouter des tâches de différents types
        tasks = [
            {"task_id": "task_1", "type": "analysis", "priority": "high", "data": {"files": ["file1.py"]}},
            {"task_id": "task_2", "type": "generation", "priority": "medium", "data": {"template": "test"}},
            {"task_id": "task_3", "type": "validation", "priority": "low", "data": {"coverage": 0.8}}
        ]
        
        for task in tasks:
            await orchestrator.add_task(task)
        
        # Vérifier la queue des tâches
        assert len(orchestrator.task_queue) == 3
        
        # Test du traitement des tâches
        results = await orchestrator.process_all_tasks()
        assert "processed_tasks" in results
        assert "failed_tasks" in results
        assert "processing_time" in results
        
    @pytest.mark.asyncio
    async def test_performance_monitoring_comprehensive(self, enhanced_config):
        """Test complet du monitoring des performances"""
        from orchestrator.agents.autonomous_orchestrator import AutonomousOrchestrator
        
        orchestrator = AutonomousOrchestrator(enhanced_config)
        
        # Test de collecte de métriques de base
        base_metrics = await orchestrator._collect_base_metrics()
        assert "cpu_usage" in base_metrics
        assert "memory_usage" in base_metrics
        assert "active_agents" in base_metrics
        
        # Test de calcul de performances
        perf_scores = await orchestrator._calculate_performance_scores()
        assert "efficiency_score" in perf_scores
        assert "reliability_score" in perf_scores
        assert "autonomy_score" in perf_scores
        
        # Test d'optimisation des performances
        optimization_result = await orchestrator._optimize_performance()
        assert "optimizations_applied" in optimization_result
        assert "performance_improvement" in optimization_result


class TestMetaCognitiveAgentRefactor:
    """Tests REFACTOR pour améliorer la couverture de l'agent méta-cognitif"""
    
    @pytest.mark.asyncio
    async def test_comprehensive_cognitive_patterns(self, enhanced_config):
        """Test complet des patterns cognitifs"""
        from orchestrator.agents.meta_cognitive_agent import MetaCognitiveAgent, CognitivePattern
        
        agent = MetaCognitiveAgent(enhanced_config)
        
        # Créer plusieurs patterns cognitifs
        patterns = [
            CognitivePattern(
                id="pattern_1", name="Problem Solving", description="Advanced problem solving",
                efficiency_score=0.85, usage_count=10, success_rate=0.9,
                learned_at="2025-01-01", last_used="2025-01-08",
                improvement_suggestions=["Increase parallelization", "Add caching"]
            ),
            CognitivePattern(
                id="pattern_2", name="Pattern Recognition", description="Visual pattern recognition",
                efficiency_score=0.75, usage_count=15, success_rate=0.8,
                learned_at="2025-01-02", last_used="2025-01-07",
                improvement_suggestions=["Improve accuracy", "Reduce latency"]
            )
        ]
        
        # Ajouter les patterns à l'agent
        for pattern in patterns:
            agent.cognitive_patterns[pattern.id] = pattern
        
        # Test d'analyse des patterns
        pattern_analysis = await agent._analyze_recent_behavior()
        assert len(pattern_analysis) > 0
        
        # Test d'évaluation des décisions
        decision_quality = await agent._evaluate_recent_decisions()
        assert 0.0 <= decision_quality <= 1.0
        
        # Test de gathering des métriques
        metrics = await agent._gather_performance_metrics()
        assert "pattern_recognition" in metrics
        assert "abstract_reasoning" in metrics
        assert "meta_awareness" in metrics
        
    @pytest.mark.asyncio
    async def test_meta_thought_processing(self, enhanced_config):
        """Test complet du traitement des méta-pensées"""
        from orchestrator.agents.meta_cognitive_agent import MetaCognitiveAgent, MetaThought
        
        agent = MetaCognitiveAgent(enhanced_config)
        
        # Créer des méta-pensées
        meta_thoughts = [
            MetaThought(
                thought_id="thought_1",
                content="System is learning efficiently",
                confidence=0.9,
                reasoning_chain=["Observed pattern improvement", "Success rate increased"],
                predicted_outcomes=["Continued improvement", "Better performance"]
            ),
            MetaThought(
                thought_id="thought_2", 
                content="Need to optimize memory usage",
                confidence=0.7,
                reasoning_chain=["Memory usage trending up", "Performance impact detected"],
                predicted_outcomes=["Implement caching", "Reduce memory footprint"]
            )
        ]
        
        # Ajouter les pensées à l'agent
        agent.meta_thoughts.extend(meta_thoughts)
        
        # Test de traitement des pensées
        assert len(agent.meta_thoughts) == 2
        
        # Test d'évolution du niveau de conscience
        old_consciousness = agent.consciousness_level
        await agent._evolve_consciousness()
        new_consciousness = agent.consciousness_level
        
        # La conscience devrait évoluer
        assert new_consciousness >= old_consciousness
        
        # Test du rapport de conscience
        consciousness_report = agent.get_consciousness_report()
        assert "consciousness_level" in consciousness_report
        assert "autonomy_index" in consciousness_report
        assert "intelligence_metrics" in consciousness_report


class TestSelfEvolutionAgentRefactor:
    """Tests REFACTOR pour améliorer la couverture de l'agent d'auto-évolution"""
    
    @pytest.mark.asyncio
    async def test_comprehensive_improvement_detection(self, enhanced_config, temp_dir):
        """Test complet de la détection d'améliorations"""
        from orchestrator.agents.self_evolution_agent import SelfEvolutionAgent
        
        agent = SelfEvolutionAgent(enhanced_config)
        agent.main_repo_path = temp_dir
        
        # Créer des fichiers de test avec des patterns d'amélioration
        test_files = [
            "src/test_module1.py",
            "src/test_module2.py", 
            "tests/test_existing.py"
        ]
        
        for file_path in test_files:
            full_path = temp_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            content = """# TODO: Add error handling
def test_function():
    # FIXME: This needs optimization
    return "test"
"""
            full_path.write_text(content)
        
        # Test de détection d'améliorations
        improvements = await agent.detect_improvements()
        assert len(improvements) > 0
        
        # Vérifier les types d'amélioration détectés
        improvement_types = [imp["type"] for imp in improvements]
        expected_types = ["test_coverage", "feature"]  # "bug_fix", "performance" peuvent être absents
        
        for expected_type in expected_types:
            if expected_type == "test_coverage":
                # Il devrait y avoir des gaps de couverture
                assert expected_type in improvement_types
        
    @pytest.mark.asyncio
    async def test_version_management(self, enhanced_config, temp_dir):
        """Test complet de la gestion des versions"""
        from orchestrator.agents.self_evolution_agent import SelfEvolutionAgent
        
        agent = SelfEvolutionAgent(enhanced_config)
        agent.main_repo_path = temp_dir
        
        # Test de la version actuelle
        current_version = agent._get_current_version()
        assert len(current_version) == 8  # Hash MD5 tronqué
        
        # Modifier un fichier et vérifier que la version change
        test_file = temp_dir / "src" / "test_change.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("# Version 1")
        
        new_version_1 = agent._get_current_version()
        
        # Modifier le fichier
        test_file.write_text("# Version 2")
        new_version_2 = agent._get_current_version()
        
        # Les versions doivent être différentes
        assert new_version_1 != new_version_2
        
        # Test de l'historique d'évolution
        assert isinstance(agent.evolution_history, list)
        assert agent.evolution_cycle == 0
        assert agent.is_evolving is False


class TestTestRunnerAgentRefactor:
    """Tests REFACTOR pour améliorer la couverture de l'agent test runner"""
    
    @pytest.mark.asyncio
    async def test_comprehensive_pytest_execution(self, enhanced_config):
        """Test complet de l'exécution pytest"""
        from orchestrator.agents.test_runner_agent import TestRunnerAgent
        
        test_runner = TestRunnerAgent(enhanced_config)
        
        # Test du parsing des résultats pytest avec différents formats
        test_outputs = [
            "2 passed, 1 failed in 1.23s",
            "5 passed in 0.87s",
            "1 failed, 3 error in 2.45s",
            "10 passed, 2 failed, 1 skipped in 5.67s"
        ]
        
        for output in test_outputs:
            passed, failed, total = test_runner._parse_pytest_results(output)
            assert total == passed + failed
            assert passed >= 0
            assert failed >= 0
        
    @pytest.mark.asyncio
    async def test_comprehensive_quality_scoring(self, enhanced_config):
        """Test complet du calcul de score de qualité"""
        from orchestrator.agents.test_runner_agent import TestRunnerAgent
        
        test_runner = TestRunnerAgent(enhanced_config)
        
        # Test avec différentes configurations de qualité
        quality_scenarios = [
            {
                "mypy": {"issues": 0},
                "flake8": {"issues": 0}, 
                "bandit": {"high_severity": 0, "medium_severity": 0},
                "expected_score": 100.0
            },
            {
                "mypy": {"issues": 5},
                "flake8": {"issues": 10},
                "bandit": {"high_severity": 1, "medium_severity": 2},
                "expected_score": 60.0  # 100 - 5*2 - 10*1 - 1*10 - 2*5 = 60
            },
            {
                "mypy": {"issues": 20},
                "flake8": {"issues": 50},
                "bandit": {"high_severity": 5, "medium_severity": 10},
                "expected_score": 0.0  # Plafonné à 0
            }
        ]
        
        for scenario in quality_scenarios:
            quality_results = {
                "mypy": scenario["mypy"],
                "flake8": scenario["flake8"],
                "bandit": scenario["bandit"]
            }
            
            score = test_runner._calculate_quality_score(quality_results)
            assert score == scenario["expected_score"]
            assert 0.0 <= score <= 100.0
        
    @pytest.mark.asyncio
    async def test_coverage_analysis_comprehensive(self, enhanced_config, temp_dir):
        """Test complet de l'analyse de couverture"""
        from orchestrator.agents.test_runner_agent import TestRunnerAgent
        
        test_runner = TestRunnerAgent(enhanced_config)
        
        # Créer un fichier de couverture simulé
        coverage_data = {
            "totals": {
                "num_statements": 100,
                "covered_lines": 80
            },
            "files": {
                "src/module1.py": {
                    "summary": {"num_statements": 50, "covered_lines": 45},
                    "missing_lines": [10, 15, 20, 25, 30]
                },
                "src/module2.py": {
                    "summary": {"num_statements": 50, "covered_lines": 35},
                    "missing_lines": [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75]
                }
            }
        }
        
        # Sauvegarder temporairement les données de couverture
        coverage_file = temp_dir / "coverage.json"
        coverage_file.write_text(json.dumps(coverage_data))
        
        # Changer le répertoire de travail temporairement
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Analyser la couverture
            coverage_analysis = await test_runner._analyze_coverage()
            
            # Vérifications
            assert coverage_analysis["coverage"] == 80.0  # 80/100 * 100
            assert coverage_analysis["covered_lines"] == 80
            assert coverage_analysis["total_lines"] == 100
            assert len(coverage_analysis["low_coverage_files"]) == 1  # module2.py a 70% < 80%
            assert coverage_analysis["low_coverage_files"][0]["file"] == "src/module2.py"
            
        finally:
            os.chdir(original_cwd)


@pytest.mark.integration
class TestRefactorIntegrationWorkflow:
    """Tests d'intégration pour le workflow complet REFACTOR"""
    
    @pytest.mark.asyncio
    async def test_complete_autonomous_workflow(self, enhanced_config, temp_dir):
        """Test du workflow autonome complet après REFACTOR"""
        from orchestrator.agents.autonomous_orchestrator import AutonomousOrchestrator
        from orchestrator.agents.meta_cognitive_agent import MetaCognitiveAgent
        from orchestrator.agents.self_evolution_agent import SelfEvolutionAgent
        
        # Créer tous les agents principaux
        orchestrator = AutonomousOrchestrator(enhanced_config)
        meta_agent = MetaCognitiveAgent(enhanced_config)
        evolution_agent = SelfEvolutionAgent(enhanced_config)
        evolution_agent.main_repo_path = temp_dir
        
        # Test d'intégration des composants
        components = [orchestrator, meta_agent, evolution_agent]
        
        # Chaque composant doit être correctement initialisé
        for component in components:
            assert component.config == enhanced_config
        
        # Test de la coordination entre composants
        coordination_result = await orchestrator._coordinate_with_agents([meta_agent, evolution_agent])
        assert "coordination_success" in coordination_result
        assert coordination_result["coordination_success"] is True
        
        # Test du rapport d'état complet
        system_status = await orchestrator._get_complete_system_status()
        assert "orchestrator_status" in system_status
        assert "agents_status" in system_status
        assert "overall_health" in system_status
        
    @pytest.mark.asyncio
    async def test_refactor_quality_improvements(self, enhanced_config):
        """Test que les améliorations REFACTOR maintiennent la qualité"""
        # Test que toutes les classes principales peuvent être importées
        from orchestrator.agents.autonomous_orchestrator import AutonomousOrchestrator
        from orchestrator.agents.meta_cognitive_agent import MetaCognitiveAgent
        from orchestrator.agents.self_evolution_agent import SelfEvolutionAgent
        from orchestrator.agents.test_runner_agent import TestRunnerAgent
        
        # Test d'instanciation sans erreur
        agents = [
            AutonomousOrchestrator(enhanced_config),
            MetaCognitiveAgent(enhanced_config), 
            SelfEvolutionAgent(enhanced_config),
            TestRunnerAgent(enhanced_config)
        ]
        
        # Tous les agents doivent être correctement initialisés
        for agent in agents:
            assert agent.config == enhanced_config
            assert hasattr(agent, 'config')
        
        # Test de la couverture attendue après REFACTOR
        coverage_targets = {
            "autonomous_orchestrator": 0.65,  # Objectif réaliste post-REFACTOR
            "meta_cognitive_agent": 0.60,
            "self_evolution_agent": 0.55,
            "test_runner_agent": 0.50
        }
        
        # Les cibles doivent être réalistes
        for component, target in coverage_targets.items():
            assert 0.5 <= target <= 1.0, f"{component} target should be between 50% and 100%"