#!/usr/bin/env python3
"""
Card Tracker - Système de suivi des cards GitHub Project
Déplace automatiquement les cards entre les colonnes selon l'avancement TDD
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
import httpx

class CardTracker:
    """Système de suivi et déplacement des cards GitHub Project"""
    
    def __init__(self, github_config: Dict[str, str], project_id: int):
        self.github_headers = {
            "Authorization": f"Bearer {github_config['token']}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.owner = github_config['owner']
        self.repo_name = github_config['repo_name']
        self.project_id = project_id
        self.columns_cache = {}  # Cache des colonnes
        
        # Mapping des étapes TDD vers les colonnes
        self.tdd_phase_mapping = {
            "setup": "To Do",
            "tdd_red": "🔴 RED Phase", 
            "tdd_green": "🟢 GREEN Phase",
            "tdd_refactor": "🔄 REFACTOR Phase",
            "e2e_testing": "🧪 E2E Testing",
            "completed": "✅ Done",
            "blocked": "🚫 Blocked"
        }
    
    async def get_project_columns(self) -> Dict[str, Dict]:
        """Récupérer les colonnes du projet"""
        if self.columns_cache:
            return self.columns_cache
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.github.com/projects/{self.project_id}/columns",
                    headers=self.github_headers
                )
                
                if response.status_code == 200:
                    columns = response.json()
                    self.columns_cache = {col['name']: col for col in columns}
                    print(f"[TRACKER] {len(columns)} colonnes recuperees")
                    
                    # Afficher les colonnes disponibles
                    for col_name in self.columns_cache.keys():
                        print(f"  - {col_name}")
                    
                    return self.columns_cache
                else:
                    print(f"[TRACKER-ERROR] Erreur colonnes: {response.status_code}")
                    return {}
                    
        except Exception as e:
            print(f"[TRACKER-ERROR] Erreur get columns: {e}")
            return {}
    
    async def move_cards_to_phase(self, phase: str, task_description: str, details: str):
        """Déplacer toutes les cards actives vers une phase TDD"""
        print(f"[TRACKER] Deplacement cards vers phase: {phase}")
        
        # Récupérer les colonnes si nécessaire
        columns = await self.get_project_columns()
        if not columns:
            return
        
        # Déterminer la colonne cible
        target_column_name = self.tdd_phase_mapping.get(phase, "To Do")
        target_column = columns.get(target_column_name)
        
        if not target_column:
            print(f"[TRACKER-WARNING] Colonne '{target_column_name}' non trouvee")
            return
        
        # Récupérer toutes les cards du projet
        cards = await self._get_all_project_cards()
        
        # Déplacer les cards pertinentes
        moved_count = 0
        for card in cards:
            if await self._should_move_card(card, phase):
                success = await self._move_card_to_column(card, target_column)
                if success:
                    moved_count += 1
                    
                    # Commenter sur l'issue liée
                    await self._comment_on_card_issue(card, phase, task_description, details)
        
        print(f"[TRACKER] {moved_count} cards deplacees vers '{target_column_name}'")
    
    async def _get_all_project_cards(self) -> List[Dict]:
        """Récupérer toutes les cards du projet"""
        all_cards = []
        
        try:
            columns = await self.get_project_columns()
            
            async with httpx.AsyncClient() as client:
                for column in columns.values():
                    response = await client.get(
                        f"{column['url']}/cards",
                        headers=self.github_headers
                    )
                    
                    if response.status_code == 200:
                        cards = response.json()
                        all_cards.extend(cards)
                        
            return all_cards
            
        except Exception as e:
            print(f"[TRACKER-ERROR] Erreur get cards: {e}")
            return []
    
    async def _should_move_card(self, card: Dict, phase: str) -> bool:
        """Déterminer si une card doit être déplacée"""
        # Pour cette implémentation simplifiée, on déplace toutes les cards
        # qui ne sont pas dans "Done" ou "Blocked"
        
        # Récupérer la colonne actuelle de la card
        current_column = await self._get_card_column(card)
        if not current_column:
            return False
        
        # Ne pas déplacer les cards terminées ou bloquées
        if current_column['name'] in ['✅ Done', '🚫 Blocked']:
            return False
        
        return True
    
    async def _get_card_column(self, card: Dict) -> Optional[Dict]:
        """Récupérer la colonne d'une card"""
        try:
            card_url = card.get('url', '')
            if '/cards/' in card_url:
                column_url = card_url.rsplit('/cards/', 1)[0]
                
                columns = await self.get_project_columns()
                for column in columns.values():
                    if column['url'] == column_url:
                        return column
                        
        except Exception as e:
            print(f"[TRACKER-ERROR] Erreur get card column: {e}")
        
        return None
    
    async def _move_card_to_column(self, card: Dict, target_column: Dict) -> bool:
        """Déplacer une card vers une colonne"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    card['url'],
                    headers=self.github_headers,
                    json={
                        "position": "top",
                        "column_id": target_column['id']
                    }
                )
                
                if response.status_code == 200:
                    return True
                else:
                    print(f"[TRACKER-ERROR] Erreur move card: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"[TRACKER-ERROR] Erreur move: {e}")
            return False
    
    async def _comment_on_card_issue(self, card: Dict, phase: str, task_description: str, details: str):
        """Commenter sur l'issue liée à la card"""
        try:
            # Récupérer l'ID de l'issue liée
            content_url = card.get('content_url')
            if not content_url or '/issues/' not in content_url:
                return
            
            issue_number = content_url.split('/issues/')[-1]
            
            # Créer le commentaire selon la phase
            phase_emojis = {
                "setup": "🏗️",
                "tdd_red": "🔴", 
                "tdd_green": "🟢",
                "tdd_refactor": "🔄",
                "e2e_testing": "🧪",
                "completed": "✅",
                "blocked": "🚫"
            }
            
            emoji = phase_emojis.get(phase, "📋")
            
            comment = f"""{emoji} **Phase {phase.upper()}** - {task_description}

{details}

📍 **Card déplacée**: {self.tdd_phase_mapping.get(phase, 'Unknown')}
⏰ **Timestamp**: {time.strftime('%Y-%m-%d %H:%M:%S')}

🤖 Mise à jour automatique par Enhanced Orchestrator"""
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.github.com/repos/{self.owner}/{self.repo_name}/issues/{issue_number}/comments",
                    headers=self.github_headers,
                    json={"body": comment}
                )
                
                if response.status_code == 201:
                    print(f"[TRACKER] Commentaire ajoute a issue #{issue_number}")
                    
        except Exception as e:
            print(f"[TRACKER-ERROR] Erreur comment: {e}")