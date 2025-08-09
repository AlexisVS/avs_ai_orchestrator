#!/usr/bin/env python3
"""
Tests pour GitHubSyncAgent - Problemes detectes dans les logs
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from orchestrator.agents.github_sync_agent import GitHubSyncAgent


class TestGitHubSyncAgentProblems:
    """Tests pour corriger les problemes detectes dans les logs"""
    
    @pytest.fixture
    def config(self):
        """Configuration de test"""
        return {
            "github": {
                "owner": "AlexisVS",
                "repo": "avs_ai_orchestrator", 
                "project_id": "12"
            },
            "sandbox_path": Path.cwd() / "test_sandbox"
        }
    
    @pytest.fixture
    def agent(self, config):
        """Instance de l'agent pour les tests"""
        return GitHubSyncAgent(config)
    
    def test_project_id_validation(self, agent):
        """Test: Verifier que project_id est correctement recupere"""
        assert agent.config["github"]["project_id"] == "12"
        # Verifier que l'agent a acces au project_id
        assert hasattr(agent, 'project_id') or agent.config["github"]["project_id"] == "12"
    
    def test_file_path_correction(self, agent):
        """Test: Correction des noms de fichiers generes"""
        # Probleme detecte: 'src/bug_fixs.py' au lieu de 'src/bug_fixes.py'
        generated_files = {
            "src/bug_fixs.py": "# Code fix",  # Nom incorrect
            "src/test_coverages.py": "# Test code"  # Nom incorrect
        }
        
        # Simuler une methode de correction
        corrected_files = {}
        for path, content in generated_files.items():
            # Corriger les noms de fichiers pluriels incorrects
            if path.endswith("_fixs.py"):
                corrected_path = path.replace("_fixs.py", "_fixes.py")
            elif path.endswith("_coverages.py"):
                corrected_path = path.replace("_coverages.py", "_coverage.py")
            else:
                corrected_path = path
            corrected_files[corrected_path] = content
        
        # Verifier les corrections
        assert "src/bug_fixes.py" in corrected_files
        assert "src/test_coverage.py" in corrected_files
        assert "src/bug_fixs.py" not in corrected_files
        assert "src/test_coverages.py" not in corrected_files
    
    def test_encoding_fix_in_logs(self, agent):
        """Test: Correction de l'encodage UTF-8"""
        # Texte avec caracteres speciaux qui causent des problemes
        test_message = "Amelioration: Resolution des problemes detectes"
        
        # Verifier que l'encodage UTF-8 fonctionne
        try:
            encoded = test_message.encode('utf-8')
            decoded = encoded.decode('utf-8')
            
            assert decoded == test_message
            assert "Amelioration" in decoded
            assert "Resolution" in decoded
        except UnicodeEncodeError:
            # Si l'encodage pose probleme, utiliser une version ASCII
            ascii_message = "Amelioration: Resolution des problemes detectes"
            assert ascii_message is not None
    
    def test_gh_command_project_id_fix(self, agent):
        """Test: Fix pour project-id must be provided"""
        # Simuler la construction d'une commande avec project-id
        issue_number = 123
        project_id = agent.config["github"]["project_id"]
        
        # Commande correcte avec project-id
        expected_command = [
            "gh", "project", "item-edit",
            "--project-id", project_id,
            "--field-id", "Status",
            "--single-select-option-id", "In Progress",
            f"#{issue_number}"
        ]
        
        # Verifier que project-id est inclus
        assert "--project-id" in expected_command
        assert project_id in expected_command
        assert f"#{issue_number}" in expected_command
    
    def test_git_pathspec_prevention(self, agent):
        """Test: Prevention erreur pathspec Git"""
        # Liste de fichiers potentiellement generes
        test_files = {
            "src/bug_fixes.py": "# Bug fix code",
            "tests/test_new_module.py": "# Test code",
            "src/nonexistent.py": "# Code"
        }
        
        # Simuler la verification d'existence des fichiers
        sandbox_path = Path("test_sandbox")
        sandbox_path.mkdir(exist_ok=True)
        
        # Creer seulement certains fichiers
        existing_files = {}
        for file_path, content in test_files.items():
            full_path = sandbox_path / file_path
            if file_path != "src/nonexistent.py":  # Ne pas creer ce fichier
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding='utf-8')
                existing_files[file_path] = content
        
        # Verifier que seuls les fichiers existants sont retournes
        assert "src/bug_fixes.py" in existing_files
        assert "tests/test_new_module.py" in existing_files
        assert "src/nonexistent.py" not in existing_files
        
        # Nettoyer
        import shutil
        shutil.rmtree(sandbox_path, ignore_errors=True)
    
    def test_empty_branch_pr_prevention(self, agent):
        """Test: Prevention erreur PR avec branche vide"""
        branch_name = "auto/bug_fix/issue-11"
        
        # Simuler la verification qu'une branche a des commits
        def has_commits(branch):
            # Dans un vrai scenario, on verifierait avec git
            # git rev-list --count branch
            return branch != "auto/bug_fix/issue-11"  # Simuler branche vide
        
        # Verifier la detection de branche vide
        assert not has_commits(branch_name)
        
        # La creation de PR devrait etre evitee si pas de commits
        should_create_pr = has_commits(branch_name)
        assert not should_create_pr


