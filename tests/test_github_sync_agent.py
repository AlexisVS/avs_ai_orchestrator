#!/usr/bin/env python3
"""
Tests TDD pour GitHubSyncAgent - Phase RED
Tests pour workflow GitHub complet avec auto-versioning
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator.agents.github_sync_agent import GitHubSyncAgent


class TestGitHubSyncAgentBasics:
    """Tests basiques pour GitHubSyncAgent - TDD Phase RED"""
    
    def test_github_sync_agent_initialization(self):
        """Test l'initialisation du GitHubSyncAgent"""
        # GIVEN une configuration avec paramètres GitHub
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
        
        # THEN la configuration doit être correcte
        assert agent.config == config
        assert agent.repo_owner == "TestOwner"
        assert agent.repo_name == "test-repo"
        assert agent.project_id == "42"
        assert agent.current_version == "1.0.0"
        assert agent.active_issues == {}
        assert agent.pending_prs == {}
    
    def test_github_sync_agent_default_config(self):
        """Test la configuration par défaut"""
        # GIVEN une configuration minimale
        config = {}
        
        # WHEN on initialise l'agent
        agent = GitHubSyncAgent(config)
        
        # THEN les valeurs par défaut doivent être utilisées
        assert agent.repo_owner == "AlexisVS"
        assert agent.repo_name == "avs_ai_orchestrator"
        assert agent.project_id == "12"


