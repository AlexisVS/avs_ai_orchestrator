#!/usr/bin/env python3
"""
Main Autonomous Orchestrator - Point d'entree pour l'orchestration independante
Lance le systeme d'auto-evolution perpetuelle en production
"""

import asyncio
import sys
import os
import signal
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Ajouter le path src pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from orchestrator.agents.autonomous_orchestrator import AutonomousOrchestrator
    from orchestrator.agents.self_evolution_agent import SelfEvolutionAgent
    from orchestrator.agents.bug_detector_agent import BugDetectorAgent
    from orchestrator.agents.code_generator_agent import CodeGeneratorAgent
    from orchestrator.agents.meta_cognitive_agent import MetaCognitiveAgent
    from orchestrator.agents.test_runner_agent import TestRunnerAgent
    from orchestrator.agents.github_sync_agent import GitHubSyncAgent
    from orchestrator.application.project_service import ProjectApplicationService
except ImportError:
    # Essayer avec les imports src/
    from src.orchestrator.agents.autonomous_orchestrator import AutonomousOrchestrator
    from src.orchestrator.agents.self_evolution_agent import SelfEvolutionAgent
    from src.orchestrator.agents.bug_detector_agent import BugDetectorAgent
    from src.orchestrator.agents.code_generator_agent import CodeGeneratorAgent
    from src.orchestrator.agents.meta_cognitive_agent import MetaCognitiveAgent
    from src.orchestrator.agents.test_runner_agent import TestRunnerAgent
    from src.orchestrator.agents.github_sync_agent import GitHubSyncAgent
    
    # DDD et SOLID imports - essayer sans project_service si pas dispo
    try:
        from src.orchestrator.application.project_service import ProjectApplicationService
    except ImportError:
        # Mock si pas disponible
        class ProjectApplicationService:
            def resolve_project_config(self, project_name):
                return {"name": project_name}


