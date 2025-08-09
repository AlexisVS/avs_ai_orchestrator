#!/usr/bin/env python3
"""
Interface MCPInterface - Domain-Driven Design
Définit le contrat pour tous les clients MCP
Respecte le principe SOLID ISP (Interface Segregation Principle)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from enum import Enum


class MCPConnectionState(Enum):
    """États de connexion MCP"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


class MCPInterface(ABC):
    """Interface abstraite pour tous les clients MCP"""
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Se connecter au serveur MCP
        
        Returns:
            True si la connexion réussit
            
        Raises:
            MCPConnectionError: En cas d'échec de connexion
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Se déconnecter du serveur MCP
        
        Returns:
            True si la déconnexion réussit
        """
        pass
    
    @abstractmethod
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Appeler un outil MCP
        
        Args:
            tool_name: Nom de l'outil à appeler
            arguments: Arguments pour l'outil
            
        Returns:
            Résultat de l'appel d'outil
            
        Raises:
            MCPToolError: En cas d'erreur d'appel d'outil
        """
        pass
    
    @abstractmethod
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        Lister les outils disponibles
        
        Returns:
            Liste des outils avec leurs métadonnées
            
        Raises:
            MCPError: En cas d'erreur de communication
        """
        pass
    
    @abstractmethod
    async def get_resources(self) -> List[Dict[str, Any]]:
        """
        Récupérer les ressources disponibles
        
        Returns:
            Liste des ressources avec leurs métadonnées
            
        Raises:
            MCPError: En cas d'erreur de communication
        """
        pass
    
    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Indique si le client est connecté"""
        pass
    
    @property
    @abstractmethod
    def connection_state(self) -> MCPConnectionState:
        """État actuel de la connexion"""
        pass


class MCPError(Exception):
    """Exception de base pour les erreurs MCP"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict] = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}


class MCPConnectionError(MCPError):
    """Erreur de connexion MCP"""
    pass


class MCPToolError(MCPError):
    """Erreur d'appel d'outil MCP"""
    
    def __init__(self, message: str, tool_name: str, error_code: Optional[str] = None, details: Optional[Dict] = None):
        super().__init__(message, error_code, details)
        self.tool_name = tool_name


class MCPResourceError(MCPError):
    """Erreur d'accès aux ressources MCP"""
    pass


class MCPConfiguration:
    """Configuration MCP - Value Object DDD"""
    
    def __init__(
        self,
        container_name: str,
        docker_host: str = "unix:///var/run/docker.sock",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        auto_start: bool = False,
        auto_reconnect: bool = True,
        health_check_enabled: bool = True,
        health_check_interval: int = 60,
        **extra_params
    ):
        # Validation selon DDD
        if not container_name or not isinstance(container_name, str):
            raise ValueError("container_name doit être une string non-vide")
        
        if timeout <= 0:
            raise ValueError("timeout doit être positif")
        
        if max_retries < 0:
            raise ValueError("max_retries ne peut être négatif")
        
        if retry_delay < 0:
            raise ValueError("retry_delay ne peut être négatif")
        
        if health_check_interval <= 0:
            raise ValueError("health_check_interval doit être positif")
        
        # Immutable value object
        self._container_name = container_name
        self._docker_host = docker_host
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._auto_start = auto_start
        self._auto_reconnect = auto_reconnect
        self._health_check_enabled = health_check_enabled
        self._health_check_interval = health_check_interval
        self._extra_params = extra_params
    
    @property
    def container_name(self) -> str:
        return self._container_name
    
    @property
    def docker_host(self) -> str:
        return self._docker_host
    
    @property
    def timeout(self) -> int:
        return self._timeout
    
    @property
    def max_retries(self) -> int:
        return self._max_retries
    
    @property
    def retry_delay(self) -> float:
        return self._retry_delay
    
    @property
    def auto_start(self) -> bool:
        return self._auto_start
    
    @property
    def auto_reconnect(self) -> bool:
        return self._auto_reconnect
    
    @property
    def health_check_enabled(self) -> bool:
        return self._health_check_enabled
    
    @property
    def health_check_interval(self) -> int:
        return self._health_check_interval
    
    @property
    def extra_params(self) -> Dict[str, Any]:
        return self._extra_params.copy()
    
    def __eq__(self, other):
        if not isinstance(other, MCPConfiguration):
            return False
        return (
            self.container_name == other.container_name and
            self.docker_host == other.docker_host and
            self.timeout == other.timeout and
            self.max_retries == other.max_retries and
            self.retry_delay == other.retry_delay and
            self.auto_start == other.auto_start and
            self.auto_reconnect == other.auto_reconnect and
            self.health_check_enabled == other.health_check_enabled and
            self.health_check_interval == other.health_check_interval and
            self.extra_params == other.extra_params
        )
    
    def __hash__(self):
        return hash((
            self.container_name,
            self.docker_host,
            self.timeout,
            self.max_retries,
            self.retry_delay,
            self.auto_start,
            self.auto_reconnect,
            self.health_check_enabled,
            self.health_check_interval,
            tuple(sorted(self.extra_params.items()))
        ))
    
    def __repr__(self):
        return f"MCPConfiguration(container_name='{self.container_name}', docker_host='{self.docker_host}')"


