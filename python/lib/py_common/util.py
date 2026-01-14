"""
Utility functions for data manipulation
Compatible with StashApp's py_common.util
"""

def dig(obj, *keys, default=None):
    """
    Safely navigate nested dictionaries/objects.
    
    Example:
        dig({'a': {'b': {'c': 1}}}, 'a', 'b', 'c') returns 1
        dig({'a': {}}, 'a', 'b', 'c', default=0) returns 0
    """
    try:
        result = obj
        for key in keys:
            if isinstance(result, dict):
                result = result[key]
            elif isinstance(result, (list, tuple)):
                result = result[int(key)]
            else:
                result = getattr(result, key)
        return result
    except (KeyError, IndexError, AttributeError, TypeError, ValueError):
        return default


def replace_all(obj, key, replacement_func):
    """
    Recursively find all occurrences of a key in nested dict/list
    and apply replacement_func to their values.
    
    Args:
        obj: The object to traverse (dict, list, or other)
        key: The key to find
        replacement_func: Function to apply to the value
    
    Returns:
        Modified copy of the object
    """
    if isinstance(obj, dict):
        return {
            k: replacement_func(v) if k == key else replace_all(v, key, replacement_func)
            for k, v in obj.items()
        }
    elif isinstance(obj, list):
        return [replace_all(item, key, replacement_func) for item in obj]
    else:
        return obj


def replace_at(obj, *path, replacement):
    """
    Replace a value at a specific path in a nested structure.
    
    Args:
        obj: The object to modify
        *path: The path to the value (e.g., 'studio', 'name')
        replacement: Function or value to replace with
    
    Returns:
        Modified copy of the object
    """
    if not path or obj is None:
        return obj
    
    if len(path) == 1:
        key = path[0]
        if isinstance(obj, dict) and key in obj:
            obj = obj.copy()
            if callable(replacement):
                obj[key] = replacement(obj[key])
            else:
                obj[key] = replacement
        return obj
    
    # Recursive case
    key = path[0]
    if isinstance(obj, dict) and key in obj:
        obj = obj.copy()
        obj[key] = replace_at(obj[key], *path[1:], replacement=replacement)
    
    return obj
