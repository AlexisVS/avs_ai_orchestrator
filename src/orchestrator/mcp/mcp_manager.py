"""
MCP Manager - Gestionnaire des serveurs MCP
Implementation minimale pour faire passer les tests
"""

from typing import List, Dict, Any, Optional
import asyncio


class MCPManager:
    """Gestionnaire pour la decouverte et gestion des serveurs MCP"""
    
    def __init__(self):
        self.servers: List[Dict[str, Any]] = []
        self.active_connections = {}
    
    async def discover_services(self) -> List[Dict[str, Any]]:
        """Decouvrir les services MCP disponibles"""
        discovered = []
        
        try:
            # Dans la vraie implementation, on utiliserait Docker API
            # Pour les tests, on retourne un service mock
            import docker
            client = docker.from_env()
            containers = client.containers.list()
            
            for container in containers:
                if container.labels.get("mcp.enabled") == "true":
                    # Extraire l'IP du conteneur
                    networks = container.attrs["NetworkSettings"]["Networks"]
                    ip = None
                    for network in networks.values():
                        if network.get("IPAddress"):
                            ip = network["IPAddress"]
                            break
                    
                    if ip:
                        discovered.append({
                            "name": container.name,
                            "ip": ip,
                            "labels": container.labels
                        })
        except Exception as e:
            print(f"Erreur decouverte services: {e}")
            # Retourner un service par defaut pour les tests
            pass
        
        return discovered
    
    async def connect_to_server(self, server_info: Dict[str, Any]) -> bool:
        """Se connecter a un serveur MCP"""
        from .mcp_client import MCPClient
        
        try:
            client = MCPClient(
                host=server_info.get("ip", "localhost"),
                port=server_info.get("port", 8080)
            )
            
            result = await client.connect()
            if result:
                self.active_connections[server_info["name"]] = client
            
            return result
        except Exception as e:
            print(f"Erreur connexion serveur {server_info.get('name')}: {e}")
            return False
    
    async def disconnect_all(self):
        """Deconnecter tous les serveurs"""
        for name, client in self.active_connections.items():
            try:
                await client.disconnect()
            except Exception as e:
                print(f"Erreur deconnexion {name}: {e}")
        
        self.active_connections.clear()
    
    def get_active_servers(self) -> List[str]:
        """Obtenir la liste des serveurs actifs"""
        return list(self.active_connections.keys())
    
    async def send_to_server(self, server_name: str, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Envoyer un message a un serveur specifique"""
        client = self.active_connections.get(server_name)
        if not client:
            return None
        
        try:
            return await client.send_message(message)
        except Exception as e:
            print(f"Erreur envoi message a {server_name}: {e}")
            return None