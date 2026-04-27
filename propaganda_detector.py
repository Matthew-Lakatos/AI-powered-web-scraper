"""
propaganda_detector.py
======================
Enhanced lexicon-based propaganda technique detector.

Detects ten well-documented propaganda techniques and returns a
composite score (0.0 = clean, 1.0 = heavy propaganda) alongside:
  - detected technique names with individual intensity scores
  - the specific flagged words / phrases that triggered each technique
  - sentence-level evidence (which sentences triggered which technique)
  - a human-readable confidence label

Techniques detected
-------------------
 1. Loaded Language          – emotionally charged / dehumanising words
 2. Fear Mongering           – language designed to induce fear or panic
 3. Black-and-White Thinking – absolutist, either/or framing
 4. Glittering Generalities  – vague, feel-good buzzwords without substance
 5. Name Calling             – derogatory labels aimed at individuals/groups
 6. Bandwagon                – "everyone agrees / nobody believes" framing
 7. Repetition / Hammering   – unnaturally high frequency of a single term
 8. Appeal to Authority      – citing unnamed/vague experts to shut down debate
 9. False Equivalence        – comparing unequal things as if they are the same
10. Card Stacking            – one-sided selective use of evidence
"""

import re
from collections import Counter
from typing import Any, Dict, List, Tuple


# -----------------------------------------------------------------------
# LEXICONS
# -----------------------------------------------------------------------

_LOADED_LANGUAGE: frozenset = frozenset({
    "radical", "extremist", "regime", "puppet", "cronies",
    "brainwash", "indoctrinate", "traitor", "corrupt", "fake",
    "lies", "hoax", "scam", "shill", "enemy", "invasion",
    "destroy", "obliterate", "criminal", "disgrace",
    "illegitimate", "sellout", "rigged", "subversive", "menace",
    "parasite", "vermin", "filth", "degeneracy",
    "woke", "elites", "agenda", "pawn", "lapdog", "stooge",
    "hack", "mouthpiece",
})

_FEAR_WORDS: frozenset = frozenset({
    "catastrophe", "collapse", "chaos", "apocalypse", "existential",
    "doom", "panic", "terror", "attack", "crisis", "war",
    "dying", "destroyed", "extinction", "survival", "threat",
    "emergency", "alarm", "dire", "peril", "devastation",
    "imminent", "irreversible", "unstoppable", "catastrophic",
    "disastrous", "fatal", "deadly", "lethal", "annihilate",
    "wipeout", "armageddon", "doomsday", "meltdown", "implosion",
})

_ABSOLUTIST_WORDS: frozenset = frozenset({
    "always", "never", "all", "none", "every", "nobody",
    "everyone", "totally", "completely", "absolutely", "undeniably",
    "obviously", "clearly", "undoubtedly", "unquestionably",
    "impossible", "inevitable", "certainty", "solely", "only",
    "nothing", "anywhere", "everywhere", "nowhere", "forever",
    "permanently", "guaranteed", "definitive", "conclusive",
})

_GLITTERING_GENERALITIES: frozenset = frozenset({
    "freedom", "democracy", "patriot", "values", "tradition",
    "heritage", "natural", "common", "rights", "liberty",
    "justice", "unity", "strength", "pride", "honour",
    "decency", "integrity", "progress", "prosperity",
    "sovereignty", "greatness", "excellence", "virtue",
    "morality", "dignity", "civilisation", "security", "peace",
    "truth", "transparency", "accountability", "fairness",
})

_NAME_CALLING: frozenset = frozenset({
    "idiot", "moron", "stupid", "ignorant", "fool", "clown",
    "liar", "hypocrite", "thug", "terrorist", "communist",
    "fascist", "nazi", "globalist", "elitist",
    "snowflake", "sheeple", "sheep", "puppet",
    "loser", "failure", "buffoon", "coward", "traitor",
    "criminal", "crook", "thief", "fraudster",
    "degenerate", "psychopath", "maniac", "extremist",
})

_BANDWAGON_PHRASES: frozenset = frozenset({
    "everyone knows",
    "all experts",
    "scientists agree",
    "nobody believes",
    "the public thinks",
    "people are saying",
    "everyone can see",
    "any reasonable person",
    "polls show everyone",
    "the whole world agrees",
    "nobody disputes",
    "most people agree",
    "the majority agrees",
    "nobody can deny",
    "the consensus is clear",
    "everybody understands",
    "no one questions",
})

_APPEAL_TO_AUTHORITY_PHRASES: frozenset = frozenset({
    "experts say",
    "scientists say",
    "studies show",
    "research proves",
    "authorities confirm",
    "insiders report",
    "sources say",
    "officials claim",
    "it has been proven",
    "it is well known",
    "it is widely accepted",
    "leading experts agree",
    "top researchers found",
    "unnamed sources",
    "anonymous officials",
    "some experts believe",
    "certain authorities",
})

_FALSE_EQUIVALENCE_PHRASES: frozenset = frozenset({
    "both sides",
    "just as bad",
    "equally guilty",
    "no different from",
    "same as",
    "just like",
    "no better than",
    "they all do it",
    "everyone does it",
    "no worse than",
    "comparable to",
    "equivalent to",
    "identical to",
})