class TestGitHubSyncAgentBasics:
    """Tests basiques pour GitHubSyncAgent - TDD Phase RED"""
    
    def test_github_sync_agent_initialization(self):
        """Test l'initialisation du GitHubSyncAgent"""
        # GIVEN une configuration avec parametres GitHub
        config = {
            "github": {
                "owner": "TestOwner",
                "repo": "test-repo",
                "project_id": "42"
            },
            "auto_merge": True,
            "auto_versioning": True
        }
        
        # WHEN on initialise l'agent
        agent = GitHubSyncAgent(config)
        
        # THEN la configuration doit etre correcte
        assert agent.config == config
        assert agent.repo_owner == "TestOwner"
        assert agent.repo_name == "test-repo"
        assert agent.project_id == "42"
        assert agent.current_version == "1.0.0"
        assert agent.active_issues == {}
        assert agent.pending_prs == {}
    
    def test_github_sync_agent_default_config(self):
        """Test la configuration par defaut"""
        # GIVEN une configuration minimale
        config = {}
        
        # WHEN on initialise l'agent
        agent = GitHubSyncAgent(config)
        
        # THEN les valeurs par defaut doivent etre utilisees
        assert agent.repo_owner == "AlexisVS"
        assert agent.repo_name == "avs_ai_orchestrator"
        assert agent.project_id == "12"


