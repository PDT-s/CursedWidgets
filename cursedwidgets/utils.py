def is_key_printable(key: int) -> bool:
    """
    Return True if the key is a printable character.

    Parameters
    ----------
    key : int
        The key to be checked.

    Returns
    -------
    bool
        True if the key is a printable character.
    """
    return 32 <= key <= 126 or key in (ord(ch) for ch in "ñÑáéíóúÁÉÍÓÚ")
