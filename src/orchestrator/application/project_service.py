"""
Application Service for Project management (DDD Application Layer)
"""

from typing import Optional, Dict, Any
from ..domain.project import (
    ProjectName,
    ProjectPath,
    ProjectConfiguration,
    ProjectValidationService,
    ProjectResolutionService,
    GitHubValidationService
)
from pathlib import Path


class ProjectApplicationService:
    """Application Service for Project operations (DDD)"""
    
    def __init__(self):
        # Dependency Injection (SOLID: Dependency Inversion)
        self.github_validator = GitHubValidationService()
        self.validation_service = ProjectValidationService(self.github_validator)
        self.resolution_service = ProjectResolutionService()
    
    def create_project_configuration(
        self, 
        project_name: str, 
        project_path: Optional[str] = None
    ) -> ProjectConfiguration:
        """Create project configuration with full validation (DDD Use Case)"""
        
        # Resolve project path if not provided
        if project_path is None:
            project_path = self.resolution_service.resolve_project_path(project_name)
        
        # Validate the project
        validation_result = self.validation_service.validate_project(project_name, project_path)
        
        if not validation_result["valid"]:
            raise ValueError(f"Invalid project: {validation_result.get('error', 'Unknown error')}")
        
        return validation_result["configuration"]
    
    def generate_configuration_dict(
        self, 
        project_name: str, 
        project_path: Optional[str] = None,
        github_owner: str = "AlexisVS"
    ) -> Dict[str, Any]:
        """Generate configuration dictionary for legacy compatibility"""
        try:
            project_config = self.create_project_configuration(project_name, project_path)
            return project_config.to_dict()
        except Exception:
            # Fallback for backward compatibility
            return self._create_fallback_configuration(project_name, project_path, github_owner)
    
    def _create_fallback_configuration(
        self, 
        project_name: str, 
        project_path: Optional[str],
        github_owner: str
    ) -> Dict[str, Any]:
        """Create fallback configuration when validation fails"""
        if project_path is None:
            project_path = str(Path.cwd().parent / project_name)
        
        sandbox_path = Path(project_path).parent / f"{project_name}_sandbox"
        
        return {
            "target_project": {
                "name": project_name,
                "path": project_path
            },
            "github": {
                "owner": github_owner,
                "repo": project_name,
                "project_id": "1"
            },
            "sandbox_path": str(sandbox_path),
            "main_repo_path": project_path,
        }
    
    def validate_project_configuration(self, project_name: str, project_path: str) -> Dict[str, Any]:
        """Validate project configuration (exposed for backward compatibility)"""
        return self.validation_service.validate_project(project_name, project_path)
    
    def resolve_project_path(self, project_name: str) -> str:
        """Resolve project path (exposed for backward compatibility)"""
        return self.resolution_service.resolve_project_path(project_name)