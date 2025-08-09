#!/usr/bin/env python3
"""
Script pour corriger automatiquement tous les problemes d'encodage dans l'orchestrateur
"""

from pathlib import Path
import re


def clean_accents(text):
    """Remplacer tous les accents par des equivalents ASCII"""
    replacements = {
        # Minuscules
        'e': 'e', 'e': 'e', 'e': 'e', 'e': 'e',
        'a': 'a', 'a': 'a', 'a': 'a', 'a': 'a',
        'i': 'i', 'i': 'i', 'i': 'i', 'i': 'i',
        'o': 'o', 'o': 'o', 'o': 'o', 'o': 'o',
        'u': 'u', 'u': 'u', 'u': 'u', 'u': 'u',
        'c': 'c', 'n': 'n',
        # Majuscules
        'E': 'E', 'E': 'E', 'E': 'E', 'E': 'E',
        'A': 'A', 'A': 'A', 'A': 'A', 'A': 'A',
        'I': 'I', 'I': 'I', 'I': 'I', 'I': 'I',
        'O': 'O', 'O': 'O', 'O': 'O', 'O': 'O',
        'U': 'U', 'U': 'U', 'U': 'U', 'U': 'U',
        'C': 'C', 'N': 'N'
    }
    
    result = text
    for accented, ascii_char in replacements.items():
        result = result.replace(accented, ascii_char)
    return result


def fix_file_encoding(file_path: Path):
    """Corriger l'encodage d'un fichier specifique"""
    if not file_path.exists() or file_path.suffix not in ['.py']:
        return False
        
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Nettoyer les accents
        content = clean_accents(content)
        
        # Si des changements ont ete effectues
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            print(f"[OK] Corrige: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"[ERROR] Erreur sur {file_path}: {e}")
        return False


def main():
    """Corriger tous les fichiers Python de l'orchestrateur"""
    print("[FIX] Correction automatique de tous les problemes d'encodage")
    print("=" * 60)
    
    base_path = Path(__file__).parent.parent
    
    # Fichiers critiques a corriger
    critical_files = [
        "orchestrator/autonomous.py",
        "src/orchestrator/agents/autonomous_orchestrator.py", 
        "src/orchestrator/agents/github_sync_agent.py",
        "src/orchestrator/agents/bug_detector_agent.py",
        "src/orchestrator/agents/code_generator_agent.py",
        "src/orchestrator/agents/meta_cognitive_agent.py",
        "src/orchestrator/agents/self_evolution_agent.py",
        "src/orchestrator/agents/test_runner_agent.py"
    ]
    
    fixed_count = 0
    
    # Corriger les fichiers critiques d'abord
    print("[FILES] Correction des fichiers critiques:")
    for file_rel_path in critical_files:
        file_path = base_path / file_rel_path
        if fix_file_encoding(file_path):
            fixed_count += 1
    
    # Corriger tous les autres fichiers Python recursivement  
    print("\n[RECURSIVE] Correction recursive de tous les fichiers .py:")
    for py_file in base_path.rglob("*.py"):
        # Eviter les fichiers deja traites et certains dossiers
        skip_dirs = ['.venv', '__pycache__', '.pytest_cache', 'node_modules']
        if any(skip_dir in str(py_file) for skip_dir in skip_dirs):
            continue
            
        if fix_file_encoding(py_file):
            fixed_count += 1
    
    print("\n" + "=" * 60)
    print(f"[SUCCESS] Correction terminee: {fixed_count} fichiers modifies")
    
    if fixed_count > 0:
        print("[RESTART] Redemarrage de l'orchestrateur recommande pour appliquer les changements")
    else:
        print("[OK] Tous les fichiers etaient deja corrects !")


if __name__ == "__main__":
    main()