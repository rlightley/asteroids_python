import json
from pathlib import Path


HIGH_SCORE_LIMIT = 5
HIGH_SCORE_FILE = Path(__file__).with_name("high_scores.json")


def ensure_high_score_file(path=HIGH_SCORE_FILE):
    if path.exists():
        return

    with open(path, "w", encoding="utf-8") as file:
        json.dump([], file, indent=2)


def load_high_scores(path=HIGH_SCORE_FILE):
    ensure_high_score_file(path)
    try:
        with open(path, "r", encoding="utf-8") as file:
            scores = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

    if not isinstance(scores, list):
        return []

    cleaned_scores = []
    for score in scores:
        if not isinstance(score, dict):
            continue
        name = str(score.get("name", "Pilot"))[:12] or "Pilot"
        cleaned_scores.append(
            {
                "name": name,
                "score": int(score.get("score", 0)),
                "wave": int(score.get("wave", 1)),
            }
        )

    cleaned_scores.sort(key=lambda entry: (entry["score"], entry["wave"]), reverse=True)
    return cleaned_scores[:HIGH_SCORE_LIMIT]


def save_high_score(name, score, wave, path=HIGH_SCORE_FILE):
    scores = load_high_scores(path)
    scores.append(
        {
            "name": (name.strip() or "Pilot")[:12],
            "score": int(score),
            "wave": int(wave),
        }
    )
    scores.sort(key=lambda entry: (entry["score"], entry["wave"]), reverse=True)
    scores = scores[:HIGH_SCORE_LIMIT]

    with open(path, "w", encoding="utf-8") as file:
        json.dump(scores, file, indent=2)

    return scores