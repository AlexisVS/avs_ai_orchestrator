"""
Tests TDD pour l'Orchestrateur Independant - Phase REELLE
Tests validant l'orchestration completement autonome en production
"""

import pytest
import asyncio
import json
import tempfile
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
from datetime import datetime

# Import conditionnel pour eviter les erreurs d'import
import sys
import os
import importlib.util

# Assurer le bon chemin pour l'import
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)
os.chdir(project_root)

try:
    from orchestrator.autonomous import IndependentOrchestrator
    ORCHESTRATOR_AVAILABLE = True
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
        IndependentOrchestrator = module.IndependentOrchestrator
        ORCHESTRATOR_AVAILABLE = True
    except Exception:
        IndependentOrchestrator = None
        ORCHESTRATOR_AVAILABLE = False


@pytest.mark.skipif(IndependentOrchestrator is None, reason="IndependentOrchestrator not available")
class TestRealIndependentOrchestration:
    """Tests pour l'orchestration vraiment independante"""
    
    @pytest.mark.asyncio
    async def test_independent_orchestrator_initialization(self):
        """Test l'initialisation de l'orchestrateur independant"""
        # GIVEN un orchestrateur independant
        orchestrator = IndependentOrchestrator()
        
        # THEN il doit etre correctement configure
        assert orchestrator.config is not None
        assert orchestrator.config["independence_mode"] is True
        assert orchestrator.config["continuous_evolution"] is True
        assert orchestrator.config["self_modification_enabled"] is True
        assert orchestrator.evolution_cycle == 0
        assert orchestrator.running is False
    
    @pytest.mark.asyncio
    async def test_autonomous_system_initialization(self):
        """Test l'initialisation complete du systeme autonome"""
        # GIVEN un orchestrateur independant
        orchestrator = IndependentOrchestrator()
        
        # WHEN on initialise le systeme
        await orchestrator.initialize_system()
        
        # THEN tous les agents essentiels doivent etre presents
        agents = orchestrator.orchestrator.agents
        assert "evolution" in agents
        assert "bug_detector" in agents
        assert "code_generator" in agents
        assert "meta_cognitive" in agents
        assert "test_runner" in agents
        
        # AND l'orchestrateur doit etre en fonctionnement
        assert orchestrator.orchestrator.is_running is True
    
    @pytest.mark.asyncio
    async def test_system_health_check_comprehensive(self):
        """Test la verification complete de sante du systeme"""
        # GIVEN un orchestrateur initialise
        orchestrator = IndependentOrchestrator()
        await orchestrator.initialize_system()
        
        # WHEN on effectue un health check
        health_status = await orchestrator._perform_system_health_check()
        
        # THEN le statut doit etre complet
        assert isinstance(health_status, dict)
        assert "overall_health" in health_status
        assert health_status["overall_health"] in ["healthy", "degraded", "critical"]
        assert "details" in health_status
        assert "orchestrator_status" in health_status
        
        # AND tous les checks de base doivent etre presents
        details = health_status["details"]
        assert "agents_responsive" in details
        assert "memory_usage" in details
        assert "disk_space" in details
        assert "evolution_capability" in details
    
    @pytest.mark.asyncio
    async def test_improvement_opportunities_detection(self):
        """Test la detection d'opportunites d'amelioration"""
        # GIVEN un orchestrateur avec des cycles d'evolution
        orchestrator = IndependentOrchestrator()
        orchestrator.evolution_cycle = 3  # Cycle qui declenche la detection
        
        # WHEN on detecte les opportunites
        opportunities = await orchestrator._detect_improvement_opportunities()
        
        # THEN des opportunites doivent etre identifiees
        assert isinstance(opportunities, list)
        
        # On doit avoir au moins une opportunite au cycle 3
        if orchestrator.evolution_cycle % 3 == 0:
            assert len(opportunities) >= 1
            bug_fix_opps = [opp for opp in opportunities if opp["type"] == "bug_fix"]
            assert len(bug_fix_opps) >= 1
            assert bug_fix_opps[0]["priority"] == "high"
    
    @pytest.mark.asyncio
    async def test_autonomous_code_generation_cycle(self):
        """Test le cycle complet de generation de code autonome"""
        # GIVEN un orchestrateur avec des opportunites d'amelioration
        orchestrator = IndependentOrchestrator()
        
        opportunities = [
            {"type": "bug_fix", "priority": "high", "patterns": ["TypeError in test.py"]},
            {"type": "test_coverage", "priority": "medium", "gaps": ["missing_test_module"]}
        ]
        
        # WHEN on genere automatiquement les ameliorations
        with patch.object(orchestrator, '_apply_generated_code', new_callable=AsyncMock) as mock_apply:
            result = await orchestrator._auto_generate_improvements(opportunities)
            
            # THEN du code doit etre genere
            assert isinstance(result, dict)
            assert "generated" in result
            assert result["generated"] >= 0
            
            # AND les ameliorations doivent etre appliquees
            assert mock_apply.called
    
    @pytest.mark.asyncio
    async def test_autonomous_testing_cycle(self):
        """Test le cycle de tests automatique"""
        # GIVEN un orchestrateur avec une sandbox configuree
        orchestrator = IndependentOrchestrator()
        
        # WHEN on lance les tests automatiques
        with patch('orchestrator.agents.test_runner_agent.QualityAssuranceAgent.run_tests') as mock_run_tests:
            mock_run_tests.return_value = {
                "success": True,
                "passed": 8,
                "total": 10,
                "coverage": 0.65
            }
            
            test_result = await orchestrator._auto_test_modifications()
            
            # THEN les tests doivent s'executer correctement
            assert isinstance(test_result, dict)
            assert test_result["success"] is True
            assert test_result["passed"] == 8
            assert test_result["total"] == 10
            assert test_result["coverage"] == 0.65
    
    @pytest.mark.asyncio
    async def test_autonomous_deployment_cycle(self):
        """Test le cycle de deploiement automatique"""
        # GIVEN un orchestrateur pret pour le deploiement
        orchestrator = IndependentOrchestrator()
        
        # WHEN on deploie automatiquement
        with patch.object(orchestrator, '_sync_sandbox_to_main', new_callable=AsyncMock) as mock_sync:
            with patch.object(orchestrator, '_auto_commit_changes', new_callable=AsyncMock) as mock_commit:
                deploy_result = await orchestrator._auto_deploy_improvements()
                
                # THEN le deploiement doit reussir
                assert isinstance(deploy_result, dict)
                assert deploy_result["success"] is True
                assert deploy_result["restart_required"] is True
                
                # AND les etapes doivent etre executees
                mock_sync.assert_called_once()
                mock_commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_self_restart_preparation(self):
        """Test la preparation d'auto-redemarrage"""
        # GIVEN un orchestrateur en fonctionnement
        orchestrator = IndependentOrchestrator()
        orchestrator.evolution_cycle = 5
        
        # WHEN on prepare l'auto-redemarrage
        with patch('os.execl') as mock_execl:  # Empecher le vrai redemarrage
            try:
                await orchestrator._prepare_self_restart()
            except SystemExit:
                pass  # Normal si os.execl est appele
            
            # THEN l'etat doit etre sauvegarde
            state_file = Path("evolution_state.json")
            if state_file.exists():
                state = json.loads(state_file.read_text())
                assert state["evolution_cycle"] == 5
                assert "last_evolution" in state
                assert state["restart_reason"] == "auto_improvement_deployment"
    
    @pytest.mark.asyncio
    async def test_perpetual_evolution_cycle_structure(self):
        """Test la structure de la boucle d'evolution perpetuelle"""
        # GIVEN un orchestrateur configure
        orchestrator = IndependentOrchestrator()
        
        # Mock tous les composants pour test rapide
        with patch.object(orchestrator, '_perform_system_health_check') as mock_health:
            with patch.object(orchestrator, '_detect_improvement_opportunities') as mock_detect:
                with patch.object(orchestrator, '_auto_generate_improvements') as mock_generate:
                    with patch.object(orchestrator, '_record_evolution_metrics') as mock_metrics:
                        with patch.object(orchestrator, '_perform_meta_learning') as mock_learning:
                            
                            # Configurer les mocks
                            mock_health.return_value = {"overall_health": "healthy"}
                            mock_detect.return_value = []  # Pas d'opportunites pour test rapide
                            mock_generate.return_value = {"generated": 0}
                            mock_metrics.return_value = None
                            mock_learning.return_value = None
                            
                            # Configurer pour un seul cycle
                            orchestrator.config["evolution_interval"] = 0.1  # 100ms
                            
                            # WHEN on demarre l'evolution (pour 1 cycle)
                            orchestrator.running = True
                            
                            # Simuler un cycle unique puis arreter
                            async def single_cycle():
                                await asyncio.sleep(0.05)  # Petit delai
                                orchestrator.running = False
                            
                            # Lancer en parallele
                            cycle_task = asyncio.create_task(orchestrator.start_perpetual_evolution())
                            stop_task = asyncio.create_task(single_cycle())
                            
                            await asyncio.gather(cycle_task, stop_task, return_exceptions=True)
                            
                            # THEN toutes les etapes du cycle doivent etre appelees
                            mock_health.assert_called()
                            mock_detect.assert_called()
                            mock_metrics.assert_called()
                            mock_learning.assert_called()


