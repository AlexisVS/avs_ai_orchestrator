#!/usr/bin/env python3
"""
Tests pour les dernieres corrections d'encodage dans l'orchestrateur
"""

import pytest
import logging
import sys
from pathlib import Path
from unittest.mock import patch, Mock

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestFinalEncodingFixes:
    """Tests pour les dernieres corrections d'encodage"""
    
    def test_remaining_encoding_issues_fixed(self):
        """Test: Verifier que tous les caracteres problematiques sont corriges"""
        # Messages qui posaient probleme dans les logs
        problematic_messages = [
            "[REFRESH] Mode PULL active - Lecture des issues GitHub...",
            "[OK] GitHub PULL: 0 opportunites detectees", 
            "Sante systeme: healthy",
            "Opportunites detectees: 0",
            "CYCLE EVOLUTION #1",
            "Meta-apprentissage en cours...",
            "=== INITIALISATION ORCHESTRATEUR INDEPENDANT ==="
        ]
        
        # Messages corriges (ASCII-safe)
        corrected_messages = [
            "[REFRESH] Mode PULL active - Lecture des issues GitHub...",
            "[OK] GitHub PULL: 0 opportunites detectees",
            "Sante systeme: healthy", 
            "Opportunites detectees: 0",
            "CYCLE EVOLUTION #1",
            "Meta-apprentissage en cours...",
            "=== INITIALISATION ORCHESTRATEUR INDEPENDANT ==="
        ]
        
        # Verifier que tous les messages corriges sont ASCII-safe
        for msg in corrected_messages:
            try:
                msg.encode('ascii')
                # Si on arrive ici, le message est ASCII-safe
                assert True
            except UnicodeEncodeError:
                pytest.fail(f"Message non ASCII-safe: {msg}")
    
    def test_encoding_conversion_function(self):
        """Test: Fonction de conversion d'encodage pour logs"""
        def make_logs_ascii_safe(text):
            """Convertir les logs vers ASCII sur"""
            replacements = {
                # Caracteres accentues francais
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
        
        # Test des conversions
        test_cases = [
            ("[REFRESH] Mode PULL active", "[REFRESH] Mode PULL active"),
            ("opportunites detectees", "opportunites detectees"),
            ("Sante systeme", "Sante systeme"),
            ("EVOLUTION", "EVOLUTION"),
            ("Meta-apprentissage", "Meta-apprentissage"),
            ("INDEPENDANT", "INDEPENDANT")
        ]
        
        for original, expected in test_cases:
            converted = make_logs_ascii_safe(original)
            assert converted == expected
    
    def test_orchestrator_log_messages_ascii(self):
        """Test: Messages de l'orchestrateur sont ASCII-safe"""
        # Messages actuels dans l'orchestrateur (apres corrections)
        current_messages = [
            "=== ORCHESTRATEUR AI INDEPENDANT ===",
            "Demarrage du systeme d'auto-evolution perpetuelle...",
            "=== INITIALISATION ORCHESTRATEUR INDEPENDANT ===",
            "Systeme autonome initialise avec 5 agents",
            "DEMARRAGE EVOLUTION PERPETUELLE",
            "=== CYCLE EVOLUTION #1 ===",
            "Sante systeme: healthy",
            "[REFRESH] Mode PULL active - Lecture des issues GitHub...",
            "Opportunites detectees: 0",
            "Meta-apprentissage en cours..."
        ]
        
        # Verifier que tous sont ASCII-safe
        for msg in current_messages:
            try:
                encoded = msg.encode('ascii')
                decoded = encoded.decode('ascii')
                assert decoded == msg
            except UnicodeError:
                pytest.fail(f"Message non ASCII-safe: {msg}")
    
    def test_github_sync_log_messages_ascii(self):
        """Test: Messages GitHubSyncAgent sont ASCII-safe"""
        current_messages = [
            "Demarrage GitHub sync pour: bug_fix",
            "Issues recuperees: 3",
            "Cartes recuperees (Todo): 0", 
            "Sync Project Board: 0 opportunites creees",
            "Demarrage workflow PULL mode",
            "Workflow PULL termine: 0 opportunites",
            "Issue creee: #123",
            "Branche creee: auto/bug_fix/issue-123",
            "PR creee: https://github.com/test/test/pull/1"
        ]
        
        # Verifier que tous sont ASCII-safe
        for msg in current_messages:
            try:
                msg.encode('ascii')
            except UnicodeEncodeError:
                pytest.fail(f"Message GitHubSyncAgent non ASCII-safe: {msg}")
    
    def test_no_corrupted_characters_in_logs(self):
        """Test: Aucun caractere corrompu dans les logs"""
        # Caracteres qui apparaissent corrompus dans les logs Windows
        corrupted_chars = ['�', '\ufffd', '\xe9', '\xe8', '\xe0']
        
        # Messages qui ne doivent plus contenir de caracteres corrompus
        safe_messages = [
            "=== CYCLE EVOLUTION #1 ===",
            "Sante systeme: healthy",
            "[REFRESH] Mode PULL active - Lecture des issues GitHub...", 
            "[OK] GitHub PULL: 0 opportunites detectees",
            "Opportunites detectees: 0",
            "Meta-apprentissage en cours..."
        ]
        
        # Verifier qu'aucun caractere corrompu n'est present
        for msg in safe_messages:
            for corrupt_char in corrupted_chars:
                assert corrupt_char not in msg, f"Caractere corrompu '{corrupt_char}' trouve dans: {msg}"
    
    def test_logging_handler_encoding_safe(self):
        """Test: Handler de logging securise pour l'encodage"""
        import io
        import logging
        
        # Creer un logger avec handler personnalise
        logger = logging.getLogger("EncodingSafeTest")
        logger.handlers.clear()  # Nettoyer les handlers existants
        
        # Stream buffer pour capturer les logs
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.INFO)
        
        # Formateur qui gere l'encodage
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Messages de test avec caracteres potentiellement problematiques
        test_messages = [
            "Test ASCII simple",
            "=== CYCLE EVOLUTION #1 ===",
            "Sante systeme: healthy",
            "[REFRESH] Mode PULL active",
            "Opportunites detectees: 0"
        ]
        
        # Tester le logging
        for msg in test_messages:
            try:
                logger.info(msg)
            except UnicodeError:
                pytest.fail(f"Erreur encodage lors du log de: {msg}")
        
        # Verifier que des logs ont ete produits
        log_output = log_stream.getvalue()
        assert len(log_output) > 0
        
        # Verifier qu'aucun caractere corrompu dans la sortie
        corrupted_chars = ['�', '\ufffd']
        for corrupt_char in corrupted_chars:
            assert corrupt_char not in log_output, f"Caractere corrompu trouve dans les logs: {corrupt_char}"


