"""Ripple Realms package initialization.

This file marks the ``ripple_realms_full_game`` directory as a Python
package and exposes some convenient imports at the package level.  The
main entry point for the game is ``app.main`` when running with
Streamlit.
"""

from .app import main  # noqa: F401