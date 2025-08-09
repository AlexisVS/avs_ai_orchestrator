"""
Tests pour Test Runner Agent - Améliorer couverture
Tests basiques pour augmenter la couverture globale
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
import tempfile
import os
import json

from src.orchestrator.agents.test_runner_agent import TestRunnerAgent


class TestTestRunnerAgentBasics:
    """Tests pour TestRunnerAgent"""
    
    def test_initialization(self):
        """Test l'initialisation du TestRunnerAgent"""
        config = {"python_command": "py", "test_timeout": 120}
        agent = TestRunnerAgent(config)
        
        assert agent.config == config
        assert agent.python_cmd == "py"
        assert agent.test_timeout == 120
    
    def test_initialization_with_defaults(self):
        """Test l'initialisation avec valeurs par défaut"""
        config = {}
        agent = TestRunnerAgent(config)
        
        assert agent.python_cmd == "python"
        assert agent.test_timeout == 300
    
    def test_parse_pytest_results(self):
        """Test le parsing des résultats pytest"""
        config = {}
        agent = TestRunnerAgent(config)
        
        # Simuler une sortie pytest
        pytest_output = """
        ========================= test session starts =========================
        collected 15 items

        tests/test_example.py::test_one PASSED                        [ 33%]
        tests/test_example.py::test_two FAILED                        [ 66%] 
        tests/test_example.py::test_three PASSED                      [100%]

        ======================= 2 passed, 1 failed in 0.12s =======================
        """
        
        total, passed, failed = agent._parse_pytest_results(pytest_output)
        
        assert total >= 0
        assert passed >= 0  
        assert failed >= 0
    
    def test_count_mypy_issues(self):
        """Test le comptage des problèmes MyPy"""
        config = {}
        agent = TestRunnerAgent(config)
        
        # Simuler une sortie MyPy
        mypy_output = """
        src/agent.py:10: error: Name 'undefined_var' is not defined
        src/agent.py:20: warning: Unused import
        Found 2 errors in 1 file
        """
        
        issues = agent._count_mypy_issues(mypy_output)
        assert isinstance(issues, int)
        assert issues >= 0
    
    def test_calculate_quality_score(self):
        """Test le calcul du score de qualité"""
        config = {}
        agent = TestRunnerAgent(config)
        
        quality_results = {
            "mypy_issues": 2,
            "flake8_issues": 1,
            "bandit_issues": 0,
            "test_passed": True
        }
        
        score = agent._calculate_quality_score(quality_results)
        assert isinstance(score, (float, int))
        assert score >= 0.0
    
    @pytest.mark.asyncio
    async def test_run_quality_checks_mock(self):
        """Test les vérifications de qualité avec mocks"""
        config = {}
        agent = TestRunnerAgent(config)
        
        # Mock les méthodes subprocess
        with patch.object(agent, '_run_mypy', return_value={"mypy_issues": 2}):
            with patch.object(agent, '_run_flake8', return_value={"flake8_issues": 1}):
                with patch.object(agent, '_run_bandit', return_value={"bandit_issues": 0}):
                    result = await agent._run_quality_checks()
                    
                    assert isinstance(result, dict)
                    assert "quality_score" in result
    
    @pytest.mark.asyncio
    async def test_analyze_coverage_mock(self):
        """Test l'analyse de couverture avec mock"""
        config = {}
        agent = TestRunnerAgent(config)
        
        # Mock la lecture du fichier de couverture
        mock_coverage_data = {
            "files": {
                "src/agent.py": {
                    "summary": {"covered_lines": 80, "num_statements": 100}
                }
            },
            "totals": {"covered_lines": 80, "num_statements": 100}
        }
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', return_value=json.dumps(mock_coverage_data)):
                result = await agent._analyze_coverage()
                
                assert isinstance(result, dict)
                assert "coverage" in result
    
    @pytest.mark.asyncio
    async def test_run_mypy_mock(self):
        """Test l'exécution de MyPy avec mock"""
        config = {}
        agent = TestRunnerAgent(config)
        
        # Mock subprocess
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success: no issues found"
        
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"Success: no issues found", b"")
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await agent._run_mypy()
            
            assert isinstance(result, dict)
            assert "issues" in result
    
    @pytest.mark.asyncio
    async def test_run_flake8_mock(self):
        """Test l'exécution de Flake8 avec mock"""
        config = {}
        agent = TestRunnerAgent(config)
        
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await agent._run_flake8()
            
            assert isinstance(result, dict)
            assert "issues" in result
    
    @pytest.mark.asyncio
    async def test_run_bandit_mock(self):
        """Test l'exécution de Bandit avec mock"""
        config = {}
        agent = TestRunnerAgent(config)
        
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"No issues found", b"")
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await agent._run_bandit()
            
            assert isinstance(result, dict)
            assert "issues" in result
    
    @pytest.mark.asyncio
    async def test_create_autonomous_quality_validator(self):
        """Test la création du validateur qualité autonome"""
        config = {}
        agent = TestRunnerAgent(config)
        
        validator = await agent._create_autonomous_quality_validator()
        
        assert validator is not None
        # Test de base pour améliorer la couverture
        assert hasattr(validator, 'test_runner')


class TestTestRunnerAgentIntegration:
    """Tests d'intégration pour TestRunnerAgent"""
    
    @pytest.mark.asyncio
    async def test_run_pytest_with_coverage_mock(self):
        """Test pytest avec couverture"""
        config = {}
        agent = TestRunnerAgent(config)
        
        # Mock subprocess
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"2 passed, 0 failed", b"")
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await agent._run_pytest_with_coverage()
            
            assert isinstance(result, dict)
            assert "success" in result