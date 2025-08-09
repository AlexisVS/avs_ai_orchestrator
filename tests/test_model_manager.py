"""
Tests TDD pour le Model Manager
Phase RED : Ces tests doivent echouer initialement
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path


class TestModelManager:
    """Tests pour le gestionnaire de modeles AI"""
    
    @pytest.mark.unit
    def test_model_manager_initialization(self, mock_config):
        """Test l'initialisation du gestionnaire de modeles"""
        # GIVEN une configuration avec modeles
        from orchestrator.models.model_manager import ModelManager
        
        # WHEN on cree un gestionnaire de modeles
        manager = ModelManager(mock_config)
        
        # THEN le gestionnaire doit etre initialise
        assert manager is not None
        assert hasattr(manager, 'config')
        assert hasattr(manager, 'active_models')
        assert hasattr(manager, 'docker_models')
        assert hasattr(manager, 'lm_studio_models')
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_connect_docker_models(self, mock_config, mock_docker_client):
        """Test la connexion aux modeles Docker"""
        # GIVEN un gestionnaire avec Docker configure
        from orchestrator.models.model_manager import ModelManager
        
        # Mock DockerMCPClient
        mock_docker_mcp_client = AsyncMock()
        mock_docker_mcp_client.connect = AsyncMock(return_value=True)
        
        with patch('orchestrator.models.model_manager.DockerMCPClient', return_value=mock_docker_mcp_client):
            manager = ModelManager(mock_config)
            
            # WHEN on connecte les modeles Docker
            result = await manager.connect_docker_models()
            
            # THEN la connexion doit reussir
            assert result is True
            assert len(manager.docker_models) >= 0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_connect_lm_studio(self, mock_config, mock_lm_studio_client):
        """Test la connexion a LM Studio"""
        # GIVEN un gestionnaire avec LM Studio configure
        from orchestrator.models.model_manager import ModelManager
        
        with patch('orchestrator.models.model_manager.LMStudioClient', return_value=mock_lm_studio_client):
            manager = ModelManager(mock_config)
            
            # WHEN on connecte LM Studio
            result = await manager.connect_lm_studio()
            
            # THEN la connexion doit reussir
            assert result is True
            mock_lm_studio_client.health_check.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_select_best_model(self, mock_config):
        """Test la selection du meilleur modele"""
        # GIVEN un gestionnaire avec plusieurs modeles
        from orchestrator.models.model_manager import ModelManager
        
        manager = ModelManager(mock_config)
        manager.active_models = [
            {"name": "model1", "type": "docker", "load": 0.5},
            {"name": "model2", "type": "lm_studio", "load": 0.2},
            {"name": "model3", "type": "docker", "load": 0.8}
        ]
        
        # WHEN on selectionne le meilleur modele
        best_model = await manager.select_best_model()
        
        # THEN le modele avec la charge la plus faible doit etre selectionne
        assert best_model is not None
        assert best_model["name"] == "model2"
        assert best_model["load"] == 0.2
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_load_balancing(self, mock_config):
        """Test le load balancing entre modeles"""
        # GIVEN un gestionnaire avec plusieurs requetes
        from orchestrator.models.model_manager import ModelManager
        
        manager = ModelManager(mock_config)
        manager.active_models = [
            {"name": "model1", "type": "docker", "capacity": 10},
            {"name": "model2", "type": "docker", "capacity": 10}
        ]
        
        # WHEN on distribue plusieurs requetes
        assignments = []
        for _ in range(10):
            model = await manager.assign_request()
            assignments.append(model["name"])
        
        # THEN les requetes doivent etre distribuees equitablement
        assert assignments.count("model1") > 0
        assert assignments.count("model2") > 0
        assert abs(assignments.count("model1") - assignments.count("model2")) <= 2
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_model_health_check(self, mock_config):
        """Test la verification de sante des modeles"""
        # GIVEN un gestionnaire avec modeles
        from orchestrator.models.model_manager import ModelManager
        
        manager = ModelManager(mock_config)
        manager.active_models = [
            {"name": "healthy", "status": "running"},
            {"name": "unhealthy", "status": "error"}
        ]
        
        # WHEN on verifie la sante des modeles
        healthy_models = await manager.check_models_health()
        
        # THEN seuls les modeles sains doivent etre retournes
        assert len(healthy_models) == 1
        assert healthy_models[0]["name"] == "healthy"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_failover_mechanism(self, mock_config):
        """Test le mecanisme de failover"""
        # GIVEN un modele principal defaillant
        from orchestrator.models.model_manager import ModelManager
        
        manager = ModelManager(mock_config)
        manager.primary_model = {"name": "primary", "status": "error"}
        manager.backup_models = [
            {"name": "backup1", "status": "running"},
            {"name": "backup2", "status": "running"}
        ]
        
        # WHEN le modele principal echoue
        active_model = await manager.get_active_model()
        
        # THEN un modele de backup doit etre utilise
        assert active_model["name"] in ["backup1", "backup2"]
        assert active_model["status"] == "running"
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_generate_with_retry(self, mock_config, mock_ai_client):
        """Test la generation avec retry automatique"""
        # GIVEN un gestionnaire avec retry configure
        from orchestrator.models.model_manager import ModelManager
        
        manager = ModelManager(mock_config)
        manager.max_retries = 3
        
        # Simuler une erreur puis succes
        mock_ai_client.generate_response.side_effect = [
            Exception("Error 1"),
            Exception("Error 2"),
            "Success response"
        ]
        
        with patch.object(manager, 'get_client', return_value=mock_ai_client):
            # WHEN on genere avec retry
            response = await manager.generate_with_retry("test prompt")
            
            # THEN la reponse doit etre obtenue apres retries
            assert response == "Success response"
            assert mock_ai_client.generate_response.call_count == 3
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_model_switching_on_error(self, mock_config):
        """Test le changement de modele en cas d'erreur"""
        # GIVEN un modele qui echoue
        from orchestrator.models.model_manager import ModelManager
        
        manager = ModelManager(mock_config)
        failing_model = {"name": "failing", "errors": 0, "max_errors": 3}
        
        # WHEN des erreurs se produisent
        for _ in range(4):
            await manager.report_model_error(failing_model)
        
        # THEN le modele doit etre desactive
        assert failing_model["errors"] > failing_model["max_errors"]
        assert failing_model not in manager.active_models
    
    @pytest.mark.unit
    def test_model_configuration_validation(self, mock_config):
        """Test la validation de la configuration des modeles"""
        # GIVEN des configurations de modeles variees
        from orchestrator.models.model_manager import ModelManager
        
        valid_config = {
            "name": "test-model",
            "type": "docker",
            "endpoint": "http://localhost:8080"
        }
        
        invalid_config = {
            "name": "invalid",
            # type manquant
        }
        
        manager = ModelManager(mock_config)
        
        # WHEN on valide les configurations
        valid_result = manager.validate_model_config(valid_config)
        invalid_result = manager.validate_model_config(invalid_config)
        
        # THEN la validation doit etre correcte
        assert valid_result is True
        assert invalid_result is False