#!/usr/bin/env python3
"""
LM Studio Client - Implementation
Connexion aux modeles LM Studio via API REST
Respecte les principes DDD (Domain-Driven Design) et SOLID
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
import aiohttp
from urllib.parse import urljoin

from .ai_model_interface import AIModelInterface, AIModelError, AIModelConfiguration


class LMStudioClient(AIModelInterface):
    """Client pour LM Studio API - respecte SOLID SRP"""
    
    def __init__(
        self, 
        base_url: str,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs
    ):
        # Utiliser le Value Object de configuration
        self._config = AIModelConfiguration(
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            model_name=model_name,
            api_key=api_key,
            **kwargs
        )
        
        self._logger = logging.getLogger(__name__)
        self._session: Optional[aiohttp.ClientSession] = None
        
        # URLs API LM Studio
        self._chat_url = urljoin(self._config.base_url.rstrip('/') + '/', 'v1/chat/completions')
        self._models_url = urljoin(self._config.base_url.rstrip('/') + '/', 'v1/models')
    
    @property
    def base_url(self) -> str:
        """Propriete pour acces a l'URL de base"""
        return self._config.base_url
    
    @property
    def timeout(self) -> int:
        """Propriete pour acces au timeout"""
        return self._config.timeout
    
    @property
    def max_retries(self) -> int:
        """Propriete pour acces au max_retries"""
        return self._config.max_retries
    
    @property
    def retry_delay(self) -> float:
        """Propriete pour acces au retry_delay"""
        return self._config.retry_delay
    
    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Assurer qu'une session HTTP existe"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self._config.timeout)
            headers = {"Content-Type": "application/json"}
            
            if self._config.api_key:
                headers["Authorization"] = f"Bearer {self._config.api_key}"
            
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=headers
            )
        
        return self._session
    
    async def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Faire une requete HTTP avec retry logic"""
        session = await self._ensure_session()
        
        for attempt in range(self._config.max_retries):
            try:
                async with session.request(method, url, **kwargs) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise AIModelError(
                            f"API Error: {response.status} - {error_text}",
                            error_code=str(response.status)
                        )
            
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == self._config.max_retries - 1:
                    raise AIModelError(f"Connection failed after {self._config.max_retries} attempts: {e}")
                
                self._logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                await asyncio.sleep(self._config.retry_delay)
    
    async def generate_code(self, prompt: str, **kwargs) -> str:
        """Generer du code via LM Studio"""
        try:
            # Construction du prompt systeme pour generation de code
            system_prompt = kwargs.get('system_prompt', 
                "You are an expert software developer. Generate clean, well-documented code based on the request."
            )
            
            language = kwargs.get('language', 'python')
            framework = kwargs.get('framework', '')
            
            enhanced_prompt = f"""Generate {language} code"""
            if framework:
                enhanced_prompt += f" using {framework} framework"
            enhanced_prompt += f":\n\n{prompt}\n\nProvide only the code without explanations."
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": enhanced_prompt}
            ]
            
            payload = {
                "model": self._config.model_name or "local-model",
                "messages": messages,
                "temperature": kwargs.get('temperature', 0.7),
                "max_tokens": kwargs.get('max_tokens', 2000)
            }
            
            response = await self._make_request("POST", self._chat_url, json=payload)
            
            if "choices" in response and len(response["choices"]) > 0:
                return response["choices"][0]["message"]["content"]
            else:
                raise AIModelError("No response from model", details=response)
                
        except Exception as e:
            if isinstance(e, AIModelError):
                raise
            raise AIModelError(f"Code generation failed: {e}")
    
    async def analyze_text(self, text: str, analysis_type: str, **kwargs) -> str:
        """Analyser du texte selon un type specifique"""
        try:
            # Prompts systeme selon le type d'analyse
            system_prompts = {
                "bug_detection": "You are a code analysis expert. Analyze the code for potential bugs, security issues, and improvements.",
                "code_review": "You are a senior developer conducting a code review. Provide detailed feedback on code quality, style, and best practices.",
                "performance": "You are a performance optimization expert. Analyze the code for performance bottlenecks and suggest improvements.",
                "security": "You are a security expert. Analyze the code for security vulnerabilities and provide recommendations."
            }
            
            system_prompt = system_prompts.get(analysis_type, 
                "You are an expert analyst. Provide detailed analysis of the provided text."
            )
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this {analysis_type}:\n\n{text}"}
            ]
            
            payload = {
                "model": self._config.model_name or "local-model",
                "messages": messages,
                "temperature": kwargs.get('temperature', 0.3),
                "max_tokens": kwargs.get('max_tokens', 1500)
            }
            
            response = await self._make_request("POST", self._chat_url, json=payload)
            
            if "choices" in response and len(response["choices"]) > 0:
                return response["choices"][0]["message"]["content"]
            else:
                raise AIModelError("No analysis response from model", details=response)
                
        except Exception as e:
            if isinstance(e, AIModelError):
                raise
            raise AIModelError(f"Text analysis failed: {e}")
    
    async def generate_tests(self, code: str, test_framework: str = "pytest", **kwargs) -> str:
        """Generer des tests pour le code donne"""
        try:
            # Prompt specialise pour generation de tests TDD
            system_prompt = f"""You are a test-driven development expert using {test_framework}. 
            Generate comprehensive unit tests following TDD best practices:
            - Use GIVEN/WHEN/THEN structure in comments
            - Test edge cases and error conditions  
            - Use descriptive test names
            - Include proper assertions"""
            
            test_prompt = f"""Generate {test_framework} unit tests for this code:

