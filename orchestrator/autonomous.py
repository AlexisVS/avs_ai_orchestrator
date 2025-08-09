#!/usr/bin/env python3
"""
Main Autonomous Orchestrator - Point d'entrée pour l'orchestration indépendante
Lance le système d'auto-évolution perpétuelle en production
"""

import asyncio
import sys
import os
import signal
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Ajouter le path src pour les imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from orchestrator.agents.autonomous_orchestrator import AutonomousOrchestrator
from orchestrator.agents.self_evolution_agent import SelfEvolutionAgent
from orchestrator.agents.bug_detector_agent import BugDetectorAgent
from orchestrator.agents.code_generator_agent import CodeGeneratorAgent
from orchestrator.agents.meta_cognitive_agent import MetaCognitiveAgent
from orchestrator.agents.test_runner_agent import TestRunnerAgent
from orchestrator.agents.github_sync_agent import GitHubSyncAgent


class IndependentOrchestrator:
    """Orchestrateur complètement indépendant qui s'auto-évolue en permanence"""
    
    def __init__(self):
        self.config = self._load_config()
        self.orchestrator = AutonomousOrchestrator(self.config)
        self.evolution_agent = SelfEvolutionAgent(self.config)
        self.github_sync = GitHubSyncAgent(self.config)
        self.running = False
        self.evolution_cycle = 0
        self.last_evolution = None
        self.setup_logging()
        self.setup_signal_handlers()
        
    def _load_config(self) -> Dict[str, Any]:
        """Charger la configuration"""
        config = {
            "evolution_interval": 300,  # 5 minutes entre chaque cycle
            "autonomy_threshold": 0.8,
            "self_modification_enabled": True,
            "continuous_evolution": True,
            "sandbox_path": Path.cwd().parent / "avs_ai_orchestrator_sandbox",
            "main_repo_path": Path.cwd(),
            "auto_testing": True,
            "auto_deployment": True,
            "independence_mode": True,
            "github": {
                "owner": "AlexisVS",
                "repo": "avs_ai_orchestrator",
                "project_id": "12"
            },
            "auto_merge": True,
            "auto_versioning": True
        }
        
        # Charger depuis fichier s'il existe
        config_file = Path("config/autonomous_config.json")
        if config_file.exists():
            try:
                file_config = json.loads(config_file.read_text())
                config.update(file_config)
            except Exception as e:
                print(f"[CONFIG] Erreur lecture config: {e}")
        
        return config
    
    def setup_logging(self):
        """Configurer le logging pour l'orchestration autonome"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "autonomous_orchestrator.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger("IndependentOrchestrator")
    
    def setup_signal_handlers(self):
        """Configurer les gestionnaires de signaux pour arrêt gracieux"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Gestionnaire de signaux pour arrêt propre"""
        self.logger.info(f"Signal {signum} reçu, arrêt gracieux...")
        self.running = False
    
    async def initialize_system(self):
        """Initialiser tous les composants du système autonome"""
        self.logger.info("=== INITIALISATION ORCHESTRATEUR INDÉPENDANT ===")
        
        # Initialiser l'orchestrateur principal
        self.orchestrator.is_running = True
        
        # Ajouter les agents essentiels
        await self.orchestrator.add_agent("evolution", "self_evolution", {
            "sandbox_path": str(self.config["sandbox_path"]),
            "auto_modification": True
        })
        
        await self.orchestrator.add_agent("bug_detector", "bug_detector", {
            "continuous_monitoring": True,
            "auto_fix": True
        })
        
        await self.orchestrator.add_agent("code_generator", "code_generator", {
            "auto_feature_generation": True,
            "smart_templates": True
        })
        
        await self.orchestrator.add_agent("meta_cognitive", "meta_cognitive", {
            "self_awareness": True,
            "learning_enabled": True
        })
        
        await self.orchestrator.add_agent("test_runner", "test_runner", {
            "auto_testing": True,
            "coverage_target": 0.7
        })
        
        self.logger.info("Systeme autonome initialise avec 5 agents")
        
    async def start_perpetual_evolution(self):
        """Démarrer la boucle d'évolution perpétuelle"""
        self.logger.info("DEMARRAGE EVOLUTION PERPETUELLE")
        self.running = True
        
        while self.running:
            try:
                self.evolution_cycle += 1
                cycle_start = datetime.now()
                
                self.logger.info(f"=== CYCLE ÉVOLUTION #{self.evolution_cycle} ===")
                
                # 1. Auto-surveillance du système
                health_status = await self._perform_system_health_check()
                self.logger.info(f"Santé système: {health_status['overall_health']}")
                
                # 2. Détection des opportunités d'amélioration
                improvements = await self._detect_improvement_opportunities()
                self.logger.info(f"Opportunités détectées: {len(improvements)}")
                
                # 3. Auto-génération des améliorations avec GitHub sync
                if improvements:
                    # Initier workflow GitHub pour chaque amélioration
                    github_workflows = []
                    for improvement in improvements:
                        improvement["cycle"] = self.evolution_cycle
                        workflow = await self.github_sync.sync_improvement_to_github(improvement)
                        github_workflows.append(workflow)
                        self.logger.info(f"GitHub workflow initié: Issue #{workflow.get('issue_created', 'N/A')}")
                    
                    generation_result = await self._auto_generate_improvements(improvements)
                    self.logger.info(f"Améliorations générées: {generation_result['generated']}")
                    
                    # 4. Auto-test des modifications
                    if generation_result["generated"] > 0:
                        test_result = await self._auto_test_modifications()
                        self.logger.info(f"Tests: {test_result['passed']}/{test_result['total']}")
                        
                        # 5. Compléter les workflows GitHub
                        for i, workflow in enumerate(github_workflows):
                            if "issue_created" in workflow:
                                # Utiliser les vrais noms de fichiers générés
                                improvement_type = improvements[i]['type']
                                real_generated_files = {
                                    f"src/{improvement_type}s.py": f"# Auto-generated code for {improvement_type}",
                                    f"tests/test_{improvement_type}.py": f"# Auto-generated tests for {improvement_type}"
                                }
                                completion = await self.github_sync.complete_improvement_workflow(
                                    workflow["issue_created"], real_generated_files
                                )
                                self.logger.info(f"Workflow GitHub terminé: {completion.get('workflow_completed', False)}")
                        
                        # 6. Auto-déploiement si tests passent
                        if test_result["success"]:
                            deploy_result = await self._auto_deploy_improvements()
                            status = "SUCCES" if deploy_result['success'] else "ECHEC"
                            self.logger.info(f"Deploiement: {status}")
                            
                            # 7. Auto-relance si nécessaire
                            if deploy_result["restart_required"]:
                                await self._prepare_self_restart()
                
                # 8. Métriques et apprentissage
                await self._record_evolution_metrics(cycle_start)
                await self._perform_meta_learning()
                
                # 9. Affichage statut GitHub sync
                if hasattr(self, 'github_sync'):
                    sync_status = await self.github_sync.get_sync_status()
                    self.logger.info(f"GitHub Sync: {sync_status['active_issues']} issues actives, version {sync_status['current_version']}")
                
                # 10. Attendre le prochain cycle
                await asyncio.sleep(self.config["evolution_interval"])
                
            except Exception as e:
                self.logger.error(f"Erreur cycle évolution {self.evolution_cycle}: {e}")
                # Auto-récupération
                await self._perform_error_recovery(e)
                await asyncio.sleep(60)  # Attendre 1 minute avant retry
    
    async def _perform_system_health_check(self) -> Dict[str, Any]:
        """Vérification complète de la santé du système"""
        status = await self.orchestrator._get_complete_system_status()
        
        # Ajouter des vérifications spécifiques
        health_checks = {
            "agents_responsive": all(
                agent.get("status") == "active" 
                for agent in self.orchestrator.agents.values()
            ),
            "memory_usage": self._check_memory_usage(),
            "disk_space": self._check_disk_space(),
            "evolution_capability": await self._check_evolution_capability()
        }
        
        overall_health = "healthy" if all(health_checks.values()) else "degraded"
        
        return {
            "overall_health": overall_health,
            "details": health_checks,
            "orchestrator_status": status
        }
    
    async def _detect_improvement_opportunities(self) -> list:
        """Détecter les opportunités d'amélioration"""
        opportunities = []
        
        # MODE PULL : Récupérer les opportunités depuis GitHub Issues et Project Board
        if self.config.get("pull_mode_enabled", False):
            try:
                self.logger.info("[REFRESH] Mode PULL activé - Lecture des issues GitHub...")
                github_result = await self.github_sync.execute_pull_workflow()
                
                if github_result.get("workflow_status") == "completed":
                    github_opportunities = github_result.get("opportunities_created", [])
                    opportunities.extend(github_opportunities)
                    self.logger.info(f"[OK] GitHub PULL: {len(github_opportunities)} opportunités détectées")
                else:
                    self.logger.warning(f"[WARN] GitHub PULL échoué: {github_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                self.logger.error(f"[ERROR] Erreur GitHub PULL mode: {e}")
        
        # Analyser les logs pour des patterns d'erreur
        error_patterns = await self._analyze_error_logs()
        if error_patterns:
            opportunities.extend([
                {"type": "bug_fix", "priority": "high", "patterns": error_patterns}
            ])
        
        # Analyser la couverture de tests
        coverage_gaps = await self._analyze_test_coverage_gaps()
        if coverage_gaps:
            opportunities.append({
                "type": "test_coverage", 
                "priority": "medium", 
                "gaps": coverage_gaps
            })
        
        # Détecter des optimisations possibles
        performance_issues = await self._detect_performance_issues()
        if performance_issues:
            opportunities.append({
                "type": "performance", 
                "priority": "medium",
                "issues": performance_issues
            })
        
        # Auto-générer de nouvelles fonctionnalités basées sur l'usage
        feature_ideas = await self._generate_feature_ideas()
        if feature_ideas:
            opportunities.append({
                "type": "feature", 
                "priority": "low",
                "ideas": feature_ideas
            })
        
        return opportunities
    
    async def _auto_generate_improvements(self, opportunities: list) -> Dict[str, Any]:
        """Auto-générer les améliorations"""
        generated_count = 0
        
        for opportunity in opportunities:
            try:
                if opportunity["type"] == "bug_fix":
                    generator = CodeGeneratorAgent(self.config)
                    fixes = await generator.generate_bug_fix(opportunity["patterns"])
                    await self._apply_generated_code(fixes, "bug_fixes")
                    generated_count += len(fixes)
                    
                elif opportunity["type"] == "test_coverage":
                    generator = CodeGeneratorAgent(self.config)
                    tests = await generator.generate_tests(opportunity["gaps"])
                    await self._apply_generated_code(tests, "tests")
                    generated_count += len(tests)
                    
                elif opportunity["type"] == "performance":
                    generator = CodeGeneratorAgent(self.config)
                    optimizations = await generator.generate_performance_improvement(
                        opportunity["issues"]
                    )
                    await self._apply_generated_code(optimizations, "optimizations")
                    generated_count += len(optimizations)
                    
                elif opportunity["type"] == "feature":
                    generator = CodeGeneratorAgent(self.config)
                    features = await generator.generate_feature(opportunity["ideas"])
                    await self._apply_generated_code(features, "features")
                    generated_count += len(features)
                    
            except Exception as e:
                self.logger.error(f"Erreur génération {opportunity['type']}: {e}")
        
        return {"generated": generated_count}
    
    async def _apply_generated_code(self, code_dict: Dict[str, str], category: str):
        """Appliquer le code généré dans la sandbox"""
        sandbox_path = self.config["sandbox_path"]
        
        for file_path, code_content in code_dict.items():
            try:
                full_path = sandbox_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(code_content)
                self.logger.info(f"Code généré appliqué: {file_path} ({category})")
            except Exception as e:
                self.logger.error(f"Erreur application code {file_path}: {e}")
    
    async def _auto_test_modifications(self) -> Dict[str, Any]:
        """Tester automatiquement les modifications"""
        test_runner = TestRunnerAgent(self.config)
        sandbox_path = self.config["sandbox_path"]
        
        try:
            result = await test_runner.run_tests(sandbox_path)
            return {
                "success": result.get("success", False),
                "passed": result.get("passed", 0),
                "total": result.get("total", 0),
                "coverage": result.get("coverage", 0.0)
            }
        except Exception as e:
            self.logger.error(f"Erreur auto-test: {e}")
            return {"success": False, "passed": 0, "total": 1, "coverage": 0.0}
    
    async def _auto_deploy_improvements(self) -> Dict[str, Any]:
        """Déployer automatiquement les améliorations"""
        try:
            # Copier les fichiers modifiés de la sandbox vers le repo principal
            await self._sync_sandbox_to_main()
            
            # Commit automatique
            await self._auto_commit_changes()
            
            self.logger.info("Deploiement automatique reussi")
            return {"success": True, "restart_required": True}
            
        except Exception as e:
            self.logger.error(f"Erreur déploiement: {e}")
            return {"success": False, "restart_required": False}
    
    async def _prepare_self_restart(self):
        """Préparer l'auto-relance du système"""
        self.logger.info("PREPARATION AUTO-RELANCE...")
        
        # Sauvegarder l'état actuel
        state = {
            "evolution_cycle": self.evolution_cycle,
            "last_evolution": datetime.now().isoformat(),
            "total_improvements": self.evolution_cycle * 2,  # Estimation
            "restart_reason": "auto_improvement_deployment"
        }
        
        state_file = Path("evolution_state.json")
        state_file.write_text(json.dumps(state, indent=2))
        
        self.logger.info("État sauvegardé, redémarrage dans 10 secondes...")
        await asyncio.sleep(10)
        
        # Auto-relance
        os.execl(sys.executable, sys.executable, *sys.argv)
    
    # Méthodes utilitaires simplifiées pour le prototype
    def _check_memory_usage(self) -> bool:
        return True  # Toujours OK pour le prototype
    
    def _check_disk_space(self) -> bool:
        return True  # Toujours OK pour le prototype
    
    async def _check_evolution_capability(self) -> bool:
        return True  # Capacité d'évolution toujours active
    
    async def _analyze_error_logs(self) -> list:
        # Simulation : retourner parfois des patterns d'erreur
        if self.evolution_cycle % 3 == 0:
            return ["TypeError in agent.py line 42", "Missing import in utils.py"]
        return []
    
    async def _analyze_test_coverage_gaps(self) -> list:
        # Simulation : identifier des gaps de couverture
        if self.evolution_cycle % 4 == 0:
            return ["Module sans test: new_module", "Méthode non couverte: process_data"]
        return []
    
    async def _detect_performance_issues(self) -> list:
        # Simulation : détecter des problèmes de performance
        if self.evolution_cycle % 5 == 0:
            return [{"function": "slow_processing", "type": "slow_function"}]
        return []
    
    async def _generate_feature_ideas(self) -> list:
        # Simulation : générer des idées de fonctionnalités
        if self.evolution_cycle % 6 == 0:
            return ["TODO: Add caching system", "TODO: Implement retry logic"]
        return []
    
    async def _sync_sandbox_to_main(self):
        # Simulation de synchronisation
        self.logger.info("Synchronisation sandbox → main repo")
        await asyncio.sleep(1)
    
    async def _auto_commit_changes(self):
        # Simulation de commit automatique
        commit_msg = f"Auto-evolution cycle #{self.evolution_cycle} - Automated improvements"
        self.logger.info(f"Auto-commit: {commit_msg}")
        await asyncio.sleep(0.5)
    
    async def _record_evolution_metrics(self, cycle_start: datetime):
        cycle_duration = (datetime.now() - cycle_start).total_seconds()
        self.logger.info(f"Cycle {self.evolution_cycle} terminé en {cycle_duration:.1f}s")
    
    async def _perform_meta_learning(self):
        # Méta-apprentissage pour optimiser le processus d'évolution
        self.logger.info("Méta-apprentissage en cours...")
        await asyncio.sleep(0.1)
    
    async def _perform_error_recovery(self, error: Exception):
        # Récupération automatique d'erreur
        self.logger.info(f"Récupération d'erreur: {type(error).__name__}")
        await asyncio.sleep(1)


async def main():
    """Point d'entrée principal pour l'orchestrateur indépendant"""
    print("=== ORCHESTRATEUR AI INDEPENDANT ===")
    print("Demarrage du systeme d'auto-evolution perpetuelle...")
    
    # Restaurer l'état si redémarrage
    state_file = Path("evolution_state.json")
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text())
            print(f"Redemarrage detecte - Cycle #{state.get('evolution_cycle', 0)}")
            print(f"Raison: {state.get('restart_reason', 'unknown')}")
        except Exception as e:
            print(f"Erreur lecture etat: {e}")
    
    orchestrator = IndependentOrchestrator()
    
    try:
        # Initialisation
        await orchestrator.initialize_system()
        
        # Démarrage de l'évolution perpétuelle
        await orchestrator.start_perpetual_evolution()
        
    except KeyboardInterrupt:
        print("\nArret demande par l'utilisateur")
    except Exception as e:
        print(f"Erreur fatale: {e}")
        logging.exception("Erreur fatale dans l'orchestrateur")
    finally:
        print("Arret de l'orchestrateur autonome")


if __name__ == "__main__":
    asyncio.run(main())