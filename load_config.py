#!/usr/bin/env python3
"""
Chargeur de configuration sécurisée
"""

import os
from pathlib import Path

def load_github_config():
    """Charge la configuration GitHub depuis différentes sources"""
    
    # 1. Essayer les variables d'environnement
    github_token = os.getenv("GITHUB_TOKEN")
    
    if github_token:
        print("✅ Token trouvé dans les variables d'environnement")
        return {
            "github_token": github_token,
            "repo_owner": os.getenv("GITHUB_REPO_OWNER", ""),
            "repo_name": os.getenv("GITHUB_REPO_NAME", ""),
            "project_number": int(os.getenv("GITHUB_PROJECT_NUMBER", "1"))
        }
    
    # 2. Essayer le fichier .env
    env_file = Path(".env")
    if env_file.exists():
        print("✅ Fichier .env trouvé")
        
        config = {}
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
        
        if 'GITHUB_TOKEN' in config:
            return {
                "github_token": config.get("GITHUB_TOKEN"),
                "repo_owner": config.get("GITHUB_REPO_OWNER", ""),
                "repo_name": config.get("GITHUB_REPO_NAME", ""),
                "project_number": int(config.get("GITHUB_PROJECT_NUMBER", "1"))
            }
    
    # 3. Demander à l'utilisateur
    print("❌ Aucune configuration trouvée")
    print("\nOptions:")
    print("1. Configurer maintenant")
    print("2. Utiliser le mode démo")
    
    choice = input("Choix (1/2): ").strip()
    
    if choice == "1":
        print("\n📝 Configuration manuelle:")
        token = input("GitHub Token: ").strip()
        owner = input("Repository Owner: ").strip()
        name = input("Repository Name: ").strip()
        project = input("Project Number (1): ").strip() or "1"
        
        return {
            "github_token": token,
            "repo_owner": owner, 
            "repo_name": name,
            "project_number": int(project)
        }
    
    return None

def save_to_env(config):
    """Sauvegarde la configuration dans .env"""
    
    env_content = f"""# Configuration GitHub TDD Orchestrator
GITHUB_TOKEN={config['github_token']}
GITHUB_REPO_OWNER={config['repo_owner']}
GITHUB_REPO_NAME={config['repo_name']}
GITHUB_PROJECT_NUMBER={config['project_number']}

# Configuration LM Studio
LM_STUDIO_URL=http://127.0.0.1:1234
LM_STUDIO_MODEL=qwen/qwen3-coder-30b
"""
    
    with open(".env", 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Configuration sauvegardée dans .env")

if __name__ == "__main__":
    config = load_github_config()
    
    if config:
        print(f"\n✅ Configuration chargée:")
        print(f"   Token: {config['github_token'][:20]}...")
        print(f"   Repository: {config['repo_owner']}/{config['repo_name']}")
        print(f"   Project: #{config['project_number']}")
        
        save_choice = input("\nSauvegarder dans .env? (y/N): ").lower()
        if save_choice == 'y':
            save_to_env(config)
    else:
        print("❌ Configuration échouée")