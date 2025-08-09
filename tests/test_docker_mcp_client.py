#!/usr/bin/env python3
"""
Tests TDD pour Docker MCP Client
Respecte les principes DDD (Domain-Driven Design) et SOLID
Connexion aux serveurs MCP via Docker Toolkit
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator.mcp.docker_mcp_client import DockerMCPClient
from src.orchestrator.mcp.mcp_interface import MCPInterface


class TestDockerMCPClientDomain:
    """Tests TDD pour le domaine Docker MCP Client"""
    
    def test_docker_mcp_client_implements_mcp_interface(self):
        """DOMAIN: DockerMCPClient doit implémenter MCPInterface"""
        # GIVEN une instance DockerMCPClient
        client = DockerMCPClient(container_name="mcp-filesystem")
        
        # THEN elle doit implémenter l'interface MCPInterface
        assert isinstance(client, MCPInterface)
        
        # AND avoir toutes les méthodes requises
        assert hasattr(client, 'call_tool')
        assert hasattr(client, 'list_tools')
        assert hasattr(client, 'get_resources')
        assert hasattr(client, 'connect')
        assert hasattr(client, 'disconnect')
    
    def test_docker_mcp_client_configuration_validation(self):
        """DOMAIN: Configuration Docker doit être validée"""
        # GIVEN des configurations valides
        valid_configs = [
            {"container_name": "mcp-filesystem"},
            {"container_name": "mcp-web", "docker_host": "unix:///var/run/docker.sock"},
            {"container_name": "mcp-db", "timeout": 30}
        ]
        
        # WHEN on crée des clients avec configs valides
        for config in valid_configs:
            client = DockerMCPClient(**config)
            # THEN aucune exception ne doit être levée
            assert client.container_name is not None
        
        # GIVEN des configurations invalides
        invalid_configs = [
            {},  # container_name manquant
            {"container_name": ""},  # container_name vide
            {"container_name": "test", "timeout": -1},  # timeout négatif
        ]
        
        # WHEN on crée des clients avec configs invalides
        for config in invalid_configs:
            # THEN une exception de validation doit être levée
            with pytest.raises(ValueError):
                DockerMCPClient(**config)


class TestDockerMCPClientConnection:
    """Tests TDD pour la connexion Docker MCP"""
    
    @pytest.mark.asyncio
    async def test_connect_to_docker_container_success(self):
        """CONNECTION: Connexion réussie au conteneur Docker"""
        # GIVEN un client MCP configuré
        client = DockerMCPClient(container_name="mcp-filesystem")
        
        # AND un conteneur Docker qui répond
        mock_docker = MagicMock()
        mock_container = MagicMock()
        mock_container.status = "running"
        mock_container.exec_run.return_value.exit_code = 0
        mock_container.exec_run.return_value.output = b'{"jsonrpc": "2.0", "result": {"capabilities": {}}}'
        
        with patch('docker.from_env', return_value=mock_docker):
            mock_docker.containers.get.return_value = mock_container
            
            # WHEN on se connecte
            result = await client.connect()
        
        # THEN la connexion doit réussir
        assert result is True
        assert client.is_connected is True
        
        # AND Docker doit être interrogé
        mock_docker.containers.get.assert_called_once_with("mcp-filesystem")
    
    @pytest.mark.asyncio
    async def test_connect_to_stopped_container(self):
        """CONNECTION: Gestion d'un conteneur arrêté"""
        # GIVEN un client et un conteneur arrêté
        client = DockerMCPClient(container_name="mcp-stopped")
        
        mock_docker = MagicMock()
        mock_container = MagicMock()
        mock_container.status = "exited"
        
        with patch('docker.from_env', return_value=mock_docker):
            mock_docker.containers.get.return_value = mock_container
            
            # WHEN on tente de se connecter
            # THEN une exception doit être levée
            with pytest.raises(Exception) as exc_info:
                await client.connect()
            
            assert "Container is not running" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_auto_start_container_if_configured(self):
        """CONNECTION: Démarrage automatique du conteneur si configuré"""
        # GIVEN un client avec auto-start activé
        client = DockerMCPClient(
            container_name="mcp-auto-start", 
            auto_start=True
        )
        
        mock_docker = MagicMock()
        mock_container = MagicMock()
        mock_container.status = "exited"
        
        # Mock pour changer le statut après reload
        def mock_reload():
            mock_container.status = "running"
        
        mock_container.reload.side_effect = mock_reload
        
        # Mock pour exec_run (test MCP)
        mock_container.exec_run.return_value.exit_code = 0
        mock_container.exec_run.return_value.output = b'{"jsonrpc":"2.0","id":1,"result":{"capabilities":{}}}'
        
        with patch('docker.from_env', return_value=mock_docker):
            mock_docker.containers.get.return_value = mock_container
            
            # WHEN on se connecte
            await client.connect()
        
        # THEN le conteneur doit être démarré automatiquement
        mock_container.start.assert_called_once()
        mock_container.reload.assert_called_once()