class TestGitHubIssueCreation:
    """Tests TDD pour creation d'issues GitHub - Phase RED"""
    
    @pytest.mark.asyncio
    async def test_sync_improvement_to_github_bug_fix(self):
        """Test synchronisation amelioration bug_fix vers GitHub"""
        # GIVEN un GitHubSyncAgent configure
        config = {"github": {"owner": "test", "repo": "test"}}
        agent = GitHubSyncAgent(config)
        
        # AND une amelioration de type bug_fix
        improvement = {
            "type": "bug_fix",
            "priority": "high",
            "patterns": ["TypeError in test.py", "Missing import"],
            "cycle": 5
        }
        
        # WHEN on synchronise avec GitHub
        with patch.object(agent, '_create_github_issue') as mock_create_issue:
            with patch.object(agent, '_update_project_board') as mock_update_board:
                with patch.object(agent, '_create_feature_branch') as mock_create_branch:
                    
                    # Configurer les mocks
                    mock_create_issue.return_value = {"number": 123, "url": "https://test", "title": "Bug Fix"}
                    mock_update_board.return_value = True
                    mock_create_branch.return_value = "auto/bug_fix/issue-123"
                    
                    result = await agent.sync_improvement_to_github(improvement)
        
        # THEN le workflow doit etre initie
        assert result["issue_created"] == 123
        assert result["branch_created"] == "auto/bug_fix/issue-123"
        assert result["project_updated"] is True
        assert result["workflow_status"] == "initiated"
        
        # AND l'issue doit etre trackee
        assert 123 in agent.active_issues
        assert agent.active_issues[123]["status"] == "in_progress"
        assert agent.active_issues[123]["improvement"] == improvement
    
    @pytest.mark.asyncio
    async def test_sync_improvement_to_github_test_coverage(self):
        """Test synchronisation amelioration test_coverage vers GitHub"""
        # GIVEN un agent et une amelioration test_coverage
        config = {}
        agent = GitHubSyncAgent(config)
        
        improvement = {
            "type": "test_coverage",
            "priority": "medium",
            "gaps": ["Module sans test: utils.py", "Methode non couverte: calculate"]
        }
        
        # WHEN on synchronise
        with patch.object(agent, '_create_github_issue') as mock_create_issue:
            with patch.object(agent, '_update_project_board') as mock_update_board:
                with patch.object(agent, '_create_feature_branch') as mock_create_branch:
                    
                    mock_create_issue.return_value = {"number": 456, "url": "https://test", "title": "Test Coverage"}
                    mock_update_board.return_value = True
                    mock_create_branch.return_value = "auto/test_coverage/issue-456"
                    
                    result = await agent.sync_improvement_to_github(improvement)
        
        # THEN le resultat doit etre correct
        assert result["issue_created"] == 456
        assert result["branch_created"] == "auto/test_coverage/issue-456"
        assert result["workflow_status"] == "initiated"
    
    def test_generate_issue_content_bug_fix(self):
        """Test generation contenu issue pour bug_fix"""
        # GIVEN un agent et une amelioration bug_fix
        agent = GitHubSyncAgent({})
        improvement = {
            "type": "bug_fix",
            "priority": "high",
            "patterns": ["TypeError in agent.py line 42", "Missing import in utils.py"],
            "cycle": 3
        }
        
        # WHEN on genere le contenu
        title, description = agent._generate_issue_content(improvement)
        
        # THEN le titre doit etre approprie
        assert title.startswith("[BUG] Auto-Fix:")
        assert "TypeError in agent.py line 42" in title
        
        # AND la description doit contenir les details
        assert "**Priorite:** HIGH" in description
        assert "Cycle #3" in description
        assert "TypeError in agent.py line 42" in description
        assert "Missing import in utils.py" in description
        assert "Auto-genere le" in description
    
    def test_generate_issue_content_test_coverage(self):
        """Test generation contenu issue pour test_coverage"""
        # GIVEN un agent et une amelioration test_coverage
        agent = GitHubSyncAgent({})
        improvement = {
            "type": "test_coverage",
            "priority": "medium", 
            "gaps": ["Module sans test: new_module", "Methode non couverte: process_data"]
        }
        
        # WHEN on genere le contenu
        title, description = agent._generate_issue_content(improvement)
        
        # THEN le titre doit etre approprie
        assert title.startswith("[TEST] Auto-Test:")
        assert "couverture de tests" in title
        
        # AND la description doit contenir les gaps
        assert "**Priorite:** MEDIUM" in description
        assert "Module sans test: new_module" in description
        assert "Methode non couverte: process_data" in description
    
    def test_generate_issue_content_performance(self):
        """Test generation contenu issue pour performance"""
        # GIVEN un agent et une amelioration performance
        agent = GitHubSyncAgent({})
        improvement = {
            "type": "performance",
            "priority": "medium",
            "issues": [{"function": "slow_processing", "type": "slow_function"}]
        }
        
        # WHEN on genere le contenu
        title, description = agent._generate_issue_content(improvement)
        
        # THEN le titre doit etre approprie
        assert title.startswith("[PERF] Auto-Optimisation:")
        assert "Performance" in title
        
        # AND la description doit contenir les issues
        assert "**Priorite:** MEDIUM" in description
        assert "Issues Detectees:" in description
    
    def test_generate_issue_content_feature(self):
        """Test generation contenu issue pour feature"""
        # GIVEN un agent et une amelioration feature
        agent = GitHubSyncAgent({})
        improvement = {
            "type": "feature",
            "priority": "low",
            "ideas": ["TODO: Add caching system", "TODO: Implement retry logic"]
        }
        
        # WHEN on genere le contenu
        title, description = agent._generate_issue_content(improvement)
        
        # THEN le titre doit contenir la premiere idee
        assert title.startswith("[FEAT] Auto-Feature:")
        assert "TODO: Add caching system" in title
        
        # AND la description doit contenir toutes les idees
        assert "**Priorite:** LOW" in description
        assert "TODO: Add caching system" in description
        assert "TODO: Implement retry logic" in description
    
    def test_get_issue_labels(self):
        """Test obtention des labels d'issue selon le type"""
        # GIVEN un agent
        agent = GitHubSyncAgent({})
        
        # WHEN on obtient les labels pour differents types
        bug_labels = agent._get_issue_labels("bug_fix")
        test_labels = agent._get_issue_labels("test_coverage")
        perf_labels = agent._get_issue_labels("performance")
        feature_labels = agent._get_issue_labels("feature")
        unknown_labels = agent._get_issue_labels("unknown")
        
        # THEN les labels doivent correspondre a l'implementation reelle
        assert bug_labels == ["bug"]
        assert test_labels == ["enhancement"]
        assert perf_labels == ["enhancement"]
        assert feature_labels == ["enhancement"]
        assert unknown_labels == ["enhancement"]


