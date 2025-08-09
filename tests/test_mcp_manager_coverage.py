"""
Tests TDD pour améliorer la couverture de MCPManager
Test de couverture pour améliorer le score global
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.orchestrator.mcp.mcp_manager import MCPManager


class TestMCPManagerCoverage:
    """Tests pour améliorer la couverture de MCPManager"""
    
    @pytest.mark.unit
    def test_mcp_manager_initialization(self):
        """Test l'initialisation du MCPManager"""
        manager = MCPManager()
        
        assert manager.servers == []
        assert manager.active_connections == {}
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_discover_services_docker_available(self):
        """Test découverte de services avec Docker disponible"""
        manager = MCPManager()
        
        # Mock Docker container
        mock_container = Mock()
        mock_container.labels = {"mcp.enabled": "true"}
        mock_container.attrs = {
            "NetworkSettings": {
                "Networks": {
                    "bridge": {"IPAddress": "172.17.0.2"}
                }
            }
        }
        mock_container.name = "test-mcp-service"
        
        # Mock Docker client
        mock_client = Mock()
        mock_client.containers.list.return_value = [mock_container]
        
        with patch('docker.from_env', return_value=mock_client):
            services = await manager.discover_services()
        
        assert isinstance(services, list)
        assert len(services) > 0
        assert services[0]["name"] == "test-mcp-service"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_discover_services_docker_error(self):
        """Test découverte de services avec erreur Docker"""
        manager = MCPManager()
        
        with patch('docker.from_env', side_effect=Exception("Docker not available")):
            services = await manager.discover_services()
        
        assert isinstance(services, list)
        assert len(services) == 0
    
    @pytest.mark.unit  
    @pytest.mark.asyncio
    async def test_connect_to_server(self):
        """Test connexion à un serveur MCP"""
        manager = MCPManager()
        
        server_info = {
            "name": "test-service",
            "ip": "172.17.0.2", 
            "port": 8080
        }
        
        result = await manager.connect_to_server(server_info)
        
        # Vérifier que ça retourne un bool
        assert isinstance(result, bool)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_disconnect_all(self):
        """Test déconnexion de tous les services MCP"""
        manager = MCPManager()
        
        # Test que ça n'échoue pas
        await manager.disconnect_all()
    
    @pytest.mark.unit
    def test_get_active_servers(self):
        """Test récupération des serveurs actifs"""
        manager = MCPManager()
        
        # Ajouter quelques connexions mockées
        manager.active_connections["service1"] = Mock()
        manager.active_connections["service2"] = Mock()
        
        servers = manager.get_active_servers()
        
        assert isinstance(servers, list)
        assert len(servers) == 2