"""
MCP Load Balancer - Equilibrage de charge entre serveurs MCP
Implementation minimale pour faire passer les tests
"""

from typing import Dict, Any, List, Optional
import asyncio


class MCPLoadBalancer:
    """Load balancer pour distribuer les requetes entre serveurs MCP"""
    
    def __init__(self):
        self.servers: List[Dict[str, Any]] = []
        self.current_index = 0
        self.strategy = "least_loaded"  # least_loaded, round_robin, random
    
    async def get_next_server(self) -> Optional[Dict[str, Any]]:
        """Obtenir le prochain serveur selon la strategie"""
        if not self.servers:
            return None
        
        if self.strategy == "least_loaded":
            # Retourner le serveur avec la charge la plus faible
            return min(self.servers, key=lambda s: s.get("load", 0))
        
        elif self.strategy == "round_robin":
            # Round-robin simple
            server = self.servers[self.current_index % len(self.servers)]
            self.current_index += 1
            return server
        
        elif self.strategy == "random":
            # Selection aleatoire
            import random
            return random.choice(self.servers)
        
        return self.servers[0]
    
    def add_server(self, server: Dict[str, Any]):
        """Ajouter un serveur au pool"""
        if server not in self.servers:
            self.servers.append(server)
    
    def remove_server(self, server_name: str):
        """Retirer un serveur du pool"""
        self.servers = [s for s in self.servers if s.get("name") != server_name]
    
    async def update_server_load(self, server_name: str, load: float):
        """Mettre a jour la charge d'un serveur"""
        for server in self.servers:
            if server.get("name") == server_name:
                server["load"] = load
                break
    
    def get_server_count(self) -> int:
        """Obtenir le nombre de serveurs dans le pool"""
        return len(self.servers)
    
    def set_strategy(self, strategy: str):
        """Definir la strategie de load balancing"""
        if strategy in ["least_loaded", "round_robin", "random"]:
            self.strategy = strategy
    
    async def health_check(self) -> List[Dict[str, Any]]:
        """Verifier la sante de tous les serveurs"""
        healthy_servers = []
        
        for server in self.servers:
            # Implementation minimale : considerer tous les serveurs comme sains
            # Dans la vraie implementation, on ferait un vrai health check
            if server.get("load", 0) < server.get("capacity", 100):
                healthy_servers.append(server)
        
        return healthy_servers
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtenir les statistiques du load balancer"""
        total_load = sum(s.get("load", 0) for s in self.servers)
        avg_load = total_load / len(self.servers) if self.servers else 0
        
        return {
            "server_count": len(self.servers),
            "total_load": total_load,
            "average_load": avg_load,
            "strategy": self.strategy
        }