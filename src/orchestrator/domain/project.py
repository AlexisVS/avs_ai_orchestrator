"""
Domain model for Project - DDD Value Object and Entity
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pathlib import Path
from abc import ABC, abstractmethod


@dataclass(frozen=True)
class ProjectName:
    """Value Object for Project Name (DDD)"""
    value: str
    
    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Project name cannot be empty")
        if len(self.value) > 50:
            raise ValueError("Project name too long (max 50 characters)")
        if not self.value.replace("-", "").replace("_", "").replace(".", "").isalnum():
            raise ValueError("Project name must be alphanumeric with hyphens, underscores, or dots")


@dataclass(frozen=True)
class ProjectPath:
    """Value Object for Project Path (DDD)"""
    value: Path
    
    def __post_init__(self):
        if not self.value.exists():
            raise ValueError(f"Project path does not exist: {self.value}")
        if not self.value.is_dir():
            raise ValueError(f"Project path is not a directory: {self.value}")
    
    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class GitHubRepository:
    """Value Object for GitHub Repository (DDD)"""
    owner: str
    repo: str
    project_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.owner or not self.repo:
            raise ValueError("GitHub owner and repo are required")
    
    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.repo}"


@dataclass
class ProjectConfiguration:
    """Entity for Project Configuration (DDD)"""
    name: ProjectName
    path: ProjectPath
    github: GitHubRepository
    sandbox_path: Optional[Path] = None
    additional_config: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.sandbox_path is None:
            self.sandbox_path = self.path.value.parent / f"{self.name.value}_sandbox"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for compatibility"""
        return {
            "target_project": {
                "name": self.name.value,
                "path": str(self.path.value)
            },
            "github": {
                "owner": self.github.owner,
                "repo": self.github.repo,
                "project_id": self.github.project_id or "1"
            },
            "sandbox_path": str(self.sandbox_path),
            "main_repo_path": str(self.path.value),
            **self.additional_config
        }


class ProjectRepository(ABC):
    """Repository interface for Project persistence (DDD)"""
    
    @abstractmethod
    def find_project_by_name(self, name: ProjectName) -> Optional[ProjectConfiguration]:
        """Find project configuration by name"""
        pass
    
    @abstractmethod
    def save_project(self, project: ProjectConfiguration) -> None:
        """Save project configuration"""
        pass


class ProjectValidationService:
    """Domain Service for Project validation (DDD)"""
    
    def __init__(self, github_validator: 'GitHubValidationService'):
        self.github_validator = github_validator
    
    def validate_project(self, name: str, path: str) -> Dict[str, Any]:
        """Validate project configuration (SOLID: Single Responsibility)"""
        try:
            project_name = ProjectName(name)
            project_path = ProjectPath(Path(path))
            
            # Validate GitHub repository
            github_info = self.github_validator.validate_repository(name)
            github_repo = GitHubRepository(
                owner=github_info.get("owner", "AlexisVS"),
                repo=name,
                project_id=github_info.get("project_id")
            )
            
            # Create project configuration
            project_config = ProjectConfiguration(
                name=project_name,
                path=project_path,
                github=github_repo
            )
            
            return {
                "valid": True,
                "project_name": name,
                "project_path": path,
                "github": github_info,
                "configuration": project_config
            }
            
        except ValueError as e:
            return {
                "valid": False,
                "error": str(e),
                "project_name": name,
                "project_path": path
            }


class GitHubValidationService:
    """Domain Service for GitHub validation (DDD)"""
    
    def validate_repository(self, repo_name: str) -> Dict[str, Any]:
        """Validate GitHub repository existence"""
        # Pour les tests et le développement, simulation
        # En production, ceci ferait un appel API réel
        return {
            "exists": True,
            "owner": "AlexisVS",
            "repo": repo_name,
            "project_id": "1"
        }


class ProjectResolutionService:
    """Domain Service for Project path resolution (DDD)"""
    
    @staticmethod
    def resolve_project_path(project_name: str) -> str:
        """Resolve project path using search strategy (SOLID: Strategy pattern)"""
        search_strategies = [
            CurrentDirectorySearchStrategy(),
            ParentDirectorySearchStrategy(),
            SiblingDirectorySearchStrategy()
        ]
        
        for strategy in search_strategies:
            try:
                path = strategy.find_project(project_name)
                if path:
                    return path
            except Exception:
                continue
        
        raise ValueError(f"Project directory not found: {project_name}")


class ProjectSearchStrategy(ABC):
    """Strategy interface for project search (SOLID: Strategy pattern)"""
    
    @abstractmethod
    def find_project(self, project_name: str) -> Optional[str]:
        """Find project in specific location"""
        pass


class CurrentDirectorySearchStrategy(ProjectSearchStrategy):
    """Search in current directory"""
    
    def find_project(self, project_name: str) -> Optional[str]:
        current_path = Path.cwd() / project_name
        if current_path.exists() and current_path.is_dir():
            return str(current_path)
        return None


class ParentDirectorySearchStrategy(ProjectSearchStrategy):
    """Search in parent directory"""
    
    def find_project(self, project_name: str) -> Optional[str]:
        parent_path = Path.cwd().parent / project_name
        if parent_path.exists() and parent_path.is_dir():
            return str(parent_path)
        return None


class SiblingDirectorySearchStrategy(ProjectSearchStrategy):
    """Search in sibling directories"""
    
    def find_project(self, project_name: str) -> Optional[str]:
        parent_dir = Path.cwd().parent
        if not parent_dir.exists():
            return None
            
        for sibling in parent_dir.iterdir():
            if sibling.is_dir() and sibling.name == project_name:
                return str(sibling)
        return None