def clip(value, min_value, max_value):
    if min_value is None:
        return min(value, max_value)
    if max_value is None:
        return max(value, min_value)
    return min(max(value, min_value), max_value)
