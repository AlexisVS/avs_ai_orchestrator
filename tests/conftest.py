"""
Configuration des fixtures pytest pour tous les tests
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Ajouter src au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import pour éviter l'erreur de package
import orchestrator


@pytest.fixture
def event_loop():
    """Créer une boucle d'événements pour les tests async"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """Créer un répertoire temporaire pour les tests"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_config():
    """Configuration mock pour les tests"""
    return {
        "project": {
            "name": "test-project",
            "type": "python",
            "description": "Test project for TDD"
        },
        "github": {
            "enabled": False,
            "owner": "test-owner",
            "repo_name": "test-repo"
        },
        "ai": {
            "provider": "mock",
            "model": "test-model"
        },
        "mcp": {
            "enabled": False,
            "servers": []
        },
        "docker_models": [
            {
                "name": "test-docker-model",
                "container_name": "mcp-test-container",
                "docker_host": "unix:///var/run/docker.sock",
                "auto_start": True
            }
        ],
        "lm_studio": {
            "name": "test-lm-studio",
            "base_url": "http://localhost:1234",
            "timeout": 30
        },
        "jetbrains_mcp": {
            "name": "jetbrains-inspector",
            "enabled": True,
            "java_command": r"C:\Users\alexi\AppData\Local\Programs\PyCharm Community\jbr\bin\java.exe",
            "mcp_port": "64342"
        }
    }


@pytest.fixture
def mock_ai_client():
    """Client AI mocké pour les tests"""
    client = AsyncMock()
    client.generate_response = AsyncMock(return_value="Generated response")
    client.test_connection = AsyncMock(return_value=True)
    return client


@pytest.fixture
def mock_github_client():
    """Client GitHub mocké pour les tests"""
    client = Mock()
    client.get_repo = Mock()
    client.create_issue = Mock()
    client.list_issues = Mock(return_value=[])
    return client


@pytest.fixture
def mock_mcp_server():
    """Serveur MCP mocké pour les tests"""
    server = AsyncMock()
    server.connect = AsyncMock(return_value=True)
    server.send_message = AsyncMock(return_value={"status": "ok"})
    server.disconnect = AsyncMock()
    return server


@pytest.fixture
def config_file(temp_dir, mock_config):
    """Créer un fichier de configuration temporaire"""
    import yaml
    config_path = temp_dir / "test_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(mock_config, f)
    return str(config_path)


@pytest.fixture
def mock_docker_client():
    """Client Docker mocké pour les tests"""
    client = Mock()
    client.containers = Mock()
    client.containers.list = Mock(return_value=[])
    client.containers.run = Mock()
    return client


@pytest.fixture
def mock_lm_studio_client():
    """Client LM Studio mocké pour les tests"""
    client = AsyncMock()
    client.connect = AsyncMock(return_value=True)
    client.generate = AsyncMock(return_value="LM Studio response")
    client.list_models = AsyncMock(return_value=["model1", "model2"])
    client.health_check = AsyncMock(return_value={"status": "healthy", "models_available": 2})
    return client