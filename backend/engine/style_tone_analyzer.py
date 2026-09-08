"""
Style and Tone Analyzer Module
Detects wordiness, redundancies, passive voice, informal colloquialisms,
evaluates document tone (Formal, Casual, Professional, Academic),
and provides smart professional rewrites (e.g. "Hey, what's up with the report?").
"""

import re
from typing import Dict, List, Any
from .preprocessor import ProcessedDocument, Token


CONCISENESS_RULES = [
    (r"\bdue\s+to\s+the\s+fact\s+that\b", "because", 'Replace wordy "due to the fact that" with "because".', "STYLE_DUE_TO_THE_FACT_THAT"),
    (r"\bin\s+order\s+to\b", "to", 'Simplify "in order to" to "to".', "STYLE_IN_ORDER_TO"),
    (r"\bat\s+this\s+point\s+in\s+time\b", "currently", 'Replace "at this point in time" with "currently" or "now".', "STYLE_AT_THIS_POINT_IN_TIME"),
    (r"\bat\s+the\s+present\s+time\b", "presently", 'Simplify "at the present time" to "presently" or "now".', "STYLE_AT_THE_PRESENT_TIME"),
    (r"\bin\s+the\s+event\s+that\b", "if", 'Simplify "in the event that" to "if".', "STYLE_IN_THE_EVENT_THAT"),
    (r"\bfor\s+the\s+purpose\s+of\b", "to", 'Simplify "for the purpose of" to "to" or "for".', "STYLE_FOR_THE_PURPOSE_OF"),
    (r"\bwith\s+regard\s+to\b", "regarding", 'Replace "with regard to" with "regarding" or "about".', "STYLE_WITH_REGARD_TO"),
    (r"\bwith\s+reference\s+to\b", "regarding", 'Replace "with reference to" with "regarding".', "STYLE_WITH_REFERENCE_TO"),
    (r"\bdespite\s+the\s+fact\s+that\b", "although", 'Simplify "despite the fact that" to "although".', "STYLE_DESPITE_THE_FACT_THAT"),
    (r"\bin\s+spite\s+of\s+the\s+fact\s+that\b", "although", 'Simplify "in spite of the fact that" to "although".', "STYLE_IN_SPITE_OF_THE_FACT_THAT"),
    (r"\buntil\s+such\s+time\s+as\b", "until", 'Simplify "until such time as" to "until".', "STYLE_UNTIL_SUCH_TIME_AS"),
    (r"\bin\s+close\s+proximity\s+to\b", "near", 'Simplify "in close proximity to" to "near".', "STYLE_IN_CLOSE_PROXIMITY"),
    (r"\bhas\s+the\s+ability\s+to\b", "can", 'Simplify "has the ability to" to "can".', "STYLE_HAS_THE_ABILITY_TO"),
    (r"\bis\s+able\s+to\b", "can", 'Simplify "is able to" to "can".', "STYLE_IS_ABLE_TO"),
    (r"\bmake\s+a\s+decision\b", "decide", 'Use the direct verb "decide" instead of nominalization "make a decision".', "STYLE_MAKE_A_DECISION"),
    (r"\btake\s+into\s+consideration\b", "consider", 'Simplify "take into consideration" to "consider".', "STYLE_TAKE_INTO_CONSIDERATION"),
    (r"\bgive\s+consideration\s+to\b", "consider", 'Simplify "give consideration to" to "consider".', "STYLE_GIVE_CONSIDERATION_TO"),
    (r"\breach\s+a\s+conclusion\b", "conclude", 'Use the direct verb "conclude".', "STYLE_REACH_A_CONCLUSION"),
    (r"\bconduct\s+an\s+investigation\s+into\b", "investigate", 'Simplify to "investigate".', "STYLE_CONDUCT_INVESTIGATION"),
    
    # Redundancies
    (r"\bend\s+result\b", "result", 'Omit "end" as "result" inherently implies the end.', "STYLE_REDUNDANCY_END_RESULT"),
    (r"\bfuture\s+plans\b", "plans", 'Omit "future" as "plans" are inherently for the future.', "STYLE_REDUNDANCY_FUTURE_PLANS"),
    (r"\bpast\s+history\b", "history", 'Omit "past" as "history" inherently refers to the past.', "STYLE_REDUNDANCY_PAST_HISTORY"),
    (r"\bfree\s+gift\b", "gift", 'Omit "free" as a "gift" is by definition free.', "STYLE_REDUNDANCY_FREE_GIFT"),
    (r"\bbasic\s+fundamentals\b", "fundamentals", 'Omit "basic" as "fundamentals" are already basic.', "STYLE_REDUNDANCY_BASIC_FUNDAMENTALS"),
    (r"\bunexpected\s+surprise\b", "surprise", 'Omit "unexpected" as a "surprise" is inherently unexpected.', "STYLE_REDUNDANCY_UNEXPECTED_SURPRISE"),
]