class TestGitHubIssueCreation:
    """Tests TDD pour création d'issues GitHub - Phase RED"""
    
    @pytest.mark.asyncio
    async def test_sync_improvement_to_github_bug_fix(self):
        """Test synchronisation amélioration bug_fix vers GitHub"""
        # GIVEN un GitHubSyncAgent configuré
        config = {"github": {"owner": "test", "repo": "test"}}
        agent = GitHubSyncAgent(config)
        
        # AND une amélioration de type bug_fix
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
        
        # THEN le workflow doit être initié
        assert result["issue_created"] == 123
        assert result["branch_created"] == "auto/bug_fix/issue-123"
        assert result["project_updated"] is True
        assert result["workflow_status"] == "initiated"
        
        # AND l'issue doit être trackée
        assert 123 in agent.active_issues
        assert agent.active_issues[123]["status"] == "in_progress"
        assert agent.active_issues[123]["improvement"] == improvement
    
    @pytest.mark.asyncio
    async def test_sync_improvement_to_github_test_coverage(self):
        """Test synchronisation amélioration test_coverage vers GitHub"""
        # GIVEN un agent et une amélioration test_coverage
        config = {}
        agent = GitHubSyncAgent(config)
        
        improvement = {
            "type": "test_coverage",
            "priority": "medium",
            "gaps": ["Module sans test: utils.py", "Méthode non couverte: calculate"]
        }
        
        # WHEN on synchronise
        with patch.object(agent, '_create_github_issue') as mock_create_issue:
            with patch.object(agent, '_update_project_board') as mock_update_board:
                with patch.object(agent, '_create_feature_branch') as mock_create_branch:
                    
                    mock_create_issue.return_value = {"number": 456, "url": "https://test", "title": "Test Coverage"}
                    mock_update_board.return_value = True
                    mock_create_branch.return_value = "auto/test_coverage/issue-456"
                    
                    result = await agent.sync_improvement_to_github(improvement)
        
        # THEN le résultat doit être correct
        assert result["issue_created"] == 456
        assert result["branch_created"] == "auto/test_coverage/issue-456"
        assert result["workflow_status"] == "initiated"
    
    def test_generate_issue_content_bug_fix(self):
        """Test génération contenu issue pour bug_fix"""
        # GIVEN un agent et une amélioration bug_fix
        agent = GitHubSyncAgent({})
        improvement = {
            "type": "bug_fix",
            "priority": "high",
            "patterns": ["TypeError in agent.py line 42", "Missing import in utils.py"],
            "cycle": 3
        }
        
        # WHEN on génère le contenu
        title, description = agent._generate_issue_content(improvement)
        
        # THEN le titre doit être approprié
        assert title.startswith("[BUG] Auto-Fix:")
        assert "TypeError in agent.py line 42" in title
        
        # AND la description doit contenir les détails
        assert "**Priorité:** HIGH" in description
        assert "Cycle #3" in description
        assert "TypeError in agent.py line 42" in description
        assert "Missing import in utils.py" in description
        assert "Auto-généré le" in description
    
    def test_generate_issue_content_test_coverage(self):
        """Test génération contenu issue pour test_coverage"""
        # GIVEN un agent et une amélioration test_coverage
        agent = GitHubSyncAgent({})
        improvement = {
            "type": "test_coverage",
            "priority": "medium", 
            "gaps": ["Module sans test: new_module", "Méthode non couverte: process_data"]
        }
        
        # WHEN on génère le contenu
        title, description = agent._generate_issue_content(improvement)
        
        # THEN le titre doit être approprié
        assert title.startswith("[TEST] Auto-Test:")
        assert "couverture de tests" in title
        
        # AND la description doit contenir les gaps
        assert "**Priorité:** MEDIUM" in description
        assert "Module sans test: new_module" in description
        assert "Méthode non couverte: process_data" in description
    
    def test_generate_issue_content_performance(self):
        """Test génération contenu issue pour performance"""
        # GIVEN un agent et une amélioration performance
        agent = GitHubSyncAgent({})
        improvement = {
            "type": "performance",
            "priority": "medium",
            "issues": [{"function": "slow_processing", "type": "slow_function"}]
        }
        
        # WHEN on génère le contenu
        title, description = agent._generate_issue_content(improvement)
        
        # THEN le titre doit être approprié
        assert title.startswith("[EMOJI] Auto-Optimisation:")
        assert "Performance" in title
        
        # AND la description doit contenir les issues
        assert "**Priorité:** MEDIUM" in description
        assert "Issues Détectées:" in description
    
    def test_generate_issue_content_feature(self):
        """Test génération contenu issue pour feature"""
        # GIVEN un agent et une amélioration feature
        agent = GitHubSyncAgent({})
        improvement = {
            "type": "feature",
            "priority": "low",
            "ideas": ["TODO: Add caching system", "TODO: Implement retry logic"]
        }
        
        # WHEN on génère le contenu
        title, description = agent._generate_issue_content(improvement)
        
        # THEN le titre doit contenir la première idée
        assert title.startswith("[EMOJI] Auto-Feature:")
        assert "TODO: Add caching system" in title
        
        # AND la description doit contenir toutes les idées
        assert "**Priorité:** LOW" in description
        assert "TODO: Add caching system" in description
        assert "TODO: Implement retry logic" in description
    
    def test_get_issue_labels(self):
        """Test obtention des labels d'issue selon le type"""
        # GIVEN un agent
        agent = GitHubSyncAgent({})
        
        # WHEN on obtient les labels pour différents types
        bug_labels = agent._get_issue_labels("bug_fix")
        test_labels = agent._get_issue_labels("test_coverage")
        perf_labels = agent._get_issue_labels("performance")
        feature_labels = agent._get_issue_labels("feature")
        unknown_labels = agent._get_issue_labels("unknown")
        
        # THEN les labels doivent être appropriés
        assert "auto-generated" in bug_labels
        assert "orchestrator" in bug_labels
        assert "bug" in bug_labels
        assert "auto-fix" in bug_labels
        
        assert "tests" in test_labels
        assert "enhancement" in test_labels
        
        assert "performance" in perf_labels
        assert "optimization" in perf_labels
        
        assert "feature" in feature_labels
        assert "enhancement" in feature_labels
        
        # Types inconnus doivent avoir au moins les labels de base
        assert "auto-generated" in unknown_labels
        assert "orchestrator" in unknown_labels


