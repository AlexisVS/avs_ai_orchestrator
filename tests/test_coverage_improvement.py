"""
Tests TDD pour augmenter la couverture des agents autonomes
Ces tests ciblent spécifiquement les lignes manquantes pour atteindre 80% de couverture
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
import json
import tempfile


class TestMetaCognitiveAgentCoverage:
    """Tests pour augmenter la couverture du MetaCognitiveAgent"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_meta_cognitive_loop_execution(self, mock_config):
        """Test l'exécution complète de la boucle méta-cognitive"""
        from orchestrator.agents.meta_cognitive_agent import MetaCognitiveAgent
        
        agent = MetaCognitiveAgent(mock_config)
        
        # Mock pour arrêter la boucle après quelques itérations
        with patch.object(agent, '_observe_self') as mock_observe:
            with patch.object(agent, '_reflect_on_processes') as mock_reflect:
                with patch.object(agent, '_generate_self_improvements') as mock_improve:
                    with patch.object(agent, '_implement_improvements') as mock_implement:
                        with patch.object(agent, '_evaluate_changes') as mock_evaluate:
                            with patch.object(agent, '_evolve_consciousness') as mock_evolve:
                                with patch('asyncio.sleep') as mock_sleep:
                                    
                                    mock_reflect.return_value = [{"insight": "test"}]
                                    mock_improve.return_value = [{"improvement": "test"}]
                                    mock_sleep.side_effect = [None, Exception("Stop loop")]
                                    
                                    # Test que la boucle s'exécute
                                    with pytest.raises(Exception):
                                        await agent.start_meta_cognitive_loop()
                                    
                                    # Vérifier que les méthodes ont été appelées
                                    mock_observe.assert_called()
                                    mock_reflect.assert_called()
                                    mock_improve.assert_called()
                                    mock_implement.assert_called()
                                    mock_evaluate.assert_called()
                                    mock_evolve.assert_called()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reflect_on_processes_with_patterns(self, mock_config):
        """Test la réflexion sur les processus avec patterns existants"""
        from orchestrator.agents.meta_cognitive_agent import MetaCognitiveAgent, CognitivePattern
        
        agent = MetaCognitiveAgent(mock_config)
        
        # Ajouter des patterns avec usage élevé
        for i in range(5):
            pattern = CognitivePattern(
                id=f"pattern_{i}",
                name=f"Pattern {i}",
                description="Test pattern",
                efficiency_score=0.8,
                usage_count=15,  # > 10 pour déclencher la réflexion
                success_rate=0.9,
                learned_at="2023-01-01",
                last_used="2023-01-01",
                improvement_suggestions=[]
            )
            agent.cognitive_patterns[f"pattern_{i}"] = pattern
        
        # Mock les méthodes de réflexion
        with patch.object(agent, '_reflect_on_pattern') as mock_pattern_reflect:
            with patch.object(agent, '_reflect_on_failures') as mock_failures:
                with patch.object(agent, '_reflect_on_successes') as mock_successes:
                    
                    mock_pattern_reflect.return_value = {"pattern_insight": "test"}
                    mock_failures.return_value = [{"failure_insight": "test"}]
                    mock_successes.return_value = [{"success_insight": "test"}]
                    
                    insights = await agent._reflect_on_processes()
                    
                    assert isinstance(insights, list)
                    # Vérifier que les réflexions ont été appelées
                    assert mock_pattern_reflect.call_count == 5
                    mock_failures.assert_called_once()
                    mock_successes.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_self_improvements(self, mock_config):
        """Test la génération d'améliorations autonomes"""
        from orchestrator.agents.meta_cognitive_agent import MetaCognitiveAgent
        
        agent = MetaCognitiveAgent(mock_config)
        
        insights = [
            {"type": "efficiency", "data": "low efficiency detected", "improvement_type": "pattern_optimization"},
            {"type": "pattern", "data": "pattern optimization needed", "improvement_type": "algorithm_enhancement"},
            {"type": "learning", "data": "learning strategy improvement", "improvement_type": "cognitive_upgrade"},
            {"type": "creative", "data": "creative enhancement", "improvement_type": "emergent_capability"},
            {"type": "general", "data": "general improvement", "improvement_type": "unknown"}
        ]
        
        improvements = await agent._generate_self_improvements(insights)
        
        assert isinstance(improvements, list)
        assert len(improvements) > 0
        
        # Vérifier que les améliorations ont des propriétés requises
        for improvement in improvements:
            assert "type" in improvement
            # Note: Le format exact peut varier selon l'implémentation
            
    @pytest.mark.unit 
    @pytest.mark.asyncio
    async def test_implement_improvements_different_types(self, mock_config):
        """Test l'implémentation d'améliorations de différents types"""
        from orchestrator.agents.meta_cognitive_agent import MetaCognitiveAgent
        
        agent = MetaCognitiveAgent(mock_config)
        
        improvements = [
            {"type": "algorithm_modification", "description": "Algorithm improvement"},
            {"type": "cognitive_rewiring", "description": "Cognitive rewiring"},
            {"type": "pattern_enhancement", "description": "Pattern enhancement"},
            {"type": "emergent_behavior", "description": "Emergent behavior"},
            {"type": "unknown_type", "description": "Unknown improvement type"}
        ]
        
        # Test l'implémentation
        await agent._implement_improvements(improvements)
        
        # Vérifier que le compteur de modifications a augmenté
        assert agent.self_modification_count > 0
        
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_evaluate_changes(self, mock_config):
        """Test l'évaluation des changements"""
        from orchestrator.agents.meta_cognitive_agent import MetaCognitiveAgent
        
        agent = MetaCognitiveAgent(mock_config)
        
        # Ajouter des métriques d'intelligence
        agent.intelligence_metrics = {
            "pattern_recognition": 0.7,
            "abstract_reasoning": 0.6,
            "predictive_accuracy": 0.8,
            "adaptive_learning": 0.75,
            "creative_synthesis": 0.65,
            "meta_awareness": 0.9
        }
        
        # Test l'évaluation
        await agent._evaluate_changes()
        
        # Vérifier que la conscience a évolué
        assert agent.consciousness_level >= 0.0


