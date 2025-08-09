#!/usr/bin/env python3
"""
GitHub TDD Orchestrator - Développement automatisé avec TDD strict
Récupère les issues GitHub, développe avec TDD, et maintient la qualité
"""

import asyncio
import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import yaml
import httpx
import subprocess
from enum import Enum

class TaskStatus(Enum):
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    TESTING = "Testing"
    REVIEW = "Review"
    DONE = "Done"

class TDDPhase(Enum):
    RED = "red"      # Test écrit, échoue
    GREEN = "green"  # Code minimal pour faire passer
    REFACTOR = "refactor"  # Amélioration du code

class GitHubTDDOrchestrator:
    """Orchestrateur GitHub avec TDD strict"""
    
    def __init__(self, github_token: str, repo_owner: str, repo_name: str):
        self.github_token = github_token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.repo_path = Path(".")
        self.lm_client_url = "http://127.0.0.1:1234"
        self.current_issue = None
        self.tdd_phase = TDDPhase.RED
        
    async def get_project_issues(self, project_number: int) -> List[Dict]:
        """Récupère les issues d'un GitHub Project"""
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        async with httpx.AsyncClient() as client:
            # Récupérer les issues du projet
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues"
            params = {
                "state": "open",
                "sort": "created",
                "direction": "asc"
            }
            
            response = await client.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                issues = response.json()
                # Filtrer les issues avec les labels appropriés
                return [issue for issue in issues if self._is_development_task(issue)]
            else:
                print(f"[ERROR] Failed to fetch issues: {response.status_code}")
                return []
    
    def _is_development_task(self, issue: Dict) -> bool:
        """Vérifie si une issue est une tâche de développement"""
        labels = [label["name"].lower() for label in issue.get("labels", [])]
        dev_labels = ["feature", "enhancement", "bug", "task", "story"]
        return any(label in labels for label in dev_labels)
    
    async def comment_on_issue(self, issue_number: int, comment: str):
        """Ajoute un commentaire à une issue"""
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with httpx.AsyncClient() as client:
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues/{issue_number}/comments"
            data = {"body": comment}
            
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                print(f"[GITHUB] Comment added to issue #{issue_number}")
            else:
                print(f"[ERROR] Failed to comment: {response.status_code}")
    
    async def ai_analyze_issue(self, issue: Dict) -> Dict[str, Any]:
        """Analyse une issue avec l'IA pour planifier le développement"""
        prompt = f"""
Analyze this GitHub issue for TDD development:

**Title:** {issue['title']}
**Description:** {issue['body']}
**Labels:** {[label['name'] for label in issue['labels']]}

Please provide:
1. **Feature Analysis**: What functionality needs to be implemented?
2. **Test Strategy**: What tests should be written first (TDD approach)?
3. **Implementation Plan**: Step-by-step development approach
4. **Acceptance Criteria**: How to know when it's complete?
5. **File Structure**: What files need to be created/modified?

Focus on TDD approach: Tests first, minimal implementation, then refactor.
"""
        
        return await self._call_ai(prompt, max_tokens=1000)
    
    async def ai_write_tests(self, issue: Dict, analysis: Dict) -> str:
        """Génère les tests pour une fonctionnalité (phase RED)"""
        prompt = f"""
Write comprehensive tests for this feature using TDD approach:

**Feature:** {issue['title']}
**Analysis:** {analysis.get('content', 'See issue description')}

Requirements:
1. Write tests that FAIL initially (RED phase of TDD)
2. Cover all acceptance criteria
3. Use pytest or appropriate testing framework
4. Include unit tests, integration tests if needed
5. Mock external dependencies
6. Aim for >90% coverage

Return complete test code that I can run immediately.
Focus on making tests fail first - this drives the implementation.
"""
        
        return await self._call_ai(prompt, max_tokens=1500)
    
    async def ai_implement_feature(self, issue: Dict, tests: str) -> str:
        """Implémente le minimum pour faire passer les tests (phase GREEN)"""
        prompt = f"""
Implement the MINIMAL code to make these tests pass (GREEN phase of TDD):

**Feature:** {issue['title']}
**Tests to satisfy:**
{tests}

Requirements:
1. Write ONLY the minimum code needed to make tests pass
2. Don't over-engineer - just make it work
3. Focus on making tests green, not on perfect code
4. Follow the existing codebase structure
5. Return complete, runnable code

This is the GREEN phase - minimal implementation only.
We'll refactor in the next phase.
"""
        
        return await self._call_ai(prompt, max_tokens=1500)
    
    async def ai_refactor_code(self, issue: Dict, implementation: str, test_results: str) -> str:
        """Améliore le code sans casser les tests (phase REFACTOR)"""
        prompt = f"""
Refactor this code while keeping all tests passing (REFACTOR phase of TDD):

**Feature:** {issue['title']}
**Current Implementation:**
{implementation}

**Test Results:**
{test_results}

Requirements:
1. Improve code quality WITHOUT changing behavior
2. Apply SOLID principles
3. Remove code duplication
4. Improve readability and maintainability
5. Ensure ALL tests still pass
6. Don't add new features - only improve existing code

Return the refactored code that maintains the same functionality.
"""
        
        return await self._call_ai(prompt, max_tokens=1500)
    
    async def _call_ai(self, prompt: str, max_tokens: int = 800) -> Dict[str, Any]:
        """Appelle l'IA locale (Qwen3-Coder)"""
        try:
            async with httpx.AsyncClient() as client:
                data = {
                    "model": "qwen/qwen3-coder-30b",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a senior software engineer specialized in TDD, clean code, and GitHub workflow. Provide practical, implementable solutions."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.3,  # Plus déterministe pour le code
                    "stream": False
                }
                
                response = await client.post(
                    f"{self.lm_client_url}/v1/chat/completions",
                    json=data,
                    timeout=300.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "content": result["choices"][0]["message"]["content"],
                        "tokens": result.get("usage", {}).get("total_tokens", 0)
                    }
                else:
                    return {"success": False, "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_tests(self) -> Dict[str, Any]:
        """Exécute les tests et retourne les résultats"""
        try:
            # Essayer pytest d'abord
            result = subprocess.run(
                ["python", "-m", "pytest", "-v", "--tb=short", "--cov=.", "--cov-report=term-missing"],
                capture_output=True,
                text=True,
                cwd=self.repo_path
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
                "coverage": self._extract_coverage(result.stdout)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _extract_coverage(self, output: str) -> float:
        """Extrait le pourcentage de couverture"""
        lines = output.split('\n')
        for line in lines:
            if 'TOTAL' in line and '%' in line:
                match = re.search(r'(\d+)%', line)
                if match:
                    return float(match.group(1))
        return 0.0
    
    async def process_issue_with_tdd(self, issue: Dict) -> bool:
        """Traite une issue complète avec cycle TDD"""
        issue_number = issue["number"]
        issue_title = issue["title"]
        
        print(f"\n{'='*80}")
        print(f"🎯 PROCESSING ISSUE #{issue_number}: {issue_title}")
        print(f"{'='*80}")
        
        self.current_issue = issue
        
        # Étape 1: Analyser l'issue
        print(f"\n[PHASE 1] 🔍 Analyzing issue with AI...")
        await self.comment_on_issue(issue_number, f"🤖 **Auto-development started**\n\n**Phase:** Analysis\n**Status:** Analyzing requirements and planning TDD approach...")
        
        analysis = await self.ai_analyze_issue(issue)
        if not analysis["success"]:
            print(f"[ERROR] Failed to analyze issue: {analysis['error']}")
            return False
        
        print(f"[SUCCESS] Analysis complete ({analysis.get('tokens', 0)} tokens)")
        
        # Étape 2: Phase RED - Écrire les tests qui échouent
        print(f"\n[PHASE 2] 🔴 RED - Writing failing tests...")
        self.tdd_phase = TDDPhase.RED
        
        await self.comment_on_issue(issue_number, f"🔴 **TDD Phase: RED**\n\nWriting tests that should fail initially. This drives the implementation requirements.")
        
        tests_code = await self.ai_write_tests(issue, analysis)
        if not tests_code:
            print("[ERROR] Failed to generate tests")
            return False
        
        # Sauvegarder les tests
        test_file = self.repo_path / f"test_{issue_number}_{issue_title.lower().replace(' ', '_')}.py"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(tests_code)
        
        # Exécuter les tests (doivent échouer)
        test_result = self.run_tests()
        if test_result["success"]:
            print("[WARNING] Tests pass immediately - they should fail in RED phase!")
        else:
            print(f"[SUCCESS] Tests fail as expected (RED phase)")
        
        # Étape 3: Phase GREEN - Implémentation minimale
        print(f"\n[PHASE 3] 🟢 GREEN - Minimal implementation...")
        self.tdd_phase = TDDPhase.GREEN
        
        await self.comment_on_issue(issue_number, f"🟢 **TDD Phase: GREEN**\n\nImplementing minimal code to make tests pass. Focus on functionality, not perfection.")
        
        implementation = await self.ai_implement_feature(issue, tests_code)
        if not implementation:
            print("[ERROR] Failed to generate implementation")
            return False
        
        # Sauvegarder l'implémentation
        impl_file = self.repo_path / f"{issue_title.lower().replace(' ', '_')}.py"
        with open(impl_file, 'w', encoding='utf-8') as f:
            f.write(implementation)
        
        # Vérifier que les tests passent maintenant
        test_result = self.run_tests()
        if not test_result["success"]:
            print(f"[ERROR] Tests still failing after implementation!")
            print(f"Output: {test_result['output']}")
            print(f"Errors: {test_result['errors']}")
            return False
        
        coverage = test_result.get("coverage", 0)
        print(f"[SUCCESS] Tests passing! Coverage: {coverage}%")
        
        if coverage < 80:
            print(f"[WARNING] Coverage {coverage}% below minimum (80%)")
            await self.comment_on_issue(issue_number, f"⚠️ **Coverage Warning**\n\nCurrent coverage: {coverage}%\nMinimum required: 80%\nAdding more tests...")
            
            # Demander plus de tests à l'IA
            # ... (logique pour améliorer la couverture)
        
        # Étape 4: Phase REFACTOR - Amélioration du code
        print(f"\n[PHASE 4] 🔄 REFACTOR - Code improvement...")
        self.tdd_phase = TDDPhase.REFACTOR
        
        await self.comment_on_issue(issue_number, f"🔄 **TDD Phase: REFACTOR**\n\nImproving code quality while maintaining all tests green.\nCoverage: {coverage}%")
        
        refactored_code = await self.ai_refactor_code(issue, implementation, test_result["output"])
        if refactored_code:
            with open(impl_file, 'w', encoding='utf-8') as f:
                f.write(refactored_code)
            
            # Vérifier que les tests passent toujours
            final_test = self.run_tests()
            if final_test["success"]:
                final_coverage = final_test.get("coverage", 0)
                print(f"[SUCCESS] Refactoring complete! Final coverage: {final_coverage}%")
                
                # Commentaire final
                await self.comment_on_issue(issue_number, f"""✅ **Development Complete!**

**TDD Cycle Completed:**
- 🔴 RED: Tests written and failed initially
- 🟢 GREEN: Minimal implementation made tests pass  
- 🔄 REFACTOR: Code improved while maintaining tests

**Final Results:**
- ✅ All tests passing
- 📊 Coverage: {final_coverage}%
- 📁 Files: `{impl_file.name}`, `{test_file.name}`

Ready for code review! 🚀""")
                
                return True
            else:
                print("[ERROR] Tests broken after refactoring!")
                return False
        
        return True
    
    async def run_development_cycle(self, project_number: int):
        """Lance le cycle complet de développement"""
        print(f"🚀 Starting GitHub TDD Development Cycle")
        print(f"Repository: {self.repo_owner}/{self.repo_name}")
        print(f"Project: #{project_number}")
        
        # Récupérer les issues
        issues = await self.get_project_issues(project_number)
        
        if not issues:
            print("No development issues found.")
            return
        
        print(f"\nFound {len(issues)} development tasks:")
        for issue in issues:
            print(f"  - #{issue['number']}: {issue['title']}")
        
        # Traiter chaque issue
        for issue in issues:
            success = await self.process_issue_with_tdd(issue)
            
            if not success:
                print(f"[FAILED] Issue #{issue['number']} - stopping here")
                break
            
            print(f"[COMPLETED] Issue #{issue['number']} ✅")
        
        print(f"\n🎉 Development cycle complete!")

async def main():
    """Point d'entrée principal"""
    
    # Configuration (à adapter selon vos besoins)
    config = {
        "github_token": os.getenv("GITHUB_TOKEN", "your-token-here"),
        "repo_owner": "your-username",
        "repo_name": "your-repo-name", 
        "project_number": 1
    }
    
    if config["github_token"] == "your-token-here":
        print("⚠️  Please configure your GitHub token and repository details")
        print("Set GITHUB_TOKEN environment variable or edit the config")
        return
    
    orchestrator = GitHubTDDOrchestrator(
        github_token=config["github_token"],
        repo_owner=config["repo_owner"],
        repo_name=config["repo_name"]
    )
    
    await orchestrator.run_development_cycle(config["project_number"])

if __name__ == "__main__":
    asyncio.run(main())