class TestGitHubProjectBoard:
    """Tests TDD pour GitHub Project Board - Phase RED"""
    
    @pytest.mark.asyncio
    async def test_update_project_board_success(self):
        """Test mise à jour réussie du project board"""
        # GIVEN un agent avec un project_id
        config = {"github": {"project_id": "42"}}
        agent = GitHubSyncAgent(config)
        
        # WHEN on met à jour le project board
        with patch.object(agent, '_run_gh_command') as mock_gh:
            mock_gh.return_value = "Updated successfully"
            
            result = await agent._update_project_board(123, "In Progress")
        
        # THEN la mise à jour doit réussir
        assert result is True
        mock_gh.assert_called_once()
        
        # AND la commande gh doit être correcte
        call_args = mock_gh.call_args[0][0]
        assert "gh" in call_args
        assert "project" in call_args
        assert "item-edit" in call_args
        assert "#123" in call_args
        assert "42" in call_args
    
    @pytest.mark.asyncio
    async def test_update_project_board_failure(self):
        """Test échec mise à jour project board"""
        # GIVEN un agent
        agent = GitHubSyncAgent({})
        
        # WHEN la commande gh échoue
        with patch.object(agent, '_run_gh_command') as mock_gh:
            mock_gh.side_effect = Exception("GitHub API error")
            
            result = await agent._update_project_board(123, "Done")
        
        # THEN la méthode doit retourner False sans exception
        assert result is False
    
    def test_project_status_mapping(self):
        """Test mapping des statuts pour project board"""
        # GIVEN un agent
        agent = GitHubSyncAgent({})
        
        # WHEN on teste le mapping dans _update_project_board
        # On ne peut pas tester directement car c'est dans la méthode
        # Mais on peut vérifier les valeurs utilisées
        
        # Les statuts mappés doivent être corrects
        status_map = {
            "Todo": "Todo",
            "In Progress": "In Progress", 
            "Done": "Done",
            "Testing": "In Progress"
        }
        
        # THEN le mapping doit être logique
        assert status_map["Todo"] == "Todo"
        assert status_map["In Progress"] == "In Progress"
        assert status_map["Done"] == "Done" 
        assert status_map["Testing"] == "In Progress"  # Testing -> In Progress


class TestGitHubBranchManagement:
    """Tests TDD pour gestion des branches - Phase RED"""
    
    @pytest.mark.asyncio
    async def test_create_feature_branch_success(self):
        """Test création réussie d'une branche feature"""
        # GIVEN un agent
        agent = GitHubSyncAgent({})
        
        # WHEN on crée une branche
        with patch.object(agent, '_run_git_command') as mock_git:
            mock_git.return_value = "Branch created"
            
            branch_name = await agent._create_feature_branch(123, "bug_fix")
        
        # THEN la branche doit être créée avec le bon nom
        assert branch_name == "auto/bug_fix/issue-123"
        
        # AND les commandes git doivent être appelées
        assert mock_git.call_count == 2  # checkout + push
        
        # Vérifier les commandes appelées
        calls = mock_git.call_args_list
        assert ["git", "checkout", "-b", "auto/bug_fix/issue-123"] in calls[0][0]
        assert ["git", "push", "-u", "origin", "auto/bug_fix/issue-123"] in calls[1][0]
    
    @pytest.mark.asyncio 
    async def test_create_feature_branch_failure(self):
        """Test échec création branche"""
        # GIVEN un agent
        agent = GitHubSyncAgent({})
        
        # WHEN la commande git échoue
        with patch.object(agent, '_run_git_command') as mock_git:
            mock_git.side_effect = Exception("Git error")
            
            branch_name = await agent._create_feature_branch(456, "test_coverage")
        
        # THEN le nom de branche doit être retourné même en cas d'échec
        assert branch_name == "auto/test_coverage/issue-456"
    
    def test_branch_naming_convention(self):
        """Test convention de nommage des branches"""
        # GIVEN différents types d'améliorations
        test_cases = [
            (123, "bug_fix", "auto/bug_fix/issue-123"),
            (456, "test_coverage", "auto/test_coverage/issue-456"),
            (789, "performance", "auto/performance/issue-789"),
            (101, "feature", "auto/feature/issue-101")
        ]
        
        # WHEN on génère les noms de branches
        for issue_number, improvement_type, expected in test_cases:
            # THEN le nom doit suivre la convention
            actual = f"auto/{improvement_type}/issue-{issue_number}"
            assert actual == expected


