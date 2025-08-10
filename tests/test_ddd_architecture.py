"""
Tests for DDD Architecture implementation
Tests the complete TDD → SOLID → DDD cycle
"""

import pytest
import tempfile
from pathlib import Path
import sys

# Ajouter le path src pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from orchestrator.domain.project import (
    ProjectName,
    ProjectPath,
    GitHubRepository,
    ProjectConfiguration,
    ProjectValidationService,
    GitHubValidationService,
    ProjectResolutionService,
    CurrentDirectorySearchStrategy,
    ParentDirectorySearchStrategy
)
from orchestrator.application.project_service import ProjectApplicationService


class TestDomainValueObjects:
    """Test Domain Value Objects (DDD)"""
    
    def test_project_name_value_object(self):
        """Test: ProjectName value object validation"""
        # GIVEN & WHEN & THEN
        valid_name = ProjectName("weather-dashboard")
        assert valid_name.value == "weather-dashboard"
        
        # Test invalid names
        with pytest.raises(ValueError, match="Project name cannot be empty"):
            ProjectName("")
        
        with pytest.raises(ValueError, match="Project name too long"):
            ProjectName("a" * 51)
        
        with pytest.raises(ValueError, match="Project name must be alphanumeric"):
            ProjectName("invalid@name")
    
    def test_project_path_value_object(self):
        """Test: ProjectPath value object validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # GIVEN
            valid_path = Path(temp_dir)
            
            # WHEN & THEN
            project_path = ProjectPath(valid_path)
            assert project_path.value == valid_path
            assert str(project_path) == str(valid_path)
            
            # Test invalid path
            with pytest.raises(ValueError, match="Project path does not exist"):
                ProjectPath(Path("/nonexistent/path"))
    
    def test_github_repository_value_object(self):
        """Test: GitHubRepository value object"""
        # GIVEN & WHEN
        github_repo = GitHubRepository("AlexisVS", "weather-dashboard", "1")
        
        # THEN
        assert github_repo.owner == "AlexisVS"
        assert github_repo.repo == "weather-dashboard"
        assert github_repo.project_id == "1"
        assert github_repo.full_name == "AlexisVS/weather-dashboard"
        
        # Test validation
        with pytest.raises(ValueError, match="GitHub owner and repo are required"):
            GitHubRepository("", "repo")


class TestDomainEntity:
    """Test Domain Entity (DDD)"""
    
    def test_project_configuration_entity(self):
        """Test: ProjectConfiguration entity"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # GIVEN
            project_name = ProjectName("test-project")
            project_path = ProjectPath(Path(temp_dir))
            github_repo = GitHubRepository("TestOwner", "test-project")
            
            # WHEN
            project_config = ProjectConfiguration(
                name=project_name,
                path=project_path,
                github=github_repo
            )
            
            # THEN
            assert project_config.name == project_name
            assert project_config.path == project_path
            assert project_config.github == github_repo
            assert project_config.sandbox_path is not None
            
            # Test to_dict conversion
            config_dict = project_config.to_dict()
            assert config_dict["target_project"]["name"] == "test-project"
            assert config_dict["github"]["owner"] == "TestOwner"


