#!/usr/bin/env python3
"""
Clean Emojis from Python Files
Replaces emojis with ASCII alternatives to prevent encoding bugs
"""
import re
from pathlib import Path

# Emoji to text replacements
EMOJI_REPLACEMENTS = {
    '[START]': '[START]',
    '[OK]': '[OK]',
    '[ERROR]': '[ERROR]', 
    '[WARN]': '[WARN]',
    '[INFO]': '[INFO]',
    '[NOTE]': '[NOTE]',
    '[TARGET]': '[TARGET]',
    '[TIP]': '[TIP]',
    '[SEARCH]': '[SEARCH]',
    '[DATA]': '[DATA]',
    '[SUCCESS]': '[SUCCESS]',
    '[CRITICAL]': '[CRITICAL]',
    '[STOP]': '[STOP]',
    '[BUG]': '[BUG]',
    '[TEST]': '[TEST]',
    '[REFRESH]': '[REFRESH]',
    '[FEATURE]': '[FEATURE]',
    '[LIST]': '[LIST]',
    '[CONTROL]': '[CONTROL]',
    '[BUILD]': '[BUILD]',
    '[CONFIG]': '[CONFIG]',
    '[ALERT]': '[ALERT]',
    '[SECURE]': '[SECURE]',
    '[PACKAGE]': '[PACKAGE]',
    '[PYTHON]': '[PYTHON]',
}

def clean_emojis_from_text(text):
    """Replace emojis with ASCII alternatives"""
    cleaned_text = text
    
    for emoji, replacement in EMOJI_REPLACEMENTS.items():
        cleaned_text = cleaned_text.replace(emoji, replacement)
    
    # Remove any remaining emojis with generic replacement
    emoji_pattern = re.compile(
        r'[\U0001F600-\U0001F64F]|'
        r'[\U0001F300-\U0001F5FF]|' 
        r'[\U0001F680-\U0001F6FF]|'
        r'[\U0001F1E0-\U0001F1FF]|'
        r'[\U00002702-\U000027B0]|'
        r'[\U000024C2-\U0001F251]'
    )
    
    cleaned_text = emoji_pattern.sub('[EMOJI]', cleaned_text)
    return cleaned_text

def clean_python_files():
    """Clean all Python files from emojis"""
    print("Cleaning emojis from Python files...")
    
    files_cleaned = 0
    
    # Process all Python files
    for py_file in Path(".").glob("**/*.py"):
        # Skip certain directories
        if any(skip in str(py_file) for skip in ['.git', '__pycache__', 'htmlcov']):
            continue
            
        try:
            # Read file
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                original_content = f.read()
            
            # Clean emojis
            cleaned_content = clean_emojis_from_text(original_content)
            
            # Write back if changed
            if cleaned_content != original_content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                files_cleaned += 1
                print(f"  CLEANED: {py_file}")
                
        except Exception as e:
            print(f"  ERROR: Could not clean {py_file}: {e}")
    
    print(f"\nCleaned {files_cleaned} Python files")
    return files_cleaned

def main():
    """Main entry point"""
    print("Emoji Cleaner for Python Files")
    print("=" * 40)
    
    cleaned = clean_python_files()
    
    if cleaned > 0:
        print(f"\nSUCCESS: Cleaned {cleaned} files")
        print("All Python files now safe for Windows encoding")
    else:
        print("\nNO ACTION: No emojis found in Python files")

if __name__ == "__main__":
    main()