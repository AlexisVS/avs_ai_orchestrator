"""
Unit Tests for Project Value Objects (DDD Domain Layer)
Tests focalisés sur la logique métier pure, sans dépendances externes
"""

import pytest
import tempfile
from pathlib import Path
import sys

# Ajouter le path src pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from orchestrator.domain.project import (
    ProjectName,
    ProjectPath, 
    GitHubRepository
)


class TestProjectNameValueObject:
    """Tests for ProjectName Value Object (DDD: Value Object pattern)"""
    
    def test_project_name_should_accept_valid_alphanumeric_names(self):
        """Test: ProjectName should accept valid alphanumeric names"""
        # GIVEN
        valid_names = [
            "weather-dashboard",
            "my_project", 
            "project123",
            "test.app",
            "a"
        ]
        
        # WHEN & THEN
        for name in valid_names:
            project_name = ProjectName(name)
            assert project_name.value == name
    
    def test_project_name_should_be_immutable(self):
        """Test: ProjectName should be immutable (Value Object characteristic)"""
        # GIVEN
        project_name = ProjectName("immutable-project")
        
        # WHEN & THEN - Should not be able to modify
        with pytest.raises(AttributeError):
            project_name.value = "modified"
    
    def test_project_name_should_reject_empty_or_whitespace_names(self):
        """Test: ProjectName should reject empty or whitespace-only names"""
        # GIVEN
        invalid_names = ["", " ", "\t", "\n", "   "]
        
        # WHEN & THEN
        for name in invalid_names:
            with pytest.raises(ValueError, match="Project name cannot be empty"):
                ProjectName(name)
    
    def test_project_name_should_reject_names_exceeding_length_limit(self):
        """Test: ProjectName should enforce maximum length constraint"""
        # GIVEN
        long_name = "a" * 51  # Exceeds 50 character limit
        
        # WHEN & THEN
        with pytest.raises(ValueError, match="Project name too long"):
            ProjectName(long_name)
    
    def test_project_name_should_reject_invalid_characters(self):
        """Test: ProjectName should reject names with invalid characters"""
        # GIVEN
        invalid_names = [
            "project@invalid",
            "project with spaces", 
            "project#hash",
            "project$dollar",
            "project!exclamation"
        ]
        
        # WHEN & THEN
        for name in invalid_names:
            with pytest.raises(ValueError, match="Project name must be alphanumeric"):
                ProjectName(name)
    
    def test_project_names_should_be_equal_when_values_equal(self):
        """Test: Value Object equality based on value (DDD characteristic)"""
        # GIVEN
        name1 = ProjectName("same-project")
        name2 = ProjectName("same-project") 
        name3 = ProjectName("different-project")
        
        # WHEN & THEN
        assert name1 == name2  # Same value = equal
        assert name1 != name3  # Different value = not equal
        assert hash(name1) == hash(name2)  # Same hash for same value


