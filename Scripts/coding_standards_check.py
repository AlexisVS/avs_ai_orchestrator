#!/usr/bin/env python3
"""
Coding Standards Checker - Verify no emojis in Python files
Prevents encoding bugs on Windows systems
"""
import re
from pathlib import Path
import sys

def has_emoji(text):
    """Check if text contains emoji characters"""
    # Unicode ranges for emojis
    emoji_pattern = re.compile(
        r'[\U0001F600-\U0001F64F]|'  # emoticons
        r'[\U0001F300-\U0001F5FF]|'  # symbols & pictographs
        r'[\U0001F680-\U0001F6FF]|'  # transport & map symbols
        r'[\U0001F1E0-\U0001F1FF]|'  # flags (iOS)
        r'[\U00002702-\U000027B0]|'  # dingbats
        r'[\U000024C2-\U0001F251]'   # enclosed characters
    )
    return bool(emoji_pattern.search(text))

def check_python_files():
    """Check all Python files for emoji usage"""
    print("Coding Standards Check - No Emojis in Python")
    print("=" * 50)
    
    violations = []
    
    # Find all Python files
    for py_file in Path(".").glob("**/*.py"):
        # Skip certain directories
        if any(skip in str(py_file) for skip in ['.git', '__pycache__', 'htmlcov']):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                if has_emoji(line):
                    violations.append({
                        'file': str(py_file),
                        'line': line_num,
                        'content': line.strip()
                    })
        except Exception as e:
            print(f"WARN: Could not check {py_file}: {e}")
    
    # Report results
    if violations:
        print(f"\nERROR: Found {len(violations)} emoji violations:")
        for violation in violations:
            print(f"  {violation['file']}:{violation['line']}")
            print(f"    {violation['content']}")
        return False
    else:
        print("OK: No emojis found in Python files")
        return True

def suggest_alternatives():
    """Show alternatives for common emojis"""
    alternatives = {
        'OK': ['OK', '[OK]', 'SUCCESS'],
        'ERROR': ['ERROR', '[ERROR]', 'FAILED'],
        'WARN': ['WARN', '[WARN]', 'WARNING'],
        'INFO': ['INFO', '[INFO]', 'NOTE'],
        'START': ['START', '[START]', 'INIT'],
        'DONE': ['DONE', '[DONE]', 'COMPLETE']
    }
    
    print("\nRecommended text alternatives:")
    for emoji_type, alts in alternatives.items():
        print(f"  {emoji_type}: {', '.join(alts)}")

def main():
    """Main entry point"""
    clean = check_python_files()
    
    if not clean:
        suggest_alternatives()
        print("\nFix these violations to prevent encoding issues on Windows")
        sys.exit(1)
    else:
        print("All Python files follow encoding standards")
        sys.exit(0)

if __name__ == "__main__":
    main()