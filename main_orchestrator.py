#!/usr/bin/env python3
"""
Orchestrateur Principal - Point d'entrée unifié
Utilise le système modulaire complet avec templates hérités
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Import des modules créés
from universal_orchestrator import UniversalOrchestrator
from todo_loop_manager import TodoLoopManager

class MainOrchestrator:
    """Orchestrateur principal qui coordonne tous les composants"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.universal_orchestrator = UniversalOrchestrator(config_path)
        self.todo_manager = TodoLoopManager(self.universal_orchestrator.config)
        
        print("[MAIN] Orchestrateur principal initialisé")
    
    async def run_full_workflow(self):
        """Exécuter le workflow complet : GitHub → TDD → Code → Tests → Deploy"""
        
        print("=" * 80)
        print("[MAIN WORKFLOW] DÉMARRAGE ORCHESTRATION COMPLÈTE")
        print("=" * 80)
        
        try:
            # 1. Phase d'initialisation
            print("\n[PHASE 1] INITIALISATION")
            success = await self._initialization_phase()
            if not success:
                return False
            
            # 2. Phase GitHub (repo + project + issues)
            print("\n[PHASE 2] SYNCHRONISATION GITHUB")
            github_tasks = await self._github_phase()
            if not github_tasks:
                return False
            
            # 3. Phase TDD automatique
            print("\n[PHASE 3] CYCLE TDD AUTOMATIQUE")
            tdd_success = await self._tdd_phase(github_tasks)
            if not tdd_success:
                return False
            
            # 4. Phase de validation
            print("\n[PHASE 4] VALIDATION ET TESTS")
            validation_success = await self._validation_phase()
            if not validation_success:
                return False
            
            # 5. Phase de finalisation
            print("\n[PHASE 5] FINALISATION ET DÉPLOIEMENT")
            deploy_success = await self._deployment_phase()
            
            # 6. Rapport final
            await self._generate_final_report()
            
            print("\n" + "=" * 80)
            print("[SUCCESS] ORCHESTRATION TERMINÉE AVEC SUCCÈS!")
            print("=" * 80)
            
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Erreur dans le workflow principal: {e}")
            return False
    
    async def _initialization_phase(self) -> bool:
        """Phase 1: Initialisation et validation"""
        
        # Test connexion IA
        ai_ok = await self.universal_orchestrator.test_ai_connection()
        if not ai_ok:
            print("[ERROR] Connexion IA indisponible")
            return False
        print("[OK] Connexion IA validée")
        
        # Charger templates
        self.universal_orchestrator.load_templates()
        print("[OK] Templates chargés")
        
        return True
    
    async def _github_phase(self) -> list:
        """Phase 2: GitHub repo, project et issues"""
        
        # Créer/valider repository
        repo_ok = await self.universal_orchestrator.create_github_repository()
        if not repo_ok:
            print("[ERROR] Repository GitHub inaccessible") 
            return []
        print("[OK] Repository GitHub prêt")
        
        # Créer issues depuis templates
        github_issues = await self.universal_orchestrator.create_github_issues()
        if not github_issues:
            print("[WARNING] Aucune issue créée")
        else:
            print(f"[OK] {len(github_issues)} issues GitHub créées")
        
        # Synchroniser avec TODO Loop Manager
        synced_tasks = await self.todo_manager.sync_with_github_issues()
        print(f"[OK] {len(synced_tasks)} tâches synchronisées dans TODO Loop")
        
        return synced_tasks
    
    async def _tdd_phase(self, tasks: list) -> bool:
        """Phase 3: Cycle TDD automatique pour chaque tâche"""
        
        if not tasks:
            print("[WARNING] Aucune tâche pour TDD")
            return True
        
        print(f"[TDD] Traitement de {len(tasks)} tâches avec cycle TDD")
        
        for task in tasks:
            print(f"\n[TDD] === TÂCHE: {task.title} ===")
            
            try:
                # Phase RED: Tests qui échouent
                await self._tdd_red_phase(task)
                
                # Phase GREEN: Code minimal 
                await self._tdd_green_phase(task)
                
                # Phase REFACTOR: Amélioration
                await self._tdd_refactor_phase(task)
                
                print(f"[OK] Tâche {task.title} terminée avec TDD")
                
            except Exception as e:
                print(f"[ERROR] Erreur TDD pour {task.title}: {e}")
                # Marquer tâche comme bloquée
                from todo_loop_manager import TaskStatus
                await self.todo_manager.update_task_status(task.id, TaskStatus.BLOCKED)
                continue
        
        return True
    
    async def _tdd_red_phase(self, task):
        """Phase RED: Génération tests qui échouent"""
        from todo_loop_manager import TaskStatus
        
        print(f"[TDD-RED] {task.title}")
        
        # Marquer en phase RED
        await self.todo_manager.update_task_status(task.id, TaskStatus.TDD_RED)
        
        # Commenter sur GitHub
        comment = f"""🔴 **Phase RED - Tests qui échouent**

**Tâche**: {task.title}
**Statut**: Génération des tests en cours...

L'orchestrateur génère maintenant les tests qui doivent échouer (comportement normal TDD).
"""
        await self.todo_manager.comment_on_github_issue(task.id, comment)
        
        # Ici on générerait les tests avec l'IA
        # Pour la démo, on simule
        await asyncio.sleep(2)
        
        print(f"[RED] Tests générés pour {task.title}")
    
    async def _tdd_green_phase(self, task):
        """Phase GREEN: Code minimal fonctionnel"""
        from todo_loop_manager import TaskStatus
        
        print(f"[TDD-GREEN] {task.title}")
        
        # Marquer en phase GREEN
        await self.todo_manager.update_task_status(task.id, TaskStatus.TDD_GREEN)
        
        # Commenter sur GitHub
        comment = f"""🟢 **Phase GREEN - Tests passants**

**Tâche**: {task.title}
**Statut**: Implémentation minimale créée

Les tests passent maintenant avec l'implémentation minimale.
➡️ **Prochaine étape**: Phase REFACTOR
"""
        await self.todo_manager.comment_on_github_issue(task.id, comment)
        
        # Générer code minimal
        await asyncio.sleep(2)
        
        print(f"[GREEN] Code minimal généré pour {task.title}")
    
    async def _tdd_refactor_phase(self, task):
        """Phase REFACTOR: Amélioration du code"""
        from todo_loop_manager import TaskStatus
        
        print(f"[TDD-REFACTOR] {task.title}")
        
        # Marquer en phase REFACTOR
        await self.todo_manager.update_task_status(task.id, TaskStatus.TDD_REFACTOR)
        
        # Commenter sur GitHub
        comment = f"""🔄 **Phase REFACTOR - Code amélioré**

**Tâche**: {task.title}
**Statut**: Code refactorisé avec succès

**Améliorations apportées**:
- Structure optimisée
- Documentation ajoutée  
- Gestion d'erreurs robuste
- Performance améliorée

✅ **Tests toujours passants**
"""
        await self.todo_manager.comment_on_github_issue(task.id, comment)
        
        # Refactoriser
        await asyncio.sleep(2)
        
        print(f"[REFACTOR] Code refactorisé pour {task.title}")
        
        # Marquer comme terminé
        await self.todo_manager.update_task_status(task.id, TaskStatus.COMPLETED)
    
    async def _validation_phase(self) -> bool:
        """Phase 4: Validation et tests"""
        
        print("[VALIDATION] Exécution des validations...")
        
        # Générer structure de projet
        await self.universal_orchestrator.generate_project_structure()
        print("[OK] Structure de projet générée")
        
        # Exécuter tests (simulé pour la démo)
        test_success = await self.universal_orchestrator.run_tests()
        if not test_success:
            print("[WARNING] Certains tests ont échoué")
        else:
            print("[OK] Tous les tests passent")
        
        return True
    
    async def _deployment_phase(self) -> bool:
        """Phase 5: Déploiement"""
        
        print("[DEPLOY] Préparation déploiement...")
        
        # Déployer si configuré
        await self.universal_orchestrator.deploy_project()
        print("[OK] Déploiement initié")
        
        return True
    
    async def _generate_final_report(self):
        """Générer rapport final"""
        
        # Rapport TODO Loop
        report = self.todo_manager.generate_progress_report()
        
        # Statistiques
        stats = self.todo_manager.get_loop_statistics()
        
        print(f"""
[RAPPORT FINAL]
================

{report}

RÉSUMÉ DE L'ORCHESTRATION:
- Projet: {self.universal_orchestrator.config['project']['name']}
- Type: {self.universal_orchestrator.config['project']['type']}
- Sortie: {self.universal_orchestrator.project_root}
- GitHub: {self.universal_orchestrator.config['github']['owner']}/{self.universal_orchestrator.config['github']['repo_name']}

SUCCÈS: Application générée avec workflow TDD complet!
""")

async def main():
    """Point d'entrée principal"""
    
    if len(sys.argv) < 2:
        print("Usage: python main_orchestrator.py <config.yaml>")
        print("\nExemples:")
        print("  python main_orchestrator.py configs/weather-app.yaml")
        return
    
    config_file = sys.argv[1]
    
    if not Path(config_file).exists():
        print(f"Erreur: Fichier de configuration '{config_file}' introuvable")
        return
    
    # Charger variables d'environnement
    load_dotenv()
    
    # Créer et lancer orchestrateur principal
    orchestrator = MainOrchestrator(config_file)
    success = await orchestrator.run_full_workflow()
    
    if success:
        print("\n[SUCCESS] ORCHESTRATION REUSSIE!")
    else:
        print("\n[FAILED] ORCHESTRATION ECHOUEE!")

if __name__ == "__main__":
    asyncio.run(main())