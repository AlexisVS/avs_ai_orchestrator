#!/usr/bin/env python3
"""
Orchestrateur Universel - Système générique modulaire pour tous les projets
Workflow: Config → GitHub → Templates → TDD → Code → Tests → Deploy
"""

import asyncio
import os
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import httpx
import yaml
from dotenv import load_dotenv

class UniversalOrchestrator:
    """Orchestrateur universel modulaire pour tous types de projets"""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.project_root = Path(self.config['project']['output_dir'])
        self.templates = {}
        self.ai_client_url = self.config['ai']['url']
        self.ai_model = self.config['ai']['model']
        
        # Créer dossier de sortie
        self.project_root.mkdir(exist_ok=True)
        
        print(f"[INIT] Orchestrateur universel initialise")
        print(f"[INIT] Projet: {self.config['project']['name']}")
        print(f"[INIT] Type: {self.config['project']['type']}")
        print(f"[INIT] Output: {self.project_root}")
    
    def load_config(self) -> Dict[str, Any]:
        """Charger configuration projet"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration non trouvee: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            if self.config_path.suffix == '.yaml':
                return yaml.safe_load(f)
            else:
                return json.load(f)
    
    def load_templates(self):
        """Charger templates pour le type de projet"""
        templates_dir = Path("templates") / self.config['project']['type']
        
        if not templates_dir.exists():
            print(f"[WARNING] Templates non trouves pour {self.config['project']['type']}")
            return
        
        for template_file in templates_dir.glob("*.yaml"):
            with open(template_file, 'r', encoding='utf-8') as f:
                template_name = template_file.stem
                self.templates[template_name] = yaml.safe_load(f)
                
        print(f"[TEMPLATES] {len(self.templates)} templates charges")
    
    async def test_ai_connection(self) -> bool:
        """Tester connexion IA"""
        try:
            data = {
                "model": self.ai_model,
                "messages": [{"role": "user", "content": "Test connection - reply 'OK'"}],
                "max_tokens": 10,
                "temperature": 0.1
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.ai_client_url, json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    return "OK" in content and "Error" not in content
                    
                return False
                
        except Exception as e:
            print(f"[ERROR] Test IA: {e}")
            return False
    
    async def call_ai(self, prompt: str, max_tokens: int = 1500) -> str:
        """Appel IA avec gestion d'erreur"""
        try:
            data = {
                "model": self.ai_model,
                "messages": [
                    {
                        "role": "system",
                        "content": self.config['ai']['system_prompt']
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": self.config['ai'].get('temperature', 0.3)
            }
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(self.ai_client_url, json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"].strip()
                    
                    # Validation contenu
                    if any(error in content.lower() for error in ["api error", "erreur", "error"]):
                        raise Exception("Contenu IA invalide")
                    
                    return content
                else:
                    raise Exception(f"Status HTTP: {response.status_code}")
                    
        except Exception as e:
            print(f"[ERROR] Appel IA: {e}")
            return self.get_fallback_content(prompt)
    
    def get_fallback_content(self, prompt: str) -> str:
        """Contenu de secours si IA échoue"""
        return f"// Contenu générique pour: {prompt[:100]}...\n// Template de secours utilisé"
    
    async def create_github_repository(self) -> bool:
        """Créer repository GitHub"""
        if not self.config.get('github', {}).get('auto_create', False):
            return True
            
        print("[GITHUB] Creation repository...")
        
        headers = {
            "Authorization": f"Bearer {self.config['github']['token']}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        data = {
            "name": self.config['github']['repo_name'],
            "description": self.config['project']['description'],
            "private": self.config['github'].get('private', False),
            "has_issues": True,
            "has_projects": True,
            "auto_init": True
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.github.com/user/repos",
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 201:
                    print("[OK] Repository GitHub cree")
                    return True
                elif response.status_code == 422:
                    print("[INFO] Repository existe deja")
                    return True
                else:
                    print(f"[ERROR] Erreur GitHub: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"[ERROR] Creation repo: {e}")
            return False
    
    async def create_github_issues(self) -> List[Dict]:
        """Créer issues GitHub à partir des templates"""
        if not self.config.get('github', {}).get('create_issues', False):
            return []
        
        print("[GITHUB] Creation des issues...")
        
        issues_template = self.templates.get('issues', {})
        if not issues_template:
            print("[WARNING] Pas de template d'issues")
            return []
        
        headers = {
            "Authorization": f"Bearer {self.config['github']['token']}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        created_issues = []
        
        for issue_config in issues_template.get('issues', []):
            # Remplacer variables dans le template
            title = issue_config['title'].format(**self.config['project'])
            body = issue_config['body'].format(**self.config['project'])
            
            issue_data = {
                "title": title,
                "body": body,
                "labels": issue_config.get('labels', [])
            }
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"https://api.github.com/repos/{self.config['github']['owner']}/{self.config['github']['repo_name']}/issues",
                        headers=headers,
                        json=issue_data
                    )
                    
                    if response.status_code == 201:
                        issue = response.json()
                        created_issues.append(issue)
                        print(f"[OK] Issue creee: {issue['title']}")
                    else:
                        print(f"[ERROR] Erreur issue: {response.status_code}")
                        
            except Exception as e:
                print(f"[ERROR] Creation issue: {e}")
        
        return created_issues
    
    async def generate_project_structure(self):
        """Générer structure complète du projet"""
        print("[STRUCTURE] Generation structure projet...")
        
        structure_template = self.templates.get('structure', {})
        if not structure_template:
            print("[WARNING] Pas de template de structure")
            return
        
        # Créer dossiers
        for folder in structure_template.get('folders', []):
            folder_path = self.project_root / folder
            folder_path.mkdir(parents=True, exist_ok=True)
            print(f"[FOLDER] {folder}")
        
        # Générer fichiers
        for file_config in structure_template.get('files', []):
            await self.generate_file(file_config)
    
    async def generate_file(self, file_config: Dict[str, Any]):
        """Générer un fichier avec IA ou template"""
        file_path = self.project_root / file_config['path']
        
        print(f"[FILE] Generation {file_config['path']}...")
        
        # Vérifier si template statique ou IA
        if 'template' in file_config:
            # Template statique
            content = file_config['template'].format(**self.config['project'])
        elif 'ai_prompt' in file_config:
            # Génération IA
            prompt = file_config['ai_prompt'].format(**self.config['project'])
            content = await self.call_ai(prompt, file_config.get('max_tokens', 1500))
        else:
            content = f"// Fichier généré: {file_config['path']}"
        
        # Nettoyer le contenu (supprimer balises markdown)
        if "```" in content:
            lines = content.split('\\n')
            in_code_block = False
            code_lines = []
            
            for line in lines:
                if line.strip().startswith('```'):
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    code_lines.append(line)
            
            if code_lines:
                content = '\\n'.join(code_lines)
        
        # Sauvegarder
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[OK] {file_config['path']} genere ({len(content)} chars)")
    
    async def run_tdd_cycle(self, issues: List[Dict]):
        """Cycle TDD pour chaque issue"""
        if not self.config.get('tdd', {}).get('enabled', False):
            return
        
        print("[TDD] Debut cycle TDD...")
        
        for issue in issues:
            await self.process_issue_tdd(issue)
    
    async def process_issue_tdd(self, issue: Dict):
        """Traiter une issue avec TDD"""
        print(f"[TDD] Issue: {issue['title']}")
        
        tdd_template = self.templates.get('tdd', {})
        if not tdd_template:
            return
        
        # Phase RED: Tests qui échouent
        if 'red_phase' in tdd_template:
            await self.run_tdd_phase('RED', tdd_template['red_phase'], issue)
        
        # Phase GREEN: Code minimal
        if 'green_phase' in tdd_template:
            await self.run_tdd_phase('GREEN', tdd_template['green_phase'], issue)
        
        # Phase REFACTOR: Amélioration
        if 'refactor_phase' in tdd_template:
            await self.run_tdd_phase('REFACTOR', tdd_template['refactor_phase'], issue)
    
    async def run_tdd_phase(self, phase: str, phase_config: Dict, issue: Dict):
        """Exécuter une phase TDD"""
        print(f"[TDD-{phase}] {issue['title']}")
        
        for file_config in phase_config.get('files', []):
            # Variables disponibles pour les templates
            context = {
                **self.config['project'],
                'issue_title': issue['title'],
                'issue_body': issue.get('body', ''),
                'phase': phase
            }
            
            file_config_expanded = {
                'path': file_config['path'].format(**context),
                'ai_prompt': file_config.get('ai_prompt', '').format(**context),
                'max_tokens': file_config.get('max_tokens', 1500)
            }
            
            await self.generate_file(file_config_expanded)
    
    async def run_tests(self) -> bool:
        """Exécuter les tests"""
        if not self.config.get('testing', {}).get('enabled', False):
            return True
        
        print("[TESTS] Execution des tests...")
        
        test_commands = self.config['testing'].get('commands', [])
        
        for command in test_commands:
            try:
                result = subprocess.run(
                    command.split(),
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    print(f"[OK] {command}")
                else:
                    print(f"[ERROR] {command}: {result.stderr}")
                    return False
                    
            except Exception as e:
                print(f"[ERROR] Test {command}: {e}")
                return False
        
        return True
    
    async def deploy_project(self):
        """Déployer le projet"""
        if not self.config.get('deploy', {}).get('enabled', False):
            return
        
        print("[DEPLOY] Deploiement...")
        
        deploy_commands = self.config['deploy'].get('commands', [])
        
        for command in deploy_commands:
            try:
                result = subprocess.run(
                    command.split(),
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=600
                )
                
                if result.returncode == 0:
                    print(f"[OK] Deploy: {command}")
                else:
                    print(f"[ERROR] Deploy {command}: {result.stderr}")
                    
            except Exception as e:
                print(f"[ERROR] Deploy {command}: {e}")
    
    async def orchestrate_full_workflow(self):
        """Workflow complet d'orchestration"""
        print("=" * 60)
        print("[ORCHESTRATOR] DEBUT WORKFLOW UNIVERSEL")
        print("=" * 60)
        
        try:
            # 1. Test connexion IA
            if not await self.test_ai_connection():
                print("[ERROR] Connexion IA defaillante")
                return False
            
            print("[OK] Connexion IA validee")
            
            # 2. Charger templates
            self.load_templates()
            
            # 3. Créer repository GitHub
            if not await self.create_github_repository():
                print("[ERROR] Creation repository echouee")
                return False
            
            # 4. Créer issues GitHub
            issues = await self.create_github_issues()
            
            # 5. Générer structure projet
            await self.generate_project_structure()
            
            # 6. Cycle TDD
            await self.run_tdd_cycle(issues)
            
            # 7. Exécuter tests
            if not await self.run_tests():
                print("[WARNING] Certains tests ont echoue")
            
            # 8. Déploiement
            await self.deploy_project()
            
            print("=" * 60)
            print("[SUCCESS] WORKFLOW COMPLET TERMINE")
            print("=" * 60)
            print(f"Projet: {self.config['project']['name']}")
            print(f"Type: {self.config['project']['type']}")
            print(f"Output: {self.project_root}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Workflow echoue: {e}")
            return False

async def main():
    """Point d'entrée principal"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python universal_orchestrator.py <config.yaml>")
        return
    
    config_path = sys.argv[1]
    
    orchestrator = UniversalOrchestrator(config_path)
    success = await orchestrator.orchestrate_full_workflow()
    
    if success:
        print("\\n[FINAL] Orchestration reussie!")
    else:
        print("\\n[FINAL] Orchestration echouee!")

if __name__ == "__main__":
    asyncio.run(main())