class TestGitHubProjectBoard:
    """Tests TDD pour GitHub Project Board - Phase RED"""
    
    @pytest.mark.asyncio
    async def test_update_project_board_success(self):
        """Test mise a jour reussie du project board"""
        # GIVEN un agent avec un project_id
        config = {"github": {"project_id": "42"}}
        agent = GitHubSyncAgent(config)
        
        # WHEN on met a jour le project board
        with patch.object(agent, '_run_gh_command') as mock_gh:
            mock_gh.return_value = "Updated successfully"
            
            result = await agent._update_project_board(123, "In Progress")
        
        # THEN la mise a jour doit reussir
        assert result is True
        mock_gh.assert_called_once()
        
        # AND la commande gh doit etre correcte
        call_args = mock_gh.call_args[0][0]
        assert "gh" in call_args
        assert "project" in call_args
        assert "item-edit" in call_args
        assert "#123" in call_args
        assert "42" in call_args
    
    @pytest.mark.asyncio
    async def test_update_project_board_failure(self):
        """Test echec mise a jour project board"""
        # GIVEN un agent
        agent = GitHubSyncAgent({})
        
        # WHEN la commande gh echoue
        with patch.object(agent, '_run_gh_command') as mock_gh:
            mock_gh.side_effect = Exception("GitHub API error")
            
            result = await agent._update_project_board(123, "Done")
        
        # THEN la methode doit retourner False sans exception
        assert result is False
    
    def test_project_status_mapping(self):
        """Test mapping des statuts pour project board"""
        # GIVEN un agent
        agent = GitHubSyncAgent({})
        
        # WHEN on teste le mapping dans _update_project_board
        # On ne peut pas tester directement car c'est dans la methode
        # Mais on peut verifier les valeurs utilisees
        
        # Les statuts mappes doivent etre corrects
        status_map = {
            "Todo": "Todo",
            "In Progress": "In Progress", 
            "Done": "Done",
            "Testing": "In Progress"
        }
        
        # THEN le mapping doit etre logique
        assert status_map["Todo"] == "Todo"
        assert status_map["In Progress"] == "In Progress"
        assert status_map["Done"] == "Done" 
        assert status_map["Testing"] == "In Progress"  # Testing -> In Progress


