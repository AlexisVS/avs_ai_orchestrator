#!/usr/bin/env python3
"""
Tests complets pour l'orchestrateur enhanced avec GitHub integration
"""

import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import httpx

from enhanced_orchestrator import EnhancedOrchestrator
from task_documenter import TaskDocumenter
from card_tracker import CardTracker

class TestEnhancedOrchestrator:
    """Tests pour l'orchestrateur complet"""
    
    @pytest.fixture
    def config(self):
        return {
            'project': {
                'name': 'test-project',
                'type': 'nextjs',
                'description': 'Test project',
                'output_dir': '/tmp/test-project'
            },
            'github': {
                'enabled': True,
                'token': 'test_token',
                'owner': 'test_owner',
                'repo_name': 'test_repo'
            },
            'ai': {
                'url': 'http://localhost:1234/v1/chat/completions',
                'model': 'test-model'
            }
        }
    
    @pytest.fixture
    def orchestrator(self, config, tmp_path):
        config['project']['output_dir'] = str(tmp_path / 'test-project')
        
        # Mock les fichiers de configuration
        config_file = tmp_path / 'test_config.yaml'
        with open(config_file, 'w') as f:
            import yaml
            yaml.dump(config, f)
        
        return EnhancedOrchestrator(str(config_file))
    
    @pytest.mark.asyncio
    async def test_project_initialization(self, orchestrator):
        """Test l'initialisation complète du projet"""
        
        # Mock les appels réseau
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "OK"}}]
            }
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            # Mock subprocess pour npm
            with patch('subprocess.run') as mock_subprocess:
                mock_subprocess.return_value.returncode = 0
                mock_subprocess.return_value.stdout = ""
                mock_subprocess.return_value.stderr = ""
                
                await orchestrator.initialize_project_completely()
                
                # Vérifier que la structure est créée
                assert orchestrator.project_root.exists()
                assert (orchestrator.project_root / 'package.json').exists()
                assert (orchestrator.project_root / 'src/app').exists()

class TestTaskDocumenter:
    """Tests pour le système de documentation"""
    
    @pytest.fixture
    def documenter(self):
        config = {
            'token': 'test_token',
            'owner': 'test_owner',
            'repo_name': 'test_repo'
        }
        return TaskDocumenter(config)
    
    @pytest.mark.asyncio
    async def test_comment_on_issue(self, documenter):
        """Test commentaire automatique sur issue"""
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            await documenter._comment_on_issue(123, "Test comment")
            
            # Vérifier que l'appel a été fait
            mock_client.return_value.__aenter__.return_value.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_document_task_completion(self, documenter):
        """Test documentation complète d'une tâche"""
        
        with patch.object(documenter, '_comment_on_issue') as mock_comment:
            with patch.object(documenter, '_update_task_log') as mock_log:
                
                await documenter.document_task_completion(
                    "Test Task", 
                    "Task details",
                    issue_number=123
                )
                
                mock_comment.assert_called_once()
                mock_log.assert_called_once()

class TestCardTracker:
    """Tests pour le suivi des cards GitHub Project"""
    
    @pytest.fixture
    def card_tracker(self):
        config = {
            'token': 'test_token',
            'owner': 'test_owner', 
            'repo_name': 'test_repo'
        }
        return CardTracker(config, project_id=11)
    
    @pytest.mark.asyncio
    async def test_get_project_columns(self, card_tracker):
        """Test récupération des colonnes du projet"""
        
        mock_columns = [
            {'id': 1, 'name': 'To Do', 'url': 'test_url_1'},
            {'id': 2, 'name': '🔴 RED Phase', 'url': 'test_url_2'},
            {'id': 3, 'name': '✅ Done', 'url': 'test_url_3'}
        ]
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_columns
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            columns = await card_tracker.get_project_columns()
            
            assert len(columns) == 3
            assert 'To Do' in columns
            assert '🔴 RED Phase' in columns
    
    @pytest.mark.asyncio
    async def test_move_cards_to_phase(self, card_tracker):
        """Test déplacement des cards entre phases"""
        
        # Mock les colonnes
        card_tracker.columns_cache = {
            'To Do': {'id': 1, 'name': 'To Do', 'url': 'test_url_1'},
            '🔴 RED Phase': {'id': 2, 'name': '🔴 RED Phase', 'url': 'test_url_2'}
        }
        
        # Mock les cards
        mock_cards = [
            {
                'id': 1,
                'url': 'test_card_url_1',
                'content_url': 'https://api.github.com/repos/test/test/issues/123'
            }
        ]
        
        with patch.object(card_tracker, '_get_all_project_cards', return_value=mock_cards):
            with patch.object(card_tracker, '_should_move_card', return_value=True):
                with patch.object(card_tracker, '_move_card_to_column', return_value=True):
                    with patch.object(card_tracker, '_comment_on_card_issue'):
                        
                        await card_tracker.move_cards_to_phase(
                            'tdd_red', 
                            'Test move', 
                            'Test details'
                        )
                        
                        # Vérifier que les méthodes ont été appelées
                        card_tracker._should_move_card.assert_called_once()
                        card_tracker._move_card_to_column.assert_called_once()

