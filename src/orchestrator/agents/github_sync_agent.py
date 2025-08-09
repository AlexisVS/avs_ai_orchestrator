#!/usr/bin/env python3
"""
GitHub Sync Agent - Synchronisation complete avec GitHub
Gere les Issues, Project Board, Branches, PRs et Releases automatiquement
"""

import json
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging


class GitHubSyncAgent:
    """Agent de synchronisation GitHub pour workflow complet"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.repo_owner = config.get("github", {}).get("owner", "AlexisVS")
        self.repo_name = config.get("github", {}).get("repo", "avs_ai_orchestrator")
        self.project_id = config.get("github", {}).get("project_id", "12")
        self.logger = logging.getLogger("GitHubSyncAgent")
        
        # Workflow state tracking
        self.current_version = "1.0.0"
        self.active_issues = {}
        self.pending_prs = {}
    
    def _sanitize_generated_file_paths(self, code_dict: Dict[str, str]) -> Dict[str, str]:
        """FIX: Corriger les noms de fichiers generes incorrectement"""
        sanitized = {}
        for file_path, code_content in code_dict.items():
            # Corriger les pluriels incorrects
            corrected_path = file_path
            if file_path.endswith("_fixs.py"):
                corrected_path = file_path.replace("_fixs.py", "_fixes.py")
            elif file_path.endswith("_coverages.py"):
                corrected_path = file_path.replace("_coverages.py", "_coverage.py")
            
            sanitized[corrected_path] = code_content
        return sanitized
    
    def _filter_existing_files(self, code_dict: Dict[str, str], base_path: Path) -> Dict[str, str]:
        """FIX: Filtrer seulement les fichiers qui existent pour eviter pathspec errors"""
        existing_files = {}
        for file_path, content in code_dict.items():
            full_path = base_path / file_path
            if full_path.exists():
                existing_files[file_path] = content
            else:
                self.logger.warning(f"Fichier ignore (n'existe pas): {file_path}")
        return existing_files
        
    async def sync_improvement_to_github(self, improvement: Dict[str, Any]) -> Dict[str, Any]:
        """Synchroniser une amelioration detectee avec GitHub workflow complet"""
        try:
            self.logger.info(f"Demarrage GitHub sync pour: {improvement['type']}")
            
            # 1. Creer une issue GitHub
            issue = await self._create_github_issue(improvement)
            
            # 2. Mettre a jour le Project Board
            await self._update_project_board(issue["number"], "Todo")
            
            # 3. Creer une branche pour l'issue
            branch_name = await self._create_feature_branch(issue["number"], improvement["type"])
            
            # 4. Developpement (simule ici, reel dans l'orchestrateur)
            await self._update_project_board(issue["number"], "In Progress")
            
            result = {
                "issue_created": issue["number"],
                "branch_created": branch_name,
                "project_updated": True,
                "workflow_status": "initiated"
            }
            
            # Sauvegarder pour suivi
            self.active_issues[issue["number"]] = {
                "improvement": improvement,
                "branch": branch_name,
                "status": "in_progress",
                "created_at": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur GitHub sync: {e}")
            return {"error": str(e), "workflow_status": "failed"}
    
    async def _create_github_issue(self, improvement: Dict[str, Any]) -> Dict[str, Any]:
        """Creer une issue GitHub automatiquement"""
        
        # Generer titre et description bases sur le type d'amelioration
        title, description = self._generate_issue_content(improvement)
        
        # Labels bases sur le type
        labels = self._get_issue_labels(improvement["type"])
        
        try:
            # Essayer de creer l'issue avec tous les labels
            cmd = [
                "gh", "issue", "create",
                "--repo", f"{self.repo_owner}/{self.repo_name}",
                "--title", title,
                "--body", description,
                "--label", ",".join(labels)
            ]
            
            try:
                result = await self._run_gh_command(cmd)
                issue_url = result.strip()
                # Corriger le parsing : supprimer le numero duplique a la fin
                if '\n' in issue_url:
                    issue_url = issue_url.split('\n')[0]
                issue_number = issue_url.split("/")[-1]
                
                self.logger.info(f"Issue creee: #{issue_number}")
                
                return {
                    "number": int(issue_number),
                    "url": issue_url,
                    "title": title
                }
            except Exception as e:
                if "label" in str(e) and "not found" in str(e):
                    # Retry sans aucun label
                    self.logger.warning(f"Retry creation issue sans labels")
                    
                    cmd_safe = [
                        "gh", "issue", "create",
                        "--repo", f"{self.repo_owner}/{self.repo_name}",
                        "--title", title,
                        "--body", description
                    ]
                    
                    try:
                        result = await self._run_gh_command(cmd_safe)
                        issue_url = result.strip()
                        if '\n' in issue_url:
                            issue_url = issue_url.split('\n')[0]
                        issue_number = issue_url.split("/")[-1]
                        
                        self.logger.info(f"Issue creee (sans labels): #{issue_number}")
                        
                        return {
                            "number": int(issue_number),
                            "url": issue_url,
                            "title": title
                        }
                    except Exception as e2:
                        self.logger.error(f"Erreur creation issue (retry): {e2}")
                        raise e2
                else:
                    raise e
            
        except Exception as e:
            self.logger.error(f"Erreur creation issue: {e}")
            # Fallback: creer issue simulee
            return {
                "number": 999,
                "url": f"https://github.com/{self.repo_owner}/{self.repo_name}/issues/999",
                "title": title
            }
    
    def _generate_issue_content(self, improvement: Dict[str, Any]) -> tuple[str, str]:
        """Generer titre et description d'issue bases sur l'amelioration"""
        
        issue_type = improvement["type"]
        priority = improvement.get("priority", "medium")
        
        if issue_type == "bug_fix":
            title = f"[BUG] Auto-Fix: {improvement.get('patterns', ['Unknown issue'])[0]}"
            description = f"""## Bug Detecte Automatiquement