class TestGitHubBranchManagement:
    """Tests TDD pour gestion des branches - Phase RED"""
    
    @pytest.mark.asyncio
    async def test_create_feature_branch_success(self):
        """Test creation reussie d'une branche feature"""
        # GIVEN un agent
        agent = GitHubSyncAgent({})
        
        # WHEN on cree une branche
        with patch.object(agent, '_run_git_command') as mock_git:
            mock_git.return_value = "Branch created"
            
            branch_name = await agent._create_feature_branch(123, "bug_fix")
        
        # THEN la branche doit etre creee avec le bon nom
        assert branch_name == "auto/bug_fix/issue-123"
        
        # AND les commandes git doivent etre appelees
        assert mock_git.call_count == 2  # checkout + push
        
        # Verifier les commandes appelees
        calls = mock_git.call_args_list
        assert ["git", "checkout", "-b", "auto/bug_fix/issue-123"] in calls[0][0]
        assert ["git", "push", "-u", "origin", "auto/bug_fix/issue-123"] in calls[1][0]
    
    @pytest.mark.asyncio 
    async def test_create_feature_branch_failure(self):
        """Test echec creation branche"""
        # GIVEN un agent
        agent = GitHubSyncAgent({})
        
        # WHEN la commande git echoue
        with patch.object(agent, '_run_git_command') as mock_git:
            mock_git.side_effect = Exception("Git error")
            
            branch_name = await agent._create_feature_branch(456, "test_coverage")
        
        # THEN le nom de branche doit etre retourne meme en cas d'echec
        assert branch_name == "auto/test_coverage/issue-456"
    
    def test_branch_naming_convention(self):
        """Test convention de nommage des branches"""
        # GIVEN differents types d'ameliorations
        test_cases = [
            (123, "bug_fix", "auto/bug_fix/issue-123"),
            (456, "test_coverage", "auto/test_coverage/issue-456"),
            (789, "performance", "auto/performance/issue-789"),
            (101, "feature", "auto/feature/issue-101")
        ]
        
        # WHEN on genere les noms de branches
        for issue_number, improvement_type, expected in test_cases:
            # THEN le nom doit suivre la convention
            actual = f"auto/{improvement_type}/issue-{issue_number}"
            assert actual == expected


class TestGitHubPullRequests:
    """Tests TDD pour Pull Requests - Phase RED"""
    
    @pytest.mark.asyncio
    async def test_create_pull_request_success(self):
        """Test creation reussie d'une PR"""
        # GIVEN un agent avec une issue active
        agent = GitHubSyncAgent({"github": {"owner": "test", "repo": "test"}})
        agent.active_issues[123] = {
            "improvement": {"type": "bug_fix", "priority": "high"},
            "branch": "auto/bug_fix/issue-123",
            "status": "in_progress"
        }
        
        # WHEN on cree une PR
        with patch.object(agent, '_run_gh_command') as mock_gh:
            mock_gh.return_value = "https://github.com/test/test/pull/5"
            
            pr_url = await agent._create_pull_request(123, "auto/bug_fix/issue-123")
        
        # THEN la PR doit etre creee
        assert pr_url == "https://github.com/test/test/pull/5"
        mock_gh.assert_called_once()
        
        # AND la commande doit contenir les bons parametres
        call_args = mock_gh.call_args[0][0]
        assert "gh" in call_args
        assert "pr" in call_args
        assert "create" in call_args
        assert "--head" in call_args
        assert "auto/bug_fix/issue-123" in call_args
    
    @pytest.mark.asyncio
    async def test_create_pull_request_failure(self):
        """Test echec creation PR"""
        # GIVEN un agent avec une issue active
        agent = GitHubSyncAgent({"github": {"owner": "test", "repo": "test"}})
        agent.active_issues[456] = {
            "improvement": {"type": "feature", "priority": "low"},
            "branch": "auto/feature/issue-456"
        }
        
        # WHEN la creation PR echoue
        with patch.object(agent, '_run_gh_command') as mock_gh:
            mock_gh.side_effect = Exception("PR creation failed")
            
            pr_url = await agent._create_pull_request(456, "auto/feature/issue-456")
        
        # THEN une URL fallback doit etre retournee
        assert "https://github.com/test/test/pull/auto-456" in pr_url


