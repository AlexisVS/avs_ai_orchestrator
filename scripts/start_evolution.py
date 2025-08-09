#!/usr/bin/env python3
"""
Script de démarrage pour l'auto-évolution autonome
Lance l'orchestrateur en mode auto-évolution permanente
"""

import sys
import asyncio
import signal
import os
from pathlib import Path

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from orchestrator.core import MainOrchestrator


class AutoEvolutionRunner:
    """Runner pour l'auto-évolution en mode daemon"""
    
    def __init__(self):
        self.orchestrator = None
        self.running = True
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """Configurer les handlers pour arrêt propre"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handler pour arrêt propre"""
        print(f"\n[SIGNAL] Signal {signum} reçu - Arrêt en cours...")
        self.running = False
        
        if self.orchestrator and hasattr(self.orchestrator, 'evolution_agent'):
            self.orchestrator.evolution_agent.stop_evolution()
    
    async def start(self):
        """Démarrer l'auto-évolution"""
        print("=" * 80)
        print("AVS AI ORCHESTRATOR - AUTO-EVOLUTION MODE")
        print("=" * 80)
        print("Demarrage de l'auto-evolution autonome...")
        print("Le systeme va s'ameliorer automatiquement")
        print("Boucle d'evolution infinie activee")
        print("=" * 80)
        
        try:
            # Créer l'orchestrateur avec la config d'auto-évolution
            config_file = "auto_evolution_config.yaml"
            
            if not Path(config_file).exists():
                print(f"[ERROR] Configuration manquante: {config_file}")
                return False
            
            self.orchestrator = MainOrchestrator(config_file)
            
            # Démarrer le workflow initial
            print("[INIT] Initialisation de l'orchestrateur...")
            success = await self.orchestrator.run_full_workflow()
            
            if not success:
                print("[ERROR] Échec initialisation")
                return False
            
            # Maintenir le processus en vie pour l'auto-évolution
            print("\n[AUTO-EVOLUTION] Orchestrateur en mode auto-évolution")
            print("[INFO] Appuyez sur Ctrl+C pour arrêter proprement")
            
            # Boucle principale - maintenir en vie
            while self.running:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                # Vérifier que l'auto-évolution tourne toujours
                if hasattr(self.orchestrator.evolution_agent, 'is_evolving'):
                    if not self.orchestrator.evolution_agent.is_evolving:
                        print("[WARNING] Auto-évolution arrêtée, redémarrage...")
                        await self.orchestrator.evolution_agent.start_evolution_loop()
            
            print("\n[SHUTDOWN] Arrêt propre de l'auto-évolution")
            return True
            
        except KeyboardInterrupt:
            print("\n[INTERRUPT] Arrêt demandé par l'utilisateur")
            return True
        except Exception as e:
            print(f"\n[ERROR] Erreur fatale: {e}")
            return False
    
    async def monitor_health(self):
        """Monitorer la santé du système"""
        while self.running:
            try:
                # Vérifier l'état des composants
                if self.orchestrator:
                    # Log des métriques
                    if hasattr(self.orchestrator.evolution_agent, 'evolution_cycle'):
                        cycle = self.orchestrator.evolution_agent.evolution_cycle
                        print(f"[HEALTH] Cycle d'évolution: {cycle}")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"[HEALTH ERROR] Erreur monitoring: {e}")
                await asyncio.sleep(30)


async def main():
    """Point d'entrée principal"""
    
    # Vérifications préalables
    if not Path("src").exists():
        print("[ERROR] Répertoire src/ manquant")
        return False
    
    # Créer les répertoires nécessaires
    for directory in ["logs", "metrics", "sandbox"]:
        Path(directory).mkdir(exist_ok=True)
    
    # Démarrer l'auto-évolution
    runner = AutoEvolutionRunner()
    
    # Lancer le monitoring en parallèle
    monitor_task = asyncio.create_task(runner.monitor_health())
    evolution_task = asyncio.create_task(runner.start())
    
    # Attendre la completion
    await asyncio.gather(evolution_task, monitor_task, return_exceptions=True)


def check_dependencies():
    """Vérifier les dépendances nécessaires"""
    required_modules = [
        'yaml', 'aiohttp', 'pytest', 'asyncio'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"[ERROR] Modules manquants: {', '.join(missing)}")
        print("Installez avec: pip install " + " ".join(missing))
        return False
    
    return True


if __name__ == "__main__":
    print("[INIT] Verification des dependances...")
    
    if not check_dependencies():
        sys.exit(1)
    
    print("[INIT] Dependances OK")
    
    # Démarrer l'auto-évolution
    try:
        asyncio.run(main())
        print("\n[SUCCESS] Auto-evolution terminee")
    except KeyboardInterrupt:
        print("\n[STOP] Arret demande")
    except Exception as e:
        print(f"\n[ERROR] Erreur: {e}")
        sys.exit(1)