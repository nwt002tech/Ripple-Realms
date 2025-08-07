"""
This module defines the sequence of zones a player can progress through
in Ripple Realms.  The order establishes the narrative path and
difficulty curve.  Additional zones can be appended here and the rest
of the game will adapt automatically.
"""

# Ordered list of zones.  The index of each name defines its
# progression; when a player completes the activities in the current
# zone they may unlock the next one.
ZONE_ORDER = [
    "village",
    "forest",
    "temple",
    "tower",
    "ruins",
]


def next_zone(current: str) -> str | None:
    """Return the name of the next zone after ``current`` or ``None``.

    If ``current`` is not found in the list or is the last zone, None is
    returned.
    """
    try:
        idx = ZONE_ORDER.index(current)
    except ValueError:
        return None
    if idx + 1 < len(ZONE_ORDER):
        return ZONE_ORDER[idx + 1]
    return None


def unlock_next_zone_for_realm(realm: dict) -> bool:
    """Attempt to advance the realm's zone to the next one.

    Returns ``True`` if a new zone was unlocked, ``False`` otherwise.
    """
    current = realm.get("realm_state", {}).get("zone")
    new_zone = next_zone(current)
    if new_zone:
        realm["realm_state"]["zone"] = new_zone
        return True
    return False