{code}

Follow TDD format with:
- Clear test method names describing what is being tested
- GIVEN/WHEN/THEN structure in comments
- Comprehensive coverage of functionality
- Edge cases and error conditions
- Proper mocking where needed"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": test_prompt}
            ]
            
            payload = {
                "model": self._config.model_name or "local-model", 
                "messages": messages,
                "temperature": kwargs.get('temperature', 0.4),
                "max_tokens": kwargs.get('max_tokens', 2500)
            }
            
            response = await self._make_request("POST", self._chat_url, json=payload)
            
            if "choices" in response and len(response["choices"]) > 0:
                return response["choices"][0]["message"]["content"]
            else:
                raise AIModelError("No test generation response from model", details=response)
                
        except Exception as e:
            if isinstance(e, AIModelError):
                raise
            raise AIModelError(f"Test generation failed: {e}")
    
    async def fix_bugs(self, code: str, bug_description: str, **kwargs) -> str:
        """Corriger des bugs dans le code"""
        try:
            system_prompt = """You are an expert debugger and software engineer. 
            Fix the reported bugs while maintaining code functionality and style.
            Provide only the corrected code without explanations unless requested."""
            
            fix_prompt = f"""Fix the bugs in this code:

CODE:
{code}

BUGS TO FIX:
{bug_description}

Provide the corrected code maintaining the same structure and functionality."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": fix_prompt}
            ]
            
            payload = {
                "model": self._config.model_name or "local-model",
                "messages": messages, 
                "temperature": kwargs.get('temperature', 0.2),
                "max_tokens": kwargs.get('max_tokens', 2000)
            }
            
            response = await self._make_request("POST", self._chat_url, json=payload)
            
            if "choices" in response and len(response["choices"]) > 0:
                return response["choices"][0]["message"]["content"]
            else:
                raise AIModelError("No bug fix response from model", details=response)
                
        except Exception as e:
            if isinstance(e, AIModelError):
                raise  
            raise AIModelError(f"Bug fixing failed: {e}")
    
    async def list_available_models(self) -> List[Dict[str, Any]]:
        """Lister les modeles disponibles sur LM Studio"""
        try:
            response = await self._make_request("GET", self._models_url)
            
            if "data" in response:
                return response["data"]
            else:
                return []
                
        except Exception as e:
            self._logger.warning(f"Failed to list models: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifier la sante du serveur LM Studio"""
        try:
            # Tentative de requete simple pour verifier la disponibilite
            models = await self.list_available_models()
            
            return {
                "status": "healthy",
                "base_url": self._config.base_url,
                "models_available": len(models),
                "models": [model.get("id", "unknown") for model in models[:3]]  # Premier 3 modeles
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "base_url": self._config.base_url, 
                "error": str(e)
            }
    
    async def close(self):
        """Fermer la session HTTP"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def __aenter__(self):
        """Support du context manager async"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Nettoyage du context manager async"""
        await self.close()


# Factory Pattern pour creation de clients selon DDD
class LMStudioClientFactory:
    """Factory pour creer des instances de LMStudioClient"""
    
    @staticmethod
    def create_client(config: Dict[str, Any]) -> LMStudioClient:
        """Creer un client LM Studio a partir d'une configuration"""
        required_fields = ["base_url"]
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Configuration manquante: {field}")
        
        return LMStudioClient(**config)
    
    @staticmethod
    def create_from_env() -> LMStudioClient:
        """Creer un client a partir des variables d'environnement"""
        import os
        
        base_url = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234")
        api_key = os.getenv("LM_STUDIO_API_KEY")
        model_name = os.getenv("LM_STUDIO_MODEL_NAME")
        
        config = {"base_url": base_url}
        
        if api_key:
            config["api_key"] = api_key
        if model_name:
            config["model_name"] = model_name
        
        return LMStudioClient(**config)