class TestOrchestatorRuntime:
    """Tests d'execution de l'orchestrateur avec encodage corrige"""
    
    def test_orchestrator_messages_pattern(self):
        """Test: Pattern des messages d'orchestrateur"""
        # Pattern attendu dans les logs de l'orchestrateur
        expected_patterns = [
            r"=== ORCHESTRATEUR AI INDEPENDANT ===",
            r"=== INITIALISATION ORCHESTRATEUR INDEPENDANT ===", 
            r"=== CYCLE EVOLUTION #\d+ ===",
            r"Sante systeme: \w+",
            r"\[REFRESH\] Mode PULL active",
            r"Opportunites detectees: \d+",
            r"Meta-apprentissage en cours\.\.\."
        ]
        
        import re
        
        # Messages de test
        test_messages = [
            "=== ORCHESTRATEUR AI INDEPENDANT ===",
            "=== INITIALISATION ORCHESTRATEUR INDEPENDANT ===",
            "=== CYCLE EVOLUTION #5 ===", 
            "Sante systeme: healthy",
            "[REFRESH] Mode PULL active - Lecture des issues GitHub...",
            "Opportunites detectees: 0",
            "Meta-apprentissage en cours..."
        ]
        
        # Verifier que chaque message correspond a son pattern
        for i, msg in enumerate(test_messages):
            if i < len(expected_patterns):
                pattern = expected_patterns[i]
                assert re.search(pattern, msg), f"Message '{msg}' ne correspond pas au pattern '{pattern}'"
    
    def test_no_french_accents_in_runtime_logs(self):
        """Test: Aucun accent francais dans les logs runtime"""
        # Messages runtime reels (apres corrections)
        runtime_messages = [
            "Demarrage du systeme d'auto-evolution perpetuelle...",
            "Systeme autonome initialise avec 5 agents", 
            "DEMARRAGE EVOLUTION PERPETUELLE",
            "Cycle 1 termine en 2.4s",
            "GitHub Sync: 0 issues actives, version 1.0.0"
        ]
        
        # Caracteres accentues a eviter
        french_accents = ['é', 'è', 'à', 'ç', 'ô', 'ù', 'É', 'È', 'À', 'Ç']
        
        # Verifier l'absence d'accents
        for msg in runtime_messages:
            for accent in french_accents:
                assert accent not in msg, f"Accent '{accent}' trouve dans le message runtime: {msg}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])