class TestDockerMCPClientToolCalls:
    """Tests TDD pour les appels d'outils MCP"""
    
    @pytest.mark.asyncio
    async def test_call_tool_filesystem_read_success(self):
        """TOOLS: Appel réussi d'un outil filesystem"""
        # GIVEN un client connecté
        client = DockerMCPClient(container_name="mcp-filesystem")
        client._connected = True
        client._container = MagicMock()
        
        # AND une réponse MCP valide
        mcp_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": "File content here"
                    }
                ]
            }
        }
        
        client._container.exec_run.return_value.exit_code = 0
        client._container.exec_run.return_value.output = json.dumps(mcp_response).encode()
        
        # WHEN on appelle l'outil read_file
        result = await client.call_tool(
            tool_name="read_file", 
            arguments={"path": "/test/file.txt"}
        )
        
        # THEN le contenu du fichier doit être retourné
        assert result["content"][0]["text"] == "File content here"
        
        # AND la commande MCP doit être exécutée
        client._container.exec_run.assert_called_once()
        exec_args = client._container.exec_run.call_args[0][0]
        assert "read_file" in ' '.join(exec_args)
    
    @pytest.mark.asyncio
    async def test_call_tool_with_complex_arguments(self):
        """TOOLS: Appel d'outil avec arguments complexes"""
        # GIVEN un client connecté
        client = DockerMCPClient(container_name="mcp-web")
        client._connected = True
        client._container = MagicMock()
        
        # AND des arguments complexes
        complex_args = {
            "url": "https://api.example.com/data",
            "headers": {"Authorization": "Bearer token123"},
            "params": {"limit": 10, "offset": 0},
            "method": "POST",
            "body": {"query": "test data"}
        }
        
        mcp_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"status": "success", "data": {"items": []}}
        }
        
        client._container.exec_run.return_value.exit_code = 0
        client._container.exec_run.return_value.output = json.dumps(mcp_response).encode()
        
        # WHEN on appelle l'outil avec arguments complexes
        result = await client.call_tool(
            tool_name="http_request",
            arguments=complex_args
        )
        
        # THEN l'appel doit réussir
        assert result["status"] == "success"
        
        # AND les arguments doivent être correctement encodés
        exec_call = client._container.exec_run.call_args
        assert "http_request" in ' '.join(exec_call[0][0])
    
    @pytest.mark.asyncio
    async def test_call_tool_mcp_error_handling(self):
        """TOOLS: Gestion des erreurs MCP"""
        # GIVEN un client connecté
        client = DockerMCPClient(container_name="mcp-tools")
        client._connected = True
        client._container = MagicMock()
        
        # WHEN le serveur MCP retourne une erreur
        mcp_error_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": -1,
                "message": "Tool not found",
                "data": {"tool_name": "unknown_tool"}
            }
        }
        
        client._container.exec_run.return_value.exit_code = 0
        client._container.exec_run.return_value.output = json.dumps(mcp_error_response).encode()
        
        # THEN une exception MCP doit être levée
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("unknown_tool", {})
        
        assert "Tool not found" in str(exc_info.value)


class TestDockerMCPClientDiscovery:
    """Tests TDD pour la découverte des outils et ressources"""
    
    @pytest.mark.asyncio
    async def test_list_available_tools(self):
        """DISCOVERY: Liste des outils disponibles"""
        # GIVEN un client connecté
        client = DockerMCPClient(container_name="mcp-toolkit")
        client._connected = True
        client._container = MagicMock()
        
        # AND une réponse avec liste d'outils
        tools_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "tools": [
                    {
                        "name": "read_file",
                        "description": "Read a file from filesystem",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"}
                            }
                        }
                    },
                    {
                        "name": "write_file",
                        "description": "Write content to a file",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"},
                                "content": {"type": "string"}
                            }
                        }
                    }
                ]
            }
        }
        
        client._container.exec_run.return_value.exit_code = 0
        client._container.exec_run.return_value.output = json.dumps(tools_response).encode()
        
        # WHEN on demande la liste des outils
        tools = await client.list_tools()
        
        # THEN on doit obtenir les outils disponibles
        assert len(tools) == 2
        assert tools[0]["name"] == "read_file"
        assert tools[1]["name"] == "write_file"
        assert "inputSchema" in tools[0]
    
    @pytest.mark.asyncio
    async def test_get_resources_from_mcp_server(self):
        """DISCOVERY: Récupération des ressources MCP"""
        # GIVEN un client connecté
        client = DockerMCPClient(container_name="mcp-resources")
        client._connected = True
        client._container = MagicMock()
        
        # AND des ressources disponibles
        resources_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "resources": [
                    {
                        "uri": "file:///app/data/config.json",
                        "name": "Application Config",
                        "mimeType": "application/json"
                    },
                    {
                        "uri": "file:///app/logs/app.log",
                        "name": "Application Logs",
                        "mimeType": "text/plain"
                    }
                ]
            }
        }
        
        client._container.exec_run.return_value.exit_code = 0
        client._container.exec_run.return_value.output = json.dumps(resources_response).encode()
        
        # WHEN on récupère les ressources
        resources = await client.get_resources()
        
        # THEN on doit obtenir la liste des ressources
        assert len(resources) == 2
        assert resources[0]["name"] == "Application Config"
        assert resources[0]["mimeType"] == "application/json"