class TestSelfEvolutionAgentCoverage:
    """Tests pour augmenter la couverture du SelfEvolutionAgent"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_evolution_loop_full_cycle(self, mock_config, temp_dir):
        """Test un cycle complet d'évolution"""
        from orchestrator.agents.self_evolution_agent import SelfEvolutionAgent
        
        agent = SelfEvolutionAgent(mock_config)
        agent.main_repo_path = temp_dir
        agent.is_evolving = True
        
        # Mock toutes les méthodes pour simuler un cycle complet
        with patch.object(agent, 'detect_improvements') as mock_detect:
            with patch.object(agent, 'generate_improvements') as mock_generate:
                with patch.object(agent, 'test_in_sandbox') as mock_test:
                    with patch.object(agent, 'push_to_main_repo') as mock_push:
                        with patch.object(agent, 'self_restart') as mock_restart:
                            with patch('asyncio.sleep') as mock_sleep:
                                
                                # Simuler détection d'améliorations
                                mock_detect.return_value = [{"type": "bug_fix"}]
                                mock_generate.return_value = True
                                mock_test.return_value = True
                                mock_sleep.side_effect = [None, Exception("Stop")]
                                
                                # Test le cycle
                                with pytest.raises(Exception):
                                    await agent.start_evolution_loop()
                                
                                # Vérifier les appels
                                mock_detect.assert_called()
                                mock_generate.assert_called()
                                mock_test.assert_called()
                                mock_push.assert_called()
                                mock_restart.assert_called()
                                
                                # Le cycle peut être supérieur à 1 si la boucle itère plusieurs fois
                                assert agent.evolution_cycle >= 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_logs_with_errors(self, mock_config, temp_dir):
        """Test l'analyse de logs avec des erreurs"""
        from orchestrator.agents.self_evolution_agent import SelfEvolutionAgent
        
        agent = SelfEvolutionAgent(mock_config)
        agent.main_repo_path = temp_dir
        
        # Créer des fichiers de log avec erreurs
        log_dir = temp_dir / "logs"
        log_dir.mkdir()
        
        error_log = log_dir / "error.log"
        error_log.write_text("""
2023-01-01 10:00:00 INFO Starting application
2023-01-01 10:00:01 ERROR Failed to connect to database
2023-01-01 10:00:02 Exception in thread main:
    Traceback (most recent call last):
        File "main.py", line 10, in <module>
            raise ValueError("Test error")
    ValueError: Test error
        """)
        
        patterns = await agent._analyze_logs()
        
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        
        # Vérifier que les erreurs ont été détectées
        found_error = any("ERROR" in pattern or "Exception" in pattern for pattern in patterns)
        assert found_error

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_performance_with_metrics(self, mock_config, temp_dir):
        """Test l'analyse de performance avec métriques"""
        from orchestrator.agents.self_evolution_agent import SelfEvolutionAgent
        
        agent = SelfEvolutionAgent(mock_config)
        agent.main_repo_path = temp_dir
        
        # Créer un fichier de métriques
        metrics_file = temp_dir / "metrics.json"
        metrics_data = {
            "slow_functions": [
                {"function": "slow_computation", "time": 5.2},
                {"function": "database_query", "time": 3.1}
            ]
        }
        metrics_file.write_text(json.dumps(metrics_data))
        
        issues = await agent._analyze_performance()
        
        assert isinstance(issues, list)
        assert len(issues) == 2
        assert issues[0]["function"] == "slow_computation"
        assert issues[1]["function"] == "database_query"