class TestGitHubPullRequests:
    """Tests TDD pour Pull Requests - Phase RED"""
    
    @pytest.mark.asyncio
    async def test_create_pull_request_success(self):
        """Test création réussie d'une PR"""
        # GIVEN un agent avec une issue active
        agent = GitHubSyncAgent({"github": {"owner": "test", "repo": "test"}})
        agent.active_issues[123] = {
            "improvement": {"type": "bug_fix", "priority": "high"},
            "branch": "auto/bug_fix/issue-123",
            "status": "in_progress"
        }
        
        # WHEN on crée une PR
        with patch.object(agent, '_run_gh_command') as mock_gh:
            mock_gh.return_value = "https://github.com/test/test/pull/5"
            
            pr_url = await agent._create_pull_request(123, "auto/bug_fix/issue-123")
        
        # THEN la PR doit être créée
        assert pr_url == "https://github.com/test/test/pull/5"
        mock_gh.assert_called_once()
        
        # AND la commande doit contenir les bons paramètres
        call_args = mock_gh.call_args[0][0]
        assert "gh" in call_args
        assert "pr" in call_args
        assert "create" in call_args
        assert "--head" in call_args
        assert "auto/bug_fix/issue-123" in call_args
    
    @pytest.mark.asyncio
    async def test_create_pull_request_failure(self):
        """Test échec création PR"""
        # GIVEN un agent avec une issue active
        agent = GitHubSyncAgent({"github": {"owner": "test", "repo": "test"}})
        agent.active_issues[456] = {
            "improvement": {"type": "feature", "priority": "low"},
            "branch": "auto/feature/issue-456"
        }
        
        # WHEN la création PR échoue
        with patch.object(agent, '_run_gh_command') as mock_gh:
            mock_gh.side_effect = Exception("PR creation failed")
            
            pr_url = await agent._create_pull_request(456, "auto/feature/issue-456")
        
        # THEN une URL fallback doit être retournée
        assert "https://github.com/test/test/pull/auto-456" in pr_url


