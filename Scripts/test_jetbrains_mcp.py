#!/usr/bin/env python3
"""
Test simple de connexion JetBrains MCP
"""
import asyncio
import sys
from pathlib import Path
import aiohttp

async def test_jetbrains_mcp():
    """Test de connexion au serveur JetBrains MCP"""
    print("Test de connexion JetBrains MCP")
    print("=" * 40)
    
    # Vérifier si le conteneur est en cours d'exécution
    try:
        async with aiohttp.ClientSession() as session:
            # Test de connexion de base
            test_url = "http://localhost:8080/health"  
            
            try:
                async with session.get(test_url, timeout=5) as response:
                    print(f"Statut de connexion: {response.status}")
                    if response.status == 200:
                        print("OK: Serveur JetBrains MCP accessible")
                        return True
                    else:
                        print("WARN: Serveur repond mais avec erreur")
                        return False
            except aiohttp.ClientError as e:
                print(f"ERREUR: Impossible de se connecter: {e}")
                return False
                
    except Exception as e:
        print(f"ERREUR critique: {e}")
        return False

async def main():
    """Point d'entrée"""
    connected = await test_jetbrains_mcp()
    
    if connected:
        print("\nLe serveur JetBrains MCP est accessible.")
        print("Vous pouvez maintenant utiliser les outils de refactoring.")
    else:
        print("\nImpossible de se connecter au serveur JetBrains MCP.")
        print("Verifiez que le conteneur Docker est lance:")
        print("  docker ps | grep jetbrains")

if __name__ == "__main__":
    asyncio.run(main())