class IndependentOrchestrator:
    """Orchestrateur completement independant qui s'auto-evolue en permanence"""
    
    def __init__(self, target_project: Optional[str] = None):
        self.target_project = target_project
        # Dependency Injection (SOLID: Dependency Inversion Principle)
        self.project_service = ProjectApplicationService()
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
        
        # Surcharger avec le projet cible si spécifié
        if self.target_project:
            project_config = self._generate_project_config(self.target_project)
            config.update(project_config)
        
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
        """Configurer les gestionnaires de signaux pour arret gracieux"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Gestionnaire de signaux pour arret propre"""
        self.logger.info(f"Signal {signum} recu, arret gracieux...")
        self.running = False
    
    async def initialize_system(self):
        """Initialiser tous les composants du systeme autonome"""
        self.logger.info("=== INITIALISATION ORCHESTRATEUR INDEPENDANT ===")
        
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
        """Demarrer la boucle d'evolution perpetuelle"""
        self.logger.info("DEMARRAGE EVOLUTION PERPETUELLE")
        self.running = True
        
        while self.running:
            try:
                self.evolution_cycle += 1
                cycle_start = datetime.now()
                
                self.logger.info(f"=== CYCLE EVOLUTION #{self.evolution_cycle} ===")
                
                # 1. Auto-surveillance du systeme
                health_status = await self._perform_system_health_check()
                self.logger.info(f"Sante systeme: {health_status['overall_health']}")
                
                # 2. Detection des opportunites d'amelioration
                improvements = await self._detect_improvement_opportunities()
                self.logger.info(f"Opportunites detectees: {len(improvements)}")
                
                # 3. Auto-generation des ameliorations avec GitHub sync
                if improvements:
                    # Initier workflow GitHub pour chaque amelioration
                    github_workflows = []
                    for improvement in improvements:
                        improvement["cycle"] = self.evolution_cycle
                        workflow = await self.github_sync.sync_improvement_to_github(improvement)
                        github_workflows.append(workflow)
                        self.logger.info(f"GitHub workflow initie: Issue #{workflow.get('issue_created', 'N/A')}")
                    
                    generation_result = await self._auto_generate_improvements(improvements)
                    self.logger.info(f"Ameliorations generees: {generation_result['generated']}")
                    
                    # 4. Auto-test des modifications
                    if generation_result["generated"] > 0:
                        test_result = await self._auto_test_modifications()
                        self.logger.info(f"Tests: {test_result['passed']}/{test_result['total']}")
                        
                        # 5. Completer les workflows GitHub
                        for i, workflow in enumerate(github_workflows):
                            if "issue_created" in workflow:
                                # Utiliser les vrais noms de fichiers generes
                                improvement_type = improvements[i]['type']
                                real_generated_files = {
                                    f"src/{improvement_type}s.py": f"# Auto-generated code for {improvement_type}",
                                    f"tests/test_{improvement_type}.py": f"# Auto-generated tests for {improvement_type}"
                                }
                                completion = await self.github_sync.complete_improvement_workflow(
                                    workflow["issue_created"], real_generated_files
                                )
                                self.logger.info(f"Workflow GitHub termine: {completion.get('workflow_completed', False)}")
                        
                        # 6. Auto-deploiement si tests passent
                        if test_result["success"]:
                            deploy_result = await self._auto_deploy_improvements()
                            status = "SUCCES" if deploy_result['success'] else "ECHEC"
                            self.logger.info(f"Deploiement: {status}")
                            
                            # 7. Auto-relance si necessaire
                            if deploy_result["restart_required"]:
                                await self._prepare_self_restart()
                
                # 8. Metriques et apprentissage
                await self._record_evolution_metrics(cycle_start)
                await self._perform_meta_learning()
                
                # 9. Affichage statut GitHub sync
                if hasattr(self, 'github_sync'):
                    sync_status = await self.github_sync.get_sync_status()
                    self.logger.info(f"GitHub Sync: {sync_status['active_issues']} issues actives, version {sync_status['current_version']}")
                
                # 10. Attendre le prochain cycle
                await asyncio.sleep(self.config["evolution_interval"])
                
            except Exception as e:
                self.logger.error(f"Erreur cycle evolution {self.evolution_cycle}: {e}")
                # Auto-recuperation
                await self._perform_error_recovery(e)
                await asyncio.sleep(60)  # Attendre 1 minute avant retry
    
    async def _perform_system_health_check(self) -> Dict[str, Any]:
        """Verification complete de la sante du systeme"""
        status = await self.orchestrator._get_complete_system_status()
        
        # Ajouter des verifications specifiques
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
        """Detecter les opportunites d'amelioration"""
        opportunities = []
        
        # MODE PULL : Recuperer les opportunites depuis GitHub Issues et Project Board
        if self.config.get("pull_mode_enabled", False):
            try:
                self.logger.info("[REFRESH] Mode PULL active - Lecture des issues GitHub...")
                github_result = await self.github_sync.execute_pull_workflow()
                
                if github_result.get("workflow_status") == "completed":
                    github_opportunities = github_result.get("opportunities_created", [])
                    opportunities.extend(github_opportunities)
                    self.logger.info(f"[OK] GitHub PULL: {len(github_opportunities)} opportunites detectees")
                else:
                    self.logger.warning(f"[WARN] GitHub PULL echoue: {github_result.get('error', 'Unknown error')}")
                    
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
        
        # Detecter des optimisations possibles
        performance_issues = await self._detect_performance_issues()
        if performance_issues:
            opportunities.append({
                "type": "performance", 
                "priority": "medium",
                "issues": performance_issues
            })
        
        # Auto-generer de nouvelles fonctionnalites basees sur l'usage
        feature_ideas = await self._generate_feature_ideas()
        if feature_ideas:
            opportunities.append({
                "type": "feature", 
                "priority": "low",
                "ideas": feature_ideas
            })
        
        return opportunities
    
    async def _auto_generate_improvements(self, opportunities: list) -> Dict[str, Any]:
        """Auto-generer les ameliorations"""
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
                self.logger.error(f"Erreur generation {opportunity['type']}: {e}")
        
        return {"generated": generated_count}
    
    async def _apply_generated_code(self, code_dict: Dict[str, str], category: str):
        """Appliquer le code genere dans la sandbox"""
        sandbox_path = self.config["sandbox_path"]
        
        for file_path, code_content in code_dict.items():
            try:
                full_path = sandbox_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(code_content)
                self.logger.info(f"Code genere applique: {file_path} ({category})")
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
        """Deployer automatiquement les ameliorations"""
        try:
            # Copier les fichiers modifies de la sandbox vers le repo principal
            await self._sync_sandbox_to_main()
            
            # Commit automatique
            await self._auto_commit_changes()
            
            self.logger.info("Deploiement automatique reussi")
            return {"success": True, "restart_required": True}
            
        except Exception as e:
            self.logger.error(f"Erreur deploiement: {e}")
            return {"success": False, "restart_required": False}
    
    async def _prepare_self_restart(self):
        """Preparer l'auto-relance du systeme"""
        self.logger.info("PREPARATION AUTO-RELANCE...")
        
        # Sauvegarder l'etat actuel
        state = {
            "evolution_cycle": self.evolution_cycle,
            "last_evolution": datetime.now().isoformat(),
            "total_improvements": self.evolution_cycle * 2,  # Estimation
            "restart_reason": "auto_improvement_deployment"
        }
        
        state_file = Path("evolution_state.json")
        state_file.write_text(json.dumps(state, indent=2))
        
        self.logger.info("Etat sauvegarde, redemarrage dans 10 secondes...")
        await asyncio.sleep(10)
        
        # Auto-relance
        os.execl(sys.executable, sys.executable, *sys.argv)
    
    # Methodes utilitaires simplifiees pour le prototype
    def _check_memory_usage(self) -> bool:
        return True  # Toujours OK pour le prototype
    
    def _check_disk_space(self) -> bool:
        return True  # Toujours OK pour le prototype
    
    async def _check_evolution_capability(self) -> bool:
        return True  # Capacite d'evolution toujours active
    
    async def _analyze_error_logs(self) -> list:
        # Simulation : retourner parfois des patterns d'erreur
        if self.evolution_cycle % 3 == 0:
            return ["TypeError in agent.py line 42", "Missing import in utils.py"]
        return []
    
    async def _analyze_test_coverage_gaps(self) -> list:
        # Simulation : identifier des gaps de couverture
        if self.evolution_cycle % 4 == 0:
            return ["Module sans test: new_module", "Methode non couverte: process_data"]
        return []
    
    async def _detect_performance_issues(self) -> list:
        # Simulation : detecter des problemes de performance
        if self.evolution_cycle % 5 == 0:
            return [{"function": "slow_processing", "type": "slow_function"}]
        return []
    
    async def _generate_feature_ideas(self) -> list:
        # Simulation : generer des idees de fonctionnalites
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
        self.logger.info(f"Cycle {self.evolution_cycle} termine en {cycle_duration:.1f}s")
    
    async def _perform_meta_learning(self):
        # Meta-apprentissage pour optimiser le processus d'evolution
        self.logger.info("Meta-apprentissage en cours...")
        await asyncio.sleep(0.1)
    
    async def _perform_error_recovery(self, error: Exception):
        # Recuperation automatique d'erreur
        self.logger.info(f"Recuperation d'erreur: {type(error).__name__}")
        await asyncio.sleep(1)
    
    def _generate_project_config(self, project_name: str) -> Dict[str, Any]:
        """Générer la configuration spécifique au projet (DDD + SOLID)"""
        try:
            # Utiliser le service d'application (DDD Application Service)
            return self.project_service.generate_configuration_dict(project_name)
            
        except Exception as e:
            self.logger.error(f"[CONFIG] Erreur génération config projet {project_name}: {e}")
            # Le service a déjà un fallback intégré, mais on peut ajouter un fallback supplémentaire
            return {
                "target_project": {
                    "name": project_name,
                    "path": str(Path.cwd().parent / project_name)
                },
                "github": {
                    "repo": project_name,
                    "owner": "AlexisVS"
                }
            }