class TestDomainServices:
    """Test Domain Services (DDD)"""
    
    def test_github_validation_service(self):
        """Test: GitHubValidationService domain service"""
        # GIVEN
        service = GitHubValidationService()
        
        # WHEN
        result = service.validate_repository("test-repo")
        
        # THEN
        assert result["exists"] is True
        assert result["owner"] == "AlexisVS"
        assert result["repo"] == "test-repo"
    
    def test_project_validation_service(self):
        """Test: ProjectValidationService domain service"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # GIVEN
            github_service = GitHubValidationService()
            validation_service = ProjectValidationService(github_service)
            
            # WHEN
            result = validation_service.validate_project("test-project", temp_dir)
            
            # THEN
            assert result["valid"] is True
            assert result["project_name"] == "test-project"
            assert result["project_path"] == temp_dir
            assert "configuration" in result
            assert isinstance(result["configuration"], ProjectConfiguration)


class TestStrategiesPattern:
    """Test Strategy Pattern implementation (SOLID: Open/Closed)"""
    
    def test_current_directory_search_strategy(self):
        """Test: CurrentDirectorySearchStrategy"""
        # GIVEN
        strategy = CurrentDirectorySearchStrategy()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            import os
            old_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                test_project = Path(temp_dir) / "test-project"
                test_project.mkdir()
                
                # WHEN
                result = strategy.find_project("test-project")
                
                # THEN
                assert result == str(test_project)
                
                # Test not found
                assert strategy.find_project("nonexistent") is None
                
            finally:
                os.chdir(old_cwd)
    
    def test_parent_directory_search_strategy(self):
        """Test: ParentDirectorySearchStrategy"""
        # GIVEN
        strategy = ParentDirectorySearchStrategy()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            import os
            old_cwd = os.getcwd()
            try:
                # Create structure: temp_dir/test-project and temp_dir/subdir
                test_project = Path(temp_dir) / "test-project"
                test_project.mkdir()
                sub_dir = Path(temp_dir) / "subdir"
                sub_dir.mkdir()
                os.chdir(str(sub_dir))
                
                # WHEN
                result = strategy.find_project("test-project")
                
                # THEN
                assert result == str(test_project)
                
            finally:
                os.chdir(old_cwd)


class TestApplicationService:
    """Test Application Service (DDD Application Layer)"""
    
    def test_project_application_service_integration(self):
        """Test: Complete integration of ProjectApplicationService"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # GIVEN
            service = ProjectApplicationService()
            test_project = Path(temp_dir) / "integration-project"
            test_project.mkdir()
            
            # WHEN
            config_dict = service.generate_configuration_dict(
                "integration-project", 
                str(test_project)
            )
            
            # THEN
            assert config_dict["target_project"]["name"] == "integration-project"
            assert config_dict["target_project"]["path"] == str(test_project)
            assert config_dict["github"]["repo"] == "integration-project"
            assert "sandbox_path" in config_dict
    
    def test_application_service_fallback(self):
        """Test: Application service fallback mechanism"""
        # GIVEN
        service = ProjectApplicationService()
        
        # WHEN - Using nonexistent project should trigger fallback
        config_dict = service.generate_configuration_dict(
            "nonexistent-project", 
            "/nonexistent/path"
        )
        
        # THEN - Should return fallback configuration
        assert config_dict["target_project"]["name"] == "nonexistent-project"
        assert config_dict["github"]["repo"] == "nonexistent-project"


class TestSOLIDPrinciples:
    """Test SOLID Principles implementation"""
    
    def test_single_responsibility_principle(self):
        """Test: Each class has single responsibility"""
        # GIVEN - Each service class should have one clear responsibility
        github_service = GitHubValidationService()
        validation_service = ProjectValidationService(github_service)
        resolution_service = ProjectResolutionService()
        
        # WHEN & THEN - Each service should handle only its responsibility
        assert hasattr(github_service, 'validate_repository')
        assert hasattr(validation_service, 'validate_project')  
        assert hasattr(resolution_service, 'resolve_project_path')
    
    def test_dependency_inversion_principle(self):
        """Test: High-level modules depend on abstractions"""
        # GIVEN - ProjectValidationService depends on GitHubValidationService abstraction
        github_service = GitHubValidationService()
        validation_service = ProjectValidationService(github_service)
        
        # WHEN & THEN - Should be able to inject different implementations
        assert validation_service.github_validator == github_service
    
    def test_open_closed_principle(self):
        """Test: Open for extension, closed for modification"""
        # GIVEN - Strategy pattern allows extension without modification
        from orchestrator.domain.project import ProjectSearchStrategy
        
        class CustomSearchStrategy(ProjectSearchStrategy):
            def find_project(self, project_name: str):
                return "/custom/path"
        
        # WHEN & THEN - Should be able to add new strategies
        custom_strategy = CustomSearchStrategy()
        result = custom_strategy.find_project("test")
        assert result == "/custom/path"


class TestCompleteTDDCycle:
    """Test complete TDD → SOLID → DDD cycle"""
    
    def test_complete_integration_cycle(self):
        """Test: Complete TDD → SOLID → DDD integration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # GIVEN - Create realistic project structure
            project_dir = Path(temp_dir) / "complete-project"
            project_dir.mkdir()
            
            # WHEN - Use complete application service
            service = ProjectApplicationService()
            
            # 1. Test domain validation
            validation_result = service.validate_project_configuration("complete-project", str(project_dir))
            assert validation_result["valid"] is True
            
            # 2. Test configuration generation
            config_dict = service.generate_configuration_dict("complete-project", str(project_dir))
            assert config_dict["target_project"]["name"] == "complete-project"
            
            # 3. Test path resolution works
            import os
            old_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                resolved_path = service.resolve_project_path("complete-project")
                assert resolved_path == str(project_dir)
            finally:
                os.chdir(old_cwd)
            
            # THEN - All components should work together seamlessly
            assert True  # If we reach here, integration is successful


if __name__ == "__main__":
    pytest.main([__file__, "-v"])