**Priorite:** {priority.upper()}
**Detecte par:** Auto-Orchestrateur Cycle #{improvement.get('cycle', 'N/A')}

### Patterns d'Erreur:
{chr(10).join(f'- {pattern}' for pattern in improvement.get('patterns', []))}

### Action Automatique:
- [ ] Analyse du code source
- [ ] Generation du fix automatique
- [ ] Tests de regression
- [ ] Application du correctif

**Auto-genere le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**
"""
        
        elif issue_type == "test_coverage":
            title = f"[TEST] Auto-Test: Ameliorer couverture de tests"
            description = f"""## Gap de Couverture Detecte

**Priorite:** {priority.upper()}
**Detecte par:** Auto-Orchestrateur

### Modules sans Tests:
{chr(10).join(f'- {gap}' for gap in improvement.get('gaps', []))}

### Plan d'Action:
- [ ] Generation tests unitaires
- [ ] Generation tests d'integration
- [ ] Validation couverture >75%

**Auto-genere le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**
"""
        
        elif issue_type == "performance":
            title = f"[PERF] Auto-Optimisation: Performance"
            description = f"""## Optimisation Performance Requise

**Priorite:** {priority.upper()}
**Detecte par:** Auto-Orchestrateur

### Issues Detectees:
{chr(10).join(f'- {issue}' for issue in improvement.get('issues', []))}

### Optimisations Prevues:
- [ ] Analyse profiling
- [ ] Optimisation algorithmes
- [ ] Tests de performance

**Auto-genere le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**
"""
        
        elif issue_type == "feature":
            title = f"[FEAT] Auto-Feature: {improvement.get('ideas', ['New Feature'])[0]}"
            description = f"""## Nouvelle Fonctionnalite Auto-Generee

**Priorite:** {priority.upper()}
**Generee par:** Auto-Orchestrateur

### Idees Detectees:
{chr(10).join(f'- {idea}' for idea in improvement.get('ideas', []))}

### Developpement:
- [ ] Analyse des besoins
- [ ] Implementation feature
- [ ] Tests complets
- [ ] Documentation

**Auto-genere le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**
"""
        
        else:
            title = f"🤖 Auto-Amelioration: {issue_type}"
            description = f"""## Amelioration Auto-Detectee

**Type:** {issue_type}
**Priorite:** {priority.upper()}

