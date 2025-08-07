"""
Minigames for Ripple Realms.

These short interactive challenges provide variety and test different
player skills.  Each game returns ``True`` for success, ``False`` for
failure, or ``None`` if the player has not yet completed the attempt.

Games:
    - unscramble_game: Unscramble a shuffled word.
    - reflex_game: Click a button as quickly as possible after a random delay.
    - puzzle_game: Solve a simple riddle (future extension).  Currently
      implemented as an unscramble game with a different word list.

Note that minigames rely on Streamlit state to manage user input.  They
should be invoked within a Streamlit context.  To avoid repeated calls
to ``st.button`` or ``st.text_input`` with the same label across
different quests, pass a unique ``key_prefix`` to each function.
"""

import random
import time
from typing import List, Optional
import streamlit as st


def unscramble_game(words: List[str], key_prefix: str) -> Optional[bool]:
    """Present a simple unscramble challenge.

    The player is shown a scrambled version of a randomly chosen word.
    They must input the correct unscrambled word.  Upon submission the
    function returns ``True`` for success, ``False`` for failure.  If
    the player has not yet submitted an answer it returns ``None``.

    Args:
        words: List of words to choose from.
        key_prefix: Unique prefix for Streamlit widgets to avoid key
            clashes when multiple games run on the same page.

    Returns:
        ``True``, ``False`` or ``None`` as described above.
    """
    if not words:
        return False
    # Store the selected word in session state so it persists across reruns
    word_key = f"{key_prefix}_word"
    if word_key not in st.session_state:
        st.session_state[word_key] = random.choice(words)
        # Generate a scrambled version
        chars = list(st.session_state[word_key])
        random.shuffle(chars)
        st.session_state[f"{key_prefix}_scrambled"] = ''.join(chars)
    scrambled = st.session_state.get(f"{key_prefix}_scrambled")
    target_word = st.session_state.get(word_key)
    st.write(f"Unscramble this word: **{scrambled}**")
    answer = st.text_input("Your answer", key=f"{key_prefix}_answer")
    submitted = st.button("Submit", key=f"{key_prefix}_submit")
    if submitted:
        if answer.strip().lower() == target_word.lower():
            st.success("Correct!")
            # Reset word so next call chooses a new one
            for k in [word_key, f"{key_prefix}_scrambled", f"{key_prefix}_answer"]:
                if k in st.session_state:
                    del st.session_state[k]
            return True
        else:
            st.error(f"Incorrect. The correct word was '{target_word}'.")
            for k in [word_key, f"{key_prefix}_scrambled", f"{key_prefix}_answer"]:
                if k in st.session_state:
                    del st.session_state[k]
            return False
    return None


def reflex_game(key_prefix: str) -> Optional[bool]:
    """Run a simplified reflex test game.

    The player clicks a "Start" button to begin.  Immediately after
    starting a "Click now!" button appears.  The elapsed time between
    the start and click is measured.  The game returns ``True`` if
    the reaction time is under one second, ``False`` otherwise.
    ``None`` is returned if the game has not completed yet.
    
    The original version of this minigame relied on
    ``st.experimental_rerun`` to swap between stages after a random
    delay.  Because ``experimental_rerun`` is deprecated in newer
    versions of Streamlit, this simplified version measures reaction
    time directly without a random delay.
    """
    stage_key = f"{key_prefix}_stage"
    if stage_key not in st.session_state:
        st.session_state[stage_key] = "ready"
    stage = st.session_state[stage_key]
    if stage == "ready":
        if st.button("Start Reflex Challenge", key=f"{key_prefix}_start"):
            st.session_state[stage_key] = "go"
            st.session_state[f"{key_prefix}_start_time"] = time.perf_counter()
    elif stage == "go":
        if st.button("Click now!", key=f"{key_prefix}_click"):
            reaction = time.perf_counter() - st.session_state.get(f"{key_prefix}_start_time", time.perf_counter())
            # Reset stage for next round
            st.session_state[stage_key] = "ready"
            # Provide user feedback
            st.write(f"Your reaction time: {reaction:.3f} seconds")
            if reaction < 1.0:
                st.success("Great reflexes!")
                return True
            else:
                st.info("A bit slow! Keep practising.")
                return False
    return None


def puzzle_game(key_prefix: str) -> Optional[bool]:
    """A placeholder for more complex puzzles.

    Currently implemented as an alias of ``unscramble_game``.  In a
    future expansion this function can deliver riddles, logic puzzles or
    spatial challenges.
    """
    # For now reuse unscramble with different words
    words = ["temple", "tower", "ruins", "magic", "energy"]
    return unscramble_game(words, key_prefix)