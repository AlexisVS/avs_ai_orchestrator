#!/usr/bin/env python3
"""
Quality Gates - Garde-fous pour le développement TDD
Validation automatique de la qualité du code
"""

import subprocess
import re
import ast
from pathlib import Path
from typing import Dict, List, Any, Tuple
import json

class QualityGates:
    """Système de garde-fous qualité"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.quality_gates = config.get("quality_gates", {})
        
    def check_all_gates(self, files_to_check: List[Path]) -> Dict[str, Any]:
        """Vérifie tous les garde-fous"""
        results = {
            "passed": True,
            "issues": [],
            "metrics": {},
            "blockers": []
        }
        
        # 1. Tests coverage
        coverage_result = self.check_test_coverage()
        results["metrics"]["coverage"] = coverage_result
        
        if coverage_result["percentage"] < self.quality_gates.get("min_coverage", 80):
            results["passed"] = False
            results["blockers"].append(f"Coverage {coverage_result['percentage']}% below minimum {self.quality_gates.get('min_coverage', 80)}%")
        
        # 2. Lint check
        lint_result = self.check_lint(files_to_check)
        results["metrics"]["lint"] = lint_result
        
        if lint_result["errors"] > 0:
            results["passed"] = False
            results["blockers"].append(f"Linting errors: {lint_result['errors']}")
        
        # 3. Type checking
        if self.quality_gates.get("require_type_hints", True):
            type_result = self.check_type_hints(files_to_check)
            results["metrics"]["type_hints"] = type_result
            
            if type_result["errors"] > 0:
                results["passed"] = False
                results["blockers"].append(f"Type checking errors: {type_result['errors']}")
        
        # 4. Complexity check
        complexity_result = self.check_complexity(files_to_check)
        results["metrics"]["complexity"] = complexity_result
        
        max_complexity = self.quality_gates.get("max_complexity", 10)
        if complexity_result["max_complexity"] > max_complexity:
            results["passed"] = False
            results["blockers"].append(f"Complexity {complexity_result['max_complexity']} above limit {max_complexity}")
        
        # 5. Documentation check
        if self.quality_gates.get("require_docstrings", True):
            doc_result = self.check_docstrings(files_to_check)
            results["metrics"]["documentation"] = doc_result
            
            if doc_result["missing_docstrings"] > 0:
                results["issues"].append(f"Missing docstrings: {doc_result['missing_docstrings']} functions/classes")
        
        return results
    
    def check_test_coverage(self) -> Dict[str, Any]:
        """Vérifie la couverture de tests"""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--cov=.", "--cov-report=json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Lire le rapport JSON de coverage
                cov_file = Path("coverage.json")
                if cov_file.exists():
                    with open(cov_file) as f:
                        coverage_data = json.load(f)
                    
                    total_coverage = coverage_data["totals"]["percent_covered"]
                    
                    return {
                        "percentage": total_coverage,
                        "lines_covered": coverage_data["totals"]["covered_lines"],
                        "lines_total": coverage_data["totals"]["num_statements"],
                        "missing_lines": coverage_data["totals"]["missing_lines"]
                    }
            
            return {"percentage": 0, "error": "Coverage check failed"}
            
        except Exception as e:
            return {"percentage": 0, "error": str(e)}
    
    def check_lint(self, files: List[Path]) -> Dict[str, Any]:
        """Vérifie le linting avec ruff/pylint"""
        try:
            file_paths = [str(f) for f in files if f.suffix == '.py']
            
            # Essayer ruff d'abord (plus rapide)
            result = subprocess.run(
                ["python", "-m", "ruff", "check"] + file_paths,
                capture_output=True,
                text=True
            )
            
            errors = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            
            return {
                "errors": errors,
                "warnings": 0,
                "output": result.stdout,
                "tool": "ruff"
            }
            
        except FileNotFoundError:
            # Fallback vers flake8
            try:
                result = subprocess.run(
                    ["python", "-m", "flake8"] + [str(f) for f in files],
                    capture_output=True,
                    text=True
                )
                
                errors = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
                
                return {
                    "errors": errors,
                    "output": result.stdout,
                    "tool": "flake8"
                }
            except:
                return {"errors": 0, "error": "No linter available"}
    
    def check_type_hints(self, files: List[Path]) -> Dict[str, Any]:
        """Vérifie les type hints avec mypy"""
        try:
            file_paths = [str(f) for f in files if f.suffix == '.py']
            
            result = subprocess.run(
                ["python", "-m", "mypy", "--strict"] + file_paths,
                capture_output=True,
                text=True
            )
            
            errors = len([line for line in result.stdout.split('\n') if 'error:' in line])
            
            return {
                "errors": errors,
                "output": result.stdout,
                "warnings": len([line for line in result.stdout.split('\n') if 'warning:' in line])
            }
            
        except FileNotFoundError:
            return {"errors": 0, "error": "mypy not available"}
    
    def check_complexity(self, files: List[Path]) -> Dict[str, Any]:
        """Vérifie la complexité cyclomatique"""
        try:
            max_complexity = 0
            complex_functions = []
            
            for file_path in files:
                if file_path.suffix != '.py':
                    continue
                    
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        tree = ast.parse(f.read())
                        complexity = self._calculate_complexity(tree)
                        
                        if complexity > max_complexity:
                            max_complexity = complexity
                            
                        if complexity > self.quality_gates.get("max_complexity", 10):
                            complex_functions.append({
                                "file": str(file_path),
                                "complexity": complexity
                            })
                            
                    except SyntaxError:
                        continue
            
            return {
                "max_complexity": max_complexity,
                "complex_functions": complex_functions,
                "threshold": self.quality_gates.get("max_complexity", 10)
            }
            
        except Exception as e:
            return {"max_complexity": 0, "error": str(e)}
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calcule la complexité cyclomatique simplifiée"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.Try):
                complexity += len(child.handlers)
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
                
        return complexity
    
    def check_docstrings(self, files: List[Path]) -> Dict[str, Any]:
        """Vérifie la présence de docstrings"""
        missing_docstrings = 0
        total_functions = 0
        
        for file_path in files:
            if file_path.suffix != '.py':
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        total_functions += 1
                        
                        # Vérifier si une docstring existe
                        if not (node.body and isinstance(node.body[0], ast.Expr) 
                               and isinstance(node.body[0].value, ast.Constant)
                               and isinstance(node.body[0].value.value, str)):
                            missing_docstrings += 1
                            
            except (SyntaxError, UnicodeDecodeError):
                continue
        
        return {
            "missing_docstrings": missing_docstrings,
            "total_functions": total_functions,
            "coverage_percentage": ((total_functions - missing_docstrings) / total_functions * 100) if total_functions > 0 else 100
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Exécute tous les tests"""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "-v", "--tb=short"],
                capture_output=True,
                text=True
            )
            
            # Parser les résultats
            output_lines = result.stdout.split('\n')
            
            passed = len([line for line in output_lines if '::' in line and 'PASSED' in line])
            failed = len([line for line in output_lines if '::' in line and 'FAILED' in line])
            errors = len([line for line in output_lines if '::' in line and 'ERROR' in line])
            
            return {
                "success": result.returncode == 0,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "output": result.stdout,
                "stderr": result.stderr
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_quality_report(self, results: Dict[str, Any]) -> str:
        """Génère un rapport de qualité formaté"""
        report = "# Quality Gates Report\n\n"
        
        if results["passed"]:
            report += "## ✅ All Quality Gates Passed!\n\n"
        else:
            report += "## ❌ Quality Gates Failed\n\n"
            report += "### Blockers:\n"
            for blocker in results["blockers"]:
                report += f"- 🚫 {blocker}\n"
            report += "\n"
        
        if results["issues"]:
            report += "### Issues (Non-blocking):\n"
            for issue in results["issues"]:
                report += f"- ⚠️ {issue}\n"
            report += "\n"
        
        report += "## Metrics\n\n"
        
        metrics = results["metrics"]
        
        if "coverage" in metrics:
            cov = metrics["coverage"]
            report += f"- **Coverage:** {cov.get('percentage', 0):.1f}%\n"
        
        if "lint" in metrics:
            lint = metrics["lint"]
            report += f"- **Lint Errors:** {lint.get('errors', 0)}\n"
        
        if "complexity" in metrics:
            comp = metrics["complexity"]
            report += f"- **Max Complexity:** {comp.get('max_complexity', 0)}\n"
        
        if "documentation" in metrics:
            doc = metrics["documentation"]
            report += f"- **Documentation:** {doc.get('coverage_percentage', 0):.1f}% functions documented\n"
        
        return report

# Exemple d'utilisation
if __name__ == "__main__":
    config = {
        "quality_gates": {
            "min_coverage": 80,
            "max_complexity": 10,
            "require_docstrings": True,
            "require_type_hints": True
        }
    }
    
    gates = QualityGates(config)
    files_to_check = [Path("github_tdd_orchestrator.py")]
    
    results = gates.check_all_gates(files_to_check)
    print(gates.generate_quality_report(results))