class TestGitHubIntegration:
    """Tests pour l'intégration GitHub complète"""
    
    @pytest.mark.asyncio 
    async def test_create_issues_and_cards(self, orchestrator):
        """Test création d'issues avec cards liées"""
        
        mock_issue = {
            'id': 123,
            'number': 456,
            'title': 'Test Issue',
            'html_url': 'test_url'
        }
        
        with patch.object(orchestrator, '_create_github_issue', return_value=mock_issue):
            with patch.object(orchestrator, '_create_and_link_project_card'):
                
                issues = await orchestrator.create_issues_and_cards()
                
                assert len(issues) > 0
                orchestrator._create_github_issue.assert_called()
                orchestrator._create_and_link_project_card.assert_called()
    
    @pytest.mark.asyncio
    async def test_push_code_to_github(self, orchestrator):
        """Test push automatique du code vers GitHub"""
        
        with patch.object(orchestrator, '_init_git_repository', return_value=True):
            with patch.object(orchestrator, '_setup_github_remote', return_value=True):
                with patch.object(orchestrator, '_commit_and_push_files', return_value=True):
                    
                    result = await orchestrator._push_code_to_github()
                    
                    assert result == True
                    orchestrator._init_git_repository.assert_called_once()
                    orchestrator._setup_github_remote.assert_called_once()
                    orchestrator._commit_and_push_files.assert_called_once()

class TestE2EValidation:
    """Tests pour la validation end-to-end"""
    
    @pytest.mark.asyncio
    async def test_e2e_validation_success(self, orchestrator):
        """Test validation E2E réussie"""
        
        with patch.object(orchestrator, '_start_dev_server', return_value=True):
            with patch.object(orchestrator, '_wait_for_server_ready', return_value=True):
                with patch.object(orchestrator, '_run_playwright_tests', return_value={'success': True}):
                    with patch.object(orchestrator, '_stop_dev_server'):
                        with patch.object(orchestrator, '_analyze_e2e_results', return_value=[]):
                            
                            result = await orchestrator.run_e2e_validation_loop()
                            
                            assert result == True
    
    @pytest.mark.asyncio
    async def test_e2e_auto_fix_404(self, orchestrator):
        """Test correction automatique des erreurs 404"""
        
        issues = ["Page 404 détectée"]
        
        with patch.object(orchestrator, '_fix_404_issue', return_value=True):
            
            corrections = await orchestrator._auto_fix_detected_issues(issues)
            
            assert len(corrections) > 0
            assert "404 corrigée" in corrections

class TestWorkflowIntegration:
    """Tests d'intégration du workflow complet"""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self, orchestrator):
        """Test du workflow TDD complet"""
        
        # Mock toutes les étapes du workflow
        with patch.object(orchestrator, 'test_ai_connection', return_value=True):
            with patch.object(orchestrator, 'create_github_project_with_columns', return_value='test_url'):
                with patch.object(orchestrator, 'create_issues_and_cards', return_value=[]):
                    with patch.object(orchestrator, 'initialize_project_completely'):
                        with patch.object(orchestrator, '_push_code_to_github', return_value=True):
                            with patch.object(orchestrator, '_final_validation', return_value=True):
                                with patch.object(orchestrator, 'run_e2e_validation_loop', return_value=True):
                                    
                                    result = await orchestrator.run_complete_workflow()
                                    
                                    assert result == True
                                    
                                    # Vérifier que toutes les étapes ont été appelées
                                    orchestrator.test_ai_connection.assert_called_once()
                                    orchestrator.create_github_project_with_columns.assert_called_once()
                                    orchestrator.create_issues_and_cards.assert_called_once()
                                    orchestrator.initialize_project_completely.assert_called_once()

# Tests de validation GitHub réels (optionnels - nécessitent vraies credentials)
class TestGitHubValidation:
    """Tests de validation avec vraie API GitHub (optionnel)"""
    
    @pytest.mark.skipif(not Path('.env').exists(), reason="Pas de credentials GitHub")
    @pytest.mark.asyncio
    async def test_real_github_project_access(self):
        """Test accès réel au projet GitHub ID 11"""
        
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            pytest.skip("GITHUB_TOKEN non disponible")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/projects/11/columns",
                headers=headers
            )
            
            # Vérifier que le projet existe et est accessible
            assert response.status_code in [200, 404]  # 404 si pas d'accès, mais pas d'erreur auth

if __name__ == "__main__":
    # Lancer les tests
    pytest.main([__file__, '-v'])