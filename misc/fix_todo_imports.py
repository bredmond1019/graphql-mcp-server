#!/usr/bin/env python3
"""Fix import paths in all todo tools."""

import os
import re

TODO_TOOLS_DIR = "src/healthie_mcp/tools/todo"

# Define the import replacements
REPLACEMENTS = [
    # Model imports
    (r'from \.\.models\.', 'from ...models.'),
    (r'from \.\.base import', 'from ...base import'),
    (r'from \.\.config\.loader import', 'from ...config.loader import'),
    (r'from \.\.exceptions import', 'from ...exceptions import'),
    (r'from \.\.schema_manager import', 'from ...schema_manager import'),
    # Absolute imports that need to be relative
    (r'from src\.healthie_mcp\.base import', 'from ...base import'),
    (r'from src\.healthie_mcp\.models\.', 'from ...models.'),
    (r'from src\.healthie_mcp\.config\.loader import', 'from ...config.loader import'),
    (r'from src\.healthie_mcp\.exceptions import', 'from ...exceptions import'),
]

def fix_imports_in_file(filepath):
    """Fix imports in a single file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    for old_pattern, new_pattern in REPLACEMENTS:
        content = re.sub(old_pattern, new_pattern, content)
    
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ Fixed imports in {os.path.basename(filepath)}")
    else:
        print(f"⏭️  No changes needed in {os.path.basename(filepath)}")

def main():
    """Fix imports in all todo tools."""
    print("Fixing imports in todo tools...")
    
    for filename in os.listdir(TODO_TOOLS_DIR):
        if filename.endswith('.py') and filename != '__init__.py':
            filepath = os.path.join(TODO_TOOLS_DIR, filename)
            fix_imports_in_file(filepath)
    
    print("\n✅ Import fixes complete!")

if __name__ == "__main__":
    main()