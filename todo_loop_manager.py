#!/usr/bin/env python3
"""
TODO Loop Manager - Gestion intelligente des tâches avec templates
Intégration GitHub Issues → TDD Phases → Validation → Completion
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum
import httpx
from dataclasses import dataclass, asdict

class TaskStatus(Enum):
    """États possibles d'une tâche"""
    TODO = "todo"
    IN_PROGRESS = "in_progress" 
    TDD_RED = "tdd_red"
    TDD_GREEN = "tdd_green"
    TDD_REFACTOR = "tdd_refactor"
    TESTING = "testing"
    VALIDATION = "validation"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"

class Priority(Enum):
    """Priorités des tâches"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class Task:
    """Structure d'une tâche dans la TODO loop"""
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: Priority
    github_issue_number: Optional[int] = None
    github_labels: List[str] = None
    dependencies: List[str] = None
    tdd_phase: Optional[str] = None
    test_files: List[str] = None
    implementation_files: List[str] = None
    validation_results: Dict[str, Any] = None
    created_at: float = 0.0
    updated_at: float = 0.0
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    
    def __post_init__(self):
        if self.github_labels is None:
            self.github_labels = []
        if self.dependencies is None:
            self.dependencies = []
        if self.test_files is None:
            self.test_files = []
        if self.implementation_files is None:
            self.implementation_files = []
        if self.validation_results is None:
            self.validation_results = {}
        if self.created_at == 0.0:
            self.created_at = time.time()
        if self.updated_at == 0.0:
            self.updated_at = time.time()

