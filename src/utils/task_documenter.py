#!/usr/bin/env python3
"""
Task Documenter - Documentation automatique des micro-tâches
Commente automatiquement chaque action sur GitHub
"""

import asyncio
import time
from typing import Dict, Any, Optional
import httpx

class TaskDocumenter:
    """Système de documentation automatique des tâches"""
    
    def __init__(self, github_config: Dict[str, str]):
        self.github_headers = {
            "Authorization": f"Bearer {github_config['token']}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.owner = github_config['owner']
        self.repo_name = github_config['repo_name']
        
    async def document_task_completion(self, task_title: str, details: str, issue_number: Optional[int] = None):
        """Documenter l'achèvement d'une tâche"""
        print(f"[DOC] Documentation tache: {task_title}")
        
        # 1. Commenter sur une issue spécifique si fournie
        if issue_number:
            await self._comment_on_issue(issue_number, f"🤖 **Task Completed**: {task_title}\n\n{details}")
        
        # 2. Créer/mettre à jour un fichier de log dans le repo
        await self._update_task_log(task_title, details)
        
        # 3. Créer un commit de documentation
        await self._create_documentation_commit(task_title, details)
    
    async def _comment_on_issue(self, issue_number: int, comment: str):
        """Commenter sur une issue GitHub"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.github.com/repos/{self.owner}/{self.repo_name}/issues/{issue_number}/comments",
                    headers=self.github_headers,
                    json={"body": comment}
                )
                
                if response.status_code == 201:
                    print(f"[DOC] Commentaire ajoute a issue #{issue_number}")
                else:
                    print(f"[DOC-ERROR] Erreur commentaire: {response.status_code}")
                    
        except Exception as e:
            print(f"[DOC-ERROR] Erreur comment issue: {e}")
    
    async def _update_task_log(self, task_title: str, details: str):
        """Mettre à jour le fichier de log des tâches"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"""
## {timestamp} - {task_title}

{details}

---
"""
        
        # Pour l'instant, juste afficher le log
        # Dans une vraie implémentation, on pourrait l'envoyer via l'API GitHub
        print(f"[DOC-LOG] {log_entry}")
    
    async def _create_documentation_commit(self, task_title: str, details: str):
        """Créer un commit de documentation (optionnel)"""
        # Cette fonctionnalité pourrait être implémentée pour commiter
        # automatiquement la documentation des tâches
        pass

class AutoDocumentedTask:
    """Décorateur pour auto-documenter les tâches"""
    
    def __init__(self, documenter: TaskDocumenter, task_name: str):
        self.documenter = documenter
        self.task_name = task_name
    
    def __call__(self, func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Documenter le succès
                duration = time.time() - start_time
                await self.documenter.document_task_completion(
                    self.task_name,
                    f"✅ Tâche complétée avec succès\n⏱️ Durée: {duration:.2f}s"
                )
                
                return result
                
            except Exception as e:
                # Documenter l'erreur
                duration = time.time() - start_time
                await self.documenter.document_task_completion(
                    f"❌ ERREUR - {self.task_name}",
                    f"❌ Erreur lors de l'exécution\n"
                    f"🐛 Message: {str(e)}\n"
                    f"⏱️ Durée avant erreur: {duration:.2f}s"
                )
                raise
        
        return wrapper