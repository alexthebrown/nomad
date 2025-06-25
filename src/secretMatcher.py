from rapidfuzz import fuzz, process

TRIGGER_PHRASES = {
    "You know who else is E equals 8?": "audio/cEqualEight.mp3",
}

def secret_match_trigger(recognized_text, threshold=50):
    best_match, score, _ = process.extractOne(
        recognized_text.lower(),
        TRIGGER_PHRASES.keys(),
        scorer=fuzz.ratio
    )
    if score >= threshold:
        return TRIGGER_PHRASES[best_match]
    return None
