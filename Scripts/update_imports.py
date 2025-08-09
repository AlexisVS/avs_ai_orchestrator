#!/usr/bin/env python3
"""
Script to update imports and references after file renaming
"""
import os
import re
from pathlib import Path

def update_imports():
    """Update all import statements and file references"""
    
    # Mapping of old names to new names
    replacements = {
        # Python imports
        'from github_tdd_orchestrator import': 'from orchestrator.github import',
        'import github_tdd_orchestrator': 'import orchestrator.github as github_tdd_orchestrator',
        'from universal_orchestrator import': 'from orchestrator.core import',
        'import universal_orchestrator': 'import orchestrator.core as universal_orchestrator',
        'from main_autonomous_orchestrator import': 'from orchestrator.autonomous import',
        'import main_autonomous_orchestrator': 'import orchestrator.autonomous as main_autonomous_orchestrator',
        
        # Config file references
        'mcp_agent.config.yaml': 'config/mcp_agents.yaml',
        'mcp_agent.secrets.yaml': 'config/secrets.yaml',
        'tdd_config.yaml': 'config/tdd.yaml',
        'auto_evolution_config.yaml': 'config/evolution.yaml',
        'ultimate_autonomous_config.yaml': 'config/autonomous.yaml',
        
        # Script references
        'start-mcp-servers.bat': 'scripts/start_mcp.bat',
        'launch_ultimate_independence.py': 'scripts/launch_autonomous.py',
        'start_auto_evolution.py': 'scripts/start_evolution.py',
        
        # Docker compose
        'docker-compose.mcp.yml': 'docker_compose_mcp.yml',
        
        # Class name updates (maintain backward compatibility)
        'GitHubTDDOrchestrator': 'GitHubTDDOrchestrator',
        'UniversalOrchestrator': 'UniversalOrchestrator',
    }
    
    # Files to update
    files_to_update = []
    
    # Find all Python files
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'htmlcov', 'Lib', 'Scripts'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith(('.py', '.yaml', '.yml', '.md', '.bat', '.sh')):
                files_to_update.append(os.path.join(root, file))
    
    print(f"Updating {len(files_to_update)} files...")
    
    # Update each file
    updated_files = []
    for file_path in files_to_update:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            
            # Apply replacements
            for old, new in replacements.items():
                if old in content:
                    content = content.replace(old, new)
                    print(f"  {file_path}: {old} -> {new}")
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                updated_files.append(file_path)
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    print(f"\nUpdated {len(updated_files)} files:")
    for file_path in updated_files:
        print(f"  - {file_path}")

if __name__ == "__main__":
    update_imports()