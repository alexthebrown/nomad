from rapidfuzz import fuzz, process

TRIGGER_PHRASES = {
    # "i am captain james kirk": "audio/i_am_captain_james_kirk.wav",
    # "nomad, you are in error": "audio/you_are_in_error.wav",
    # "my function is to probe for biological infestations": "audio/probe_biological.wav"
    "hey there delilah": "audio/htd.mp3"
}

def match_trigger(recognized_text, threshold=50):
    best_match, score, _ = process.extractOne(
        recognized_text.lower(),
        TRIGGER_PHRASES.keys(),
        scorer=fuzz.ratio
    )
    if score >= threshold:
        return TRIGGER_PHRASES[best_match]
    return None
