#!/usr/bin/env python3
"""
Docker MCP Client - Implementation
Connexion aux serveurs MCP via Docker Toolkit
Respecte les principes DDD (Domain-Driven Design) et SOLID
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, TYPE_CHECKING

# Import conditionnel pour eviter les erreurs si docker n'est pas installe
try:
    import docker
    from docker.errors import NotFound, APIError
    DOCKER_AVAILABLE = True
except ImportError:
    # Mock Docker classes si docker n'est pas installe
    DOCKER_AVAILABLE = False
    
    class NotFound(Exception):
        pass
    
    class APIError(Exception):
        pass
    
    # Type stub pour les annotations
    if TYPE_CHECKING:
        import docker

from .mcp_interface import (
    MCPInterface, MCPError, MCPConnectionError, MCPToolError, MCPResourceError,
    MCPConfiguration, MCPConnectionState, MCPToolMetadata, MCPResource
)


class DockerMCPClient(MCPInterface):
    """Client pour serveurs MCP Docker - respecte SOLID SRP"""
    
    def __init__(
        self, 
        container_name: Optional[str] = None,
        docker_host: str = "unix:///var/run/docker.sock",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        auto_start: bool = False,
        auto_reconnect: bool = True,
        health_check_enabled: bool = True,
        **kwargs
    ):
        # Validation explicite pour respecter les tests
        if not container_name:
            raise ValueError("container_name doit etre une string non-vide")
        # Utiliser le Value Object de configuration
        self._config = MCPConfiguration(
            container_name=container_name,
            docker_host=docker_host,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            auto_start=auto_start,
            auto_reconnect=auto_reconnect,
            health_check_enabled=health_check_enabled,
            **kwargs
        )
        
        self._logger = logging.getLogger(__name__)
        self._docker_client = None  # Optional[docker.DockerClient] = None
        self._container = None  # Optional[docker.models.containers.Container] = None
        self._connection_state = MCPConnectionState.DISCONNECTED
        self._connected = False
        self._request_counter = 0
    
    @property
    def container_name(self) -> str:
        """Propriete pour acces au nom du conteneur"""
        return self._config.container_name
    
    @property
    def is_connected(self) -> bool:
        """Indique si le client est connecte"""
        return self._connected
    
    @property
    def connection_state(self) -> MCPConnectionState:
        """Etat actuel de la connexion"""
        return self._connection_state
    
    def _get_docker_client(self) -> "docker.DockerClient":
        """Obtenir le client Docker"""
        if not DOCKER_AVAILABLE:
            raise MCPConnectionError("Docker package not installed. Please install with: pip install docker")
        
        if self._docker_client is None:
            try:
                self._docker_client = docker.from_env()
            except Exception as e:
                raise MCPConnectionError(f"Cannot connect to Docker daemon: {e}")
        
        return self._docker_client
    
    async def connect(self) -> bool:
        """Se connecter au conteneur Docker MCP"""
        try:
            self._connection_state = MCPConnectionState.CONNECTING
            
            # Obtenir le client Docker
            docker_client = self._get_docker_client()
            
            # Recuperer le conteneur
            try:
                self._container = docker_client.containers.get(self._config.container_name)
            except NotFound:
                if self._config.auto_start:
                    # Tenter de creer/demarrer le conteneur (logique simplifiee)
                    raise MCPConnectionError(f"Container '{self._config.container_name}' not found and auto-start not implemented")
                else:
                    raise MCPConnectionError(f"Container '{self._config.container_name}' not found")
            
            # Verifier l'etat du conteneur
            if self._container.status != "running":
                if self._config.auto_start:
                    self._logger.info(f"Starting container {self._config.container_name}")
                    self._container.start()
                    # Attendre que le conteneur demarre
                    await asyncio.sleep(2)
                    self._container.reload()
                    
                    if self._container.status != "running":
                        raise MCPConnectionError(f"Container failed to start: {self._container.status}")
                else:
                    raise MCPConnectionError(f"Container is not running: {self._container.status}")
            
            # Tester la connexion MCP
            try:
                test_request = {
                    "jsonrpc": "2.0",
                    "id": self._get_next_request_id(),
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "DockerMCPClient",
                            "version": "1.0.0"
                        }
                    }
                }
                
                result = self._execute_mcp_command(test_request)
                
                # Verifier la reponse
                if result.get("jsonrpc") == "2.0" and "result" in result:
                    self._connected = True
                    self._connection_state = MCPConnectionState.CONNECTED
                    self._logger.info(f"Connected to MCP server in container {self._config.container_name}")
                    return True
                else:
                    raise MCPConnectionError(f"Invalid MCP response: {result}")
                    
            except Exception as e:
                raise MCPConnectionError(f"MCP server test failed: {e}")
                
        except Exception as e:
            self._connection_state = MCPConnectionState.ERROR
            self._connected = False
            self._logger.error(f"Connection failed: {e}")
            raise
    
    async def disconnect(self) -> bool:
        """Se deconnecter du serveur MCP"""
        try:
            if self._connected:
                self._connected = False
                self._connection_state = MCPConnectionState.DISCONNECTED
                self._logger.info(f"Disconnected from MCP server in container {self._config.container_name}")
            
            if self._docker_client:
                self._docker_client.close()
                self._docker_client = None
            
            return True
            
        except Exception as e:
            self._logger.error(f"Disconnect error: {e}")
            return False
    
    def _get_next_request_id(self) -> int:
        """Generer un ID unique pour les requetes MCP"""
        self._request_counter += 1
        return self._request_counter
    
    def _execute_mcp_command(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Executer une commande MCP dans le conteneur"""
        if not self._container:
            raise MCPConnectionError("No container connection")
        
        try:
            # Construire la commande MCP
            cmd = [
                "python", "-c", 
                f"import json; import sys; sys.stdout.write(json.dumps({json.dumps(request)}))"
            ]
            
            # Executer dans le conteneur
            exec_result = self._container.exec_run(
                cmd,
                stdout=True,
                stderr=True,
                demux=True
            )
            
            if exec_result.exit_code != 0:
                error_msg = exec_result.output.decode() if exec_result.output else "Unknown error"
                raise MCPError(f"Command execution failed: {error_msg}")
            
            # Parser la reponse JSON
            response_text = exec_result.output.decode().strip()
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            raise MCPError(f"Invalid JSON response: {e}")
        except Exception as e:
            raise MCPError(f"Command execution error: {e}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Appeler un outil MCP avec retry et reconnexion automatique"""
        if not self._connected:
            raise MCPConnectionError("Not connected to MCP server")
        
        for attempt in range(self._config.max_retries):
            try:
                request = {
                    "jsonrpc": "2.0",
                    "id": self._get_next_request_id(),
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments
                    }
                }
                
                response = self._execute_mcp_command(request)
                
                # Verifier les erreurs MCP
                if "error" in response:
                    error = response["error"]
                    raise MCPToolError(
                        f"Tool call failed: {error.get('message', 'Unknown error')}",
                        tool_name=tool_name,
                        error_code=str(error.get('code', -1)),
                        details=error.get('data', {})
                    )
                
                if "result" in response:
                    return response["result"]
                else:
                    raise MCPToolError(f"No result in response for tool {tool_name}", tool_name=tool_name)
                    
            except MCPToolError:
                raise  # Ne pas retry sur les erreurs MCP
            except Exception as e:
                if attempt == self._config.max_retries - 1:
                    raise MCPToolError(f"Tool call error: {e}", tool_name=tool_name)
                
                # Tentative de reconnexion si configuree
                if self._config.auto_reconnect:
                    self._logger.warning(f"Tool call failed (attempt {attempt + 1}), trying to reconnect: {e}")
                    try:
                        await self.connect()
                        await asyncio.sleep(self._config.retry_delay)
                        continue  # Retry l'operation
                    except Exception as reconnect_error:
                        self._logger.error(f"Reconnection failed: {reconnect_error}")
                
                await asyncio.sleep(self._config.retry_delay)
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """Lister les outils disponibles"""
        if not self._connected:
            raise MCPConnectionError("Not connected to MCP server")
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": self._get_next_request_id(),
                "method": "tools/list",
                "params": {}
            }
            
            response = self._execute_mcp_command(request)
            
            if "error" in response:
                error = response["error"]
                raise MCPError(f"List tools failed: {error.get('message', 'Unknown error')}")
            
            if "result" in response and "tools" in response["result"]:
                return response["result"]["tools"]
            else:
                return []
                
        except Exception as e:
            raise MCPError(f"List tools error: {e}")
    
    async def get_resources(self) -> List[Dict[str, Any]]:
        """Recuperer les ressources disponibles"""
        if not self._connected:
            raise MCPConnectionError("Not connected to MCP server")
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": self._get_next_request_id(),
                "method": "resources/list",
                "params": {}
            }
            
            response = self._execute_mcp_command(request)
            
            if "error" in response:
                error = response["error"]
                raise MCPResourceError(f"List resources failed: {error.get('message', 'Unknown error')}")
            
            if "result" in response and "resources" in response["result"]:
                return response["result"]["resources"]
            else:
                return []
                
        except Exception as e:
            raise MCPResourceError(f"List resources error: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifier la sante du serveur MCP"""
        if not self._config.health_check_enabled:
            return {"status": "disabled"}
        
        try:
            if not self._connected:
                return {
                    "status": "unhealthy",
                    "error": "Not connected"
                }
            
            # Test simple avec list_tools
            tools = await self.list_tools()
            
            return {
                "status": "healthy",
                "container_name": self._config.container_name,
                "tools_count": len(tools),
                "connection_state": self._connection_state.value
            }
            
        except Exception as e:
            return {
                "status": "unhealthy", 
                "error": str(e),
                "container_name": self._config.container_name
            }
    
    async def close(self):
        """Fermer toutes les connexions"""
        await self.disconnect()
    
    async def __aenter__(self):
        """Support du context manager async"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Nettoyage du context manager async"""
        await self.close()


# Factory Pattern pour creation de clients selon DDD
class DockerMCPClientFactory:
    """Factory pour creer des instances de DockerMCPClient"""
    
    @staticmethod
    def create_client(config: Dict[str, Any]) -> DockerMCPClient:
        """Creer un client Docker MCP a partir d'une configuration"""
        required_fields = ["container_name"]
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Configuration manquante: {field}")
        
        return DockerMCPClient(**config)
    
    @staticmethod
    def create_from_env() -> DockerMCPClient:
        """Creer un client a partir des variables d'environnement"""
        import os
        
        container_name = os.getenv("MCP_CONTAINER_NAME")
        if not container_name:
            raise ValueError("MCP_CONTAINER_NAME environment variable required")
        
        docker_host = os.getenv("DOCKER_HOST", "unix:///var/run/docker.sock")
        auto_start = os.getenv("MCP_AUTO_START", "false").lower() == "true"
        
        config = {
            "container_name": container_name,
            "docker_host": docker_host,
            "auto_start": auto_start
        }
        
        return DockerMCPClient(**config)