#!/usr/bin/env python3
"""
Configuration rapide par projet (compatible Windows)
"""

import os
from pathlib import Path

def setup_project():
    """Configuration interactive pour un nouveau projet"""
    
    print("Configuration GitHub TDD Orchestrator")
    print("=" * 50)
    
    # Charger la configuration existante
    env_file = Path(".env")
    config = {}
    
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    
    current_owner = config.get('GITHUB_REPO_OWNER', 'AlexisVS')
    current_repo = config.get('GITHUB_REPO_NAME', '')
    current_project = config.get('GITHUB_PROJECT_NUMBER', '1')
    
    print(f"\nConfiguration actuelle:")
    print(f"   Owner: {current_owner}")
    print(f"   Repo: {current_repo}")
    print(f"   Project: #{current_project}")
    
    print(f"\nNouveau projet:")
    
    # Demander les infos du nouveau projet
    repo_name = input(f"Repository name: ").strip()
    if not repo_name:
        print("Nom du repository requis")
        return None
    
    project_number = input(f"Project number (defaut: 1): ").strip() or "1"
    
    # Mettre à jour la configuration
    config['GITHUB_REPO_NAME'] = repo_name
    config['GITHUB_PROJECT_NUMBER'] = project_number
    
    # Réécrire le fichier .env
    env_content = f"""# Configuration sécurisée GitHub TDD Orchestrator
# Ce fichier est dans .gitignore - ne sera JAMAIS commité

GITHUB_TOKEN={config.get('GITHUB_TOKEN', '')}
GITHUB_REPO_OWNER={current_owner}
GITHUB_REPO_NAME={repo_name}
GITHUB_PROJECT_NUMBER={project_number}

# Configuration LM Studio
LM_STUDIO_URL=http://127.0.0.1:1234
LM_STUDIO_MODEL=qwen/qwen3-coder-30b
"""
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"\n[OK] Configuration mise a jour:")
    print(f"   Repository: {current_owner}/{repo_name}")
    print(f"   Project: #{project_number}")
    print(f"   URL: https://github.com/{current_owner}/{repo_name}/projects/{project_number}")
    
    return {
        'owner': current_owner,
        'repo': repo_name,
        'project': int(project_number)
    }

def show_usage():
    """Affiche les commandes disponibles"""
    
    print(f"\n=== COMMANDES DISPONIBLES ===")
    print(f"")
    print(f"1. Mode demo (simulation):")
    print(f"   python demo_simple.py")
    print(f"")
    print(f"2. Test IA Qwen3-Coder:")
    print(f"   python dev_orchestrator_lm.py --tasks 'votre tache'")
    print(f"")
    print(f"3. Orchestrateur complet (GitHub reel):")
    print(f"   python start_github_dev.py")
    print(f"")
    print(f"4. Configuration projet:")
    print(f"   python project_config.py")

if __name__ == "__main__":
    print("Configuration par projet")
    print("=" * 30)
    
    choice = input("Configurer un nouveau projet? (y/N): ").lower()
    
    if choice == 'y':
        project_config = setup_project()
        if project_config:
            print(f"\n[SUCCESS] Projet configure!")
    
    show_usage()