class TodoLoopManager:
    """Gestionnaire de la boucle TODO avec intégration GitHub et TDD"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tasks: Dict[str, Task] = {}
        self.github_headers = {
            "Authorization": f"Bearer {config['github']['token']}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.loop_state_file = Path("todo_loop_state.json")
        self.load_state()
        
        print(f"[TODO-LOOP] Gestionnaire initialisé")
        print(f"[TODO-LOOP] {len(self.tasks)} tâches chargées")
    
    def save_state(self):
        """Sauvegarder l'état de la TODO loop"""
        state = {
            "tasks": {
                task_id: asdict(task) for task_id, task in self.tasks.items()
            },
            "last_updated": time.time()
        }
        
        with open(self.loop_state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, default=str)
    
    def load_state(self):
        """Charger l'état sauvegardé de la TODO loop"""
        if not self.loop_state_file.exists():
            return
            
        try:
            with open(self.loop_state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
                
            for task_id, task_data in state.get('tasks', {}).items():
                # Reconstituer les enums
                task_data['status'] = TaskStatus(task_data['status'])
                task_data['priority'] = Priority(task_data['priority'])
                
                # Créer l'objet Task
                self.tasks[task_id] = Task(**task_data)
                
            print(f"[TODO-LOOP] État rechargé: {len(self.tasks)} tâches")
            
        except Exception as e:
            print(f"[ERROR] Erreur chargement état: {e}")
    
    async def sync_with_github_issues(self) -> List[Task]:
        """Synchroniser avec les issues GitHub"""
        print("[SYNC] Synchronisation avec GitHub Issues...")
        
        try:
            async with httpx.AsyncClient() as client:
                # Récupérer toutes les issues ouvertes
                response = await client.get(
                    f"https://api.github.com/repos/{self.config['github']['owner']}/{self.config['github']['repo_name']}/issues",
                    headers=self.github_headers,
                    params={"state": "open"}
                )
                
                if response.status_code != 200:
                    print(f"[ERROR] Erreur GitHub API: {response.status_code}")
                    return []
                
                github_issues = response.json()
                synced_tasks = []
                
                for issue in github_issues:
                    task_id = f"github_{issue['number']}"
                    
                    # Déterminer statut basé sur les labels
                    status = self._determine_status_from_labels(issue.get('labels', []))
                    priority = self._determine_priority_from_labels(issue.get('labels', []))
                    
                    if task_id in self.tasks:
                        # Mettre à jour tâche existante
                        task = self.tasks[task_id]
                        task.title = issue['title']
                        task.description = issue['body'] or ""
                        task.status = status
                        task.priority = priority
                        task.updated_at = time.time()
                    else:
                        # Créer nouvelle tâche
                        task = Task(
                            id=task_id,
                            title=issue['title'],
                            description=issue['body'] or "",
                            status=status,
                            priority=priority,
                            github_issue_number=issue['number'],
                            github_labels=[label['name'] for label in issue.get('labels', [])]
                        )
                        
                    self.tasks[task_id] = task
                    synced_tasks.append(task)
                    
                print(f"[SYNC] {len(synced_tasks)} tâches synchronisées")
                self.save_state()
                return synced_tasks
                
        except Exception as e:
            print(f"[ERROR] Erreur synchronisation GitHub: {e}")
            return []
    
    def _determine_status_from_labels(self, labels: List[Dict]) -> TaskStatus:
        """Déterminer le statut d'une tâche basé sur ses labels GitHub"""
        label_names = [label['name'] for label in labels]
        
        if 'tdd-red' in label_names:
            return TaskStatus.TDD_RED
        elif 'tdd-green' in label_names:
            return TaskStatus.TDD_GREEN
        elif 'tdd-refactor' in label_names:
            return TaskStatus.TDD_REFACTOR
        elif 'testing' in label_names:
            return TaskStatus.TESTING
        elif 'validation' in label_names:
            return TaskStatus.VALIDATION
        elif 'blocked' in label_names:
            return TaskStatus.BLOCKED
        elif 'in-progress' in label_names:
            return TaskStatus.IN_PROGRESS
        else:
            return TaskStatus.TODO
    
    def _determine_priority_from_labels(self, labels: List[Dict]) -> Priority:
        """Déterminer la priorité basée sur les labels"""
        label_names = [label['name'] for label in labels]
        
        if 'critical' in label_names or 'high-priority' in label_names:
            return Priority.HIGH
        elif 'medium-priority' in label_names:
            return Priority.MEDIUM
        elif 'low-priority' in label_names:
            return Priority.LOW
        else:
            return Priority.MEDIUM  # Par défaut
    
    def get_next_tasks(self, limit: int = 5) -> List[Task]:
        """Obtenir les prochaines tâches à traiter"""
        
        # Filtrer les tâches disponibles (pas bloquées, pas terminées)
        available_tasks = [
            task for task in self.tasks.values()
            if task.status not in [TaskStatus.COMPLETED, TaskStatus.BLOCKED, TaskStatus.FAILED]
        ]
        
        # Trier par priorité puis par date de création
        priority_order = {Priority.CRITICAL: 0, Priority.HIGH: 1, Priority.MEDIUM: 2, Priority.LOW: 3}
        
        available_tasks.sort(
            key=lambda t: (priority_order[t.priority], t.created_at)
        )
        
        # Vérifier les dépendances
        ready_tasks = []
        for task in available_tasks[:limit * 2]:  # Examiner plus de tâches pour tenir compte des dépendances
            if self._are_dependencies_satisfied(task):
                ready_tasks.append(task)
                if len(ready_tasks) >= limit:
                    break
        
        return ready_tasks
    
    def _are_dependencies_satisfied(self, task: Task) -> bool:
        """Vérifier si toutes les dépendances d'une tâche sont satisfaites"""
        for dep_id in task.dependencies:
            if dep_id in self.tasks:
                dep_task = self.tasks[dep_id]
                if dep_task.status != TaskStatus.COMPLETED:
                    return False
            else:
                # Dépendance non trouvée - considérée comme non satisfaite
                return False
        return True
    
    async def update_task_status(self, task_id: str, new_status: TaskStatus, 
                                 additional_data: Optional[Dict] = None):
        """Mettre à jour le statut d'une tâche"""
        if task_id not in self.tasks:
            print(f"[ERROR] Tâche {task_id} non trouvée")
            return
        
        task = self.tasks[task_id]
        old_status = task.status
        task.status = new_status
        task.updated_at = time.time()
        
        # Mettre à jour données additionnelles
        if additional_data:
            if 'test_files' in additional_data:
                task.test_files.extend(additional_data['test_files'])
            if 'implementation_files' in additional_data:
                task.implementation_files.extend(additional_data['implementation_files'])
            if 'validation_results' in additional_data:
                task.validation_results.update(additional_data['validation_results'])
        
        print(f"[UPDATE] Tâche {task_id}: {old_status.value} → {new_status.value}")
        
        # Synchroniser avec GitHub
        await self._update_github_issue_labels(task)
        
        # Sauvegarder
        self.save_state()
    
    async def _update_github_issue_labels(self, task: Task):
        """Mettre à jour les labels de l'issue GitHub correspondante"""
        if not task.github_issue_number:
            return
        
        # Mapping statut → label
        status_labels = {
            TaskStatus.TODO: ["todo"],
            TaskStatus.IN_PROGRESS: ["in-progress"],
            TaskStatus.TDD_RED: ["tdd-red", "in-progress"],
            TaskStatus.TDD_GREEN: ["tdd-green", "in-progress"],
            TaskStatus.TDD_REFACTOR: ["tdd-refactor", "in-progress"],
            TaskStatus.TESTING: ["testing", "in-progress"],
            TaskStatus.VALIDATION: ["validation", "in-progress"],
            TaskStatus.COMPLETED: ["completed"],
            TaskStatus.BLOCKED: ["blocked"],
            TaskStatus.FAILED: ["failed"]
        }
        
        new_labels = status_labels.get(task.status, [])
        
        # Conserver les labels existants qui ne sont pas liés au statut
        preserved_labels = [
            label for label in task.github_labels
            if label not in ['todo', 'in-progress', 'tdd-red', 'tdd-green', 
                           'tdd-refactor', 'testing', 'validation', 'completed', 
                           'blocked', 'failed']
        ]
        
        all_labels = preserved_labels + new_labels
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"https://api.github.com/repos/{self.config['github']['owner']}/{self.config['github']['repo_name']}/issues/{task.github_issue_number}",
                    headers=self.github_headers,
                    json={"labels": all_labels}
                )
                
                if response.status_code == 200:
                    task.github_labels = all_labels
                    print(f"[GITHUB] Labels mis à jour pour issue #{task.github_issue_number}")
                else:
                    print(f"[ERROR] Erreur mise à jour labels: {response.status_code}")
                    
        except Exception as e:
            print(f"[ERROR] Erreur GitHub labels: {e}")
    
    async def comment_on_github_issue(self, task_id: str, comment: str):
        """Ajouter un commentaire sur l'issue GitHub"""
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        if not task.github_issue_number:
            return
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.github.com/repos/{self.config['github']['owner']}/{self.config['github']['repo_name']}/issues/{task.github_issue_number}/comments",
                    headers=self.github_headers,
                    json={"body": comment}
                )
                
                if response.status_code == 201:
                    print(f"[GITHUB] Commentaire ajouté à issue #{task.github_issue_number}")
                else:
                    print(f"[ERROR] Erreur commentaire GitHub: {response.status_code}")
                    
        except Exception as e:
            print(f"[ERROR] Erreur commentaire: {e}")
    
    def get_loop_statistics(self) -> Dict[str, Any]:
        """Obtenir les statistiques de la TODO loop"""
        status_counts = {}
        priority_counts = {}
        
        for task in self.tasks.values():
            status_counts[task.status.value] = status_counts.get(task.status.value, 0) + 1
            priority_counts[task.priority.value] = priority_counts.get(task.priority.value, 0) + 1
        
        total_tasks = len(self.tasks)
        completed_tasks = status_counts.get(TaskStatus.COMPLETED.value, 0)
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": completion_rate,
            "status_distribution": status_counts,
            "priority_distribution": priority_counts,
            "blocked_tasks": status_counts.get(TaskStatus.BLOCKED.value, 0),
            "in_progress_tasks": sum(
                status_counts.get(status.value, 0) 
                for status in [TaskStatus.IN_PROGRESS, TaskStatus.TDD_RED, 
                              TaskStatus.TDD_GREEN, TaskStatus.TDD_REFACTOR]
            )
        }
    
    def generate_progress_report(self) -> str:
        """Générer un rapport de progression"""
        stats = self.get_loop_statistics()
        
        report = f"""
# Rapport de Progression TODO Loop

## Vue d'ensemble
- **Total des tâches**: {stats['total_tasks']}
- **Tâches terminées**: {stats['completed_tasks']}
- **Taux de completion**: {stats['completion_rate']:.1f}%
- **Tâches en cours**: {stats['in_progress_tasks']}
- **Tâches bloquées**: {stats['blocked_tasks']}

## Distribution par statut
"""
        
        for status, count in stats['status_distribution'].items():
            report += f"- **{status.replace('_', ' ').title()}**: {count}\n"
        
        report += "\n## Distribution par priorité\n"
        
        for priority, count in stats['priority_distribution'].items():
            report += f"- **{priority.title()}**: {count}\n"
        
        # Tâches suivantes
        next_tasks = self.get_next_tasks(3)
        if next_tasks:
            report += "\n## Prochaines tâches prioritaires\n"
            for i, task in enumerate(next_tasks, 1):
                report += f"{i}. **{task.title}** ({task.priority.value})\n"
        
        return report
    
    async def run_continuous_loop(self, interval_seconds: int = 300):
        """Exécuter la boucle TODO en continu"""
        print(f"[TODO-LOOP] Démarrage boucle continue (intervalle: {interval_seconds}s)")
        
        while True:
            try:
                # Synchroniser avec GitHub
                await self.sync_with_github_issues()
                
                # Traiter les tâches suivantes
                next_tasks = self.get_next_tasks(3)
                
                if next_tasks:
                    print(f"[TODO-LOOP] {len(next_tasks)} tâches à traiter")
                    for task in next_tasks:
                        print(f"  - {task.title} ({task.status.value})")
                else:
                    print("[TODO-LOOP] Aucune tâche à traiter")
                
                # Générer rapport de progression
                if len(self.tasks) > 0:
                    stats = self.get_loop_statistics()
                    print(f"[STATS] {stats['completed_tasks']}/{stats['total_tasks']} tâches terminées ({stats['completion_rate']:.1f}%)")
                
                # Attendre avant la prochaine itération
                await asyncio.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                print("[TODO-LOOP] Arrêt demandé")
                break
            except Exception as e:
                print(f"[ERROR] Erreur dans la boucle: {e}")
                await asyncio.sleep(60)  # Attente plus longue en cas d'erreur

async def main():
    """Point d'entrée pour test du TODO Loop Manager"""
    
    # Configuration de test
    config = {
        'github': {
            'token': 'your_token',
            'owner': 'your_owner', 
            'repo_name': 'your_repo'
        }
    }
    
    # Créer gestionnaire
    todo_manager = TodoLoopManager(config)
    
    # Test synchronisation
    tasks = await todo_manager.sync_with_github_issues()
    print(f"Tâches synchronisées: {len(tasks)}")
    
    # Générer rapport
    report = todo_manager.generate_progress_report()
    print(report)

if __name__ == "__main__":
    asyncio.run(main())