"""
Quest definitions and quest engine for Ripple Realms.

This module defines the narrative content of each zone and provides a
``run_quest`` function which handles user interaction, choice
selection, optional minigames and the application of ripple effects to
the player's realm.  Quests are specified in the ``QUESTS``
dictionary below.

For each zone the quests are listed in the order they should be
presented.  Each quest dict includes a unique ``id``, a ``title``,
``description``, the filename of an ``image`` to display and a
list of ``choices``.  Choices may include direct ``effects`` (such
as granting a trait or NPC), a ``message`` shown on success, an
optional ``minigame`` definition and optional failure keys.  If a
choice specifies a minigame the player must complete it before
receiving the effects.  The quest requirements feature allows
quests to be gated by player traits.  If a requirement callable
returns ``False`` the quest is skipped.
"""

from __future__ import annotations

import os
import streamlit as st
from typing import Any, Dict, List, Optional

from . import supabase_client
from .zones import ZONE_ORDER, next_zone
from .minigames import unscramble_game, reflex_game, puzzle_game


# Definition of all quests available in the game.  Each zone key maps
# to a list of quest dictionaries.  See the module docstring for the
# structure of each quest definition.
QUESTS: Dict[str, List[Dict[str, Any]]] = {
    "village": [
        {
            "id": "flickering_orb",
            "title": "The Flickering Orb",
            "description": "A glowing orb hovers over your village. It pulses gently, watching you.",
            "image": "orb.png",
            "choices": [
                {
                    "label": "Investigate the orb",
                    "effects": {"npc": {"name": "Watcher Orb", "type": "mystic"}},
                    "message": "The Watcher Orb joins your realm and illuminates dark corners.",
                },
                {
                    "label": "Speak to it",
                    "effects": {"trait": "clever"},
                    "message": "The orb whispers knowledge into your mind. You feel clever.",
                },
                {
                    "label": "Ignore it",
                    "effects": {},
                    "message": "You walk away. Nothing changes, but you might have missed something...",
                },
            ],
            "requirements": [],
        },
        {
            "id": "lost_creature",
            "title": "The Lost Creature",
            "description": "A small lost creature appears at the edge of the village. It looks scared and hungry.",
            "image": "seed_avatar.png",
            "choices": [
                {
                    "label": "Comfort the creature",
                    "effects": {"npc": {"name": "Grateful Creature", "type": "companion"}, "trait": "kind"},
                    "message": "The creature warms to you and pledges loyalty. You become kinder.",
                },
                {
                    "label": "Chase it away",
                    "effects": {"trait": "hothead"},
                    "message": "You scare it off. You feel your temper growing.",
                },
                {
                    "label": "Offer it food",
                    "minigame": {"type": "unscramble", "words": ["herbs", "bread", "grain"]},
                    "effects": {"npc": {"name": "Thankful Creature", "type": "companion"}},
                    "message": "Your generosity pays off; the creature becomes your friend.",
                    "failure_message": "You fumble with your supplies and the creature wanders off disappointed.",
                },
            ],
            "requirements": [],
        },
    ],
    "forest": [
        {
            "id": "whispers_in_trees",
            "title": "Whispers in the Trees",
            "description": "As you wander the forest, the trees whisper secrets in an ancient tongue.",
            "image": "tree_sprite.png",
            "choices": [
                {
                    "label": "Follow the whispers",
                    "effects": {"npc": {"name": "Whisper Sprite", "type": "guide"}, "trait": "curious"},
                    "message": "A sprite appears and promises to guide you. Your curiosity grows.",
                },
                {
                    "label": "Meditate",
                    "effects": {"trait": "mysterious"},
                    "message": "You sit beneath the trees and absorb their wisdom. You become more mysterious.",
                },
                {
                    "label": "Ignore the whispers",
                    "effects": {},
                    "message": "You ignore the voices. The forest remains silent around you.",
                },
            ],
            "requirements": [],
        },
        {
            "id": "hidden_path",
            "title": "The Hidden Path",
            "description": "A narrow path covered in vines leads deeper into the woods. Rumours say it hides great treasure.",
            "image": "forest.png",
            "choices": [
                {
                    "label": "Clear the path",
                    "minigame": {"type": "unscramble", "words": ["vine", "leaf", "root"]},
                    "effects": {"trait": "bold"},
                    "message": "You bravely hack away the vines and feel bolder for your efforts.",
                    "failure_message": "You struggle to clear the vines and decide to turn back, feeling drained.",
                },
                {
                    "label": "Walk away",
                    "effects": {},
                    "message": "You leave the mysterious path untouched for another day.",
                },
            ],
            "requirements": [],
        },
    ],
    "temple": [
        {
            "id": "mirror_trials",
            "title": "Mirror Trials",
            "description": "You stand before a mirror that reflects not your face but your inner self. It asks: Are you content with who you've become?",
            "image": "temple.png",
            "choices": [
                {
                    "label": "Yes",
                    "effects": {"trait": "confident"},
                    "message": "You embrace your journey. Confidence flows through you.",
                },
                {
                    "label": "No",
                    "effects": {"trait": "humble"},
                    "message": "You vow to grow and change. Humility guides you.",
                },
                {
                    "label": "Smash the mirror",
                    "effects": {"trait": "hothead"},
                    "message": "You shatter the mirror. Shards scatter as your temper flares.",
                },
            ],
            "requirements": [],
        },
        {
            "id": "guardians_riddle",
            "title": "Guardian's Riddle",
            "description": "A stone guardian blocks your path and asks: 'I speak without mouth and hear without ears. I have no body, but I come alive with wind. What am I?'",
            "image": "temple.png",
            "choices": [
                {
                    "label": "Answer: Echo",
                    "effects": {"trait": "wise"},
                    "message": "The guardian nods and allows you passage. Wisdom fills you.",
                },
                {
                    "label": "Answer: Sound",
                    "effects": {},
                    "message": "The statue remains silent. Perhaps another answer?",
                },
                {
                    "label": "Answer: Silence",
                    "effects": {},
                    "message": "A whisper passes through the air. The guardian still blocks your way.",
                },
            ],
            "requirements": [],
        },
    ],
    "tower": [
        {
            "id": "arcane_rhythm",
            "title": "Arcane Rhythm",
            "description": "In the tower's heart, glowing runes pulse to a rhythm. You must align with their tempo.",
            "image": "tower.png",
            "choices": [
                {
                    "label": "Start the reflex trial",
                    "minigame": {"type": "reflex"},
                    "effects": {"trait": "agile"},
                    "message": "Your quick reactions impress the tower spirits. You feel more agile.",
                    "failure_message": "Your reactions lag behind the runes. They dim and nothing changes.",
                },
            ],
            "requirements": [],
        },
        {
            "id": "puzzle_of_stairs",
            "title": "Puzzle of Stairs",
            "description": "An inscription on the stairs reads: 'Only those who understand may ascend.'",
            "image": "tower.png",
            "choices": [
                {
                    "label": "Solve the puzzle",
                    "minigame": {"type": "unscramble", "words": ["magic", "wizard", "tower"]},
                    "effects": {"trait": "clever"},
                    "message": "You decipher the inscription and feel cleverer.",
                    "failure_message": "You cannot solve the inscription. The stairs remain locked.",
                },
            ],
            "requirements": [],
        },
    ],
    "ruins": [
        {
            "id": "ancient_guardian",
            "title": "Ancient Guardian",
            "description": "Among the ruins, a slumbering stone guardian awakens and challenges you to prove your worth.",
            "image": "ruins.png",
            "choices": [
                {
                    "label": "Answer its riddle",
                    "minigame": {"type": "unscramble", "words": ["ruins", "ancient", "legend"]},
                    "effects": {"trait": "legendary"},
                    "message": "You solve the ancient riddle. The guardian bows and bestows a legendary aura upon you.",
                    "failure_message": "Your answer crumbles like the ruins around you. The guardian returns to sleep.",
                },
            ],
            "requirements": [],
        },
    ],
}


