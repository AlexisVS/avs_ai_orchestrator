#!/usr/bin/env python3
"""
JetBrains MCP Client - Implementation SSE
Connexion au serveur MCP JetBrains via Server-Sent Events
Respecte les principes DDD (Domain-Driven Design) et SOLID
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
import aiohttp
from urllib.parse import urljoin

from .mcp_interface import (
    MCPInterface, MCPError, MCPConnectionError, MCPToolError, MCPResourceError,
    MCPConnectionState
)


class JetBrainsMCPClient(MCPInterface):
    """Client pour serveur MCP JetBrains via SSE - respecte SOLID SRP"""
    
    def __init__(
        self, 
        sse_url: str = "http://localhost:64342/sse",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        **kwargs
    ):
        # Validation de l'URL SSE
        if not sse_url or not sse_url.startswith(('http://', 'https://')):
            raise ValueError("sse_url doit être une URL HTTP valide")
        
        self.sse_url = sse_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self._logger = logging.getLogger(__name__)
        self._session: Optional[aiohttp.ClientSession] = None
        self._connection_state = MCPConnectionState.DISCONNECTED
        self._connected = False
        self._request_counter = 0
        self._capabilities = {}
    
    @property
    def is_connected(self) -> bool:
        """Indique si le client est connecté"""
        return self._connected
    
    @property
    def connection_state(self) -> MCPConnectionState:
        """État actuel de la connexion"""
        return self._connection_state
    
    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Assurer qu'une session HTTP existe"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session
    
    def _get_next_request_id(self) -> int:
        """Générer un ID unique pour les requêtes MCP"""
        self._request_counter += 1
        return self._request_counter
    
    async def _make_mcp_request(self, method: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Faire une requête MCP via HTTP POST"""
        session = await self._ensure_session()
        
        request_data = {
            "jsonrpc": "2.0",
            "id": self._get_next_request_id(),
            "method": method
        }
        
        if params:
            request_data["params"] = params
        
        try:
            # Utiliser POST pour envoyer la requête MCP
            api_url = self.sse_url.replace('/sse', '/api')  # Assuming API endpoint
            
            async with session.post(api_url, json=request_data) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Vérifier les erreurs MCP
                    if "error" in result:
                        error = result["error"]
                        raise MCPError(
                            f"MCP Error: {error.get('message', 'Unknown error')}",
                            error_code=str(error.get('code', -1)),
                            details=error.get('data', {})
                        )
                    
                    return result
                else:
                    error_text = await response.text()
                    raise MCPConnectionError(f"HTTP Error {response.status}: {error_text}")
                    
        except aiohttp.ClientError as e:
            raise MCPConnectionError(f"Connection error: {e}")
    
    async def connect(self) -> bool:
        """Se connecter au serveur MCP JetBrains"""
        try:
            self._connection_state = MCPConnectionState.CONNECTING
            
            # Initialiser la connexion MCP
            result = await self._make_mcp_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "JetBrainsMCPClient", 
                    "version": "1.0.0"
                }
            })
            
            # Vérifier la réponse d'initialisation
            if "result" in result:
                self._capabilities = result["result"].get("capabilities", {})
                self._connected = True
                self._connection_state = MCPConnectionState.CONNECTED
                self._logger.info(f"Connected to JetBrains MCP server: {self.sse_url}")
                return True
            else:
                raise MCPConnectionError("Invalid initialization response")
                
        except Exception as e:
            self._connection_state = MCPConnectionState.ERROR
            self._connected = False
            self._logger.error(f"JetBrains MCP connection failed: {e}")
            raise
    
    async def disconnect(self) -> bool:
        """Se déconnecter du serveur MCP"""
        try:
            if self._connected:
                self._connected = False
                self._connection_state = MCPConnectionState.DISCONNECTED
                self._logger.info("Disconnected from JetBrains MCP server")
            
            if self._session and not self._session.closed:
                await self._session.close()
                self._session = None
            
            return True
            
        except Exception as e:
            self._logger.error(f"Disconnect error: {e}")
            return False
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Appeler un outil MCP JetBrains"""
        if not self._connected:
            raise MCPConnectionError("Not connected to JetBrains MCP server")
        
        try:
            result = await self._make_mcp_request("tools/call", {
                "name": tool_name,
                "arguments": arguments
            })
            
            if "result" in result:
                return result["result"]
            else:
                raise MCPToolError(f"No result for tool {tool_name}", tool_name=tool_name)
                
        except MCPError:
            raise
        except Exception as e:
            raise MCPToolError(f"Tool call error: {e}", tool_name=tool_name)
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """Lister les outils disponibles"""
        if not self._connected:
            raise MCPConnectionError("Not connected to JetBrains MCP server")
        
        try:
            result = await self._make_mcp_request("tools/list", {})
            
            if "result" in result and "tools" in result["result"]:
                return result["result"]["tools"]
            else:
                return []
                
        except Exception as e:
            raise MCPError(f"List tools error: {e}")
    
    async def get_resources(self) -> List[Dict[str, Any]]:
        """Récupérer les ressources disponibles"""
        if not self._connected:
            raise MCPConnectionError("Not connected to JetBrains MCP server")
        
        try:
            result = await self._make_mcp_request("resources/list", {})
            
            if "result" in result and "resources" in result["result"]:
                return result["result"]["resources"]
            else:
                return []
                
        except Exception as e:
            raise MCPResourceError(f"List resources error: {e}")
    
    async def inspect_code(self, file_path: str, checks: Optional[List[str]] = None) -> Dict[str, Any]:
        """Inspecter du code avec PyCharm (outil spécialisé JetBrains)"""
        arguments = {"file_path": file_path}
        if checks:
            arguments["checks"] = checks
        
        return await self.call_tool("inspect_code", arguments)
    
    async def debug_code(self, file_path: str, line_number: int, variables: Optional[List[str]] = None) -> Dict[str, Any]:
        """Déboguer du code avec PyCharm (outil spécialisé JetBrains)"""
        arguments = {
            "file_path": file_path,
            "line_number": line_number
        }
        if variables:
            arguments["variables"] = variables
        
        return await self.call_tool("debug_code", arguments)
    
    async def refactor_code(self, file_path: str, refactor_type: str, **kwargs) -> Dict[str, Any]:
        """Refactoriser du code avec PyCharm (outil spécialisé JetBrains)"""
        arguments = {
            "file_path": file_path,
            "refactor_type": refactor_type,
            **kwargs
        }
        
        return await self.call_tool("refactor_code", arguments)
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérifier la santé du serveur MCP JetBrains"""
        try:
            if not self._connected:
                return {
                    "status": "unhealthy",
                    "error": "Not connected"
                }
            
            # Test avec list_tools
            tools = await self.list_tools()
            
            return {
                "status": "healthy",
                "sse_url": self.sse_url,
                "tools_count": len(tools),
                "capabilities": self._capabilities,
                "connection_state": self._connection_state.value
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "sse_url": self.sse_url
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


# Factory Pattern pour création de clients selon DDD
class JetBrainsMCPClientFactory:
    """Factory pour créer des instances de JetBrainsMCPClient"""
    
    @staticmethod
    def create_client(config: Dict[str, Any]) -> JetBrainsMCPClient:
        """Créer un client JetBrains MCP à partir d'une configuration"""
        required_fields = ["sse_url"]
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Configuration manquante: {field}")
        
        return JetBrainsMCPClient(**config)
    
    @staticmethod
    def create_from_env() -> JetBrainsMCPClient:
        """Créer un client à partir des variables d'environnement"""
        import os
        
        sse_url = os.getenv("JETBRAINS_MCP_SSE_URL", "http://localhost:64342/sse")
        
        config = {
            "sse_url": sse_url
        }
        
        return JetBrainsMCPClient(**config)