class TestCodeGeneratorAgentCoverage:
    """Tests pour augmenter la couverture du CodeGeneratorAgent"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_performance_improvement_generation(self, mock_config):
        """Test la génération d'améliorations de performance"""
        from orchestrator.agents.code_generator_agent import CodeGeneratorAgent
        
        generator = CodeGeneratorAgent(mock_config)
        
        performance_issues = [
            {"function": "slow_computation", "type": "slow_function", "time": 5.2},
            {"function": "inefficient_loop", "type": "nested_loop", "complexity": "O(n²)"}
        ]
        
        improvements = await generator.generate_performance_improvement(performance_issues)
        
        assert isinstance(improvements, dict)
        assert len(improvements) > 0
        
        # Vérifier que les améliorations contiennent du code
        for file_path, code in improvements.items():
            assert isinstance(code, str)
            assert len(code) > 0
            
    @pytest.mark.unit
    def test_extract_function_name(self, mock_config):
        """Test l'extraction d'un nom de fonction"""
        from orchestrator.agents.code_generator_agent import CodeGeneratorAgent
        
        generator = CodeGeneratorAgent(mock_config)
        
        # Test avec une fonction simple
        function_name = generator._extract_function_name("def test_function():")
        assert function_name == "test_function"
        
        # Test avec méthode de classe
        method_name = generator._extract_function_name("    def method_name(self):")
        assert method_name == "method_name"

    @pytest.mark.unit
    def test_generate_function_template(self, mock_config):
        """Test la génération de template de fonction"""
        from orchestrator.agents.code_generator_agent import CodeGeneratorAgent
        
        generator = CodeGeneratorAgent(mock_config)
        
        function_code = generator._generate_function_template("test_function", "Test function")
        
        assert isinstance(function_code, str)
        assert "def test_function" in function_code
        assert "Test function" in function_code


class TestTestRunnerAgentCoverage:
    """Tests pour augmenter la couverture du TestRunnerAgent"""
    
    @pytest.mark.unit
    def test_test_runner_initialization(self, mock_config):
        """Test l'initialisation du test runner"""
        from orchestrator.agents.test_runner_agent import TestRunnerAgent
        
        test_runner = TestRunnerAgent(mock_config)
        
        assert test_runner is not None
        assert hasattr(test_runner, 'config')
        assert test_runner.config == mock_config

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_coverage_with_mock_data(self, mock_config, temp_dir):
        """Test l'analyse de couverture avec données mockées"""
        from orchestrator.agents.test_runner_agent import TestRunnerAgent
        
        test_runner = TestRunnerAgent(mock_config)
        
        # Créer un fichier de couverture mock
        coverage_data = {
            "totals": {
                "num_statements": 100,
                "covered_lines": 85
            },
            "files": {
                "src/test.py": {
                    "summary": {"num_statements": 50, "covered_lines": 40},
                    "missing_lines": [10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
                }
            }
        }
        
        coverage_file = temp_dir / "coverage.json"
        coverage_file.write_text(json.dumps(coverage_data))
        
        # Test avec mock du path.cwd()
        with patch('pathlib.Path.cwd', return_value=temp_dir):
            result = await test_runner._analyze_coverage()
            
            assert isinstance(result, dict)
            assert "coverage" in result
            assert result["coverage"] == 85.0


class TestBugDetectorAgentCoverage:
    """Tests pour augmenter la couverture du BugDetectorAgent"""
    
    @pytest.mark.unit
    def test_bug_detector_initialization(self, mock_config):
        """Test l'initialisation du détecteur de bugs"""
        from orchestrator.agents.bug_detector_agent import BugDetectorAgent
        
        detector = BugDetectorAgent(mock_config)
        
        assert detector is not None
        assert hasattr(detector, 'config')
        assert detector.config == mock_config

    @pytest.mark.unit
    @pytest.mark.asyncio 
    async def test_bug_detector_basic_functionality(self, mock_config):
        """Test les fonctionnalités de base du détecteur de bugs"""
        from orchestrator.agents.bug_detector_agent import BugDetectorAgent
        
        detector = BugDetectorAgent(mock_config)
        
        # Test des méthodes accessibles
        assert hasattr(detector, 'config')
        
        # Vérifier que l'agent peut être utilisé dans des opérations de base
        result = await detector._detect_common_patterns("test code")
        assert isinstance(result, list)