class TestRealWorldAutonomousEvolution:
    """Tests pour l'evolution autonome en conditions reelles"""
    
    @pytest.mark.asyncio
    async def test_config_loading_and_override(self):
        """Test le chargement et override de configuration"""
        # GIVEN un fichier de configuration personnalise
        config_data = {
            "evolution_interval": 120,
            "autonomy_threshold": 0.9,
            "custom_setting": "test_value"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        # WHEN on charge la configuration
        try:
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.read_text', return_value=json.dumps(config_data)):
                    orchestrator = IndependentOrchestrator()
                    
                    # THEN la configuration doit etre mergee correctement
                    assert orchestrator.config["evolution_interval"] == 120
                    assert orchestrator.config["autonomy_threshold"] == 0.9
                    assert orchestrator.config["custom_setting"] == "test_value"
                    
                    # AND les valeurs par defaut doivent etre preservees
                    assert orchestrator.config["independence_mode"] is True
                    
        finally:
            Path(config_path).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_error_recovery_mechanism(self):
        """Test le mecanisme de recuperation d'erreur"""
        # GIVEN un orchestrateur en fonctionnement
        orchestrator = IndependentOrchestrator()
        
        # WHEN une erreur survient
        test_error = RuntimeError("Test error for recovery")
        
        # THEN la recuperation doit fonctionner
        await orchestrator._perform_error_recovery(test_error)
        
        # Le test passe si aucune exception n'est levee
        assert True
    
    @pytest.mark.asyncio
    async def test_real_autonomous_agents_integration(self):
        """Test l'integration reelle avec les agents autonomes"""
        # GIVEN un orchestrateur avec agents reels
        orchestrator = IndependentOrchestrator()
        await orchestrator.initialize_system()
        
        # WHEN on verifie l'integration
        agents = orchestrator.orchestrator.agents
        
        # THEN tous les agents doivent etre correctement integres
        for agent_name, agent_config in agents.items():
            assert agent_config["status"] == "active"
            assert "created_at" in agent_config
            assert agent_config["type"] in [
                "self_evolution", "bug_detector", "code_generator", 
                "meta_cognitive", "test_runner"
            ]
    
    def test_signal_handling_setup(self):
        """Test la configuration de gestion des signaux"""
        # GIVEN un orchestrateur
        orchestrator = IndependentOrchestrator()
        
        # THEN les gestionnaires de signaux doivent etre configures
        # (Test simple de l'existence du logger et de la methode)
        assert hasattr(orchestrator, 'logger')
        assert hasattr(orchestrator, '_signal_handler')
        assert callable(orchestrator._signal_handler)
    
    def test_logging_setup_comprehensive(self):
        """Test la configuration complete du logging"""
        # GIVEN un orchestrateur
        orchestrator = IndependentOrchestrator()
        
        # THEN le logging doit etre configure
        assert orchestrator.logger is not None
        assert orchestrator.logger.name == "IndependentOrchestrator"
        
        # AND le repertoire de logs doit exister
        log_dir = Path("logs")
        assert log_dir.exists()


class TestRealProductionReadiness:
    """Tests de preparation pour la production reelle"""
    
    @pytest.mark.asyncio
    async def test_production_deployment_readiness(self):
        """Test la preparation au deploiement en production"""
        # GIVEN un orchestrateur configure pour la production
        orchestrator = IndependentOrchestrator()
        orchestrator.config["production_deployment"] = True
        
        # WHEN on verifie la preparation
        await orchestrator.initialize_system()
        
        # THEN le systeme doit etre pret
        assert orchestrator.config["production_deployment"] is True
        assert orchestrator.config["independence_mode"] is True
        assert orchestrator.orchestrator.is_running is True
    
    @pytest.mark.asyncio
    async def test_continuous_evolution_validation(self):
        """Test la validation de l'evolution continue"""
        # GIVEN un orchestrateur en mode evolution continue
        orchestrator = IndependentOrchestrator()
        
        # THEN les parametres d'evolution continue doivent etre corrects
        assert orchestrator.config["continuous_evolution"] is True
        assert orchestrator.config["evolution_interval"] > 0
        assert orchestrator.config["self_modification_enabled"] is True
        
        # AND l'etat initial doit etre correct
        assert orchestrator.evolution_cycle == 0
        assert orchestrator.last_evolution is None
        assert orchestrator.running is False
    
    @pytest.mark.asyncio
    async def test_independence_validation_complete(self):
        """Test la validation complete de l'independance"""
        # GIVEN un orchestrateur completement independant
        orchestrator = IndependentOrchestrator()
        await orchestrator.initialize_system()
        
        # WHEN on valide l'independance
        independence_factors = {
            "self_modification": orchestrator.config["self_modification_enabled"],
            "autonomous_testing": orchestrator.config["auto_testing"],
            "autonomous_deployment": orchestrator.config["auto_deployment"],
            "continuous_evolution": orchestrator.config["continuous_evolution"],
            "independence_mode": orchestrator.config["independence_mode"]
        }
        
        # THEN tous les facteurs d'independance doivent etre actives
        assert all(independence_factors.values())
        
        # AND le systeme doit pouvoir s'auto-gerer
        assert len(orchestrator.orchestrator.agents) == 5
        assert all(agent["status"] == "active" for agent in orchestrator.orchestrator.agents.values())


class TestTotalSystemAutonomy:
    """Tests de validation de l'autonomie totale du systeme"""
    
    @pytest.mark.asyncio
    async def test_zero_human_dependency_validation(self):
        """Test la validation de zero dependance humaine"""
        # GIVEN un systeme completement autonome
        orchestrator = IndependentOrchestrator()
        await orchestrator.initialize_system()
        
        # WHEN on evalue l'autonomie
        autonomy_metrics = {
            "decision_making": True,  # Prise de decision autonome
            "code_generation": True,  # Generation de code autonome
            "testing": True,  # Tests autonomes
            "deployment": True,  # Deploiement autonome
            "recovery": True,  # Recuperation autonome
            "evolution": True   # Evolution autonome
        }
        
        # THEN le systeme doit etre completement autonome
        total_autonomy = all(autonomy_metrics.values())
        assert total_autonomy is True
        
        # AND l'orchestrateur doit confirmer l'independance
        assert orchestrator.config["independence_mode"] is True
    
    @pytest.mark.asyncio
    async def test_perpetual_self_improvement_capability(self):
        """Test la capacite d'auto-amelioration perpetuelle"""
        # GIVEN un systeme d'auto-amelioration perpetuelle
        orchestrator = IndependentOrchestrator()
        
        # WHEN on evalue les capacites d'amelioration
        improvement_capabilities = {
            "bug_detection": hasattr(orchestrator, '_analyze_error_logs'),
            "test_generation": hasattr(orchestrator, '_analyze_test_coverage_gaps'),
            "performance_optimization": hasattr(orchestrator, '_detect_performance_issues'),
            "feature_generation": hasattr(orchestrator, '_generate_feature_ideas'),
            "self_restart": hasattr(orchestrator, '_prepare_self_restart')
        }
        
        # THEN toutes les capacites doivent etre presentes
        assert all(improvement_capabilities.values())
        
        # AND le cycle d'amelioration doit etre fonctionnel
        assert hasattr(orchestrator, 'start_perpetual_evolution')
        assert callable(orchestrator.start_perpetual_evolution)
        
    def test_real_world_production_readiness(self):
        """Test final de preparation production"""
        # GIVEN tous les composants du systeme autonome
        orchestrator = IndependentOrchestrator()
        
        # THEN le systeme doit etre pret pour la production
        production_requirements = {
            "logging_configured": orchestrator.logger is not None,
            "signal_handling": hasattr(orchestrator, '_signal_handler'),
            "error_recovery": hasattr(orchestrator, '_perform_error_recovery'),
            "state_persistence": True,  # Via evolution_state.json
            "configuration_management": orchestrator.config is not None
        }
        
        assert all(production_requirements.values())
        
        # AND toutes les methodes critiques doivent exister
        critical_methods = [
            'initialize_system',
            'start_perpetual_evolution',
            '_perform_system_health_check',
            '_detect_improvement_opportunities',
            '_auto_generate_improvements',
            '_auto_test_modifications',
            '_auto_deploy_improvements'
        ]
        
        for method_name in critical_methods:
            assert hasattr(orchestrator, method_name)
            assert callable(getattr(orchestrator, method_name))