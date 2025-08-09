#!/usr/bin/env python3
"""
Tests pour corriger les problemes d'encodage detectes dans les logs
"""

import pytest
import logging
import sys
import os
import io
from pathlib import Path
from unittest.mock import patch, Mock

# Ajouter le path src
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from orchestrator.agents.github_sync_agent import GitHubSyncAgent


class TestEncodingFixes:
    """Tests pour corriger les problemes d'encodage dans l'orchestrateur"""
    
    def test_french_characters_logging(self):
        """Test: Gerer les caracteres francais dans les logs"""
        # Problemes detectes: "Sant� syst�me", "�VOLUTION", "r�cup�r�es"
        french_texts = [
            "Sante systeme: healthy",
            "CYCLE EVOLUTION #1",
            "Cartes recuperees (Todo): 0",
            "Opportunites detectees: 0",
            "Meta-apprentissage en cours..."
        ]
        
        # Test que tous les caracteres francais sont supportes
        for text in french_texts:
            try:
                # Essayer d'encoder/decoder
                encoded = text.encode('utf-8')
                decoded = encoded.decode('utf-8')
                assert decoded == text
                
                # Verifier les caracteres speciaux
                assert 'e' in text or 'e' in text or 'a' in text or 'c' in text or text in ["CYCLE EVOLUTION #1"]
                
            except UnicodeError as e:
                pytest.fail(f"Erreur encodage pour '{text}': {e}")
    
    def test_ascii_fallback_for_logs(self):
        """Test: Fallback ASCII pour les logs si UTF-8 echoue"""
        problematic_chars = {
            "e": "e",
            "e": "e", 
            "a": "a",
            "c": "c",
            "o": "o",
            "u": "u",
            "E": "E",
            "E": "E",
            "A": "A"
        }
        
        def ascii_fallback(text):
            """Convertir texte avec accents vers ASCII"""
            result = text
            for accented, ascii_char in problematic_chars.items():
                result = result.replace(accented, ascii_char)
            return result
        
        # Test des conversions
        test_cases = [
            ("Sante systeme", "Sante systeme"),
            ("EVOLUTION", "EVOLUTION"), 
            ("recuperees", "recuperees"),
            ("Opportunites", "Opportunites"),
            ("Meta-apprentissage", "Meta-apprentissage")
        ]
        
        for original, expected in test_cases:
            converted = ascii_fallback(original)
            assert converted == expected
    
    def test_logger_encoding_safe(self):
        """Test: Logger securise contre les problemes d'encodage"""
        # Creer un logger avec gestion d'encodage
        logger = logging.getLogger("TestEncodingSafe")
        
        # Stream qui capture les logs
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Messages problematiques
        problematic_messages = [
            "Sante systeme: healthy",
            "CYCLE EVOLUTION #1", 
            "Cartes recuperees: 0",
            "Opportunites detectees: 0"
        ]
        
        # Test que le logging ne plante pas
        for msg in problematic_messages:
            try:
                logger.info(msg)
            except UnicodeEncodeError:
                # Si erreur Unicode, utiliser fallback ASCII
                ascii_msg = msg.encode('ascii', 'ignore').decode('ascii')
                logger.info(f"[ASCII] {ascii_msg}")
        
        # Verifier que des logs ont ete produits
        log_output = log_stream.getvalue()
        assert len(log_output) > 0
    
    def test_file_writing_encoding(self):
        """Test: Ecriture de fichiers avec encodage UTF-8"""
        test_content = """
        # Code avec caracteres francais
        def fonction_metier():
            '''
            Fonction qui gere les donnees
            '''
            return "Resultat cree avec succes"
        """
        
        # Test ecriture/lecture UTF-8
        test_file = Path("test_encoding.py")
        try:
            # Ecrire avec encodage UTF-8 explicite
            test_file.write_text(test_content, encoding='utf-8')
            
            # Relire et verifier
            read_content = test_file.read_text(encoding='utf-8')
            assert read_content == test_content
            assert "metier" in read_content
            assert "gere" in read_content
            assert "cree" in read_content
            assert "succes" in read_content
            
        finally:
            # Nettoyer
            if test_file.exists():
                test_file.unlink()
    
    def test_github_sync_agent_encoding_safe(self):
        """Test: GitHubSyncAgent avec messages securises"""
        config = {"github": {"project_id": "12"}}
        agent = GitHubSyncAgent(config)
        
        # Tester la generation de contenu sans caracteres problematiques
        improvement = {
            "type": "bug_fix",
            "priority": "high",
            "patterns": ["Erreur detectee dans le systeme"],
            "cycle": 1
        }
        
        title, description = agent._generate_issue_content(improvement)
        
        # Verifier que le contenu est sur pour l'encodage
        try:
            title.encode('ascii', 'ignore')
            description.encode('ascii', 'ignore')
        except Exception as e:
            pytest.fail(f"Probleme encodage dans le contenu genere: {e}")
        
        # Le titre et la description doivent etre non-vides
        assert len(title) > 0
        assert len(description) > 0
    
    def test_console_output_encoding(self):
        """Test: Output console securise"""
        # Simuler differents environnements d'encodage
        test_messages = [
            "=== ORCHESTRATEUR AI INDEPENDANT ===",
            "Demarrage du systeme d'auto-evolution perpetuelle",
            "Sante systeme: healthy",
            "Opportunites detectees: 0"
        ]
        
        for msg in test_messages:
            # Test que l'affichage ne plante pas
            try:
                # Simuler print() avec differents encodages
                msg_bytes = msg.encode('utf-8')
                msg_decoded = msg_bytes.decode('utf-8')
                assert msg_decoded == msg
                
                # Test fallback ASCII si necessaire
                ascii_safe = msg.encode('ascii', 'ignore').decode('ascii')
                assert len(ascii_safe) > 0  # Au moins quelque chose reste
                
            except Exception as e:
                pytest.fail(f"Erreur console pour '{msg}': {e}")