class MCPToolMetadata:
    """Métadonnées d'un outil MCP - Value Object DDD"""
    
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        output_schema: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        version: Optional[str] = None
    ):
        if not name or not isinstance(name, str):
            raise ValueError("name doit être une string non-vide")
        
        if not description or not isinstance(description, str):
            raise ValueError("description doit être une string non-vide")
        
        if not isinstance(input_schema, dict):
            raise ValueError("input_schema doit être un dictionnaire")
        
        self._name = name
        self._description = description
        self._input_schema = input_schema
        self._output_schema = output_schema
        self._tags = tags or []
        self._version = version
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return self._input_schema.copy()
    
    @property
    def output_schema(self) -> Optional[Dict[str, Any]]:
        return self._output_schema.copy() if self._output_schema else None
    
    @property
    def tags(self) -> List[str]:
        return self._tags.copy()
    
    @property
    def version(self) -> Optional[str]:
        return self._version
    
    def has_tag(self, tag: str) -> bool:
        """Vérifie si l'outil a un tag donné"""
        return tag in self._tags
    
    def validates_input(self, arguments: Dict[str, Any]) -> bool:
        """Valide les arguments selon le schema d'entrée (simplifiée)"""
        required = self._input_schema.get("required", [])
        properties = self._input_schema.get("properties", {})
        
        # Vérifier les champs requis
        for field in required:
            if field not in arguments:
                return False
        
        # Vérifier les types (validation basique)
        for field, value in arguments.items():
            if field in properties:
                expected_type = properties[field].get("type")
                if expected_type == "string" and not isinstance(value, str):
                    return False
                elif expected_type == "number" and not isinstance(value, (int, float)):
                    return False
                elif expected_type == "boolean" and not isinstance(value, bool):
                    return False
                elif expected_type == "array" and not isinstance(value, list):
                    return False
                elif expected_type == "object" and not isinstance(value, dict):
                    return False
        
        return True
    
    def __eq__(self, other):
        if not isinstance(other, MCPToolMetadata):
            return False
        return (
            self.name == other.name and
            self.description == other.description and
            self.input_schema == other.input_schema and
            self.output_schema == other.output_schema and
            self.tags == other.tags and
            self.version == other.version
        )
    
    def __hash__(self):
        return hash((
            self.name,
            self.description,
            tuple(sorted(self.input_schema.items())),
            tuple(sorted(self.output_schema.items())) if self.output_schema else None,
            tuple(sorted(self.tags)),
            self.version
        ))
    
    def __repr__(self):
        return f"MCPToolMetadata(name='{self.name}', version='{self.version}')"


class MCPResource:
    """Ressource MCP - Value Object DDD"""
    
    def __init__(
        self,
        uri: str,
        name: str,
        mime_type: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        if not uri or not isinstance(uri, str):
            raise ValueError("uri doit être une string non-vide")
        
        if not name or not isinstance(name, str):
            raise ValueError("name doit être une string non-vide")
        
        self._uri = uri
        self._name = name
        self._mime_type = mime_type
        self._description = description
        self._metadata = metadata or {}
    
    @property
    def uri(self) -> str:
        return self._uri
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def mime_type(self) -> Optional[str]:
        return self._mime_type
    
    @property
    def description(self) -> Optional[str]:
        return self._description
    
    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata.copy()
    
    def __eq__(self, other):
        if not isinstance(other, MCPResource):
            return False
        return (
            self.uri == other.uri and
            self.name == other.name and
            self.mime_type == other.mime_type and
            self.description == other.description and
            self.metadata == other.metadata
        )
    
    def __hash__(self):
        return hash((
            self.uri,
            self.name,
            self.mime_type,
            self.description,
            tuple(sorted(self.metadata.items()))
        ))
    
    def __repr__(self):
        return f"MCPResource(uri='{self.uri}', name='{self.name}')"