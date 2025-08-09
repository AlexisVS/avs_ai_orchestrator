"""
MCP Router - Routage des messages vers les bons serveurs
Implémentation minimale pour faire passer les tests
"""

from typing import Dict, Any, Optional, List


class MCPRouter:
    """Routeur pour diriger les messages vers les serveurs appropriés"""
    
    def __init__(self):
        self.servers: Dict[str, Any] = {}
        self.routes = {}
    
    async def route_message(self, message: Dict[str, Any]) -> Optional[Any]:
        """Router un message vers le bon serveur selon son type"""
        message_type = message.get("type", "")
        
        # Routage simple basé sur le type
        if "code" in message_type:
            return self.servers.get("code")
        elif "text" in message_type:
            return self.servers.get("text")
        elif "tools" in message_type:
            return self.servers.get("tools")
        
        # Par défaut, retourner le premier serveur disponible
        if self.servers:
            return next(iter(self.servers.values()))
        
        return None
    
    def register_server(self, name: str, server: Any, capabilities: List[str] = None):
        """Enregistrer un serveur avec ses capacités"""
        self.servers[name] = server
        if hasattr(server, 'capabilities'):
            server.capabilities = capabilities or []
    
    def unregister_server(self, name: str):
        """Désenregistrer un serveur"""
        if name in self.servers:
            del self.servers[name]
    
    def get_server_for_capability(self, capability: str) -> Optional[Any]:
        """Obtenir un serveur selon une capacité requise"""
        for name, server in self.servers.items():
            if hasattr(server, 'capabilities') and capability in server.capabilities:
                return server
        return None
    
    def list_servers(self) -> List[str]:
        """Lister tous les serveurs enregistrés"""
        return list(self.servers.keys())