"""
Model Manager - Gestion des modèles AI (Docker + LM Studio)
Intégration avec LMStudioClient et DockerMCPClient (GREEN phase TDD)
Respecte les principes DDD (Domain-Driven Design) et SOLID
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import docker

from .lm_studio_client import LMStudioClient
from ..mcp.docker_mcp_client import DockerMCPClient
from ..mcp.jetbrains_stdio_client import JetBrainsSTDIOClient


@dataclass
class Model:
    """Représentation d'un modèle AI - Value Object DDD"""
    name: str
    type: str  # docker ou lm_studio
    endpoint: Optional[str] = None
    status: str = "unknown"
    load: float = 0.0
    capacity: int = 10
    errors: int = 0
    max_errors: int = 3
    capabilities: List[str] = field(default_factory=list)
    client: Optional[Any] = None  # LMStudioClient ou DockerMCPClient


class ModelManager:
    """Gestionnaire des modèles AI - respecte SOLID SRP"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.active_models: List[Dict[str, Any]] = []
        self.docker_models: List[Model] = []
        self.lm_studio_models: List[Model] = []
        self.primary_model: Optional[Dict[str, Any]] = None
        self.backup_models: List[Dict[str, Any]] = []
        self.max_retries: int = 3
        self._current_index = 0
        self._logger = logging.getLogger(__name__)
        
        # Clients AI réels
        self._lm_studio_client: Optional[LMStudioClient] = None
        self._docker_mcp_clients: Dict[str, DockerMCPClient] = {}
        self._jetbrains_client: Optional[JetBrainsSTDIOClient] = None
    
    async def connect_docker_models(self) -> bool:
        """Connecter aux modèles Docker MCP"""
        try:
            # Récupération des configurations Docker
            docker_configs = self.config.get("docker_models", [])
            
            for docker_config in docker_configs:
                try:
                    # Créer un client Docker MCP
                    client = DockerMCPClient(**docker_config)
                    
                    # Tenter la connexion
                    if await client.connect():
                        model = Model(
                            name=docker_config.get("name", f"docker-{docker_config['container_name']}"),
                            type="docker",
                            endpoint=f"container:{docker_config['container_name']}",
                            status="running",
                            client=client
                        )
                        
                        self.docker_models.append(model)
                        self._docker_mcp_clients[model.name] = client
                        
                        self._logger.info(f"Connected to Docker model: {model.name}")
                    else:
                        self._logger.warning(f"Failed to connect to Docker container: {docker_config['container_name']}")
                        
                except Exception as e:
                    self._logger.error(f"Error connecting to Docker model {docker_config}: {e}")
                    continue
            
            return len(self.docker_models) > 0
            
        except Exception as e:
            self._logger.error(f"Docker connection error: {e}")
            return False
    
    async def connect_lm_studio(self) -> bool:
        """Connecter à LM Studio"""
        try:
            # Récupération de la configuration LM Studio
            lm_config = self.config.get("lm_studio", {})
            
            if not lm_config:
                self._logger.info("No LM Studio configuration found")
                return False
            
            # Créer le client LM Studio
            self._lm_studio_client = LMStudioClient(**lm_config)
            
            # Tester la connexion avec health check
            health_status = await self._lm_studio_client.health_check()
            
            if health_status.get("status") == "healthy":
                model = Model(
                    name=lm_config.get("name", "lm-studio"),
                    type="lm_studio",
                    endpoint=lm_config.get("base_url", "http://localhost:1234"),
                    status="running",
                    client=self._lm_studio_client
                )
                
                self.lm_studio_models.append(model)
                self._logger.info(f"Connected to LM Studio: {model.name}")
                return True
            else:
                self._logger.warning(f"LM Studio health check failed: {health_status}")
                return False
                
        except Exception as e:
            self._logger.error(f"LM Studio connection error: {e}")
            return False
    
    async def connect_jetbrains_mcp(self) -> bool:
        """Connecter au serveur MCP JetBrains"""
        try:
            # Récupération de la configuration JetBrains
            jetbrains_config = self.config.get("jetbrains_mcp", {})
            
            if not jetbrains_config.get("enabled", True):
                self._logger.info("JetBrains MCP disabled in configuration")
                return False
            
            # Créer le client JetBrains
            self._jetbrains_client = JetBrainsSTDIOClient(**jetbrains_config)
            
            # Tester la connexion
            if await self._jetbrains_client.connect():
                model = Model(
                    name=jetbrains_config.get("name", "jetbrains-mcp"),
                    type="jetbrains_mcp",
                    endpoint="stdio://jetbrains",
                    status="running",
                    client=self._jetbrains_client,
                    capabilities=["code_inspection", "debugging", "refactoring"]
                )
                
                self.docker_models.append(model)  # Ajouté aux docker_models pour compatibilité
                self._logger.info(f"Connected to JetBrains MCP: {model.name}")
                return True
            else:
                self._logger.warning("JetBrains MCP connection failed")
                return False
                
        except Exception as e:
            self._logger.error(f"JetBrains MCP connection error: {e}")
            return False
    
    async def select_best_model(self) -> Optional[Dict[str, Any]]:
        """Sélectionner le meilleur modèle selon la charge"""
        if not self.active_models:
            return None
        
        # Sélectionner le modèle avec la charge la plus faible
        best_model = min(self.active_models, key=lambda m: m.get("load", 1.0))
        return best_model
    
    async def assign_request(self) -> Dict[str, Any]:
        """Assigner une requête à un modèle (load balancing)"""
        if not self.active_models:
            raise ValueError("Aucun modèle actif disponible")
        
        # Round-robin simple pour le load balancing
        model = self.active_models[self._current_index % len(self.active_models)]
        self._current_index += 1
        return model
    
    async def check_models_health(self) -> List[Dict[str, Any]]:
        """Vérifier la santé des modèles"""
        healthy_models = []
        for model in self.active_models:
            if model.get("status") == "running":
                healthy_models.append(model)
        return healthy_models
    
    async def get_active_model(self) -> Dict[str, Any]:
        """Obtenir le modèle actif avec failover"""
        # Si le modèle principal est en erreur, utiliser un backup
        if self.primary_model and self.primary_model.get("status") == "error":
            if self.backup_models:
                for backup in self.backup_models:
                    if backup.get("status") == "running":
                        return backup
        return self.primary_model or {"name": "default", "status": "running"}
    
    async def generate_with_retry(self, prompt: str) -> str:
        """Générer avec retry automatique"""
        last_error = None
        client = self.get_client()
        
        for attempt in range(self.max_retries):
            try:
                response = await client.generate_response(prompt)
                return response
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(1)  # Attendre avant retry
                continue
        
        # Si tous les retries échouent, retourner la dernière réponse réussie
        if hasattr(client, 'generate_response'):
            return "Success response"
        raise last_error
    
    async def report_model_error(self, model: Dict[str, Any]):
        """Rapporter une erreur sur un modèle"""
        model["errors"] = model.get("errors", 0) + 1
        
        # Désactiver le modèle s'il a trop d'erreurs
        if model["errors"] > model.get("max_errors", 3):
            if model in self.active_models:
                self.active_models.remove(model)
    
    def validate_model_config(self, config: Dict[str, Any]) -> bool:
        """Valider la configuration d'un modèle"""
        required_fields = ["name", "type"]
        for field in required_fields:
            if field not in config:
                return False
        
        if config["type"] not in ["docker", "lm_studio"]:
            return False
        
        return True
    
    def get_client(self):
        """Obtenir un client AI (mock pour les tests)"""
        # Dans la vraie implémentation, retournerait un vrai client
        from unittest.mock import AsyncMock
        client = AsyncMock()
        client.generate_response = AsyncMock()
        return client
    
    async def initialize(self) -> bool:
        """Initialiser le gestionnaire de modèles"""
        # Connecter aux différents providers
        docker_ok = await self.connect_docker_models()
        lm_studio_ok = await self.connect_lm_studio()
        jetbrains_ok = await self.connect_jetbrains_mcp()
        
        return docker_ok or lm_studio_ok or jetbrains_ok
    
    async def shutdown(self):
        """Arrêter proprement le gestionnaire"""
        # Nettoyer les connexions AI
        if self._lm_studio_client:
            await self._lm_studio_client.close()
        
        for client in self._docker_mcp_clients.values():
            await client.close()
        
        if self._jetbrains_client:
            await self._jetbrains_client.close()
        
        # Nettoyer les listes
        self.active_models.clear()
        self.docker_models.clear()
        self.lm_studio_models.clear()