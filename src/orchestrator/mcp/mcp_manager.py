"""
MCP Manager - Gestionnaire des serveurs MCP
Implémentation minimale pour faire passer les tests
"""

from typing import List, Dict, Any, Optional
import asyncio


class MCPManager:
    """Gestionnaire pour la découverte et gestion des serveurs MCP"""
    
    def __init__(self):
        self.servers: List[Dict[str, Any]] = []
        self.active_connections = {}
    
    async def discover_services(self) -> List[Dict[str, Any]]:
        """Découvrir les services MCP disponibles"""
        discovered = []
        
        try:
            # Dans la vraie implémentation, on utiliserait Docker API
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
            print(f"Erreur découverte services: {e}")
            # Retourner un service par défaut pour les tests
            pass
        
        return discovered
    
    async def connect_to_server(self, server_info: Dict[str, Any]) -> bool:
        """Se connecter à un serveur MCP"""
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
        """Déconnecter tous les serveurs"""
        for name, client in self.active_connections.items():
            try:
                await client.disconnect()
            except Exception as e:
                print(f"Erreur déconnexion {name}: {e}")
        
        self.active_connections.clear()
    
    def get_active_servers(self) -> List[str]:
        """Obtenir la liste des serveurs actifs"""
        return list(self.active_connections.keys())
    
    async def send_to_server(self, server_name: str, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Envoyer un message à un serveur spécifique"""
        client = self.active_connections.get(server_name)
        if not client:
            return None
        
        try:
            return await client.send_message(message)
        except Exception as e:
            print(f"Erreur envoi message à {server_name}: {e}")
            return None