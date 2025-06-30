"""Text manipulation utility functions."""

import re
from typing import Optional


def pluralize(word: str, count: int) -> str:
    """Simple pluralization function.
    
    Args:
        word: The word to pluralize
        count: The count to determine if pluralization is needed
        
    Returns:
        The word in singular or plural form
    """
    if count == 1:
        return word
    
    # Simple rules for common cases
    if word.endswith('y') and not word.endswith('ay'):
        return word[:-1] + 'ies'
    elif word.endswith(('s', 'ss', 'sh', 'ch', 'x', 'z')):
        return word + 'es'
    else:
        return word + 's'


def camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case.
    
    Args:
        name: String in camelCase
        
    Returns:
        String in snake_case
    """
    # Insert underscore before capital letters
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    # Insert underscore before capital letter followed by lowercase
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()


def snake_to_camel(name: str, capitalize_first: bool = False) -> str:
    """Convert snake_case to camelCase.
    
    Args:
        name: String in snake_case
        capitalize_first: Whether to capitalize the first letter (PascalCase)
        
    Returns:
        String in camelCase or PascalCase
    """
    components = name.split('_')
    if not components:
        return name
    
    if capitalize_first:
        return ''.join(word.title() for word in components)
    else:
        return components[0] + ''.join(word.title() for word in components[1:])


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to a maximum length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    if max_length <= len(suffix):
        return suffix[:max_length]
    
    return text[:max_length - len(suffix)] + suffix


def indent_text(text: str, spaces: int = 2, skip_first: bool = False) -> str:
    """Indent text with specified number of spaces.
    
    Args:
        text: Text to indent
        spaces: Number of spaces to indent
        skip_first: Whether to skip indenting the first line
        
    Returns:
        Indented text
    """
    indent = ' ' * spaces
    lines = text.split('\n')
    
    if skip_first and lines:
        indented_lines = [lines[0]] + [indent + line for line in lines[1:]]
    else:
        indented_lines = [indent + line for line in lines]
    
    return '\n'.join(indented_lines)


def wrap_text(text: str, width: int = 80, indent: int = 0) -> str:
    """Wrap text to specified width.
    
    Args:
        text: Text to wrap
        width: Maximum line width
        indent: Number of spaces to indent each line
        
    Returns:
        Wrapped text
    """
    if not text:
        return text
    
    words = text.split()
    lines = []
    current_line = []
    current_length = indent
    
    for word in words:
        word_length = len(word)
        
        # Check if adding this word would exceed the width
        if current_length + word_length + 1 > width and current_line:
            lines.append(' ' * indent + ' '.join(current_line))
            current_line = [word]
            current_length = indent + word_length
        else:
            current_line.append(word)
            current_length += word_length + (1 if current_line else 0)
    
    # Add the last line
    if current_line:
        lines.append(' ' * indent + ' '.join(current_line))
    
    return '\n'.join(lines)


def remove_empty_lines(text: str) -> str:
    """Remove empty lines from text.
    
    Args:
        text: Text to process
        
    Returns:
        Text with empty lines removed
    """
    lines = text.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text.
    
    Args:
        text: Text to normalize
        
    Returns:
        Text with normalized whitespace
    """
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    return text.strip()