_CARD_STACKING_PHRASES: frozenset = frozenset({
    "only the facts show",
    "the evidence clearly",
    "conveniently ignores",
    "fails to mention",
    "never mentions",
    "omits the fact",
    "overlooks the truth",
    "the real story is",
    "what they don't tell you",
    "the media won't report",
    "hidden truth",
    "suppressed information",
    "censored facts",
    "the untold story",
    "they don't want you to know",
})

# -----------------------------------------------------------------------
# WEIGHTS
# -----------------------------------------------------------------------

_WEIGHTS: Dict[str, float] = {
    "Loaded Language":          0.20,
    "Fear Mongering":           0.18,
    "Black-and-White Thinking": 0.13,
    "Glittering Generalities":  0.08,
    "Name Calling":             0.18,
    "Bandwagon":                0.08,
    "Repetition / Hammering":   0.03,
    "Appeal to Authority":      0.05,
    "False Equivalence":        0.05,
    "Card Stacking":            0.02,
}


# -----------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------

_STOP_WORDS: frozenset = frozenset({
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
    "for", "of", "with", "by", "from", "is", "was", "are", "were",
    "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might", "shall",
    "not", "no", "nor", "so", "yet", "both", "either", "neither",
    "it", "its", "this", "that", "these", "those", "he", "she",
    "they", "we", "you", "i", "his", "her", "their", "our", "your",
    "my", "me", "him", "them", "us", "who", "which", "what",
    "said", "says", "also", "just", "more", "than", "as", "if",
})


def _tokenize(text: str) -> List[str]:
    """Return a lowercased list of word tokens."""
    return re.findall(r"\b\w+\b", text.lower())


def _split_sentences(text: str) -> List[str]:
    """Split text into sentences using a simple heuristic."""
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def _match_tokens(tokens: List[str], lexicon: frozenset) -> List[str]:
    """Return tokens that appear in the given lexicon."""
    return [t for t in tokens if t in lexicon]


def _match_phrases(text_lower: str, phrases: frozenset) -> List[str]:
    """Return phrases from the set that appear verbatim in text_lower."""
    return [p for p in phrases if p in text_lower]


def _sentence_evidence(
    sentences: List[str],
    lexicon: frozenset = None,
    phrases: frozenset = None,
    max_sentences: int = 3,
) -> List[str]:
    """Return up to *max_sentences* that contain a hit from lexicon or phrases."""
    evidence: List[str] = []
    for sent in sentences:
        sent_lower = sent.lower()
        tokens = re.findall(r"\b\w+\b", sent_lower)
        hit = (
            (lexicon and any(t in lexicon for t in tokens)) or
            (phrases and any(p in sent_lower for p in phrases))
        )
        if hit:
            evidence.append(sent)
        if len(evidence) >= max_sentences:
            break
    return evidence


def _repetition_score(tokens: List[str], threshold: float = 0.05) -> Tuple[float, str]:
    """
    Return a (score, most-common-token) pair.  Score > 0.6 indicates
    unnatural repetition of a single content word.
    """
    if not tokens:
        return 0.0, ""
    filtered = [t for t in tokens if t not in _STOP_WORDS and len(t) > 2]
    if not filtered:
        return 0.0, ""
    counts = Counter(filtered)
    most_common_token, most_common_freq = counts.most_common(1)[0]
    ratio = most_common_freq / len(filtered)
    return min(ratio / threshold, 1.0), most_common_token


def _deduplicate(items: List[str]) -> List[str]:
    seen: set = set()
    out: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _confidence_label(score: float) -> str:
    if score < 0.10:
        return "clean"
    if score < 0.25:
        return "low"
    if score < 0.45:
        return "moderate"
    if score < 0.65:
        return "high"
    return "very high"


# -----------------------------------------------------------------------
# PUBLIC API
# -----------------------------------------------------------------------