TONE_REWRITE_RULES = [
    (r"\b(?:hey|hi|yo)\s*,?\s*what'?s\s+up\s+with\s+(?:the\s+)?([^?.,]+)\??",
     r"Could you please provide an update on the \1?",
     'Casual greeting and informal inquiry. Consider phrasing more professionally.',
     "TONE_INFORMAL_WHATS_UP"),
    (r"\bwhat'?s\s+up\s+with\s+(?:the\s+)?([^?.,]+)\??",
     r"What is the current status of the \1?",
     'Informal phrasing. Consider a more professional inquiry.',
     "TONE_WHATS_UP"),
    (r"\bhit\s+me\s+up\b", "please contact me", 'Replace slang "hit me up" with "please contact me".', "TONE_HIT_ME_UP"),
    (r"\bwanna\b", "want to", 'Replace informal "wanna" with "want to".', "TONE_WANNA"),
    (r"\bgonna\b", "going to", 'Replace informal "gonna" with "going to".', "TONE_GONNA"),
    (r"\bgotta\b", "need to", 'Replace informal "gotta" with "need to" or "have to".', "TONE_GOTTA"),
    (r"\bkinda\b", "somewhat", 'Replace informal "kinda" with "somewhat" or "rather".', "TONE_KINDA"),
    (r"\bsorta\b", "rather", 'Replace informal "sorta" with "rather".', "TONE_SORTA"),
    (r"\ba\s+bunch\s+of\b", "several", 'In formal contexts, use "several" or "multiple" instead of "a bunch of".', "TONE_A_BUNCH_OF"),
    (r"\blots\s+of\b", "many", 'In professional writing, prefer "many" or "numerous" over "lots of".', "TONE_LOTS_OF"),
    (r"\bASAP\b", "as soon as possible", 'Spell out "as soon as possible" for a more polite and professional tone.', "TONE_ASAP"),
    (r"\bthanks\s+a\s+ton\b", "thank you very much", 'Replace "thanks a ton" with "thank you very much".', "TONE_THANKS_A_TON"),
    (r"\bno\s+worries\b", "you are welcome", 'In professional correspondence, "you are welcome" or "glad to help" is preferred.', "TONE_NO_WORRIES"),
]


