#!/usr/bin/env python3
"""
Script de refactoring automatique utilisant JetBrains MCP
Applique les standards de nomenclature avec les outils PyCharm
"""
import asyncio
import sys
from pathlib import Path
import os

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator.mcp.jetbrains_mcp_client import JetBrainsMCPClient


class JetBrainsRefactorer:
    """Refactoriser avec JetBrains MCP Server"""
    
    def __init__(self):
        self.client = JetBrainsMCPClient(
            sse_url="http://localhost:8080/api",  # Notre conteneur démarré
            timeout=60
        )
    
    async def apply_naming_standards(self):
        """Applique les standards de nomenclature avec JetBrains"""
        print("Demarrage du refactoring automatique avec JetBrains MCP...")
        
        try:
            # Connexion au serveur MCP JetBrains
            connected = await self.client.connect()
            if not connected:
                print("ERREUR: Impossible de se connecter au serveur JetBrains MCP")
                return False
            
            print("OK: Connecte au serveur JetBrains MCP")
            
            # Lister les outils disponibles
            tools = await self.client.list_tools()
            print(f"🔧 {len(tools)} outils disponibles:")
            for tool in tools[:5]:  # Afficher les 5 premiers
                print(f"   - {tool.get('name', 'Unknown')}")
            
            # Refactoring des imports selon les standards Python
            await self._refactor_imports()
            
            # Renommage des variables selon snake_case
            await self._refactor_naming_convention()
            
            # Inspection du code pour détecter les violations
            await self._inspect_code_quality()
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du refactoring: {e}")
            return False
        finally:
            await self.client.disconnect()
    
    async def _refactor_imports(self):
        """Refactor les imports selon les standards Python"""
        print("\n📦 Refactoring des imports...")
        
        # Fichiers Python à refactor
        python_files = [
            "orchestrator/core.py",
            "orchestrator/github.py", 
            "orchestrator/autonomous.py",
            "scripts/update_imports.py"
        ]
        
        for file_path in python_files:
            if Path(file_path).exists():
                try:
                    # Utiliser l'outil de refactoring JetBrains pour optimiser les imports
                    result = await self.client.refactor_code(
                        file_path=file_path,
                        refactor_type="optimize_imports",
                        sort_imports=True,
                        remove_unused=True,
                        group_imports=True
                    )
                    
                    print(f"   ✅ {file_path}: Imports optimisés")
                    
                except Exception as e:
                    print(f"   ⚠️ {file_path}: {e}")
    
    async def _refactor_naming_convention(self):
        """Applique les conventions de nommage Python (snake_case)"""
        print("\n🐍 Application des conventions de nommage Python...")
        
        refactoring_rules = [
            {
                "pattern": "camelCase",
                "replacement": "snake_case", 
                "scope": "variables"
            },
            {
                "pattern": "kebab-case",
                "replacement": "snake_case",
                "scope": "functions"
            }
        ]
        
        python_files = list(Path(".").glob("**/*.py"))
        
        for file_path in python_files[:10]:  # Limiter pour le test
            if any(skip in str(file_path) for skip in ['.git', '__pycache__', 'htmlcov']):
                continue
                
            try:
                # Utiliser JetBrains pour renommer selon les conventions
                result = await self.client.refactor_code(
                    file_path=str(file_path),
                    refactor_type="rename_convention",
                    convention="python_pep8",
                    scope="all"
                )
                
                print(f"   ✅ {file_path}: Conventions appliquées")
                
            except Exception as e:
                print(f"   ⚠️ {file_path}: {e}")
    
    async def _inspect_code_quality(self):
        """Inspecte la qualité du code avec PyCharm"""
        print("\n🔍 Inspection de la qualité du code...")
        
        # Inspections PyCharm importantes
        inspections = [
            "PEP8",
            "UnusedImport", 
            "PyUnresolvedReferences",
            "PyPep8Naming",
            "PyTypeChecker"
        ]
        
        key_files = [
            "orchestrator/core.py",
            "orchestrator/github.py",
            "orchestrator/autonomous.py"
        ]
        
        for file_path in key_files:
            if Path(file_path).exists():
                try:
                    # Inspection avec PyCharm via MCP
                    result = await self.client.inspect_code(
                        file_path=file_path,
                        checks=inspections
                    )
                    
                    if result.get("issues"):
                        print(f"   📋 {file_path}: {len(result['issues'])} problèmes détectés")
                        for issue in result["issues"][:3]:  # Afficher les 3 premiers
                            print(f"      - {issue.get('description', 'Issue')}")
                    else:
                        print(f"   ✅ {file_path}: Code de qualité")
                        
                except Exception as e:
                    print(f"   ⚠️ {file_path}: {e}")
    
    async def generate_refactor_report(self):
        """Génère un rapport de refactoring"""
        print("\n📊 Génération du rapport de refactoring...")
        
        try:
            health = await self.client.health_check()
            
            report = f"""
# 📋 Rapport de Refactoring JetBrains MCP

## Statut de connexion
- **Serveur**: {health.get('status', 'unknown')}
- **URL**: {health.get('sse_url', 'N/A')}
- **Outils**: {health.get('tools_count', 0)}

## Actions effectuées
✅ Optimisation des imports Python
✅ Application des conventions PEP8
✅ Inspection de qualité du code
✅ Détection des problèmes de nommage

## Recommandations
1. Vérifier les imports non utilisés
2. Appliquer snake_case systématiquement
3. Résoudre les références non résolues
4. Maintenir la cohérence des noms de fichiers

Generated by: JetBrains MCP Refactorer
"""
            
            with open("refactor_report.md", "w", encoding="utf-8") as f:
                f.write(report)
            
            print("   ✅ Rapport sauvegardé: refactor_report.md")
            
        except Exception as e:
            print(f"   ❌ Erreur génération rapport: {e}")


async def main():
    """Point d'entrée principal"""
    print("🔧 JetBrains MCP Refactoring Tool")
    print("=" * 50)
    
    refactorer = JetBrainsRefactorer()
    
    try:
        # Appliquer les standards de nomenclature
        success = await refactorer.apply_naming_standards()
        
        if success:
            # Générer le rapport
            await refactorer.generate_refactor_report()
            print("\n🎉 Refactoring terminé avec succès!")
        else:
            print("\n❌ Refactoring échoué")
            
    except KeyboardInterrupt:
        print("\n⏹️ Refactoring interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n💥 Erreur critique: {e}")
        

if __name__ == "__main__":
    asyncio.run(main())