#!/usr/bin/env python3
"""
Interface AIModelInterface - Domain-Driven Design
Definit le contrat pour tous les clients de modeles AI
Respecte le principe SOLID ISP (Interface Segregation Principle)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class AIModelInterface(ABC):
    """Interface abstraite pour tous les clients de modeles AI"""
    
    @abstractmethod
    async def generate_code(self, prompt: str, **kwargs) -> str:
        """
        Genere du code base sur un prompt
        
        Args:
            prompt: Description de ce qui doit etre genere
            **kwargs: Parametres additionnels (language, framework, etc.)
            
        Returns:
            Code genere sous forme de string
            
        Raises:
            AIModelError: En cas d'erreur de generation
        """
        pass
    
    @abstractmethod
    async def analyze_text(self, text: str, analysis_type: str, **kwargs) -> str:
        """
        Analyse un texte selon un type d'analyse specifique
        
        Args:
            text: Texte a analyser
            analysis_type: Type d'analyse (bug_detection, code_review, etc.)
            **kwargs: Parametres additionnels
            
        Returns:
            Resultat de l'analyse sous forme de string
            
        Raises:
            AIModelError: En cas d'erreur d'analyse
        """
        pass
    
    @abstractmethod
    async def generate_tests(self, code: str, test_framework: str = "pytest", **kwargs) -> str:
        """
        Genere des tests pour un code donne
        
        Args:
            code: Code pour lequel generer les tests
            test_framework: Framework de test a utiliser
            **kwargs: Parametres additionnels
            
        Returns:
            Code des tests genere
            
        Raises:
            AIModelError: En cas d'erreur de generation
        """
        pass
    
    @abstractmethod
    async def fix_bugs(self, code: str, bug_description: str, **kwargs) -> str:
        """
        Corrige des bugs dans le code
        
        Args:
            code: Code contenant les bugs
            bug_description: Description des bugs a corriger
            **kwargs: Parametres additionnels
            
        Returns:
            Code corrige
            
        Raises:
            AIModelError: En cas d'erreur de correction
        """
        pass


class AIModelError(Exception):
    """Exception personnalisee pour les erreurs de modeles AI"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict] = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}


class AIModelConfiguration:
    """Configuration pour les clients de modeles AI - Value Object DDD"""
    
    def __init__(
        self, 
        base_url: str,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        **extra_params
    ):
        # Validation selon DDD
        if not base_url or not isinstance(base_url, str):
            raise ValueError("base_url doit etre une string non-vide")
        
        if not base_url.startswith(('http://', 'https://')):
            raise ValueError("base_url doit commencer par http:// ou https://")
        
        if timeout <= 0:
            raise ValueError("timeout doit etre positif")
        
        if max_retries < 0:
            raise ValueError("max_retries ne peut etre negatif")
        
        if retry_delay < 0:
            raise ValueError("retry_delay ne peut etre negatif")
        
        # Immutable value object
        self._base_url = base_url
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._model_name = model_name
        self._api_key = api_key
        self._extra_params = extra_params
    
    @property
    def base_url(self) -> str:
        return self._base_url
    
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
    def model_name(self) -> Optional[str]:
        return self._model_name
    
    @property
    def api_key(self) -> Optional[str]:
        return self._api_key
    
    @property
    def extra_params(self) -> Dict[str, Any]:
        return self._extra_params.copy()
    
    def __eq__(self, other):
        if not isinstance(other, AIModelConfiguration):
            return False
        return (
            self.base_url == other.base_url and
            self.timeout == other.timeout and
            self.max_retries == other.max_retries and
            self.retry_delay == other.retry_delay and
            self.model_name == other.model_name and
            self.api_key == other.api_key and
            self.extra_params == other.extra_params
        )
    
    def __hash__(self):
        return hash((
            self.base_url,
            self.timeout,
            self.max_retries,
            self.retry_delay,
            self.model_name,
            self.api_key,
            tuple(sorted(self.extra_params.items()))
        ))
    
    def __repr__(self):
        return f"AIModelConfiguration(base_url='{self.base_url}', model_name='{self.model_name}')"


class AIModelCapabilities:
    """Capacites d'un modele AI - Value Object DDD"""
    
    def __init__(
        self,
        supports_code_generation: bool = True,
        supports_text_analysis: bool = True,
        supports_test_generation: bool = True,
        supports_bug_fixing: bool = True,
        max_context_length: Optional[int] = None,
        supported_languages: Optional[List[str]] = None,
        supported_frameworks: Optional[List[str]] = None
    ):
        self._supports_code_generation = supports_code_generation
        self._supports_text_analysis = supports_text_analysis
        self._supports_test_generation = supports_test_generation
        self._supports_bug_fixing = supports_bug_fixing
        self._max_context_length = max_context_length
        self._supported_languages = supported_languages or []
        self._supported_frameworks = supported_frameworks or []
    
    @property
    def supports_code_generation(self) -> bool:
        return self._supports_code_generation
    
    @property
    def supports_text_analysis(self) -> bool:
        return self._supports_text_analysis
    
    @property
    def supports_test_generation(self) -> bool:
        return self._supports_test_generation
    
    @property
    def supports_bug_fixing(self) -> bool:
        return self._supports_bug_fixing
    
    @property
    def max_context_length(self) -> Optional[int]:
        return self._max_context_length
    
    @property
    def supported_languages(self) -> List[str]:
        return self._supported_languages.copy()
    
    @property
    def supported_frameworks(self) -> List[str]:
        return self._supported_frameworks.copy()
    
    def can_handle_language(self, language: str) -> bool:
        """Verifie si le modele supporte un langage donne"""
        if not self._supported_languages:
            return True  # Si pas de restriction, supporte tout
        return language.lower() in [lang.lower() for lang in self._supported_languages]
    
    def can_handle_framework(self, framework: str) -> bool:
        """Verifie si le modele supporte un framework donne"""
        if not self._supported_frameworks:
            return True  # Si pas de restriction, supporte tout
        return framework.lower() in [fw.lower() for fw in self._supported_frameworks]