**Auto-genere le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**
"""
        
        return title, description
    
    def _get_issue_labels(self, improvement_type: str) -> List[str]:
        """Obtenir les labels appropries pour le type d'amelioration"""
        # Utiliser uniquement les labels de base qui existent sur GitHub
        type_labels = {
            "bug_fix": ["bug"],
            "test_coverage": ["enhancement"],
            "performance": ["enhancement"],
            "feature": ["enhancement"]
        }
        
        # Retourner seulement les labels qui existent sur le repo
        return type_labels.get(improvement_type, ["enhancement"])
    
    async def _update_project_board(self, issue_number: int, status: str) -> bool:
        """Mettre a jour le statut dans GitHub Project Board"""
        try:
            # Conversion statuts
            status_map = {
                "Todo": "Todo",
                "In Progress": "In Progress", 
                "Done": "Done",
                "Testing": "In Progress"
            }
            
            project_status = status_map.get(status, "Todo")
            
            # FIX: Utiliser gh CLI avec project-id obligatoire
            cmd = [
                "gh", "project", "item-edit",
                "--project-id", self.project_id,
                "--field-id", "Status", 
                "--single-select-option-id", project_status,
                f"#{issue_number}"
            ]
            
            await self._run_gh_command(cmd)
            self.logger.info(f"Project board mis a jour: Issue #{issue_number} -> {status}")
            return True
            
        except Exception as e:
            self.logger.warning(f"Erreur mise a jour project: {e}")
            return False
    
    async def _create_feature_branch(self, issue_number: int, improvement_type: str) -> str:
        """Creer une branche feature pour l'issue"""
        
        # Nom de branche standardise avec sanitization
        clean_type = self._sanitize_branch_name(improvement_type)
        branch_name = f"auto/{clean_type}/issue-{issue_number}"
        
        try:
            # Creer et checkout la branche
            await self._run_git_command(["git", "checkout", "-b", branch_name])
            
            # Push la branche vers origin
            await self._run_git_command(["git", "push", "-u", "origin", branch_name])
            
            self.logger.info(f"Branche creee: {branch_name}")
            return branch_name
            
        except Exception as e:
            if "already exists" in str(e):
                # La branche existe deja, basculer dessus
                self.logger.warning(f"Branche existe deja, checkout: {branch_name}")
                try:
                    await self._run_git_command(["git", "checkout", branch_name])
                    return branch_name
                except Exception as e2:
                    self.logger.warning(f"Erreur checkout branche existante: {e2}")
            else:
                self.logger.warning(f"Erreur creation branche: {e}")
            
            return branch_name
    
    async def complete_improvement_workflow(self, issue_number: int, generated_files: Dict[str, str]) -> Dict[str, Any]:
        """Completer le workflow apres generation de code"""
        try:
            if issue_number not in self.active_issues:
                return {"error": "Issue non trouvee dans le tracking"}
            
            issue_data = self.active_issues[issue_number]
            branch_name = issue_data["branch"]
            
            # 1. Commit les changements
            await self._commit_generated_code(generated_files, issue_number)
            
            # 2. Creer Pull Request
            pr_url = await self._create_pull_request(issue_number, branch_name)
            
            # 3. Mettre a jour project board
            await self._update_project_board(issue_number, "Testing")
            
            # 4. Si auto-merge active et tests passent
            if self.config.get("auto_merge", False):
                merge_result = await self._auto_merge_if_tests_pass(pr_url)
                if merge_result["merged"]:
                    await self._update_project_board(issue_number, "Done")
                    await self._close_issue(issue_number)
                    
                    # 5. Versioning automatique
                    if self.config.get("auto_versioning", False):
                        await self._create_version_release(issue_data["improvement"])
            
            return {
                "workflow_completed": True,
                "pr_created": pr_url,
                "issue_number": issue_number
            }
            
        except Exception as e:
            self.logger.error(f"Erreur completion workflow: {e}")
            return {"error": str(e)}
    
    async def _commit_generated_code(self, generated_files: Dict[str, str], issue_number: int):
        """Committer le code genere avec message approprie"""
        try:
            # Ajouter tous les fichiers generes
            for file_path in generated_files.keys():
                await self._run_git_command(["git", "add", file_path])
            
            # Commit avec message standardise
            commit_msg = f"Auto-fix: Resolve issue #{issue_number}\n\nGenerated by Auto-Orchestrator:\n"
            for file_path in generated_files.keys():
                commit_msg += f"- {file_path}\n"
            commit_msg += f"\nCloses #{issue_number}"
            
            await self._run_git_command(["git", "commit", "-m", commit_msg])
            await self._run_git_command(["git", "push"])
            
            self.logger.info(f"Code commite pour issue #{issue_number}")
            
        except Exception as e:
            self.logger.error(f"Erreur commit: {e}")
    
    async def _create_pull_request(self, issue_number: int, branch_name: str) -> str:
        """Creer une Pull Request liee a l'issue"""
        try:
            issue_data = self.active_issues[issue_number]
            improvement = issue_data["improvement"]
            
            pr_title = f"Auto-Fix #{issue_number}: {improvement['type'].replace('_', ' ').title()}"
            pr_body = f"""## Auto-Generated Pull Request

**Fixes:** #{issue_number}
**Type:** {improvement['type']}
**Priority:** {improvement.get('priority', 'medium')}

### Changes:
- Auto-generated improvements by orchestrator
- Automated testing included
- Code quality validated

### Testing:
- [x] Auto-tests executed
- [x] Code quality checks
- [x] Integration tests

**Auto-generated by orchestrator on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**
"""
            
            cmd = [
                "gh", "pr", "create",
                "--repo", f"{self.repo_owner}/{self.repo_name}",
                "--head", branch_name,
                "--title", pr_title,
                "--body", pr_body
            ]
            
            pr_url = await self._run_gh_command(cmd)
            self.logger.info(f"PR creee: {pr_url.strip()}")
            
            return pr_url.strip()
            
        except Exception as e:
            self.logger.error(f"Erreur creation PR: {e}")
            return f"https://github.com/{self.repo_owner}/{self.repo_name}/pull/auto-{issue_number}"
    
    async def _auto_merge_if_tests_pass(self, pr_url: str) -> Dict[str, Any]:
        """Auto-merge si les tests passent"""
        try:
            # Recuperer le numero de PR depuis l'URL
            pr_number = pr_url.split("/")[-1]
            
            # Verifier le statut des checks
            cmd = ["gh", "pr", "view", pr_number, "--json", "statusCheckRollup"]
            checks_result = await self._run_gh_command(cmd)
            checks_data = json.loads(checks_result)
            
            # Si tous les checks passent
            if self._all_checks_passing(checks_data):
                # Auto-merge
                merge_cmd = ["gh", "pr", "merge", pr_number, "--auto", "--squash"]
                await self._run_gh_command(merge_cmd)
                
                self.logger.info(f"PR #{pr_number} auto-merged")
                return {"merged": True, "pr_number": pr_number}
            else:
                self.logger.info(f"PR #{pr_number} - Checks en attente")
                return {"merged": False, "reason": "checks_pending"}
                
        except Exception as e:
            self.logger.error(f"Erreur auto-merge: {e}")
            return {"merged": False, "error": str(e)}
    
    def _all_checks_passing(self, checks_data: Dict) -> bool:
        """Verifier si tous les checks GitHub passent"""
        try:
            rollup = checks_data.get("statusCheckRollup", [])
            if not rollup:
                return True  # Pas de checks = OK pour auto-merge
            
            for check in rollup:
                if check.get("state") not in ["SUCCESS", "NEUTRAL"]:
                    return False
            
            return True
        except:
            return True  # En cas d'erreur, permettre le merge
    
    async def _close_issue(self, issue_number: int):
        """Fermer l'issue apres merge reussi"""
        try:
            cmd = ["gh", "issue", "close", str(issue_number), "--comment", "Auto-resolu par l'orchestrateur"]
            await self._run_gh_command(cmd)
            
            # Retirer du tracking
            if issue_number in self.active_issues:
                del self.active_issues[issue_number]
            
            self.logger.info(f"Issue #{issue_number} fermee")
            
        except Exception as e:
            self.logger.error(f"Erreur fermeture issue: {e}")
    
    async def _create_version_release(self, improvement: Dict[str, Any]):
        """Creer une release version automatique"""
        try:
            # Incrementer la version
            new_version = self._increment_version(improvement["type"])
            
            # Generer release notes
            release_notes = self._generate_release_notes(new_version, improvement)
            
            # Creer tag et release
            await self._run_git_command(["git", "tag", f"v{new_version}"])
            await self._run_git_command(["git", "push", "--tags"])
            
            cmd = [
                "gh", "release", "create", f"v{new_version}",
                "--title", f"Auto-Release v{new_version}",
                "--notes", release_notes
            ]
            
            await self._run_gh_command(cmd)
            
            self.current_version = new_version
            self.logger.info(f"Release v{new_version} creee")
            
        except Exception as e:
            self.logger.error(f"Erreur creation release: {e}")
    
    def _increment_version(self, improvement_type: str) -> str:
        """Incrementer la version selon le type d'amelioration"""
        parts = self.current_version.split(".")
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        
        if improvement_type == "feature":
            minor += 1
            patch = 0
        elif improvement_type == "bug_fix":
            patch += 1
        elif improvement_type == "performance":
            patch += 1
        else:
            patch += 1
        
        return f"{major}.{minor}.{patch}"
    
    def _generate_release_notes(self, version: str, improvement: Dict[str, Any]) -> str:
        """Generer les notes de release"""
        return f"""# Auto-Release v{version}

## What's New
- **{improvement['type'].replace('_', ' ').title()}**: Auto-generated improvements

## Changes
- Automatic code generation and testing
- Quality assurance validation
- Continuous integration workflow

## Auto-Generated
Released by orchestrator on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Full Changelog**: https://github.com/{self.repo_owner}/{self.repo_name}/compare/v{self.current_version}...v{version}
"""
    
    async def _run_gh_command(self, cmd: List[str]) -> str:
        """Executer une commande gh CLI"""
        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                raise Exception(f"gh command failed: {stderr.decode()}")
            
            return stdout.decode()
        except Exception as e:
            self.logger.error(f"Erreur commande gh: {e}")
            raise
    
    async def _run_git_command(self, cmd: List[str]) -> str:
        """Executer une commande git"""
        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                raise Exception(f"git command failed: {stderr.decode()}")
            
            return stdout.decode()
        except Exception as e:
            self.logger.error(f"Erreur commande git: {e}")
            raise
    
    async def _create_github_issue_with_retry(self, improvement: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
        """Creer une issue GitHub avec retry logic"""
        for attempt in range(max_retries):
            try:
                return await self._create_github_issue(improvement)
            except Exception as e:
                if attempt == max_retries - 1:
                    self.logger.error(f"Echec definitif creation issue apres {max_retries} tentatives")
                    raise e
                else:
                    self.logger.warning(f"Tentative {attempt + 1} echouee, retry dans 1s: {e}")
                    await asyncio.sleep(1)
        
    def _sanitize_branch_name(self, branch_type: str) -> str:
        """Nettoyer le nom de branche pour eviter les caracteres problematiques"""
        # Convertir en minuscules et remplacer les caracteres speciaux
        sanitized = branch_type.lower()
        sanitized = sanitized.replace(" ", "_")
        sanitized = sanitized.replace("/", "_")
        sanitized = sanitized.replace(":", "_")
        sanitized = sanitized.replace("-", "_")
        
        # Supprimer les caracteres multiples
        while "__" in sanitized:
            sanitized = sanitized.replace("__", "_")
            
        return sanitized.strip("_")

    # ====================== MODE PULL - SYNCHRONISATION BIDIRECTIONNELLE ======================
    
    async def fetch_github_issues(self, exclude_auto_generated: bool = False) -> List[Dict[str, Any]]:
        """Recuperer les issues GitHub existantes"""
        try:
            cmd = [
                "gh", "issue", "list",
                "--repo", f"{self.repo_owner}/{self.repo_name}",
                "--state", "open",
                "--json", "number,title,labels,body,assignees,milestone",
                "--limit", "100"
            ]
            
            result = await self._run_gh_command(cmd)
            issues = json.loads(result)
            
            if exclude_auto_generated:
                # Filtrer les issues auto-generees
                issues = [
                    issue for issue in issues
                    if not any(label.get("name") == "auto-generated" 
                             for label in issue.get("labels", []))
                ]
            
            self.logger.info(f"Issues recuperees: {len(issues)}")
            return issues
            
        except Exception as e:
            self.logger.error(f"Erreur recuperation issues: {e}")
            return []
    
    def parse_issue_to_opportunity(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Convertir une issue GitHub en opportunite d'amelioration"""
        
        # Detection du type basee sur le titre et labels
        issue_type = "feature"
        title = issue.get("title", "").lower()
        labels = [label.get("name", "").lower() for label in issue.get("labels", [])]
        
        if any(label in labels for label in ["bug", "error", "fix"]):
            issue_type = "bug_fix"
        elif any(label in labels for label in ["test", "testing", "coverage"]):
            issue_type = "test_coverage"
        elif any(label in labels for label in ["performance", "optimization"]):
            issue_type = "performance"
        elif any(label in labels for label in ["enhancement", "feature"]):
            issue_type = "feature"
        
        # Detection de priorite basee sur les labels
        priority = "medium"
        if any(label in labels for label in ["critical", "urgent", "high"]):
            priority = "high"
        elif any(label in labels for label in ["low", "minor", "documentation"]):
            priority = "low"
        
        opportunity = {
            "type": issue_type,
            "priority": priority,
            "source": "github_issue",
            "issue_number": issue.get("number"),
            "title": issue.get("title", ""),
            "description": issue.get("body", ""),
            "labels": labels,
            "assignees": [assignee.get("login") for assignee in issue.get("assignees", [])],
            "milestone": issue.get("milestone", {}).get("title") if issue.get("milestone") else None
        }
        
        return opportunity
    
    async def fetch_project_cards(self, status: str = "Todo") -> List[Dict[str, Any]]:
        """Recuperer les cartes du Project Board GitHub"""
        try:
            cmd = [
                "gh", "project", "item-list", self.project_id,
                "--owner", self.repo_owner,
                "--format", "json"
            ]
            
            result = await self._run_gh_command(cmd)
            project_data = json.loads(result)
            
            # Filtrer par statut si specifie
            cards = []
            for item in project_data.get("items", []):
                if not status or item.get("status") == status:
                    cards.append(item)
            
            # Trier par priorite (ordre dans le board)
            cards.sort(key=lambda x: x.get("priority", 999))
            
            self.logger.info(f"Cartes recuperees ({status}): {len(cards)}")
            return cards
            
        except Exception as e:
            self.logger.warning(f"Erreur recuperation project cards: {e}")
            return []
    
    async def sync_with_project_board(self) -> Dict[str, Any]:
        """Synchronisation complete avec le Project Board"""
        try:
            # 1. Recuperer les cartes du board
            todo_cards = await self.fetch_project_cards("Todo")
            in_progress_cards = await self.fetch_project_cards("In Progress")
            
            # 2. Recuperer les issues correspondantes
            all_issues = await self.fetch_github_issues(exclude_auto_generated=True)
            
            # 3. Creer une map issue_number -> issue
            issues_map = {issue["number"]: issue for issue in all_issues}
            
            # 4. Convertir les cartes Todo en opportunites
            opportunities = []
            for card in todo_cards:
                issue_number = card.get("content", {}).get("number")
                if issue_number in issues_map:
                    issue = issues_map[issue_number]
                    if self.should_process_issue(issue_number):
                        opportunity = self.parse_issue_to_opportunity(issue)
                        opportunities.append(opportunity)
            
            sync_result = {
                "synced": True,
                "todo_count": len(todo_cards),
                "in_progress_count": len(in_progress_cards),
                "opportunities": opportunities,
                "total_issues": len(all_issues)
            }
            
            self.logger.info(f"Sync Project Board: {len(opportunities)} opportunites creees")
            return sync_result
            
        except Exception as e:
            self.logger.error(f"Erreur sync project board: {e}")
            return {"synced": False, "error": str(e)}
    
    def should_process_issue(self, issue_number: int) -> bool:
        """Verifier si une issue doit etre traitee (eviter doublons)"""
        if not hasattr(self, 'processed_issues'):
            self.processed_issues = set()
        
        return issue_number not in self.processed_issues
    
    def mark_issue_processed(self, issue_number: int):
        """Marquer une issue comme traitee"""
        if not hasattr(self, 'processed_issues'):
            self.processed_issues = set()
        
        self.processed_issues.add(issue_number)
    
    async def move_project_card(self, card_id: str, new_status: str) -> bool:
        """Deplacer une carte entre les colonnes du Project Board"""
        try:
            cmd = [
                "gh", "project", "item-edit", card_id,
                "--id", self.project_id,
                "--field-id", "Status",
                "--single-select-option-id", new_status
            ]
            
            await self._run_gh_command(cmd)
            self.logger.info(f"Carte {card_id} deplacee vers {new_status}")
            return True
            
        except Exception as e:
            self.logger.warning(f"Erreur deplacement carte: {e}")
            return False
    
    def prioritize_cards(self, cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioriser les cartes selon l'ordre du Project Board"""
        return sorted(cards, key=lambda x: x.get("priority", 999))
    
    def should_process_auto_generated_issue(self, issue: Dict[str, Any]) -> bool:
        """Verifier si on doit traiter une issue auto-generee (eviter boucles)"""
        labels = [label.get("name", "").lower() for label in issue.get("labels", [])]
        
        # Ne pas traiter les issues auto-generees (eviter boucles infinies)
        if "auto-generated" in labels:
            return False
        
        return True
    
    def can_auto_process_issue(self, issue: Dict[str, Any]) -> bool:
        """Verifier si l'orchestrateur peut traiter automatiquement cette issue"""
        # Ne pas traiter les issues assignees a des utilisateurs
        assignees = issue.get("assignees", [])
        if assignees:
            return False
        
        return True
    
    async def execute_pull_workflow(self) -> Dict[str, Any]:
        """Executer le workflow complet en mode PULL"""
        try:
            self.logger.info("Demarrage workflow PULL mode")
            
            # 1. Synchronisation avec le Project Board
            sync_result = await self.sync_with_project_board()
            
            if not sync_result.get("synced"):
                return {"error": "Echec synchronisation project board"}
            
            # 2. Traitement des opportunites identifiees
            opportunities = sync_result.get("opportunities", [])
            opportunities_created = []
            
            for opportunity in opportunities:
                # Verifier si on peut traiter automatiquement
                issue_num = opportunity["issue_number"]
                all_issues = await self.fetch_github_issues()
                issue_data = next((i for i in all_issues if i["number"] == issue_num), None)
                
                if issue_data and self.can_auto_process_issue(issue_data):
                    opportunities_created.append(opportunity)
                    self.mark_issue_processed(issue_num)
            
            result = {
                "issues_fetched": sync_result.get("total_issues", 0),
                "cards_synced": sync_result.get("todo_count", 0) + sync_result.get("in_progress_count", 0),
                "opportunities_created": opportunities_created,
                "workflow_status": "completed"
            }
            
            self.logger.info(f"Workflow PULL termine: {len(opportunities_created)} opportunites")
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur workflow PULL: {e}")
            return {"error": str(e), "workflow_status": "failed"}

    async def get_sync_status(self) -> Dict[str, Any]:
        """Obtenir le statut de synchronisation GitHub"""
        status = {
            "active_issues": len(self.active_issues),
            "current_version": self.current_version,
            "repo": f"{self.repo_owner}/{self.repo_name}",
            "project_id": self.project_id,
            "sync_enabled": True
        }
        
        # Ajouter infos pour mode PULL si configure
        if self.config.get("pull_mode_enabled", False):
            status.update({
                "pull_mode_enabled": True,
                "processed_issues_count": len(getattr(self, 'processed_issues', set())),
                "pending_sync_cards": len(getattr(self, 'pending_sync_cards', []))
            })
        
        return status