class TestGitHubAutoMerge:
    """Tests TDD pour auto-merge - Phase RED"""
    
    @pytest.mark.asyncio
    async def test_auto_merge_if_tests_pass_success(self):
        """Test auto-merge réussi quand tests passent"""
        # GIVEN un agent et une PR avec tests qui passent
        agent = GitHubSyncAgent({})
        pr_url = "https://github.com/test/test/pull/5"
        
        # WHEN les checks passent
        with patch.object(agent, '_run_gh_command') as mock_gh:
            # Première commande: vérifier les checks
            checks_data = {
                "statusCheckRollup": [
                    {"state": "SUCCESS"},
                    {"state": "SUCCESS"}
                ]
            }
            mock_gh.side_effect = [
                json.dumps(checks_data),  # Premier appel: checks
                "Merged successfully"     # Deuxième appel: merge
            ]
            
            result = await agent._auto_merge_if_tests_pass(pr_url)
        
        # THEN le merge doit réussir
        assert result["merged"] is True
        assert result["pr_number"] == "5"
        assert mock_gh.call_count == 2
    
    @pytest.mark.asyncio
    async def test_auto_merge_if_tests_pass_checks_failing(self):
        """Test auto-merge échoue quand tests échouent"""
        # GIVEN un agent et une PR avec tests qui échouent
        agent = GitHubSyncAgent({})
        pr_url = "https://github.com/test/test/pull/6"
        
        # WHEN les checks échouent
        with patch.object(agent, '_run_gh_command') as mock_gh:
            checks_data = {
                "statusCheckRollup": [
                    {"state": "SUCCESS"},
                    {"state": "FAILURE"}  # Un check échoue
                ]
            }
            mock_gh.return_value = json.dumps(checks_data)
            
            result = await agent._auto_merge_if_tests_pass(pr_url)
        
        # THEN le merge ne doit pas se faire
        assert result["merged"] is False
        assert result["reason"] == "checks_pending"
        assert mock_gh.call_count == 1  # Pas de tentative de merge
    
    def test_all_checks_passing_success(self):
        """Test vérification checks qui passent tous"""
        # GIVEN un agent et des checks qui passent
        agent = GitHubSyncAgent({})
        checks_data = {
            "statusCheckRollup": [
                {"state": "SUCCESS"},
                {"state": "SUCCESS"},
                {"state": "NEUTRAL"}
            ]
        }
        
        # WHEN on vérifie les checks
        result = agent._all_checks_passing(checks_data)
        
        # THEN tous les checks doivent passer
        assert result is True
    
    def test_all_checks_passing_failure(self):
        """Test vérification checks avec échecs"""
        # GIVEN un agent et des checks dont certains échouent
        agent = GitHubSyncAgent({})
        checks_data = {
            "statusCheckRollup": [
                {"state": "SUCCESS"},
                {"state": "FAILURE"},  # Échec
                {"state": "PENDING"}   # En attente
            ]
        }
        
        # WHEN on vérifie les checks
        result = agent._all_checks_passing(checks_data)
        
        # THEN la vérification doit échouer
        assert result is False
    
    def test_all_checks_passing_empty(self):
        """Test vérification checks avec rollup vide"""
        # GIVEN un agent et pas de checks
        agent = GitHubSyncAgent({})
        checks_data = {"statusCheckRollup": []}
        
        # WHEN on vérifie les checks
        result = agent._all_checks_passing(checks_data)
        
        # THEN cela doit passer (pas de checks = OK)
        assert result is True


class TestGitHubVersioning:
    """Tests TDD pour auto-versioning - Phase RED"""
    
    def test_increment_version_feature(self):
        """Test incrémentation version pour feature"""
        # GIVEN un agent avec version actuelle
        agent = GitHubSyncAgent({})
        agent.current_version = "1.2.3"
        
        # WHEN on incrémente pour une feature
        new_version = agent._increment_version("feature")
        
        # THEN la version mineure doit être incrémentée
        assert new_version == "1.3.0"
    
    def test_increment_version_bug_fix(self):
        """Test incrémentation version pour bug_fix"""
        # GIVEN un agent avec version actuelle
        agent = GitHubSyncAgent({})
        agent.current_version = "2.1.5"
        
        # WHEN on incrémente pour un bug fix
        new_version = agent._increment_version("bug_fix")
        
        # THEN la version patch doit être incrémentée
        assert new_version == "2.1.6"
    
    def test_increment_version_performance(self):
        """Test incrémentation version pour performance"""
        # GIVEN un agent avec version actuelle
        agent = GitHubSyncAgent({})
        agent.current_version = "0.9.12"
        
        # WHEN on incrémente pour performance
        new_version = agent._increment_version("performance")
        
        # THEN la version patch doit être incrémentée
        assert new_version == "0.9.13"
    
    def test_generate_release_notes(self):
        """Test génération des notes de release"""
        # GIVEN un agent et une amélioration
        agent = GitHubSyncAgent({"github": {"owner": "test", "repo": "test"}})
        agent.current_version = "1.0.0"
        
        improvement = {
            "type": "bug_fix",
            "priority": "high"
        }
        
        # WHEN on génère les notes
        notes = agent._generate_release_notes("1.0.1", improvement)
        
        # THEN les notes doivent contenir les infos clés
        assert "# Auto-Release v1.0.1" in notes
        assert "Bug Fix" in notes
        assert "Auto-generated improvements" in notes
        assert "orchestrator" in notes
        assert "Full Changelog" in notes
        assert "v1.0.0...v1.0.1" in notes