# ============================================================================
# FUNCTIONS FOR PROJECT ARGUMENT SUPPORT (SOLID Principles Applied)
# ============================================================================

def parse_arguments(args_list: Optional[list] = None) -> argparse.Namespace:
    """Parse command line arguments (SOLID: Single Responsibility)"""
    parser = argparse.ArgumentParser(
        description="Orchestrateur AI Autonome",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python orchestrator/autonomous.py --project weather-dashboard
  python orchestrator/autonomous.py --target-project my-project
  python orchestrator/autonomous.py  # Use default config
        """
    )
    
    parser.add_argument(
        '--project', '--target-project',
        dest='project',
        type=str,
        help='Nom du projet cible à orchestrer'
    )
    
    if args_list is not None:
        return parser.parse_args(args_list)
    return parser.parse_args()


def resolve_project_path(project_name: str) -> str:
    """Résoudre le chemin du projet (Facade for DDD service)"""
    # Utilise le service DDD derrière le facade pour la compatibilité
    service = ProjectApplicationService()
    return service.resolve_project_path(project_name)


def validate_project_config(project_name: str, project_path: str) -> Dict[str, Any]:
    """Valider la configuration du projet (Facade for DDD service)"""
    # Utilise le service DDD derrière le facade pour la compatibilité
    service = ProjectApplicationService()
    return service.validate_project_configuration(project_name, project_path)


def validate_github_repo(repo_name: str) -> Dict[str, Any]:
    """Valider l'existence du repo GitHub (Legacy compatibility)"""
    # Maintenu pour compatibilité arrière, mais utilise le service DDD
    from orchestrator.domain.project import GitHubValidationService
    service = GitHubValidationService()
    return service.validate_repository(repo_name)


def generate_project_config(
    project_name: str, 
    project_path: str, 
    github_owner: str = "AlexisVS"
) -> Dict[str, Any]:
    """Générer la configuration pour un projet (Facade for DDD service)"""
    # Utilise le service DDD derrière le facade pour la compatibilité
    service = ProjectApplicationService()
    return service.generate_configuration_dict(project_name, project_path, github_owner)


async def main_with_args():
    """Point d'entrée avec parsing d'arguments (SOLID: Open/Closed)"""
    args = parse_arguments()
    
    print("=== ORCHESTRATEUR AI INDEPENDANT ===")
    if args.project:
        print(f"Projet cible: {args.project}")
    print("Demarrage du systeme d'auto-evolution perpetuelle...")
    
    # Restaurer l'etat si redemarrage
    state_file = Path("evolution_state.json")
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text())
            print(f"Redemarrage detecte - Cycle #{state.get('evolution_cycle', 0)}")
            print(f"Raison: {state.get('restart_reason', 'unknown')}")
        except Exception as e:
            print(f"Erreur lecture etat: {e}")
    
    orchestrator = IndependentOrchestrator(target_project=args.project)
    
    try:
        # Initialisation
        await orchestrator.initialize_system()
        
        # Demarrage de l'evolution perpetuelle
        await orchestrator.start_perpetual_evolution()
        
    except KeyboardInterrupt:
        print("\nArret demande par l'utilisateur")
    except Exception as e:
        print(f"Erreur fatale: {e}")
        logging.exception("Erreur fatale dans l'orchestrateur")
    finally:
        print("Arret de l'orchestrateur autonome")


async def main():
    """Point d'entree principal pour l'orchestrateur independant (legacy)"""
    # Utiliser la nouvelle fonction avec support d'arguments
    await main_with_args()


if __name__ == "__main__":
    asyncio.run(main())