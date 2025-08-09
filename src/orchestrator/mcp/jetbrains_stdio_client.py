#!/usr/bin/env python3
"""
JetBrains MCP STDIO Client - Implementation
Connexion au serveur MCP JetBrains via STDIO subprocess
Respecte les principes DDD (Domain-Driven Design) et SOLID
"""

import asyncio
import json
import logging
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path

from .mcp_interface import (
    MCPInterface, MCPError, MCPConnectionError, MCPToolError, MCPResourceError,
    MCPConnectionState
)


class JetBrainsSTDIOClient(MCPInterface):
    """Client pour serveur MCP JetBrains via STDIO - respecte SOLID SRP"""
    
    def __init__(
        self, 
        java_command: str = r"C:\Users\alexi\AppData\Local\Programs\PyCharm Community\jbr\bin\java.exe",
        mcp_port: str = "64342",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        **kwargs
    ):
        # Validation des parametres
        if not java_command or not Path(java_command).exists():
            raise ValueError("java_command doit pointer vers un executable Java valide")
        
        self.java_command = java_command
        self.mcp_port = mcp_port
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self._logger = logging.getLogger(__name__)
        self._process: Optional[subprocess.Popen] = None
        self._connection_state = MCPConnectionState.DISCONNECTED
        self._connected = False
        self._request_counter = 0
        self._capabilities = {}
        
        # Commande complete JetBrains MCP
        self._args = [
            "-classpath",
            r"C:\Users\alexi\AppData\Roaming\JetBrains\PyCharmCE2025.2\plugins\mcpserver\lib\mcpserver-frontend.jar;C:\Users\alexi\AppData\Local\Programs\PyCharm Community\lib\util-8.jar",
            "com.intellij.mcpserver.stdio.McpStdioRunnerKt"
        ]
        
        self._env = {
            "IJ_MCP_SERVER_PORT": self.mcp_port
        }
    
    @property
    def is_connected(self) -> bool:
        """Indique si le client est connecte"""
        return self._connected and self._process and self._process.poll() is None
    
    @property
    def connection_state(self) -> MCPConnectionState:
        """Etat actuel de la connexion"""
        return self._connection_state
    
    def _get_next_request_id(self) -> int:
        """Generer un ID unique pour les requetes MCP"""
        self._request_counter += 1
        return self._request_counter
    
    async def _send_mcp_request(self, method: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Envoyer une requete MCP via STDIO"""
        if not self._process:
            raise MCPConnectionError("Process not started")
        
        request_data = {
            "jsonrpc": "2.0",
            "id": self._get_next_request_id(),
            "method": method
        }
        
        if params:
            request_data["params"] = params
        
        try:
            # Envoyer la requete JSON
            request_json = json.dumps(request_data) + '\n'
            self._logger.debug(f"Sending MCP request: {request_json.strip()}")
            
            self._process.stdin.write(request_json.encode('utf-8'))
            self._process.stdin.flush()
            
            # Lire la reponse
            response_line = await asyncio.wait_for(
                asyncio.to_thread(self._process.stdout.readline),
                timeout=self.timeout
            )
            
            if not response_line:
                raise MCPConnectionError("No response from MCP server")
            
            response_text = response_line.decode('utf-8').strip()
            self._logger.debug(f"Received MCP response: {response_text}")
            
            response = json.loads(response_text)
            
            # Verifier les erreurs MCP
            if "error" in response:
                error = response["error"]
                raise MCPError(
                    f"MCP Error: {error.get('message', 'Unknown error')}",
                    error_code=str(error.get('code', -1)),
                    details=error.get('data', {})
                )
            
            return response
            
        except asyncio.TimeoutError:
            raise MCPConnectionError(f"Request timeout after {self.timeout}s")
        except json.JSONDecodeError as e:
            raise MCPError(f"Invalid JSON response: {e}")
        except Exception as e:
            raise MCPError(f"Request error: {e}")
    
    async def connect(self) -> bool:
        """Se connecter au serveur MCP JetBrains via STDIO"""
        try:
            self._connection_state = MCPConnectionState.CONNECTING
            
            # Lancer le processus Java
            full_command = [self.java_command] + self._args
            self._logger.info(f"Starting JetBrains MCP process: {' '.join(full_command)}")
            
            self._process = subprocess.Popen(
                full_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**dict(os.environ), **self._env},
                text=False,  # Mode binaire pour controler l'encodage
                bufsize=0   # Pas de buffer
            )
            
            # Attendre un peu que le processus demarre
            await asyncio.sleep(2)
            
            # Verifier que le processus est toujours en vie
            if self._process.poll() is not None:
                stderr_output = self._process.stderr.read().decode('utf-8')
                raise MCPConnectionError(f"Process exited immediately: {stderr_output}")
            
            # Initialiser la connexion MCP
            result = await self._send_mcp_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "JetBrainsSTDIOClient", 
                    "version": "1.0.0"
                }
            })
            
            # Verifier la reponse d'initialisation
            if "result" in result:
                self._capabilities = result["result"].get("capabilities", {})
                self._connected = True
                self._connection_state = MCPConnectionState.CONNECTED
                self._logger.info("Connected to JetBrains MCP server via STDIO")
                return True
            else:
                raise MCPConnectionError("Invalid initialization response")
                
        except Exception as e:
            self._connection_state = MCPConnectionState.ERROR
            self._connected = False
            self._logger.error(f"JetBrains MCP STDIO connection failed: {e}")
            
            # Nettoyer le processus en cas d'erreur
            if self._process:
                try:
                    self._process.terminate()
                    await asyncio.sleep(1)
                    if self._process.poll() is None:
                        self._process.kill()
                except:
                    pass
                self._process = None
            
            raise
    
    async def disconnect(self) -> bool:
        """Se deconnecter du serveur MCP"""
        try:
            if self._process:
                # Fermer proprement le processus
                try:
                    self._process.stdin.close()
                    self._process.terminate()
                    await asyncio.sleep(1)
                    if self._process.poll() is None:
                        self._process.kill()
                except:
                    pass
                self._process = None
            
            self._connected = False
            self._connection_state = MCPConnectionState.DISCONNECTED
            self._logger.info("Disconnected from JetBrains MCP server")
            return True
            
        except Exception as e:
            self._logger.error(f"Disconnect error: {e}")
            return False
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Appeler un outil MCP JetBrains"""
        if not self.is_connected:
            raise MCPConnectionError("Not connected to JetBrains MCP server")
        
        try:
            result = await self._send_mcp_request("tools/call", {
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
        if not self.is_connected:
            raise MCPConnectionError("Not connected to JetBrains MCP server")
        
        try:
            result = await self._send_mcp_request("tools/list", {})
            
            if "result" in result and "tools" in result["result"]:
                return result["result"]["tools"]
            else:
                return []
                
        except Exception as e:
            raise MCPError(f"List tools error: {e}")
    
    async def get_resources(self) -> List[Dict[str, Any]]:
        """Recuperer les ressources disponibles"""
        if not self.is_connected:
            raise MCPConnectionError("Not connected to JetBrains MCP server")
        
        try:
            result = await self._send_mcp_request("resources/list", {})
            
            if "result" in result and "resources" in result["result"]:
                return result["result"]["resources"]
            else:
                return []
                
        except Exception as e:
            raise MCPResourceError(f"List resources error: {e}")
    
    async def inspect_code(self, file_path: str, checks: Optional[List[str]] = None) -> Dict[str, Any]:
        """Inspecter du code avec PyCharm (outil specialise JetBrains)"""
        arguments = {"file_path": file_path}
        if checks:
            arguments["checks"] = checks
        
        return await self.call_tool("inspect_code", arguments)
    
    async def debug_code(self, file_path: str, line_number: int, variables: Optional[List[str]] = None) -> Dict[str, Any]:
        """Deboguer du code avec PyCharm (outil specialise JetBrains)"""
        arguments = {
            "file_path": file_path,
            "line_number": line_number
        }
        if variables:
            arguments["variables"] = variables
        
        return await self.call_tool("debug_code", arguments)
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifier la sante du serveur MCP JetBrains"""
        try:
            if not self.is_connected:
                return {
                    "status": "unhealthy",
                    "error": "Not connected"
                }
            
            # Test avec list_tools
            tools = await self.list_tools()
            
            return {
                "status": "healthy",
                "java_command": self.java_command,
                "mcp_port": self.mcp_port,
                "tools_count": len(tools),
                "capabilities": self._capabilities,
                "connection_state": self._connection_state.value,
                "process_alive": self._process.poll() is None if self._process else False
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "java_command": self.java_command
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


# Import os pour les variables d'environnement
import os