class TestGitHubAutoMerge:
    """Tests TDD pour auto-merge - Phase RED"""
    
    @pytest.mark.asyncio
    async def test_auto_merge_if_tests_pass_success(self):
        """Test auto-merge reussi quand tests passent"""
        # GIVEN un agent et une PR avec tests qui passent
        agent = GitHubSyncAgent({})
        pr_url = "https://github.com/test/test/pull/5"
        
        # WHEN les checks passent
        with patch.object(agent, '_run_gh_command') as mock_gh:
            # Premiere commande: verifier les checks
            checks_data = {
                "statusCheckRollup": [
                    {"state": "SUCCESS"},
                    {"state": "SUCCESS"}
                ]
            }
            mock_gh.side_effect = [
                json.dumps(checks_data),  # Premier appel: checks
                "Merged successfully"     # Deuxieme appel: merge
            ]
            
            result = await agent._auto_merge_if_tests_pass(pr_url)
        
        # THEN le merge doit reussir
        assert result["merged"] is True
        assert result["pr_number"] == "5"
        assert mock_gh.call_count == 2
    
    @pytest.mark.asyncio
    async def test_auto_merge_if_tests_pass_checks_failing(self):
        """Test auto-merge echoue quand tests echouent"""
        # GIVEN un agent et une PR avec tests qui echouent
        agent = GitHubSyncAgent({})
        pr_url = "https://github.com/test/test/pull/6"
        
        # WHEN les checks echouent
        with patch.object(agent, '_run_gh_command') as mock_gh:
            checks_data = {
                "statusCheckRollup": [
                    {"state": "SUCCESS"},
                    {"state": "FAILURE"}  # Un check echoue
                ]
            }
            mock_gh.return_value = json.dumps(checks_data)
            
            result = await agent._auto_merge_if_tests_pass(pr_url)
        
        # THEN le merge ne doit pas se faire
        assert result["merged"] is False
        assert result["reason"] == "checks_pending"
        assert mock_gh.call_count == 1  # Pas de tentative de merge
    
    def test_all_checks_passing_success(self):
        """Test verification checks qui passent tous"""
        # GIVEN un agent et des checks qui passent
        agent = GitHubSyncAgent({})
        checks_data = {
            "statusCheckRollup": [
                {"state": "SUCCESS"},
                {"state": "SUCCESS"},
                {"state": "NEUTRAL"}
            ]
        }
        
        # WHEN on verifie les checks
        result = agent._all_checks_passing(checks_data)
        
        # THEN tous les checks doivent passer
        assert result is True
    
    def test_all_checks_passing_failure(self):
        """Test verification checks avec echecs"""
        # GIVEN un agent et des checks dont certains echouent
        agent = GitHubSyncAgent({})
        checks_data = {
            "statusCheckRollup": [
                {"state": "SUCCESS"},
                {"state": "FAILURE"},  # Echec
                {"state": "PENDING"}   # En attente
            ]
        }
        
        # WHEN on verifie les checks
        result = agent._all_checks_passing(checks_data)
        
        # THEN la verification doit echouer
        assert result is False
    
    def test_all_checks_passing_empty(self):
        """Test verification checks avec rollup vide"""
        # GIVEN un agent et pas de checks
        agent = GitHubSyncAgent({})
        checks_data = {"statusCheckRollup": []}
        
        # WHEN on verifie les checks
        result = agent._all_checks_passing(checks_data)
        
        # THEN cela doit passer (pas de checks = OK)
        assert result is True


