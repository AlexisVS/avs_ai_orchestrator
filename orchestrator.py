#!/usr/bin/env python3
"""
AVS AI Orchestrator - Point d'entrée principal
Système d'orchestration AI avec auto-évolution autonome
"""

import sys
import asyncio
from pathlib import Path

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from orchestrator.core import MainOrchestrator
from dotenv import load_dotenv


async def main():
    """Point d'entrée principal de l'orchestrateur"""
    
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <config.yaml>")
        print("\nExemples:")
        print("  python orchestrator.py configs/weather-app.yaml")
        print("  python orchestrator.py mcp_agent.config.yaml")
        return
    
    config_file = sys.argv[1]
    
    if not Path(config_file).exists():
        print(f"Erreur: Fichier de configuration '{config_file}' introuvable")
        return
    
    # Charger variables d'environnement
    load_dotenv()
    
    print("=" * 80)
    print("AVS AI ORCHESTRATOR - Système d'Auto-Évolution")
    print("=" * 80)
    print(f"Configuration: {config_file}")
    print("-" * 80)
    
    try:
        # Créer et lancer orchestrateur principal
        orchestrator = MainOrchestrator(config_file)
        success = await orchestrator.run_full_workflow()
        
        if success:
            print("\n[SUCCESS] Orchestration terminée avec succès!")
            sys.exit(0)
        else:
            print("\n[FAILED] Orchestration échouée")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n[INFO] Orchestration interrompue par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        print(f"\n[ERROR] Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())