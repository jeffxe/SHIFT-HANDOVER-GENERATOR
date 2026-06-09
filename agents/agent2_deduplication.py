"""
Agent 2: Deduplication Agent
Detects and removes duplicate incidents using keyword
overlap between titles and descriptions.
"""

from difflib import SequenceMatcher


def _similarity(a: str, b: str) -> float:
    """Returns a 0–1 similarity score between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def run(collected_data: dict) -> dict:
    """
    Takes the collected incidents and removes duplicates.
    Two incidents are duplicates if their titles are >70% similar.
    Returns deduplicated incident list plus a log of removed dupes.
    """
    incidents = collected_data["all_incidents"]
    unique = []
    duplicates = []
    THRESHOLD = 0.70

    for incident in incidents:
        is_duplicate = False
        for kept in unique:
            score = _similarity(incident["title"], kept["title"])
            if score >= THRESHOLD:
                # Keep the one that is a ticket (more structured)
                if incident["source"] == "ticket" and kept["source"] == "chat":
                    unique.remove(kept)
                    unique.append(incident)
                    duplicates.append({
                        "removed": kept["title"],
                        "kept":    incident["title"],
                        "score":   round(score, 2),
                    })
                else:
                    duplicates.append({
                        "removed": incident["title"],
                        "kept":    kept["title"],
                        "score":   round(score, 2),
                    })
                is_duplicate = True
                break

        if not is_duplicate:
            unique.append(incident)

    collected_data["unique_incidents"] = unique
    collected_data["duplicates"]        = duplicates
    collected_data["total_unique"]      = len(unique)
    collected_data["total_duplicates"]  = len(duplicates)

    return collected_data