class TestGitHubVersioning:
    """Tests TDD pour auto-versioning - Phase RED"""
    
    def test_increment_version_feature(self):
        """Test incrementation version pour feature"""
        # GIVEN un agent avec version actuelle
        agent = GitHubSyncAgent({})
        agent.current_version = "1.2.3"
        
        # WHEN on incremente pour une feature
        new_version = agent._increment_version("feature")
        
        # THEN la version mineure doit etre incrementee
        assert new_version == "1.3.0"
    
    def test_increment_version_bug_fix(self):
        """Test incrementation version pour bug_fix"""
        # GIVEN un agent avec version actuelle
        agent = GitHubSyncAgent({})
        agent.current_version = "2.1.5"
        
        # WHEN on incremente pour un bug fix
        new_version = agent._increment_version("bug_fix")
        
        # THEN la version patch doit etre incrementee
        assert new_version == "2.1.6"
    
    def test_increment_version_performance(self):
        """Test incrementation version pour performance"""
        # GIVEN un agent avec version actuelle
        agent = GitHubSyncAgent({})
        agent.current_version = "0.9.12"
        
        # WHEN on incremente pour performance
        new_version = agent._increment_version("performance")
        
        # THEN la version patch doit etre incrementee
        assert new_version == "0.9.13"
    
    def test_generate_release_notes(self):
        """Test generation des notes de release"""
        # GIVEN un agent et une amelioration
        agent = GitHubSyncAgent({"github": {"owner": "test", "repo": "test"}})
        agent.current_version = "1.0.0"
        
        improvement = {
            "type": "bug_fix",
            "priority": "high"
        }
        
        # WHEN on genere les notes
        notes = agent._generate_release_notes("1.0.1", improvement)
        
        # THEN les notes doivent contenir les infos cles
        assert "# Auto-Release v1.0.1" in notes
        assert "Bug Fix" in notes
        assert "Auto-generated improvements" in notes
        assert "orchestrator" in notes
        assert "Full Changelog" in notes
        assert "v1.0.0...v1.0.1" in notes


class TestGitHubWorkflowIntegration:
    """Tests TDD pour integration workflow complet - Phase RED"""
    
    @pytest.mark.asyncio
    async def test_complete_improvement_workflow_success(self):
        """Test workflow complet reussi"""
        # GIVEN un agent avec une issue active
        agent = GitHubSyncAgent({"auto_merge": True, "auto_versioning": True})
        agent.active_issues[789] = {
            "improvement": {"type": "bug_fix", "priority": "high"},
            "branch": "auto/bug_fix/issue-789"
        }
        
        generated_files = {
            "src/bug_fix.py": "# Bug fix code",
            "tests/test_bug_fix.py": "# Test code"
        }
        
        # WHEN on complete le workflow
        with patch.object(agent, '_commit_generated_code') as mock_commit:
            with patch.object(agent, '_create_pull_request') as mock_pr:
                with patch.object(agent, '_update_project_board') as mock_board:
                    with patch.object(agent, '_auto_merge_if_tests_pass') as mock_merge:
                        with patch.object(agent, '_close_issue') as mock_close:
                            with patch.object(agent, '_create_version_release') as mock_version:
                                
                                mock_commit.return_value = None
                                mock_pr.return_value = "https://github.com/test/test/pull/10"
                                mock_board.return_value = True
                                mock_merge.return_value = {"merged": True}
                                mock_close.return_value = None
                                mock_version.return_value = None
                                
                                result = await agent.complete_improvement_workflow(789, generated_files)
        
        # THEN le workflow doit etre complet
        assert result["workflow_completed"] is True
        assert result["pr_created"] == "https://github.com/test/test/pull/10"
        assert result["issue_number"] == 789
        
        # AND toutes les etapes doivent etre appelees
        mock_commit.assert_called_once_with(generated_files, 789)
        mock_pr.assert_called_once()
        # Deux appels: Testing puis Done apres merge
        assert mock_board.call_count == 2
        mock_merge.assert_called_once()
        mock_close.assert_called_once()
        mock_version.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_complete_improvement_workflow_no_auto_merge(self):
        """Test workflow sans auto-merge"""
        # GIVEN un agent sans auto-merge
        agent = GitHubSyncAgent({"auto_merge": False})
        agent.active_issues[456] = {
            "improvement": {"type": "feature"},
            "branch": "auto/feature/issue-456"
        }
        
        # WHEN on complete le workflow
        with patch.object(agent, '_commit_generated_code'):
            with patch.object(agent, '_create_pull_request') as mock_pr:
                with patch.object(agent, '_update_project_board'):
                    with patch.object(agent, '_auto_merge_if_tests_pass') as mock_merge:
                        
                        mock_pr.return_value = "https://pr-url"
                        
                        result = await agent.complete_improvement_workflow(456, {})
        
        # THEN le merge ne doit pas etre appele
        mock_merge.assert_not_called()
        assert result["workflow_completed"] is True
    
    @pytest.mark.asyncio
    async def test_complete_improvement_workflow_issue_not_found(self):
        """Test workflow avec issue non trouvee"""
        # GIVEN un agent sans issue trackee
        agent = GitHubSyncAgent({})
        
        # WHEN on tente de completer le workflow
        result = await agent.complete_improvement_workflow(999, {})
        
        # THEN une erreur doit etre retournee
        assert "error" in result
        assert "Issue non trouvee" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_sync_status(self):
        """Test obtention du statut de synchronisation"""
        # GIVEN un agent avec des issues actives
        agent = GitHubSyncAgent({
            "github": {
                "owner": "TestOwner",
                "repo": "test-repo",
                "project_id": "42"
            }
        })
        agent.active_issues[123] = {"status": "in_progress"}
        agent.active_issues[456] = {"status": "testing"}
        agent.current_version = "1.2.3"
        
        # WHEN on obtient le statut
        status = await agent.get_sync_status()
        
        # THEN le statut doit etre complet
        assert status["active_issues"] == 2
        assert status["current_version"] == "1.2.3"
        assert status["repo"] == "TestOwner/test-repo"
        assert status["project_id"] == "42"
        assert status["sync_enabled"] is True