def _quest_available(quest: Dict[str, Any], traits: Dict[str, Any]) -> bool:
    """Return True if all requirements for this quest are satisfied."""
    for requirement in quest.get("requirements", []):
        try:
            if not requirement(traits):
                return False
        except Exception:
            continue
    return True


def _select_next_quest(zone: str, traits: Dict[str, Any], completed: List[str]) -> Optional[Dict[str, Any]]:
    """Select the next available quest for the given zone."""
    for quest in QUESTS.get(zone, []):
        if quest["id"] in completed:
            continue
        if _quest_available(quest, traits):
            return quest
    return None


def _apply_effects_to_realm(realm: dict, effects: Dict[str, Any]) -> None:
    """Apply a dictionary of effects to the realm in place."""
    traits = realm.get("traits", {})
    state = realm.get("realm_state", {})
    if not traits or not state:
        return
    trait_name = effects.get("trait")
    if trait_name:
        traits[trait_name] = True
    npc = effects.get("npc")
    if npc:
        state.setdefault("npc", []).append(npc)
    # Additional effect types (resources etc.) can be added here later


def run_quest(user_id: str, zone: str, traits: Dict[str, Any]) -> None:
    """Handle quest progression for the player's realm."""
    # Retrieve realm and state
    realm = supabase_client.get_realm_by_user(user_id)
    if not realm:
        st.error("Realm not found. Please create a realm first.")
        return
    state = realm.get("realm_state", {})
    completed = state.get("quests", [])

    # Check for ongoing minigame stored in session state
    if "current_quest" in st.session_state and st.session_state["current_quest"]:
        info = st.session_state["current_quest"]
        minigame = info.get("minigame")
        # Evaluate minigame
        if minigame:
            mg_type = minigame.get("type")
            key_prefix = f"mg_{info['quest_id']}"
            result: Optional[bool] = None
            if mg_type == "unscramble":
                result = unscramble_game(minigame.get("words", []), key_prefix)
            elif mg_type == "reflex":
                result = reflex_game(key_prefix)
            elif mg_type == "puzzle":
                result = puzzle_game(key_prefix)
            else:
                st.error("Unknown minigame type.")
                st.session_state["current_quest"] = None
                return
            if result is not None:
                # Determine which effects to apply based on result
                if result:
                    chosen_effects = info.get("success_effects", {})
                    message = info.get("success_message")
                    # Mark quest complete on success
                    state.setdefault("quests", []).append(info["quest_id"])
                else:
                    chosen_effects = info.get("failure_effects", {})
                    message = info.get("failure_message", "You failed the challenge.")
                # Apply effects
                _apply_effects_to_realm(realm, chosen_effects)
                supabase_client.update_realm(realm)
                st.session_state["current_quest"] = None
                if message:
                    st.success(message) if result else st.error(message)
                # Provide a button to continue to the next quest
                st.button("Continue", key=f"continue_after_{info['quest_id']}")
                return
        return

    # Otherwise select new quest
    next_q = _select_next_quest(zone, traits, completed)
    if not next_q:
        st.info("You have completed all available quests in this zone. Unlock the next zone to continue.")
        return

    # Display quest
    st.subheader(next_q["title"])
    # Attempt to display the associated image from the characters folder
    image_path = os.path.join(os.path.dirname(__file__), "assets", "characters", next_q["image"])
    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    st.write(next_q["description"])

    labels = [ch["label"] for ch in next_q["choices"]]
    choice_label = st.radio("What will you do?", labels, key=f"choice_{next_q['id']}")
    if st.button("Confirm", key=f"confirm_{next_q['id']}"):
        chosen = next((ch for ch in next_q["choices"] if ch["label"] == choice_label), None)
        if not chosen:
            st.error("Invalid choice selected.")
            return
        # If choice has a minigame
        if chosen.get("minigame"):
            st.session_state["current_quest"] = {
                "quest_id": next_q["id"],
                "zone": zone,
                "minigame": chosen["minigame"],
                "success_effects": chosen.get("effects", {}),
                "failure_effects": chosen.get("failure_effects", {}),
                "success_message": chosen.get("message"),
                "failure_message": chosen.get("failure_message", "You failed the challenge."),
            }
            # Rerun to show minigame interface
            st.experimental_rerun()
        else:
            # Apply immediate effects
            _apply_effects_to_realm(realm, chosen.get("effects", {}))
            state.setdefault("quests", []).append(next_q["id"])
            supabase_client.update_realm(realm)
            st.success(chosen.get("message", "Well done."))
            st.button("Continue", key=f"continue_immediate_{next_q['id']}")