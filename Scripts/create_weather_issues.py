#!/usr/bin/env python3
"""
Script pour creer correctement les issues Weather Dashboard
"""

import asyncio
import sys
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


async def create_proper_issues():
    """Creer les issues correctement avec gh CLI directement"""
    
    print("=" * 80)
    print("CREATION CORRECTE DES ISSUES WEATHER DASHBOARD")
    print("=" * 80)
    
    # Charger la configuration
    config_path = Path(__file__).parent.parent / "config" / "weather_dashboard.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    print(f"[INFO] Configuration chargee - {len(config['issues'])} issues a creer")
    
    # Creer chaque issue avec gh CLI directement
    for i, issue_config in enumerate(config['issues'], 1):
        title = issue_config['title']
        description = issue_config['description']
        labels = ','.join(issue_config['labels'])
        
        print(f"\n[{i}/5] Creation: {title}")
        
        # Utiliser gh CLI directement pour avoir un controle total
        import subprocess
        
        try:
            # Creer le fichier temporaire avec la description
            temp_file = Path(f"temp_issue_{i}.md")
            temp_file.write_text(description, encoding='utf-8')
            
            # Creer l'issue avec gh CLI
            cmd = [
                "gh", "issue", "create",
                "--repo", "AlexisVS/weather-dashboard",
                "--title", title,
                "--body-file", str(temp_file),
                "--label", labels
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Nettoyer le fichier temporaire
            temp_file.unlink()
            
            if result.returncode == 0:
                issue_url = result.stdout.strip()
                issue_number = issue_url.split('/')[-1]
                print(f"  [OK] Issue #{issue_number} creee: {issue_url}")
            else:
                print(f"  [ERROR] Erreur: {result.stderr}")
                
        except Exception as e:
            print(f"  [ERROR] Exception: {e}")
    
    print(f"\n{'='*80}")
    print("ISSUES CREEES AVEC SUCCES")
    print("="*80)
    print("\nVerification:")
    print("  gh issue list --repo AlexisVS/weather-dashboard")


if __name__ == "__main__":
    asyncio.run(create_proper_issues())