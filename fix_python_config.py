"""
Script pour diagnostiquer et potentiellement corriger la configuration Python
"""

import sys
import os
import sysconfig
from pathlib import Path

def diagnose_python_config():
    print("=== DIAGNOSTIC CONFIGURATION PYTHON ===")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print()
    
    print("=== CHEMINS PYTHON ===")
    print(f"sys.prefix: {sys.prefix}")
    print(f"sys.base_prefix: {sys.base_prefix}")
    print(f"sys.exec_prefix: {sys.exec_prefix}")
    print()
    
    print("=== SYSCONFIG PATHS ===")
    for name in ['stdlib', 'platstdlib', 'purelib', 'platlib', 'include', 'scripts']:
        try:
            path = sysconfig.get_path(name)
            exists = Path(path).exists() if path else False
            print(f"{name:12}: {path} {'✅' if exists else '❌'}")
        except Exception as e:
            print(f"{name:12}: ERROR - {e}")
    print()
    
    print("=== VARIABLES D'ENVIRONNEMENT ===")
    env_vars = ['PYTHONPATH', 'PYTHONHOME', 'VIRTUAL_ENV', 'PATH']
    for var in env_vars:
        value = os.environ.get(var, 'Not Set')
        print(f"{var}: {value[:100]}{'...' if len(value) > 100 else ''}")
    print()
    
    print("=== DIAGNOSTIC ===")
    if sys.prefix != sys.base_prefix:
        print("✅ Dans un environnement virtuel")
    else:
        print("⚠️  Utilise Python système")
        
    # Vérifier si les chemins stdlib existent
    stdlib_path = sysconfig.get_path('stdlib')
    if stdlib_path and Path(stdlib_path).exists():
        print("✅ Bibliothèque standard trouvée")
    else:
        print("❌ Problème avec la bibliothèque standard")
        
        # Proposer des solutions
        print("\n=== SOLUTIONS PROPOSÉES ===")
        print("1. Recréer l'environnement virtuel:")
        print("   rm -rf .venv && python -m venv .venv")
        print("2. Utiliser Python système temporairement:")
        print("   py -m pytest tests/...")
        print("3. Définir PYTHONHOME explicitement:")
        base_python = Path(sys.base_prefix)
        print(f"   set PYTHONHOME={base_python}")

if __name__ == "__main__":
    diagnose_python_config()