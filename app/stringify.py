def stringify(value):
    """Converts a Python value to the Lox string representation."""
    if value is None:
        return "nil"
    if isinstance(value, bool):
        return str(value).lower()
    
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
    
    return str(value)