class StyleToneAnalyzer:
    def __init__(self):
        pass

    def check(self, doc: ProcessedDocument) -> list:
        issues = []
        raw_text = doc.raw_text

        # 1. Conciseness and Clarity Rules
        for pattern, replacement, explanation, rule_id in CONCISENESS_RULES:
            for m in re.finditer(pattern, raw_text, re.IGNORECASE):
                orig = m.group(0)
                rep = replacement.upper() if orig.isupper() else (replacement.capitalize() if orig[0].isupper() else replacement)
                issues.append({
                    "start": m.start(),
                    "end": m.end(),
                    "original": orig,
                    "replacement": rep,
                    "category": "Style",
                    "rule_id": rule_id,
                    "message": f'Make your writing more concise: "{orig}" → "{rep}".',
                    "explanation": explanation,
                    "severity": "suggestion"
                })

        # 2. Tone & Colloquialisms
        for pattern, replacement, explanation, rule_id in TONE_REWRITE_RULES:
            for m in re.finditer(pattern, raw_text, re.IGNORECASE):
                orig = m.group(0)
                rep = m.expand(replacement) if "\\" in replacement else replacement
                if orig[0].isupper() and rep:
                    rep = rep[0].upper() + rep[1:]
                issues.append({
                    "start": m.start(),
                    "end": m.end(),
                    "original": orig,
                    "replacement": rep,
                    "category": "Tone",
                    "rule_id": rule_id,
                    "message": f'Adjust tone for professional clarity: "{orig}" → "{rep}".',
                    "explanation": explanation,
                    "severity": "suggestion"
                })

        return issues

    def analyze_tone(self, doc: ProcessedDocument) -> Dict[str, Any]:
        text = doc.raw_text.lower()
        if not text.strip():
            return {
                "primary_tone": "Neutral",
                "formality": "Neutral",
                "scores": {"formal": 50, "casual": 50, "professional": 50, "academic": 50},
                "summary": "Enter text to evaluate tone and style."
            }

        # Tone feature counts
        casual_cues = len(re.findall(r"\b(hey|hi|yo|wanna|gonna|gotta|kinda|sorta|bunch|stuff|cool|awesome|lol|dude|asap|btw|yep|nope)\b", text))
        casual_cues += len(re.findall(r"[!?]{2,}", text))
        casual_cues += len(re.findall(r"\b(can't|don't|won't|it's|I'm|you're|we're|they're)\b", text))

        formal_cues = len(re.findall(r"\b(furthermore|moreover|consequently|therefore|nevertheless|nonetheless|subsequently|hereby|thus|accordingly|demonstrates|indicates|utilize|implement)\b", text))
        formal_cues += len(re.findall(r"\b(in addition|with respect to|in conclusion|on the contrary)\b", text))

        professional_cues = len(re.findall(r"\b(please|regards|sincerely|appreciate|update|report|project|collaborate|schedule|objective|deliverable|feedback|confirm|discuss)\b", text))

        academic_cues = len(re.findall(r"\b(hypothesis|methodology|analysis|empirical|correlation|significant|findings|literature|framework|phenomenon|theoretical)\b", text))

        total_words = len([t for t in doc.tokens if t.is_word]) or 1

        casual_score = min(100, int((casual_cues / total_words) * 350) + 20)
        formal_score = min(100, int((formal_cues / total_words) * 450) + (10 if casual_cues == 0 else 0) + 20)
        prof_score = min(100, int((professional_cues / total_words) * 350) + (30 if casual_cues <= 1 else 10))
        acad_score = min(100, int((academic_cues / total_words) * 500) + (formal_score // 2))

        # Determine primary tone
        scores = {
            "Professional": prof_score,
            "Formal": formal_score,
            "Casual": casual_score,
            "Academic": acad_score
        }

        primary_tone = max(scores, key=scores.get)
        if casual_score > 60:
            formality = "Casual / Conversational"
            summary = "Your writing has an informal, friendly, and conversational tone."
        elif formal_score > 60 or acad_score > 60:
            formality = "Formal / Academic"
            summary = "Your writing demonstrates high formality with structured vocabulary."
        elif prof_score > 40:
            formality = "Professional & Direct"
            summary = "Your writing is clear, polite, and suitable for business communication."
        else:
            formality = "Neutral & Clear"
            summary = "Your writing maintains an objective, balanced tone."

        return {
            "primary_tone": primary_tone,
            "formality": formality,
            "scores": {
                "formal": formal_score,
                "casual": casual_score,
                "professional": prof_score,
                "academic": acad_score
            },
            "summary": summary
        }


style_tone_analyzer = StyleToneAnalyzer()