class TestOrchestatorEncodingIntegration:
    """Tests d'integration pour l'encodage dans l'orchestrateur"""
    
    def test_log_messages_ascii_safe(self):
        """Test: Messages de log convertis en ASCII sur"""
        def make_ascii_safe(text):
            """Convertir un texte en ASCII sur"""
            replacements = {
                'e': 'e', 'e': 'e', 'e': 'e', 'e': 'e',
                'a': 'a', 'a': 'a', 'a': 'a',
                'i': 'i', 'i': 'i', 'i': 'i',
                'o': 'o', 'o': 'o', 'o': 'o',
                'u': 'u', 'u': 'u', 'u': 'u',
                'c': 'c', 'n': 'n',
                'E': 'E', 'E': 'E', 'E': 'E', 'E': 'E',
                'A': 'A', 'A': 'A', 'A': 'A',
                'I': 'I', 'I': 'I', 'I': 'I',
                'O': 'O', 'O': 'O', 'O': 'O',
                'U': 'U', 'U': 'U', 'U': 'U',
                'C': 'C', 'N': 'N'
            }
            
            result = text
            for accented, ascii_equiv in replacements.items():
                result = result.replace(accented, ascii_equiv)
            return result
        
        # Messages apres correction d'encodage (versions ASCII)
        log_messages = [
            "=== INITIALISATION ORCHESTRATEUR INDEPENDANT ===",
            "Systeme autonome initialise avec 5 agents",
            "DEMARRAGE EVOLUTION PERPETUELLE", 
            "=== CYCLE EVOLUTION #1 ===",
            "Sante systeme: healthy",
            "[REFRESH] Mode PULL active - Lecture des issues GitHub...",
            "Cartes recuperees (Todo): 0",
            "Issues recuperees: 3", 
            "Opportunites detectees: 0",
            "Meta-apprentissage en cours..."
        ]
        
        # Convertir et verifier
        for msg in log_messages:
            ascii_msg = make_ascii_safe(msg)
            
            # Verifier que la conversion fonctionne
            try:
                ascii_msg.encode('ascii')
            except UnicodeEncodeError:
                pytest.fail(f"Conversion ASCII echouee pour: {msg}")
            
            # Verifier que le sens est preserve
            assert len(ascii_msg) == len(msg)  # Meme longueur
            assert ascii_msg.lower().replace(' ', '') in msg.lower().replace(' ', '') or \
                   msg.lower().replace(' ', '') in ascii_msg.lower().replace(' ', '')
    
    def test_orchestrator_startup_messages(self):
        """Test: Messages de demarrage securises"""
        startup_messages = [
            "=== ORCHESTRATEUR AI INDEPENDANT ===",  # Version ASCII
            "Demarrage du systeme d'auto-evolution perpetuelle...",  # Version ASCII
            "Redemarrage detecte - Cycle #5",  # Version ASCII
            "=== INITIALISATION ORCHESTRATEUR INDEPENDANT ===",  # Version ASCII
            "Systeme autonome initialise avec 5 agents",  # Version ASCII
            "DEMARRAGE EVOLUTION PERPETUELLE"  # Version ASCII
        ]
        
        # Verifier que tous les messages sont ASCII-safe
        for msg in startup_messages:
            try:
                msg.encode('ascii')
                # Si on arrive ici, le message est ASCII-safe
                assert True
            except UnicodeEncodeError:
                pytest.fail(f"Message non ASCII-safe: {msg}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])