class TestDockerMCPClientResilience:
    """Tests TDD pour la résilience du client Docker MCP"""
    
    @pytest.mark.asyncio
    async def test_container_restart_during_operation(self):
        """RESILIENCE: Redémarrage du conteneur pendant une opération"""
        # GIVEN un client connecté
        client = DockerMCPClient(
            container_name="mcp-unstable",
            auto_reconnect=True,
            max_retries=3
        )
        client._connected = True
        client._container = MagicMock()
        
        # WHEN le conteneur redémarre pendant un appel
        client._container.exec_run.side_effect = [
            Exception("Container stopped"),  # Premier essai échoue
            Exception("Container not found"),  # Deuxième essai échoue  
            MagicMock(exit_code=0, output=b'{"jsonrpc":"2.0","id":1,"result":{}}')  # Troisième réussit
        ]
        
        # AND mock de la reconnexion
        with patch.object(client, 'connect', new_callable=AsyncMock) as mock_reconnect:
            mock_reconnect.return_value = True
            
            # THEN l'opération doit finalement réussir après reconnexion
            result = await client.call_tool("test_tool", {})
            
            # AND la reconnexion doit être tentée
            assert mock_reconnect.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_docker_daemon_unavailable(self):
        """RESILIENCE: Docker daemon indisponible"""
        # GIVEN un client et un daemon Docker indisponible
        client = DockerMCPClient(container_name="mcp-test")
        
        # WHEN Docker daemon est indisponible
        with patch('docker.from_env') as mock_docker:
            mock_docker.side_effect = Exception("Cannot connect to Docker daemon")
            
            # THEN une exception appropriée doit être levée
            with pytest.raises(Exception) as exc_info:
                await client.connect()
            
            assert "Docker daemon" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_mcp_server_healthcheck(self):
        """RESILIENCE: Vérification de santé du serveur MCP"""
        # GIVEN un client configuré avec health check
        client = DockerMCPClient(
            container_name="mcp-health",
            health_check_enabled=True
        )
        
        # WHEN on vérifie la santé du serveur
        client._connected = True
        client._container = MagicMock()
        client._container.exec_run.return_value.exit_code = 0
        client._container.exec_run.return_value.output = b'{"jsonrpc":"2.0","id":1,"result":{"status":"healthy"}}'
        
        health_status = await client.health_check()
        
        # THEN le statut de santé doit être retourné
        assert health_status["status"] == "healthy"


class TestDockerMCPClientIntegration:
    """Tests d'intégration TDD"""
    
    @pytest.mark.asyncio
    async def test_full_mcp_workflow_filesystem(self):
        """INTEGRATION: Workflow complet avec serveur MCP filesystem"""
        # GIVEN un client filesystem connecté
        client = DockerMCPClient(container_name="mcp-filesystem")
        
        # Mock la connexion et les opérations
        with patch('docker.from_env') as mock_docker_env:
            mock_docker = MagicMock()
            mock_container = MagicMock()
            mock_container.status = "running"
            
            # Réponses pour chaque opération
            responses = [
                b'{"jsonrpc":"2.0","id":1,"result":{"capabilities":{}}}',  # connect
                b'{"jsonrpc":"2.0","id":2,"result":{"tools":[{"name":"read_file"}]}}',  # list_tools
                b'{"jsonrpc":"2.0","id":3,"result":{"content":[{"type":"text","text":"file content"}]}}',  # read_file
                b'{"jsonrpc":"2.0","id":4,"result":{"success":true}}',  # write_file
            ]
            
            mock_container.exec_run.side_effect = [
                MagicMock(exit_code=0, output=resp) for resp in responses
            ]
            
            mock_docker.containers.get.return_value = mock_container
            mock_docker_env.return_value = mock_docker
            
            # WHEN on exécute un workflow complet
            await client.connect()
            tools = await client.list_tools()
            content = await client.call_tool("read_file", {"path": "/test.txt"})
            write_result = await client.call_tool("write_file", {"path": "/output.txt", "content": "new content"})
            
            # THEN toutes les opérations doivent réussir
            assert client.is_connected
            assert len(tools) == 1
            assert content["content"][0]["text"] == "file content"
            assert write_result["success"] is True