class TestProjectPathValueObject:
    """Tests for ProjectPath Value Object (DDD: Value Object pattern)"""
    
    def test_project_path_should_accept_valid_existing_directory(self):
        """Test: ProjectPath should accept valid existing directories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # GIVEN
            valid_path = Path(temp_dir)
            
            # WHEN
            project_path = ProjectPath(valid_path)
            
            # THEN
            assert project_path.value == valid_path
            assert str(project_path) == str(valid_path)
    
    def test_project_path_should_be_immutable(self):
        """Test: ProjectPath should be immutable (Value Object characteristic)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # GIVEN
            project_path = ProjectPath(Path(temp_dir))
            
            # WHEN & THEN - Should not be able to modify
            with pytest.raises(AttributeError):
                project_path.value = Path("/different/path")
    
    def test_project_path_should_reject_nonexistent_path(self):
        """Test: ProjectPath should reject non-existent paths"""
        # GIVEN
        nonexistent_path = Path("/this/path/does/not/exist")
        
        # WHEN & THEN
        with pytest.raises(ValueError, match="Project path does not exist"):
            ProjectPath(nonexistent_path)
    
    def test_project_path_should_reject_file_instead_of_directory(self):
        """Test: ProjectPath should reject files (only directories allowed)"""
        with tempfile.NamedTemporaryFile() as temp_file:
            # GIVEN
            file_path = Path(temp_file.name)
            
            # WHEN & THEN
            with pytest.raises(ValueError, match="Project path is not a directory"):
                ProjectPath(file_path)
    
    def test_project_paths_should_be_equal_when_values_equal(self):
        """Test: Value Object equality based on value"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # GIVEN
            path = Path(temp_dir)
            path1 = ProjectPath(path)
            path2 = ProjectPath(path)
            
            # WHEN & THEN
            assert path1 == path2
            assert hash(path1) == hash(path2)


class TestGitHubRepositoryValueObject:
    """Tests for GitHubRepository Value Object (DDD: Value Object pattern)"""
    
    def test_github_repository_should_accept_valid_owner_and_repo(self):
        """Test: GitHubRepository should accept valid owner and repo"""
        # GIVEN
        owner = "AlexisVS"
        repo = "weather-dashboard"
        project_id = "123"
        
        # WHEN
        github_repo = GitHubRepository(owner, repo, project_id)
        
        # THEN
        assert github_repo.owner == owner
        assert github_repo.repo == repo
        assert github_repo.project_id == project_id
        assert github_repo.full_name == f"{owner}/{repo}"
    
    def test_github_repository_should_be_immutable(self):
        """Test: GitHubRepository should be immutable (Value Object characteristic)"""
        # GIVEN
        github_repo = GitHubRepository("owner", "repo")
        
        # WHEN & THEN - Should not be able to modify
        with pytest.raises(AttributeError):
            github_repo.owner = "modified"
    
    def test_github_repository_should_handle_optional_project_id(self):
        """Test: GitHubRepository should handle optional project_id"""
        # GIVEN & WHEN
        github_repo = GitHubRepository("owner", "repo")  # No project_id
        
        # THEN
        assert github_repo.project_id is None
        assert github_repo.full_name == "owner/repo"
    
    def test_github_repository_should_reject_empty_owner_or_repo(self):
        """Test: GitHubRepository should reject empty owner or repo"""
        # GIVEN
        empty_values = ["", None]
        
        # WHEN & THEN
        for empty_value in empty_values:
            with pytest.raises(ValueError, match="GitHub owner and repo are required"):
                GitHubRepository(empty_value, "repo")
            
            with pytest.raises(ValueError, match="GitHub owner and repo are required"):
                GitHubRepository("owner", empty_value)
    
    def test_github_repositories_should_be_equal_when_all_values_equal(self):
        """Test: Value Object equality based on all field values"""
        # GIVEN
        repo1 = GitHubRepository("owner", "repo", "123")
        repo2 = GitHubRepository("owner", "repo", "123")
        repo3 = GitHubRepository("owner", "repo", "456")  # Different project_id
        
        # WHEN & THEN
        assert repo1 == repo2  # Same values = equal
        assert repo1 != repo3  # Different project_id = not equal
        assert hash(repo1) == hash(repo2)  # Same hash for same values


class TestValueObjectsIntegration:
    """Integration tests for Value Objects working together"""
    
    def test_value_objects_should_compose_correctly_in_aggregate(self):
        """Test: Value Objects should compose correctly in domain aggregates"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # GIVEN
            project_name = ProjectName("integration-test")
            project_path = ProjectPath(Path(temp_dir))
            github_repo = GitHubRepository("TestOwner", "integration-test", "999")
            
            # WHEN - Value Objects should work together
            composite_data = {
                "name": project_name.value,
                "path": str(project_path),
                "github": github_repo.full_name,
                "project_id": github_repo.project_id
            }
            
            # THEN
            assert composite_data["name"] == "integration-test"
            assert composite_data["path"] == temp_dir
            assert composite_data["github"] == "TestOwner/integration-test"
            assert composite_data["project_id"] == "999"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])