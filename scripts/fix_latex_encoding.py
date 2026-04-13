#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to fix LaTeX character encoding in rapport.tex
Converts escaped French characters to proper UTF-8
"""

import os
import sys

# Mapping of LaTeX escaped characters to UTF-8
replacements = [
    # Acute accents
    (r"\'e", "é"),
    (r"\'a", "á"),
    (r"\'i", "í"),
    (r"\'o", "ó"),
    (r"\'u", "ú"),
    
    # Grave accents
    (r"\`e", "è"),
    (r"\`a", "à"),
    (r"\`i", "ì"),
    (r"\`o", "ò"),
    (r"\`u", "ù"),
    
    # Circumflex
    (r"\^a", "â"),
    (r"\^e", "ê"),
    (r"\^i", "î"),
    (r"\^o", "ô"),
    (r"\^u", "û"),
    
    # Diaeresis
    (r'\"e', "ë"),
    (r'\"a', "ä"),
    (r'\"i', "ï"),
    (r'\"o', "ö"),
    (r'\"u', "ü"),
    
    # Cedilla
    (r"\c{c}", "ç"),
    (r"\c{C}", "Ç"),
    
    # Tilde
    (r"\~n", "ñ"),
    (r"\~N", "Ñ"),
    
    # Special cases with braces
    (r"\^{\i}", "î"),
    (r"\^{a}", "â"),
    (r"\^{e}", "ê"),
    (r"\^{o}", "ô"),
    (r"\^{u}", "û"),
    
    # OE ligature
    (r"\oe{}", "œ"),
    (r"\OE{}", "Œ"),
    
    # AE ligature
    (r"\ae{}", "æ"),
    (r"\AE{}", "Æ"),
]

def fix_encoding(file_path):
    """Fix LaTeX encoding in the specified file"""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"[v0] ERROR: File not found: {file_path}")
            sys.exit(1)
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"[v0] Reading file: {file_path}")
        original_length = len(content)
        
        # Apply all replacements
        for latex_char, utf8_char in replacements:
            before_count = content.count(latex_char)
            if before_count > 0:
                content = content.replace(latex_char, utf8_char)
                print(f"[v0] Replaced {before_count} occurrences: {repr(latex_char)} -> {utf8_char}")
        
        # Write the fixed content back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[v0] File saved successfully!")
        print(f"[v0] Original size: {original_length} chars")
        print(f"[v0] New size: {len(content)} chars")
        print("[v0] LaTeX encoding fix COMPLETED!")
        
    except Exception as e:
        print(f"[v0] ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # Find the rapport.tex file
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, "ENSAO_Template/Modèle Rapport/rapport.tex")
    
    # Try alternative paths
    if not os.path.exists(file_path):
        file_path = os.path.join(current_dir, "ENSAO_Template/ModÃ¨le Rapport/rapport.tex")
    
    if not os.path.exists(file_path):
        # Search for it
        for root, dirs, files in os.walk(current_dir):
            if "rapport.tex" in files:
                file_path = os.path.join(root, "rapport.tex")
                break
    
    print(f"[v0] Using file path: {file_path}")
    fix_encoding(file_path)