def detect_propaganda(text: str) -> Dict[str, Any]:
    """
    Analyse *text* for propaganda techniques.

    Parameters
    ----------
    text : str
        Raw article / page text to analyse.

    Returns
    -------
    dict
        ``score``       – float in [0.0, 1.0]
        ``confidence``  – 'clean' | 'low' | 'moderate' | 'high' | 'very high'
        ``techniques``  – list of {name, intensity, evidence} dicts
        ``flags``       – deduplicated flat list of flagged words/phrases
    """
    if not text or not text.strip():
        return {"score": 0.0, "confidence": "clean", "techniques": [], "flags": []}

    tokens: List[str]    = _tokenize(text)
    text_lower: str      = text.lower()
    sentences: List[str] = _split_sentences(text)
    technique_results: List[Dict[str, Any]] = []
    all_flags: List[str] = []

    # 1. Loaded Language
    ll_hits = _match_tokens(tokens, _LOADED_LANGUAGE)
    if ll_hits:
        unique_hits = list(dict.fromkeys(ll_hits))[:8]
        technique_results.append({
            "name":      "Loaded Language",
            "intensity": round(min(len(set(ll_hits)) / 5, 1.0), 3),
            "evidence":  _sentence_evidence(sentences, lexicon=_LOADED_LANGUAGE),
        })
        all_flags.extend(unique_hits)

    # 2. Fear Mongering (require >= 2 distinct hits)
    fear_hits = _match_tokens(tokens, _FEAR_WORDS)
    if len(set(fear_hits)) >= 2:
        unique_hits = list(dict.fromkeys(fear_hits))[:8]
        technique_results.append({
            "name":      "Fear Mongering",
            "intensity": round(min(len(set(fear_hits)) / 4, 1.0), 3),
            "evidence":  _sentence_evidence(sentences, lexicon=_FEAR_WORDS),
        })
        all_flags.extend(unique_hits)

    # 3. Black-and-White Thinking (require >= 2 distinct hits)
    abs_hits = _match_tokens(tokens, _ABSOLUTIST_WORDS)
    if len(set(abs_hits)) >= 2:
        unique_hits = list(dict.fromkeys(abs_hits))[:6]
        technique_results.append({
            "name":      "Black-and-White Thinking",
            "intensity": round(min(len(set(abs_hits)) / 5, 1.0), 3),
            "evidence":  _sentence_evidence(sentences, lexicon=_ABSOLUTIST_WORDS),
        })
        all_flags.extend(unique_hits)

    # 4. Glittering Generalities (require >= 3 distinct hits)
    gg_hits = _match_tokens(tokens, _GLITTERING_GENERALITIES)
    if len(set(gg_hits)) >= 3:
        unique_hits = list(dict.fromkeys(gg_hits))[:8]
        technique_results.append({
            "name":      "Glittering Generalities",
            "intensity": round(min(len(set(gg_hits)) / 6, 1.0), 3),
            "evidence":  _sentence_evidence(sentences, lexicon=_GLITTERING_GENERALITIES),
        })
        all_flags.extend(unique_hits)

    # 5. Name Calling
    nc_hits = _match_tokens(tokens, _NAME_CALLING)
    if nc_hits:
        unique_hits = list(dict.fromkeys(nc_hits))[:8]
        technique_results.append({
            "name":      "Name Calling",
            "intensity": round(min(len(set(nc_hits)) / 3, 1.0), 3),
            "evidence":  _sentence_evidence(sentences, lexicon=_NAME_CALLING),
        })
        all_flags.extend(unique_hits)

    # 6. Bandwagon
    bw_hits = _match_phrases(text_lower, _BANDWAGON_PHRASES)
    if bw_hits:
        technique_results.append({
            "name":      "Bandwagon",
            "intensity": round(min(len(bw_hits) / 3, 1.0), 3),
            "evidence":  _sentence_evidence(sentences, phrases=_BANDWAGON_PHRASES),
        })
        all_flags.extend(bw_hits[:4])

    # 7. Repetition / Hammering (skip very short texts — false positives)
    rep_score, rep_token = _repetition_score(tokens)
    if rep_score > 0.6 and len(tokens) >= 80:
        technique_results.append({
            "name":      "Repetition / Hammering",
            "intensity": round(rep_score, 3),
            "evidence":  _sentence_evidence(
                sentences, lexicon=frozenset({rep_token}) if rep_token else None
            ),
        })
        if rep_token:
            all_flags.append(f"[repeated] {rep_token}")

    # 8. Appeal to Authority (require >= 2 phrase hits)
    auth_hits = _match_phrases(text_lower, _APPEAL_TO_AUTHORITY_PHRASES)
    if len(auth_hits) >= 2:
        technique_results.append({
            "name":      "Appeal to Authority",
            "intensity": round(min(len(auth_hits) / 4, 1.0), 3),
            "evidence":  _sentence_evidence(sentences, phrases=_APPEAL_TO_AUTHORITY_PHRASES),
        })
        all_flags.extend(auth_hits[:4])

    # 9. False Equivalence
    fe_hits = _match_phrases(text_lower, _FALSE_EQUIVALENCE_PHRASES)
    if fe_hits:
        technique_results.append({
            "name":      "False Equivalence",
            "intensity": round(min(len(fe_hits) / 3, 1.0), 3),
            "evidence":  _sentence_evidence(sentences, phrases=_FALSE_EQUIVALENCE_PHRASES),
        })
        all_flags.extend(fe_hits[:4])

    # 10. Card Stacking
    cs_hits = _match_phrases(text_lower, _CARD_STACKING_PHRASES)
    if cs_hits:
        technique_results.append({
            "name":      "Card Stacking",
            "intensity": round(min(len(cs_hits) / 2, 1.0), 3),
            "evidence":  _sentence_evidence(sentences, phrases=_CARD_STACKING_PHRASES),
        })
        all_flags.extend(cs_hits[:4])

    # Weighted composite score (intensity-adjusted)
    raw_score = sum(
        _WEIGHTS.get(t["name"], 0.05) * (0.5 + 0.5 * t["intensity"])
        for t in technique_results
    )
    score = round(min(raw_score, 1.0), 3)

    return {
        "score":      score,
        "confidence": _confidence_label(score),
        "techniques": technique_results,
        "flags":      _deduplicate(all_flags),
    }