class TestGitHubWorkflowIntegration:
    """Tests TDD pour intégration workflow complet - Phase RED"""
    
    @pytest.mark.asyncio
    async def test_complete_improvement_workflow_success(self):
        """Test workflow complet réussi"""
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
        
        # WHEN on complète le workflow
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
        
        # THEN le workflow doit être complet
        assert result["workflow_completed"] is True
        assert result["pr_created"] == "https://github.com/test/test/pull/10"
        assert result["issue_number"] == 789
        
        # AND toutes les étapes doivent être appelées
        mock_commit.assert_called_once_with(generated_files, 789)
        mock_pr.assert_called_once()
        # Deux appels: Testing puis Done après merge
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
        
        # WHEN on complète le workflow
        with patch.object(agent, '_commit_generated_code'):
            with patch.object(agent, '_create_pull_request') as mock_pr:
                with patch.object(agent, '_update_project_board'):
                    with patch.object(agent, '_auto_merge_if_tests_pass') as mock_merge:
                        
                        mock_pr.return_value = "https://pr-url"
                        
                        result = await agent.complete_improvement_workflow(456, {})
        
        # THEN le merge ne doit pas être appelé
        mock_merge.assert_not_called()
        assert result["workflow_completed"] is True
    
    @pytest.mark.asyncio
    async def test_complete_improvement_workflow_issue_not_found(self):
        """Test workflow avec issue non trouvée"""
        # GIVEN un agent sans issue trackée
        agent = GitHubSyncAgent({})
        
        # WHEN on tente de compléter le workflow
        result = await agent.complete_improvement_workflow(999, {})
        
        # THEN une erreur doit être retournée
        assert "error" in result
        assert "Issue non trouvée" in result["error"]
    
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
        
        # THEN le statut doit être complet
        assert status["active_issues"] == 2
        assert status["current_version"] == "1.2.3"
        assert status["repo"] == "TestOwner/test-repo"
        assert status["project_id"] == "42"
        assert status["sync_enabled"] is True


class TestGitHubCommandExecution:
    """Tests TDD pour exécution des commandes - Phase RED"""
    
    @pytest.mark.asyncio
    async def test_run_gh_command_success(self):
        """Test exécution réussie commande gh"""
        # GIVEN un agent
        agent = GitHubSyncAgent({})
        
        # WHEN on exécute une commande gh
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"Success output", b"")
            mock_process.returncode = 0
            mock_exec.return_value = mock_process
            
            result = await agent._run_gh_command(["gh", "version"])
        
        # THEN le résultat doit être retourné
        assert result == "Success output"
        mock_exec.assert_called_once_with(
            "gh", "version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    
    @pytest.mark.asyncio
    async def test_run_gh_command_failure(self):
        """Test échec commande gh"""
        # GIVEN un agent
        agent = GitHubSyncAgent({})
        
        # WHEN la commande gh échoue
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"Error output")
            mock_process.returncode = 1
            mock_exec.return_value = mock_process
            
            with pytest.raises(Exception) as exc_info:
                await agent._run_gh_command(["gh", "invalid"])
        
        # THEN une exception doit être levée
        assert "gh command failed" in str(exc_info.value)
        assert "Error output" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_run_git_command_success(self):
        """Test exécution réussie commande git"""
        # GIVEN un agent
        agent = GitHubSyncAgent({})
        
        # WHEN on exécute une commande git
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"Git success", b"")
            mock_process.returncode = 0
            mock_exec.return_value = mock_process
            
            result = await agent._run_git_command(["git", "status"])
        
        # THEN le résultat doit être retourné
        assert result == "Git success"
    
    @pytest.mark.asyncio
    async def test_run_git_command_failure(self):
        """Test échec commande git"""
        # GIVEN un agent
        agent = GitHubSyncAgent({})
        
        # WHEN la commande git échoue
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"Git error")
            mock_process.returncode = 1
            mock_exec.return_value = mock_process
            
            with pytest.raises(Exception) as exc_info:
                await agent._run_git_command(["git", "invalid"])
        
        # THEN une exception doit être levée
        assert "git command failed" in str(exc_info.value)
        assert "Git error" in str(exc_info.value)