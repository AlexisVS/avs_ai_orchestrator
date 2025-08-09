#!/usr/bin/env python3
"""
Script de demarrage pour l'auto-evolution autonome
Lance l'orchestrateur en mode auto-evolution permanente
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
    """Runner pour l'auto-evolution en mode daemon"""
    
    def __init__(self):
        self.orchestrator = None
        self.running = True
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """Configurer les handlers pour arret propre"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handler pour arret propre"""
        print(f"\n[SIGNAL] Signal {signum} recu - Arret en cours...")
        self.running = False
        
        if self.orchestrator and hasattr(self.orchestrator, 'evolution_agent'):
            self.orchestrator.evolution_agent.stop_evolution()
    
    async def start(self):
        """Demarrer l'auto-evolution"""
        print("=" * 80)
        print("AVS AI ORCHESTRATOR - AUTO-EVOLUTION MODE")
        print("=" * 80)
        print("Demarrage de l'auto-evolution autonome...")
        print("Le systeme va s'ameliorer automatiquement")
        print("Boucle d'evolution infinie activee")
        print("=" * 80)
        
        try:
            # Creer l'orchestrateur avec la config d'auto-evolution
            config_file = "auto_evolution_config.yaml"
            
            if not Path(config_file).exists():
                print(f"[ERROR] Configuration manquante: {config_file}")
                return False
            
            self.orchestrator = MainOrchestrator(config_file)
            
            # Demarrer le workflow initial
            print("[INIT] Initialisation de l'orchestrateur...")
            success = await self.orchestrator.run_full_workflow()
            
            if not success:
                print("[ERROR] Echec initialisation")
                return False
            
            # Maintenir le processus en vie pour l'auto-evolution
            print("\n[AUTO-EVOLUTION] Orchestrateur en mode auto-evolution")
            print("[INFO] Appuyez sur Ctrl+C pour arreter proprement")
            
            # Boucle principale - maintenir en vie
            while self.running:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                # Verifier que l'auto-evolution tourne toujours
                if hasattr(self.orchestrator.evolution_agent, 'is_evolving'):
                    if not self.orchestrator.evolution_agent.is_evolving:
                        print("[WARNING] Auto-evolution arretee, redemarrage...")
                        await self.orchestrator.evolution_agent.start_evolution_loop()
            
            print("\n[SHUTDOWN] Arret propre de l'auto-evolution")
            return True
            
        except KeyboardInterrupt:
            print("\n[INTERRUPT] Arret demande par l'utilisateur")
            return True
        except Exception as e:
            print(f"\n[ERROR] Erreur fatale: {e}")
            return False
    
    async def monitor_health(self):
        """Monitorer la sante du systeme"""
        while self.running:
            try:
                # Verifier l'etat des composants
                if self.orchestrator:
                    # Log des metriques
                    if hasattr(self.orchestrator.evolution_agent, 'evolution_cycle'):
                        cycle = self.orchestrator.evolution_agent.evolution_cycle
                        print(f"[HEALTH] Cycle d'evolution: {cycle}")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"[HEALTH ERROR] Erreur monitoring: {e}")
                await asyncio.sleep(30)


async def main():
    """Point d'entree principal"""
    
    # Verifications prealables
    if not Path("src").exists():
        print("[ERROR] Repertoire src/ manquant")
        return False
    
    # Creer les repertoires necessaires
    for directory in ["logs", "metrics", "sandbox"]:
        Path(directory).mkdir(exist_ok=True)
    
    # Demarrer l'auto-evolution
    runner = AutoEvolutionRunner()
    
    # Lancer le monitoring en parallele
    monitor_task = asyncio.create_task(runner.monitor_health())
    evolution_task = asyncio.create_task(runner.start())
    
    # Attendre la completion
    await asyncio.gather(evolution_task, monitor_task, return_exceptions=True)


def check_dependencies():
    """Verifier les dependances necessaires"""
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
    
    # Demarrer l'auto-evolution
    try:
        asyncio.run(main())
        print("\n[SUCCESS] Auto-evolution terminee")
    except KeyboardInterrupt:
        print("\n[STOP] Arret demande")
    except Exception as e:
        print(f"\n[ERROR] Erreur: {e}")
        sys.exit(1)