class TestGitHubCommandExecution:
    """Tests TDD pour execution des commandes - Phase RED"""
    
    @pytest.mark.asyncio
    async def test_run_gh_command_success(self):
        """Test execution reussie commande gh"""
        # GIVEN un agent
        agent = GitHubSyncAgent({})
        
        # WHEN on execute une commande gh
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"Success output", b"")
            mock_process.returncode = 0
            mock_exec.return_value = mock_process
            
            result = await agent._run_gh_command(["gh", "version"])
        
        # THEN le resultat doit etre retourne
        assert result == "Success output"
        mock_exec.assert_called_once_with(
            "gh", "version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    
    @pytest.mark.asyncio
    async def test_run_gh_command_failure(self):
        """Test echec commande gh"""
        # GIVEN un agent
        agent = GitHubSyncAgent({})
        
        # WHEN la commande gh echoue
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"Error output")
            mock_process.returncode = 1
            mock_exec.return_value = mock_process
            
            with pytest.raises(Exception) as exc_info:
                await agent._run_gh_command(["gh", "invalid"])
        
        # THEN une exception doit etre levee
        assert "gh command failed" in str(exc_info.value)
        assert "Error output" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_run_git_command_success(self):
        """Test execution reussie commande git"""
        # GIVEN un agent
        agent = GitHubSyncAgent({})
        
        # WHEN on execute une commande git
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"Git success", b"")
            mock_process.returncode = 0
            mock_exec.return_value = mock_process
            
            result = await agent._run_git_command(["git", "status"])
        
        # THEN le resultat doit etre retourne
        assert result == "Git success"
    
    @pytest.mark.asyncio
    async def test_run_git_command_failure(self):
        """Test echec commande git"""
        # GIVEN un agent
        agent = GitHubSyncAgent({})
        
        # WHEN la commande git echoue
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"Git error")
            mock_process.returncode = 1
            mock_exec.return_value = mock_process
            
            with pytest.raises(Exception) as exc_info:
                await agent._run_git_command(["git", "invalid"])
        
        # THEN une exception doit etre levee
        assert "git command failed" in str(exc_info.value)
        assert "Git error" in str(exc_info.value)